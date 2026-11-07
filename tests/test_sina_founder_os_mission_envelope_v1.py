import importlib.util
import unittest
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

class FounderEnvelopeTests(unittest.TestCase):
    def test_valid_envelope_validates_without_dispatch(self):
        result = module.validate(valid_payload())
        self.assertTrue(result["valid"])
        self.assertEqual(result["dispatch"], "NOT_PERFORMED")

    def test_missing_workpacket_is_rejected(self):
        payload = valid_payload()
        payload.pop("workpacket_ref")
        with self.assertRaisesRegex(ValueError, "workpacket_ref"):
            module.validate(payload)

    def test_wrong_company_tenant_is_rejected(self):
        payload = valid_payload()
        payload["company_id"] = "other-company"
        with self.assertRaisesRegex(ValueError, "tenant mismatch"):
            module.validate(payload)

    def test_a4_authority_is_rejected(self):
        payload = valid_payload()
        payload["authority_level"] = "A4"
        with self.assertRaisesRegex(ValueError, "A4"):
            module.validate(payload)

    def test_secret_field_is_rejected(self):
        payload = valid_payload()
        payload["provider_api_key"] = "not-allowed"
        with self.assertRaisesRegex(ValueError, "secret-like"):
            module.validate(payload)

    def test_expired_mandate_is_rejected(self):
        payload = valid_payload()
        payload["expires_at"] = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
        with self.assertRaisesRegex(ValueError, "expired"):
            module.validate(payload)

if __name__ == "__main__":
    unittest.main()
