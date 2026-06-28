"""Public chat API — no real Gemini calls in unit tests."""

from __future__ import annotations

import asyncio
import json
from unittest.mock import patch

from httpx import ASGITransport, AsyncClient

from noetfield_governance import api as governance_api
from noetfield_governance.api import app
from noetfield_governance.chatbot_knowledge import build_knowledge_context
from noetfield_governance.public_chat import resolve_chat_provider
from noetfield_governance.public_chat_telemetry import PublicChatTelemetrySettings


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


def test_public_chat_writes_telemetry(tmp_path) -> None:
    async def run() -> None:
        original = governance_api.chat_telemetry_settings
        governance_api.chat_telemetry_settings = PublicChatTelemetrySettings(
            enabled=True,
            path=str(tmp_path / "public-chat.jsonl"),
            max_chars=4000,
        )
        try:
            with patch(
                "noetfield_governance.api.answer_public_question",
                return_value=("Trust Brief is $10,000 for six weeks.", "openrouter", ["OFFERINGS_LOCKED.md"]),
            ):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post(
                        "/api/public/chat",
                        json={"message": "How much is Trust Brief?", "session_id": "session-1"},
                    )
            assert response.status_code == 200
            events = [
                json.loads(line)
                for line in (tmp_path / "public-chat.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            assert len(events) == 1
            assert events[0]["status"] == "ok"
            assert events[0]["provider"] == "openrouter"
            assert events[0]["message"] == "How much is Trust Brief?"
            assert "10,000" in events[0]["reply"]
            assert events[0]["session_hash"] != "session-1"
            assert events[0]["intent"]["primary_intent"] == "pricing"
            assert events[0]["conversation_state"]["turn_index"] == 1
            assert events[0]["decision_path"][1]["step"] == "intent_classified"
            assert events[0]["alignment"]["primary_intent"] == "pricing"
        finally:
            governance_api.chat_telemetry_settings = original

    asyncio.run(run())


def test_public_chat_telemetry_redacts_obvious_secrets(tmp_path) -> None:
    async def run() -> None:
        original = governance_api.chat_telemetry_settings
        governance_api.chat_telemetry_settings = PublicChatTelemetrySettings(
            enabled=True,
            path=str(tmp_path / "public-chat.jsonl"),
            max_chars=4000,
        )
        try:
            with patch(
                "noetfield_governance.api.answer_public_question",
                return_value=("Do not paste API keys into public chat.", "openrouter", []),
            ):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post(
                        "/api/public/chat",
                        json={
                            "message": "My token is sk-or-v1-abcdefghijklmnopqrstuvwxyz123456",
                            "session_id": "session-2",
                        },
                    )
            assert response.status_code == 200
            event = json.loads((tmp_path / "public-chat.jsonl").read_text(encoding="utf-8"))
            assert "sk-or-v1-" not in event["message"]
            assert "[REDACTED]" in event["message"]
        finally:
            governance_api.chat_telemetry_settings = original

    asyncio.run(run())


def test_public_chat_tracks_conversation_state_across_turns(tmp_path) -> None:
    async def run() -> None:
        original = governance_api.chat_telemetry_settings
        governance_api.chat_telemetry_settings = PublicChatTelemetrySettings(
            enabled=True,
            path=str(tmp_path / "public-chat.jsonl"),
            max_chars=4000,
        )
        try:
            with patch(
                "noetfield_governance.api.answer_public_question",
                return_value=("Trust Brief is $10,000 for six weeks.", "openrouter", ["OFFERINGS_LOCKED.md"]),
            ):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    first = await client.post(
                        "/api/public/chat",
                        json={"message": "How much is Trust Brief?", "session_id": "same-session"},
                    )
                    second = await client.post(
                        "/api/public/chat",
                        json={"message": "How do we engage?", "session_id": "same-session"},
                    )
            assert first.status_code == 200
            assert second.status_code == 200
            events = [
                json.loads(line)
                for line in (tmp_path / "public-chat.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            assert events[0]["conversation_state"]["turn_index"] == 1
            assert events[1]["conversation_state"]["turn_index"] == 2
            assert events[1]["conversation_state"]["recent"][0]["message"] == "How much is Trust Brief?"
        finally:
            governance_api.chat_telemetry_settings = original

    asyncio.run(run())


def test_public_chat_privacy_history_answer_is_deterministic(tmp_path) -> None:
    async def run() -> None:
        original = governance_api.chat_telemetry_settings
        governance_api.chat_telemetry_settings = PublicChatTelemetrySettings(
            enabled=True,
            path=str(tmp_path / "public-chat.jsonl"),
            max_chars=4000,
        )
        try:
            with patch("noetfield_governance.api.answer_public_question") as llm:
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post(
                        "/api/public/chat",
                        json={"message": "Do you store my chat history?", "session_id": "privacy-session"},
                    )
            assert response.status_code == 200
            body = response.json()
            assert body["provider"] == "deterministic"
            assert "may be logged" in body["reply"]
            assert "non-confidential" in body["reply"]
            llm.assert_not_called()
            event = json.loads((tmp_path / "public-chat.jsonl").read_text(encoding="utf-8"))
            assert event["intent"]["primary_intent"] == "privacy_history"
            assert event["alignment"]["aligned"] is True
            assert event["decision_path"][2]["step"] == "deterministic_policy"
        finally:
            governance_api.chat_telemetry_settings = original

    asyncio.run(run())


def test_public_chat_sme_pricing_ladder_is_deterministic(tmp_path) -> None:
    async def run() -> None:
        original = governance_api.chat_telemetry_settings
        governance_api.chat_telemetry_settings = PublicChatTelemetrySettings(
            enabled=True,
            path=str(tmp_path / "public-chat.jsonl"),
            max_chars=4000,
        )
        try:
            with patch("noetfield_governance.api.answer_public_question") as llm:
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post(
                        "/api/public/chat",
                        json={
                            "message": "We are a mortgage broker in Toronto — what do you offer and what does it cost?",
                            "session_id": "sme-pricing-session",
                        },
                    )
            assert response.status_code == 200
            body = response.json()
            assert body["provider"] == "deterministic"
            assert "Diagnostic Sprint" in body["reply"]
            assert "$2,500" in body["reply"]
            assert "Copilot Governance Pack" in body["reply"]
            assert "Trust Brief" in body["reply"]
            llm.assert_not_called()
        finally:
            governance_api.chat_telemetry_settings = original

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
