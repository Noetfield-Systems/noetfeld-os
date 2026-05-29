"""Professional Telegram bot — commands, menus, typing, session memory."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from noetfield_config import CANONICAL_INTAKE_EMAIL
from noetfield_governance.chat_errors import ChatAPIError, ChatConfigurationError
from noetfield_governance.public_chat import ChatProvider, answer_public_question
from noetfield_governance.public_intake import submit_intake
from noetfield_governance.telegram_client import TelegramAPIError, send_chat_action, send_message
from noetfield_governance.telegram_commands import (
    BOT_COMMANDS,
    after_reply_keyboard,
    human_message,
    intake_message,
    main_menu_keyboard,
    offerings_message,
    trustbrief_message,
    welcome_message,
)
from noetfield_governance.telegram_format import escape_html, split_telegram_chunks
from noetfield_governance.telegram_session import (
    append_turn_async,
    clear_session_async,
    format_history_for_prompt,
    get_history_async,
)

logger = logging.getLogger("noetfield.governance.telegram.webhook")

_COPILOT_MSG = (
    "<b>Copilot Governance Pack</b>\n"
    "Enterprise AI compliance and policy validation for Microsoft 365 Copilot.\n\n"
    "Rollout gating, policy alignment, and defensible compliance logging.\n\n"
    '<a href="https://www.noetfield.com/copilot/">Learn more</a> · '
    '<a href="https://www.noetfield.com/trust-brief/intake/">Request Brief</a>'
)

_BANK_PILOT_MSG = (
    "<b>Bank Pilot</b>\n"
    "Read-only governance simulation in shadow mode.\n"
    "No execution rights · compliance evaluation only.\n\n"
    '<a href="https://www.noetfield.com/enterprise/">Enterprise</a> · '
    '<a href="https://www.noetfield.com/console/">Governance Console</a>'
)

_HELP_MSG = (
    "<b>Noetfield assistant</b>\n\n"
    "Institutional Q&amp;A grounded in public product information.\n\n"
    "<b>Commands</b>\n"
    "/offerings · /trustbrief · /copilot · /pilot\n"
    "/intake · /human · /reset\n"
    "Structured lead: <code>INTAKE: Org | email@example.com | message</code>\n\n"
    "Type a question or use the menu below."
)


def _session_key(chat_id: int) -> str:
    return f"telegram:{chat_id}"


def extract_chat_id(update: dict[str, Any]) -> int | None:
    """Best-effort chat id for fallback replies when an update cannot be handled normally."""
    message = update.get("message") or update.get("edited_message")
    if isinstance(message, dict):
        chat = message.get("chat")
        if isinstance(chat, dict) and chat.get("id") is not None:
            return int(chat["id"])
    cb = update.get("callback_query")
    if isinstance(cb, dict):
        msg = cb.get("message")
        if isinstance(msg, dict):
            chat = msg.get("chat")
            if isinstance(chat, dict) and chat.get("id") is not None:
                return int(chat["id"])
    return None


def extract_message(update: dict[str, Any]) -> tuple[int, str, str | None, int | None] | None:
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
    from_user = message.get("from") if isinstance(message.get("from"), dict) else {}
    first_name = from_user.get("first_name") if isinstance(from_user.get("first_name"), str) else None
    message_id = message.get("message_id")
    return int(chat_id), text.strip(), first_name, int(message_id) if message_id is not None else None


def extract_callback(update: dict[str, Any]) -> tuple[int, str, str, int] | None:
    cb = update.get("callback_query")
    if not isinstance(cb, dict):
        return None
    cb_id = cb.get("id")
    data = cb.get("data")
    message = cb.get("message")
    if not isinstance(message, dict):
        return None
    chat = message.get("chat")
    if cb_id is None or not isinstance(data, str) or not isinstance(chat, dict):
        return None
    chat_id = chat.get("id")
    message_id = message.get("message_id")
    if chat_id is None or message_id is None:
        return None
    return int(chat_id), str(cb_id), data, int(message_id)


async def _send_html_chunks(
    *,
    token: str,
    chat_id: int,
    text: str,
    reply_markup: dict | None = None,
) -> None:
    chunks = split_telegram_chunks(text)
    for i, chunk in enumerate(chunks):
        markup = reply_markup if i == len(chunks) - 1 else None
        try:
            await asyncio.to_thread(
                send_message,
                token=token,
                chat_id=chat_id,
                text=chunk,
                parse_mode="HTML",
                reply_markup=markup,
            )
        except TelegramAPIError:
            await asyncio.to_thread(
                send_message,
                token=token,
                chat_id=chat_id,
                text=chunk.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", ""),
                parse_mode=None,
                reply_markup=markup,
            )


async def _send_canned(
    *,
    token: str,
    chat_id: int,
    html: str,
    keyboard: dict | None = None,
) -> None:
    await _send_html_chunks(token=token, chat_id=chat_id, text=html, reply_markup=keyboard)


async def _send_fallback(
    *,
    token: str,
    chat_id: int,
    html: str,
) -> None:
    """Last-resort plain reply when rich HTML/keyboards fail."""
    try:
        await asyncio.to_thread(
            send_message,
            token=token,
            chat_id=chat_id,
            text=html.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", ""),
            parse_mode=None,
            reply_markup=None,
        )
    except TelegramAPIError as exc:
        logger.error("telegram_fallback_failed chat_id=%s %s", chat_id, exc)


async def _handle_command(
    command: str,
    *,
    token: str,
    chat_id: int,
    first_name: str | None,
) -> bool:
    cmd = command.split()[0].split("@")[0].lower()
    if cmd in ("/start", "/help"):
        text = welcome_message(first_name) if cmd == "/start" else _HELP_MSG
        await _send_canned(token=token, chat_id=chat_id, html=text, keyboard=main_menu_keyboard())
        return True
    if cmd == "/offerings":
        await _send_canned(token=token, chat_id=chat_id, html=offerings_message(), keyboard=main_menu_keyboard())
        return True
    if cmd == "/trustbrief":
        await _send_canned(token=token, chat_id=chat_id, html=trustbrief_message(), keyboard=after_reply_keyboard())
        return True
    if cmd == "/copilot":
        await _send_canned(token=token, chat_id=chat_id, html=_COPILOT_MSG, keyboard=after_reply_keyboard())
        return True
    if cmd == "/pilot":
        await _send_canned(token=token, chat_id=chat_id, html=_BANK_PILOT_MSG, keyboard=after_reply_keyboard())
        return True
    if cmd == "/intake":
        await _send_canned(token=token, chat_id=chat_id, html=intake_message(), keyboard=after_reply_keyboard())
        return True
    if cmd == "/human":
        await _send_canned(token=token, chat_id=chat_id, html=human_message(), keyboard=after_reply_keyboard())
        return True
    if cmd == "/reset":
        await clear_session_async(_session_key(chat_id))
        await _send_canned(
            token=token,
            chat_id=chat_id,
            html="Conversation context cleared. How can I help you?",
            keyboard=main_menu_keyboard(),
        )
        return True
    return False


async def _handle_menu_callback(
    data: str,
    *,
    token: str,
    chat_id: int,
) -> str | None:
    if not data.startswith("menu:"):
        return None
    key = data.split(":", 1)[1]
    mapping = {
        "offerings": offerings_message(),
        "trustbrief": trustbrief_message(),
        "copilot": _COPILOT_MSG,
        "bankpilot": _BANK_PILOT_MSG,
        "human": human_message(),
    }
    html = mapping.get(key)
    if html:
        await _send_canned(token=token, chat_id=chat_id, html=html, keyboard=after_reply_keyboard())
    return "ok"


async def _try_structured_intake(text: str, *, token: str, chat_id: int) -> bool:
    """NF-ENG-17: INTAKE: Org | email | message → POST /api/intake pipeline."""
    raw = text.strip()
    if not raw.upper().startswith("INTAKE:"):
        return False
    rest = raw.split(":", 1)[1].strip()
    parts = [p.strip() for p in rest.split("|")]
    if len(parts) < 3:
        await _send_canned(
            token=token,
            chat_id=chat_id,
            html=(
                "Use: <code>INTAKE: Organization | email@example.com | Your message</code>\n\n"
                f'Or use <a href="https://www.noetfield.com/trust-brief/intake/">web intake</a>.'
            ),
            keyboard=after_reply_keyboard(),
        )
        return True
    org, email, message = parts[0], parts[1], "|".join(parts[2:]).strip()
    try:
        rec = await submit_intake(
            organization=org,
            contact_email=email,
            message=message,
            request_id=None,
            contact_name=None,
            sku="general",
            vector="telegram-intake",
            source="telegram",
            client_key=f"telegram:{chat_id}:{email}",
            metadata={"chat_id": chat_id},
        )
        rid = rec.request_id or "—"
        await _send_canned(
            token=token,
            chat_id=chat_id,
            html=(
                f"<b>Intake recorded.</b> ID <code>{escape_html(rec.intake_id)}</code>\n"
                f"Request ID: <code>{escape_html(rid)}</code>\n"
                f"Ops: {CANONICAL_INTAKE_EMAIL}"
            ),
            keyboard=after_reply_keyboard(),
        )
    except ValueError as exc:
        await _send_canned(
            token=token,
            chat_id=chat_id,
            html=f"Intake invalid: {escape_html(str(exc))}",
            keyboard=after_reply_keyboard(),
        )
    except PermissionError:
        await _send_canned(
            token=token,
            chat_id=chat_id,
            html="Too many intake submissions. Try again in a minute.",
        )
    return True


async def _answer_with_llm(
    *,
    token: str,
    chat_id: int,
    text: str,
    chat_provider: ChatProvider,
    gemini_api_key: str | None,
    gemini_model: str,
    openrouter_api_key: str | None,
    openrouter_model: str,
) -> None:
    session = _session_key(chat_id)
    history = await get_history_async(session)
    prompt = format_history_for_prompt(history, text)

    await asyncio.to_thread(send_chat_action, token=token, chat_id=chat_id, action="typing")

    reply, _provider = await answer_public_question(
        message=prompt,
        provider=chat_provider,
        gemini_api_key=gemini_api_key,
        gemini_model=gemini_model,
        openrouter_api_key=openrouter_api_key,
        openrouter_model=openrouter_model,
        client_key=session,
    )

    await append_turn_async(session, "user", text)
    await append_turn_async(session, "assistant", reply)

    body = escape_html(reply)
    body += f"\n\n<i>Noetfield · Governance assistant</i>"
    await _send_html_chunks(
        token=token,
        chat_id=chat_id,
        text=body,
        reply_markup=after_reply_keyboard(),
    )


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
    """Return True if the update was handled."""
    callback = extract_callback(update)
    if callback is not None:
        chat_id, cb_id, data, _msg_id = callback
        from noetfield_governance.telegram_client import answer_callback_query

        try:
            await asyncio.to_thread(
                answer_callback_query,
                token=bot_token,
                callback_query_id=cb_id,
                text="Opening…",
            )
            await _handle_menu_callback(data, token=bot_token, chat_id=chat_id)
            return True
        except TelegramAPIError as exc:
            logger.warning("callback_failed %s", exc)
            await _send_fallback(
                token=bot_token,
                chat_id=chat_id,
                html="Menu action failed. Try /start or type your question.",
            )
            return True

    parsed = extract_message(update)
    if parsed is None:
        return await handle_unrecognized_update(update, bot_token=bot_token)
    chat_id, text, first_name, _ = parsed

    if await _try_structured_intake(text, token=bot_token, chat_id=chat_id):
        return True

    if text.startswith("/"):
        try:
            return await _handle_command(text, token=bot_token, chat_id=chat_id, first_name=first_name)
        except TelegramAPIError as exc:
            logger.warning("command_failed chat_id=%s %s", chat_id, exc)
            await _send_fallback(
                token=bot_token,
                chat_id=chat_id,
                html=f"Sorry — I could not send a reply. Try /start or email {CANONICAL_INTAKE_EMAIL}.",
            )
            return True

    try:
        await _answer_with_llm(
            token=bot_token,
            chat_id=chat_id,
            text=text,
            chat_provider=chat_provider,
            gemini_api_key=gemini_api_key,
            gemini_model=gemini_model,
            openrouter_api_key=openrouter_api_key,
            openrouter_model=openrouter_model,
        )
        return True
    except ValueError as exc:
        await _send_canned(token=bot_token, chat_id=chat_id, html=f"Invalid message: {escape_html(str(exc))}")
        return True
    except PermissionError:
        await _send_canned(
            token=bot_token,
            chat_id=chat_id,
            html="Too many messages. Please wait a minute and try again.",
        )
        return True
    except ChatConfigurationError:
        await _send_canned(
            token=bot_token,
            chat_id=chat_id,
            html=(
                "Assistant is not configured on the server. "
                f"Email {CANONICAL_INTAKE_EMAIL} or visit "
                '<a href="https://www.noetfield.com/trust-brief/intake/">intake</a>.'
            ),
        )
        return True
    except ChatAPIError:
        await _send_canned(
            token=bot_token,
            chat_id=chat_id,
            html=(
                "Assistant temporarily unavailable. Please try again or email "
                f"{CANONICAL_INTAKE_EMAIL}."
            ),
        )
        return True
    except TelegramAPIError as exc:
        logger.warning("telegram_reply_failed chat_id=%s %s", chat_id, exc)
        await _send_fallback(
            token=bot_token,
            chat_id=chat_id,
            html=f"Sorry — delivery failed. Try /start or email {CANONICAL_INTAKE_EMAIL}.",
        )
        return True


async def handle_unrecognized_update(
    update: dict[str, Any],
    *,
    bot_token: str,
) -> bool:
    """Reply when Telegram sends a non-text message or unknown update shape."""
    chat_id = extract_chat_id(update)
    if chat_id is None:
        logger.info("telegram_update_unhandled keys=%s", sorted(update.keys()))
        return False
    await _send_canned(
        token=bot_token,
        chat_id=chat_id,
        html=(
            "I can read text messages and menu buttons.\n\n"
            "Send /start for the menu, or type your question in plain language."
        ),
        keyboard=main_menu_keyboard(),
    )
    return True
