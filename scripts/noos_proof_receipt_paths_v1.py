"""Committed proof-grade receipt paths (governed-autorun L6).

Proof receipts live under receipts/proof/ in the repo or in Supabase.
.noos-runtime/ is runtime churn only — never cite as closeout evidence.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOF_DIR = ROOT / "receipts/proof"


def proof_receipt(filename: str) -> Path:
    PROOF_DIR.mkdir(parents=True, exist_ok=True)
    return PROOF_DIR / filename
