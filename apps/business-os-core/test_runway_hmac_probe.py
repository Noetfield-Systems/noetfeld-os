"""No secret/body logging; valid HMAC != a successful Runtime job."""
import io
import json
import os
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

import runway_hmac_probe as p


class TestRunwayHmacProbe(unittest.TestCase):
    def test_nonce_backend_failure_distinct_from_invalid_signature(self):
        self.assertEqual(p.classify(401, "AUTH_FAILED", "supabase rpc consume_runway_runtime_nonce_v1 HTTP 530"), "HMAC_VALID_NONCE_BACKEND_UNAVAILABLE")
        self.assertEqual(p.classify(503, "AUTH_BACKEND_UNAVAILABLE", ""), "HMAC_VALID_NONCE_BACKEND_UNAVAILABLE")
        self.assertEqual(p.classify(401, "AUTH_SIGNATURE_INVALID", ""), "HMAC_SIGNATURE_MISMATCH")
        self.assertEqual(p.classify(401, "AUTH_KEY_UNKNOWN", ""), "HMAC_KEY_ID_NOT_FOUND")
        self.assertEqual(p.classify(200, None, ""), "HMAC_AUTHENTICATED")

    def test_missing_credentials_does_not_open_network(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(p.urllib.request, "urlopen", side_effect=AssertionError("network not allowed")):
            result = p.probe()
        self.assertFalse(result["configured_secret"])
        self.assertEqual(result["verdict"], "NOT_CONFIGURED")

    def test_unresolved_railway_reference_does_not_call_network(self):
        with patch.dict(os.environ, {
            "NOETFIELD_RUNWAY_API_URL": "https://runtime.example",
            "NOETFIELD_RUNWAY_API_SECRET": "${{BROKEN_REFERENCE}}",
        }, clear=True), patch.object(p.urllib.request, "urlopen", side_effect=AssertionError("no network")):
            result = p.probe()
        self.assertEqual(result["verdict"], "REFERENCE_UNRESOLVED")

    def test_signature_rejected_status_safe_and_secret_not_logged(self):
        secret = "SUPER-PRIVATE-SECRET-DO-NOT-LOG"
        def respond(req, timeout):
            self.assertIn("NOETFIELD-HMAC staging-proof:", req.headers.get("Authorization", ""))
            raise HTTPError(req.full_url, 401, "invalid", {}, io.BytesIO(
                json.dumps({"error": "AUTH_SIGNATURE_INVALID", "detail": secret}).encode()))
        with patch.dict(os.environ, {
            "NOETFIELD_RUNWAY_API_URL": "https://runtime.example",
            "NOETFIELD_RUNWAY_API_SECRET": secret,
        }, clear=True), patch.object(p.urllib.request, "urlopen", side_effect=respond):
            result = p.probe()
        self.assertEqual(result["verdict"], "HMAC_SIGNATURE_MISMATCH")
        self.assertNotIn(secret, json.dumps(result))

    def test_backend_error_returns_sanitized_verdict(self):
        def respond(req, timeout):
            raise HTTPError(req.full_url, 401, "backend", {}, io.BytesIO(
                b'{"error":"AUTH_FAILED","detail":"supabase rpc consume_runway_runtime_nonce_v1 HTTP 530: PRIVATE"}'))
        with patch.dict(os.environ, {
            "NOETFIELD_RUNWAY_API_URL": "https://runtime.example",
            "NOETFIELD_RUNWAY_API_SECRET": "x" * 32,
        }, clear=True), patch.object(p.urllib.request, "urlopen", side_effect=respond):
            result = p.probe()
        self.assertEqual(result["verdict"], "HMAC_VALID_NONCE_BACKEND_UNAVAILABLE")
        self.assertNotIn("PRIVATE", json.dumps(result))


if __name__ == "__main__":
    unittest.main()
