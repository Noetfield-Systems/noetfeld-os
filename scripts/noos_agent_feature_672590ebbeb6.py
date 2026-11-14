from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Iterable, Mapping, Sequence


# ---------------------------------------------------------------------------
# Deterministic Company OS engineering WorkPacket priority scorer.
#
# Pure stdlib. No network, no env reads, no shell, no external writes.
# Fails closed on invalid numeric input (raises ValueError).
# Produces a bounded, explainable priority decision with stable tie-breaking.
# ---------------------------------------------------------------------------

# Bounds for each raw input dimension (all expected on a 0..1 scale).
_MIN = 0.0
_MAX = 1.0

# Weights for the positive contribution dimensions. Must sum to 1.0.
_POSITIVE_WEIGHTS: Mapping[str, float] = {
    "business_impact": 0.30,
    "urgency": 0.20,
    "evidence_quality": 0.15,
    "dependency_readiness": 0.15,
    "user_revenue_impact": 0.20,
}

# Effort is a cost dimension: higher effort reduces priority.
_EFFORT_WEIGHT = 0.25

# Final score is clamped into this band.
_SCORE_MIN = 0.0
_SCORE_MAX = 100.0

# Priority tiers, evaluated top-down against the final score.
_TIERS: Sequence[tuple[str, float]] = (
    ("P0", 80.0),
    ("P1", 60.0),
    ("P2", 40.0),
    ("P3", 20.0),
    ("P4", 0.0),
)


@dataclass(frozen=True)
class WorkPacketInputs:
    """Raw, untrusted inputs for a single work packet.

    All numeric fields are expected on a 0.0..1.0 scale.
    """

    packet_id: str
    business_impact: float
    urgency: float
    evidence_quality: float
    expected_effort: float
    dependency_readiness: float
    user_revenue_impact: float

    def as_dimension_map(self) -> dict[str, float]:
        return {
            "business_impact": self.business_impact,
            "urgency": self.urgency,
            "evidence_quality": self.evidence_quality,
            "expected_effort": self.expected_effort,
            "dependency_readiness": self.dependency_readiness,
            "user_revenue_impact": self.user_revenue_impact,
        }


@dataclass(frozen=True)
class PriorityDecision:
    """Explainable, bounded priority decision for a work packet."""

    packet_id: str
    score: float
    tier: str
    contributions: Mapping[str, float] = field(default_factory=dict)
    rationale: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "packet_id": self.packet_id,
            "score": self.score,
            "tier": self.tier,
            "contributions": dict(self.contributions),
            "rationale": self.rationale,
        }


def _validate_number(name: str, value: object) -> float:
    """Validate a single numeric input, failing closed on bad values."""
    if isinstance(value, bool):
        # bool is a subclass of int; reject it explicitly.
        raise ValueError(f"{name} must be a number, not bool")
    if not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number, got {type(value).__name__}")
    fvalue = float(value)
    if math.isnan(fvalue) or math.isinf(fvalue):
        raise ValueError(f"{name} must be finite, got {value!r}")
    if fvalue < _MIN or fvalue > _MAX:
        raise ValueError(f"{name} must be within [{_MIN}, {_MAX}], got {fvalue}")
    return fvalue


def _validate_packet_id(packet_id: object) -> str:
    if not isinstance(packet_id, str):
        raise ValueError("packet_id must be a string")
    stripped = packet_id.strip()
    if not stripped:
        raise ValueError("packet_id must be a non-empty string")
    return stripped


def _tier_for_score(score: float) -> str:
    for tier, threshold in _TIERS:
        if score >= threshold:
            return tier
    return _TIERS[-1][0]


def score_work_packet(inputs: WorkPacketInputs) -> PriorityDecision:
    """Score a single work packet deterministically.

    Raises ValueError on any invalid input (fail closed).
    """
    if not isinstance(inputs, WorkPacketInputs):
        raise ValueError("inputs must be a WorkPacketInputs instance")

    packet_id = _validate_packet_id(inputs.packet_id)
    dims = inputs.as_dimension_map()
    validated = {name: _validate_number(name, value) for name, value in dims.items()}

    contributions: dict[str, float] = {}
    positive_total = 0.0
    for name, weight in _POSITIVE_WEIGHTS.items():
        contribution = validated[name] * weight
        contributions[name] = round(contribution, 6)
        positive_total += contribution

    effort_penalty = validated["expected_effort"] * _EFFORT_WEIGHT
    contributions["expected_effort"] = round(-effort_penalty, 6)

    raw = positive_total - effort_penalty
    # raw is bounded in [-0.25, 0.75]; map to [0, 100].
    normalized = (raw + _EFFORT_WEIGHT) / (1.0 + _EFFORT_WEIGHT)
    score = round(max(_SCORE_MIN, min(_SCORE_MAX, normalized * _SCORE_MAX)), 4)

    tier = _tier_for_score(score)
    rationale = _build_rationale(validated, contributions, score, tier)

    return PriorityDecision(
        packet_id=packet_id,
        score=score,
        tier=tier,
        contributions=contributions,
        rationale=rationale,
    )


def _build_rationale(
    validated: Mapping[str, float],
    contributions: Mapping[str, float],
    score: float,
    tier: str,
) -> str:
    drivers = sorted(
        (name for name in _POSITIVE_WEIGHTS),
        key=lambda n: (-contributions[n], n),
    )
    top = drivers[0]
    return (
        f"tier={tier} score={score:.4f}; "
        f"top_driver={top} (contribution={contributions[top]:.4f}); "
        f"effort_penalty={contributions['expected_effort']:.4f}"
    )


def rank_work_packets(
    packets: Iterable[WorkPacketInputs],
) -> list[PriorityDecision]:
    """Score and rank packets by descending score with stable tie-breaking.

    Tie-break order (deterministic):
      1. higher score
      2. higher business_impact
      3. higher urgency
      4. lexicographically smaller packet_id
    """
    if isinstance(packets, (str, bytes)):
        raise ValueError("packets must be an iterable of WorkPacketInputs")

    decisions: list[tuple[PriorityDecision, WorkPacketInputs]] = []
    for packet in packets:
        decision = score_work_packet(packet)
        decisions.append((decision, packet))

    def sort_key(item: tuple[PriorityDecision, WorkPacketInputs]) -> tuple:
        decision, packet = item
        return (
            -decision.score,
            -float(packet.business_impact),
            -float(packet.urgency),
            decision.packet_id,
        )

    decisions.sort(key=sort_key)
    return [decision for decision, _ in decisions]


def select_next_packet(
    packets: Iterable[WorkPacketInputs],
) -> PriorityDecision | None:
    """Return the single highest-priority packet, or None if empty."""
    ranked = rank_work_packets(packets)
    return ranked[0] if ranked else None
