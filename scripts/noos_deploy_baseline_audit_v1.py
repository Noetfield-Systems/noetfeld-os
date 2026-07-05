#!/usr/bin/env python3
"""Step 1 — deploy truth baseline: scaffold vs Fly L4 vs Cloudflare www."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCOPES = ROOT / "data/noos-deploy-scopes-v1.json"
RUNTIME = ROOT / ".noos-runtime/deploy/deploy-baseline-v1.json"
PROOF = ROOT / "receipts/proof/noos-deploy-baseline-audit-v1.json"
FLY_BIN = Path.home() / ".fly/bin/fly"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def probe(url: str, *, follow: bool = False) -> dict[str, Any]:
    try:
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "noos-deploy-baseline/1.0"})
        if follow:
            # manual one-hop for 308 trailing slash
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = resp.read(512)
                return {
                    "url": url,
                    "ok": 200 <= resp.status < 300,
                    "status": resp.status,
                    "server": resp.headers.get("Server"),
                }
        with urllib.request.urlopen(req, timeout=15) as resp:
            return {
                "url": url,
                "ok": resp.status == 200,
                "status": resp.status,
                "server": resp.headers.get("Server"),
            }
    except urllib.error.HTTPError as exc:
        loc = exc.headers.get("Location") if follow else None
        if follow and exc.code in (301, 302, 307, 308) and loc:
            return probe(loc if loc.startswith("http") else url.rstrip("/") + "/", follow=False)
        return {"url": url, "ok": False, "status": exc.code, "error": str(exc)}
    except OSError as exc:
        return {"url": url, "ok": False, "status": None, "error": str(exc)}


def fly_auth_ok() -> dict[str, Any]:
    fly = shutil.which("fly") or (str(FLY_BIN) if FLY_BIN.is_file() else None)
    if not fly:
        return {"ok": False, "fly_cli": False, "reason": "fly_cli_missing"}
    proc = subprocess.run([fly, "auth", "whoami"], capture_output=True, text=True, check=False)
    return {
        "ok": proc.returncode == 0,
        "fly_cli": True,
        "fly_path": fly,
        "whoami": proc.stdout.strip() or proc.stderr.strip(),
    }


def scaffold_paths() -> dict[str, Any]:
    rows: dict[str, Any] = {}
    for key, rel in (
        ("fly_inbox", "ops/fly/noos-inbox-runner/fly.toml"),
        ("fly_self_heal", "ops/fly/noos-self-heal-runner/fly.toml"),
    ):
        p = ROOT / rel
        rows[key] = {"path": rel, "exists": p.is_file()}
    return rows


def build_baseline() -> dict[str, Any]:
    scopes_cfg = json.loads(SCOPES.read_text(encoding="utf-8"))
    scopes: dict[str, Any] = {}
    fly_live_count = 0
    for scope_id, cfg in (scopes_cfg.get("scopes") or {}).items():
        health = probe(str(cfg.get("health_url") or ""), follow=scope_id == "www")
        ready_url = cfg.get("ready_url")
        ready = probe(str(ready_url), follow=False) if ready_url else {"skipped": True}
        l4 = bool(health.get("ok")) and (ready.get("ok") if ready_url else True)
        if scope_id.startswith("fly-") and l4:
            fly_live_count += 1
        scopes[scope_id] = {
            "title": cfg.get("title"),
            "upg": cfg.get("upg"),
            "health_probe": health,
            "ready_probe": ready,
            "l4_live": l4,
            "scaffold_only": scope_id.startswith("fly-") and not l4,
        }

    cf_motor = probe(
        "https://noos-loop-fleet-tick-v1.sina-kazemnezhad-ca.workers.dev/health",
        follow=False,
    )
    fly_auth = fly_auth_ok()
    scaffolds = scaffold_paths()

    return {
        "schema": "noos-deploy-baseline-audit-v1",
        "audited_at": utc_now(),
        "authority": "NOOS_T2_DEPLOY_ACG_STEP_1",
        "motor_matrix": {
            "primary": "cf_loop_fleet",
            "cf_motor_probe": cf_motor,
            "secondary": "fly_always_on",
            "fly_live": fly_live_count >= 2,
            "fly_live_count": fly_live_count,
            "gha_loops": True,
            "gel_api_railway": scopes.get("gel-api", {}).get("l4_live"),
            "www_cloudflare": scopes.get("www", {}).get("l4_live"),
        },
        "fly_auth": fly_auth,
        "scaffolds": scaffolds,
        "scopes": scopes,
        "manifest_gap_note": (
            "UPG-0201/0202/0206 marked done on scaffold evidence until Fly L4 probes pass"
        ),
        "ok": bool(scopes.get("www", {}).get("l4_live")) and bool(cf_motor.get("ok")),
        "report_line": (
            f"deploy_baseline · fly_l4={fly_live_count}/2 www={scopes.get('www', {}).get('l4_live')} "
            f"fly_auth={fly_auth.get('ok')}"
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    row = build_baseline()
    if args.write_receipt:
        RUNTIME.parent.mkdir(parents=True, exist_ok=True)
        PROOF.parent.mkdir(parents=True, exist_ok=True)
        RUNTIME.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        PROOF.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_paths"] = [str(RUNTIME.relative_to(ROOT)), str(PROOF.relative_to(ROOT))]

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
