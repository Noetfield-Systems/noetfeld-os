"""Public chat API — no real Gemini calls in unit tests."""

from __future__ import annotations

import asyncio
import json
from unittest.mock import patch

from httpx import ASGITransport, AsyncClient

from noetfield_governance import api as governance_api
from noetfield_governance.api import app
from noetfield_governance.chatbot_knowledge import build_knowledge_context
from noetfield_governance.public_chat import answer_public_question, resolve_chat_provider
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


def test_public_chat_has_no_local_faq_rule_engine() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    vercel_fallback = (root / "api" / "public" / "chat" / "index.js").read_text(
        encoding="utf-8"
    )
    frontend = (root / "assets" / "noetfield-chat.js").read_text(encoding="utf-8")
    intent_helper = (
        root
        / "services"
        / "governance"
        / "noetfield_governance"
        / "public_chat_intelligence.py"
    ).read_text(encoding="utf-8")

    assert "const RULES" not in vercel_fallback
    assert "static rule script" not in vercel_fallback
    assert "I will not answer" not in vercel_fallback
    assert "deterministic_reply_for_intent" not in intent_helper
    assert "deterministic_policy" not in intent_helper
    assert "Ask naturally" not in frontend
    assert "site assistant" in frontend
    assert "move money" not in vercel_fallback
    assert "hold custody" not in vercel_fallback
    assert "isInternalSourceLeakReply" in vercel_fallback


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
            assert events[0]["intent"]["primary_intent"] == "general_product"
            assert events[0]["conversation_state"]["turn_index"] == 1
            assert events[0]["decision_path"][1]["step"] == "intent_classified"
            assert events[0]["alignment"]["primary_intent"] == "general_product"
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


def test_public_chat_resolves_follow_up_subject_from_prior_turn(tmp_path) -> None:
    async def run() -> None:
        original = governance_api.chat_telemetry_settings
        governance_api.chat_telemetry_settings = PublicChatTelemetrySettings(
            enabled=True,
            path=str(tmp_path / "public-chat.jsonl"),
            max_chars=4000,
        )
        captured: list[str] = []

        try:
            async def fake_answer(**kwargs):
                captured.append(str((kwargs.get("conversation_state") or {}).get("recent")))
                message = kwargs["message"]
                if message == "Should the Intelligence tab stay?":
                    return (
                        "If Intelligence points home, make it Home or create a real hub.",
                        "openrouter",
                        ["/"],
                    )
                return (
                    "Because Intelligence was the active subject from the previous turn.",
                    "openrouter",
                    ["/"],
                )

            with patch("noetfield_governance.api.answer_public_question", side_effect=fake_answer):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    first = await client.post(
                        "/api/public/chat",
                        json={
                            "message": "Should the Intelligence tab stay?",
                            "session_id": "subject-session",
                        },
                    )
                    second = await client.post(
                        "/api/public/chat",
                        json={"message": "why retired?", "session_id": "subject-session"},
                    )

            assert first.status_code == 200
            assert second.status_code == 200
            assert "Intelligence" in captured[-1]
            events = [
                json.loads(line)
                for line in (tmp_path / "public-chat.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            assert events[1]["conversation_state"]["recent"][0]["message"] == (
                "Should the Intelligence tab stay?"
            )
        finally:
            governance_api.chat_telemetry_settings = original

    asyncio.run(run())


def test_answer_public_question_composes_with_active_subject() -> None:
    async def run() -> None:
        captured: dict[str, str] = {}

        def fake_generate(**kwargs):
            captured["system"] = kwargs["system_instruction"]
            captured["user"] = kwargs["user_message"]
            return "It refers to the Intelligence tab from the prior turn."

        state = {
            "recent": [
                {
                    "message": "Should the Intelligence tab stay?",
                    "reply_preview": "If Intelligence just means home, rename it Home.",
                }
            ]
        }
        with patch("noetfield_governance.public_chat._generate_sync", side_effect=fake_generate):
            reply, provider, citations = await answer_public_question(
                message="why retired?",
                provider="openrouter",
                gemini_api_key=None,
                gemini_model="gemini-2.0-flash",
                openrouter_api_key="or-key",
                openrouter_model="google/gemini-2.5-flash",
                client_key="active-subject-test",
                conversation_state=state,
            )

        assert provider == "openrouter"
        assert "Intelligence tab" in reply
        assert "Active subject: Intelligence" in captured["system"]
        assert "Resolved retrieval query: Intelligence: why retired?" in captured["user"]
        assert citations

    asyncio.run(run())


def test_public_chat_privacy_history_uses_model_path(tmp_path) -> None:
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
                return_value=(
                    "Use the public assistant for non-confidential questions. For sensitive context, use /trust-brief/intake/.",
                    "openrouter",
                    ["/privacy/", "/trust-brief/intake/"],
                ),
            ) as llm:
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post(
                        "/api/public/chat",
                        json={"message": "Do you store my chat history?", "session_id": "privacy-session"},
                    )
            assert response.status_code == 200
            body = response.json()
            assert body["provider"] == "openrouter"
            assert "non-confidential" in body["reply"]
            llm.assert_called_once()
            event = json.loads((tmp_path / "public-chat.jsonl").read_text(encoding="utf-8"))
            assert event["intent"]["primary_intent"] == "privacy_history"
            assert event["alignment"]["aligned"] is True
            assert event["decision_path"][2]["step"] == "knowledge_retrieval"
        finally:
            governance_api.chat_telemetry_settings = original

    asyncio.run(run())


def test_public_chat_sme_pricing_ladder_uses_model_path(tmp_path) -> None:
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
                return_value=(
                    "For a Toronto mortgage broker, start with Diagnostic Sprint from $2,500. If the work moves into Copilot governance, compare Copilot Governance Pack ($2k-$10k) and Trust Brief ($10,000). See /pricing/.",
                    "openrouter",
                    ["knowledge/intelligence-lane.md", "knowledge/pricing-matrix.md", "/pricing/"],
                ),
            ) as llm:
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
            assert body["provider"] == "openrouter"
            assert "Diagnostic Sprint" in body["reply"]
            assert "$2,500" in body["reply"]
            assert "Copilot Governance Pack" in body["reply"]
            assert "Trust Brief" in body["reply"]
            llm.assert_called_once()
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


def test_greeting_short_circuits_without_llm() -> None:
    async def run() -> None:
        with patch("noetfield_governance.public_chat._generate_sync") as generate:
            reply, provider, citations = await answer_public_question(
                message="HI",
                provider="auto",
                gemini_api_key="gemini-key",
                openrouter_api_key="or-key",
                gemini_model="gemini-2.0-flash",
                openrouter_model="google/gemini-2.5-flash",
                client_key="test-client",
            )
            generate.assert_not_called()
        assert provider == "greeting"
        assert "Noetfield" in reply
        assert "Stablecoin" not in reply
        assert "ask naturally" not in reply.lower()
        assert citations == ["/pricing/", "/gel/", "/copilot/pilot/"]

    asyncio.run(run())
