#!/usr/bin/env python3
"""Verify plan-motor end-to-end wiring (LOCKED registry)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WIRING = ROOT / "data/noos-plan-motor-wiring-v1.json"
PROOF = ROOT / "receipts/proof/noos-plan-motor-wiring-verify-v1.json"


def _check_path(rel: str) -> dict[str, Any]:
    path = ROOT / rel
    return {"path": rel, "ok": path.is_file(), "exists": path.exists()}


def verify(*, write_receipt: bool = False) -> dict[str, Any]:
    wiring = json.loads(WIRING.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    for rel in (
        wiring.get("plan_ssot", {}).get("manifest"),
        wiring.get("plan_ssot", {}).get("planes"),
        wiring.get("roles", {}).get("inbox", {}).get("script"),
        wiring.get("roles", {}).get("inbox", {}).get("plan_dequeue"),
        wiring.get("roles", {}).get("researcher", {}).get("script"),
        wiring.get("roles", {}).get("specialist", {}).get("script"),
        wiring.get("roles", {}).get("orchestrator", {}).get("script"),
        wiring.get("kernel", {}).get("bridge"),
        wiring.get("kernel", {}).get("router"),
        wiring.get("dispatch", {}).get("dispatch_table"),
    ):
        if rel:
            checks.append(_check_path(str(rel)))

    inbox_src = (ROOT / "scripts/cloud_inbox_worker_v1.py").read_text(encoding="utf-8")
    checks.append({"name": "inbox_imports_plan_motor", "ok": "noos_plan_motor_v1" in inbox_src})
    researcher_src = (ROOT / "scripts/noos_researcher_v1.py").read_text(encoding="utf-8")
    checks.append({"name": "researcher_kernel_bridge", "ok": "noos_plan_motor_kernel_bridge_v1" in researcher_src})
    specialist_src = (ROOT / "scripts/noos_specialist_v1.py").read_text(encoding="utf-8")
    checks.append({"name": "specialist_kernel_bridge", "ok": "noos_plan_motor_kernel_bridge_v1" in specialist_src})

    loops = json.loads((ROOT / "data/noos-24-7-loops-v1.json").read_text(encoding="utf-8"))
    orch_cmd = ""
    for loop in loops.get("loops") or []:
        if loop.get("id") == "orchestrator_cross_repo":
            steps = loop.get("steps") or []
            if steps:
                orch_cmd = " ".join(steps[0].get("cmd") or [])
    checks.append({"name": "orchestrator_real_script", "ok": "noos_orchestrator_v1.py" in orch_cmd})

    dispatch = json.loads((ROOT / wiring["dispatch"]["dispatch_table"]).read_text(encoding="utf-8"))
    dispatch_ids = {t.get("dispatch_id") for t in dispatch.get("targets") or []}
    for role, want in (
        ("inbox", "inbox"),
        ("researcher", "researcher"),
        ("specialist", "specialist"),
        ("orchestrator", "orchestrator"),
    ):
        checks.append({"name": f"cf_dispatch_{role}", "ok": want in dispatch_ids})

    ok = all(c.get("ok") for c in checks)
    row: dict[str, Any] = {
        "schema": "noos-plan-motor-wiring-verify-v1",
        "lock_state": wiring.get("lock_state"),
        "ok": ok,
        "checks": checks,
        "closure_token": f"NOOS_PLAN_MOTOR_WIRING: {'PASS' if ok else 'FAIL'}",
    }
    if write_receipt:
        PROOF.parent.mkdir(parents=True, exist_ok=True)
        PROOF.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(PROOF.relative_to(ROOT))
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    args = ap.parse_args()
    row = verify(write_receipt=args.write_receipt)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["closure_token"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
