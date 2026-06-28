"""First-party telemetry for public chatbot behavior analysis.

The public assistant needs durable operator visibility: what users asked, what
the bot replied, which provider handled it, and where failures happened. This
module writes JSONL locally by default and can be pointed at a durable mounted
path in production. It hashes client/session identifiers and redacts obvious
API-key/token patterns before storing free text.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


_SECRET_PATTERNS = (
    re.compile(r"\b(sk-or-v1-[A-Za-z0-9_-]{12,})\b"),
    re.compile(r"\b(sk-[A-Za-z0-9_-]{12,})\b"),
    re.compile(r"\b(AIza[0-9A-Za-z_-]{16,})\b"),
    re.compile(r"\b(Bearer\s+)[A-Za-z0-9._-]{12,}\b", re.I),
    re.compile(r"\b(api[_-]?key|token|secret|password)\s*[:=]\s*\S+", re.I),
)


@dataclass(frozen=True)
class PublicChatTelemetrySettings:
    enabled: bool
    path: str
    max_chars: int = 4000


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def monotonic_ms() -> int:
    return int(time.monotonic() * 1000)


def hash_identifier(value: str | None) -> str:
    normalized = (value or "anonymous").strip() or "anonymous"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:24]


def redact_text(value: str | None, *, max_chars: int) -> str:
    text = (value or "").strip()
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    if len(text) > max_chars:
        return text[: max_chars - 15].rstrip() + " ...[truncated]"
    return text


def resolve_telemetry_path(path: str) -> Path:
    target = Path(path).expanduser()
    if not target.is_absolute():
        target = Path(__file__).resolve().parents[3] / target
    return target


def record_public_chat_event(
    *,
    settings: PublicChatTelemetrySettings,
    event: dict[str, Any],
) -> None:
    """Append one telemetry event. Best-effort: never break public chat."""

    if not settings.enabled:
        return
    try:
        target = resolve_telemetry_path(settings.path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=True, sort_keys=True) + "\n")
    except Exception:
        # Public chat must not fail because telemetry storage is unavailable.
        return


def build_public_chat_event(
    *,
    status: str,
    message: str,
    reply: str | None,
    provider: str | None,
    citations: list[str] | None,
    client_key: str,
    session_id: str | None,
    user_agent: str | None,
    duration_ms: int,
    settings: PublicChatTelemetrySettings,
    conversation_state: dict[str, Any] | None = None,
    intent: dict[str, Any] | None = None,
    decision_path: list[dict[str, Any]] | None = None,
    alignment: dict[str, Any] | None = None,
    error_type: str | None = None,
    error_detail: str | None = None,
) -> dict[str, Any]:
    return {
        "event_type": "public_chat_turn",
        "created_at": utc_now(),
        "status": status,
        "provider": provider,
        "citations": citations or [],
        "client_hash": hash_identifier(client_key),
        "session_hash": hash_identifier(session_id),
        "user_agent_hash": hash_identifier(user_agent),
        "message": redact_text(message, max_chars=settings.max_chars),
        "reply": redact_text(reply, max_chars=settings.max_chars),
        "message_chars": len(message or ""),
        "reply_chars": len(reply or ""),
        "duration_ms": duration_ms,
        "conversation_state": conversation_state or {},
        "intent": intent or {},
        "decision_path": decision_path or [],
        "alignment": alignment or {},
        "error_type": error_type,
        "error_detail": redact_text(error_detail, max_chars=800) if error_detail else None,
    }


def read_session_events(
    settings: PublicChatTelemetrySettings,
    *,
    session_hash: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    target = resolve_telemetry_path(settings.path)
    if not settings.enabled or not target.is_file():
        return []
    events: list[dict[str, Any]] = []
    try:
        with target.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get("session_hash") == session_hash:
                    events.append(event)
    except Exception:
        return []
    return events[-limit:]


def conversation_state_for_session(
    settings: PublicChatTelemetrySettings,
    *,
    session_hash: str,
    limit: int = 5,
) -> dict[str, Any]:
    events = read_session_events(settings, session_hash=session_hash, limit=limit)
    return {
        "prior_turn_count": len(events),
        "turn_index": len(events) + 1,
        "recent": [
            {
                "status": event.get("status"),
                "intent": (event.get("intent") or {}).get("primary_intent"),
                "message": event.get("message"),
                "reply_preview": (event.get("reply") or "")[:240],
            }
            for event in events
        ],
    }


def telemetry_stats(settings: PublicChatTelemetrySettings) -> dict[str, Any]:
    target = resolve_telemetry_path(settings.path)
    if not settings.enabled:
        return {"enabled": False, "path": settings.path, "configured": False}
    if not target.is_file():
        return {"enabled": True, "path": settings.path, "configured": True, "events": 0}
    events = 0
    last: dict[str, Any] | None = None
    try:
        with target.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                events += 1
                try:
                    last = json.loads(line)
                except json.JSONDecodeError:
                    last = {"status": "invalid_json"}
    except Exception as exc:
        return {
            "enabled": True,
            "path": settings.path,
            "configured": True,
            "events": events,
            "read_error": type(exc).__name__,
        }
    return {
        "enabled": True,
        "path": settings.path,
        "configured": True,
        "events": events,
        "last_created_at": last.get("created_at") if isinstance(last, dict) else None,
        "last_status": last.get("status") if isinstance(last, dict) else None,
    }
