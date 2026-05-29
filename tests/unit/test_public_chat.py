"""Public chat API — no real Gemini calls in unit tests."""

from __future__ import annotations

import asyncio
from unittest.mock import patch

from httpx import ASGITransport, AsyncClient

from noetfield_governance.api import app
from noetfield_governance.chatbot_knowledge import build_knowledge_context
from noetfield_governance.public_chat import resolve_chat_provider


def test_knowledge_context_includes_faq() -> None:
    ctx = build_knowledge_context()
    assert "Trust Brief" in ctx
    assert "operations@noetfield.com" in ctx
    assert "Bank Pilot" in ctx


def test_resolve_auto_prefers_openrouter() -> None:
    provider, _key = resolve_chat_provider(
        preference="auto",
        gemini_api_key="gemini-key",
        openrouter_api_key="or-key",
    )
    assert provider == "openrouter"


def test_no_api_keys_in_frontend_chat_script() -> None:
    from pathlib import Path

    text = (Path(__file__).resolve().parents[2] / "assets" / "noetfield-chat.js").read_text(
        encoding="utf-8"
    )
    assert "sk-or-v1-" not in text
    assert "GEMINI_API_KEY" not in text
    assert "OPENROUTER_API_KEY" not in text


def test_public_chat_health() -> None:
    async def run() -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/public/chat/health")
        assert response.status_code == 200
        body = response.json()
        assert "configured" in body
        assert "enabled" in body

    asyncio.run(run())


def test_public_chat_returns_reply_when_configured() -> None:
    async def run() -> None:
        with patch(
            "noetfield_governance.api.answer_public_question",
            return_value=("Trust Brief is $10,000 for six weeks.", "openrouter", ["OFFERINGS_LOCKED.md"]),
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/public/chat",
                    json={"message": "How much is Trust Brief?", "session_id": "test"},
                )
        assert response.status_code == 200
        assert "10,000" in response.json()["reply"]

    asyncio.run(run())


def test_ecosystem_health_includes_intake() -> None:
    async def run() -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/ecosystem/health")
        assert response.status_code == 200
        assert "intake_api" in response.json()

    asyncio.run(run())


def test_public_chat_rejects_empty_message() -> None:
    async def run() -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/public/chat", json={"message": "   "})
        assert response.status_code == 400

    asyncio.run(run())
