from __future__ import annotations

import secrets
from dataclasses import dataclass
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class GovernanceDecision:
    decision: str
    risk_score: int
    reason: list[str]
    conditions: list[str]
    rid: str


def generate_rid() -> str:
    suffix = secrets.token_hex(4).upper()
    return f"RID-{uuid4().hex[:8].upper()}-{suffix}"


def evaluate_intent(
    *,
    actor: str,
    action: str,
    context: str,
    metadata: dict[str, Any] | None = None,
) -> GovernanceDecision:
    """Deterministic v1 governance rules — no AI, no execution logic."""
    reasons: list[str] = []
    conditions: list[str] = []
    score = 10

    actor_clean = (actor or "").strip()
    action_clean = (action or "").strip().lower()
    context_clean = (context or "").strip().lower()
    meta = metadata or {}

    if not actor_clean:
        return GovernanceDecision(
            decision="deny",
            risk_score=100,
            reason=["Actor is required for any governed action."],
            conditions=["Provide a non-empty actor identifier."],
            rid=generate_rid(),
        )

    if "transfer" in action_clean or "payment" in action_clean or "withdraw" in action_clean:
        score += 35
        reasons.append("Action suggests value movement — elevated pre-execution scrutiny.")

    if "unknown" in context_clean or "unverified" in context_clean:
        score += 25
        reasons.append("Context contains unverified or unknown signals.")

    if len(context_clean) < 12:
        score += 15
        reasons.append("Context is minimal — insufficient operational detail for STP.")

    if meta.get("high_risk") is True:
        score += 20
        reasons.append("Metadata flagged high_risk=true.")

    if meta.get("pii_exposure") is True:
        score += 15
        reasons.append("Metadata flagged pii_exposure=true.")
        conditions.append("Human review required before Copilot or agent execution.")

    score = min(100, max(0, score))

    if score >= 70:
        decision = "deny"
        if not reasons:
            reasons.append("Risk score exceeds deny threshold.")
        conditions.append("Remediate policy gaps before retrying evaluate.")
    elif score >= 40:
        decision = "review"
        if not reasons:
            reasons.append("Risk score requires human review.")
        conditions.append("Route to compliance owner with RID attached.")
    else:
        decision = "allow"
        reasons.append("Intent within default policy tolerance for shadow evaluation.")
        conditions.append("External systems may proceed only under your institution's execution authority.")

    return GovernanceDecision(
        decision=decision,
        risk_score=score,
        reason=reasons,
        conditions=conditions,
        rid=generate_rid(),
    )
