from __future__ import annotations

import math

import pytest

from scripts.noos_agent_feature_672590ebbeb6 import (
    PriorityDecision,
    WorkPacketInputs,
    rank_work_packets,
    score_work_packet,
    select_next_packet,
)


def _packet(**overrides) -> WorkPacketInputs:
    base = dict(
        packet_id="pkt-1",
        business_impact=0.5,
        urgency=0.5,
        evidence_quality=0.5,
        expected_effort=0.5,
        dependency_readiness=0.5,
        user_revenue_impact=0.5,
    )
    base.update(overrides)
    return WorkPacketInputs(**base)


def test_score_is_bounded_and_explainable():
    decision = score_work_packet(_packet())
    assert isinstance(decision, PriorityDecision)
    assert 0.0 <= decision.score <= 100.0
    assert decision.tier in {"P0", "P1", "P2", "P3", "P4"}
    assert decision.packet_id == "pkt-1"
    assert "top_driver" in decision.rationale
    assert set(decision.contributions) == {
        "business_impact",
        "urgency",
        "evidence_quality",
        "expected_effort",
        "dependency_readiness",
        "user_revenue_impact",
    }


def test_higher_impact_scores_higher_than_lower_impact():
    high = score_work_packet(_packet(business_impact=0.9, urgency=0.9))
    low = score_work_packet(_packet(business_impact=0.1, urgency=0.1))
    assert high.score > low.score


def test_higher_effort_reduces_score():
    cheap = score_work_packet(_packet(expected_effort=0.0))
    expensive = score_work_packet(_packet(expected_effort=1.0))
    assert cheap.score > expensive.score


@pytest.mark.parametrize(
    "field_name, bad_value",
    [
        ("business_impact", -0.1),
        ("urgency", 1.5),
        ("evidence_quality", float("nan")),
        ("expected_effort", float("inf")),
        ("dependency_readiness", "high"),
        ("user_revenue_impact", True),
    ],
)
def test_invalid_numbers_fail_closed(field_name, bad_value):
    with pytest.raises(ValueError):
        score_work_packet(_packet(**{field_name: bad_value}))


def test_empty_packet_id_rejected():
    with pytest.raises(ValueError):
        score_work_packet(_packet(packet_id="   "))


def test_ranking_is_deterministic_and_stable_on_ties():
    a = _packet(packet_id="b-packet")
    b = _packet(packet_id="a-packet")
    ranked = rank_work_packets([a, b])
    # Identical scores and impacts -> lexicographically smaller id first.
    assert [d.packet_id for d in ranked] == ["a-packet", "b-packet"]


def test_ranking_orders_by_score_descending():
    strong = _packet(packet_id="strong", business_impact=0.95, urgency=0.95)
    weak = _packet(packet_id="weak", business_impact=0.05, urgency=0.05)
    ranked = rank_work_packets([weak, strong])
    assert [d.packet_id for d in ranked] == ["strong", "weak"]
    assert ranked[0].score >= ranked[1].score


def test_select_next_packet_returns_none_for_empty():
    assert select_next_packet([]) is None


def test_select_next_packet_returns_top():
    strong = _packet(packet_id="strong", business_impact=0.9, urgency=0.9)
    weak = _packet(packet_id="weak", business_impact=0.1, urgency=0.1)
    chosen = select_next_packet([weak, strong])
    assert chosen is not None
    assert chosen.packet_id == "strong"


def test_deterministic_repeat_scoring():
    packet = _packet(business_impact=0.7, urgency=0.3, expected_effort=0.2)
    first = score_work_packet(packet)
    second = score_work_packet(packet)
    assert first.to_dict() == second.to_dict()


def test_rank_rejects_string_iterable():
    with pytest.raises(ValueError):
        rank_work_packets("not-a-list")
