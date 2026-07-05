"""Resend webhook — email.delivered / email.bounced → intake row by request_id."""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import logging
import re
import time
from typing import Any

logger = logging.getLogger("noetfield.governance.resend_webhook")

_RID_RE = re.compile(r"(RID-[A-Z0-9\-]{6,64})", re.IGNORECASE)
_HANDLED_TYPES = frozenset({"email.delivered", "email.bounced"})


def _secret(value: object | None) -> str:
    if value is None:
        return ""
    getter = getattr(value, "get_secret_value", None)
    if callable(getter):
        return str(getter() or "").strip()
    return str(value).strip()


def verify_svix_signature(payload: bytes, headers: dict[str, str], secret: str) -> bool:
    """Verify Resend (Svix) webhook signature."""
    if not secret:
        return False
    msg_id = (headers.get("svix-id") or headers.get("Svix-Id") or "").strip()
    msg_ts = (headers.get("svix-timestamp") or headers.get("Svix-Timestamp") or "").strip()
    msg_sig = (headers.get("svix-signature") or headers.get("Svix-Signature") or "").strip()
    if not msg_id or not msg_ts or not msg_sig:
        return False
    try:
        ts_int = int(msg_ts)
    except ValueError:
        return False
    if abs(time.time() - ts_int) > 300:
        return False

    key_part = secret[6:] if secret.startswith("whsec_") else secret
    try:
        secret_bytes = base64.b64decode(key_part)
    except (ValueError, binascii.Error):
        return False

    signed = f"{msg_id}.{msg_ts}.".encode() + payload
    digest = hmac.new(secret_bytes, signed, hashlib.sha256).digest()
    expected = base64.b64encode(digest).decode("utf-8")

    for part in msg_sig.split():
        if part.startswith("v1,") and hmac.compare_digest(part[3:], expected):
            return True
    return False


def _tag_value(tags: object, name: str) -> str | None:
    if isinstance(tags, dict):
        raw = tags.get(name)
        return str(raw).strip().upper() if raw else None
    if isinstance(tags, list):
        for item in tags:
            if not isinstance(item, dict):
                continue
            if str(item.get("name") or "").lower() == name.lower():
                val = str(item.get("value") or "").strip()
                return val.upper() if val else None
    return None


def extract_request_id(event: dict[str, Any]) -> str | None:
    data = event.get("data")
    if not isinstance(data, dict):
        return None

    rid = _tag_value(data.get("tags"), "request_id")
    if rid and _RID_RE.fullmatch(rid):
        return rid

    subject = str(data.get("subject") or "")
    match = _RID_RE.search(subject)
    if match:
        return match.group(1).upper()

    return None


def parse_delivery_event(event: dict[str, Any]) -> dict[str, str] | None:
    event_type = str(event.get("type") or "")
    if event_type not in _HANDLED_TYPES:
        return None

    request_id = extract_request_id(event)
    if not request_id:
        return None

    status = "delivered" if event_type == "email.delivered" else "bounced"
    detail = ""
    if status == "bounced":
        data = event.get("data") if isinstance(event.get("data"), dict) else {}
        bounce = data.get("bounce") if isinstance(data.get("bounce"), dict) else {}
        detail = str(bounce.get("message") or bounce.get("type") or data.get("error") or "").strip()

    return {
        "request_id": request_id,
        "status": status,
        "detail": detail[:500],
        "event_type": event_type,
    }


async def handle_resend_webhook(
    settings: object,
    payload: bytes,
    headers: dict[str, str],
) -> dict[str, object]:
    secret = _secret(getattr(settings, "resend_webhook_secret", None))
    if not secret:
        return {"ok": False, "error": "resend_webhook_not_configured"}

    if not verify_svix_signature(payload, headers, secret):
        return {"ok": False, "error": "invalid_signature"}

    try:
        event = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {"ok": False, "error": "invalid_payload"}

    parsed = parse_delivery_event(event)
    if not parsed:
        return {"ok": True, "handled": False, "type": event.get("type")}

    from noetfield_governance import intake_repository

    updated = await intake_repository.update_email_archive_status(
        request_id=parsed["request_id"],
        status=parsed["status"],
        detail=parsed["detail"] or None,
    )
    if not updated:
        logger.warning(
            "resend_webhook_no_intake request_id=%s type=%s",
            parsed["request_id"],
            parsed["event_type"],
        )
        return {
            "ok": True,
            "handled": False,
            "reason": "intake_not_found",
            "request_id": parsed["request_id"],
        }

    logger.info(
        "resend_webhook_intake_updated request_id=%s status=%s intake_id=%s",
        parsed["request_id"],
        parsed["status"],
        updated.get("intake_id"),
    )
    return {
        "ok": True,
        "handled": True,
        "request_id": parsed["request_id"],
        "status": parsed["status"],
        "intake_id": updated.get("intake_id"),
    }
