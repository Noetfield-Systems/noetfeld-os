#!/usr/bin/env python3
"""UPG-PLAN-05 — CF motor + Railway + liveness sustain checks."""

from __future__ import annotations

import json
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "receipts/proof/noos-motor-sustain-v1.json"

CHECKS = [
    ("cf_loop_fleet", "https://noos-loop-fleet-tick-v1.sina-kazemnezhad-ca.workers.dev/health"),
    ("cf_factory_tick", "https://noos-factory-autorun-tick-v1.sina-kazemnezhad-ca.workers.dev/health"),
    ("railway_loop_runner", "https://noos-loop-runner-production.up.railway.app/health"),
    ("cf_deadman", "https://noos-deadman-v1.sina-kazemnezhad-ca.workers.dev/health"),
]


def _http_ok(url: str) -> dict:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "noos-motor-sustain-v1"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", errors="replace")[:500]
            return {"ok": resp.status == 200, "status": resp.status, "body": body}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status": exc.code, "error": str(exc)}
    except OSError as exc:
        return {"ok": False, "error": str(exc)}


def _liveness() -> dict:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/autorun_status_v1.py"), "--json"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if proc.returncode != 0 and not proc.stdout.strip():
        return {"ok": False, "error": proc.stderr[-400:]}
    try:
        doc = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return {"ok": False, "error": str(exc)}
    critique = doc.get("critique") or {}
    stale = None
    for wf in doc.get("workflows") or []:
        if wf.get("loop_id") == "noos_loop_liveness_registry" or "stale_count" in wf:
            stale = wf.get("stale_count")
            break
    return {
        "ok": bool(critique.get("overall_ok")),
        "findings": len(critique.get("findings") or []),
        "stale_count": stale,
    }


def verify(*, write_receipt: bool = False) -> dict:
    checks: dict[str, dict] = {}
    for name, url in CHECKS:
        checks[name] = _http_ok(url)
    liveness = _liveness()
    ok = all(c.get("ok") for c in checks.values()) and liveness.get("ok")
    row = {
        "schema": "noos-motor-sustain-v1",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ok": ok,
        "checks": checks,
        "liveness": liveness,
    }
    if write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(RECEIPT)
    return row


def main() -> int:
    write = "--write-receipt" in sys.argv
    row = verify(write_receipt=write)
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
