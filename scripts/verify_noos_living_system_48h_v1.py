#!/usr/bin/env python3
"""Phase E — 48h living system baseline capture and final verify."""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "data/noos-living-system-baseline-v1.json"
PROOF = ROOT / "receipts/proof/noos-living-system-48h-v1.json"

CF_MOTOR = "https://noos-loop-fleet-tick-v1.sina-kazemnezhad-ca.workers.dev/health"
DEADMAN = "https://noos-deadman-v1.sina-kazemnezhad-ca.workers.dev/health"
RAILWAY = "https://noos-loop-runner-production.up.railway.app/health"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_env() -> tuple[str, str]:
    env_file = Path.home() / ".sourcea-secrets/noetfield.env"
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())
    url = (os.environ.get("NOETFIELD_SUPABASE_URL") or os.environ.get("SUPABASE_URL") or "").rstrip("/")
    key = os.environ.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or ""
    return url, key


def fetch_json(url: str) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "living-system-48h-v1"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return {"ok": resp.status == 200, "status": resp.status, "body": json.loads(resp.read().decode("utf-8"))}
    except (urllib.error.HTTPError, OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)}


def registry_snapshot(url: str, key: str) -> list[dict[str, Any]]:
    req = urllib.request.Request(
        f"{url}/rest/v1/noos_loop_registry?select=loop_id,last_fired_at,interval_minutes,last_cycle_status",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def deadman_runs_count(url: str, key: str, since_iso: str) -> int:
    q = urllib.parse.urlencode({"select": "run_id", "created_at": f"gte.{since_iso}"})
    req = urllib.request.Request(
        f"{url}/rest/v1/noos_deadman_runs?{q}",
        headers={"apikey": key, "Authorization": f"Bearer {key}", "Prefer": "count=exact"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        cr = resp.headers.get("Content-Range", "")
        if "/" in cr:
            total = cr.split("/")[-1]
            return int(total) if total.isdigit() else 0
    return 0


def capture_baseline() -> dict[str, Any]:
    url, key = load_env()
    motors = {
        "cf_loop_motor": fetch_json(CF_MOTOR),
        "cf_deadman": fetch_json(DEADMAN),
        "railway_loop_runner": fetch_json(RAILWAY),
    }
    registry: list[dict[str, Any]] = []
    if url and key:
        try:
            registry = registry_snapshot(url, key)
        except OSError:
            registry = []
    return {
        "schema": "noos-living-system-baseline-v1",
        "captured_at": utc_now(),
        "motors": motors,
        "registry_rows": registry,
        "registry_count": len(registry),
        "rows_with_last_fired": sum(1 for r in registry if r.get("last_fired_at")),
    }


def verify_final(*, baseline: dict[str, Any]) -> dict[str, Any]:
    current = capture_baseline()
    t0 = baseline.get("captured_at") or ""
    url, key = load_env()
    deadman_runs = deadman_runs_count(url, key, t0) if url and key and t0 else None

    motors_ok = all((current.get("motors") or {}).get(k, {}).get("ok") for k in ("cf_loop_motor", "cf_deadman", "railway_loop_runner"))
    registry_ok = current.get("registry_count", 0) >= baseline.get("registry_count", 0)
    fired_ok = current.get("rows_with_last_fired", 0) >= max(1, baseline.get("rows_with_last_fired", 0))

    row = {
        "schema": "noos-living-system-48h-v1",
        "verified_at": utc_now(),
        "baseline_captured_at": t0,
        "current": current,
        "deadman_runs_since_baseline": deadman_runs,
        "checks": {
            "motors_green": motors_ok,
            "registry_preserved": registry_ok,
            "liveness_maintained": fired_ok,
            "deadman_active": (deadman_runs or 0) >= 48 if deadman_runs is not None else None,
        },
        "ok": motors_ok and registry_ok and fired_ok,
    }
    if deadman_runs is not None:
        row["ok"] = row["ok"] and deadman_runs >= 48
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--baseline", action="store_true", help="Capture T0 baseline")
    ap.add_argument("--final", action="store_true", help="Verify against saved baseline")
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.baseline:
        row = capture_baseline()
        row["ok"] = True
        BASELINE.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["baseline_path"] = str(BASELINE.relative_to(ROOT))
    elif args.final:
        if not BASELINE.is_file():
            row = {"ok": False, "error": "baseline_missing"}
        else:
            baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
            row = verify_final(baseline=baseline)
    else:
        row = {"ok": False, "error": "specify --baseline or --final"}
        if args.json:
            print(json.dumps(row, indent=2))
        return 1

    if args.write_receipt:
        PROOF.parent.mkdir(parents=True, exist_ok=True)
        PROOF.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(PROOF.relative_to(ROOT))

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"living_system_48h · ok={row.get('ok')}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
