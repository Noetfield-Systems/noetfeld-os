import os
import time
import unittest
import hf_station_bridge as hf

class HFStationBoundaryTests(unittest.TestCase):
    def test_contract_rejects_missing_and_untrusted_input(self):
        with self.assertRaises(hf.StationError):
            hf._validate_request({"task_id":"task-1"})
        p={"task_id":"task-123","role_id":"coding-diagnostician","goal_id":"goal-123",
           "decision_ref":"decision-123",
           "expires_at":"2099-01-01T00:00:00Z",
           "prompt":"Inspect a sanitized build failure","max_cost_usd":0.02,"max_tokens":256}
        self.assertEqual(hf._validate_request(p),p)
        p["prompt"]="Bearer a-secret"
        with self.assertRaises(hf.StationError): hf._validate_request(p)
    def test_expiry_enforced(self):
        p={"task_id":"task-123","role_id":"coding-diagnostician","goal_id":"goal-123",
           "decision_ref":"decision-123","nac_workpacket_ref":"nac-123",
           "expires_at":"2020-01-01T00:00:00Z","prompt":"Diagnose sanitized logs",
           "max_cost_usd":0.02}
        with self.assertRaises(hf.StationError): hf._validate_request(p)
    def test_nac_reference_is_not_supplied_by_untrusted_dispatch(self):
        p={"task_id":"task-123","role_id":"coding-diagnostician","goal_id":"goal-123",
           "decision_ref":"decision-123","nac_workpacket_ref":"fake-nac",
           "expires_at":"2099-01-01T00:00:00Z",
           "prompt":"Analyze a synthetic CI failure","max_cost_usd":0.02}
        with self.assertRaises(hf.StationError):hf._validate_request(p)

    def test_request_signature(self):
        a=hf._sign("secret","123",b"body")
        self.assertEqual(a,hf._sign("secret","123",b"body"))
        self.assertNotEqual(a,hf._sign("secret","123",b"altered"))
    def test_callback_auth_requires_distinct_service_identity(self):
        os.environ.pop("HF_STATION_CALLBACK_TOKEN",None)
        self.assertFalse(hf.callback_authorized("Bearer x"))
        os.environ["HF_STATION_CALLBACK_TOKEN"]="c"*48
        self.assertTrue(hf.callback_authorized("Bearer "+"c"*48))
        self.assertFalse(hf.callback_authorized("Bearer "+"d"*48))
        os.environ.pop("HF_STATION_CALLBACK_TOKEN",None)
if __name__=="__main__": unittest.main()
