from __future__ import annotations

import pytest

from scripts.noos_agent_feature_63350d554259 import (
    PENDING,
    REJECTED,
    VERIFIED,
    ReleaseReceipt,
    verify_release_receipt,
)

SHA = "a" * 40
OTHER_SHA = "b" * 40


def _receipt(**overrides):
    base = dict(
        commit_sha=SHA,
        environment="production",
        ci_status="success",
        deploy_status="deployed",
        verification_signal="sig-abc",
        source="github",
    )
    base.update(overrides)
    return ReleaseReceipt(**base)


def test_verified_success():
    decision = verify_release_receipt(_receipt(), SHA, "production")
    assert decision.decision == VERIFIED
    assert decision.verified is True
    assert decision.reasons == ()


def test_commit_sha_mismatch_rejected():
    decision = verify_release_receipt(_receipt(commit_sha=OTHER_SHA), SHA, "production")
    assert decision.decision == REJECTED
    assert "commit_sha_mismatch" in decision.reasons


def test_pending_release():
    decision = verify_release_receipt(
        _receipt(ci_status="pending"), SHA, "production"
    )
    assert decision.decision == PENDING
    assert "release_pending" in decision.reasons


def test_failed_ci_rejected():
    decision = verify_release_receipt(
        _receipt(ci_status="failure"), SHA, "production"
    )
    assert decision.decision == REJECTED
    assert "ci_not_successful" in decision.reasons


def test_missing_verification_signal_rejected():
    decision = verify_release_receipt(
        _receipt(verification_signal=""), SHA, "production"
    )
    assert decision.decision == REJECTED
    assert "missing_verification_signal" in decision.reasons


def test_invalid_expected_sha_rejected():
    decision = verify_release_receipt(_receipt(), "not-a-sha", "production")
    assert decision.decision == REJECTED
    assert "invalid_expected_sha" in decision.reasons


def test_environment_mismatch_rejected():
    decision = verify_release_receipt(_receipt(), SHA, "staging")
    assert decision.decision == REJECTED
    assert "environment_mismatch" in decision.reasons


def test_missing_receipt_rejected():
    decision = verify_release_receipt(None, SHA, "production")
    assert decision.decision == REJECTED
    assert "missing_receipt" in decision.reasons


def test_accepts_mapping_input():
    payload = {
        "commit_sha": SHA,
        "environment": "production",
        "ci_status": "success",
        "deploy_status": "deployed",
        "verification_signal": "sig",
        "source": "railway",
    }
    decision = verify_release_receipt(payload, SHA, "production")
    assert decision.decision == VERIFIED
    assert decision.to_dict() == {"decision": VERIFIED, "reasons": []}


def test_deploy_failed_rejected():
    decision = verify_release_receipt(
        _receipt(deploy_status="failed"), SHA, "production"
    )
    assert decision.decision == REJECTED
    assert "deploy_not_successful" in decision.reasons
