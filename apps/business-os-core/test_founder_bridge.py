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

    def test_real_persisted_contributor_flows_into_existing_founder_signal_outbox_once(self):
        from datetime import datetime, timezone
        source={
            "intake_id":"INT-ABCDEF123456",
            "request_id":"RID-CONTRIBUTOR-ABC123",
            "created_at":datetime.now(timezone.utc).isoformat(),
            "sku":"general",
            "vector":"work-with-us-contributor",
            "qualification":None,
            "contributor":{
                "application_kind":"agent","project_id":"buildrelay","role":"qa",
            },
        }
        receipt=core.queue_platform_intake_projection(source)
        with core.connect() as db:
            event=dict(db.execute(
                "SELECT * FROM events WHERE id=?",(receipt["event_id"],)
            ).fetchone())
        seen=[]
        def deliver(method,path,payload=None):
            self.assertEqual(method,"POST")
            self.assertEqual(path,"/api/v2/organization/company/signal")
            seen.append(payload)
            return {"signal_id":"f"*32}
        with patch.object(founder_bridge,"_request",side_effect=deliver):
            # Queued Platform records alone are NOT evidence of a handled application.
            self.assertEqual(founder_bridge.publish_contributor_signals(),0)
            core.process_platform_intake_signal(event)
            self.assertEqual(founder_bridge.publish_contributor_signals(),1)
            self.assertEqual(founder_bridge.publish_contributor_signals(),0)
        self.assertEqual(len(seen),1)
        data=seen[0]
        self.assertEqual(data["source_event_id"],"contributor:INT-ABCDEF123456")
        self.assertEqual(data["event_type"],"contributor_application")
        self.assertEqual(data["evidence_ref"],"receipt:noetfield/intake/INT-ABCDEF123456")
        self.assertNotIn("buildrelay",json.dumps(data))
        self.assertNotIn("@",json.dumps(data))
        with core.connect() as db:
            row=db.execute(
                "SELECT source_event_id FROM founder_org_signals"
            ).fetchone()
            self.assertEqual(row["source_event_id"],"contributor:INT-ABCDEF123456")

    def test_contributor_publishing_failure_retries_without_phantom_delivery(self):
        from datetime import datetime, timezone
        source={
            "intake_id":"INT-ABCDEF123457","request_id":None,
            "created_at":datetime.now(timezone.utc).isoformat(),
            "sku":"general","vector":"work-with-us-contributor",
            "qualification":None,
            "contributor":{"application_kind":"human","project_id":"noetfield","role":"design"},
        }
        receipt=core.queue_platform_intake_projection(source)
        with core.connect() as db:
            event=dict(db.execute("SELECT * FROM events WHERE id=?",
                                  (receipt["event_id"],)).fetchone())
        core.process_platform_intake_signal(event)
        with patch.object(founder_bridge,"_request",side_effect=OSError("transport down")):
            with self.assertRaises(OSError):
                founder_bridge.publish_contributor_signals()
        with core.connect() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM founder_org_signals").fetchone()[0],0)
        with patch.object(founder_bridge,"_request",return_value={"signal_id":"e"*32}):
            self.assertEqual(founder_bridge.publish_contributor_signals(),1)
            self.assertEqual(founder_bridge.publish_contributor_signals(),0)

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

    def test_duplicate_workstream_ack_conflict_is_quarantined_not_retried(self):
        import io
        from urllib.error import HTTPError
        item=request()
        task_id,_=founder_bridge.admit(item, founder_bridge._allowed_projects())
        payload={"error":"invalid_company_ack",
                 "message":"workstream_already_bound_to_different_task"}
        def conflict(*args,**kwargs):
            raise HTTPError("https://sina-founder-os-staging-staging.up.railway.app/api/v2/organization/company/ack",
                             400,"Conflict",{},io.BytesIO(json.dumps(payload).encode()))
        with patch.object(founder_bridge,"_request",side_effect=conflict):
            self.assertEqual(founder_bridge.reconcile(),0)
        with core.connect() as db:
            row=db.execute("SELECT last_acked FROM founder_org_bindings").fetchone()
            self.assertEqual(row["last_acked"],"ACK_CONFLICT")
            task=db.execute("SELECT status FROM tasks WHERE id=?",(task_id,)).fetchone()
            self.assertEqual(task["status"],"blocked")
            self.assertEqual(db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0],1)
        self.assertEqual(founder_bridge.health()["ack_conflicts_quarantined"],1)
        # Even when status changes, stale duplicate ACK cannot re-enter retries.
        with patch.object(founder_bridge,"_request",side_effect=AssertionError("should not retry")):
            self.assertEqual(founder_bridge.reconcile(),0)

    def test_unrelated_ack_http_error_does_not_get_misclassified(self):
        import io
        from urllib.error import HTTPError
        founder_bridge.admit(request(),founder_bridge._allowed_projects())
        def other(*args,**kwargs):
            raise HTTPError("https://sina-founder-os-staging-staging.up.railway.app/api/v2/organization/company/ack",
                              400,"Bad Request",{},io.BytesIO(
                                  b'{"error":"invalid_company_ack","message":"unknown_workstream"}'))
        with patch.object(founder_bridge,"_request",side_effect=other):
            with self.assertRaises(HTTPError):
                founder_bridge.reconcile()
        with core.connect() as db:
            self.assertEqual(db.execute(
                "SELECT last_acked FROM founder_org_bindings").fetchone()[0],"")

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


    def test_rejected_workpacket_records_typed_reason_without_leaking_request(self):
        item=request(request_id="d"*32,project_id="unapproved-private-tenant")
        item["task"]="CONTACT secret.customer@example.invalid should stay private"
        def wire(method,path,payload=None):
            self.assertEqual(method,"GET")
            return {"schema":"sina.company-os.work-intake.v1","items":[item]}
        with patch.object(founder_bridge,"_request",side_effect=wire), \
             patch.object(founder_bridge,"reconcile",return_value=0), \
             patch.object(founder_bridge,"publish_commercial_signals",return_value=0), \
             patch.object(founder_bridge,"publish_contributor_signals",return_value=0):
            result=founder_bridge.tick()
        self.assertEqual(result["state"],"LIVE")
        self.assertEqual(result["rejected"],1)
        self.assertEqual(result["rejection_reasons"],{"project_not_allowed":1})
        reported=founder_bridge.health()
        self.assertEqual(reported["last_cycle_rejection_reasons"],{"project_not_allowed":1})
        self.assertEqual(reported["last_cycle_rejected_projects"],[{
            "reason_code":"project_not_allowed",
            "project_id":"unapproved-private-tenant","company_id":"noetfield-systems-inc"}])
        self.assertNotIn("secret.customer",str(result)+str(reported))
        self.assertNotIn(item["request_id"],str(result)+str(reported))
        with core.connect() as db:
            saved=db.execute("SELECT value FROM state WHERE key='founder_bridge_last_rejections'").fetchone()[0]
        self.assertEqual(json.loads(saved),{"project_not_allowed":1})
        self.assertNotIn("secret.customer",saved)
        with core.connect() as db:
            scoped=db.execute("SELECT value FROM state WHERE key='founder_bridge_last_rejected_projects'").fetchone()[0]
        self.assertEqual(len(json.loads(scoped)),1)
        self.assertNotIn("secret.customer",scoped)

    def test_live_observability_uses_stored_success_and_never_exposes_credentials(self):
        before=founder_bridge.health()
        self.assertTrue(before["configured"])
        self.assertEqual(before["connection"], "AWAITING_FIRST_CYCLE")
        def wire(method,path,payload=None):
            if method=="GET":
                return {"schema":"sina.company-os.work-intake.v1","items":[request()]}
            return {"workstream_id":payload["workstream_id"]}
        with patch.object(founder_bridge,"_request",side_effect=wire):
            self.assertEqual(founder_bridge.tick()["state"],"LIVE")
        live=founder_bridge.health()
        self.assertEqual(live["connection"],"LIVE")
        self.assertEqual(live["work_packets_claimed"],1)
        self.assertEqual(live["pending_ack"],0)
        self.assertEqual(live["verified_outcomes"],0)
        self.assertEqual(live["external_effects"],0)
        self.assertNotIn(os.environ["SINA_ORG_CONTINUOUS_TOKEN"],str(live))
        founder_bridge.record_failure(ConnectionError("Bearer secret ignored"))
        degraded=founder_bridge.health()
        self.assertEqual(degraded["connection"],"DEGRADED")
        self.assertEqual(degraded["last_error_type"],"ConnectionError")
        self.assertNotIn("Bearer",str(degraded))
        with core.connect() as db:
            db.execute("UPDATE state SET value='2000-01-01T00:00:00+00:00' WHERE key='founder_bridge_last_success'")
        self.assertEqual(founder_bridge.health()["connection"],"STALE")



if __name__ == "__main__":
    unittest.main()
