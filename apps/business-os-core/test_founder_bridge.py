"""Real canonical Company OS SQLite queue tests; network I/O mocked only."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import core
import founder_bridge


def request(request_id="a" * 32, project_id="noetfield-company-os-commercial-product"):
    return {
        "schema": "sina.company-os.workpacket-request.v1",
        "request_id": request_id,
        "program_id": "b" * 32,
        "origin": "sina_autonomous_organization",
        "authority": "ADVISORY_ONLY_NO_PERMIT",
        "company_id": "noetfield-systems-inc",
        "tenant_scope": "noetfield-systems-inc",
        "project_id": project_id,
        "business_outcome": "Improve workflow reliability for real customer usage",
        "functional_unit": "product",
        "requested_role": "product_engineer",
        "task": "Investigate known onboarding problems and propose a bounded engineering improvement with actual evidence.",
        "priority_score": 81,
        "resources": {"budget_usd": 0, "financial_effect_allowed": False},
        "dependencies": [],
        "acceptance": ["Evidence linked; approved permits before effects"],
        "governance": {
            "governor_decision_required": True,
            "NAC_workpacket_required": True,
            "independent_verifier_required": True,
            "a4_human_reserved": True,
            "self_verification_allowed": False,
            "customer_outreach_allowed": False,
            "production_mutation_allowed": False,
            "cross_tenant_access": False,
        },
        "routing_state": "NOT_DISPATCHED_COMPANY_OS_OWNS_EXECUTION",
    }


class CompanyFounderContinuousBridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_db = core.DB
        core.DB = Path(self.tmp.name) / "company.sqlite3"
        self.old_env = dict(os.environ)
        core.init()
        founder_bridge.init()
        os.environ["SINA_ORG_BRIDGE_PROJECT_IDS"] = "noetfield-company-os-commercial-product,venture-formation-lab"
        os.environ["SINA_ORG_BRIDGE_ENABLED"] = "true"
        os.environ["SINA_ORG_CONTINUOUS_TOKEN"] = "test_" + "x" * 48

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.old_env)
        core.DB = self.old_db
        self.tmp.cleanup()

    def test_exact_scope_advisory_only_no_unlicensed_effect(self):
        item = request()
        for bad in [
            {"authority": "EXECUTE"},
            {"tenant_scope": "other-company"},
            {"project_id": "unknown-project"},
            {"resources": {"budget_usd": 10, "financial_effect_allowed": True}},
            {"governance": {**item["governance"], "production_mutation_allowed": True}},
            {"task": "Please message alice@example.com about our plan"},
            {"functional_unit": "verification"},
        ]:
            with self.subTest(bad=bad):
                with self.assertRaises(founder_bridge.UnsafeRequest):
                    founder_bridge.admit({**item, **bad}, founder_bridge._allowed_projects())
        with core.connect() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0], 0)

    def test_idempotent_admission_uses_canonical_worker_and_fails_on_mutation(self):
        first = request()
        tid, created = founder_bridge.admit(first, founder_bridge._allowed_projects())
        same, again = founder_bridge.admit(first, founder_bridge._allowed_projects())
        self.assertTrue(created)
        self.assertFalse(again)
        self.assertEqual(tid, same)
        self.assertTrue(tid.startswith("task_"))
        with core.connect() as db:
            rows = db.execute("SELECT * FROM tasks").fetchall()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["role"], "product_strategy")
            self.assertEqual(rows[0]["autonomy"], "draft")
            self.assertEqual(rows[0]["opportunity_id"], None)
            self.assertEqual(rows[0]["status"], "queued")
        with self.assertRaises(founder_bridge.UnsafeRequest):
            founder_bridge.admit({**first, "priority_score": 100}, founder_bridge._allowed_projects())

        claimed = core.claim("tasks")
        self.assertEqual(claimed["id"], tid)
        core.process_task(claimed)
        with core.connect() as db:
            t = db.execute("SELECT status,result FROM tasks WHERE id=?", (tid,)).fetchone()
            self.assertEqual(t["status"], "drafted")
            self.assertEqual(json.loads(t["result"])["external_action"], "not_executed")

    def test_acknowledgement_progress_and_retry_are_independent_of_external_execution(self):
        tid, _ = founder_bridge.admit(request(), founder_bridge._allowed_projects())
        replies = []
        def ack(method, path, payload=None):
            self.assertEqual(method, "POST")
            self.assertEqual(path, "/api/v2/organization/company/ack")
            replies.append(payload.copy())
            return {"workstream_id": payload["workstream_id"], "verified": False}
        with patch.object(founder_bridge, "_request", side_effect=ack):
            self.assertEqual(founder_bridge.reconcile(), 1)
            self.assertEqual(replies[-1]["status"], "ACCEPTED")
            self.assertEqual(replies[-1]["task_id"], tid)
            self.assertEqual(founder_bridge.reconcile(), 0)
            core.process_task(core.claim("tasks"))
            self.assertEqual(founder_bridge.reconcile(), 1)
            self.assertEqual(replies[-1]["status"], "DRAFTED")
            self.assertEqual(founder_bridge.reconcile(), 0)
        with core.connect() as db:
            self.assertEqual(db.execute("SELECT last_acked FROM founder_org_bindings").fetchone()[0], "DRAFTED")

    def test_rejected_http_ack_retains_pending_and_retries_after_restart(self):
        tid, _ = founder_bridge.admit(request(), founder_bridge._allowed_projects())
        with patch.object(founder_bridge, "_request", side_effect=OSError("Founder unavailable")):
            with self.assertRaises(OSError):
                founder_bridge.reconcile()
        with core.connect() as db:
            self.assertEqual(db.execute("SELECT last_acked FROM founder_org_bindings").fetchone()[0], "")
            self.assertEqual(db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0], 1)
        with patch.object(founder_bridge, "_request", return_value={"workstream_id": "a" * 32}):
            self.assertEqual(founder_bridge.reconcile(), 1)
        with core.connect() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0], 1)

    def test_commercial_signal_only_on_real_processed_public_intake(self):
        def add(source):
            payload = {
                "brand": "noetfield", "audience": "founder", "intent": "automation",
                "name": "Actual Test Operator", "email": "real-person@example.test",
                "company": "Test", "role": "Owner",
                "problem": "We need real workflow changes with measurable result.",
                "urgency": "now", "estimated_value": 0, "ai_consent": False,
            }
            eid = core.add_event("intake.received", source, "noetfield", payload)
            if source == "public_web":
                # Claim and process using the original production queue.
                self.assertEqual(core.claim("events")["id"], eid)
                core.process_intake({"id": eid, "payload": json.dumps(payload), "source": source})
            return eid
        eid = add("public_web")
        sent = []
        def ingest(method, route, payload=None):
            sent.append(payload)
            return {"created": True, "signal_id": "sig_live_123"}
        with patch.object(founder_bridge, "_request", side_effect=ingest):
            self.assertEqual(founder_bridge.publish_commercial_signals(), 1)
            self.assertEqual(founder_bridge.publish_commercial_signals(), 0)
        self.assertEqual(sent[0]["source_event_id"], "intake:" + eid)
        self.assertNotIn("example.test", json.dumps(sent))
        self.assertEqual(sent[0]["event_type"], "commercial_intake")
        self.assertNotIn("email", sent[0])
        self.assertNotIn("revenue", json.dumps(sent).lower())

    def test_existing_worker_tick_pulls_and_reports_without_second_scheduler(self):
        issued = request()
        calls = []
        def wire(method, path, payload=None):
            calls.append((method, path))
            if method == "GET":
                return {"schema": "sina.company-os.work-intake.v1", "items": [issued]}
            return {"workstream_id": payload["workstream_id"]}
        with patch.object(founder_bridge, "_request", side_effect=wire):
            first = founder_bridge.tick()
            self.assertEqual(first["state"], "LIVE")
            self.assertEqual(first["accepted"], 1)
            self.assertEqual(first["acknowledged"], 1)
            self.assertEqual(first["external_effects"], 0)
            self.assertEqual(first["independent_receipts"], 0)
            self.assertEqual(founder_bridge.tick()["state"], "NEXT_POLL_NOT_DUE")
            with core.connect() as db:
                db.execute("UPDATE state SET value='0' WHERE key='founder_bridge_last_attempt'")
            self.assertEqual(founder_bridge.tick()["accepted"], 0)
        with core.connect() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main()
