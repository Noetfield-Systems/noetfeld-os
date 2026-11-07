import json
import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import app
import core


class CompanyOSPublicIntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.original_db = core.DB
        core.DB = Path(self.temp.name) / "company-os-test.sqlite"
        app.RATE.clear()
        app.TOKEN = "founder-test-token"
        os.environ["COMPANY_OS_PROXY_TOKEN"] = "company-proxy-test-token"
        os.environ["COMPANY_OS_REQUIRE_PROXY_AUTH"] = "true"
        core.init()
        self.client = TestClient(app.app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        core.DB = self.original_db
        self.temp.cleanup()
        os.environ.pop("COMPANY_OS_PROXY_TOKEN", None)
        os.environ.pop("COMPANY_OS_REQUIRE_PROXY_AUTH", None)
        app.RATE.clear()

    def headers(self, client_hash="a" * 64):
        return {
            "X-Company-OS-Proxy-Token": "company-proxy-test-token",
            "X-Company-OS-Client-Hash": client_hash,
        }

    def body(self, **extra):
        payload = {
            "brand": "noetfield",
            "audience": "enterprise",
            "intent": "automation",
            "name": "Alex Example",
            "email": "alex@example.test",
            "company": "Example Manufacturing",
            "role": "COO",
            "problem": "We need to connect our service workflows and order operations.",
            "urgency": "30_days",
            "estimated_value": 0,
            "consent": True,
            "ai_consent": False,
            "website": "",
            "idempotency_key": "company-os-test-0001",
        }
        payload.update(extra)
        return payload

    def test_proxy_token_is_required_in_staging(self):
        response = self.client.post("/api/intake", json=self.body())
        self.assertEqual(response.status_code, 401)

    def test_invalid_proxy_fingerprint_is_rejected(self):
        response = self.client.post(
            "/api/intake",
            headers=self.headers("not-a-hash"),
            json=self.body(),
        )
        self.assertEqual(response.status_code, 400)

    def test_valid_request_is_accepted_and_queued(self):
        response = self.client.post(
            "/api/intake",
            headers=self.headers(),
            json=self.body(),
        )
        self.assertEqual(response.status_code, 202)
        result = response.json()
        self.assertTrue(result["accepted"])
        self.assertTrue(result["reference"])
        self.assertEqual(result["route"], "enterprise_solution")
        self.assertTrue(result["idempotent"])

        with core.connect() as db:
            event = db.execute(
                "SELECT * FROM events WHERE idempotency_key=?",
                ("company-os-test-0001",),
            ).fetchone()
        self.assertIsNotNone(event)
        payload = json.loads(event["payload"])
        self.assertFalse(payload["ai_consent"])
        self.assertEqual(event["source"], "company_os_staging_proxy")

    def test_retry_with_same_idempotency_key_returns_same_reference(self):
        first = self.client.post(
            "/api/intake",
            headers=self.headers(),
            json=self.body(),
        )
        second = self.client.post(
            "/api/intake",
            headers=self.headers(),
            json=self.body(),
        )
        self.assertEqual(first.status_code, 202)
        self.assertEqual(second.status_code, 202)
        self.assertEqual(first.json()["reference"], second.json()["reference"])
        with core.connect() as db:
            count = db.execute(
                "SELECT COUNT(*) AS n FROM events WHERE idempotency_key=?",
                ("company-os-test-0001",),
            ).fetchone()["n"]
        self.assertEqual(count, 1)

    def test_honeypot_is_silently_accepted_without_creating_event(self):
        response = self.client.post(
            "/api/intake",
            headers=self.headers(),
            json=self.body(website="https://spam.invalid"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["accepted"])
        with core.connect() as db:
            count = db.execute("SELECT COUNT(*) AS n FROM events").fetchone()["n"]
        self.assertEqual(count, 0)

    def test_consent_is_required(self):
        response = self.client.post(
            "/api/intake",
            headers=self.headers(),
            json=self.body(consent=False),
        )
        self.assertEqual(response.status_code, 400)

    def test_unknown_fields_are_rejected(self):
        response = self.client.post(
            "/api/intake",
            headers=self.headers(),
            json=self.body(founder_api_token="should-not-be-accepted"),
        )
        self.assertEqual(response.status_code, 422)

    def test_request_body_limit_runs_before_json_parsing(self):
        response = self.client.post(
            "/api/intake",
            headers={
                **self.headers(),
                "content-type": "application/json",
            },
            content=b"x" * 24001,
        )
        self.assertEqual(response.status_code, 413)

    def test_legacy_non_proxy_mode_remains_compatible(self):
        os.environ["COMPANY_OS_REQUIRE_PROXY_AUTH"] = "false"
        os.environ.pop("COMPANY_OS_PROXY_TOKEN", None)
        response = self.client.post(
            "/api/intake",
            json=self.body(idempotency_key=None),
        )
        self.assertEqual(response.status_code, 202)
        self.assertFalse(response.json()["idempotent"])


if __name__ == "__main__":
    unittest.main()
