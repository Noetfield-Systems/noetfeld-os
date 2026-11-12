"""Real local Company OS boundaries on the existing canonical worker/DB.

These tests prove distinct per-venture executive/team configurations, strict
project-scoped inference admission and autonomous event-to-task continuation.
They do NOT treat synthetic fixtures as users or claim actual code deployments.
"""
import os
import json
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

    def test_farid_receives_real_founder_mandate_before_first_member_metric(self):
        # No real users, no analytics, no paid transaction and no fabricated
        # BuildRelay observation. Source is the ORIGINAL adopted Founder goal.
        product_loops.register({
            "company_id":"founder-portfolio",
            "project_id":"buildrelay-bridge-economy",
            "name":"BuildRelay","vertical":"founder-network",
            "objective":"Activate authentic founder collaborations and bilateral receipts",
            "priority":4,"max_tasks_per_cycle":6})
        with core.connect() as db:
            venture.reconcile(db)
            absent=venture._queue_first_named_manager_source_assignment(db)
            self.assertEqual(absent["state"],
                             "NO_AUTHENTIC_MANAGER_SOURCE_OR_FOUNDER_MANDATE")
            db.commit()
        goal={
            "schema":"sina.company-os.venture-mandate.v1",
            "program_id":"f"*32,
            "mission_id":"M07-VENTURE-NETWORK",
            "project_id":"buildrelay-bridge-economy",
            "company_id":None,"tenant_scope":"founder-portfolio",
            "objective":"Launch actual BuildRelay founder matching and verified bilateral collaboration through useful onboarding and seven-day sprint execution",
            "priority_score":94,
            "success_metric":"verified_activated_members_and_bilateral_collaboration",
            "authority":"PORTFOLIO_DIRECTIVE_ONLY_NO_PERMIT",
            "execution_owner":"PROJECT_LOCAL_COMPANY_OS",
            "source_ref":"strategic:M07-VENTURE-NETWORK:v1",
        }
        adopted=venture.adopt_founder_mandate(goal)
        self.assertEqual(adopted["state"],"ADOPTED_LOCAL_COMPANY_OS")
        with core.connect() as db:
            first=venture._queue_first_named_manager_source_assignment(db)
            self.assertEqual(first["state"],"QUEUED_IN_ORIGINAL_COMPANY_OS")
            self.assertEqual(first["original_source_kind"],"ORIGINAL_FOUNDER_MANDATE")
            self.assertTrue(first["original_event_id"].startswith(
                "company_mandate:"+goal["program_id"]+":"))
            self.assertEqual(first["actor_id"],"gm-buildrelay-farid")
            self.assertEqual(first["external_actions"],False)
            repeated=venture._queue_first_named_manager_source_assignment(db)
            self.assertEqual(repeated["state"],"ALREADY_QUEUED")
            event=db.execute("SELECT * FROM events WHERE id=?",
                             (first["original_queue_event_id"],)).fetchone()
            db.commit()
        produced=product_loops.process_signal(dict(event))
        self.assertTrue(produced["executive_task"])
        with core.connect() as db:
            tasks=db.execute(
                "SELECT role,company_id,project_id FROM tasks WHERE event_id=?",
                (event["id"],)).fetchall()
            self.assertTrue(any(x["role"]=="chief_of_staff" for x in tasks))
            self.assertTrue(all(x["company_id"]=="founder-portfolio"
                and x["project_id"]=="buildrelay-bridge-economy" for x in tasks))
            self.assertEqual(db.execute(
                "SELECT COUNT(*) FROM product_observations WHERE company_id=? "
                "AND project_id=? AND source_event_id LIKE 'manager-first-source:%'",
                ("founder-portfolio","buildrelay-bridge-economy")).fetchone()[0],1)
        self.assertFalse(first["independently_verified"])

    def test_unbacked_fake_mandate_observation_cannot_commission_farid(self):
        product_loops.register({
            "company_id":"founder-portfolio",
            "project_id":"buildrelay-bridge-economy",
            "name":"BuildRelay","vertical":"founder-network",
            "objective":"Authentic founder team matching from original evidence",
            "priority":3,"max_tasks_per_cycle":5})
        with core.connect() as db:
            venture.reconcile(db)
            product_loops._insert_observation(db,
                "founder-portfolio","buildrelay-bridge-economy",{
                    "source_event_id":"company_mandate:"+"e"*32+":deadbeefabcd",
                    "source_kind":"REPORTED_OPERATIONAL",
                    "source_ref":"company-os:portfolio-directive",
                    "signal":"feature_request",
                    "summary":"An unbacked observation cannot mint Founder authority",
                    "severity":2},verified=False)
            attempt=venture._queue_first_named_manager_source_assignment(db)
            self.assertEqual(attempt["state"],
                             "NO_AUTHENTIC_MANAGER_SOURCE_OR_FOUNDER_MANDATE")
            db.commit()

    def test_real_tagged_farid_run_starts_one_original_source_bound_followup(self):
        product_loops.register({
            "company_id":"founder-portfolio",
            "project_id":"buildrelay-bridge-economy",
            "name":"BuildRelay","vertical":"founder-network",
            "objective":"Real qualified founder matching and bilateral contribution receipts",
            "priority":4,"max_tasks_per_cycle":6})
        source=product_loops.observe("founder-portfolio","buildrelay-bridge-economy",{
            "source_event_id":"br-local-real-source-fixture",
            "source_kind":"REPORTED_OPERATIONAL",
            "source_ref":"company-os:test-real-source",
            "signal":"activation",
            "summary":"Only a synthetic test fixture; not a real BuildRelay member",
            "severity":1})
        with core.connect() as db:
            venture.reconcile(db)
            first=venture._queue_first_named_manager_source_assignment(db)
            self.assertTrue(first["queued"])
            self.assertEqual(venture._queue_manager_source_followup(db)["state"],
                             "WAITING_FOR_REAL_MANAGER_MODEL_REPLY")
            event=dict(db.execute("SELECT * FROM events WHERE id=?",
                                  (first["original_queue_event_id"],)).fetchone())
            db.commit()
        product_loops.process_signal(event)
        with core.connect() as db:
            manager_task=db.execute("""SELECT id,observation_id FROM tasks
                WHERE event_id=? AND role='chief_of_staff'""",
                (event["id"],)).fetchone()
            self.assertIsNotNone(manager_task)
            run_id="run_model_real_001"
            db.execute("UPDATE tasks SET status='drafted' WHERE id=?",
                       (manager_task["id"],))
            db.execute("""INSERT INTO runs
                (id,task_id,role,provider,model,status,input_tokens,output_tokens,
                 started_at,finished_at,result)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)""",(
                run_id,manager_task["id"],"chief_of_staff",
                "sina-cloudflare","glm-4.7-flash","completed",
                135,210,"2026-11-11T16:01:00Z",
                "2026-11-11T16:01:08Z",
                json.dumps({
                    "manager_actor_id":"gm-buildrelay-farid",
                    "next_best_action":"Investigate the real profile-to-first-match gap with source-linked activation evidence",
                    "external_execution_verified":False,
                    "independent_business_outcome_verified":False,
                })))
            first_followup=venture._queue_manager_source_followup(db)
            self.assertEqual(first_followup["state"],
                             "SOURCE_BACKED_MANAGER_FOLLOWUP_QUEUED")
            self.assertEqual(first_followup["original_manager_run_id"],run_id)
            self.assertTrue(first_followup["queued"])
            self.assertFalse(first_followup["independent_verification"])
            self.assertFalse(first_followup["external_actions"])
            self.assertEqual(venture._queue_manager_source_followup(db)["state"],
                             "FOLLOWUP_ALREADY_QUEUED")
            row=db.execute("SELECT * FROM product_observations WHERE id=?",
                           (first_followup["source_observation_id"],)).fetchone()
            self.assertEqual(row["source_ref"],"company-os:run:"+run_id)
            self.assertEqual(row["verification"],"SOURCE_REPORTED_UNVERIFIED")
            event2=dict(db.execute("SELECT * FROM events WHERE id=?",
                                   (first_followup["original_queue_event_id"],)).fetchone())
            db.commit()
        continued=product_loops.process_signal(event2)
        self.assertGreaterEqual(continued["task_count"],2)
        with core.connect() as db:
            self.assertTrue(db.execute("SELECT id FROM tasks WHERE event_id=?",
                                       (event2["id"],)).fetchone())
            self.assertEqual(db.execute(
                "SELECT COUNT(*) FROM product_observations WHERE source_event_id=?",
                ("manager-followup:gm-buildrelay-farid:v1",)).fetchone()[0],1)

    def test_manager_followup_does_not_accept_unattributed_model_result(self):
        product_loops.register({
            "company_id":"founder-portfolio",
            "project_id":"buildrelay-bridge-economy",
            "name":"BuildRelay","vertical":"founder-network",
            "objective":"Maintain genuine bounded company task provenance",
            "priority":3,"max_tasks_per_cycle":5})
        product_loops.observe("founder-portfolio","buildrelay-bridge-economy",{
            "source_event_id":"br-second-fixture-only",
            "source_kind":"REPORTED_OPERATIONAL",
            "source_ref":"company-os:test-source",
            "signal":"activation","summary":"Test-only operational observation",
            "severity":1})
        with core.connect() as db:
            venture.reconcile(db)
            first=venture._queue_first_named_manager_source_assignment(db)
            event=dict(db.execute("SELECT * FROM events WHERE id=?",
                                  (first["original_queue_event_id"],)).fetchone())
            db.commit()
        product_loops.process_signal(event)
        with core.connect() as db:
            task=db.execute("SELECT id FROM tasks WHERE event_id=? AND role='chief_of_staff'",
                            (event["id"],)).fetchone()
            db.execute("UPDATE tasks SET status='drafted' WHERE id=?",(task["id"],))
            db.execute("""INSERT INTO runs
                 (id,task_id,role,provider,model,status,input_tokens,output_tokens,
                  started_at,finished_at,result)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?)""",(
                 "run_untagged",task["id"],"chief_of_staff",
                 "sina-cloudflare","glm-4.7-flash","completed",
                 80,100,"2026-11-11T16:05:00Z","2026-11-11T16:05:10Z",
                 json.dumps({"next_best_action":"Perform an unauthorized arbitrary action",
                   "external_execution_verified":False,
                   "independent_business_outcome_verified":False})))
            result=venture._queue_manager_source_followup(db)
            self.assertEqual(result["state"],"WAITING_FOR_REAL_MANAGER_MODEL_REPLY")
            self.assertFalse(result["queued"])
            db.commit()

    def test_first_named_manager_mission_requires_original_buildrelay_source_and_is_once_only(self):
        product_loops.register({
            "company_id":"founder-portfolio","project_id":"buildrelay-bridge-economy",
            "name":"BuildRelay","vertical":"founder-network",
            "objective":"Real founder matching and bilateral collaboration after qualified onboarding",
            "priority":3,"max_tasks_per_cycle":5})
        with core.connect() as db:
            venture.reconcile(db)
            self.assertEqual(
                venture._queue_first_named_manager_source_assignment(db)["state"],
                "NO_AUTHENTIC_MANAGER_SOURCE_OR_FOUNDER_MANDATE")
            db.commit()
        # A reported aggregate is authentic source transport, not a
        # qualified-human metric. This is synthetic UNIT-TEST input only.
        source=product_loops.observe("founder-portfolio","buildrelay-bridge-economy",{
            "source_event_id":"br-20261111-ready-profiles",
            "source_kind":"REPORTED_OPERATIONAL",
            "source_ref":"https://buildrelay-staging-staging.up.railway.app/api/v1/growth-ops/snapshot",
            "signal":"activation","metric_name":"ready_profiles",
            "metric_value":0,"sample_count":1,
            "summary":"BuildRelay qualified profile source reports count zero; synthetic test fixture only",
            "severity":1,
        })
        with core.connect() as db:
            first=venture._queue_first_named_manager_source_assignment(db)
            self.assertEqual(first["state"],"QUEUED_IN_ORIGINAL_COMPANY_OS")
            self.assertTrue(first["queued"])
            self.assertEqual(first["original_source_observation_id"],source["observation_id"])
            assert first["original_queue_event_id"]
            again=venture._queue_first_named_manager_source_assignment(db)
            self.assertEqual(again["state"],"ALREADY_QUEUED")
            self.assertFalse(again["queued"])
            event=db.execute("SELECT * FROM events WHERE id=?",(
                first["original_queue_event_id"],)).fetchone()
            self.assertEqual(event["status"],"queued")
            count=db.execute("""SELECT COUNT(*) FROM product_observations
                WHERE source_event_id='manager-first-source:gm-buildrelay-farid:v1'""").fetchone()[0]
            self.assertEqual(count,1)
            db.commit()
        dispatched=product_loops.process_signal(dict(event))
        # The source queue creates specialist tasks first, then a dependency-
        # gated chief_of_staff executive synthesis task, not a specialist
        # listed as "chief_of_staff" inside the specialist array.
        self.assertTrue(dispatched["executive_task"])
        self.assertGreaterEqual(dispatched["task_count"],2)
        with core.connect() as db:
            original=db.execute("""SELECT role,company_id,project_id,status
                FROM tasks WHERE event_id=?""",(first["original_queue_event_id"],)).fetchall()
        self.assertTrue(any(x["role"]=="chief_of_staff"
            and x["company_id"]=="founder-portfolio"
            and x["project_id"]=="buildrelay-bridge-economy" for x in original))
        self.assertFalse(first["external_actions"])
        self.assertFalse(first["independently_verified"])

    def test_farid_degraded_source_task_recovers_once_without_new_queue(self):
        product_loops.register({
            "company_id":"founder-portfolio","project_id":"buildrelay-bridge-economy",
            "name":"BuildRelay","vertical":"founder-network",
            "objective":"Enable authentic founder matching and bilateral collaboration",
            "priority":3,"max_tasks_per_cycle":5})
        with core.connect() as db:
            venture.reconcile(db)
            db.commit()
        original=product_loops.observe("founder-portfolio","buildrelay-bridge-economy",{
            "source_event_id":"br-test-source-only",
            "source_kind":"REPORTED_OPERATIONAL",
            "source_ref":"https://buildrelay.example.test/test-source",
            "signal":"activation","metric_name":"ready_profiles",
            "metric_value":0,"sample_count":1,
            "summary":"TEST FIXTURE ONLY — source observation, not real users",
            "severity":1})
        with core.connect() as db:
            queued=venture._queue_first_named_manager_source_assignment(db)
            self.assertEqual(queued["original_source_observation_id"],original["observation_id"])
            event=dict(db.execute("SELECT * FROM events WHERE id=?",
                                  (queued["original_queue_event_id"],)).fetchone())
            db.commit()
        dispatched=product_loops.process_signal(event)
        self.assertGreaterEqual(dispatched["task_count"],2)
        with core.connect() as db:
            row=db.execute("SELECT id FROM tasks WHERE event_id=? AND role='engineering_operator'",
                           (event["id"],)).fetchone()
            self.assertIsNotNone(row)
            task_id=row["id"]
            db.execute("UPDATE tasks SET status='drafted',updated_at=datetime('now','-4 minutes') WHERE id=?",
                       (task_id,))
            db.execute("""INSERT INTO runs(id,task_id,role,provider,model,status,
                         input_tokens,output_tokens,started_at,finished_at,result)
                         VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                       ("run_failed",task_id,"engineering_operator","specialist_degraded",
                        "none","degraded",0,0,"2026-11-11T23:31:00Z",
                        "2026-11-11T23:31:01Z",'{"model_issue_class":"HTTPError"}'))
            db.commit()
        with patch.object(sina_work_bridge,"specialist_configured",return_value=True):
            with core.connect() as db:
                first=venture._recover_named_manager_tasks(db)
                self.assertEqual(first["state"],"ONE_SHOT_ORIGINAL_TASK_RECOVERY")
                self.assertEqual(first["original_task_ids"],[task_id])
                db.commit()
            with core.connect() as db:
                self.assertEqual(db.execute("SELECT status FROM tasks WHERE id=?",
                                            (task_id,)).fetchone()["status"],"queued")
                db.execute("UPDATE tasks SET status='drafted',updated_at=datetime('now','-4 minutes') WHERE id=?",
                           (task_id,))
                # A repeated degraded result cannot resurrect work indefinitely.
                second=venture._recover_named_manager_tasks(db)
                self.assertEqual(second["requeued_count"],0)
                self.assertEqual(db.execute("SELECT status FROM tasks WHERE id=?",
                                            (task_id,)).fetchone()["status"],"drafted")
                db.commit()
        # A later HTTP 429 must wait until the real provider cap is revised.
        with core.connect() as db:
            db.execute("""INSERT INTO runs(id,task_id,role,provider,model,status,
                input_tokens,output_tokens,started_at,finished_at,result)
                VALUES(?,?,?,?,?,?,?,?,?,strftime('%Y-%m-%dT%H:%M:%SZ','now'),?)""",
                ("run_quota_429",task_id,"engineering_operator",
                 "specialist_degraded","none","degraded",0,0,
                 "2026-11-11T23:40:00Z",
                 '{"model_issue_code":"MODEL_HTTP_429"}'))
            db.execute("UPDATE tasks SET status='drafted',updated_at=datetime('now','-4 minutes') WHERE id=?",
                       (task_id,))
            db.commit()
        with patch.object(sina_work_bridge,"specialist_configured",return_value=True):
            with patch.dict(os.environ,{"COMPANY_OS_FARID_CAPACITY_REVISION":""}):
                with core.connect() as db:
                    self.assertEqual(venture._recover_named_manager_capacity(db)["requeued_count"],0)
                    self.assertEqual(venture._recover_named_manager_tasks(db)["requeued_count"],0)
            with patch.dict(os.environ,{"COMPANY_OS_FARID_CAPACITY_REVISION":"cap96-20261111"}):
                with core.connect() as db:
                    capacity=venture._recover_named_manager_capacity(db)
                    self.assertEqual(capacity["state"],"CAPACITY_REOPENED_ORIGINAL_TASKS")
                    self.assertEqual(capacity["original_task_ids"],[task_id])
                    self.assertEqual(capacity["policy_revision"],"cap96-20261111")
                    db.commit()
                with core.connect() as db:
                    self.assertEqual(db.execute("SELECT status FROM tasks WHERE id=?",
                                                (task_id,)).fetchone()["status"],"queued")
                    db.execute("UPDATE tasks SET status='drafted',updated_at=datetime('now','-4 minutes') WHERE id=?",
                               (task_id,))
                    self.assertEqual(venture._recover_named_manager_capacity(db)["requeued_count"],0)
                    db.commit()
        manager=venture.portfolio(project_id="buildrelay-bridge-economy")["instances"][0]["manager"]
        self.assertEqual(manager["capacity_recovery_count_visible"],1)
        self.assertEqual(manager["one_shot_original_task_recoveries_visible"],1)
        self.assertEqual(manager["degraded_original_model_runs_visible"],0)
        self.assertGreaterEqual(manager["team_degraded_model_runs_recorded"],1)
        self.assertFalse(manager["independent_product_delivery_verified"])

    def test_actual_failed_specialist_model_run_is_not_completed(self):
        product_loops.register({
            "company_id":"founder-portfolio","project_id":"buildrelay-bridge-economy",
            "name":"BuildRelay","vertical":"founder-network",
            "objective":"Build working first useful founder matching experience",
            "priority":3,"max_tasks_per_cycle":5})
        with core.connect() as db:
            venture.reconcile(db)
            task_id=core.add_task(db,None,None,"portfolio","engineering_operator",
                "BuildRelay real task with unavailable specialist provider",
                "Investigate authentic BuildRelay activation evidence",
                "Draft the next engineering acceptance criteria")
            db.execute("UPDATE tasks SET company_id=?,project_id=?,status='running' WHERE id=?",
                       ("founder-portfolio","buildrelay-bridge-economy",task_id))
            row=db.execute("SELECT * FROM tasks WHERE id=?",(task_id,)).fetchone()
            task=dict(row)
            db.commit()
        with patch.object(sina_work_bridge,"configured",return_value=False), \
             patch.object(sina_work_bridge,"specialist_configured",return_value=True), \
             patch.object(sina_work_bridge,"is_company_os_task",return_value=True), \
             patch.object(sina_work_bridge,"specialist_proposal",side_effect=RuntimeError("model_unavailable")):
            core.process_task(task)
        with core.connect() as db:
            record=db.execute("SELECT status,provider FROM runs WHERE task_id=? ORDER BY rowid DESC LIMIT 1",
                              (task_id,)).fetchone()
            self.assertEqual(record["provider"],"specialist_degraded")
            self.assertEqual(record["status"],"degraded")
            self.assertNotEqual(record["status"],"completed")
            full=db.execute("SELECT result FROM runs WHERE task_id=? ORDER BY rowid DESC LIMIT 1",
                            (task_id,)).fetchone()
            details=json.loads(full["result"])
            self.assertEqual(details["model_issue_code"],"MODEL_RUNTIME_ERROR")
            self.assertNotIn("model_unavailable",json.dumps(details.get("model_issue_code")))

    def test_real_founder_mandate_is_linked_to_farid_without_forged_ack(self):
        product_loops.register({
            "company_id":"founder-portfolio","project_id":"buildrelay-bridge-economy",
            "name":"BuildRelay","vertical":"founder-network",
            "objective":"Authentic founder matching and bilateral 7 day collaboration",
            "priority":3,"max_tasks_per_cycle":5})
        directive={
            "schema":"sina.company-os.venture-mandate.v1",
            "program_id":"b"*32,"mission_id":"M35-BUILDRELAY-GLOBAL",
            "project_id":"buildrelay-bridge-economy","company_id":None,
            "tenant_scope":"founder-portfolio",
            "objective":"Make BuildRelay onboarding and founder matching work for actual users with trustworthy seven day sprint outcomes",
            "priority_score":91,"success_metric":"genuine_founder_matches_with_bilateral_receipts",
            "authority":"PORTFOLIO_DIRECTIVE_ONLY_NO_PERMIT",
            "execution_owner":"PROJECT_LOCAL_COMPANY_OS",
            "source_ref":"strategic:M35-BUILDRELAY-GLOBAL:v1"}
        with patch.object(sina_work_bridge,"_resolve_operating_project",
                          return_value="buildrelay-bridge-economy"):
            admitted=venture.adopt_founder_mandate(directive)
        self.assertEqual(admitted["state"],"ADOPTED_LOCAL_COMPANY_OS")
        with core.connect() as db:
            original_event=dict(db.execute("SELECT * FROM events WHERE id=?",
                                           (admitted["event_id"],)).fetchone())
        out=product_loops.process_signal(original_event)
        self.assertGreaterEqual(out["task_count"],2)
        manager=venture.portfolio(project_id="buildrelay-bridge-economy")["instances"][0]["manager"]
        self.assertEqual(len(manager["original_founder_mandate_cases"]),1)
        before=manager["original_founder_mandate_cases"][0]
        self.assertEqual(before["founder_program_id"],directive["program_id"])
        self.assertEqual(before["mission_id"],directive["mission_id"])
        self.assertEqual(before["state"],"TASKS_CREATED_NO_NAMED_MANAGER_REPLY")
        self.assertIn(out["executive_task"],before["original_manager_task_ids"])
        self.assertFalse(before["manager_ack_verified"])
        self.assertFalse(before["independent_product_delivery_verified"])
        self.assertFalse(before["autonomous_next_action_verified"])
        with core.connect() as db:
            db.execute("""INSERT INTO runs
                (id,task_id,role,provider,model,status,input_tokens,
                 output_tokens,started_at,finished_at,result)
                VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                ("run_farid_mandate_reply",out["executive_task"],
                 "chief_of_staff","sina-deepseek","deepseek-v4-flash",
                 "completed",120,180,"2026-11-11T23:42:00Z",
                 "2026-11-11T23:42:08Z",
                 '{"manager_actor_id":"gm-buildrelay-farid","assessment":"internal recommendation"}'))
            db.commit()
        after=venture.portfolio(project_id="buildrelay-bridge-economy")["instances"][0]["manager"]
        case=after["original_founder_mandate_cases"][0]
        self.assertEqual(case["state"],"MANAGER_MODEL_REPLY_OBSERVED_REVIEW_PENDING")
        self.assertEqual(case["original_manager_model_reply_count_visible"],1)
        self.assertEqual(case["manager_model_reply_refs"][0]["original_manager_run_id"],
                         "run_farid_mandate_reply")
        self.assertFalse(case["manager_ack_verified"])
        self.assertFalse(case["manager_reviewed_team_verified"])
        self.assertFalse(case["independent_product_delivery_verified"])
        self.assertFalse(case["autonomous_next_action_verified"])
        other=venture.portfolio(project_id="cairn-season-0")["instances"][0]
        self.assertIsNone(other["manager"])

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
