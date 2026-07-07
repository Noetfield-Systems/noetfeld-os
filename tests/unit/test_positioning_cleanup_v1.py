"""Positioning verdict matrix + cleanup dimensions SSOT."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_verdict_matrix_has_accept_rows() -> None:
    data = json.loads((ROOT / "data/www-positioning-verdict-matrix-v1.json").read_text(encoding="utf-8"))
    claims = data["claims"]
    assert any(c["verdict"] == "ACCEPT" for c in claims)
    assert any(c["verdict"] == "REJECT" for c in claims)
    assert all(c.get("evidence") or c["verdict"] == "REJECT" for c in claims if c["verdict"] == "ACCEPT")


def test_cleanup_dimensions_five_plus_outcome() -> None:
    data = json.loads((ROOT / "data/nf_cleanup_dimensions_v1.json").read_text(encoding="utf-8"))
    assert len(data["dimensions"]) == 5
    assert data["outcome_sku"]["id"] == "machine-rule-pack"
    skus = {d["contract_sku"] for d in data["dimensions"]}
    assert "Trust Brief" in skus
    assert "Copilot Governance Pack" in skus


def test_audit_lens_ai_language_hygiene() -> None:
    data = json.loads((ROOT / "scripts/site_audit/lenses/noetfield-lenses-v1.json").read_text(encoding="utf-8"))
    lens = data["lenses"]["ai_language_hygiene"]
    ids = {c["id"] for c in lens["checks"]}
    assert "ALH-1" in ids and "ALH-6" in ids
