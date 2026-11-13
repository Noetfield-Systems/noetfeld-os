from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional


VALID_STATUSES = frozenset({"queued", "leased", "running", "failed", "succeeded"})

ACTION_RETRY_NOW = "retry_now"
ACTION_WAIT = "wait"
ACTION_ABANDON = "abandon"
ACTION_NONE = "none"


class InvalidJobInput(ValueError):
    """Raised when job scheduling inputs are malformed."""


@dataclass(frozen=True)
class RetryDecision:
    action: str
    reason: str
    next_attempt_at: Optional[datetime]
    attempts_remaining: int

    def as_dict(self) -> dict:
        return {
            "action": self.action,
            "reason": self.reason,
            "next_attempt_at": (
                self.next_attempt_at.isoformat()
                if self.next_attempt_at is not None
                else None
            ),
            "attempts_remaining": self.attempts_remaining,
        }


def _ensure_aware_utc(value: datetime, field: str) -> datetime:
    if not isinstance(value, datetime):
        raise InvalidJobInput(f"{field} must be a datetime, got {type(value).__name__}")
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        raise InvalidJobInput(f"{field} must be timezone-aware")
    return value.astimezone(timezone.utc)


def _validate_non_negative_int(value: int, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise InvalidJobInput(f"{field} must be an int, got {type(value).__name__}")
    if value < 0:
        raise InvalidJobInput(f"{field} must be >= 0, got {value}")
    return value


def _validate_positive_int(value: int, field: str) -> int:
    value = _validate_non_negative_int(value, field)
    if value == 0:
        raise InvalidJobInput(f"{field} must be > 0")
    return value


def _validate_status(status: str) -> str:
    if not isinstance(status, str):
        raise InvalidJobInput(f"status must be a str, got {type(status).__name__}")
    normalized = status.strip().lower()
    if normalized not in VALID_STATUSES:
        raise InvalidJobInput(
            f"status must be one of {sorted(VALID_STATUSES)}, got {status!r}"
        )
    return normalized


def compute_retry_decision(
    *,
    created_at: datetime,
    now: datetime,
    lease_expires_at: Optional[datetime],
    retry_count: int,
    max_attempts: int,
    status: str,
    backoff_base_seconds: int = 30,
    backoff_cap_seconds: int = 3600,
) -> RetryDecision:
    """Compute the deterministic next action for a job.

    All datetimes must be timezone-aware; they are normalized to UTC.
    """
    created = _ensure_aware_utc(created_at, "created_at")
    current = _ensure_aware_utc(now, "now")
    lease = (
        _ensure_aware_utc(lease_expires_at, "lease_expires_at")
        if lease_expires_at is not None
        else None
    )
    retries = _validate_non_negative_int(retry_count, "retry_count")
    max_att = _validate_positive_int(max_attempts, "max_attempts")
    base = _validate_positive_int(backoff_base_seconds, "backoff_base_seconds")
    cap = _validate_positive_int(backoff_cap_seconds, "backoff_cap_seconds")
    if cap < base:
        raise InvalidJobInput("backoff_cap_seconds must be >= backoff_base_seconds")
    if current < created:
        raise InvalidJobInput("now must not be before created_at")
    normalized_status = _validate_status(status)

    attempts_remaining = max_att - retries

    if normalized_status == "succeeded":
        return RetryDecision(
            action=ACTION_NONE,
            reason="job already succeeded",
            next_attempt_at=None,
            attempts_remaining=max(attempts_remaining, 0),
        )

    if attempts_remaining <= 0:
        return RetryDecision(
            action=ACTION_ABANDON,
            reason=f"max attempts exhausted ({retries}/{max_att})",
            next_attempt_at=None,
            attempts_remaining=0,
        )

    if normalized_status == "queued":
        return RetryDecision(
            action=ACTION_RETRY_NOW,
            reason="job is queued and ready to run",
            next_attempt_at=current,
            attempts_remaining=attempts_remaining,
        )

    if lease is not None and lease > current:
        return RetryDecision(
            action=ACTION_WAIT,
            reason="lease still active",
            next_attempt_at=lease,
            attempts_remaining=attempts_remaining,
        )

    delay = min(base * (2 ** retries), cap)
    next_at = current + timedelta(seconds=delay)
    reason = (
        "lease expired" if lease is not None else "no active lease"
    )
    return RetryDecision(
        action=ACTION_RETRY_NOW,
        reason=reason,
        next_attempt_at=next_at,
        attempts_remaining=attempts_remaining,
    )
