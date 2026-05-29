"""Telegram Bot API client — token server-side only."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.parse
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


def send_message(
    *,
    token: str,
    chat_id: int | str,
    text: str,
    parse_mode: str | None = None,
    timeout_seconds: float = 30.0,
) -> dict[str, Any]:
    if not token.strip():
        raise TelegramConfigurationError("TELEGRAM_BOT_TOKEN is not configured.")
    body: dict[str, Any] = {"chat_id": chat_id, "text": text[:4096]}
    if parse_mode:
        body["parse_mode"] = parse_mode
    payload = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        _api_url(token, "sendMessage"),
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        logger.warning("telegram_send_error status=%s %s", exc.code, detail)
        raise TelegramAPIError(f"Telegram sendMessage failed ({exc.code})") from exc
    except urllib.error.URLError as exc:
        raise TelegramAPIError("Unable to reach Telegram API") from exc
    if not data.get("ok"):
        raise TelegramAPIError(str(data.get("description", "Telegram API error")))
    return data


def set_webhook(
    *,
    token: str,
    webhook_url: str,
    secret_token: str | None = None,
    timeout_seconds: float = 30.0,
) -> dict[str, Any]:
    if not token.strip():
        raise TelegramConfigurationError("TELEGRAM_BOT_TOKEN is not configured.")
    body: dict[str, Any] = {"url": webhook_url, "allowed_updates": ["message"]}
    if secret_token:
        body["secret_token"] = secret_token
    payload = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        _api_url(token, "setWebhook"),
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        logger.warning("telegram_webhook_error status=%s %s", exc.code, detail)
        raise TelegramAPIError(f"Telegram setWebhook failed ({exc.code})") from exc
    if not data.get("ok"):
        raise TelegramAPIError(str(data.get("description", "setWebhook failed")))
    return data


def get_webhook_info(*, token: str) -> dict[str, Any]:
    request = urllib.request.Request(_api_url(token, "getWebhookInfo"), method="GET")
    with urllib.request.urlopen(request, timeout=15.0) as response:
        return json.loads(response.read().decode("utf-8"))
