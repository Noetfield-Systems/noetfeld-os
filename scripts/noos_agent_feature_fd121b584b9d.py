from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Iterable, Mapping, Optional


class EvidenceState(str, Enum):
    MISSING = "MISSING"
    TESTED = "TESTED"
    DEPLOYED = "DEPLOYED"
    VERIFIED = "VERIFIED"
    CONTRADICTORY = "CONTRADICTORY"
    STALE = "STALE"


class Severity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    BLOCKER = "BLOCKER"


@dataclass(frozen=True)
class Finding:
    code: str
    severity: Severity
    message: str


@dataclass(frozen=True)
class NextStep:
    action: str
    reason: str


@dataclass(frozen=True)
class Assessment:
    state: EvidenceState
    findings: tuple[Finding, ...]
    next_steps: tuple[NextStep, ...]

    @property
    def is_release_ready(self) -> bool:
        return self.state is EvidenceState.VERIFIED and not any(
            f.severity is Severity.BLOCKER for f in self.findings
        )


@dataclass(frozen=True)
class ReleaseReceipt:
    source_commit: Optional[str]
    expected_commit: Optional[str]
    ci_status: Optional[str]
    deployment_state: Optional[str]
    verifier_id: Optional[str]
    author_id: Optional[str]
    evidence_timestamp: Optional[str]
    now: Optional[str] = None
    max_age_seconds: int = 86400


_CI_PASS = {"success", "passed", "green"}
_CI_FAIL = {"failure", "failed", "red", "error", "cancelled"}
_DEPLOY_OK = {"deployed", "live", "released"}
_DEPLOY_BAD = {"failed", "rolled_back", "not_deployed", "pending"}


def _parse_ts(value: Optional[str]) -> Optional[datetime]:
    if not value or not isinstance(value, str):
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _norm(value: Optional[str]) -> Optional[str]:
    if not isinstance(value, str):
        return None
    v = value.strip().lower()
    return v or None


def assess_receipt(receipt: ReleaseReceipt) -> Assessment:
    findings: list[Finding] = []
    steps: list[NextStep] = []

    # 1. Source commit identity
    src = _norm(receipt.source_commit)
    exp = _norm(receipt.expected_commit)
    commit_ok = False
    if src is None or exp is None:
        findings.append(Finding("COMMIT_MISSING", Severity.BLOCKER,
                                "Source or expected commit identity is missing."))
        steps.append(NextStep("Record source_commit and expected_commit in the receipt.",
                              "Commit identity cannot be validated without both values."))
    elif src != exp:
        findings.append(Finding("COMMIT_MISMATCH", Severity.BLOCKER,
                                f"Source commit {src!r} does not match expected {exp!r}."))
        steps.append(NextStep("Rebuild evidence from the expected commit.",
                              "Evidence was produced from a different commit."))
    else:
        commit_ok = True

    # 2. CI status
    ci = _norm(receipt.ci_status)
    ci_ok = False
    if ci is None:
        findings.append(Finding("CI_MISSING", Severity.BLOCKER, "CI status is missing."))
        steps.append(NextStep("Attach a CI run result for the source commit.",
                              "No CI evidence was provided."))
    elif ci in _CI_FAIL:
        findings.append(Finding("CI_FAILED", Severity.BLOCKER, f"CI status is {ci!r}."))
        steps.append(NextStep("Fix failing CI and re-run the pipeline.",
                              "CI did not pass."))
    elif ci in _CI_PASS:
        ci_ok = True
    else:
        findings.append(Finding("CI_UNKNOWN", Severity.WARNING, f"Unrecognized CI status {ci!r}."))
        steps.append(NextStep("Provide a recognized CI status (success/failure).",
                              "CI status could not be interpreted."))

    # 3. Deployment state
    dep = _norm(receipt.deployment_state)
    dep_ok = False
    if dep is None:
        findings.append(Finding("DEPLOY_MISSING", Severity.WARNING, "Deployment state is missing."))
        steps.append(NextStep("Record deployment state for the release.",
                              "Deployment evidence is absent."))
    elif dep in _DEPLOY_BAD:
        findings.append(Finding("DEPLOY_NOT_LIVE", Severity.BLOCKER, f"Deployment state is {dep!r}."))
        steps.append(NextStep("Complete or roll forward the deployment.",
                              "Deployment is not in a live state."))
    elif dep in _DEPLOY_OK:
        dep_ok = True
    else:
        findings.append(Finding("DEPLOY_UNKNOWN", Severity.WARNING, f"Unrecognized deployment state {dep!r}."))

    # 4. Verifier identity separation
    ver = _norm(receipt.verifier_id)
    auth = _norm(receipt.author_id)
    verifier_ok = False
    if ver is None:
        findings.append(Finding("VERIFIER_MISSING", Severity.BLOCKER, "Verifier identity is missing."))
        steps.append(NextStep("Assign an independent verifier.",
                              "No verifier identity was recorded."))
    elif auth is not None and ver == auth:
        findings.append(Finding("VERIFIER_NOT_INDEPENDENT", Severity.BLOCKER,
                                "Verifier identity equals author identity."))
        steps.append(NextStep("Have a different party verify the evidence.",
                              "Verifier must be independent of the author."))
    else:
        verifier_ok = True

    # 5. Evidence timestamp freshness
    ts = _parse_ts(receipt.evidence_timestamp)
    now = _parse_ts(receipt.now) or datetime.now(timezone.utc)
    fresh_ok = False
    if ts is None:
        findings.append(Finding("TIMESTAMP_MISSING", Severity.BLOCKER,
                                "Evidence timestamp is missing or unparseable."))
        steps.append(NextStep("Record a valid ISO-8601 evidence timestamp.",
                              "Freshness cannot be assessed without a timestamp."))
    elif ts > now:
        findings.append(Finding("TIMESTAMP_FUTURE", Severity.BLOCKER,
                                "Evidence timestamp is in the future."))
        steps.append(NextStep("Correct the evidence timestamp.",
                              "Future timestamps are not trustworthy."))
    else:
        age = (now - ts).total_seconds()
        if age > receipt.max_age_seconds:
            findings.append(Finding("TIMESTAMP_STALE", Severity.WARNING,
                                    f"Evidence is {int(age)}s old (max {receipt.max_age_seconds}s)."))
            steps.append(NextStep("Refresh evidence with a recent run.",
                                  "Evidence exceeds the freshness window."))
        else:
            fresh_ok = True

    # Determine state
    if not commit_ok or not ci_ok:
        state = EvidenceState.CONTRADICTORY if (src and exp and src != exp) else EvidenceState.MISSING
    elif not fresh_ok:
        state = EvidenceState.STALE
    elif not dep_ok:
        state = EvidenceState.TESTED
    elif not verifier_ok:
        state = EvidenceState.DEPLOYED
    else:
        state = EvidenceState.VERIFIED

    if not steps:
        steps.append(NextStep("No action required; evidence is complete.",
                              "All provenance checks passed."))

    return Assessment(state=state, findings=tuple(findings), next_steps=tuple(steps))


def assess_many(receipts: Iterable[ReleaseReceipt]) -> list[Assessment]:
    return [assess_receipt(r) for r in receipts]


def summarize(assessments: Iterable[Assessment]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for a in assessments:
        counts[a.state.value] = counts.get(a.state.value, 0) + 1
    return counts
