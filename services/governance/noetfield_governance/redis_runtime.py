"""Redis-backed rate limits and Telegram session memory (optional)."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

logger = logging.getLogger("noetfield.governance.redis")

_client: Any = None
_enabled = False


async def connect(redis_url: str | None, *, enabled: bool = True) -> bool:
    global _client, _enabled
    if not enabled or not (redis_url or "").strip():
        _client = None
        _enabled = False
        return False
    try:
        import redis.asyncio as redis
    except ImportError:
        logger.warning("redis package unavailable")
        _enabled = False
        return False

    try:
        _client = redis.from_url(redis_url, decode_responses=True)
        await _client.ping()
        _enabled = True
        logger.info("redis_connected")
        return True
    except Exception as exc:
        logger.warning("redis_connect_failed %s", exc)
        _client = None
        _enabled = False
        return False


async def close() -> None:
    global _client, _enabled
    if _client is not None:
        try:
            await _client.aclose()
        except Exception:
            pass
    _client = None
    _enabled = False


def is_enabled() -> bool:
    return _enabled and _client is not None


async def check_rate_limit(key: str, *, max_calls: int, window_sec: int) -> None:
    """Raises PermissionError when limit exceeded."""
    if not is_enabled():
        return
    assert _client is not None
    rk = f"nf:rl:{key}"
    count = await _client.incr(rk)
    if count == 1:
        await _client.expire(rk, window_sec)
    if count > max_calls:
        raise PermissionError("Rate limit exceeded. Try again in a minute.")


async def append_session_turn(session_key: str, role: str, content: str, *, max_turns: int = 8) -> None:
    if not is_enabled():
        return
    assert _client is not None
    rk = f"nf:sess:{session_key}"
    payload = json.dumps({"role": role, "content": content[:2000], "at": time.time()})
    pipe = _client.pipeline()
    await pipe.rpush(rk, payload)
    await pipe.ltrim(rk, -max_turns, -1)
    await pipe.expire(rk, 3600)
    await pipe.execute()


async def get_session_history(session_key: str) -> list[tuple[str, str]]:
    if not is_enabled():
        return []
    assert _client is not None
    rk = f"nf:sess:{session_key}"
    raw = await _client.lrange(rk, 0, -1)
    out: list[tuple[str, str]] = []
    now = time.time()
    for item in raw:
        try:
            data = json.loads(item)
            if now - float(data.get("at", 0)) > 3600:
                continue
            out.append((str(data.get("role", "")), str(data.get("content", ""))))
        except json.JSONDecodeError:
            continue
    return out


async def clear_session(session_key: str) -> None:
    if not is_enabled():
        return
    assert _client is not None
    await _client.delete(f"nf:sess:{session_key}")
