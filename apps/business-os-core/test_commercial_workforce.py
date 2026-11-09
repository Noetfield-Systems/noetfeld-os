"""Commercial workforce onboarding regression checks. Run from apps/business-os-core:
python -m unittest -v test_commercial_workforce
"""
import tempfile
import unittest
from pathlib import Path
import core


class CommercialWorkforceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        core.DB = Path(self.tmp.name) / "commercial.sqlite3"
        core.init()

    def tearDown(self):
        self.tmp.cleanup()

    def test_existing_seats_reused_without_new_scheduler(self):
        role_map = {r["role"]: r for r in core.agent_roster()}
        self.assertEqual(role_map["sales_qualification"]["company_role_id"], "N-05")
        self.assertEqual(role_map["customer_success"]["company_role_id"], "N-07")
        self.assertEqual(role_map["marketing_editorial"]["company_role_id"], "N-06")
        self.assertEqual(role_map["marketing_editorial"]["tier"], "draft")
        self.assertEqual(role_map["marketing_editorial"]["company_role_activation"], "draft_only")

    def test_customer_and_support_intent_override_brand_sales_routing(self):
        for brand in ("noetfield", "trustfield", "buildworkflow"):
            self.assertEqual(core.route_for(brand, "customer", "support")[1], "customer_success")
            self.assertEqual(core.route_for(brand, "enterprise", "support")[1], "customer_success")
        self.assertEqual(core.route_for("trustfield", "enterprise", "trustfield")[1], "sales_qualification")
        self.assertEqual(core.route_for("noetfield", "enterprise", "automation")[1], "sales_qualification")

    def test_real_support_inbound_creates_approval_gated_work(self):
        payload = {
            "brand": "trustfield",
            "audience": "customer",
            "intent": "support",
            "name": "Sample Customer",
            "email": "customer@example.test",
            "company": "Example Demo Company",
            "role": "Administrator",
            "problem": "I need help finding the case review export for our workflow.",
            "urgency": "now",
            "estimated_value": 0,
            "consent": True,
            "ai_consent": False,
        }
        event_id = core.add_event("intake.received", "test", "trustfield", payload)
        e = core.claim("events")
        self.assertEqual(e["id"], event_id)
        core.process_event(e)
        with core.connect() as db:
            roles = [r["role"] for r in db.execute(
                "SELECT role FROM tasks WHERE event_id=?", (event_id,)).fetchall()]
            ex = db.execute(
                "SELECT status FROM events WHERE id=?", (event_id,)).fetchone()
        self.assertEqual(ex["status"], "processed")
        self.assertIn("customer_success", roles)
        self.assertIn("chief_of_staff", roles)
        self.assertNotIn("sales_qualification", roles)

    def test_marketing_agent_is_internal_draft_only(self):
        with core.connect() as db:
            task_id = core.add_task(
                db, None, None, "noetfield", "marketing_editorial",
                "Prepare workflow acceptance content",
                "Write a claims-bound and evidence-backed draft about human acceptance of AI results.",
                "Draft for human review only. Never publish.",
            )
        t = core.claim("tasks")
        self.assertEqual(t["id"], task_id)
        core.process_task(t)
        with core.connect() as db:
            task = db.execute("SELECT status,autonomy,result FROM tasks WHERE id=?", (task_id,)).fetchone()
            audit = db.execute("SELECT provider FROM runs WHERE task_id=?", (task_id,)).fetchone()
        self.assertEqual(task["status"], "drafted")
        self.assertEqual(task["autonomy"], "draft")
        self.assertEqual(audit["provider"], "deterministic")
        self.assertNotIn("published", task["status"])


if __name__ == "__main__":
    unittest.main()
