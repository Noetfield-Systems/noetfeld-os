"""BuildRelay / Company OS scoped ingress tests. Disposable SQLite only."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import core
import buildrelay_intake

class BuildRelayInbound(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.prev=core.DB
        core.DB=Path(self.tmp.name)/"isolated-company.sqlite"
        self.env=patch.dict(os.environ,{
            "COMPANY_OS_PORTFOLIO_AUTOSTART":"false",
            "BUILDRELAY_COMPANY_OS_BEARER":"a"*48,
        })
        self.env.start()
        core.init()

    def tearDown(self):
        self.env.stop()
        core.DB=self.prev
        self.tmp.cleanup()

    def body(self):
        return dict(schema="buildrelay.company-os.observation.v1",
                    source_event_id="br-20261111-member-accounts",
                    metric="member_accounts",value=0,
                    observed_at="2026-11-11T12:00:00Z")

    def test_auth_scope_idempotency_and_true_zero(self):
        self.assertFalse(buildrelay_intake.authorized(None))
        self.assertFalse(buildrelay_intake.authorized("Bearer wrong"))
        self.assertTrue(buildrelay_intake.authorized("Bearer "+"a"*48))
        first=buildrelay_intake.accept(self.body())
        self.assertTrue(first["accepted"])
        self.assertFalse(first["idempotent"])
        self.assertFalse(first["real_users_independently_verified"])
        self.assertEqual(first["project_id"],"buildrelay-bridge-economy")
        self.assertEqual(first["company_id"],"founder-portfolio")
        repeat=buildrelay_intake.accept(self.body())
        self.assertTrue(repeat["idempotent"])
        self.assertEqual(first["observation_id"],repeat["observation_id"])
        status=buildrelay_intake.status()
        self.assertEqual(status["observation_count"],1)
        self.assertEqual(status["observations"][0]["metric_value"],0)
        self.assertEqual(status["observations"][0]["verification"],"SOURCE_REPORTED_UNVERIFIED")
        with core.connect() as db:
            foreign=db.execute("SELECT COUNT(*) AS n FROM product_programs WHERE project_id='cairn-season-0'").fetchone()
            self.assertEqual(foreign["n"],0)
            queued=db.execute("SELECT COUNT(*) AS n FROM events WHERE event_type='product.signal_observed'").fetchone()
            self.assertGreaterEqual(queued["n"],1)

    def test_rejects_cross_scope_and_false_growth(self):
        b=self.body()
        for bad in [
            dict(b,company_id="noetfield-systems-inc"),
            dict(b,metric="payments",source_event_id="br-20261111-payments"),
            dict(b,metric="ready_profiles"),
            dict(b,value=-1),
            dict(b,value=True),
            dict(b,value=1.2),
            dict(b,source_event_id="test-metric-fake"),
        ]:
            with self.subTest(payload=bad),self.assertRaises(ValueError):
                buildrelay_intake.accept(bad)
        buildrelay_intake.accept(b)
        with self.assertRaises(ValueError):
            buildrelay_intake.accept(dict(b,value=7))

if __name__=="__main__":
    unittest.main()
