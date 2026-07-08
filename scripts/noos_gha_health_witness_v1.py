#!/usr/bin/env python3
"""GHA secondary witness — ICL-D10–D12 + witness billing-gate early warning."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from noos_gha_run_health_v1 import run_gha_health  # noqa: E402

PROOF = ROOT / "receipts/proof/noos-gha-health-witness-v1.json"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    args = ap.parse_args()

    row = run_gha_health()
    row["schema"] = "noos-gha-health-witness-v1"
    row["witness_mode"] = True
    row["closure_token"] = row["closure_token"].replace("NOOS_GHA_HEALTH", "NOOS_GHA_HEALTH_WITNESS")

    if args.write_receipt:
        PROOF.parent.mkdir(parents=True, exist_ok=True)
        PROOF.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(PROOF)

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["closure_token"])

    # Fail witness on billing precursor or latest billing gate — early warning surface
    checks = row.get("checks") or {}
    gate_fail = not checks.get("ICL-D10", {}).get("ok")
    witness_fail = not checks.get("witness_early_warning", {}).get("ok")
    return 1 if gate_fail or witness_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
