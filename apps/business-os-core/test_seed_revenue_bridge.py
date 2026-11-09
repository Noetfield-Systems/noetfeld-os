"""The Sina seed connector is read-only and never exports buyer personal data."""
import os
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import core

class SinaSeedRevenueBridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.previous = core.DB
        core.DB = Path(self.tmp.name) / "core.sqlite"
        core.init()

    def tearDown(self):
        core.DB = self.previous
        self.tmp.cleanup()

    def test_bridge_fails_closed_and_returns_only_typed_signal_fields(self):
        signal = {
            "intake_id": "INT-ABCDEF123456",
            "request_id": "RID-TEST123-ABC",
            "created_at": "2026-11-09T05:00:00+00:00",
            "sku": "copilot",
            "vector": "copilot-governance",
            "qualification": {
                "tier": "A",
                "fit_score": 88,
                "urgency": "immediate",
                "next_step": "schedule_briefing",
                "owner_sla_hours": 24,
                "blockers": [],
                "qualifier_version": "enterprise-intake-qualifier-v1",
            },
        }
        core.queue_platform_intake_projection(signal)
        with patch.dict(os.environ, {"SINA_SEED_BRIDGE_TOKEN": ""}):
            self.assertFalse(core.sina_bridge_authorized("any"))
        with patch.dict(os.environ, {"SINA_SEED_BRIDGE_TOKEN": "strong-test-token"}):
            self.assertFalse(core.sina_bridge_authorized(None))
            self.assertFalse(core.sina_bridge_authorized("wrong"))
            self.assertTrue(core.sina_bridge_authorized("strong-test-token"))
            items=core.sina_seed_revenue_items()
        result={
            "schema":"noetfield.sina-seed.revenue-queue.v1",
            "pii_included":False,"items":items,
        }
        self.assertEqual(result["schema"], "noetfield.sina-seed.revenue-queue.v1")
        self.assertIs(result["pii_included"], False)
        self.assertEqual(result["items"][0]["tier"], "A")
        self.assertEqual(result["items"][0]["intake_id"], signal["intake_id"])
        self.assertEqual(result["items"][0]["sales_task_status"], "not_created")
        forbidden = {"contact_email", "organization", "message", "contact_name", "request_id"}
        self.assertFalse(forbidden.intersection(result["items"][0]))
        self.assertNotIn("private@example.com", json.dumps(result))


if __name__ == "__main__":
    unittest.main()
