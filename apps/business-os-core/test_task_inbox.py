"""Full work queue: real source rows, bounded paging and filters, no extra workers."""
import tempfile
import unittest
from pathlib import Path

import core
import app
from fastapi import HTTPException


class TaskInboxTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.old_db=core.DB
        self.old_token=app.TOKEN
        core.DB=Path(self.tmp.name)/"company.sqlite"
        app.TOKEN="FIXTURE_FOUNDER_KEY"
        core.init()
        with core.connect() as db:
            for i in range(85):
                status=("drafted","queued","completed")[i%3]
                brand="noetfield" if i%2==0 else "signalforge"
                title="Special milestone for investor" if i==27 else f"Review work item {i:03d}"
                db.execute(
                    """INSERT INTO tasks(id,brand,role,title,objective,next_action,autonomy,status,created_at,updated_at)
                       VALUES(?,?,?,?,?,?,?,?,?,?)""",
                    (f"task_fixture_{i:03d}",brand,"partnerships",title,
                     "Review actual scope and evidence","Verify next action","draft",
                     status,f"2026-11-12T{i%24:02d}:00:00+00:00","2026-11-12T19:00:00+00:00")
                )

    def tearDown(self):
        core.DB=self.old_db
        app.TOKEN=self.old_token
        self.tmp.cleanup()

    def inbox(self,**changes):
        arguments={"authorization":"Bearer FIXTURE_FOUNDER_KEY","limit":40,"offset":0,
                   "status":None,"brand":None,"q":""}
        arguments.update(changes)
        return app.task_inbox(**arguments)

    def test_page_entire_queue_no_missing_or_repeated_rows(self):
        pages=[self.inbox(offset=0),self.inbox(offset=40),self.inbox(offset=80)]
        self.assertEqual([len(p["tasks"]) for p in pages],[40,40,5])
        self.assertTrue(pages[0]["has_more"])
        self.assertFalse(pages[2]["has_more"])
        self.assertTrue(all(p["total"]==85 for p in pages))
        ids=[x["id"] for p in pages for x in p["tasks"]]
        self.assertEqual(len(set(ids)),85)
        self.assertEqual(pages[0]["source"],"Company OS durable tasks")
        self.assertFalse(pages[0]["verified_outcomes_inferred"])

    def test_status_brand_and_search(self):
        drafts=self.inbox(status="drafted")
        self.assertEqual(drafts["total"],29)
        self.assertTrue(all(x["status"]=="drafted" for x in drafts["tasks"]))
        filtered=self.inbox(brand="signalforge",q="Special milestone")
        self.assertEqual(filtered["total"],1)
        self.assertEqual(filtered["tasks"][0]["id"],"task_fixture_027")
        self.assertEqual(self.inbox(q="No such known title")["total"],0)

    def test_rejects_invalid_filters_and_bad_auth(self):
        for args in (
            {"limit":101},
            {"offset":-1},
            {"brand":"unknown"},
            {"status":"something_unknown"},
            {"q":"z"*121},
            {"authorization":None},
        ):
            with self.subTest(args=args):
                with self.assertRaises(HTTPException) as err:
                    self.inbox(**args)
                self.assertIn(err.exception.status_code,(401,422))

    def test_literal_search_does_not_match_wildcards(self):
        self.assertEqual(self.inbox(q="%")["total"],0)
        self.assertEqual(self.inbox(q="fixture_027")["total"],1)
        self.assertEqual(self.inbox(q="fixture%027")["total"],0)


if __name__=="__main__":
    unittest.main()
