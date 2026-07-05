#!/usr/bin/env python3
"""Step 1 — machine loop baseline audit: status digest + CF motor probe + receipt."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/noos-24-7-loops-v1.json"
RUNTIME_RECEIPT = ROOT / ".noos-runtime/machine-loops/baseline-audit-v1.json"
PROOF_RECEIPT = ROOT / "receipts/proof/noos-loop-baseline-audit-v1.json"

CORE_LOOP_IDS = (
    "inbox",
    "runtime",
    "surface",
    "chain",
    "self_heal",
    "sourcea_observe",
    "agent_nerve",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_cmd(cmd: list[str]) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
    return {
        "cmd": cmd,
        "exit_code": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def probe_url(url: str) -> dict[str, Any]:
    try:
        req = urllib.request.Request(
            url,
            method="GET",
            headers={"User-Agent": "noos-loop-baseline-audit/1.0", "Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return {"url": url, "ok": resp.status == 200, "status": resp.status}
    except urllib.error.HTTPError as exc:
        return {"url": url, "ok": False, "status": exc.code, "error": str(exc)}
    except OSError as exc:
        return {"url": url, "ok": False, "status": None, "error": str(exc)}


def loop_rows(registry: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for loop in registry.get("loops") or []:
        loop_id = str(loop.get("id") or "")
        rows.append(
            {
                "loop_id": loop_id,
                "title": loop.get("title"),
                "factory_id": loop.get("factory_id"),
                "github_workflow": loop.get("github_workflow"),
                "event_type": loop.get("event_type"),
                "interval_minutes": loop.get("interval_minutes"),
                "core_domain_loop": loop_id in CORE_LOOP_IDS,
                "verification_state": "DECLARED",
            }
        )
    return rows


def build_baseline() -> dict[str, Any]:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    motor = registry.get("motor") or {}
    health_url = str(motor.get("health_url") or "")

    machine_status = run_cmd([sys.executable, "scripts/noos_machine_loops_v1.py", "--json", "status"])
    machine_audit = run_cmd([sys.executable, "scripts/noos_machine_loops_v1.py", "--json", "audit"])
    schedule_verify = run_cmd(
        [sys.executable, "scripts/verify_noos_github_schedule_v1.py", "--write-receipt", "--json"]
    )

    loops_status_stdout = run_cmd(
        [
            sys.executable,
            "-c",
            "import json; d=json.load(open('data/noos-24-7-loops-v1.json')); "
            "print(json.dumps({'motor':d['motor'],'loops':[{'id':x['id'],'interval':x['interval_minutes'],'event':x['event_type']} for x in d['loops']]}))",
        ]
    )

    motor_probe = probe_url(health_url) if health_url else {"ok": False, "error": "health_url_missing"}

    loops = loop_rows(registry)
    core = [row for row in loops if row["core_domain_loop"]]

    return {
        "schema": "noos-loop-baseline-audit-v1",
        "audited_at": utc_now(),
        "authority": "NOOS_MACHINE_LOOPS_UPGRADE_STEP_1",
        "motor": motor,
        "motor_health_probe": motor_probe,
        "core_loop_count": len(core),
        "total_loop_count": len(loops),
        "loops": loops,
        "core_loops": core,
        "commands": {
            "machine_status": machine_status,
            "loops_status": loops_status_stdout,
            "schedule_verify": schedule_verify,
            "machine_audit": machine_audit,
        },
        "ok": motor_probe.get("ok") is True and schedule_verify.get("exit_code") == 0,
        "report_line": (
            f"loop_baseline_audit · core={len(core)} motor={'ok' if motor_probe.get('ok') else 'fail'}"
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    row = build_baseline()
    if args.write_receipt:
        RUNTIME_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        PROOF_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RUNTIME_RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        PROOF_RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_paths"] = [
            str(RUNTIME_RECEIPT.relative_to(ROOT)),
            str(PROOF_RECEIPT.relative_to(ROOT)),
        ]

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
