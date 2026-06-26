"""
FastAPI router exposing the core decisioning API (Phase 2).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field

from auth import AuthenticatedClient, require_decision_write
from decision_engine import DecisionProvenance, DecisionResult, decide
from exceptions import DuplicateRequestError, GateError, PolicyGateError


router = APIRouter(prefix="/v1", tags=["decisioning"])


class DecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    applicant_id: str = Field(..., description="Opaque applicant identifier")
    credit_score: int = Field(..., ge=300, le=850)
    monthly_debt: float = Field(..., ge=0)
    monthly_income: float = Field(..., gt=0)
    loan_amount: float = Field(..., gt=0)
    collateral_value: float = Field(..., gt=0)
    employment_history_years: float = Field(..., ge=0)
    liquid_reserves_months: float = Field(..., ge=0)
    request_id: str | None = Field(
        default=None,
        description="Optional idempotency key; server generates UUID if omitted",
    )
    correlation_id: str | None = Field(
        default=None,
        description="Optional client trace correlation id",
    )
    rule_set_version: str | None = Field(
        default=None,
        description="Must match active policy pack version when supplied",
    )


class DecisionProvenanceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    policy_decision: str
    corridor_decision: str | None
    corridor_breaches: list[str]
    final_source: str


class PolicyHashesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    base: str
    corridor: str
    combined: str


class DecisionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

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
    policy_hashes: PolicyHashesResponse
    provenance: DecisionProvenanceResponse
    audit_id: int
    correlation_id: str | None = None


def _to_response(result: DecisionResult) -> DecisionResponse:
    combined = f"{result.policy_base_hash}:{result.policy_corridor_hash}"
    return DecisionResponse(
        request_id=result.request_id,
        applicant_id=result.applicant_id,
        tenant_id=result.tenant_id,
        decision=result.decision,
        composite_score=result.composite_score,
        score_breakdown=result.score_breakdown,
        policy_decision=result.policy_decision,
        corridor_decision=result.corridor_decision,
        corridor_breaches=result.corridor_breaches,
        rule_set_id=result.rule_set_id,
        rule_set_version=result.rule_set_version,
        policy_hashes=PolicyHashesResponse(
            base=result.policy_base_hash,
            corridor=result.policy_corridor_hash,
            combined=combined,
        ),
        provenance=DecisionProvenanceResponse(
            policy_decision=result.provenance.policy_decision,
            corridor_decision=result.provenance.corridor_decision,
            corridor_breaches=result.provenance.corridor_breaches,
            final_source=result.provenance.final_source,
        ),
        audit_id=result.audit_id,
        correlation_id=result.correlation_id,
    )


@router.post("/decision", response_model=DecisionResponse)
async def create_decision(
    payload: DecisionRequest,
    response: Response,
    client: AuthenticatedClient = Depends(require_decision_write),
) -> DecisionResponse:
    body = payload.model_dump(
        exclude={"request_id", "correlation_id", "rule_set_version"},
    )
    try:
        result = decide(
            payload=body,
            applicant_id=payload.applicant_id,
            client=client,
            request_id=payload.request_id,
            correlation_id=payload.correlation_id,
            rule_set_version=payload.rule_set_version,
        )
    except DuplicateRequestError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message) from exc
    except PolicyGateError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=exc.message) from exc
    except GateError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=exc.message) from exc

    response.headers["X-Request-ID"] = result.request_id
    return _to_response(result)


@router.get("/decision/{request_id}", response_model=DecisionResponse)
async def get_decision(
    request_id: str,
    client: AuthenticatedClient = Depends(require_decision_write),
) -> DecisionResponse:
    from database import get_audit_by_request_id

    record = get_audit_by_request_id(request_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found")
    if record.get("tenant_id") != client.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found")

    from decision_engine import result_from_audit

    return _to_response(result_from_audit(record))


__all__ = ["router", "DecisionRequest", "DecisionResponse"]
