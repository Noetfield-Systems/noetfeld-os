"""End-to-end contract tests: authenticated Sina answer -> local Company OS event
-> existing worker tasks, without task clones or unauthorized effects.
"""
from __future__ import annotations
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import core
import product_loops
import venture_company_os
import venture_decision_bridge as bridge
import sina_work_bridge

class FakeResponse:
    status=200
    def __init__(self,data):self.data=data
    def __enter__(self):return self
    def __exit__(self,*unused):return False
    def read(self,n):return json.dumps(self.data).encode()

class FakeFetcher:
    def __init__(self,answer):self.answer=answer;self.calls=[]
    def open(self,request,timeout=0):
        body=json.loads(request.data.decode())
        self.calls.append((request.full_url,request.headers.get("Authorization"),body))
        return FakeResponse(self.answer)

class LocalDecisionContinuationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.old_db=core.DB
        self.old_auto=os.environ.pop("COMPANY_OS_PORTFOLIO_AUTOSTART",None)
        core.DB=Path(self.tmp.name)/"company.sqlite3"
        core.init()
        for project,scope,name in (
            ("noetfield-web3-launchpad","noetfield-systems-inc","RHEVO"),
            ("cairn-season-0","founder-portfolio","Cairn")):
            product_loops.register({
                "company_id":scope,"project_id":project,"name":name,
                "vertical":"creator-web3","objective":"Genuine free user activation and utility",
                "priority":3,"max_tasks_per_cycle":5})
        with core.connect() as db:
            venture_company_os.reconcile(db)
            db.commit()
        self.old_bridge=os.environ.get(sina_work_bridge.TOKEN_ENV)
        os.environ[sina_work_bridge.TOKEN_ENV]="p"*48
    def tearDown(self):
        core.DB=self.old_db
        self.tmp.cleanup()
        if self.old_auto is not None:os.environ["COMPANY_OS_PORTFOLIO_AUTOSTART"]=self.old_auto
        if self.old_bridge is None:os.environ.pop(sina_work_bridge.TOKEN_ENV,None)
        else:os.environ[sina_work_bridge.TOKEN_ENV]=self.old_bridge
    def answer(self,*,project="noetfield-web3-launchpad",scope="noetfield-systems-inc",
               decision="PROCEED_IN_LOCAL_COMPANY_OS"):
        return {
            "schema":bridge.DECISION_SCHEMA,
            "decision":decision,"decision_ref":"a"*32,
            "execution_owner":"PROJECT_LOCAL_COMPANY_OS",
            "portfolio_owner":"SINA_FOUNDER_OS",
            "project_id":project,"company_scope":scope,
            "next_action":"Implement the next real creator onboarding improvement and test it",
            "founder_question_required":False,
            "founder_question":None,"policy_version":"founder-goalkeeper-agent-gateway-v1.1",
            "authority":"ADVISORY_DECISION_NO_PERMIT",
            "governor_permit_issued":False,"external_effect_authorized":False,
            "agent_execution_permit":False,
            "founder_intent_memory":{"digest":"b"*64},
            "audit_record_updated":True
        }
    def ask(self,project="noetfield-web3-launchpad",scope="noetfield-systems-inc"):
        return {"project_id":project,"company_id":scope,"agent_role":"CODING_AGENT",
                "intent":"NEXT_STEP","proposed_action":"IMPLEMENT_CODE",
                "question":"Continue the useful project improvement",
                "options":[],"evidence_refs":[],"request_id":"rhevo-next-feature-0001"}
    def test_real_local_company_event_and_task_fanout_deduped(self):
        client=FakeFetcher(self.answer())
        first=bridge.submit_question(self.ask(),fetch=client)
        self.assertEqual(first["decision"],"PROCEED_IN_LOCAL_COMPANY_OS")
        self.assertTrue(first["queued_for_company_os"])
        self.assertFalse(first["governor_permit_issued"])
        self.assertEqual(first["execution_owner"],"PROJECT_LOCAL_COMPANY_OS")
        self.assertEqual(len(client.calls),1)
        url,token,body=client.calls[0]
        self.assertEqual(url,sina_work_bridge.SOURCE_URL+bridge.DECISION_PATH)
        self.assertEqual(token,"Bearer "+"p"*48)
        self.assertEqual(body["schema"],bridge.QUESTION_SCHEMA)
        self.assertEqual(body["project_id"],"noetfield-web3-launchpad")
        repeat=bridge.submit_question(self.ask(),fetch=client)
        self.assertTrue(repeat["replay"])
        with core.connect() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM venture_company_os_decisions").fetchone()[0],1)
            events=db.execute("SELECT * FROM events WHERE id=?",(first["event_id"],)).fetchall()
            self.assertEqual(len(events),1)
        result=product_loops.process_signal(dict(events[0]))
        self.assertIn("engineering_operator",result["specialists"])
        with core.connect() as db:
            tasks=db.execute("SELECT company_id,project_id FROM tasks WHERE event_id=?",
                             (events[0]["id"],)).fetchall()
            self.assertTrue(tasks)
            self.assertTrue(all(t["company_id"]=="noetfield-systems-inc" and
                                t["project_id"]=="noetfield-web3-launchpad" for t in tasks))
        self.assertEqual(bridge.history("noetfield-systems-inc","noetfield-web3-launchpad")["items"][0]["decision_ref"],"a"*32)
    def test_outcome_feedback_is_durable_idempotent_and_never_verified_by_model(self):
        source=FakeFetcher(self.answer())
        first=bridge.submit_question(self.ask(),fetch=source)
        with core.connect() as db:
            items=db.execute("""SELECT * FROM venture_company_os_decision_feedback
                WHERE decision_ref=?""",(first["decision_ref"],)).fetchall()
            self.assertEqual(len(items),1)
            self.assertEqual(items[0]["status"],"STARTED")
            self.assertEqual(items[0]["delivery_state"],"PENDING")
        class FeedbackFetcher:
            def __init__(self):self.calls=0
            def open(self,req,timeout=0):
                self.calls+=1
                self.url=req.full_url
                self.body=json.loads(req.data.decode())
                return FakeResponse({"recorded":True,
                                     "evidence_status":"SOURCE_REPORTED_UNVERIFIED",
                                     "policy_auto_modified":False})
        transport=FeedbackFetcher()
        delivered=bridge.flush_feedback(fetch=transport)
        self.assertEqual(delivered["delivered"],1)
        self.assertFalse(delivered["independent_verification"])
        self.assertEqual(transport.url,sina_work_bridge.SOURCE_URL+
                          sina_work_bridge.AGENT_FEEDBACK_PATH)
        self.assertEqual(transport.body["decision_ref"],first["decision_ref"])
        self.assertEqual(bridge.flush_feedback(fetch=transport)["delivered"],0)
        self.assertEqual(transport.calls,1)
        with core.connect() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM venture_company_os_decision_feedback "
                "WHERE delivery_state='DELIVERED'").fetchone()[0],1)

    def test_degraded_sina_feedback_retries_original_source_report(self):
        first=bridge.submit_question(self.ask(),fetch=FakeFetcher(self.answer()))
        class FailTransport:
            def open(self,*args,**kwargs):
                raise TimeoutError("upstream unavailable")
        pending=bridge.flush_feedback(fetch=FailTransport())
        self.assertEqual(pending["pending_retry"],1)
        with core.connect() as db:
            row=db.execute("SELECT delivery_state,attempts FROM venture_company_os_decision_feedback "
                "WHERE decision_ref=?",(first["decision_ref"],)).fetchone()
            self.assertEqual(row["delivery_state"],"PENDING")
            self.assertEqual(row["attempts"],1)

    def test_founder_reserved_response_does_not_create_tasks(self):
        response=self.answer(decision="GOVERNOR_AND_OWNER_AUTHORIZATION_REQUIRED")
        response["founder_question_required"]=True
        response["founder_question"]="Approve the exact reserved action?"
        client=FakeFetcher(response)
        result=bridge.submit_question(self.ask(),fetch=client)
        self.assertFalse(result["queued_for_company_os"])
        self.assertTrue(result["founder_question_required"])
        with core.connect() as db:
            self.assertEqual(db.execute(
                "SELECT COUNT(*) FROM product_observations WHERE source_event_id LIKE 'venture_agent_decision:%'"
                ).fetchone()[0],0)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM venture_company_os_decisions").fetchone()[0],1)
    def test_cross_tenant_spoofed_goalkeeper_response_is_refused(self):
        bad=self.answer(scope="founder-portfolio")
        with self.assertRaises(ValueError):
            bridge.submit_question(self.ask(),fetch=FakeFetcher(bad))
        with core.connect() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM venture_company_os_decisions").fetchone()[0],0)
    def test_permit_escalation_from_remote_response_refused(self):
        response=self.answer()
        response["governor_permit_issued"]=True
        with self.assertRaises(ValueError):
            bridge.submit_question(self.ask(),fetch=FakeFetcher(response))
    def test_task_consults_goalkeeper_without_new_task_or_cross_scope(self):
        with core.connect() as db:
            task_id=core.add_task(db,None,None,"portfolio","engineering_operator",
                "Implement RHEVO activation","Improve creator onboarding with real evidence",
                "Prepare bounded internal code scope")
            db.execute("UPDATE tasks SET company_id=?,project_id=?,status='running' WHERE id=?",
                       ("noetfield-systems-inc","noetfield-web3-launchpad",task_id))
            db.commit()
            task=dict(db.execute("SELECT * FROM tasks WHERE id=?",(task_id,)).fetchone())
        client=FakeFetcher(self.answer())
        result=bridge.consult_existing_task(task,fetch=client)
        self.assertEqual(result["state"],"CONSULTED")
        self.assertFalse(result["external_permit"])
        self.assertEqual(client.calls[0][2]["request_id"],"company-task:"+task_id)
        with core.connect() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0],1)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM venture_company_os_decisions").fetchone()[0],1)
        with self.assertRaises(ValueError):
            bridge.consult_existing_task(dict(task,company_id="founder-portfolio"),
                                         fetch=client)

if __name__=="__main__":
    unittest.main()
