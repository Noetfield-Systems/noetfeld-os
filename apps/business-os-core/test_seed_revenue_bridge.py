"""The Sina seed connector is read-only and never exports buyer personal data."""
import os
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import core
import app
from fastapi import HTTPException


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
            with self.assertRaises(HTTPException) as denied:
                app.sina_revenue_queue("any")
            self.assertEqual(denied.exception.status_code, 503)
        with patch.dict(os.environ, {"SINA_SEED_BRIDGE_TOKEN": "strong-test-token"}):
            for credential in (None, "wrong"):
                with self.assertRaises(HTTPException) as denied:
                    app.sina_revenue_queue(credential)
                self.assertEqual(denied.exception.status_code, 401)
            result = app.sina_revenue_queue("strong-test-token")
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
