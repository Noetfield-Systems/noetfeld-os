from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Iterable, Mapping


class DeliveryState(IntEnum):
    """Ordered delivery states. Higher value implies strictly more evidence."""

    NONE = 0
    CANDIDATE = 1
    TESTED = 2
    RELEASED = 3
    DEPLOYED = 4
    VERIFIED = 5


_SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")
_BRANCH_RE = re.compile(r"^[A-Za-z0-9._/-]{1,200}$")
_PR_RE = re.compile(r"^[A-Za-z0-9._/#-]{1,200}$")

_TEST_PASS = {"pass", "passed", "success", "succeeded", "green", "ok"}
_TEST_FAIL = {"fail", "failed", "failure", "error", "red", "broken"}
_DEPLOY_OK = {"ok", "success", "succeeded", "healthy", "live", "deployed"}
_DEPLOY_BAD = {"fail", "failed", "error", "unhealthy", "down", "missing"}


def _norm(value: Any) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise TypeError(f"expected string, got {type(value).__name__}")
    return value.strip().lower()


def _valid_sha(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    v = value.strip().lower()
    return v if _SHA_RE.match(v) else None


def _valid_branch(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    v = value.strip()
    if not v or not _BRANCH_RE.match(v):
        return None
    if ".." in v or v.startswith("/") or v.endswith("/"):
        return None
    return v


def _valid_pr(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    v = value.strip()
    return v if v and _PR_RE.match(v) else None


def _classify_test(status: Any) -> bool | None:
    s = _norm(status)
    if not s:
        return None
    if s in _TEST_PASS:
        return True
    if s in _TEST_FAIL:
        return False
    return None


def _classify_deploy(status: Any) -> bool | None:
    s = _norm(status)
    if not s:
        return None
    if s in _DEPLOY_OK:
        return True
    if s in _DEPLOY_BAD:
        return False
    return None


@dataclass(frozen=True)
class DeliveryEvidence:
    """Raw, untrusted delivery evidence for a single coding job."""

    commit_sha: str | None = None
    test_status: str | None = None
    pr_ref: str | None = None
    branch: str | None = None
    deployment_status: str | None = None
    readback_ok: bool | None = None

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "DeliveryEvidence":
        if not isinstance(data, Mapping):
            raise TypeError("evidence must be a mapping")
        return cls(
            commit_sha=data.get("commit_sha"),
            test_status=data.get("test_status"),
            pr_ref=data.get("pr_ref"),
            branch=data.get("branch"),
            deployment_status=data.get("deployment_status"),
            readback_ok=data.get("readback_ok"),
        )


@dataclass(frozen=True)
class DeliveryAssessment:
    state: DeliveryState
    commit_sha: str | None
    branch: str | None
    pr_ref: str | None
    tests_passed: bool | None
    deployed: bool | None
    verified: bool
    reasons: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_released(self) -> bool:
        return self.state >= DeliveryState.RELEASED

    @property
    def is_deployed(self) -> bool:
        return self.state >= DeliveryState.DEPLOYED

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": self.state.name,
            "commit_sha": self.commit_sha,
            "branch": self.branch,
            "pr_ref": self.pr_ref,
            "tests_passed": self.tests_passed,
            "deployed": self.deployed,
            "verified": self.verified,
            "reasons": list(self.reasons),
        }


def assess_delivery(evidence: DeliveryEvidence | Mapping[str, Any]) -> DeliveryAssessment:
    """Evaluate delivery evidence, returning the highest *justified* state.

    States are strictly ordered and never conflated: a passing test does not
    imply release, a release does not imply deployment, and deployment does
    not imply verified readback.
    """
    if isinstance(evidence, Mapping):
        evidence = DeliveryEvidence.from_mapping(evidence)
    if not isinstance(evidence, DeliveryEvidence):
        raise TypeError("evidence must be DeliveryEvidence or mapping")

    reasons: list[str] = []

    sha = _valid_sha(evidence.commit_sha)
    if evidence.commit_sha is not None and sha is None:
        reasons.append("invalid commit_sha")

    branch = _valid_branch(evidence.branch)
    if evidence.branch is not None and branch is None:
        reasons.append("invalid branch")

    pr_ref = _valid_pr(evidence.pr_ref)
    if evidence.pr_ref is not None and pr_ref is None:
        reasons.append("invalid pr_ref")

    tests_passed = _classify_test(evidence.test_status)
    if evidence.test_status is not None and tests_passed is None:
        reasons.append("unrecognized test_status")

    deployed = _classify_deploy(evidence.deployment_status)
    if evidence.deployment_status is not None and deployed is None:
        reasons.append("unrecognized deployment_status")

    readback = evidence.readback_ok
    if readback is not None and not isinstance(readback, bool):
        reasons.append("invalid readback_ok")
        readback = None

    state = DeliveryState.NONE

    if sha is not None:
        state = DeliveryState.CANDIDATE

    if state >= DeliveryState.CANDIDATE and tests_passed is True:
        state = DeliveryState.TESTED

    if state >= DeliveryState.TESTED and (pr_ref is not None or branch is not None):
        state = DeliveryState.RELEASED

    if state >= DeliveryState.RELEASED and deployed is True:
        state = DeliveryState.DEPLOYED

    verified = state >= DeliveryState.DEPLOYED and readback is True
    if verified:
        state = DeliveryState.VERIFIED

    return DeliveryAssessment(
        state=state,
        commit_sha=sha,
        branch=branch,
        pr_ref=pr_ref,
        tests_passed=tests_passed,
        deployed=deployed,
        verified=verified,
        reasons=tuple(reasons),
    )


def canonical_work_packet_id(*parts: str) -> str:
    """Deterministic, idempotent WorkPacket identifier.

    The identifier is a stable hash over normalized, non-empty parts, so the
    same logical packet always yields the same id regardless of ordering of
    whitespace or duplicate parts.
    """
    if not parts:
        raise ValueError("at least one part is required")
    normalized: list[str] = []
    for part in parts:
        if not isinstance(part, str):
            raise TypeError("all parts must be strings")
        token = " ".join(part.split())
        if token:
            normalized.append(token)
    if not normalized:
        raise ValueError("at least one non-empty part is required")
    digest = hashlib.sha256("\x1f".join(normalized).encode("utf-8")).hexdigest()
    return f"WP-{digest[:32]}"


def summarize_states(assessments: Iterable[DeliveryAssessment]) -> dict[str, int]:
    """Count assessments per state name; useful for dashboards."""
    counts: dict[str, int] = {s.name: 0 for s in DeliveryState}
    for a in assessments:
        if not isinstance(a, DeliveryAssessment):
            raise TypeError("expected DeliveryAssessment instances")
        counts[a.state.name] += 1
    return counts
