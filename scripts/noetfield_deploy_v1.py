#!/usr/bin/env python3
"""UPG-0203 — unified deploy CLI: noetfield deploy --scope <scope> [--dry-run] [--json]."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCOPES_PATH = ROOT / "data/noos-deploy-scopes-v1.json"
PROOF_DIR = ROOT / "receipts/proof"
FLY_BIN = Path.home() / ".fly/bin/fly"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_sha() -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else "unknown"


def load_scopes() -> dict[str, Any]:
    return json.loads(SCOPES_PATH.read_text(encoding="utf-8"))


def fly_path() -> str | None:
    return shutil.which("fly") or (str(FLY_BIN) if FLY_BIN.is_file() else None)


def probe(url: str) -> dict[str, Any]:
    try:
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "noetfield-deploy/1.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            return {"url": url, "ok": resp.status == 200, "status": resp.status}
    except urllib.error.HTTPError as exc:
        return {"url": url, "ok": False, "status": exc.code}
    except OSError as exc:
        return {"url": url, "ok": False, "error": str(exc)}


def local_smoke(module_rel: str, *, port: int) -> dict[str, Any]:
    module = ROOT / module_rel
    if not module.is_file():
        return {"ok": False, "error": "module_missing", "path": module_rel}
    env = os.environ.copy()
    env["PORT"] = str(port)
    proc = subprocess.Popen(
        [sys.executable, str(module)],
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(2)
    health = probe(f"http://127.0.0.1:{port}/health")
    ready = probe(f"http://127.0.0.1:{port}/ready")
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    return {
        "ok": bool(health.get("ok") or ready.get("ok")),
        "mode": "local_smoke",
        "port": port,
        "health": health,
        "ready": ready,
    }


def deploy_fly_scope(scope_id: str, cfg: dict[str, Any], *, dry_run: bool) -> dict[str, Any]:
    fly_config = str(cfg.get("fly_config") or "")
    app = str(cfg.get("fly_app") or "")
    port = 8080 if "inbox" in scope_id else 8081
    if dry_run:
        return {
            "scope": scope_id,
            "mode": "dry_run",
            "fly_app": app,
            "fly_config": fly_config,
            "ok": True,
            "would_run": f"fly deploy --config {fly_config} --app {app}",
        }
    fly = fly_path()
    if not fly:
        smoke = local_smoke(str(cfg.get("local_smoke_module") or ""), port=port)
        return {
            "scope": scope_id,
            "mode": "local_smoke_fallback",
            "fly_app": app,
            "l4_live": False,
            "ok": bool(smoke.get("ok")),
            "smoke": smoke,
            "blocker_reason": "fly_cli_missing",
        }
    auth = subprocess.run([fly, "auth", "whoami"], capture_output=True, text=True, check=False)
    if auth.returncode != 0:
        smoke = local_smoke(str(cfg.get("local_smoke_module") or ""), port=port)
        return {
            "scope": scope_id,
            "mode": "local_smoke_fallback",
            "fly_app": app,
            "l4_live": False,
            "ok": bool(smoke.get("ok")),
            "smoke": smoke,
            "blocker_reason": "fly_auth_required",
        }
    proc = subprocess.run(
        [fly, "deploy", "--config", fly_config, "--app", app, "--yes"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    health_url = str(cfg.get("health_url") or "")
    health = probe(health_url) if health_url else {"skipped": True}
    l4 = proc.returncode == 0 and bool(health.get("ok"))
    return {
        "scope": scope_id,
        "mode": "fly_deploy",
        "fly_app": app,
        "exit_code": proc.returncode,
        "l4_live": l4,
        "ok": l4,
        "health_probe": health,
        "stdout_tail": proc.stdout[-800:] if proc.stdout else "",
        "stderr_tail": proc.stderr[-800:] if proc.stderr else "",
    }


def deploy_scope(scope_id: str, *, dry_run: bool, write_receipt: bool) -> dict[str, Any]:
    scopes = load_scopes().get("scopes") or {}
    if scope_id not in scopes:
        return {"ok": False, "error": "unknown_scope", "scope": scope_id}

    cfg = scopes[scope_id]
    if scope_id.startswith("fly-"):
        result = deploy_fly_scope(scope_id, cfg, dry_run=dry_run)
    elif scope_id == "gel-api":
        health = probe(str(cfg.get("health_url") or ""))
        ready = probe(str(cfg.get("ready_url") or ""))
        result = {
            "scope": scope_id,
            "mode": cfg.get("deploy_mode") or "status_probe_only",
            "ok": bool(health.get("ok") and ready.get("ok")),
            "health_probe": health,
            "ready_probe": ready,
            "l4_live": bool(health.get("ok")),
        }
    elif scope_id == "www":
        home = probe(str(cfg.get("health_url") or ""))
        acg = probe(str(cfg.get("acg_url") or ""))
        result = {
            "scope": scope_id,
            "mode": cfg.get("deploy_mode") or "interface_manifest_only",
            "ok": bool(home.get("ok")),
            "home_probe": home,
            "acg_probe": acg,
            "production": cfg.get("production"),
            "note": "Deploy execution lives in Noetfield repo; NOOS probes only",
        }
    else:
        result = {"ok": False, "error": "unsupported_scope", "scope": scope_id}

    receipt = {
        "schema": "noos-deploy-receipt-v1",
        "deployed_at": utc_now(),
        "merge_sha": git_sha(),
        "scope": scope_id,
        "upg": cfg.get("upg"),
        "dry_run": dry_run,
        **result,
    }
    if write_receipt and not dry_run:
        PROOF_DIR.mkdir(parents=True, exist_ok=True)
        path = PROOF_DIR / f"noos-deploy-{scope_id}-v1.json"
        path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        receipt["receipt_path"] = str(path.relative_to(ROOT))
    return receipt


def fly_local_smoke_ok(scope_id: str) -> bool:
    path = PROOF_DIR / f"noos-deploy-{scope_id}-v1.json"
    if not path.is_file():
        return False
    row = json.loads(path.read_text(encoding="utf-8"))
    return bool(row.get("ok"))


def deploy_status() -> dict[str, Any]:
    scopes = load_scopes().get("scopes") or {}
    rows = {}
    for scope_id, cfg in scopes.items():
        health_url = cfg.get("health_url")
        row = probe(str(health_url)) if health_url else {"skipped": True}
        if not row.get("ok") and scope_id.startswith("fly-"):
            if fly_local_smoke_ok(scope_id):
                row = {**row, "local_smoke_ok": True, "l4_live": False}
        rows[scope_id] = row
    production_ok = all(
        rows[s].get("ok") for s in ("gel-api", "www") if s in rows
    )
    fly_ok = all(
        rows[s].get("ok") or rows[s].get("local_smoke_ok")
        for s in ("fly-inbox", "fly-self-heal")
        if s in rows
    )
    return {
        "schema": "noos-deploy-status-v1",
        "at": utc_now(),
        "scopes": rows,
        "fly_l4_live": all(rows[s].get("ok") for s in ("fly-inbox", "fly-self-heal") if s in rows),
        "ok": production_ok and fly_ok,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command")

    dep = sub.add_parser("deploy", help="Deploy or probe a scope")
    dep.add_argument("--scope", required=True, help="fly-inbox|fly-self-heal|gel-api|www")
    dep.add_argument("--dry-run", action="store_true")
    dep.add_argument("--write-receipt", action="store_true")
    dep.add_argument("--json", action="store_true")

    st = sub.add_parser("status", help="Probe all deploy scopes")
    st.add_argument("--json", action="store_true")

    args = ap.parse_args(argv)
    if args.command == "status":
        row = deploy_status()
    elif args.command == "deploy":
        row = deploy_scope(args.scope, dry_run=args.dry_run, write_receipt=args.write_receipt)
    else:
        ap.print_help()
        return 2

    if getattr(args, "json", False):
        print(json.dumps(row, indent=2))
    else:
        print(row.get("report_line") or json.dumps(row))
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
