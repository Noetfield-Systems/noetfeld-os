"""Telegram Bot API client — token server-side only."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any

logger = logging.getLogger("noetfield.governance.telegram")

TELEGRAM_API = "https://api.telegram.org"


class TelegramConfigurationError(RuntimeError):
    """Bot token missing or invalid configuration."""


class TelegramAPIError(RuntimeError):
    """Telegram API request failed."""


def _api_url(token: str, method: str) -> str:
    return f"{TELEGRAM_API}/bot{token}/{method}"


def _post(token: str, method: str, body: dict[str, Any], *, timeout: float = 30.0) -> dict[str, Any]:
    if not token.strip():
        raise TelegramConfigurationError("TELEGRAM_BOT_TOKEN is not configured.")
    payload = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        _api_url(token, method),
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        logger.warning("telegram_%s_error status=%s %s", method, exc.code, detail)
        raise TelegramAPIError(f"Telegram {method} failed ({exc.code})") from exc
    except urllib.error.URLError as exc:
        raise TelegramAPIError("Unable to reach Telegram API") from exc
    if not data.get("ok"):
        raise TelegramAPIError(str(data.get("description", "Telegram API error")))
    return data


def send_chat_action(*, token: str, chat_id: int | str, action: str = "typing") -> None:
    _post(token, "sendChatAction", {"chat_id": chat_id, "action": action}, timeout=10.0)


def send_message(
    *,
    token: str,
    chat_id: int | str,
    text: str,
    parse_mode: str | None = "HTML",
    reply_markup: dict[str, Any] | None = None,
    disable_web_page_preview: bool = True,
    timeout_seconds: float = 30.0,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "chat_id": chat_id,
        "text": text[:4096],
        "disable_web_page_preview": disable_web_page_preview,
    }
    if parse_mode:
        body["parse_mode"] = parse_mode
    if reply_markup:
        body["reply_markup"] = reply_markup
    return _post(token, "sendMessage", body, timeout=timeout_seconds)


def answer_callback_query(
    *,
    token: str,
    callback_query_id: str,
    text: str | None = None,
    show_alert: bool = False,
) -> dict[str, Any]:
    body: dict[str, Any] = {"callback_query_id": callback_query_id}
    if text:
        body["text"] = text[:200]
    body["show_alert"] = show_alert
    return _post(token, "answerCallbackQuery", body, timeout=10.0)


def set_webhook(
    *,
    token: str,
    webhook_url: str,
    secret_token: str | None = None,
    timeout_seconds: float = 30.0,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "url": webhook_url,
        "allowed_updates": ["message", "callback_query"],
        "drop_pending_updates": False,
    }
    if secret_token:
        body["secret_token"] = secret_token
    return _post(token, "setWebhook", body, timeout=timeout_seconds)


def set_my_commands(*, token: str, commands: list[dict[str, str]]) -> dict[str, Any]:
    return _post(token, "setMyCommands", {"commands": commands}, timeout=15.0)


def get_webhook_info(*, token: str) -> dict[str, Any]:
    request = urllib.request.Request(_api_url(token, "getWebhookInfo"), method="GET")
    with urllib.request.urlopen(request, timeout=15.0) as response:
        return json.loads(response.read().decode("utf-8"))
