#!/usr/bin/env python3
"""Step 3 proof — self-heal local reaction time under 60s."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "receipts/proof/noos-fly-selfheal-reaction-v1.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def measure_reaction() -> dict[str, Any]:
    start = time.monotonic()
    proc = subprocess.run(
        [sys.executable, "scripts/reenqueue_blocked_upg_inbox_v1.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    elapsed_ms = int((time.monotonic() - start) * 1000)
    return {
        "schema": "noos-fly-selfheal-reaction-v1",
        "measured_at": utc_now(),
        "command": "reenqueue_blocked_upg_inbox_v1.py",
        "exit_code": proc.returncode,
        "reaction_ms": elapsed_ms,
        "under_60s": elapsed_ms < 60000,
        "ok": proc.returncode == 0 and elapsed_ms < 60000,
        "report_line": f"self_heal_reaction · {elapsed_ms}ms",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = measure_reaction()
    if args.write_receipt:
        PROOF.parent.mkdir(parents=True, exist_ok=True)
        PROOF.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(PROOF.relative_to(ROOT))
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
