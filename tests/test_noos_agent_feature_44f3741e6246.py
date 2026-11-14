from datetime import datetime, timedelta, timezone

import pytest

from scripts.noos_agent_feature_44f3741e6246 import (
    Decision,
    JobState,
    evaluate_lease,
)


NOW = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def test_new_job_starts():
    result = evaluate_lease(JobState.NEW, 0, 3, NOW, None)
    assert result.decision is Decision.START
    assert result.reason == "new_job"
    assert result.retry_allowed is False


def test_active_lease_waits():
    expiry = NOW + timedelta(minutes=5)
    result = evaluate_lease("running", 1, 3, NOW, expiry)
    assert result.decision is Decision.WAIT
    assert result.reason == "active_lease"
    assert result.retry_allowed is False


def test_expired_lease_allows_retry():
    expiry = NOW - timedelta(minutes=5)
    result = evaluate_lease(JobState.RUNNING, 1, 3, NOW, expiry)
    assert result.decision is Decision.RETRY
    assert result.reason == "expired_lease"
    assert result.retry_allowed is True


def test_retry_exhaustion_denies():
    expiry = NOW - timedelta(minutes=5)
    result = evaluate_lease(JobState.RUNNING, 3, 3, NOW, expiry)
    assert result.decision is Decision.DENY
    assert result.reason == "retry_exhausted"
    assert result.retry_allowed is False


@pytest.mark.parametrize("state", [JobState.SUCCEEDED, JobState.FAILED, JobState.CANCELLED])
def test_terminal_states_deny(state):
    result = evaluate_lease(state, 0, 3, NOW, None)
    assert result.decision is Decision.DENY
    assert result.reason == f"terminal_state:{state.value}"
    assert result.retry_allowed is False


def test_naive_datetime_rejected():
    naive = datetime(2026, 1, 1, 12, 0, 0)
    with pytest.raises(ValueError):
        evaluate_lease(JobState.RUNNING, 1, 3, naive, None)


def test_invalid_attempts_rejected():
    with pytest.raises(ValueError):
        evaluate_lease(JobState.RUNNING, 4, 3, NOW, None)
    with pytest.raises(ValueError):
        evaluate_lease(JobState.RUNNING, 0, 0, NOW, None)
    with pytest.raises(TypeError):
        evaluate_lease(JobState.RUNNING, True, 3, NOW, None)


def test_unknown_state_rejected():
    with pytest.raises(ValueError):
        evaluate_lease("bogus", 0, 3, NOW, None)


def test_as_dict_serialization():
    result = evaluate_lease(JobState.NEW, 0, 3, NOW, None)
    assert result.as_dict() == {
        "decision": "start",
        "reason": "new_job",
        "retry_allowed": False,
    }
