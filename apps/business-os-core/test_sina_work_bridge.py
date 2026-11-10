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

if __name__=="__main__":
    unittest.main()
