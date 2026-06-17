"""Tests for governance runtime 10-step implementation."""

from pathlib import Path
from uuid import uuid4

from noetfield_governance.gel_adapter import GEL_DECISION_MAP, GelAdapter
from noetfield_governance.governance_config import load_governance_config
from noetfield_governance.ledger_digest import compute_tle_audit_digest, signature_key_id
from noetfield_governance.policy_loader import load_pack_document, load_policy_pack
from noetfield_governance.control_plane import ControlPlaneState, advance_control_plane
from noetfield_sdk.governance import Governance


def test_policy_pack_loader_copilot_v1() -> None:
    pack = load_policy_pack("copilot-governance-v1")
    assert "copilot-governance-v1@1.0.0" == pack.version
    assert pack.minimum_confidence == 0.75
    assert "submit_payment_intent" in pack.forbidden_financial_actions
    document = load_pack_document("copilot-governance-v1")
    assert document["pack_type"] == "copilot-governance"


def test_governance_config_yaml() -> None:
    sample = Path("docs/spec/samples/governance-copilot-v1.yaml")
    config = load_governance_config(sample)
    assert config.policy_pack_id == "copilot-governance-v1"
    assert config.human_required is True
    assert config.max_cost_usd == 5.0
    assert config.config_hash.startswith("sha256:")


def test_gel_adapter_disabled_by_default() -> None:
    adapter = GelAdapter(base_url="")
    assert adapter.enabled is False
    assert adapter.evaluate_sync(tenant_id="t1", applicant_id="a1", request_id="RID-1") is None


def test_gel_decision_map() -> None:
    assert GEL_DECISION_MAP["APPROVE"] == "PROCEED"
    assert GEL_DECISION_MAP["DECLINE"] == "REJECT"


def test_control_plane_state_machine() -> None:
    assert advance_control_plane(ControlPlaneState.GOVERNANCE_CHECKED) == ControlPlaneState.EXECUTED
    assert advance_control_plane(ControlPlaneState.EXECUTED) == ControlPlaneState.ARCHIVED


def test_tle_audit_digest() -> None:
    body = {"tle_id": "TLE-1", "status": "Draft", "decision": "Go"}
    digest = compute_tle_audit_digest(body)
    assert digest.startswith("sha256:")
    body["audit_digest"] = digest
    assert compute_tle_audit_digest(body) == digest


def test_signature_key_id() -> None:
    assert signature_key_id("1.0.0") == "nf-governance-v1-1.0.0"


def test_bank_pilot_pack_loads() -> None:
    pack = load_policy_pack("bank-pilot-v1")
    assert pack.minimum_confidence == 0.80


def test_tle_signer_roundtrip() -> None:
    from noetfield_governance.tle_signer import sign_tle_body, verify_tle_signature

    body = {"tle_id": "TLE-1", "status": "Draft"}
    sig = sign_tle_body(body, key_id="nf-governance-v1-1.0.0")
    assert verify_tle_signature(body, sig)


def test_rid_lineage_binding() -> None:
    from noetfield_governance.governance_rid import bind_rid_lineage, generate_rid

    lineage = bind_rid_lineage(
        rid=generate_rid(),
        policy_refs=["copilot-governance-v1@1.0.0"],
        config_policy_version_hash="sha256:test",
    )
    assert "policy_version_hash" in lineage


def test_governance_sdk_constructor() -> None:
    gov = Governance("https://platform.noetfield.com", api_key="test", tenant_id=uuid4(), organization_id=uuid4())
    assert gov.client.base_url == "https://platform.noetfield.com"


def test_evaluate_response_includes_config_hash_field() -> None:
    from noetfield_governance.governance_v1 import GovernanceEvaluateV1Response

    response = GovernanceEvaluateV1Response(
        request_id="RID-TEST",
        mode="shadow",
        decision="PROCEED",
        allowed=True,
        reason="ok",
        reason_code="ALLOW",
        policy_version_hash="sha256:abc",
        config_policy_version_hash="sha256:def",
    )
    assert response.config_policy_version_hash == "sha256:def"
