import tempfile
import unittest
from pathlib import Path

import client_status
import core


class CustomerIntakeStatusTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        core.DB = Path(self.temp.name) / "business.db"
        core.init()
        client_status.init()
        client_status.POLL_HITS.clear()
        self.payload = {
            "brand": "noetfield",
            "audience": "founder",
            "intent": "automation",
            "name": "Tester",
            "email": "person@example.test",
            "company": "Example Co",
            "role": "Product owner",
            "problem": "Streamline product onboarding and improve our own CRM pipeline.",
            "urgency": "exploring",
            "estimated_value": 0,
            "consent": True,
            "ai_consent": False,
        }
        self.event_id = core.add_event("intake.received", "test", "noetfield", self.payload)
        self.token = client_status.issue(self.event_id)

    def tearDown(self):
        self.temp.cleanup()

    def test_issue_is_random_and_has_only_read_progress_authority(self):
        self.assertTrue(self.token)
        first = client_status.snapshot(self.event_id, self.token)
        self.assertEqual(first["stage"], "intake_queued")
        self.assertEqual(first["customer_workpacket"], "NOT_DISPATCHED")
        self.assertEqual(first["independent_verification"], "NOT_PERFORMED")
        self.assertEqual(first["artifacts_shared"], 0)
        self.assertNotIn(self.payload["email"], str(first))
        self.assertNotIn(self.payload["problem"], str(first))

    def test_token_bound_to_exact_event_and_missing_or_wrong_token_is_denied(self):
        other = core.add_event("intake.received", "test", "noetfield", self.payload)
        other_token = client_status.issue(other)
        self.assertIsNone(client_status.snapshot(self.event_id, other_token))
        self.assertIsNone(client_status.snapshot(other, self.token))
        self.assertIsNone(client_status.snapshot(self.event_id, "not-a-token"))
        self.assertIsNone(client_status.snapshot("evt_bad", self.token))
        with core.connect() as db:
            row = db.execute("SELECT token_sha256 FROM intake_progress_capabilities WHERE event_id=?", (self.event_id,)).fetchone()
        self.assertNotIn(self.token, row["token_sha256"])

    def test_tracks_real_specialist_dependency_cycle_without_exposing_business_data(self):
        core.process_event(core.claim("events"))
        snap = client_status.snapshot(self.event_id, self.token)
        self.assertEqual(snap["tasks_total"], 4)
        self.assertEqual(snap["stage"], "specialists_working")
        self.assertEqual(snap["tasks_drafted"], 0)
        self.assertEqual({v["status"] for v in snap["roles"]}, {"queued"})
        self.assertNotIn(self.payload["email"], str(snap))
        for _ in range(4):
            task = core.claim("tasks")
            self.assertIsNotNone(task)
            core.process_task(task)
        final = client_status.snapshot(self.event_id, self.token)
        self.assertEqual(final["tasks_drafted"], 4)
        self.assertEqual(final["tasks_total"], 4)
        self.assertEqual(final["stage"], "internal_drafts_ready")
        self.assertEqual(final["external_execution"], "NOT_AUTHORIZED")
        self.assertNotIn("result", final)
        self.assertNotIn("evidence", final)

    def test_failure_and_revocation_and_poll_limit(self):
        with core.connect() as db:
            db.execute("UPDATE events SET status='failed' WHERE id=?", (self.event_id,))
        self.assertEqual(client_status.snapshot(self.event_id, self.token)["stage"], "intake_failed")
        for _ in range(19):
            self.assertNotIn("rate_limited",client_status.snapshot(self.event_id, self.token))
        self.assertTrue(client_status.snapshot(self.event_id, self.token)["rate_limited"])
        with core.connect() as db:
            db.execute("UPDATE intake_progress_capabilities SET revoked_at=? WHERE event_id=?", (core.now(),self.event_id))
        self.assertIsNone(client_status.snapshot(self.event_id,self.token))


if __name__ == "__main__":
    unittest.main()
