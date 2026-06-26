"""Tests for JSON policy pack loader."""

from noetfield_governance.policy_loader import load_pack_document, load_policy_pack


def test_load_copilot_governance_pack() -> None:
    pack = load_policy_pack("copilot-governance-v1")
    assert pack.minimum_confidence == 0.75
    assert "run_copilot_governance_demo" in pack.high_impact_actions


def test_load_bank_pilot_pack() -> None:
    pack = load_policy_pack("bank-pilot-v1")
    assert pack.minimum_confidence == 0.80
    document = load_pack_document("bank-pilot-v1")
    assert document["pack_type"] == "bank-pilot"


def test_default_pack_fallback() -> None:
    from noetfield_governance.policy_loader import load_default_policy_pack

    pack = load_default_policy_pack()
    assert pack.minimum_confidence >= 0.75
