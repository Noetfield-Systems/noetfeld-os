"""NOOS loop failure category must trigger machine repair, not Founder review.

No real Supabase network, credentials, or test-only completion claims.
"""
from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from noos_loop_runner_v1 import classify_step_failure


class ClassifiedLoopFailureTests(unittest.TestCase):
    def test_inbox_supabase_missing_table(self):
        raw=json.dumps({"ok":False,"error":'{"code":"PGRST205","message":"Could not find the table public.noetfield_worker_inbox_queue"}'})
        self.assertEqual(classify_step_failure("",raw),"SUPABASE_TABLE_NOT_FOUND")

    def test_inbox_nxdomain(self):
        raw=json.dumps({"ok":False,"error":"<urlopen error [Errno -2] Name or service not known>"})
        self.assertEqual(classify_step_failure("",raw),"SUPABASE_ENDPOINT_DNS_UNRESOLVED")

    def test_inbox_credential_rejected(self):
        raw=json.dumps({"ok":False,"error":"Invalid API key"})
        self.assertEqual(classify_step_failure("",raw),"UPSTREAM_CREDENTIAL_REJECTED")

    def test_plan_infer_runway_pin_from_structured_output(self):
        result={"ok":False,"dispatch":{"ok":False,"verdict":"BLOCKED_DEEPSEEK_PIN_DRIFT"}}
        self.assertEqual(classify_step_failure(json.dumps(result),""),"RUNWAY_MODEL_PIN_DRIFT")

    def test_plan_failed_sink_is_specific_not_unknown(self):
        result={"ok":False,"compile":{"ok":False,
          "supabase_sink":{"ok":False,"reason":"postgres_connection_failed"}}}
        self.assertEqual(classify_step_failure(json.dumps(result),""),"SUPABASE_PLAN_SINK_FAILED")

    def test_unknown_error_stays_unknown_and_no_raw_exception_is_returned(self):
        secret="EXAMPLE_TOP_SECRET_NEVER_ECHO_123456"
        category=classify_step_failure("",secret)
        self.assertEqual(category,"UNCLASSIFIED_NONZERO_EXIT")
        self.assertNotIn(secret,category)

    def test_auth_error_http_code(self):
        self.assertEqual(classify_step_failure("","HTTP Error 403: Forbidden"),
                         "UPSTREAM_PERMISSION_403")


if __name__=="__main__":
    unittest.main()
