"""Resend intake webhook and status API."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
import time

from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr

from noetfield_governance import api as governance_api
from noetfield_governance.api import app
from noetfield_governance.resend_webhook import verify_svix_signature


def _sign_payload(payload: bytes, secret: str) -> dict[str, str]:
    msg_id = "msg_test_001"
    msg_ts = str(int(time.time()))
    key_part = secret[6:] if secret.startswith("whsec_") else secret
    secret_bytes = base64.b64decode(key_part)
    signed = f"{msg_id}.{msg_ts}.".encode() + payload
    digest = hmac.new(secret_bytes, signed, hashlib.sha256).digest()
    signature = "v1," + base64.b64encode(digest).decode("utf-8")
    return {
        "svix-id": msg_id,
        "svix-timestamp": msg_ts,
        "svix-signature": signature,
    }


def test_intake_health_includes_resend_webhook_flags() -> None:
    async def run() -> None:
        original = governance_api.settings.resend_webhook_secret
        governance_api.settings.resend_webhook_secret = SecretStr("whsec_" + base64.b64encode(b"test-secret").decode())
        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/intake/health")
            assert response.status_code == 200
            body = response.json()
            assert body["resend_webhook_configured"] is True
            assert body["email_delivery_tracking"] is True
        finally:
            governance_api.settings.resend_webhook_secret = original

    asyncio.run(run())


def test_resend_webhook_updates_intake_status() -> None:
    async def run() -> None:
        from noetfield_governance import intake_repository

        await intake_repository.init_intake_repository()
        original = governance_api.settings.resend_webhook_secret
        secret = "whsec_" + base64.b64encode(b"resend-webhook-test").decode()
        governance_api.settings.resend_webhook_secret = SecretStr(secret)
        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                submit = await client.post(
                    "/api/intake",
                    json={
                        "organization": "Webhook Test Co",
                        "contact_email": "ops@example.com",
                        "message": "Resend webhook test.",
                        "request_id": "RID-WEBHOOK-TEST-001",
                        "source": "web",
                    },
                )
                assert submit.status_code == 200

                event = {
                    "type": "email.delivered",
                    "data": {
                        "subject": "Noetfield — Contact (RID-WEBHOOK-TEST-001)",
                        "tags": [{"name": "request_id", "value": "RID-WEBHOOK-TEST-001"}],
                    },
                }
                payload = json.dumps(event).encode("utf-8")
                headers = _sign_payload(payload, secret)
                webhook = await client.post(
                    "/api/intake/resend/webhook",
                    content=payload,
                    headers={**headers, "content-type": "application/json"},
                )
                assert webhook.status_code == 200
                body = webhook.json()
                assert body["handled"] is True
                assert body["status"] == "delivered"

                status = await client.get(
                    "/api/intake/status",
                    params={"request_id": "RID-WEBHOOK-TEST-001"},
                )
            assert status.status_code == 200
            status_body = status.json()
            assert status_body["request_id"] == "RID-WEBHOOK-TEST-001"
            assert status_body["email_archive_status"] == "delivered"
        finally:
            governance_api.settings.resend_webhook_secret = original

    asyncio.run(run())


def test_verify_svix_signature_roundtrip() -> None:
    secret = "whsec_" + base64.b64encode(b"roundtrip").decode()
    payload = b'{"type":"email.delivered"}'
    headers = _sign_payload(payload, secret)
    assert verify_svix_signature(payload, headers, secret) is True
    assert verify_svix_signature(payload, headers, "whsec_wrong") is False
