import pytest

from scripts.noos_agent_feature_9d60ee948cb9 import (
    DeliveryAssessment,
    DeliveryEvidence,
    DeliveryState,
    assess_delivery,
    canonical_work_packet_id,
    summarize_states,
)


VALID_SHA = "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"


def test_candidate_only_with_sha():
    result = assess_delivery(DeliveryEvidence(commit_sha=VALID_SHA))
    assert result.state is DeliveryState.CANDIDATE
    assert result.commit_sha == VALID_SHA
    assert result.tests_passed is None
    assert result.is_released is False


def test_states_are_not_conflated():
    tested = assess_delivery(
        DeliveryEvidence(commit_sha=VALID_SHA, test_status="passed")
    )
    assert tested.state is DeliveryState.TESTED
    assert tested.is_released is False
    assert tested.is_deployed is False

    released = assess_delivery(
        DeliveryEvidence(commit_sha=VALID_SHA, test_status="passed", pr_ref="#42")
    )
    assert released.state is DeliveryState.RELEASED
    assert released.is_deployed is False

    deployed = assess_delivery(
        DeliveryEvidence(
            commit_sha=VALID_SHA,
            test_status="passed",
            branch="main",
            deployment_status="healthy",
        )
    )
    assert deployed.state is DeliveryState.DEPLOYED
    assert deployed.verified is False

    verified = assess_delivery(
        DeliveryEvidence(
            commit_sha=VALID_SHA,
            test_status="passed",
            branch="main",
            deployment_status="healthy",
            readback_ok=True,
        )
    )
    assert verified.state is DeliveryState.VERIFIED
    assert verified.verified is True


def test_failed_tests_block_progression():
    result = assess_delivery(
        DeliveryEvidence(
            commit_sha=VALID_SHA,
            test_status="failed",
            pr_ref="#7",
            deployment_status="healthy",
            readback_ok=True,
        )
    )
    assert result.state is DeliveryState.CANDIDATE
    assert result.tests_passed is False
    assert result.verified is False


def test_malformed_inputs_are_rejected_and_flagged():
    result = assess_delivery(
        {
            "commit_sha": "not-a-sha",
            "test_status": "maybe",
            "branch": "../evil",
            "deployment_status": "???",
            "readback_ok": "yes",
        }
    )
    assert result.state is DeliveryState.NONE
    assert result.commit_sha is None
    assert result.branch is None
    assert result.tests_passed is None
    assert result.deployed is None
    assert result.verified is False
    assert "invalid commit_sha" in result.reasons
    assert "invalid branch" in result.reasons
    assert "unrecognized test_status" in result.reasons
    assert "invalid readback_ok" in result.reasons


def test_assess_rejects_non_mapping():
    with pytest.raises(TypeError):
        assess_delivery(123)  # type: ignore[arg-type]


def test_canonical_work_packet_id_is_idempotent():
    a = canonical_work_packet_id("NOOS", "feature-9d60", "delivery")
    b = canonical_work_packet_id("  NOOS ", "feature-9d60", "delivery")
    assert a == b
    assert a.startswith("WP-")
    assert len(a) == len("WP-") + 32


def test_canonical_work_packet_id_requires_content():
    with pytest.raises(ValueError):
        canonical_work_packet_id()
    with pytest.raises(ValueError):
        canonical_work_packet_id("   ", "")
    with pytest.raises(TypeError):
        canonical_work_packet_id("ok", 5)  # type: ignore[arg-type]


def test_summarize_states_counts():
    assessments = [
        assess_delivery(DeliveryEvidence(commit_sha=VALID_SHA)),
        assess_delivery(
            DeliveryEvidence(commit_sha=VALID_SHA, test_status="passed")
        ),
        assess_delivery(DeliveryEvidence()),
    ]
    counts = summarize_states(assessments)
    assert counts["CANDIDATE"] == 1
    assert counts["TESTED"] == 1
    assert counts["NONE"] == 1
    assert counts["VERIFIED"] == 0


def test_assessment_to_dict_roundtrip_shape():
    result = assess_delivery(
        DeliveryEvidence(commit_sha=VALID_SHA, test_status="green")
    )
    payload = result.to_dict()
    assert payload["state"] == "TESTED"
    assert payload["commit_sha"] == VALID_SHA
    assert payload["tests_passed"] is True
    assert isinstance(payload["reasons"], list)
