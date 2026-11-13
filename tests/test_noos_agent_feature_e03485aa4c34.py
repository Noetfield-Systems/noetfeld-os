from datetime import datetime, timedelta, timezone

import pytest

from scripts.noos_agent_feature_e03485aa4c34 import (
    ACTION_ABANDON,
    ACTION_NONE,
    ACTION_RETRY_NOW,
    ACTION_WAIT,
    InvalidJobInput,
    compute_retry_decision,
)

UTC = timezone.utc


def _dt(seconds: int = 0) -> datetime:
    return datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC) + timedelta(seconds=seconds)


def test_active_lease_waits_until_expiry():
    decision = compute_retry_decision(
        created_at=_dt(0),
        now=_dt(10),
        lease_expires_at=_dt(60),
        retry_count=1,
        max_attempts=5,
        status="running",
    )
    assert decision.action == ACTION_WAIT
    assert decision.reason == "lease still active"
    assert decision.next_attempt_at == _dt(60)
    assert decision.attempts_remaining == 4


def test_expired_lease_schedules_backoff_retry():
    decision = compute_retry_decision(
        created_at=_dt(0),
        now=_dt(120),
        lease_expires_at=_dt(60),
        retry_count=2,
        max_attempts=5,
        status="failed",
        backoff_base_seconds=30,
        backoff_cap_seconds=3600,
    )
    assert decision.action == ACTION_RETRY_NOW
    assert decision.reason == "lease expired"
    # 30 * 2**2 = 120 seconds
    assert decision.next_attempt_at == _dt(120) + timedelta(seconds=120)
    assert decision.attempts_remaining == 3


def test_queued_status_retries_immediately():
    decision = compute_retry_decision(
        created_at=_dt(0),
        now=_dt(5),
        lease_expires_at=None,
        retry_count=0,
        max_attempts=3,
        status="queued",
    )
    assert decision.action == ACTION_RETRY_NOW
    assert decision.reason == "job is queued and ready to run"
    assert decision.next_attempt_at == _dt(5)
    assert decision.attempts_remaining == 3


def test_max_attempts_exhausted_abandons():
    decision = compute_retry_decision(
        created_at=_dt(0),
        now=_dt(500),
        lease_expires_at=_dt(100),
        retry_count=3,
        max_attempts=3,
        status="failed",
    )
    assert decision.action == ACTION_ABANDON
    assert decision.attempts_remaining == 0
    assert decision.next_attempt_at is None
    assert "exhausted" in decision.reason


def test_succeeded_job_has_no_action():
    decision = compute_retry_decision(
        created_at=_dt(0),
        now=_dt(10),
        lease_expires_at=None,
        retry_count=1,
        max_attempts=3,
        status="succeeded",
    )
    assert decision.action == ACTION_NONE
    assert decision.next_attempt_at is None


def test_naive_datetime_rejected():
    with pytest.raises(InvalidJobInput):
        compute_retry_decision(
            created_at=datetime(2026, 1, 1, 12, 0, 0),
            now=_dt(0),
            lease_expires_at=None,
            retry_count=0,
            max_attempts=3,
            status="queued",
        )


def test_invalid_status_rejected():
    with pytest.raises(InvalidJobInput):
        compute_retry_decision(
            created_at=_dt(0),
            now=_dt(0),
            lease_expires_at=None,
            retry_count=0,
            max_attempts=3,
            status="bogus",
        )


def test_negative_retry_count_rejected():
    with pytest.raises(InvalidJobInput):
        compute_retry_decision(
            created_at=_dt(0),
            now=_dt(0),
            lease_expires_at=None,
            retry_count=-1,
            max_attempts=3,
            status="queued",
        )


def test_now_before_created_rejected():
    with pytest.raises(InvalidJobInput):
        compute_retry_decision(
            created_at=_dt(100),
            now=_dt(0),
            lease_expires_at=None,
            retry_count=0,
            max_attempts=3,
            status="queued",
        )


def test_backoff_is_capped():
    decision = compute_retry_decision(
        created_at=_dt(0),
        now=_dt(0),
        lease_expires_at=None,
        retry_count=10,
        max_attempts=20,
        status="failed",
        backoff_base_seconds=30,
        backoff_cap_seconds=120,
    )
    assert decision.next_attempt_at == _dt(0) + timedelta(seconds=120)


def test_timezone_normalization_to_utc():
    tz = timezone(timedelta(hours=2))
    local_now = datetime(2026, 1, 1, 14, 0, 0, tzinfo=tz)  # == 12:00 UTC
    decision = compute_retry_decision(
        created_at=_dt(0),
        now=local_now,
        lease_expires_at=None,
        retry_count=0,
        max_attempts=3,
        status="queued",
    )
    assert decision.next_attempt_at == _dt(0)
    assert decision.next_attempt_at.tzinfo == UTC
