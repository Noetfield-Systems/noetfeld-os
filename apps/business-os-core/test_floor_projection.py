import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import core
import floor_projection


class CompanyFloorProjectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.previous=core.DB
        core.DB=Path(self.tmp.name)/"business.sqlite"
        core.init()

    def tearDown(self):
        core.DB=self.previous
        self.tmp.cleanup()

    def test_service_identity_requires_distinct_read_token(self):
        with patch.dict(os.environ, {"COMPANY_FLOOR_CORE_READ_TOKEN": ""}):
            self.assertFalse(floor_projection.authorized("anything"))
        with patch.dict(os.environ, {"COMPANY_FLOOR_CORE_READ_TOKEN": "dedicated-floor-token"}):
            self.assertFalse(floor_projection.authorized(None))
            self.assertFalse(floor_projection.authorized("wrong"))
            self.assertTrue(floor_projection.authorized("dedicated-floor-token"))

    def test_live_snapshot_uses_canonical_tasks_not_fake_agents_or_pii(self):
        with core.connect() as db:
            tid=core.add_task(
                db,None,None,"noetfield","sales_qualification",
                "Private Acme Ltd CEO Alice",
                "alice@example.test wants a Copilot pilot",
                "Prepare internal recommendation only.",
            )
            db.execute(
                "UPDATE tasks SET status='drafted',priority_rank=10 WHERE id=?",(tid,)
            )
        snap=floor_projection.snapshot()
        self.assertEqual(snap["schema"],floor_projection.SCHEMA)
        self.assertIs(snap["read_only"],True)
        self.assertIs(snap["pii_included"],False)
        self.assertEqual(snap["tasks"][0]["id"],tid)
        self.assertEqual(snap["tasks"][0]["state"],"drafted")
        self.assertTrue(snap["tasks"][0]["requires_founder_review"])
        self.assertEqual(snap["tasks"][0]["verification"],"NOT_INDEPENDENTLY_VERIFIED")
        self.assertIsNone(snap["cash_collected"])
        self.assertIsNone(snap["tasks"][0]["evidence_hash"])
        wire=json.dumps(snap)
        self.assertNotIn("Acme",wire)
        self.assertNotIn("alice@example.test",wire)
        self.assertIn("CONFIGURED_ROLE_NOT_PROOF_OF_EXECUTION",wire)

if __name__=="__main__":
    unittest.main()
