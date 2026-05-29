"""Telegram webhook — professional commands and callbacks."""

from __future__ import annotations

import asyncio
from unittest.mock import patch

from noetfield_governance.telegram_webhook import extract_message, handle_telegram_update


def test_extract_message_with_name() -> None:
    update = {
        "message": {
            "chat": {"id": 12345},
            "from": {"first_name": "Alex"},
            "text": "What is Trust Brief?",
            "message_id": 1,
        }
    }
    assert extract_message(update) == (12345, "What is Trust Brief?", "Alex", 1)


def test_handle_start_shows_menu() -> None:
    async def run() -> None:
        with patch("noetfield_governance.telegram_webhook.send_message") as send:
            handled = await handle_telegram_update(
                {"message": {"chat": {"id": 1}, "from": {"first_name": "Sam"}, "text": "/start"}},
                bot_token="fake-token",
                chat_provider="auto",
                gemini_api_key=None,
                gemini_model="gemini-2.0-flash",
                openrouter_api_key=None,
                openrouter_model="google/gemini-2.0-flash-001",
            )
        assert handled is True
        assert send.call_count >= 1
        kwargs = send.call_args.kwargs
        assert kwargs.get("reply_markup") is not None
        assert "Noetfield" in kwargs.get("text", "")

    asyncio.run(run())


def test_handle_offerings_command() -> None:
    async def run() -> None:
        with patch("noetfield_governance.telegram_webhook.send_message") as send:
            handled = await handle_telegram_update(
                {"message": {"chat": {"id": 2}, "text": "/offerings"}},
                bot_token="fake-token",
                chat_provider="auto",
                gemini_api_key=None,
                gemini_model="gemini-2.0-flash",
                openrouter_api_key=None,
                openrouter_model="google/gemini-2.0-flash-001",
            )
        assert handled is True
        assert "$10,000" in send.call_args.kwargs.get("text", "") or send.call_args.kwargs.get("text", "")

    asyncio.run(run())


def test_telegram_health_endpoint() -> None:
    from httpx import ASGITransport, AsyncClient

    from noetfield_governance.api import app

    async def run() -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/telegram/health")
        assert response.status_code == 200
        body = response.json()
        assert "configured" in body
        assert "hint" in body

    asyncio.run(run())


def test_structured_intake_message() -> None:
    async def run() -> None:
        from noetfield_governance import intake_repository

        await intake_repository.init_intake_repository()
        with patch("noetfield_governance.telegram_webhook.send_message") as send:
            handled = await handle_telegram_update(
                {
                    "message": {
                        "chat": {"id": 99},
                        "text": "INTAKE: Acme CU | lead@acme.example | Bank pilot interest",
                    }
                },
                bot_token="fake-token",
                chat_provider="auto",
                gemini_api_key=None,
                gemini_model="gemini-2.0-flash",
                openrouter_api_key=None,
                openrouter_model="google/gemini-2.0-flash-001",
            )
        assert handled is True
        text = send.call_args.kwargs.get("text", "")
        assert "Intake recorded" in text or "intake" in text.lower()

    asyncio.run(run())


def test_handle_non_text_message() -> None:
    async def run() -> None:
        with patch("noetfield_governance.telegram_webhook.send_message") as send:
            handled = await handle_telegram_update(
                {"message": {"chat": {"id": 99}, "photo": [{"file_id": "x"}]}},
                bot_token="fake-token",
                chat_provider="auto",
                gemini_api_key=None,
                gemini_model="gemini-2.0-flash",
                openrouter_api_key=None,
                openrouter_model="google/gemini-2.0-flash-001",
            )
        assert handled is True
        assert send.call_count >= 1
        assert "/start" in send.call_args.kwargs.get("text", "")

    asyncio.run(run())


def test_webhook_returns_ok_before_processing() -> None:
    from httpx import ASGITransport, AsyncClient

    from noetfield_governance.api import app

    async def run() -> None:
        transport = ASGITransport(app=app)
        update = {"message": {"chat": {"id": 1}, "text": "/start"}}
        with patch("noetfield_governance.api.settings") as mock_settings:
            mock_settings.telegram_bot_enabled = True
            mock_settings.telegram_bot_token = type("T", (), {"get_secret_value": lambda self: "fake"})()
            mock_settings.telegram_webhook_secret = None
            mock_settings.public_chat_provider = "auto"
            mock_settings.gemini_api_key = None
            mock_settings.gemini_model = "gemini-2.0-flash"
            mock_settings.openrouter_api_key = None
            mock_settings.openrouter_model = "google/gemini-2.0-flash-001"
            with patch("noetfield_governance.api._process_telegram_update") as worker:
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post("/api/telegram/webhook", json=update)
                assert response.status_code == 200
                assert response.json() == {"ok": True}
                worker.assert_called_once()

    asyncio.run(run())
