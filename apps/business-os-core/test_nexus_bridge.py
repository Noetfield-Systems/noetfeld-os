"""Tests for scoped NEXUS → canonical Company OS product operating program."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
import app
import core
import product_loops


class NexusCompanyOSBridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.old_db=core.DB
        core.DB=Path(self.tmp.name)/"company-os-nexus-test.db"
        self.prior=os.environ.get("COMPANY_OS_NEXUS_OBSERVATION_TOKEN")
        os.environ["COMPANY_OS_NEXUS_OBSERVATION_TOKEN"]="nexus-test-bridge-"+"x"*35
        core.init()
        product_loops.register({
            "company_id":"noetfield-systems-inc","project_id":"nexus-economic-rail",
            "name":"NEXUS Economic Rail","vertical":"agentic-economic-infrastructure",
            "objective":"Operate genuine agentic economic workflows with truthful revenue evidence.",
            "priority":5
        })
        self.client=TestClient(app.app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None,None,None)
        core.DB=self.old_db
        if self.prior is None:
            os.environ.pop("COMPANY_OS_NEXUS_OBSERVATION_TOKEN",None)
        else:
            os.environ["COMPANY_OS_NEXUS_OBSERVATION_TOKEN"]=self.prior
        self.tmp.cleanup()

    def payload(self):
        lid="nxlead_"+"a"*32
        return {"source_event_id":"nexus.lead."+lid,
                "source_kind":"REPORTED_OPERATIONAL",
                "source_ref":"nexus:growth-lead:"+lid,
                "signal":"acquisition",
                "summary":"Actual permissioned product inquiry received and queued; not verified as a customer or payment.",
                "severity":2,"metric_name":"inbound_inquiries","metric_value":1,
                "sample_count":1,"observed_at":"2026-11-09T14:00:00+00:00"}

    def test_scope_auth_and_real_source_ref(self):
        url="/api/integrations/nexus/observations"
        self.assertEqual(self.client.post(url,json=self.payload()).status_code,401)
        h={"X-Nexus-Bridge-Token":os.environ["COMPANY_OS_NEXUS_OBSERVATION_TOKEN"]}
        first=self.client.post(url,headers=h,json=self.payload())
        self.assertEqual(first.status_code,202,first.text)
        self.assertTrue(first.json()["canonical_queue"])
        self.assertFalse(first.json()["real_user_traction_verified"])
        again=self.client.post(url,headers=h,json=self.payload())
        self.assertEqual(again.status_code,200,again.text)
        self.assertEqual(first.json()["observation_id"],again.json()["observation_id"])
        with core.connect() as db:
            row=db.execute("""SELECT * FROM product_observations WHERE source_event_id=?""",
                           (self.payload()["source_event_id"],)).fetchone()
            self.assertEqual(row["company_id"],"noetfield-systems-inc")
            self.assertEqual(row["project_id"],"nexus-economic-rail")
            self.assertEqual(row["signal"],"acquisition")
            self.assertEqual(row["verification"],"SOURCE_REPORTED_UNVERIFIED")

    def test_rejects_impersonation_and_fabrication(self):
        url="/api/integrations/nexus/observations"
        h={"X-Nexus-Bridge-Token":os.environ["COMPANY_OS_NEXUS_OBSERVATION_TOKEN"]}
        variants=[
            {"company_id":"other-company"},
            {"source_kind":"SYNTHETIC_AGENT_QA"},
            {"source_ref":"nexus:growth-lead:nxlead_"+"b"*32},
            {"signal":"revenue"},
            {"metric_name":"collected_revenue"},
            {"metric_value":50000},
            {"summary":"Contact from fake@example.org must not cross into Company OS"},
        ]
        for variant in variants:
            with self.subTest(variant=variant):
                sample={**self.payload(),**variant}
                res=self.client.post(url,headers=h,json=sample)
                self.assertIn(res.status_code,(400,422))
        self.assertEqual(self.client.post(url,headers={"X-Nexus-Bridge-Token":"wrong"},json=self.payload()).status_code,401)


if __name__=="__main__":
    unittest.main()
