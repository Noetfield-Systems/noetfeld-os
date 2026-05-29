"""Process Telegram updates through the same grounded chat pipeline as the website."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from noetfield_config import CANONICAL_INTAKE_EMAIL
from noetfield_governance.chat_errors import ChatAPIError, ChatConfigurationError
from noetfield_governance.public_chat import ChatProvider, answer_public_question
from noetfield_governance.telegram_client import (
    TelegramAPIError,
    TelegramConfigurationError,
    send_message,
)

logger = logging.getLogger("noetfield.governance.telegram.webhook")

_WELCOME = (
    "Noetfield assistant — governance offerings, Trust Brief ($10,000), "
    "Copilot Governance Pack, and Bank Pilot (read-only simulation).\n\n"
    "Ask a question in plain language.\n"
    f"For engagements: {CANONICAL_INTAKE_EMAIL} or https://www.noetfield.com/trust-brief/intake/"
)


def extract_message(update: dict[str, Any]) -> tuple[int, str] | None:
    message = update.get("message") or update.get("edited_message")
    if not isinstance(message, dict):
        return None
    chat = message.get("chat")
    if not isinstance(chat, dict):
        return None
    chat_id = chat.get("id")
    text = message.get("text")
    if chat_id is None or not isinstance(text, str) or not text.strip():
        return None
    return int(chat_id), text.strip()


async def handle_telegram_update(
    update: dict[str, Any],
    *,
    bot_token: str,
    chat_provider: ChatProvider,
    gemini_api_key: str | None,
    gemini_model: str,
    openrouter_api_key: str | None,
    openrouter_model: str,
) -> bool:
    """Return True if a reply was sent."""
    parsed = extract_message(update)
    if parsed is None:
        return False
    chat_id, text = parsed

    if text.startswith("/start"):
        await asyncio.to_thread(
            send_message,
            token=bot_token,
            chat_id=chat_id,
            text=_WELCOME,
        )
        return True

    if text.startswith("/help"):
        await asyncio.to_thread(
            send_message,
            token=bot_token,
            chat_id=chat_id,
            text=_WELCOME,
        )
        return True

    client_key = f"telegram:{chat_id}"
    try:
        reply, provider = await answer_public_question(
            message=text,
            provider=chat_provider,
            gemini_api_key=gemini_api_key,
            gemini_model=gemini_model,
            openrouter_api_key=openrouter_api_key,
            openrouter_model=openrouter_model,
            client_key=client_key,
        )
        footer = f"\n\n— Noetfield ({provider})"
        if len(reply) + len(footer) > 4090:
            reply = reply[: 4090 - len(footer)] + "…"
        await asyncio.to_thread(
            send_message,
            token=bot_token,
            chat_id=chat_id,
            text=reply + footer,
        )
        return True
    except ValueError as exc:
        await asyncio.to_thread(
            send_message, token=bot_token, chat_id=chat_id, text=f"Invalid message: {exc}"
        )
        return True
    except PermissionError:
        await asyncio.to_thread(
            send_message,
            token=bot_token,
            chat_id=chat_id,
            text="Too many messages. Please wait a minute and try again.",
        )
        return True
    except ChatConfigurationError:
        await asyncio.to_thread(
            send_message,
            token=bot_token,
            chat_id=chat_id,
            text=(
                "Assistant is not configured on the server. "
                f"Email {CANONICAL_INTAKE_EMAIL} or visit https://www.noetfield.com/trust-brief/intake/"
            ),
        )
        return True
    except ChatAPIError:
        await asyncio.to_thread(
            send_message,
            token=bot_token,
            chat_id=chat_id,
            text=(
                "Assistant temporarily unavailable. Please try again later or email "
                f"{CANONICAL_INTAKE_EMAIL}."
            ),
        )
        return True
    except TelegramAPIError as exc:
        logger.warning("telegram_reply_failed chat_id=%s %s", chat_id, exc)
        return False
