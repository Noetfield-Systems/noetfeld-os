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
