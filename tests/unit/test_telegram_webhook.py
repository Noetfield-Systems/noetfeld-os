"""Telegram webhook handling — no real Bot API calls."""

from __future__ import annotations

import asyncio
from unittest.mock import patch

from noetfield_governance.telegram_webhook import extract_message, handle_telegram_update


def test_extract_message_text() -> None:
    update = {
        "message": {
            "chat": {"id": 12345},
            "text": "What is Trust Brief?",
        }
    }
    assert extract_message(update) == (12345, "What is Trust Brief?")


def test_handle_start_sends_welcome() -> None:
    async def run() -> None:
        with patch("noetfield_governance.telegram_webhook.send_message") as send:
            handled = await handle_telegram_update(
                {"message": {"chat": {"id": 1}, "text": "/start"}},
                bot_token="fake-token",
                chat_provider="auto",
                gemini_api_key=None,
                gemini_model="gemini-2.0-flash",
                openrouter_api_key=None,
                openrouter_model="google/gemini-2.0-flash-001",
            )
        assert handled is True
        send.assert_called_once()
        assert "Trust Brief" in send.call_args.kwargs["text"]

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
