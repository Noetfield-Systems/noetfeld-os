#!/usr/bin/env python3
"""UPG-PLAN-02 — machine prep for 48h laptop-closed test (founder starts T0)."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "receipts/proof/noos-living-system-48h-prep-v1.json"
BASELINE = ROOT / "receipts/proof/noos-living-system-48h-v1.json"


def prep(*, write_receipt: bool = False) -> dict:
    motor = subprocess.run(
        [sys.executable, str(ROOT / "scripts/verify_noos_motor_sustain_v1.py")],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    motor_doc = json.loads(motor.stdout) if motor.stdout.strip() else {"ok": False}

    baseline_ok = BASELINE.is_file()
    checklist = [
        {"step": "A2", "title": "Founder closes laptop (T0)", "owner": "founder", "done": False},
        {"step": "A3", "title": "Machine runs 48h CF+deadman", "owner": "machine", "done": False},
        {"step": "A5", "title": "make living-system-verify-48h", "owner": "founder", "done": False},
        {"step": "A6", "title": "make loop-verify-all + deadman-probe", "owner": "founder", "done": False},
        {"step": "A7", "title": "48h retro doc signed", "owner": "founder+machine", "done": False},
        {"step": "A8", "title": "Phase G closeout receipt ok=true", "owner": "machine", "done": False},
    ]
    ready = motor_doc.get("ok") and baseline_ok
    row = {
        "schema": "noos-living-system-48h-prep-v1",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ok": ready,
        "motor_sustain": motor_doc,
        "baseline_captured": baseline_ok,
        "checklist": checklist,
        "founder_gate": "UPG-LS-09–10",
        "entry_commands": [
            "make living-system-baseline",
            "make motor-sustain-verify",
            "# founder T0: close laptop",
            "make living-system-verify-48h",
        ],
    }
    if write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(RECEIPT)
    return row


def main() -> int:
    write = "--write-receipt" in sys.argv
    row = prep(write_receipt=write)
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
