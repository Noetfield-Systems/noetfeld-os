import importlib.util
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/validate_sina_founder_os_mission_envelope_v1.py"
spec = importlib.util.spec_from_file_location("sina_envelope_validator", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def valid_payload():
    return {
        "schema": "sina-founder-os.mission-envelope.v1",
        "envelope_id": "env-test-001",
        "company_id": "noetfield-systems-inc",
        "project_id": "noetfield-paperclip-commissioning",
        "origin": {"source": "founder-os", "actor": "founder-human-principal"},
        "objective": "Run a reversible contract validation pilot",
        "scope": {"repositories": ["Noetfield-Systems/noetfeld-os"]},
        "constraints": ["no production deploy", "no external send"],
        "acceptance_criteria": ["validator passes", "independent receipt exists"],
        "priority": "P1",
        "requested_by": "founder-human-principal",
        "decision_record_ref": "decision:test-001",
        "workpacket_ref": "workpacket:test-001",
        "authority_level": "A3",
        "budget_limit": {"currency": "USD", "max_cost": 1.0},
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
        "idempotency_key": "test-idempotency-001"
    }

def test_valid_envelope_validates_without_dispatch():
    result = module.validate(valid_payload())
    assert result["valid"] is True
    assert result["dispatch"] == "NOT_PERFORMED"

def test_missing_workpacket_is_rejected():
    payload = valid_payload()
    payload.pop("workpacket_ref")
    try:
        module.validate(payload)
        assert False, "expected missing workpacket rejection"
    except ValueError as exc:
        assert "workpacket_ref" in str(exc)

def test_wrong_company_tenant_is_rejected():
    payload = valid_payload()
    payload["company_id"] = "other-company"
    try:
        module.validate(payload)
        assert False, "expected tenant mismatch rejection"
    except ValueError as exc:
        assert "tenant mismatch" in str(exc)

def test_a4_authority_is_rejected():
    payload = valid_payload()
    payload["authority_level"] = "A4"
    try:
        module.validate(payload)
        assert False, "expected A4 rejection"
    except ValueError as exc:
        assert "A4" in str(exc)

def test_secret_field_is_rejected():
    payload = valid_payload()
    payload["provider_api_key"] = "do-not-accept"
    try:
        module.validate(payload)
        assert False, "expected secret rejection"
    except ValueError as exc:
        assert "secret-like" in str(exc)

def test_expired_mandate_is_rejected():
    payload = valid_payload()
    payload["expires_at"] = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    try:
        module.validate(payload)
        assert False, "expected expiry rejection"
    except ValueError as exc:
        assert "expired" in str(exc)
