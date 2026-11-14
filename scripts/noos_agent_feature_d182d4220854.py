from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Optional


class JobState(str, Enum):
    QUEUED = "queued"
    ACTIVE = "active"
    DONE = "done"
    FAILED = "failed"


class Outcome(str, Enum):
    DEPLOYED = "deployed"
    FAILED = "failed"
    RELEASED = "released"


@dataclass
class Job:
    job_id: str
    work_packet: str
    state: JobState = JobState.QUEUED
    attempts: int = 0
    lease_expires_at: Optional[float] = None
    outcome: Optional[Outcome] = None
    max_attempts: int = 3

    def is_expired(self, now: float) -> bool:
        return (
            self.state is JobState.ACTIVE
            and self.lease_expires_at is not None
            and now >= self.lease_expires_at
        )

    def is_terminal(self) -> bool:
        return self.state in (JobState.DONE, JobState.FAILED)


@dataclass
class RateLimit:
    max_per_window: int
    window_seconds: float
    _timestamps: list[float] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.max_per_window < 0:
            raise ValueError("max_per_window must be non-negative")
        if self.window_seconds <= 0:
            raise ValueError("window_seconds must be positive")

    def _prune(self, now: float) -> None:
        cutoff = now - self.window_seconds
        self._timestamps = [t for t in self._timestamps if t > cutoff]

    def allows(self, now: float) -> bool:
        self._prune(now)
        return len(self._timestamps) < self.max_per_window

    def record(self, now: float) -> None:
        self._prune(now)
        self._timestamps.append(now)


class RetryPolicy:
    """Deterministic retry-and-continuation policy engine."""

    def __init__(
        self,
        jobs: Iterable[Job],
        rate_limit: Optional[RateLimit] = None,
        lease_seconds: float = 60.0,
    ) -> None:
        if lease_seconds <= 0:
            raise ValueError("lease_seconds must be positive")
        self._jobs: dict[str, Job] = {}
        for job in jobs:
            if job.job_id in self._jobs:
                raise ValueError(f"duplicate job_id: {job.job_id}")
            self._jobs[job.job_id] = job
        self.rate_limit = rate_limit
        self.lease_seconds = lease_seconds

    def jobs(self) -> list[Job]:
        return list(self._jobs.values())

    def expire_leases(self, now: float) -> list[Job]:
        expired: list[Job] = []
        for job in self._jobs.values():
            if job.is_expired(now):
                job.state = JobState.QUEUED
                job.lease_expires_at = None
                expired.append(job)
        return expired

    def _is_eligible(self, job: Job) -> bool:
        if job.is_terminal():
            return False
        if job.state is JobState.ACTIVE:
            return False
        if job.attempts >= job.max_attempts:
            return False
        return True

    def next_eligible(self, now: float) -> Optional[Job]:
        self.expire_leases(now)
        if self.rate_limit is not None and not self.rate_limit.allows(now):
            return None
        for job in self._jobs.values():
            if self._is_eligible(job):
                return job
        return None

    def claim(self, job_id: str, now: float) -> Job:
        job = self._jobs.get(job_id)
        if job is None:
            raise KeyError(f"unknown job_id: {job_id}")
        if not self._is_eligible(job):
            raise ValueError(f"job not eligible: {job_id}")
        if self.rate_limit is not None:
            if not self.rate_limit.allows(now):
                raise ValueError("rate limit exceeded")
            self.rate_limit.record(now)
        job.state = JobState.ACTIVE
        job.attempts += 1
        job.lease_expires_at = now + self.lease_seconds
        return job

    def complete(self, job_id: str, outcome: Outcome) -> Job:
        job = self._jobs.get(job_id)
        if job is None:
            raise KeyError(f"unknown job_id: {job_id}")
        if job.state is not JobState.ACTIVE:
            raise ValueError(f"job not active: {job_id}")
        job.outcome = outcome
        job.lease_expires_at = None
        if outcome is Outcome.DEPLOYED:
            job.state = JobState.DONE
        else:
            job.state = JobState.FAILED
        return job

    def is_deployed(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if job is None:
            raise KeyError(f"unknown job_id: {job_id}")
        return job.state is JobState.DONE and job.outcome is Outcome.DEPLOYED

    def release_failed(self, job_id: str) -> Job:
        """A failed release must never be reported as deployed."""
        job = self._jobs.get(job_id)
        if job is None:
            raise KeyError(f"unknown job_id: {job_id}")
        job.outcome = Outcome.FAILED
        job.state = JobState.FAILED
        job.lease_expires_at = None
        return job
