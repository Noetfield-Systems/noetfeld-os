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
        for key in ("LLM_BASE_URL","LLM_API_KEY","LLM_MODEL"):
            os.environ.pop(key,None)

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
        self.assertEqual(a["actions"],2)
        with core.connect() as db:
            rows=db.execute("SELECT id,role,objective,status,autonomy FROM tasks ORDER BY priority_rank").fetchall()
            self.assertEqual(len(rows),2)
            self.assertEqual([r["role"] for r in rows],["engineering_operator","chief_of_staff"])
            self.assertEqual([r["status"] for r in rows],["queued","queued"])
            self.assertTrue(all(r["autonomy"]=="internal_diagnostic_model" for r in rows))
            self.assertTrue(all("sensitive.user" not in r["objective"] for r in rows))
            self.assertEqual(db.execute("SELECT COUNT(*) FROM task_dependencies").fetchone()[0],1)
            marker=db.execute("SELECT value FROM state WHERE key=?",
                              ("operations_relay_event:evt_failed_case_1",)).fetchone()
            self.assertEqual(marker["value"],rows[0]["id"])
        self.assertEqual(operations_relay.tick()["state"],"NOT_DUE")
        self.assertEqual(operations_relay.tick(timestamp=time.time()+120)["actions"],0)
        with core.connect() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0],2)
        # Existing specialist worker actually claims, processes and records a run.
        task=core.claim("tasks")
        self.assertEqual(task["id"],rows[0]["id"])
        core.process_task(task)
        view=operations_relay.snapshot()
        self.assertTrue(view["last_supervisor_tick"])
        self.assertTrue(any(x["action"]=="BLOCKER_OWNER_ASSIGNED" for x in view["actions"]))
        engineer=next(x for x in view["handoffs"] if x["owner_role"]=="engineering_operator")
        self.assertEqual(engineer["provider"],"deterministic")
        self.assertFalse(engineer["actual_model_call_observed"])
        self.assertFalse(view["end_to_end_motor_execution_proven"])
        manager=core.claim("tasks")
        self.assertEqual(manager["role"],"chief_of_staff")
        self.assertTrue(operations_relay.supervised_model_authorized(manager))
        self.assertEqual(operations_relay.upstream_evidence(manager)[0]["role"],"engineering_operator")
        core.process_task(manager)
        self.assertEqual(len(operations_relay.snapshot()["handoffs"]),2)

    def test_existing_platform_openrouter_fallback_is_internal_only(self):
        from unittest.mock import patch
        from urllib.error import HTTPError
        with core.connect() as db:
            db.execute("INSERT INTO state(key,value) VALUES(?,?)",
                ("founder_bridge_last_rejected_projects",json.dumps([{
                    "reason_code":"project_not_allowed","project_id":"noetfield-earnloop",
                    "company_id":"noetfield-systems-inc"}])))
        operations_relay.tick()
        os.environ.update({"LLM_BASE_URL":"https://primary.invalid/v1",
                           "LLM_API_KEY":"primary-invalid-fixture",
                           "LLM_MODEL":"original-model-fixture",
                           "LLM_FALLBACK_API_KEY":"existing-platform-reference-fixture",
                           "LLM_FALLBACK_MODEL":"platform-pinned-model-fixture"})
        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self,*_): return False
            def read(self):
                return json.dumps({
                    "choices":[{"message":{"content":json.dumps({
                        "assessment":"Scoped engineering diagnosis completed using existing model provider",
                        "next_best_action":"Check canonical project allowlist against registry",
                        "risk_flags":[],"evidence":[]})}}],
                    "usage":{"prompt_tokens":31,"completion_tokens":19}
                }).encode()
        calls=[]
        def responder(request,timeout=None):
            self.assertEqual(timeout,20)
            calls.append(request)
            if len(calls)%2==1:
                self.assertEqual(request.full_url,"https://primary.invalid/v1/chat/completions")
                raise HTTPError(request.full_url,401,"auth failed",{},None)
            self.assertEqual(request.full_url,"https://openrouter.ai/api/v1/chat/completions")
            self.assertEqual(json.loads(request.data)["model"],"platform-pinned-model-fixture")
            self.assertTrue(request.headers["Authorization"].endswith("existing-platform-reference-fixture"))
            return FakeResponse()
        with patch("urllib.request.urlopen",side_effect=responder):
            first=core.claim("tasks")
            self.assertEqual(first["role"],"engineering_operator")
            core.process_task(first)
            second=core.claim("tasks")
            self.assertEqual(second["role"],"chief_of_staff")
            core.process_task(second)
        self.assertEqual(len(calls),4)
        with core.connect() as db:
            rows=db.execute("SELECT result,status FROM tasks ORDER BY priority_rank").fetchall()
            self.assertEqual(len(rows),2)
            self.assertTrue(all(row["status"]=="drafted" for row in rows))
            self.assertTrue(all(json.loads(row["result"])["recommendation"]["model_route"]==
                                "noetfield_openrouter_fallback" for row in rows))
            self.assertEqual(db.execute("SELECT COUNT(*) FROM runs WHERE provider='openai-compatible'").fetchone()[0],2)
        self.assertFalse(operations_relay.snapshot()["end_to_end_motor_execution_proven"])

    def test_customer_llm_401_never_leaks_to_other_provider(self):
        from unittest.mock import patch
        from urllib.error import HTTPError
        old=core.now()
        with core.connect() as db:
            db.execute("""INSERT INTO opportunities
                (id,contact_id,brand,title,intent,problem,estimated_value,urgency,
                 ai_consent,route,score,stage,source,created_at,updated_at)
                VALUES(?,NULL,'noetfield','Test','testing','Customer provided data',0,'now',1,
                       'internal',1,'new','unit',?,?)""",("opp_consent_fixture",old,old))
            tid=core.add_task(db,None,"opp_consent_fixture","noetfield","product_strategy",
                              "Customer scenario","Inspect provided evidence","Draft next step")
        os.environ.update({"LLM_BASE_URL":"https://primary.invalid/v1",
                           "LLM_API_KEY":"primary-invalid-fixture","LLM_MODEL":"original-model-fixture",
                           "LLM_FALLBACK_API_KEY":"existing-platform-reference-fixture",
                           "LLM_FALLBACK_MODEL":"platform-pinned-model-fixture"})
        seen=[]
        def only_primary(request,timeout=None):
            seen.append(request.full_url)
            raise HTTPError(request.full_url,401,"auth failure",{},None)
        with patch("urllib.request.urlopen",side_effect=only_primary):
            task=core.claim("tasks")
            core.process_task(task)
        self.assertEqual(seen,["https://primary.invalid/v1/chat/completions"])
        with core.connect() as db:
            result=json.loads(db.execute("SELECT result FROM tasks WHERE id=?",(tid,)).fetchone()[0])
        self.assertEqual(result["model_error_code"],"HTTP_401")
        self.assertNotIn("existing-platform-reference-fixture",str(result))

    def test_real_internal_engineer_then_manager_llm_handoff(self):
        from unittest.mock import patch
        stamp=core.now()
        with core.connect() as db:
            db.execute("INSERT INTO events(id,event_type,source,brand,payload,status,attempts,created_at,error) "
                       "VALUES(?,?,?,?,?,'dead_letter',4,?,?)",
                       ("evt_failed_case_2","platform.intake.signal.received","unit","noetfield",
                        '{"redacted":"never_forward"}',stamp,"TimeoutError"))
        operations_relay.tick()
        calls=[]
        class FakeResponse:
            def __enter__(self):
                return self
            def __exit__(self,*_):
                return False
            def read(self):
                return json.dumps({
                    "choices":[{"message":{"content":json.dumps({
                        "assessment":"Investigate timeout and add bounded retry to intake worker",
                        "next_best_action":"Add regression test for failed webhook",
                        "risk_flags":[],"evidence":[]})}}],
                    "usage":{"prompt_tokens":42,"completion_tokens":24}
                }).encode()
        def provider_call(req,timeout=None):
            self.assertEqual(timeout,20)
            payload=json.loads(req.data)
            self.assertEqual(payload["max_tokens"],600)
            user=json.loads(payload["messages"][1]["content"])
            calls.append(user)
            self.assertNotIn("never_forward",json.dumps(user))
            return FakeResponse()
        os.environ.update({"LLM_BASE_URL":"https://example.invalid",
                           "LLM_API_KEY":"fixture-only","LLM_MODEL":"fixture-model"})
        with patch("urllib.request.urlopen",side_effect=provider_call):
            first=core.claim("tasks")
            self.assertEqual(first["role"],"engineering_operator")
            self.assertTrue(operations_relay.supervised_model_authorized(first))
            core.process_task(first)
            second=core.claim("tasks")
            self.assertEqual(second["role"],"chief_of_staff")
            self.assertTrue(operations_relay.supervised_model_authorized(second))
            core.process_task(second)
        self.assertEqual(len(calls),2)
        self.assertEqual(calls[1]["context"]["prior_specialist_result"][0]["role"],"engineering_operator")
        self.assertIn("Investigate timeout",calls[1]["context"]["prior_specialist_result"][0]["assessment"])
        with core.connect() as db:
            providers=[r[0] for r in db.execute("SELECT provider FROM runs ORDER BY started_at")]
            self.assertEqual(providers,["openai-compatible","openai-compatible"])
        view=operations_relay.snapshot()
        self.assertEqual(sum(1 for x in view["handoffs"] if x["actual_model_call_observed"]),2)
        engineer=next(x for x in view["handoffs"] if x["owner_role"]=="engineering_operator")
        self.assertIn("Investigate timeout",engineer["answer_excerpt"])
        self.assertEqual(engineer["response_kind"],"MODEL_RESPONSE")
        self.assertTrue(engineer["prompt_excerpt"].startswith("The") or engineer["prompt_excerpt"].startswith("Investigate"))
        self.assertFalse(view["end_to_end_motor_execution_proven"])

    def test_no_arbitrary_task_can_claim_internal_agent_authority(self):
        with core.connect() as db:
            tid=core.add_task(db,None,None,"noetfield","engineering_operator",
                              "Repair event processing evt_fake1234",
                              "Untrusted browser-controlled text","Do not run")
            db.execute("UPDATE tasks SET autonomy='internal_diagnostic_model' WHERE id=?",(tid,))
            item=dict(db.execute("SELECT * FROM tasks WHERE id=?",(tid,)).fetchone())
        self.assertFalse(operations_relay.supervised_model_authorized(item))

    def test_real_founder_rejection_autoroutes_engineer_to_manager_once(self):
        with core.connect() as db:
            db.execute("INSERT INTO state(key,value) VALUES(?,?)",
                ("founder_bridge_last_rejected_projects",json.dumps([{
                    "reason_code":"project_not_allowed","project_id":"noetfield-earnloop",
                    "company_id":"noetfield-systems-inc",
                    "objective":"never forward this secret@example.test"
                }])))
        result=operations_relay.tick()
        self.assertEqual(result["state"],"EXECUTED")
        self.assertIn("FOUNDER_HANDOFF_OWNER_ASSIGNED",result["action_types"])
        self.assertIn("FOUNDER_HANDOFF_MANAGER_SCHEDULED",result["action_types"])
        with core.connect() as db:
            rows=db.execute("SELECT * FROM tasks ORDER BY priority_rank").fetchall()
            self.assertEqual(len(rows),2)
            self.assertEqual([r["role"] for r in rows],["engineering_operator","chief_of_staff"])
            self.assertTrue(all("secret@example" not in r["objective"] for r in rows))
            self.assertEqual(db.execute("SELECT COUNT(*) FROM task_dependencies").fetchone()[0],1)
            self.assertTrue(all(operations_relay.supervised_model_authorized(dict(r)) for r in rows))
        self.assertEqual(operations_relay.tick(timestamp=time.time()+120)["actions"],0)
        with core.connect() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0],2)
        self.assertTrue(any(x.get("project_id")=="noetfield-earnloop"
                            for x in operations_relay.snapshot()["actions"]))
        self.assertFalse(operations_relay.snapshot()["end_to_end_motor_execution_proven"])

    def test_foreign_company_rejection_does_not_dispatch_noetfield_workers(self):
        with core.connect() as db:
            db.execute("INSERT INTO state(key,value) VALUES(?,?)",
                ("founder_bridge_last_rejected_projects",json.dumps([{
                    "reason_code":"project_not_allowed","project_id":"independent-venture",
                    "company_id":"independent-company"}])))
        self.assertEqual(operations_relay.tick()["actions"],0)
        with core.connect() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0],0)

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

    def test_latest_provider_truth_not_set_configuration_badge(self):
        self.assertEqual(operations_relay.provider_connection_status()["state"],"NOT_CONFIGURED")
        os.environ.update({"LLM_BASE_URL":"https://provider.invalid/v1",
                           "LLM_API_KEY":"fixture-not-live","LLM_MODEL":"fixture"})
        self.assertEqual(operations_relay.provider_connection_status()["state"],"CONFIGURED_UNTESTED")
        with core.connect() as db:
            db.execute("INSERT INTO runs VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                ("run_failed","task-diagnosis","engineering_operator","provider_error","fixture",
                 "degraded",0,0,core.now(),core.now(),
                 '{"model_error_code":"HTTP_401","assessment":"auth failed"}'))
        health=operations_relay.provider_connection_status()
        self.assertEqual(health["state"],"AUTH_REJECTED")
        self.assertEqual(health["last_error_code"],"HTTP_401")
        self.assertFalse(health["provider_authenticated"])
        self.assertNotIn("fixture-not-live",str(health))
        with core.connect() as db:
            db.execute("INSERT INTO runs VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                ("run_success","task-followup","chief_of_staff","openai-compatible","fixture",
                 "completed",14,22,core.now(),core.now(),
                 '{"assessment":"real model response"}'))
        recovered=operations_relay.provider_connection_status()
        self.assertEqual(recovered["state"],"MODEL_RESPONSE_RECORDED")
        self.assertTrue(recovered["provider_authenticated"])
        self.assertIsNone(recovered["last_error_code"])

    def test_provider_errors_classify_without_raw_url_or_secret(self):
        from urllib.error import HTTPError, URLError
        cases=[(HTTPError("https://provider.invalid/?token=SECRET",401,
                          "SECRET unauthorized",{},None),"HTTP_401",False),
               (HTTPError("https://provider.invalid/?token=SECRET",429,
                          "rate-limited",{},None),"HTTP_429",True),
               (TimeoutError("SECRET input timed out"),"NETWORK_TRANSIENT",True),
               (URLError("SECRET getaddrinfo failed"),"NETWORK_TRANSIENT",True),
               (ValueError("SECRET broken reply"),"PROVIDER_RESPONSE_INVALID",False)]
        for error,code,again in cases:
            result=operations_relay.classify_provider_error(error)
            self.assertEqual(result,{"code":code,"retryable":again})
            self.assertNotIn("SECRET",str(result))

    def test_supervised_model_http401_is_a_real_blocker_not_a_retry_storm(self):
        from unittest.mock import patch
        from urllib.error import HTTPError
        stamp=core.now()
        with core.connect() as db:
            db.execute("INSERT INTO state(key,value) VALUES(?,?)",
                ("founder_bridge_last_rejected_projects",json.dumps([{
                    "reason_code":"project_not_allowed","project_id":"noetfield-earnloop",
                    "company_id":"noetfield-systems-inc"}])))
        operations_relay.tick()
        os.environ.update({"LLM_BASE_URL":"https://provider.invalid/v1",
                           "LLM_API_KEY":"DO_NOT_PUBLISH_SECRET","LLM_MODEL":"fixture"})
        with patch("urllib.request.urlopen",side_effect=HTTPError(
                "https://provider.invalid/v1/chat/completions?key=DO_NOT_PUBLISH_SECRET",
                401,"DO_NOT_PUBLISH_SECRET",{},None)):
            first=core.claim("tasks")
            self.assertEqual(first["role"],"engineering_operator")
            core.process_task(first)
        with core.connect() as db:
            t=db.execute("SELECT * FROM tasks WHERE id=?",(first["id"],)).fetchone()
            result=json.loads(t["result"])
            self.assertEqual(result["model_error_code"],"HTTP_401")
            self.assertFalse(result["model_retryable"])
            self.assertNotIn("DO_NOT_PUBLISH_SECRET",t["result"])
            db.execute("UPDATE tasks SET updated_at=? WHERE id=?",(
                (datetime.now(timezone.utc)-timedelta(minutes=8)).isoformat(),first["id"]))
        next_tick=operations_relay.tick(timestamp=time.time()+120)
        self.assertIn("MODEL_PROVIDER_BLOCKER_IDENTIFIED",next_tick["action_types"])
        self.assertNotIn("SUPERVISED_MODEL_RETRY",next_tick["action_types"])
        with core.connect() as db:
            t=db.execute("SELECT * FROM tasks WHERE id=?",(first["id"],)).fetchone()
            self.assertEqual(t["status"],"blocked")
        again=operations_relay.tick(timestamp=time.time()+240)
        self.assertNotIn("MODEL_PROVIDER_BLOCKER_IDENTIFIED",again["action_types"])
        page=operations_relay.snapshot()
        task=next(x for x in page["handoffs"] if x["task_id"]==first["id"])
        self.assertEqual(task["response_kind"],"PROVIDER_FAILED")
        self.assertEqual(task["model_error_code"],"HTTP_401")
        self.assertEqual(task["answer_excerpt"],"Provider failed: HTTP_401")
        self.assertNotIn("DO_NOT_PUBLISH_SECRET",str(page))

    def test_supervised_model_http429_is_retried_after_cooldown(self):
        from unittest.mock import patch
        from urllib.error import HTTPError
        with core.connect() as db:
            db.execute("INSERT INTO state(key,value) VALUES(?,?)",
                ("founder_bridge_last_rejected_projects",json.dumps([{
                    "reason_code":"project_not_allowed","project_id":"noetfield-earnloop",
                    "company_id":"noetfield-systems-inc"}])))
        operations_relay.tick()
        os.environ.update({"LLM_BASE_URL":"https://provider.invalid/v1",
                           "LLM_API_KEY":"fixture-secret","LLM_MODEL":"fixture"})
        with patch("urllib.request.urlopen",side_effect=HTTPError(
                "https://provider.invalid/v1/chat/completions",429,"rate-limited",{},None)):
            engineer=core.claim("tasks")
            core.process_task(engineer)
        with core.connect() as db:
            row=db.execute("SELECT * FROM tasks WHERE id=?",(engineer["id"],)).fetchone()
            self.assertEqual(json.loads(row["result"])["model_error_code"],"HTTP_429")
            db.execute("UPDATE tasks SET updated_at=? WHERE id=?",(
                (datetime.now(timezone.utc)-timedelta(minutes=8)).isoformat(),engineer["id"]))
        result=operations_relay.tick(timestamp=time.time()+120)
        self.assertIn("SUPERVISED_MODEL_RETRY",result["action_types"])
        with core.connect() as db:
            row=db.execute("SELECT * FROM tasks WHERE id=?",(engineer["id"],)).fetchone()
            self.assertEqual(row["status"],"queued")
        self.assertFalse(operations_relay.snapshot()["end_to_end_motor_execution_proven"])

    def test_failed_engineer_blocks_manager_until_scoped_retry_succeeds(self):
        from unittest.mock import patch
        from urllib.error import HTTPError
        with core.connect() as db:
            db.execute("INSERT INTO state(key,value) VALUES(?,?)",
                ("founder_bridge_last_rejected_projects",json.dumps([{
                    "reason_code":"project_not_allowed","project_id":"noetfield-earnloop",
                    "company_id":"noetfield-systems-inc"}])))
        operations_relay.tick()
        os.environ.update({"LLM_BASE_URL":"https://provider.invalid/v1",
                           "LLM_API_KEY":"fixture-only","LLM_MODEL":"fixture"})
        with patch("urllib.request.urlopen",side_effect=HTTPError(
            "https://provider.invalid/v1/chat/completions",429,"rate limit",{},None)):
            first=core.claim("tasks")
            self.assertEqual(first["role"],"engineering_operator")
            core.process_task(first)
        with core.connect() as db:
            self.assertEqual(db.execute("SELECT status FROM tasks WHERE id=?",
                                         (first["id"],)).fetchone()[0],"blocked")
        # A manager MUST NOT claim a model error as an engineer's completed draft.
        self.assertIsNone(core.claim("tasks"))
        with core.connect() as db:
            manager=db.execute("SELECT * FROM tasks WHERE role='chief_of_staff'").fetchone()
            self.assertEqual(manager["status"],"blocked")
            db.execute("UPDATE tasks SET updated_at=? WHERE id=?",(
                (datetime.now(timezone.utc)-timedelta(minutes=8)).isoformat(),first["id"]))
        self.assertIn("SUPERVISED_MODEL_RETRY",
                      operations_relay.tick(timestamp=time.time()+120)["action_types"])
        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self,*_): return False
            def read(self):
                return json.dumps({
                    "choices":[{"message":{"content":json.dumps({
                        "assessment":"Diagnosed scoped model outage; retry succeeded.",
                        "next_best_action":"Validate published receipt",
                        "risk_flags":[],"evidence":[]})}}],
                    "usage":{"prompt_tokens":17,"completion_tokens":9}
                }).encode()
        with patch("urllib.request.urlopen",return_value=FakeResponse()):
            repaired=core.claim("tasks")
            self.assertEqual(repaired["id"],first["id"])
            core.process_task(repaired)
            with core.connect() as db:
                self.assertEqual(db.execute("SELECT status FROM tasks WHERE id=?",
                                             (repaired["id"],)).fetchone()[0],"drafted")
                self.assertEqual(db.execute("SELECT status FROM tasks WHERE id=?",
                                             (manager["id"],)).fetchone()[0],"blocked")
            self.assertIn("DEPENDENCY_RECOVERED",
                          operations_relay.tick(timestamp=time.time()+240)["action_types"])
            resumed=core.claim("tasks")
            self.assertEqual(resumed["role"],"chief_of_staff")
            core.process_task(resumed)
        view=operations_relay.snapshot()
        self.assertEqual(sum(1 for i in view["handoffs"] if i["actual_model_call_observed"]),2)
        self.assertFalse(view["end_to_end_motor_execution_proven"])

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
        self.assertEqual(view["handoffs"][0]["response_kind"],"DETERMINISTIC_INTERNAL_DRAFT")
        self.assertEqual(view["handoffs"][0]["result_kind"],"INTERNAL_DRAFT")
        self.assertFalse(view["end_to_end_motor_execution_proven"])


if __name__=="__main__":
    unittest.main()
