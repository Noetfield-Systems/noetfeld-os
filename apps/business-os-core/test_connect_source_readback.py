"""Source-key Company OS execution readback; never a simulated receipt."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from fastapi import HTTPException

import app
import core


class CompanyConnectReadbackTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.previous=core.DB
        core.DB=Path(self.tmp.name)/"business.sqlite"
        core.init()
        self.key="test-connect-read-only-"+"a"*48
        self.env=patch.dict(os.environ,{"CONNECT_BUSINESS_OS_READ_TOKEN":self.key})
        self.env.__enter__()

    def tearDown(self):
        self.env.__exit__(None,None,None)
        core.DB=self.previous
        self.tmp.cleanup()

    def sample(self):
        return {"intake_id":"INT-ABCDEF002468",
                "request_id":"RID-CNX-ABCDEF002468",
                "created_at":"2026-11-13T13:20:00+00:00",
                "sku":"general","vector":"external-opportunities",
                "qualification":None,
                "opportunity":{"category":"people","initiative":"noetfield",
                    "requested_next_step":"collaborate","source_channel":"linkedin"}}

    def test_strict_readonly_source_identity_and_real_task_receipts(self):
        signal=self.sample()
        receipt=core.queue_platform_intake_projection(signal)
        with core.connect() as db:
            evt=dict(db.execute("SELECT * FROM events WHERE id=?",
                                (receipt["event_id"],)).fetchone())
        core.process_platform_intake_signal(evt)
        response=app.source_backed_connect_case(signal["intake_id"],
                        x_noetfield_connect_read_token=self.key)
        data=json.loads(response.body)
        self.assertEqual(response.status_code,200)
        self.assertEqual(data["source_intake_id"],signal["intake_id"])
        self.assertGreater(data["task_count"],0)
        self.assertEqual(data["task_count"],len(data["tasks"]))
        self.assertFalse(data["independent_receipts_verified"])
        self.assertFalse(data["external_effects_verified"])
        self.assertFalse(data["payment_collected_verified"])
        self.assertNotIn("contact_email",json.dumps(data))
        self.assertNotIn("name",json.dumps(data))
        self.assertNotIn("LinkedIn discussion",json.dumps(data))
        self.assertIn("no-store",response.headers.get("cache-control",""))

    def test_cannot_use_founder_or_wrong_token(self):
        for provided in ("", "Bearer founder-secret", "wrong"):
            with self.assertRaises(HTTPException) as cm:
                app.source_backed_connect_case("INT-ABCDEF002468",
                    x_noetfield_connect_read_token=provided)
            self.assertEqual(cm.exception.status_code,401)
        with self.assertRaises(HTTPException) as cm:
            app.source_backed_connect_case("bad!",
                x_noetfield_connect_read_token=self.key)
        self.assertEqual(cm.exception.status_code,422)
        with self.assertRaises(HTTPException) as cm:
            app.source_backed_connect_case("INT-AAAAAAAAAAAA",
                x_noetfield_connect_read_token=self.key)
        self.assertEqual(cm.exception.status_code,404)

    def test_unconfigured_integration_denies_all(self):
        with patch.dict(os.environ,{"CONNECT_BUSINESS_OS_READ_TOKEN":""}):
            with self.assertRaises(HTTPException) as cm:
                app.source_backed_connect_case("INT-AAAAAAAAAAAA",
                    x_noetfield_connect_read_token=self.key)
            self.assertEqual(cm.exception.status_code,503)
