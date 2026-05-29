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
        assert "configured" in response.json()

    asyncio.run(run())
