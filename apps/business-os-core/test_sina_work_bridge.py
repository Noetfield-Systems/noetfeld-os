"""One bounded canonical task handoff test, no extra dispatcher or fake revenue."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import core
import product_loops
import sina_work_bridge as bridge

class CompanySinaOrgBridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.original_db=core.DB
        core.DB=Path(self.tmp.name)/"company.sqlite3"
        self.original_autostart=os.environ.pop("COMPANY_OS_PORTFOLIO_AUTOSTART",None)
        core.init()
        product_loops.register({
          "company_id":"noetfield-systems-inc",
          "project_id":"noetfield-company-os-commercial-product",
          "name":"Company OS commercial operations",
          "vertical":"enterprise",
          "objective":"Grow authentic company operating system adoption and customer value",
          "priority":4,"max_tasks_per_cycle":7,
        })
    def tearDown(self):
        core.DB=self.original_db
        if self.original_autostart is not None:
            os.environ["COMPANY_OS_PORTFOLIO_AUTOSTART"]=self.original_autostart
        self.tmp.cleanup()
    def work(self,request_id="a"*32):
        return {
          "schema":"sina.company-os.workpacket-request.v1",
          "request_id":request_id,"program_id":"b"*32,
          "origin":"sina_autonomous_organization",
          "authority":"ADVISORY_ONLY_NO_PERMIT",
          "company_id":"noetfield-systems-inc",
          "project_id":"noetfield-company-os-commercial-product",
          "tenant_scope":"noetfield-systems-inc",
          "business_outcome":"Improve legitimate customer acquisition",
          "functional_unit":"growth",
          "requested_role":"growth_operator",
          "task":"Develop actionable distribution improvements and measurable real-user funnel experiments",
          "priority_score":75,
          "resources":{"budget_usd":0,"financial_effect_allowed":False},
          "dependencies":[],
          "acceptance":["Write measurable plan"],
          "governance":{
            "governor_decision_required":True,"NAC_workpacket_required":True,
            "self_verification_allowed":False,
            "customer_outreach_allowed":False,"production_mutation_allowed":False,
            "cross_tenant_access":False
          },
          "routing_state":"NOT_DISPATCHED_COMPANY_OS_OWNS_EXECUTION",
        }
    def test_canonical_strategic_workpacket_admitted_and_metric_preserved(self):
        packet=self.work("2"*32)
        packet["strategic_mission_id"]="M09-RHEVO-LAUNCH"
        packet["success_metric"]="real_creator_launches_real_users_retention_and_verified_fee_flow"
        result=bridge.receive(packet)
        self.assertEqual(result["state"],"CREATED_CANONICAL_TASK")
        with core.connect() as db:
            task=db.execute("SELECT objective FROM tasks WHERE id=?",
                            (result["task_id"],)).fetchone()
            self.assertIn("M09-RHEVO-LAUNCH",task["objective"])
            self.assertIn("real_creator_launches",task["objective"])
        self.assertEqual(bridge.receive(packet)["task_id"],result["task_id"])

    def test_unknown_or_unpaired_strategic_fields_still_rejected(self):
        for suffix in (
            {"success_metric":"verified_real_user_retention"},
            {"strategic_mission_id":"M09-RHEVO-LAUNCH"},
            {"strategic_mission_id":"../unsafe","success_metric":"verified_real_user_retention"},
            {"strategic_mission_id":"M09-RHEVO-LAUNCH","success_metric":"not valid metric"},
            {"strategic_mission_id":"M09-RHEVO-LAUNCH","success_metric":"verified_real_user_retention",
             "new_permit":"ALLOW_ALL"}
        ):
            with self.subTest(suffix=suffix):
                packet=self.work("3"*32)
                packet.update(suffix)
                with self.assertRaises(ValueError):
                    bridge.receive(packet)
        with core.connect() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM sina_workstream_bindings").fetchone()[0],0)

    def test_real_company_queue_receives_typed_work_once(self):
        x=bridge.receive(self.work())
        self.assertEqual(x["state"],"CREATED_CANONICAL_TASK")
        self.assertEqual(bridge.receive(self.work())["task_id"],x["task_id"])
        with core.connect() as db:
            task=db.execute("SELECT role,company_id,project_id,status FROM tasks WHERE id=?",
                            (x["task_id"],)).fetchone()
            self.assertEqual(task["role"],"marketing_content")
            self.assertEqual(task["company_id"],"noetfield-systems-inc")
            self.assertEqual(task["status"],"queued")
            count=db.execute("SELECT COUNT(*) FROM sina_workstream_bindings").fetchone()[0]
            self.assertEqual(count,1)
    def test_unregistered_active_founder_venture_uses_canonical_company_program(self):
        new=self.work("e"*32)
        new["company_id"]=None
        new["tenant_scope"]="founder-portfolio"
        new["project_id"]="venture-formation-lab"
        owner_verified={"projects":[
          {"project_id":"venture-formation-lab","company_id":None,"name":"Venture Formation Lab"}
        ]}
        with patch("founder_portfolio_bridge.fetch_projection",return_value=owner_verified):
            first=bridge.receive(new)
        self.assertEqual(first["state"],"CREATED_CANONICAL_TASK")
        self.assertEqual(first["operational_project_id"],"venture-formation-lab")
        with core.connect() as db:
            enrolled=db.execute("SELECT status FROM product_programs WHERE company_id=? AND project_id=?",
                                ("founder-portfolio","venture-formation-lab")).fetchone()
            self.assertEqual(enrolled["status"],"FOUNDER_PROJECT_ACTIVE_NOT_LEGAL_TENANT")
        self.assertEqual(bridge.receive(new)["task_id"],first["task_id"])

    def test_existing_operational_alias_is_reused_not_duplicate_registry(self):
        product_loops.register({
          "company_id":"founder-portfolio","project_id":"atelier",
          "name":"Atelier community","vertical":"social-community",
          "objective":"Grow real community memberships and customer retention",
          "priority":4,"max_tasks_per_cycle":5})
        item=self.work("f"*32)
        item["company_id"]=None
        item["tenant_scope"]="founder-portfolio"
        item["project_id"]="atelier-community"
        result=bridge.receive(item)
        self.assertEqual(result["operational_project_id"],"atelier")
        with core.connect() as db:
            self.assertIsNone(db.execute("SELECT * FROM product_programs WHERE project_id='atelier-community'").fetchone())

    def test_new_company_scope_requires_independently_read_founder_owner(self):
        item=self.work("9"*32)
        item["project_id"]="noetfield-verification-layer"
        for source in (
            {"projects":[]},
            {"projects":[{"project_id":"noetfield-verification-layer",
                          "company_id":None,"name":"Not a Noetfield company product"}]},
        ):
            with patch("founder_portfolio_bridge.fetch_projection",return_value=source):
                with self.assertRaises(ValueError):
                    bridge.receive(item)
            with core.connect() as db:
                self.assertIsNone(db.execute(
                    "SELECT 1 FROM product_programs WHERE project_id='noetfield-verification-layer'"
                ).fetchone())
        with patch("founder_portfolio_bridge.fetch_projection",
                   side_effect=RuntimeError("upstream offline")):
            with self.assertRaises(RuntimeError):
                bridge.receive(item)

    def test_real_degraded_specialist_task_retries_once_in_same_canonical_queue(self):
        import json
        x=bridge.receive(self.work("8"*32))
        with core.connect() as db:
            db.execute("UPDATE tasks SET status='drafted',updated_at=? WHERE id=?",
                       ("2024-01-01T00:00:00+00:00",x["task_id"]))
            db.execute("""INSERT INTO runs VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                       ("run_"+"8"*16,x["task_id"],"marketing_content",
                        "specialist_degraded","none","completed",0,0,
                        "2024-01-01T00:00:00+00:00","2024-01-01T00:00:00+00:00",
                        json.dumps({"error":"temporary model response unavailable"})))
        with patch.dict(os.environ,{"SINA_ORG_SPECIALIST_TOKEN":"s"*48}):
            self.assertEqual(bridge.retry_degraded(limit=2),1)
            self.assertEqual(bridge.retry_degraded(limit=2),0)
        with core.connect() as db:
            t=db.execute("SELECT status FROM tasks WHERE id=?",(x["task_id"],)).fetchone()
            self.assertEqual(t["status"],"queued")
            b=db.execute("SELECT specialist_retry_count FROM sina_workstream_bindings WHERE task_id=?",
                         (x["task_id"],)).fetchone()
            self.assertEqual(b["specialist_retry_count"],1)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM tasks WHERE id=?",
                                        (x["task_id"],)).fetchone()[0],1)

    def test_mission_artifacts_use_real_canonical_tasks_only_and_redact_private_data(self):
        import json
        x=bridge.receive(self.work("7"*32))
        example={"provider":"sina-deepseek","recommendation":{
            "assessment":"Founder user interview identified an onboarding opportunity",
            "draft_artifact":{"deliverables":[
                "Draft a product onboarding experiment with precise conversion metrics for the platform",
                "Contact alice@example.com by email with the private token sk-abcdefghijklmnop"]},
            "next_best_action":"Develop evidence-linked landing page conversion experiment",
            "success_metric":"Observed legitimate activation rate"}}
        with core.connect() as db:
            db.execute("UPDATE tasks SET result=?,status='drafted' WHERE id=?",
                       (json.dumps(example),x["task_id"]))
        artifact=bridge.results_for_founder([x["task_id"],"task_"+"f"*16])
        self.assertEqual(artifact["found"],1)
        self.assertEqual(artifact["verified_receipts"],0)
        item=artifact["items"][0]
        self.assertEqual(item["task_id"],x["task_id"])
        self.assertEqual(item["provider"],"sina-deepseek")
        self.assertFalse(item["external_action_executed"])
        self.assertIn("[email redacted]",item["deliverables"][1])
        self.assertNotIn("alice@example.com",json.dumps(artifact))
        self.assertNotIn("sk-abcdefghijklmnop",json.dumps(artifact))
        with self.assertRaises(ValueError):
            bridge.results_for_founder(["task_BAD_ID"])
        with self.assertRaises(ValueError):
            bridge.results_for_founder([x["task_id"]]*2)

    def test_no_cross_tenant_or_self_verification(self):
        wrong=self.work("c"*32)
        wrong["tenant_scope"]="other"
        with self.assertRaises(ValueError):bridge.receive(wrong)
        bogus=self.work("d"*32)
        bogus["functional_unit"]="verification"
        with self.assertRaises(ValueError):bridge.receive(bogus)
        unsafe=self.work("e"*32)
        unsafe["resources"]["budget_usd"]=10000
        with self.assertRaises(ValueError):bridge.receive(unsafe)

if __name__=="__main__":
    unittest.main()
