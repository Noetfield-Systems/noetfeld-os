"""Real SQLite supervisor acceptance. No mock job queue or invented coding outcomes."""
import json
import os
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import core
import founder_bridge
import operations_relay


class OperationsRelayTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.saved=core.DB
        self.env=dict(os.environ)
        core.DB=Path(self.tmp.name)/"core.sqlite"
        core.init()
        founder_bridge.init()

    def tearDown(self):
        core.DB=self.saved
        os.environ.clear()
        os.environ.update(self.env)
        self.tmp.cleanup()

    def test_terminal_event_assigns_real_engineering_diagnosis_once(self):
        stamp=core.now()
        with core.connect() as db:
            db.execute("INSERT INTO events(id,event_type,source,brand,payload,status,attempts,created_at,processed_at,error) "
                       "VALUES(?,?,?,?,?,'failed',1,?,?,?)",
                       ("evt_failed_case_1","platform.intake.signal.received","unit","noetfield",
                        '{"private":"sensitive.user@example.test"}',stamp,stamp,"RuntimeError"))
        a=operations_relay.tick()
        self.assertEqual(a["state"],"EXECUTED")
        self.assertEqual(a["actions"],1)
        with core.connect() as db:
            rows=db.execute("SELECT id,role,objective,status FROM tasks").fetchall()
            self.assertEqual(len(rows),1)
            self.assertEqual(rows[0]["role"],"engineering_operator")
            self.assertEqual(rows[0]["status"],"queued")
            self.assertNotIn("sensitive.user",rows[0]["objective"])
            marker=db.execute("SELECT value FROM state WHERE key=?",
                              ("operations_relay_event:evt_failed_case_1",)).fetchone()
            self.assertEqual(marker["value"],rows[0]["id"])
        self.assertEqual(operations_relay.tick()["state"],"NOT_DUE")
        self.assertEqual(operations_relay.tick(timestamp=time.time()+120)["actions"],0)
        with core.connect() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0],1)
        # Existing specialist worker actually claims, processes and records a run.
        task=core.claim("tasks")
        self.assertEqual(task["id"],rows[0]["id"])
        core.process_task(task)
        view=operations_relay.snapshot()
        self.assertTrue(view["last_supervisor_tick"])
        self.assertTrue(any(x["action"]=="BLOCKER_OWNER_ASSIGNED" for x in view["actions"]))
        self.assertEqual(view["handoffs"][0]["provider"],"deterministic")
        self.assertFalse(view["handoffs"][0]["actual_model_call_observed"])
        self.assertFalse(view["end_to_end_motor_execution_proven"])

    def test_dependency_recovery_requeues_real_blocked_task(self):
        with core.connect() as db:
            dep=core.add_task(db,None,None,"noetfield","market_intelligence",
                              "Research","Gather known evidence","Return evidence")
            nxt=core.add_task(db,None,None,"noetfield","chief_of_staff",
                              "Manager","Synthesize researcher result","Choose next")
            core.add_task_dependency(db,nxt,dep)
            db.execute("UPDATE tasks SET status='blocked' WHERE id=?",(nxt,))
            db.execute("UPDATE tasks SET status='drafted' WHERE id=?",(dep,))
        output=operations_relay.tick()
        self.assertIn("DEPENDENCY_RECOVERED",output["action_types"])
        with core.connect() as db:
            self.assertEqual(db.execute("SELECT status FROM tasks WHERE id=?",(nxt,)).fetchone()[0],"queued")
        self.assertFalse(operations_relay.snapshot()["independent_verification_inferred"])

    def test_consent_and_attempt_ceiling_control_model_retries(self):
        old=(datetime.now(timezone.utc)-timedelta(minutes=8)).isoformat(timespec="seconds")
        with core.connect() as db:
            for key,consent,attempts in [("yes",1,1),("no",0,1),("limit",1,3)]:
                oid="opp_"+key
                db.execute("""INSERT INTO opportunities
                    (id,contact_id,brand,title,intent,problem,estimated_value,urgency,
                    ai_consent,route,score,stage,source,created_at,updated_at)
                    VALUES(?,NULL,'noetfield','Test','testing','No real customer',0,'now',?,
                           'internal',1,'new','unit',?,?)""",(oid,consent,old,old))
                tid=core.add_task(db,None,oid,"noetfield","product_strategy",
                                  "Model retry "+key,"Assess retained evidence","Return next action")
                db.execute("UPDATE tasks SET status='drafted',result=?,updated_at=? WHERE id=?",
                           ('{"provider":"provider_error"}',old,tid))
                for i in range(attempts):
                    db.execute("INSERT INTO runs VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                               ("run_"+key+str(i),tid,"product_strategy","provider_error","model",
                                "degraded",0,0,old,old,"{}"))
        os.environ.update({"LLM_BASE_URL":"https://example.invalid","LLM_API_KEY":"fixture-not-real",
                           "LLM_MODEL":"test-model"})
        result=operations_relay.tick()
        self.assertIn("CONSENTED_MODEL_RETRY",result["action_types"])
        with core.connect() as db:
            states={r["title"].split()[-1]:r["status"] for r in db.execute(
                "SELECT title,status FROM tasks WHERE title LIKE 'Model retry %'")}
        self.assertEqual(states,{"yes":"queued","no":"drafted","limit":"drafted"})

    def test_readonly_projection_never_confuses_drafts_with_execution(self):
        with core.connect() as db:
            tid=core.add_task(db,None,None,"noetfield","engineering_operator",
                              "Architect feature","Propose code edits","Submit bounded change")
            db.execute("UPDATE tasks SET status='drafted' WHERE id=?",(tid,))
            db.execute("INSERT INTO runs VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                ("run_fixture",tid,"engineering_operator","deterministic-evidence","none",
                 "completed",0,0,core.now(),core.now(),'{}'))
        view=operations_relay.snapshot()
        self.assertEqual(view["counts"]["drafted"],1)
        self.assertEqual(view["counts"]["tasks_needing_execution"],0)
        self.assertFalse(view["handoffs"][0]["actual_model_call_observed"])
        self.assertEqual(view["handoffs"][0]["result_kind"],"INTERNAL_DRAFT")
        self.assertFalse(view["end_to_end_motor_execution_proven"])


if __name__=="__main__":
    unittest.main()
