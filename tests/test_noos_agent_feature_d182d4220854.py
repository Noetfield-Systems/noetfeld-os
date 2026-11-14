import pytest

from scripts.noos_agent_feature_d182d4220854 import (
    Job,
    JobState,
    Outcome,
    RateLimit,
    RetryPolicy,
)


def make_job(job_id="j1", packet="wp-1", **kw):
    return Job(job_id=job_id, work_packet=packet, **kw)


def test_lease_expiration_requeues_job():
    job = make_job()
    policy = RetryPolicy([job], lease_seconds=10.0)
    policy.claim("j1", now=0.0)
    assert job.state is JobState.ACTIVE
    expired = policy.expire_leases(now=5.0)
    assert expired == []
    expired = policy.expire_leases(now=10.0)
    assert expired == [job]
    assert job.state is JobState.QUEUED
    assert job.lease_expires_at is None


def test_stale_job_exhausts_attempts():
    job = make_job(max_attempts=2)
    policy = RetryPolicy([job], lease_seconds=1.0)
    policy.claim("j1", now=0.0)
    policy.expire_leases(now=2.0)
    policy.claim("j1", now=3.0)
    policy.expire_leases(now=5.0)
    assert job.attempts == 2
    assert policy.next_eligible(now=6.0) is None


def test_duplicate_work_packets_are_independent():
    a = make_job(job_id="a", packet="wp-dup")
    b = make_job(job_id="b", packet="wp-dup")
    policy = RetryPolicy([a, b])
    first = policy.next_eligible(now=0.0)
    assert first is a
    policy.claim("a", now=0.0)
    second = policy.next_eligible(now=0.0)
    assert second is b


def test_duplicate_job_id_rejected():
    with pytest.raises(ValueError):
        RetryPolicy([make_job(job_id="x"), make_job(job_id="x")])


def test_no_work_scenario():
    policy = RetryPolicy([])
    assert policy.next_eligible(now=0.0) is None


def test_failed_release_not_deployed():
    job = make_job()
    policy = RetryPolicy([job])
    policy.claim("j1", now=0.0)
    policy.release_failed("j1")
    assert job.state is JobState.FAILED
    assert job.outcome is Outcome.FAILED
    assert policy.is_deployed("j1") is False


def test_complete_deployed_marks_done():
    job = make_job()
    policy = RetryPolicy([job])
    policy.claim("j1", now=0.0)
    policy.complete("j1", Outcome.DEPLOYED)
    assert policy.is_deployed("j1") is True


def test_rate_limit_blocks_claims():
    rl = RateLimit(max_per_window=1, window_seconds=10.0)
    policy = RetryPolicy([make_job(job_id="a"), make_job(job_id="b")], rate_limit=rl)
    policy.claim("a", now=0.0)
    assert policy.next_eligible(now=1.0) is None
    with pytest.raises(ValueError):
        policy.claim("b", now=1.0)
    assert policy.next_eligible(now=11.0) is not None


def test_claim_unknown_job_raises():
    policy = RetryPolicy([])
    with pytest.raises(KeyError):
        policy.claim("missing", now=0.0)


def test_invalid_lease_seconds():
    with pytest.raises(ValueError):
        RetryPolicy([], lease_seconds=0.0)
