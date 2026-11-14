from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Mapping

__all__ = [
    "ReleaseReceipt",
    "VerificationDecision",
    "verify_release_receipt",
    "SHA_RE",
]

SHA_RE = re.compile(r"^[0-9a-f]{40}$")

VALID_ENVIRONMENTS = frozenset({"production", "staging", "preview", "development"})
VALID_CI_STATUSES = frozenset({"success", "failure", "pending", "cancelled", "skipped"})
VALID_DEPLOY_STATUSES = frozenset({"deployed", "failed", "pending", "rolled_back", "not_deployed"})

VERIFIED = "verified"
PENDING = "pending"
REJECTED = "rejected"


@dataclass(frozen=True)
class ReleaseReceipt:
    """A GitHub/Railway release receipt to be verified."""

    commit_sha: str
    environment: str
    ci_status: str
    deploy_status: str
    verification_signal: str
    source: str = ""


@dataclass(frozen=True)
class VerificationDecision:
    """Machine-readable verification outcome."""

    decision: str
    reasons: tuple[str, ...] = field(default_factory=tuple)

    @property
    def verified(self) -> bool:
        return self.decision == VERIFIED

    def to_dict(self) -> dict[str, Any]:
        return {"decision": self.decision, "reasons": list(self.reasons)}


def _normalize(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().lower()


def _extract(receipt: Any, key: str) -> Any:
    if isinstance(receipt, Mapping):
        return receipt.get(key)
    return getattr(receipt, key, None)


def verify_release_receipt(
    receipt: Any,
    expected_sha: str,
    expected_environment: str,
    require_verification_signal: bool = True,
) -> VerificationDecision:
    """Verify a release receipt against an expected commit SHA and environment.

    Returns a :class:`VerificationDecision` with decision in
    ``{"verified", "pending", "rejected"}`` and a tuple of human-readable
    reasons. Missing provenance or invalid values yield ``rejected``.
    """
    reasons: list[str] = []

    if receipt is None:
        return VerificationDecision(REJECTED, ("missing_receipt",))

    exp_sha = _normalize(expected_sha)
    if not SHA_RE.match(exp_sha):
        return VerificationDecision(REJECTED, ("invalid_expected_sha",))

    exp_env = _normalize(expected_environment)
    if exp_env not in VALID_ENVIRONMENTS:
        return VerificationDecision(REJECTED, ("invalid_expected_environment",))

    commit_sha = _normalize(_extract(receipt, "commit_sha"))
    environment = _normalize(_extract(receipt, "environment"))
    ci_status = _normalize(_extract(receipt, "ci_status"))
    deploy_status = _normalize(_extract(receipt, "deploy_status"))
    verification_signal = _normalize(_extract(receipt, "verification_signal"))
    source = _normalize(_extract(receipt, "source"))

    if not commit_sha:
        reasons.append("missing_commit_sha")
    elif not SHA_RE.match(commit_sha):
        reasons.append("invalid_commit_sha")
    elif commit_sha != exp_sha:
        reasons.append("commit_sha_mismatch")

    if not environment:
        reasons.append("missing_environment")
    elif environment not in VALID_ENVIRONMENTS:
        reasons.append("invalid_environment")
    elif environment != exp_env:
        reasons.append("environment_mismatch")

    if not ci_status:
        reasons.append("missing_ci_status")
    elif ci_status not in VALID_CI_STATUSES:
        reasons.append("invalid_ci_status")

    if not deploy_status:
        reasons.append("missing_deploy_status")
    elif deploy_status not in VALID_DEPLOY_STATUSES:
        reasons.append("invalid_deploy_status")

    if require_verification_signal and not verification_signal:
        reasons.append("missing_verification_signal")

    if not source:
        reasons.append("missing_source")

    hard_reject = {
        "missing_commit_sha",
        "invalid_commit_sha",
        "commit_sha_mismatch",
        "missing_environment",
        "invalid_environment",
        "environment_mismatch",
        "missing_ci_status",
        "invalid_ci_status",
        "missing_deploy_status",
        "invalid_deploy_status",
        "missing_source",
    }
    if require_verification_signal:
        hard_reject.add("missing_verification_signal")

    if any(r in hard_reject for r in reasons):
        return VerificationDecision(REJECTED, tuple(reasons))

    if ci_status in {"failure", "cancelled"}:
        reasons.append("ci_not_successful")
        return VerificationDecision(REJECTED, tuple(reasons))

    if deploy_status in {"failed", "rolled_back", "not_deployed"}:
        reasons.append("deploy_not_successful")
        return VerificationDecision(REJECTED, tuple(reasons))

    if ci_status == "pending" or deploy_status == "pending":
        reasons.append("release_pending")
        return VerificationDecision(PENDING, tuple(reasons))

    if ci_status == "skipped":
        reasons.append("ci_skipped")
        return VerificationDecision(PENDING, tuple(reasons))

    if ci_status == "success" and deploy_status == "deployed":
        return VerificationDecision(VERIFIED, tuple(reasons))

    reasons.append("unrecognized_state")
    return VerificationDecision(REJECTED, tuple(reasons))
