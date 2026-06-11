"""Rate limits for governance v1 pilot API (Redis or in-process fallback)."""

from __future__ import annotations

import time
from collections import defaultdict

from fastapi import HTTPException

from noetfield_config import get_settings
from noetfield_governance import redis_runtime
from noetfield_governance.pilot_auth import PilotAuthContext

_memory_buckets: dict[str, list[float]] = defaultdict(list)


def _memory_check(key: str, *, max_calls: int, window_sec: int) -> None:
    now = time.time()
    bucket = _memory_buckets[key]
    cutoff = now - window_sec
    _memory_buckets[key] = [t for t in bucket if t > cutoff]
    if len(_memory_buckets[key]) >= max_calls:
        raise HTTPException(status_code=429, detail="Governance pilot rate limit exceeded")
    _memory_buckets[key].append(now)


def reset_memory_rate_limits_for_tests() -> None:
    """Test helper — clear in-process rate limit buckets."""
    _memory_buckets.clear()


async def check_governance_pilot_rate_limit(auth: PilotAuthContext, request_path: str) -> None:
    settings = get_settings()
    limit = settings.governance_pilot_rate_limit_per_min
    if limit <= 0:
        return
    key = f"gov:{auth.key_label}:{request_path}"
    if redis_runtime.is_enabled():
        try:
            await redis_runtime.check_rate_limit(
                key, max_calls=limit, window_sec=60
            )
        except PermissionError as exc:
            raise HTTPException(status_code=429, detail=str(exc)) from exc
    else:
        _memory_check(key, max_calls=limit, window_sec=60)


async def check_workspace_ui_rate_limit(auth: PilotAuthContext, operation: str) -> None:
    """Workspace UI (Trust Ledger console) rate limit bucket."""
    settings = get_settings()
    limit = settings.governance_workspace_ui_rate_limit_per_min
    if limit <= 0:
        return
    key = f"workspace-ui:{auth.key_label}:{operation}"
    if redis_runtime.is_enabled():
        try:
            await redis_runtime.check_rate_limit(key, max_calls=limit, window_sec=60)
        except PermissionError as exc:
            raise HTTPException(status_code=429, detail=str(exc)) from exc
    else:
        _memory_check(key, max_calls=limit, window_sec=60)
