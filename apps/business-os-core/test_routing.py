import json
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
        # Three specialist roles plus the dependency-gated executive synthesis.
        self.assertEqual(tasks, 4)

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



    def test_platform_intake_projection_is_idempotent_pii_free_and_not_a_sales_opportunity(self):
        item = {
            "intake_id": "INT-ABCDEF123456",
            "request_id": "RID-TEST123-ABC",
            "created_at": "2026-11-08T10:00:00+00:00",
            "sku": "trust_brief",
            "vector": "ai-value-governance-os",
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
        first = core.queue_platform_intake_projection(item)
        second = core.queue_platform_intake_projection(item)
        self.assertTrue(first["created"])
        self.assertFalse(second["created"])
        self.assertEqual(first["event_id"], second["event_id"])
        with core.connect() as db:
            signals = db.execute("SELECT COUNT(*) n FROM platform_intake_signals").fetchone()["n"]
            events = db.execute("SELECT COUNT(*) n FROM events WHERE event_type='platform.intake.signal.received'").fetchone()["n"]
        self.assertEqual(signals, 1)
        self.assertEqual(events, 1)

        event = core.claim("events")
        core.process_event(event)
        with core.connect() as db:
            signal = db.execute("SELECT status FROM platform_intake_signals WHERE intake_id=?", (item["intake_id"],)).fetchone()
            contacts = db.execute("SELECT COUNT(*) n FROM contacts").fetchone()["n"]
            opportunities = db.execute("SELECT COUNT(*) n FROM opportunities").fetchone()["n"]
            tasks = db.execute("SELECT role,priority_rank FROM tasks WHERE event_id=? ORDER BY role", (event["id"],)).fetchall()
            task_event = db.execute("SELECT status FROM events WHERE id=?", (event["id"],)).fetchone()
        self.assertEqual(signal["status"], "tasks_created")
        self.assertEqual(contacts, 0)
        self.assertEqual(opportunities, 0)
        self.assertEqual(task_event["status"], "processed")
        self.assertEqual({row["role"] for row in tasks}, {"sales_qualification", "chief_of_staff"})
        self.assertTrue(all(row["priority_rank"] == 10 for row in tasks))

        task = core.claim("tasks")
        self.assertEqual(task["role"], "sales_qualification")
        core.process_task(task)
        with core.connect() as db:
            run = db.execute("SELECT provider FROM runs WHERE task_id=?", (task["id"],)).fetchone()
            task_row = db.execute("SELECT objective,next_action FROM tasks WHERE id=?", (task["id"],)).fetchone()
        self.assertEqual(run["provider"], "deterministic")
        self.assertNotIn("email", task_row["objective"].lower())
        self.assertNotIn("contact", task_row["objective"].lower())
        self.assertIn("do not send", task_row["next_action"].lower())

    def test_revenue_agent_creates_real_action_packet_without_fabricating_buyer_or_sending(self):
        item = {
            "intake_id": "INT-ABCDEF123456",
            "request_id": "RID-TEST123-ABC",
            "created_at": "2026-11-08T10:00:00+00:00",
            "sku": "copilot",
            "vector": "copilot-governance",
            "qualification": {
                "tier": "A", "fit_score": 91, "urgency": "immediate",
                "next_step": "schedule_briefing", "owner_sla_hours": 24,
                "blockers": [], "qualifier_version": "enterprise-intake-qualifier-v1",
            },
        }
        core.queue_platform_intake_projection(item)
        core.process_event(core.claim("events"))
        sales=core.claim("tasks")
        self.assertEqual(sales["role"],"sales_qualification")
        core.process_task(sales)
        with core.connect() as db:
            sales_row=db.execute("SELECT result FROM tasks WHERE id=?",(sales["id"],)).fetchone()
        drafted=json.loads(sales_row["result"])
        action=drafted["recommendation"]["commercial_action"]
        self.assertEqual(action["intake_id"],item["intake_id"])
        self.assertEqual(action["commercial_state"],"unverified_inquiry")
        self.assertEqual(action["response_due_at"],"2026-11-09T10:00:00+00:00")
        self.assertEqual(action["offer_candidate"],"NF-QS Copilot QuickScan")
        self.assertFalse(action["buyer_identity_verified"])
        self.assertFalse(action["willingness_to_pay_verified"])
        self.assertTrue(action["founder_approval_required"])
        self.assertFalse(action["external_action_executed"])
        self.assertEqual(action["response_draft"]["state"],"internal_draft_not_sent")
        executive=core.claim("tasks")
        self.assertEqual(executive["role"],"chief_of_staff")
        core.process_task(executive)
        with core.connect() as db:
            executive_row=db.execute("SELECT result FROM tasks WHERE id=?",(executive["id"],)).fetchone()
            count=db.execute("SELECT COUNT(*) n FROM opportunities").fetchone()["n"]
        executive_result=json.loads(executive_row["result"])["recommendation"]
        self.assertEqual(executive_result["specialist_drafts"]["sales_qualification"]["status"],"drafted")
        self.assertEqual(executive_result["commercial_action"]["intake_id"],item["intake_id"])
        self.assertEqual(count,0)
        self.assertEqual(executive_result["commercial_action"]["response_draft"]["state"],"internal_draft_not_sent")

    def test_blocked_signal_never_generates_outreach_and_legacy_draft_gets_requeued(self):
        item = {
            "intake_id":"INT-BCDEF1234567",
            "request_id":None,"created_at":"2026-11-08T10:00:00+00:00",
            "sku":"bank_pilot","vector":"bank-pilot",
            "qualification":{
                "tier":"A","fit_score":90,"urgency":"immediate",
                "next_step":"founder_review","owner_sla_hours":24,
                "blockers":["payment_rails"],
                "qualifier_version":"enterprise-intake-qualifier-v1",
            },
        }
        core.queue_platform_intake_projection(item)
        core.process_event(core.claim("events"))
        sales=core.claim("tasks")
        core.process_task(sales)
        with core.connect() as db:
            first=json.loads(db.execute("SELECT result FROM tasks WHERE id=?",(sales["id"],)).fetchone()["result"])
            self.assertIsNone(first["recommendation"]["commercial_action"]["response_draft"])
            db.execute("UPDATE tasks SET result=? WHERE id=?",(
                json.dumps({"recommendation":{"assessment":"Deterministic processing."}}),sales["id"]
            ))
        core.requeue_legacy_platform_drafts()
        with core.connect() as db:
            self.assertEqual(db.execute("SELECT status FROM tasks WHERE id=?",(sales["id"],)).fetchone()["status"],"queued")
        rerun=core.claim("tasks")
        self.assertEqual(rerun["id"],sales["id"])
        core.process_task(rerun)
        with core.connect() as db:
            updated=json.loads(db.execute("SELECT result FROM tasks WHERE id=?",(sales["id"],)).fetchone()["result"])
        self.assertIsNone(updated["recommendation"]["commercial_action"]["response_draft"])
        self.assertIn("external_approval_required",updated["recommendation"]["risk_flags"])

    def test_platform_intake_projection_rejects_pii_and_untrusted_extra_fields(self):
        base = {
            "intake_id": "INT-ABCDEF123456",
            "request_id": None,
            "created_at": "2026-11-08T10:00:00+00:00",
            "sku": "trust_brief",
            "vector": "ai-value-governance-os",
            "qualification": None,
        }
        injected = dict(base)
        injected["contact_email"] = "private@example.com"
        with self.assertRaises(ValueError):
            core.validate_platform_intake_projection(injected)
        injected = dict(base)
        injected["vector"] = "private@example.com"
        with self.assertRaises(ValueError):
            core.validate_platform_intake_projection(injected)

    def test_platform_intake_tier_priority_precedes_older_low_value_internal_work(self):
        low = {
            "intake_id": "INT-ABCDEF123456",
            "request_id": None,
            "created_at": "2026-11-08T10:00:00+00:00",
            "sku": "trust_brief",
            "vector": "ai-value-governance-os",
            "qualification": {
                "tier": "C", "fit_score": 40, "urgency": "low", "next_step": "async_nurture",
                "owner_sla_hours": 72, "blockers": [], "qualifier_version": "enterprise-intake-qualifier-v1"
            },
        }
        high = {
            **low,
            "intake_id": "INT-BCDEF1234567",
            "qualification": {
                "tier": "A", "fit_score": 90, "urgency": "immediate", "next_step": "schedule_briefing",
                "owner_sla_hours": 24, "blockers": [], "qualifier_version": "enterprise-intake-qualifier-v1"
            },
        }
        core.queue_platform_intake_projection(low)
        core.queue_platform_intake_projection(high)
        with core.connect() as db:
            old_task = core.add_task(db,None,None,"noetfield","market_intelligence","Old routine task","Routine task objective","Internal note")
        core.process_event(core.claim("events"))
        core.process_event(core.claim("events"))
        first = core.claim("tasks")
        self.assertEqual(first["role"], "sales_qualification")
        self.assertEqual(first["priority_rank"], 10)


class BusinessOSGovernanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        core.DB = Path(self.temp.name) / "test.sqlite"
        core.init()

    def tearDown(self):
        self.temp.cleanup()

    def test_canonical_workforce_has_eight_roles_and_valid_reporting_lines(self):
        roster = core.company_workforce_roster()
        role_ids = {row["role_id"] for row in roster}
        self.assertEqual(len(roster), 8)
        self.assertEqual(role_ids, {f"N-{n:02d}" for n in range(1, 9)})
        for row in roster:
            self.assertIn(row["reports_to"], role_ids | {"H-001"})
        self.assertEqual(core.FOUNDER_SEAT["role_id"], "H-001")
        self.assertEqual(
            core.WORKFORCE_BINDING["canonical_source"]["git_blob_sha"],
            "5664f6aa87ee24b7eb1d703baee09b2c16ebe164",
        )
        n06 = next(row for row in roster if row["role_id"] == "N-06")
        self.assertEqual(n06["runtime_role_count"], 1)
        self.assertIn("marketing_editorial", n06["runtime_role_names"])
        self.assertEqual(core.company_role_for_runtime("marketing_editorial")["role_id"], "N-06")
        self.assertEqual(n06["activation_status"], "draft_only")

    def test_every_runtime_capability_maps_to_a_canonical_company_seat(self):
        roster = core.agent_roster()
        roles = {a[0] for a in core.AGENTS}
        company_roles = {row["role_id"] for row in core.company_workforce_roster()}
        self.assertEqual({row["role"] for row in roster}, roles)
        self.assertEqual(set(core.RUNTIME_ROLE_TO_COMPANY_ROLE), roles)
        self.assertTrue(set(core.RUNTIME_ROLE_TO_COMPANY_ROLE.values()).issubset(company_roles))
        for row in roster:
            self.assertIn(row["company_role_id"], company_roles)
            self.assertEqual(row["runtime_scope"], "internal_task_executor")

    def test_company_workforce_has_founder_plus_two_role_layers(self):
        roster = core.company_workforce_roster()
        self.assertEqual(max(row["layer"] for row in roster), 2)
        self.assertEqual(
            {row["role_id"]: row["reports_to"] for row in roster}["N-07"],
            "N-05",
        )
        self.assertEqual(
            {row["role_id"]: row["reports_to"] for row in roster}["N-08"],
            "H-001",
        )

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

    def test_specialist_prompt_is_bound_to_canonical_company_seat(self):
        # A non-model task still receives the canonical seat and authority in its result.
        with core.connect() as db:
            task = core.add_task(
                db, None, None, "noetfield", "sales_qualification",
                "Qualify buyer", "Assess urgency and buyer authority", "Draft next step"
            )
        claimed = core.claim("tasks")
        self.assertEqual(claimed["id"], task)
        core.process_task(claimed)
        with core.connect() as db:
            row = db.execute("SELECT result FROM tasks WHERE id=?", (task,)).fetchone()
        result = json.loads(row["result"])["recommendation"]
        self.assertEqual(result["company_role_id"], "N-05")
        self.assertEqual(result["company_role_authority"], "A2")

if __name__ == "__main__":
    unittest.main()
