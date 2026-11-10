"""One bounded canonical task handoff test, no extra dispatcher or fake revenue."""
import os
import tempfile
import unittest
from pathlib import Path

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


    def test_unknown_canonical_project_becomes_analysis_only_when_ssot_owner_verified(self):
        item=self.work("f"*32)
        item["project_id"]="noetfield-verification-layer"
        canonical={"projects":[{
          "project_id":"noetfield-verification-layer",
          "company_id":"noetfield-systems-inc",
          "name":"Noetfield Verification Layer",
        }]}
        self.assertEqual(bridge.receive(item)["state"],"PROJECT_NOT_COMMISSIONED")
        result=bridge.receive(item,projection=canonical)
        self.assertEqual(result["state"],"CREATED_CANONICAL_TASK")
        self.assertEqual(bridge.receive(item,projection=canonical)["task_id"],result["task_id"])
        with core.connect() as db:
            program=db.execute(
               "SELECT status,health_url FROM product_programs WHERE company_id=? AND project_id=?",
               ("noetfield-systems-inc","noetfield-verification-layer")).fetchone()
            self.assertEqual(program["status"],"SINA_ADVISORY_INTAKE_ONLY")
            self.assertIsNone(program["health_url"])
            task=db.execute("SELECT role,project_id,status FROM tasks WHERE id=?",
                            (result["task_id"],)).fetchone()
            self.assertEqual(task["role"],"marketing_content")
            self.assertEqual(task["status"],"queued")
        self.assertNotIn("SINA_ADVISORY_INTAKE_ONLY",product_loops.ACTIVE_STATES)
        core.process_task(core.claim("tasks"))
        with core.connect() as db:
            self.assertEqual(db.execute(
                "SELECT count(*) FROM tasks WHERE project_id='noetfield-verification-layer'"
            ).fetchone()[0],1)

    def test_existing_alias_is_reused_without_duplicate_company_program(self):
        product_loops.register({
          "company_id":"founder-portfolio","project_id":"signalforge",
          "name":"SignalForge","vertical":"market-intelligence",
          "objective":"Improve genuine market intelligence and product usage without invented customers",
          "priority":4,
        })
        item=self.work("1"*32)
        item["company_id"]=None
        item["tenant_scope"]="founder-portfolio"
        item["project_id"]="signal-forge"
        canonical={"projects":[{"project_id":"signal-forge","company_id":None,"name":"SignalForge"}]}
        result=bridge.receive(item,projection=canonical)
        self.assertEqual(result["state"],"CREATED_CANONICAL_TASK")
        self.assertEqual(bridge.receive(item)["task_id"],result["task_id"])
        with core.connect() as db:
            task=db.execute("SELECT company_id,project_id FROM tasks WHERE id=?",
                            (result["task_id"],)).fetchone()
            self.assertEqual(task["company_id"],"founder-portfolio")
            self.assertEqual(task["project_id"],"signalforge")
            self.assertIsNone(db.execute(
               "SELECT 1 FROM product_programs WHERE project_id='signal-forge'").fetchone())

    def test_canonical_owner_conflict_never_creates_legal_tenant(self):
        item=self.work("2"*32)
        item["project_id"]="noetfield-verification-layer"
        false_owner={"projects":[{
          "project_id":"noetfield-verification-layer",
          "company_id":None,"name":"Wrong Owner",
        }]}
        with self.assertRaisesRegex(ValueError,"owner_scope_mismatch"):
            bridge.receive(item,projection=false_owner)
        with core.connect() as db:
            self.assertIsNone(db.execute(
               "SELECT 1 FROM product_programs WHERE project_id='noetfield-verification-layer'"
            ).fetchone())

if __name__=="__main__":
    unittest.main()
