"""Real commercial WorkPacket contract regression, no external sends or payments."""
import hashlib
import json
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

import core
import commercial_workpackets as commercial


class CommercialRuntimeAcceptance(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.old_db=core.DB
        core.DB=Path(self.tmp.name)/"workpackets.sqlite"
        core.init()
        commercial.init()
        self.payload={
          "idempotency_key":str(uuid.uuid4()),
          "source_intake_id":"INT-ABCDEF123456",
          "engine":"COMPANY_OS",
          "scope_ref":"SOW-AISOS-2026-01",
          "payment_event_id":"evt_live987654321",
          "requested_work":"Perform accepted, paid, narrowly scoped commercial deliverable"
        }

    def tearDown(self):
        core.DB=self.old_db
        self.tmp.cleanup()

    def test_receiver_uses_persisted_company_task_queue_and_idempotent_replay(self):
        first=commercial.admit(self.payload)
        self.assertEqual("ACCEPTED",first["status"])
        self.assertFalse(first["idempotent"])
        self.assertFalse(first["work_completed"])
        replay=commercial.admit(self.payload)
        self.assertTrue(replay["idempotent"])
        self.assertEqual(first["workpacket_id"],replay["workpacket_id"])
        with core.connect() as db:
            self.assertEqual(1,db.execute("SELECT count(*) FROM commercial_workpackets").fetchone()[0])
            rows=db.execute("SELECT * FROM tasks").fetchall()
            self.assertEqual(2,len(rows))
            self.assertEqual({"engineering_operator","risk_governance"},{x["role"] for x in rows})
            self.assertTrue(all(x["brand"]=="noetfield" for x in rows))
            self.assertTrue(all(x["status"]=="queued" for x in rows))
            self.assertTrue(all("buyer@" not in (x["objective"] or "") for x in rows))
        self.assertFalse(commercial.public_receipt(first["workpacket_id"])["artifact_ready"])

    def test_idempotency_key_cannot_be_reused_for_other_payment_or_scope(self):
        commercial.admit(self.payload)
        modified={**self.payload,"payment_event_id":"evt_other987654321"}
        with self.assertRaisesRegex(commercial.CommercialWorkPacketError,"IDEMPOTENCY_PAYLOAD_CONFLICT"):
            commercial.admit(modified)
        with core.connect() as db:
            self.assertEqual(1,db.execute("SELECT count(*) FROM commercial_workpackets").fetchone()[0])

    def test_invalid_source_mock_or_cross_engine_never_creates_task(self):
        changes=[
          {"source_intake_id":"DEMO-INT-001"},
          {"scope_ref":"DEMO-SOW-001"},
          {"engine":"RWA_CLINIC"},
          {"payment_event_id":"evt_test"},
          {"requested_work":"DEMO- pretend to deliver an actual product"},
          {"idempotency_key":"invalid"},
        ]
        for item in changes:
            with self.subTest(item=item):
                with self.assertRaises(commercial.CommercialWorkPacketError):
                    commercial.admit({**self.payload,**item})
        with core.connect() as db:
            self.assertEqual(0,db.execute("SELECT count(*) FROM tasks").fetchone()[0])

    def test_real_provider_run_required_before_artifact(self):
        data=commercial.admit(self.payload)
        wid=data["workpacket_id"]
        progress=commercial.reconcile()
        self.assertEqual(0,progress["artifact_ready"])
        with core.connect() as db:
            tids=db.execute("SELECT id,role FROM tasks ORDER BY role").fetchall()
            for row in tids:
                db.execute("UPDATE tasks SET status='drafted',result=? WHERE id=?",(
                    json.dumps({"provider":"deterministic","recommendation":{
                    "assessment":"A very long synthetic provider assessment with no actual inference run.",
                    "next_best_action":"Validate test and owner assignment."}}),row["id"]))
        progress=commercial.reconcile()
        self.assertEqual(0,progress["artifact_ready"])
        self.assertEqual("BLOCKED_MODEL",commercial.public_receipt(wid)["status"])

    def test_two_completed_provider_runs_create_hashed_real_work_product_not_fake_delivery(self):
        receipt=commercial.admit(self.payload)
        with core.connect() as db:
            for row in db.execute("SELECT id,role FROM tasks").fetchall():
                actual={
                 "provider":"openai-compatible",
                 "recommendation":{
                   "assessment":"Detailed source-derived implementation assessment identifying lead input, deduplication and assigned owner evidence.",
                   "next_best_action":"Implement authorized intake assignment and test duplicate-source handling before deployment.",
                   "success_metric":"Exactly one owner per verified source lead."
                 }
                }
                db.execute("UPDATE tasks SET status='drafted',result=? WHERE id=?",
                           (json.dumps(actual),row["id"]))
        res=commercial.reconcile()
        self.assertEqual(1,res["artifact_ready"])
        a=commercial.artifact_for_verifier(receipt["workpacket_id"])
        self.assertEqual(a["artifact_sha256"],hashlib.sha256(
            commercial.canonical(a["artifact"]).encode()).hexdigest())
        self.assertEqual(2,len(a["artifact"]["agent_results"]))
        self.assertFalse(a["artifact"]["product_delivered"])
        self.assertFalse(a["artifact"]["customer_accepted"])
        self.assertFalse(a["artifact"]["independent_verification"])
        self.assertEqual("INTERNAL_REVIEW_READY_NOT_DEPLOYED",
                         a["artifact"]["work_product_stage"])
        self.assertTrue(all(t["verified"] is False for t in a["artifact"]["acceptance_tests"]))
        p=commercial.public_receipt(receipt["workpacket_id"])
        self.assertTrue(p["artifact_ready"])
        self.assertFalse(p["work_completed_and_independently_verified"])
        self.assertEqual(0,commercial.reconcile()["artifact_ready"])

    def test_private_receiver_token_is_not_founder_bearer_and_unauthorized_is_401(self):
        import app
        with patch.dict("os.environ",{"COMPANY_OS_COMMERCIAL_DISPATCH_TOKEN":"a"*40},clear=False):
            with self.assertRaises(Exception) as bad:
                app.commercial_workpacket_authorize("Bearer wrong")
            self.assertEqual(401,bad.exception.status_code)
            app.commercial_workpacket_authorize("Bearer "+"a"*40)

if __name__=="__main__":
    unittest.main()
