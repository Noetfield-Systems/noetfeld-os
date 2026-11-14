import pytest

from scripts.noos_agent_feature_fd121b584b9d import (
    Assessment,
    EvidenceState,
    ReleaseReceipt,
    Severity,
    assess_many,
    assess_receipt,
    summarize,
)

NOW = "2026-06-15T12:00:00Z"


def _good(**overrides):
    base = dict(
        source_commit="abc123",
        expected_commit="abc123",
        ci_status="success",
        deployment_state="deployed",
        verifier_id="verifier-1",
        author_id="author-1",
        evidence_timestamp="2026-06-15T11:00:00Z",
        now=NOW,
    )
    base.update(overrides)
    return ReleaseReceipt(**base)


def test_successful_evidence_is_verified():
    result = assess_receipt(_good())
    assert result.state is EvidenceState.VERIFIED
    assert result.is_release_ready is True
    assert not any(f.severity is Severity.BLOCKER for f in result.findings)


def test_contradictory_commit_is_flagged():
    result = assess_receipt(_good(source_commit="deadbeef"))
    assert result.state is EvidenceState.CONTRADICTORY
    assert result.is_release_ready is False
    codes = {f.code for f in result.findings}
    assert "COMMIT_MISMATCH" in codes
    assert any("commit" in s.action.lower() for s in result.next_steps)


def test_missing_ci_is_missing_state():
    result = assess_receipt(_good(ci_status=None))
    assert result.state is EvidenceState.MISSING
    assert any(f.code == "CI_MISSING" for f in result.findings)


def test_stale_evidence_is_stale():
    result = assess_receipt(_good(evidence_timestamp="2026-06-10T00:00:00Z"))
    assert result.state is EvidenceState.STALE
    assert any(f.code == "TIMESTAMP_STALE" for f in result.findings)


def test_tested_but_not_deployed():
    result = assess_receipt(_good(deployment_state="pending"))
    assert result.state is EvidenceState.TESTED
    assert result.is_release_ready is False


def test_deployed_but_verifier_not_independent():
    result = assess_receipt(_good(verifier_id="author-1"))
    assert result.state is EvidenceState.DEPLOYED
    assert any(f.code == "VERIFIER_NOT_INDEPENDENT" for f in result.findings)


def test_future_timestamp_is_blocker():
    result = assess_receipt(_good(evidence_timestamp="2026-06-16T00:00:00Z"))
    assert any(f.code == "TIMESTAMP_FUTURE" for f in result.findings)
    assert result.is_release_ready is False


def test_summarize_counts():
    results = assess_many([_good(), _good(ci_status="failure"), _good(deployment_state="pending")])
    counts = summarize(results)
    assert counts.get("VERIFIED") == 1
    assert counts.get("TESTED") == 1
    assert sum(counts.values()) == 3
