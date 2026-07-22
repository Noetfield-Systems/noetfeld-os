#!/usr/bin/env python3
"""Cross-repo orchestrator — aggregate motor, plan burn-down, and loop health."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from noos_plan_motor_v1 import burn_down_summary  # noqa: E402
import noos_role_runway_dispatch_v1 as role_dispatch  # noqa: E402

OUT = ROOT / "data/noos-orchestrator-health-v1.json"
PROOF = ROOT / "receipts/proof/noos-orchestrator-health-v1.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _autorun_core_loops() -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/autorun_status_v1.py"), "--json"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    if proc.returncode != 0 and not proc.stdout.strip():
        return {"ok": False, "error": "autorun_status_failed", "stderr": proc.stderr[-400:]}
    try:
        doc = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "error": "autorun_status_invalid_json"}
    core_ids = {
        "noos_loop_inbox",
        "noos_loop_runtime",
        "noos_loop_surface",
        "noos_loop_chain",
        "noos_loop_self_heal",
        "noos_loop_agent_nerve",
        "noos_loop_sourcea_observe",
    }
    rows = []
    for wf in doc.get("workflows") or []:
        if wf.get("id") in core_ids:
            rows.append(
                {
                    "id": wf.get("id"),
                    "status": wf.get("status"),
                    "execution_state": wf.get("execution_state"),
                    "reason": wf.get("reason"),
                }
            )
    degraded = [r for r in rows if r.get("status") != "RUNNING" or r.get("execution_state") not in (None, "RUNNING_CONFIRMED")]
    return {"ok": len(degraded) == 0, "loops": rows, "degraded_count": len(degraded)}


def aggregate() -> dict[str, Any]:
    return {
        "schema": "noos-orchestrator-health-v1",
        "at": utc_now(),
        "plan_motor": burn_down_summary(),
        "autorun": _autorun_core_loops(),
        "wiring": "data/noos-plan-motor-wiring-v1.json",
        "role_dispatch": role_dispatch.dispatch_role("orchestrator", subject="cross-repo-health"),
        "not_a_verdict": "SUBMITTED for independent verification",
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    row = aggregate()
    OUT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    if args.write_receipt:
        PROOF.parent.mkdir(parents=True, exist_ok=True)
        PROOF.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(PROOF.relative_to(ROOT))

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        pm = row.get("plan_motor") or {}
        ar = row.get("autorun") or {}
        print(
            f"orchestrator plan_open={pm.get('open_machine_safe_steps')} "
            f"autorun_ok={ar.get('ok')} degraded={ar.get('degraded_count')}"
        )
    return 0 if (row.get("autorun") or {}).get("ok", False) else 1


if __name__ == "__main__":
    raise SystemExit(main())
