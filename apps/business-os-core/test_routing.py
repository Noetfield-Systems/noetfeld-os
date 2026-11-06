import tempfile
import unittest
from pathlib import Path

import core


class BusinessOSRoutingTests(unittest.TestCase):
    def test_brand_routes_are_separate(self):
        self.assertEqual(core.route_for("buildworkflow", "operator", "buildworkflow")[0], "trade_operations")
        self.assertEqual(core.route_for("trustfield", "enterprise", "trustfield")[0], "regulated_enterprise")
        self.assertEqual(core.route_for("buildrelay", "investor", "investment")[0], "capital_partner")

    def test_urgency_increases_fit_score(self):
        low = core.score("operator", "automation", "exploring", 10000, "Improve operations and workflow")
        high = core.score("operator", "automation", "now", 10000, "Improve operations and workflow")
        self.assertGreater(high, low)

    def test_agent_roles_are_unique(self):
        roles = [agent[0] for agent in core.AGENTS]
        self.assertEqual(len(roles), len(set(roles)))
        self.assertIn("roi_analyst", roles)
        self.assertIn("risk_governance", roles)


class BusinessOSCycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        core.DB = Path(self.temp.name) / "test.sqlite"
        core.init()

    def tearDown(self):
        self.temp.cleanup()

    def test_intake_event_routes_creates_tasks_and_executes_agent(self):
        payload = {
            "brand": "buildworkflow",
            "audience": "operator",
            "intent": "buildworkflow",
            "name": "Test Operator",
            "email": "operator@example.test",
            "company": "Test Mechanical",
            "role": "Operations Manager",
            "problem": "HVAC extra work tickets are delayed before reaching the office.",
            "urgency": "now",
            "estimated_value": 12000,
            "consent": True,
            "ai_consent": False,
        }
        event_id = core.add_event("intake.received", "unit_test", "buildworkflow", payload)
        event = core.claim("events")
        self.assertEqual(event["id"], event_id)
        core.process_event(event)

        with core.connect() as db:
            stored = db.execute("SELECT status FROM events WHERE id=?", (event_id,)).fetchone()
            opp = db.execute("SELECT * FROM opportunities WHERE source='unit_test'").fetchone()
            tasks = db.execute("SELECT COUNT(*) n FROM tasks WHERE event_id=?", (event_id,)).fetchone()["n"]
        self.assertEqual(stored["status"], "processed")
        self.assertEqual(opp["route"], "trade_operations")
        self.assertEqual(opp["score"] >= 65, True)
        self.assertEqual(tasks, 3)

        drafted_task = core.claim("tasks")
        self.assertEqual(drafted_task["ai_consent"], 0)
        core.process_task(drafted_task)
        with core.connect() as db:
            status = db.execute("SELECT status FROM tasks WHERE id=?", (drafted_task["id"],)).fetchone()["status"]
            run = db.execute("SELECT provider FROM runs WHERE task_id=?", (drafted_task["id"],)).fetchone()
        self.assertEqual(status, "drafted")
        self.assertEqual(run["provider"], "deterministic")

        self.assertTrue(core.retrieve("buildworkflow", "HVAC extra work tickets"))
        self.assertFalse(core.retrieve("trustfield", "HVAC extra work tickets"))

    def test_memory_is_chunked_and_pii_redacted(self):
        long_text = ("Operational workflow evidence. " * 70) + " UNIQUE FINAL HVAC ROUTING SIGNAL. "
        core.add_memory("buildworkflow", "test", "source-1",
            "Contact user@example.test at +1 (604) 555-1234. " + long_text)
        with core.connect() as db:
            chunks = db.execute("SELECT content FROM memories WHERE source_id='source-1'").fetchall()
        self.assertGreater(len(chunks), 1)
        joined = " ".join(row["content"] for row in chunks)
        self.assertNotIn("user@example.test", joined)
        self.assertNotIn("604) 555-1234", joined)
        self.assertIn("[redacted email]", joined)
        self.assertTrue(core.retrieve("buildworkflow", "UNIQUE FINAL HVAC ROUTING SIGNAL"))

    def test_stale_event_lease_is_recovered(self):
        event_id = core.add_event("unsupported.test", "unit_test", "portfolio", {})
        first = core.claim("events")
        self.assertEqual(first["id"], event_id)
        with core.connect() as db:
            db.execute("UPDATE events SET claimed_at=datetime('now','-4 minutes') WHERE id=?", (event_id,))
        second = core.claim("events")
        self.assertEqual(second["id"], event_id)
        with core.connect() as db:
            attempts = db.execute("SELECT attempts FROM events WHERE id=?", (event_id,)).fetchone()["attempts"]
        self.assertEqual(attempts, 2)

if __name__ == "__main__":
    unittest.main()



class BusinessOSGovernanceTests(unittest.TestCase):
    def test_agent_roster_is_complete_and_managers_exist(self):
        roster = core.agent_roster()
        roles = {row["role"] for row in roster}
        self.assertEqual(roles, {row[0] for row in core.AGENTS})
        for row in roster:
            manager = row["reports_to"]
            if manager is not None:
                self.assertIn(manager, roles)
        self.assertIsNone(next(row for row in roster if row["role"] == "chief_of_staff")["reports_to"])

    def test_executive_task_waits_for_specialist_dependencies(self):
        with core.connect() as db:
            specialist_a = core.add_task(
                db, None, None, "noetfield", "sales_qualification",
                "Qualify lead", "Assess buyer fit and urgency", "Draft next action"
            )
            specialist_b = core.add_task(
                db, None, None, "noetfield", "risk_governance",
                "Review risk", "Assess consent and privacy risks", "Flag blockers"
            )
            executive = core.add_task(
                db, None, None, "noetfield", "chief_of_staff",
                "Executive synthesis", "Consolidate specialist findings", "Prepare brief"
            )
            core.add_task_dependency(db, executive, specialist_a)
            core.add_task_dependency(db, executive, specialist_b)

        first = core.claim("tasks")
        self.assertIn(first["id"], {specialist_a, specialist_b})
        core.process_task(first)
        second = core.claim("tasks")
        self.assertIn(second["id"], {specialist_a, specialist_b})
        self.assertNotEqual(second["id"], first["id"])
        core.process_task(second)
        third = core.claim("tasks")
        self.assertEqual(third["id"], executive)

    def test_agent_hierarchy_is_three_layers_and_executive_review_is_a_role(self):
        roster = core.agent_roster()
        self.assertEqual(max(row["layer"] for row in roster), 2)
        self.assertIn("chief_of_staff", {row["role"] for row in roster})
