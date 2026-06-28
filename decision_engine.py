"""
Decision engine for NOETFELD OS.

Coordinates policy evaluation, risk modelling, and audit persistence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping
from uuid import uuid4

from auth import AuthenticatedClient
from config import (
    DECISION_APPROVE,
    DECISION_DECLINE,
    DECISION_REVIEW,
    DECISION_APPROVE_THRESHOLD,
    DECISION_REVIEW_THRESHOLD,
)
from database import get_audit_by_request_id, insert_audit
from exceptions import DuplicateRequestError, PolicyGateError
from policy_meta import PolicyMeta, PolicyRegistry
from risk_model import engineer_features, score


@dataclass(frozen=True)
class DecisionProvenance:
    policy_decision: str
    corridor_decision: str | None
    corridor_breaches: list[str]
    final_source: str


@dataclass(frozen=True)
class DecisionResult:
    request_id: str
    applicant_id: str
    tenant_id: str
    decision: str
    composite_score: float
    score_breakdown: dict[str, float]
    policy_decision: str
    corridor_decision: str | None
    corridor_breaches: list[str]
    rule_set_id: str
    rule_set_version: str
    policy_base_hash: str
    policy_corridor_hash: str
    provenance: DecisionProvenance
    audit_id: int
    correlation_id: str | None = None


def _apply_policy(composite_score: float, meta: PolicyMeta) -> str:
    approve_threshold = meta.base_policy.approve_threshold or DECISION_APPROVE_THRESHOLD
    review_threshold = meta.base_policy.review_threshold or DECISION_REVIEW_THRESHOLD

    if composite_score >= approve_threshold:
        return DECISION_APPROVE
    if composite_score >= review_threshold:
        return DECISION_REVIEW
    return DECISION_DECLINE


def _apply_corridors(
    metrics: dict[str, float], meta: PolicyMeta
) -> tuple[str | None, list[str]]:
    breaches = meta.corridor_policy.find_breaches(metrics)
    if not breaches:
        return None, []

    decisions = {b.on_breach_decision for b in breaches}
    if DECISION_DECLINE in decisions:
        final = DECISION_DECLINE
    else:
        final = DECISION_REVIEW
    return final, [b.name for b in breaches]


def _canonical_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    return dict(payload)


def _result_from_audit(record: dict[str, Any]) -> DecisionResult:
    provenance = DecisionProvenance(
        policy_decision=str(record["policy_decision"]),
        corridor_decision=record.get("corridor_decision"),
        corridor_breaches=list(record.get("corridor_breaches") or []),
        final_source="corridor" if record.get("corridor_decision") else "policy",
    )
    return DecisionResult(
        request_id=str(record["request_id"]),
        applicant_id=str(record["applicant_id"]),
        tenant_id=str(record.get("tenant_id", "unknown")),
        decision=str(record["decision"]),
        composite_score=float(record["composite_score"]),
        score_breakdown=dict(record["score_breakdown"]),
        policy_decision=str(record["policy_decision"]),
        corridor_decision=record.get("corridor_decision"),
        corridor_breaches=list(record.get("corridor_breaches") or []),
        rule_set_id=str(record.get("rule_set_id", "unknown")),
        rule_set_version=str(record.get("rule_set_version", "0.0.0")),
        policy_base_hash=str(record.get("policy_base_hash") or ""),
        policy_corridor_hash=str(record.get("policy_corridor_hash") or ""),
        provenance=provenance,
        audit_id=int(record["id"]),
        correlation_id=record.get("correlation_id"),
    )


def decide(
    payload: Mapping[str, Any],
    *,
    applicant_id: str,
    client: AuthenticatedClient,
    request_id: str | None = None,
    correlation_id: str | None = None,
    rule_set_version: str | None = None,
) -> DecisionResult:
    try:
        meta = PolicyRegistry.ensure_ready()
    except Exception as exc:
        raise PolicyGateError(str(exc)) from exc

    if rule_set_version is not None and rule_set_version != meta.rule_set_version:
        raise PolicyGateError(
            f"Requested rule_set_version {rule_set_version!r} "
            f"does not match active {meta.rule_set_version!r}"
        )

    resolved_request_id = request_id or str(uuid4())
    canonical = _canonical_payload(payload)

    existing = get_audit_by_request_id(
        resolved_request_id,
        tenant_id=client.tenant_id,
    )
    if existing is not None:
        existing_inputs = {
            k: v
            for k, v in existing["input_payload"].items()
            if k not in ("applicant_id", "engineered_features")
        }
        new_inputs = {k: v for k, v in canonical.items() if k != "applicant_id"}
        if existing_inputs != new_inputs:
            raise DuplicateRequestError(
                f"request_id {resolved_request_id!r} already used with different payload"
            )
        return _result_from_audit(existing)

    features = engineer_features(payload)
    risk_result = score(features)

    metrics: dict[str, float] = {
        "dti_ratio": features.dti_ratio,
        "ltv_ratio": features.ltv_ratio,
    }
    corridor_decision, corridor_breaches = _apply_corridors(metrics, meta)
    policy_decision = _apply_policy(risk_result.composite_score, meta)

    if corridor_decision is not None:
        final_decision = corridor_decision
        final_source = "corridor"
    else:
        final_decision = policy_decision
        final_source = "policy"

    audit_payload = {**canonical, "engineered_features": metrics}

    audit_id = insert_audit(
        request_id=resolved_request_id,
        applicant_id=applicant_id,
        tenant_id=client.tenant_id,
        decision=final_decision,
        composite_score=risk_result.composite_score,
        input_payload=audit_payload,
        score_breakdown=risk_result.scores,
        policy_decision=policy_decision,
        corridor_decision=corridor_decision,
        corridor_breaches=corridor_breaches,
        rule_set_id=meta.rule_set_id,
        rule_set_version=meta.rule_set_version,
        policy_base_hash=meta.base_policy_hash,
        policy_corridor_hash=meta.corridor_policy_hash,
        api_key_id=client.key_id,
        correlation_id=correlation_id,
        notes=None,
    )

    provenance = DecisionProvenance(
        policy_decision=policy_decision,
        corridor_decision=corridor_decision,
        corridor_breaches=corridor_breaches,
        final_source=final_source,
    )

    return DecisionResult(
        request_id=resolved_request_id,
        applicant_id=applicant_id,
        tenant_id=client.tenant_id,
        decision=final_decision,
        composite_score=risk_result.composite_score,
        score_breakdown=risk_result.scores,
        policy_decision=policy_decision,
        corridor_decision=corridor_decision,
        corridor_breaches=corridor_breaches,
        rule_set_id=meta.rule_set_id,
        rule_set_version=meta.rule_set_version,
        policy_base_hash=meta.base_policy_hash,
        policy_corridor_hash=meta.corridor_policy_hash,
        provenance=provenance,
        audit_id=audit_id,
        correlation_id=correlation_id,
    )


def result_from_audit(record: dict[str, Any]) -> DecisionResult:
    return _result_from_audit(record)


__all__ = ["DecisionProvenance", "DecisionResult", "decide", "result_from_audit"]
