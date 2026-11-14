from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class JobState(str, Enum):
    NEW = "new"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


TERMINAL_STATES = frozenset({JobState.SUCCEEDED, JobState.FAILED, JobState.CANCELLED})


class Decision(str, Enum):
    START = "start"
    WAIT = "wait"
    RETRY = "retry"
    DENY = "deny"


@dataclass(frozen=True)
class LeaseEvaluation:
    decision: Decision
    reason: str
    retry_allowed: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "decision": self.decision.value,
            "reason": self.reason,
            "retry_allowed": self.retry_allowed,
        }


def _require_aware_utc(value: datetime, name: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f"{name} must be a datetime, got {type(value).__name__}")
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        raise ValueError(f"{name} must be timezone-aware (naive datetime rejected)")
    return value.astimezone(timezone.utc)


def _coerce_state(state: object) -> JobState:
    if isinstance(state, JobState):
        return state
    if isinstance(state, str):
        try:
            return JobState(state.strip().lower())
        except ValueError as exc:
            raise ValueError(f"unknown job state: {state!r}") from exc
    raise TypeError(f"state must be JobState or str, got {type(state).__name__}")


def _validate_attempts(attempt: object, max_attempts: object) -> tuple[int, int]:
    if isinstance(attempt, bool) or not isinstance(attempt, int):
        raise TypeError("attempt must be an int")
    if isinstance(max_attempts, bool) or not isinstance(max_attempts, int):
        raise TypeError("max_attempts must be an int")
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")
    if attempt < 0:
        raise ValueError("attempt must be >= 0")
    if attempt > max_attempts:
        raise ValueError("attempt must not exceed max_attempts")
    return attempt, max_attempts


def evaluate_lease(
    state: object,
    attempt: int,
    max_attempts: int,
    now: datetime,
    lease_expiry: Optional[datetime],
) -> LeaseEvaluation:
    """Evaluate a cloud coding job lease and decide whether a retry is allowed.

    Pure and deterministic: no clock reads, no I/O. All datetimes must be
    timezone-aware; naive datetimes are rejected.
    """
    job_state = _coerce_state(state)
    attempt, max_attempts = _validate_attempts(attempt, max_attempts)
    now_utc = _require_aware_utc(now, "now")

    if lease_expiry is not None:
        expiry_utc = _require_aware_utc(lease_expiry, "lease_expiry")
    else:
        expiry_utc = None

    if job_state in TERMINAL_STATES:
        return LeaseEvaluation(
            decision=Decision.DENY,
            reason=f"terminal_state:{job_state.value}",
            retry_allowed=False,
        )

    if job_state is JobState.NEW:
        return LeaseEvaluation(
            decision=Decision.START,
            reason="new_job",
            retry_allowed=False,
        )

    # RUNNING: an active lease means wait; an expired lease means retry if budget remains.
    if expiry_utc is not None and now_utc < expiry_utc:
        return LeaseEvaluation(
            decision=Decision.WAIT,
            reason="active_lease",
            retry_allowed=False,
        )

    if attempt >= max_attempts:
        return LeaseEvaluation(
            decision=Decision.DENY,
            reason="retry_exhausted",
            retry_allowed=False,
        )

    reason = "expired_lease" if expiry_utc is not None else "no_lease"
    return LeaseEvaluation(
        decision=Decision.RETRY,
        reason=reason,
        retry_allowed=True,
    )
