"""Typed, PII-free Noetfield Connect event -> existing Company OS work queue."""
import json
import tempfile
import unittest
from pathlib import Path
import core


def sample_signal(category="events", initiative="noetfield", intake_id="INT-ABCDEF246801"):
    return {
        "intake_id": intake_id,
        "request_id": "RID-CNX-ABCDEF246801",
        "created_at": "2026-11-12T20:00:00+00:00",
        "sku": "general",
        "vector": "external-opportunities",
        "qualification": None,
        "opportunity": {
            "category": category,
            "initiative": initiative,
            "requested_next_step": "meeting",
            "source_channel": "linkedin",
        },
    }


class ConnectOpportunityRoutingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = core.DB
        core.DB = Path(self.tmp.name) / "company.sqlite"
        core.init()

    def tearDown(self):
        core.DB = self.old
        self.tmp.cleanup()

    def test_event_typed_specialists_and_executive_dependency(self):
        item=sample_signal()
        created=core.queue_platform_intake_projection(item)
        self.assertTrue(created["created"])
        self.assertFalse(core.queue_platform_intake_projection(item)["created"])
        with core.connect() as db:
            e=dict(db.execute("SELECT * FROM events WHERE id=?", (created["event_id"],)).fetchone())
        core.process_platform_intake_signal(e)
        with core.connect() as db:
            tasks=[dict(r) for r in db.execute(
                "SELECT id,role,title,objective,next_action,status FROM tasks WHERE event_id=?",
                (created["event_id"],)).fetchall()]
            links=db.execute("SELECT task_id,depends_on_task_id FROM task_dependencies").fetchall()
            signal=db.execute("SELECT status FROM platform_intake_signals WHERE intake_id=?",
                              (item["intake_id"],)).fetchone()
        self.assertEqual(signal["status"], "tasks_created")
        self.assertEqual(len(tasks),3)
        self.assertEqual({t["role"] for t in tasks},{"partnerships","roi_analyst","chief_of_staff"})
        self.assertEqual(len(links),2)
        self.assertIn("source-backed", " ".join(t["next_action"] for t in tasks))
        self.assertIn("meeting", " ".join(t["objective"] for t in tasks))
        self.assertNotIn("@",json.dumps(tasks))
        core.process_platform_intake_signal(e)
        with core.connect() as db:
            count=db.execute("SELECT COUNT(*) FROM tasks WHERE event_id=?",
                             (created["event_id"],)).fetchone()[0]
        self.assertEqual(count,3)

    def test_founder_opportunity_desk_readback_is_real_and_pii_free(self):
        item=sample_signal(category="events")
        receipt=core.queue_platform_intake_projection(item)
        before=core.connect_opportunity_inbox(10)
        self.assertEqual(len(before),1)
        self.assertEqual(before[0]["review_state"],"queued")
        self.assertEqual(before[0]["advisory_tasks"],[])
        self.assertFalse(before[0]["actual_owner_assigned"])
        with core.connect() as db:
            event=dict(db.execute("SELECT * FROM events WHERE id=?",
                                  (receipt["event_id"],)).fetchone())
        core.process_platform_intake_signal(event)
        after=core.connect_opportunity_inbox(10)
        self.assertEqual(after[0]["review_state"],"tasks_created")
        self.assertEqual(after[0]["source_channel"],"linkedin")
        self.assertEqual(after[0]["category"],"events")
        self.assertEqual(len(after[0]["advisory_tasks"]),3)
        self.assertFalse(after[0]["confirmed_meeting"])
        self.assertIsNone(after[0]["verified_conversion"])
        self.assertNotIn("contact_email",json.dumps(after))
        self.assertNotIn("Sensitive Human",json.dumps(after))

    def test_category_picks_correct_existing_workforce_roles(self):
        cases={
            "business":{"sales_qualification","engineering_operator","chief_of_staff"},
            "people":{"partnerships","product_strategy","chief_of_staff"},
            "growth":{"sales_qualification","partnerships","chief_of_staff"},
            "capital":{"partnerships","roi_analyst","chief_of_staff"},
            "other":{"market_intelligence","partnerships","chief_of_staff"},
        }
        for i,(category,expected) in enumerate(cases.items()):
            with self.subTest(category=category):
                signal=sample_signal(category=category,intake_id=f"INT-ABCDEF{i:06X}")
                receipt=core.queue_platform_intake_projection(signal)
                with core.connect() as db:
                    event=dict(db.execute("SELECT * FROM events WHERE id=?",
                                          (receipt["event_id"],)).fetchone())
                core.process_platform_intake_signal(event)
                with core.connect() as db:
                    actual={row["role"] for row in db.execute(
                        "SELECT role FROM tasks WHERE event_id=?", (receipt["event_id"],)).fetchall()}
                self.assertEqual(actual,expected)

    def test_independent_venture_not_automatically_assigned(self):
        signal=sample_signal(category="partnership",initiative="trustfield")
        receipt=core.queue_platform_intake_projection(signal)
        with core.connect() as db:
            event=dict(db.execute("SELECT * FROM events WHERE id=?",(receipt["event_id"],)).fetchone())
        core.process_platform_intake_signal(event)
        with core.connect() as db:
            tasks=[dict(row) for row in db.execute(
                "SELECT brand,objective,next_action FROM tasks WHERE event_id=?",
                (receipt["event_id"],)).fetchall()]
        self.assertTrue(all(t["brand"]=="noetfield" for t in tasks))
        self.assertIn("consent", " ".join(t["objective"] for t in tasks))
        self.assertIn("No external outreach"," ".join(t["next_action"] for t in tasks))

    def test_untrusted_fields_rejected_before_any_queue_write(self):
        bad_values=[
            {"category":"shell"},
            {"initiative":"other-company-secret"},
            {"requested_next_step":"send_email_now"},
            {"source_channel":{"unsafe":"value"}},
            {"secret":"do not route"},
        ]
        for change in bad_values:
            item=sample_signal()
            item["opportunity"].update(change)
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    core.queue_platform_intake_projection(item)
        with core.connect() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM events").fetchone()[0],0)

    def test_existing_normal_and_contributor_contract_unchanged(self):
        generic={
            "intake_id":"INT-CAFEBABE1234",
            "request_id":None,
            "created_at":"2026-11-12T20:00:00+00:00",
            "sku":"general", "vector":"web-intake","qualification":None,
        }
        self.assertNotIn("opportunity",core.validate_platform_intake_projection(generic))
        with self.assertRaises(ValueError):
            core.validate_platform_intake_projection({
                **generic,"vector":"external-opportunities",
            })


if __name__=="__main__":
    unittest.main()
