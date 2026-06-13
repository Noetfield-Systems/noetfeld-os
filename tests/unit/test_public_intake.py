"""Public intake API and LLM fallback."""

from __future__ import annotations

import asyncio
from unittest.mock import patch

from httpx import ASGITransport, AsyncClient

from noetfield_governance.api import app
from noetfield_governance.chat_errors import ChatAPIError
from noetfield_governance.public_chat import answer_public_question


def test_intake_health() -> None:
    async def run() -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/intake/health")
        assert response.status_code == 200
        body = response.json()
        assert body["enabled"] is True
        assert "ops_email_configured" in body
        assert "auto_ack_enabled" in body

    asyncio.run(run())


def test_intake_submit() -> None:
    async def run() -> None:
        from noetfield_governance import intake_repository

        await intake_repository.init_intake_repository()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/intake",
                json={
                    "organization": "Acme Bank",
                    "contact_email": "lead@acme.example",
                    "message": "Interested in Trust Brief.",
                    "request_id": "RID-TEST123-ABC",
                    "source": "web",
                },
            )
        assert response.status_code == 200
        body = response.json()
        assert body["intake_id"].startswith("INT-")
        assert body["request_id"] == "RID-TEST123-ABC"

    asyncio.run(run())


def test_intake_submit_work_with_us_vector() -> None:
    async def run() -> None:
        from noetfield_governance import intake_repository

        await intake_repository.init_intake_repository()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/intake",
                json={
                    "organization": "Partner Co",
                    "contact_email": "partner@example.com",
                    "message": "Connector application.",
                    "vector": "work-with-us",
                    "sku": "general",
                    "metadata": {"program_lane": "connector", "async": True},
                    "source": "web",
                },
            )
        assert response.status_code == 200
        body = response.json()
        assert body["intake_id"].startswith("INT-")
        assert "async" in body["message"].lower()

    asyncio.run(run())


def test_llm_fallback_openrouter_to_gemini() -> None:
    async def run() -> None:
        calls: list[str] = []

        def fake_generate(*, provider, **_kwargs):
            calls.append(provider)
            if provider == "openrouter":
                raise ChatAPIError("openrouter down")
            return "Fallback answer from Gemini."

        with patch("noetfield_governance.public_chat._generate_sync", side_effect=fake_generate):
            reply, provider, _citations = await answer_public_question(
                message="What is Trust Brief?",
                provider="auto",
                gemini_api_key="gem-key",
                gemini_model="gemini-2.0-flash",
                openrouter_api_key="or-key",
                openrouter_model="google/gemini-2.0-flash-001",
                client_key="test-fallback",
            )
        assert reply == "Fallback answer from Gemini."
        assert provider == "gemini"
        assert calls == ["openrouter", "gemini"]

    asyncio.run(run())
