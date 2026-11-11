"""E2E-in-process: stored intake feed -> existing Company OS events -> specialist task -> owner-review dependency."""
import json
import tempfile
import unittest
from pathlib import Path
import core


def contributor_signal(intake_id="INT-C0FFEE123456"):
    return {
        "intake_id": intake_id,
        "request_id": "RID-CONTRIBUTOR-001",
        "created_at": "2026-11-10T21:00:00+00:00",
        "sku": "general",
        "vector": "work-with-us-contributor",
        "qualification": None,
        "contributor": {
            "application_kind": "agent",
            "project_id": "buildrelay",
            "role": "qa",
        },
    }


class ContributorIntakeConsumerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.original_db = core.DB
        core.DB = Path(self.tmp.name) / "company.sqlite3"
        core.init()

    def tearDown(self):
        core.DB = self.original_db
        self.tmp.cleanup()

    def test_persisted_signal_creates_specialist_and_review_tasks_once(self):
        item = contributor_signal()
        first = core.queue_platform_intake_projection(item)
        self.assertTrue(first["created"])
        self.assertFalse(core.queue_platform_intake_projection(item)["created"])
        with core.connect() as db:
            event = dict(db.execute(
                "SELECT * FROM events WHERE id=?", (first["event_id"],)
            ).fetchone())
        core.process_platform_intake_signal(event)
        with core.connect() as db:
            rows = [dict(r) for r in db.execute(
                "SELECT id,role,objective,status FROM tasks WHERE event_id=?",
                (first["event_id"],)
            ).fetchall()]
            deps = db.execute("SELECT task_id,depends_on_task_id FROM task_dependencies").fetchall()
            status = db.execute(
                "SELECT status FROM platform_intake_signals WHERE intake_id=?",
                (item["intake_id"],)
            ).fetchone()["status"]
        self.assertEqual(len(rows), 2)
        self.assertEqual({r["role"] for r in rows}, {"engineering_operator", "chief_of_staff"})
        self.assertEqual(status, "tasks_created")
        self.assertEqual(len(deps), 1)
        self.assertIn("buildrelay", " ".join(r["objective"] for r in rows))
        self.assertIn("Not yet assigned", " ".join(
            r["content"] for r in core.connect().execute(
                "SELECT content FROM memories WHERE category='contributor_intake_signal'"
            ).fetchall()
        ))
        self.assertNotIn("@", json.dumps(rows))
        core.process_platform_intake_signal(event)
        with core.connect() as db:
            count = db.execute(
                "SELECT COUNT(*) FROM tasks WHERE event_id=?", (first["event_id"],)
            ).fetchone()[0]
        self.assertEqual(count, 2)

    def test_untrusted_structures_and_unknown_scope_are_not_admitted(self):
        for change in (
            {"role": "arbitrary_shell"},
            {"project_id": "other-tenant-secret"},
            {"application_kind": {"role": "root"}},
            {"contact_email": "private@example.invalid"},
        ):
            item = contributor_signal()
            item["contributor"].update(change)
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    core.validate_platform_intake_projection(item)

    def test_old_commercial_contract_still_accepts_unchanged_feed_items(self):
        item = {
            "intake_id": "INT-CAFEBABE1234",
            "request_id": None,
            "created_at": "2026-11-10T21:00:00+00:00",
            "sku": "general",
            "vector": "web-intake",
            "qualification": None,
        }
        accepted = core.validate_platform_intake_projection(item)
        self.assertNotIn("contributor", accepted)


if __name__ == "__main__":
    unittest.main()
