"""In-memory conversation sessions for Telegram (per chat_id)."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from threading import Lock

_MAX_TURNS = 8
_SESSION_TTL_SEC = 3600


@dataclass
class ChatTurn:
    role: str
    content: str
    at: float = field(default_factory=time.time)


_store: dict[str, deque[ChatTurn]] = defaultdict(lambda: deque(maxlen=_MAX_TURNS))
_lock = Lock()


def append_turn(session_key: str, role: str, content: str) -> None:
    with _lock:
        bucket = _store[session_key]
        bucket.append(ChatTurn(role=role, content=content[:2000]))


def get_history(session_key: str) -> list[tuple[str, str]]:
    now = time.time()
    with _lock:
        bucket = _store[session_key]
        fresh = [t for t in bucket if now - t.at < _SESSION_TTL_SEC]
        _store[session_key] = deque(fresh, maxlen=_MAX_TURNS)
        return [(t.role, t.content) for t in fresh]


async def get_history_async(session_key: str) -> list[tuple[str, str]]:
    from noetfield_governance import redis_runtime

    if redis_runtime.is_enabled():
        hist = await redis_runtime.get_session_history(session_key)
        if hist:
            return hist
    return get_history(session_key)


async def append_turn_async(session_key: str, role: str, content: str) -> None:
    append_turn(session_key, role, content)
    from noetfield_governance import redis_runtime

    if redis_runtime.is_enabled():
        await redis_runtime.append_session_turn(session_key, role, content, max_turns=_MAX_TURNS)


async def clear_session_async(session_key: str) -> None:
    clear_session(session_key)
    from noetfield_governance import redis_runtime

    if redis_runtime.is_enabled():
        await redis_runtime.clear_session(session_key)


def clear_session(session_key: str) -> None:
    with _lock:
        _store.pop(session_key, None)


def format_history_for_prompt(history: list[tuple[str, str]], latest_user: str) -> str:
    if not history:
        return latest_user
    lines = ["[Conversation context — respond to the latest user message only]"]
    for role, content in history[-6:]:
        prefix = "User" if role == "user" else "Assistant"
        lines.append(f"{prefix}: {content}")
    lines.append(f"User: {latest_user}")
    return "\n".join(lines)
