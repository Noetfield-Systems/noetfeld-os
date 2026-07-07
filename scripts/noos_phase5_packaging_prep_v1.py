#!/usr/bin/env python3
"""UPG-PLAN-10 — Phase 5 / packaging deferred rail prep (no deploy)."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "receipts/proof/noos-phase5-packaging-prep-v1.json"

ITEMS = [
    {"id": "UPG-0167", "title": "npm @noetfield/gate publish", "gate": "legal/org"},
    {"id": "UPG-0174", "title": "Production secrets/API-key vault policy", "gate": "founder"},
    {"id": "UPG-0175", "title": "Production policy pack semver pinning", "gate": "founder"},
    {"id": "UPG-0170", "title": "Homebrew tap stub document", "gate": "machine_safe"},
    {"id": "PHASE-5", "title": "Phase 5 Tenant & Production (UPG 0177+)", "gate": "LOOP-VERIFY-ALL"},
    {"id": "ECOSYSTEM-E", "title": "Ecosystem Phase E deferred", "gate": "NOOS-C-01"},
]


def prep(*, write_receipt: bool = False) -> dict:
    row = {
        "schema": "noos-phase5-packaging-prep-v1",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ok": True,
        "deferred_items": ITEMS,
        "does_not_block": ["ICL-P2", "24/7 motor", "UPG-NF-PUB P0"],
        "product_truth": str(ROOT / "docs/_NOOS_AGENT/PRODUCT_TRUTH.md"),
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
