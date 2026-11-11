"""Real local Company OS boundaries on the existing canonical worker/DB.

These tests prove distinct per-venture executive/team configurations, strict
project-scoped inference admission and autonomous event-to-task continuation.
They do NOT treat synthetic fixtures as users or claim actual code deployments.
"""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import core
import product_loops
import venture_company_os as venture
import sina_work_bridge

class LocalCompanyOSRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.prev=core.DB
        self.previous_autostart=os.environ.pop("COMPANY_OS_PORTFOLIO_AUTOSTART",None)
        core.DB=Path(self.tmp.name)/"company-os.sqlite3"
        core.init()
        for project,name,domain,company in (
            ("noetfield-web3-launchpad","RHEVO Creator Studio","creator-web3","noetfield-systems-inc"),
            ("cairn-season-0","Cairn Season Zero","community-web3","founder-portfolio"),
            ("social-games-lab","Social Games Lab","social-games","founder-portfolio"),
        ):
            product_loops.register({
                "company_id":company,"project_id":project,
                "name":name,"vertical":domain,
                "objective":"Build a useful authentic community product with real user evidence",
                "priority":3,"max_tasks_per_cycle":5,
            })
    def tearDown(self):
        core.DB=self.prev
        if self.previous_autostart is not None:
            os.environ["COMPANY_OS_PORTFOLIO_AUTOSTART"]=self.previous_autostart
        self.tmp.cleanup()

    def test_runtime_docker_image_includes_local_company_os(self):
        docker=(Path(__file__).with_name("Dockerfile")).read_text()
        copy_line=next(x for x in docker.splitlines() if x.startswith("COPY app.py "))
        self.assertIn("venture_company_os.py",copy_line)
        # The deployed image may add source files before app.py; assert the
        # actual compile contract, not a brittle ordering of arguments.
        compile_line=next(x for x in docker.splitlines()
                          if "python -m py_compile" in x)
        self.assertIn("app.py",compile_line)
        self.assertIn("core.py",compile_line)
        self.assertIn("venture_company_os.py",compile_line)

    def test_founder_sends_one_goal_and_cairn_company_os_creates_own_tasks(self):
        goal={
          "schema":"sina.company-os.venture-mandate.v1",
          "program_id":"a"*32,"mission_id":"M12-CAIRN-WEB3",
          "project_id":"cairn-season-0","company_id":None,
          "tenant_scope":"founder-portfolio",
          "objective":"Develop a genuinely useful BNB community challenge product with repeatable developer contribution and real participant retention",
          "priority_score":90,
          "success_metric":"authentic_bnb_community_activation_and_repeat_participation",
          "authority":"PORTFOLIO_DIRECTIVE_ONLY_NO_PERMIT",
          "execution_owner":"PROJECT_LOCAL_COMPANY_OS",
          "source_ref":"strategic:M12-CAIRN-WEB3:v1",
        }
        first=venture.adopt_founder_mandate(goal)
        self.assertEqual(first["state"],"ADOPTED_LOCAL_COMPANY_OS")
        self.assertEqual(venture.adopt_founder_mandate(goal)["state"],"UNCHANGED")
        with core.connect() as db:
            mandate=db.execute("SELECT * FROM venture_company_os_mandates "
                "WHERE project_id='cairn-season-0'").fetchone()
            self.assertEqual(mandate["success_metric"],goal["success_metric"])
            self.assertIsNone(db.execute("SELECT * FROM venture_company_os_mandates "
                "WHERE project_id='noetfield-web3-launchpad'").fetchone())
            event=db.execute("SELECT * FROM events WHERE id=?",(first["event_id"],)).fetchone()
        self.assertEqual(event["source"],"company_operating_program")
        produced=product_loops.process_signal(dict(event))
        self.assertIn("engineering_operator",produced["specialists"])
        with core.connect() as db:
            tasks=db.execute("SELECT company_id,project_id,role FROM tasks WHERE event_id=?",
                (first["event_id"],)).fetchall()
            self.assertEqual(len(tasks),produced["task_count"])
            self.assertTrue(all(x["project_id"]=="cairn-season-0"
                                and x["company_id"]=="founder-portfolio" for x in tasks))
            self.assertIn("chief_of_staff",{x["role"] for x in tasks})
        self.assertFalse(first["external_actions"])

    def test_mandate_rejects_fake_permit_and_cross_product_scope(self):
        item={
          "schema":"sina.company-os.venture-mandate.v1",
          "program_id":"a"*32,"mission_id":"M12-CAIRN-WEB3",
          "project_id":"cairn-season-0","company_id":None,
          "tenant_scope":"founder-portfolio",
          "objective":"Build genuine BNB developer challenges and real user participation in Cairn without simulated token holders",
          "priority_score":90,
          "success_metric":"authentic_bnb_community_activation_and_repeat_participation",
          "authority":"PORTFOLIO_DIRECTIVE_ONLY_NO_PERMIT",
          "execution_owner":"PROJECT_LOCAL_COMPANY_OS",
          "source_ref":"strategic:M12-CAIRN-WEB3:v1",
        }
        for changes in ({"authority":"PRODUCTION_PERMIT_GRANTED"},
                        {"tenant_scope":"noetfield-systems-inc"},
                        {"success_metric":"not a safe metric"},
                        {"extra_funding":10000}):
            wrong=dict(item,**changes)
            with self.subTest(wrong=changes):
                with self.assertRaises(ValueError):
                    venture.adopt_founder_mandate(wrong)

    def test_local_instances_have_distinct_teams_goals_and_scoped_memory(self):
        with core.connect() as db:
            synced=venture.reconcile(db)
            self.assertEqual(synced["instances_created"],3)
            self.assertEqual(venture.reconcile(db)["instances_created"],0)
            db.commit()
            rhevo=venture.specialist(db,"noetfield-systems-inc",
                                      "noetfield-web3-launchpad","engineering_operator")
            cairn=venture.specialist(db,"founder-portfolio",
                                      "cairn-season-0","engineering_operator")
            self.assertNotEqual(rhevo["instance_id"],cairn["instance_id"])
            self.assertIn("Devnet mint",rhevo["remit"])
            self.assertIn("BNB Season",cairn["remit"])
            self.assertIsNone(venture.specialist(db,"noetfield-systems-inc",
                                                  "cairn-season-0","engineering_operator"))
            self.assertIsNone(venture.specialist(db,"founder-portfolio",
                                                  "social-games-lab","sales_qualification"))
        snapshot=venture.portfolio(project_id="social-games-lab")
        self.assertEqual(snapshot["count"],1)
        self.assertEqual(snapshot["instances"][0]["memory_scope"],"founder-portfolio:social-games-lab")
        self.assertEqual(snapshot["instances"][0]["physical_isolation"],
                         "SHARED_RUNTIME_SCOPED_PROJECT_INSTANCE")

    def test_each_local_director_continues_without_sina_workpacket(self):
        now=1730600000.0
        first=venture.tick(clock=lambda:now,limit=1)
        self.assertEqual(first["state"],"COMPANY_LOOPS_ADVANCED")
        self.assertEqual(first["events_created"],1)
        self.assertEqual(venture.tick(clock=lambda:now+20,limit=1)["state"],"NOT_DUE")
        with core.connect() as db:
            rows=db.execute("SELECT company_id,project_id,source_event_id "
                            "FROM product_observations WHERE source_kind='REPORTED_OPERATIONAL' "
                            "AND source_event_id LIKE 'venture_company_os:%'").fetchall()
            self.assertEqual(len(rows),1)
            row=rows[0]
            self.assertTrue(venture.specialist(db,row["company_id"],row["project_id"],
                                               "chief_of_staff"))
        after=venture.tick(clock=lambda:now+301,limit=1)
        self.assertEqual(after["events_created"],1)
        with core.connect() as db:
            events=db.execute("SELECT COUNT(*) FROM events WHERE event_type='product.signal_observed'").fetchone()[0]
            self.assertGreaterEqual(events,2)

    def test_model_inference_bound_to_real_local_company_task_not_founder_only(self):
        with core.connect() as db:
            venture.reconcile(db)
            task_id=core.add_task(db,None,None,"portfolio","engineering_operator",
                                   "Cairn build next playable challenge",
                                   "Implement a real quest UI and test it against the existing Cairn community",
                                   "Draft engineering acceptance and artifact details")
            db.execute("UPDATE tasks SET company_id=?,project_id=?,status='running' WHERE id=?",
                       ("founder-portfolio","cairn-season-0",task_id))
            db.commit()
        self.assertFalse(sina_work_bridge.is_sina_task(task_id))
        self.assertTrue(sina_work_bridge.is_company_os_task(task_id))
        with core.connect() as db:
            db.execute("UPDATE tasks SET project_id=? WHERE id=?",("unknown-uncommissioned",task_id))
            db.commit()
        self.assertFalse(sina_work_bridge.is_company_os_task(task_id))

    def test_farid_is_mapped_to_real_role_but_old_runs_are_not_retroactively_credited(self):
        product_loops.register({
            "company_id":"founder-portfolio","project_id":"buildrelay-bridge-economy",
            "name":"BuildRelay","vertical":"founder-network",
            "objective":"Activate genuine founder introductions and bilateral sprint collaboration",
            "priority":3,"max_tasks_per_cycle":5})
        with core.connect() as db:
            venture.reconcile(db)
            task_id=core.add_task(db,None,None,"portfolio","chief_of_staff",
                  "BuildRelay manager investigation",
                  "Inspect authentic BuildRelay activation and choose a useful internal next step",
                  "Record source-backed proposal")
            db.execute("UPDATE tasks SET company_id=?,project_id=?,status='drafted' WHERE id=?",
                       ("founder-portfolio","buildrelay-bridge-economy",task_id))
            db.execute("""INSERT INTO runs
                 (id,task_id,role,provider,model,status,input_tokens,output_tokens,
                  started_at,finished_at,result)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                ("run_old",task_id,"chief_of_staff","sina-deepseek","deepseek",
                 "completed",100,200,"2026-11-11T01:00:00Z",
                 "2026-11-11T01:01:00Z",'{"assessment":"legacy role run"}'))
            db.commit()
        before=venture.portfolio(project_id="buildrelay-bridge-economy")["instances"][0]["manager"]
        self.assertEqual(before["actor_id"],"gm-buildrelay-farid")
        self.assertEqual(before["status"],"ROLE_MAPPED_AWAITING_NAMED_RUNTIME_RESPONSE")
        self.assertEqual(before["named_model_reply_count_visible"],0)
        self.assertFalse(before["executive_delegation_verified"])
        self.assertTrue(before["historical_role_runs_not_attributed_to_named_person"])
        with core.connect() as db:
            db.execute("""INSERT INTO runs
                 (id,task_id,role,provider,model,status,input_tokens,output_tokens,
                  started_at,finished_at,result)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                ("run_named",task_id,"chief_of_staff","sina-deepseek","deepseek",
                 "completed",200,400,"2026-11-11T02:00:00Z",
                 "2026-11-11T02:01:00Z",
                 '{"manager_actor_id":"gm-buildrelay-farid","assessment":"source linked role response"}'))
            db.commit()
        after=venture.portfolio(project_id="buildrelay-bridge-economy")["instances"][0]["manager"]
        self.assertEqual(after["status"],"MODEL_RESPONSE_OBSERVED")
        self.assertEqual(after["named_model_reply_count_visible"],1)
        self.assertEqual(after["original_runtime_records_with_identity_visible"],1)
        self.assertEqual(len(after["original_role_task_and_run_history_latest"]),2)
        self.assertFalse(after["independent_product_delivery_verified"])
        self.assertFalse(after["sina_to_manager_mandate_ack_verified"])

    def test_mapped_manager_uses_original_project_scoped_model_request(self):
        import json
        from unittest.mock import patch
        product_loops.register({
            "company_id":"founder-portfolio","project_id":"buildrelay-bridge-economy",
            "name":"BuildRelay","vertical":"founder-network",
            "objective":"Enable real matching and seven-day collaboration receipts",
            "priority":3,"max_tasks_per_cycle":5})
        with core.connect() as db:
            venture.reconcile(db)
            task_id=core.add_task(db,None,None,"portfolio","chief_of_staff",
                "BuildRelay first manager task",
                "Analyze actual activation and compare next authorized engineering opportunities",
                "Return one source-grounded recommendation")
            db.execute("UPDATE tasks SET company_id=?,project_id=?,status='running' WHERE id=?",
                       ("founder-portfolio","buildrelay-bridge-economy",task_id))
            db.commit()
        captured={}
        class Reply:
            status=200
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self,n):
                return json.dumps({
                    "schema":"sina.organization.specialist-draft.v1",
                    "task_id":task_id,"company_id":"founder-portfolio",
                    "project_id":"buildrelay-bridge-economy",
                    "role":"chief_of_staff","authority":"ADVISORY_INTERNAL_ONLY",
                    "external_actions_executed":False,
                    "result":{"external_action":"NOT_EXECUTED","assessment":"bounded local model result"}
                }).encode()
        class Client:
            def open(self,request,timeout):
                captured["body"]=json.loads(request.data)
                return Reply()
        task={
            "id":task_id,"company_id":"founder-portfolio",
            "project_id":"buildrelay-bridge-economy","role":"chief_of_staff",
            "objective":"Analyze actual activation and compare next authorized engineering opportunities"
        }
        with patch.dict(os.environ,{"SINA_ORG_SPECIALIST_TOKEN":"x"*45}):
            response=sina_work_bridge.specialist_proposal(task,fetch=Client())
        self.assertEqual(response["role"],"chief_of_staff")
        self.assertIn("You are Farid",captured["body"]["objective"])
        self.assertIn("gm-buildrelay-farid",captured["body"]["objective"])
        self.assertEqual(captured["body"]["project_id"],"buildrelay-bridge-economy")
        self.assertEqual(captured["body"]["company_id"],"founder-portfolio")
        self.assertEqual(captured["body"]["max_cost_usd"],0.015)

    def test_drafts_never_become_external_mutations_or_verified_revenue(self):
        self.assertFalse(venture.portfolio()["external_permit_issued"])
        with core.connect() as db:
            venture.reconcile(db);db.commit()
        state=venture.portfolio(company_id="founder-portfolio")
        self.assertEqual(state["count"],2)
        self.assertTrue(all(x["permitted_effects"]=="INTERNAL_DRAFTS_ONLY"
                            and not x["independent_verification"] for x in state["instances"]))

if __name__=="__main__":
    unittest.main()
