#!/usr/bin/env python3
"""GHA witness — weekly machine loops outside audit (read-only)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from noos_machine_loops_v1 import run_outside_audit  # noqa: E402

PROOF = ROOT / "receipts/proof/noos-machine-audit-witness-v1.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def witness(*, trailing_hours: int = 168, write_receipt: bool = False) -> dict[str, Any]:
    audit = run_outside_audit(trailing_hours=trailing_hours)
    chain_ok = bool((audit.get("chain") or {}).get("ok"))
    row = {
        "schema": "noos-machine-audit-witness-v1",
        "at": utc_now(),
        "read_only": True,
        "witness_mode": True,
        "trailing_hours": trailing_hours,
        "closure_token": f"NOOS_MACHINE_AUDIT_WITNESS: {'green' if chain_ok else 'yellow'}",
        "overall_status": "green" if chain_ok else "yellow",
        "chain_ok": chain_ok,
        "audit": audit,
        "one_law": "Outside audit only — no merge/repair dispatch from witness.",
    }
    row["ok"] = True
    if write_receipt:
        PROOF.parent.mkdir(parents=True, exist_ok=True)
        PROOF.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(PROOF)
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--trailing-hours", type=int, default=168)
    args = ap.parse_args()

    row = witness(trailing_hours=args.trailing_hours, write_receipt=args.write_receipt)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["closure_token"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
