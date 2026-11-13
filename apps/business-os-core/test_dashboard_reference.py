"""Reference dashboard: true source counts and venture/date scope without fabricated revenue."""
import tempfile
import unittest
from datetime import datetime,timezone
from pathlib import Path
from fastapi import HTTPException
import core
import app

class DashboardReferenceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.db_was=core.DB
        self.token_was=app.TOKEN
        core.DB=Path(self.temp.name)/"company.sqlite"
        app.TOKEN="FIXTURE-FOUNDER-TOKEN"
        core.init()
        now=datetime.now(timezone.utc).isoformat()
        with core.connect() as d:
            for idx,brand in enumerate(("noetfield","signalforge")):
                d.execute("""INSERT INTO tasks
                             (id,brand,role,title,objective,next_action,autonomy,status,created_at,updated_at)
                             VALUES(?,?,?,?,?,?,?,?,?,?)""",
                    (f"reference-task-{idx}",brand,"partnerships","Source-backed task",
                     "Verify the commercial context","Review evidence","internal","queued",now,now))
                d.execute("""INSERT INTO events
                             (id,event_type,source,brand,payload,status,attempts,created_at)
                             VALUES(?,?,?,?,?,?,?,?)""",
                    (f"reference-event-{idx}","test.fixture","internal",brand,"{}","processed",0,now))
    def tearDown(self):
        core.DB=self.db_was
        app.TOKEN=self.token_was
        self.temp.cleanup()
    def query(self,**overrides):
        args=dict(authorization="Bearer FIXTURE-FOUNDER-TOKEN",brand=None,days=7)
        args.update(overrides)
        return app.dashboard(**args)
    def test_source_counts_date_history_and_revenue_unknown(self):
        data=self.query()
        self.assertEqual(data["counts"]["pending_tasks"],2)
        self.assertEqual(data["counts"]["activity_events"],2)
        self.assertEqual(len(data["activity_daily"]),7)
        self.assertEqual(sum(x["count"] for x in data["activity_daily"]),2)
        self.assertEqual(data["collected_revenue"]["state"],"not_connected")
        self.assertIsNone(data["collected_revenue"]["amount"])
        self.assertEqual(data["source"],"Company OS durable tables")
    def test_independent_venture_scope_not_copied_from_portfolio(self):
        n=self.query(brand="noetfield")
        m=self.query(brand="signalforge")
        self.assertEqual(n["counts"]["pending_tasks"],1)
        self.assertEqual(m["counts"]["pending_tasks"],1)
        self.assertEqual(n["counts"]["activity_events"],1)
        self.assertEqual(m["counts"]["activity_events"],1)
    def test_date_options_and_no_invalid_scope(self):
        month=self.query(days=30)
        self.assertEqual(len(month["activity_daily"]),30)
        self.assertEqual(sum(x["count"] for x in month["activity_daily"]),2)
        for bad in ({"days":365},{"brand":"unknown"},{"authorization":None}):
            with self.subTest(bad=bad):
                with self.assertRaises(HTTPException) as error:self.query(**bad)
                self.assertIn(error.exception.status_code,(401,422))

if __name__=="__main__":
    unittest.main()
