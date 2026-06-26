"""
Health, readiness, and policy metadata endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict

from policy_meta import PolicyNotReadyError, PolicyRegistry


router = APIRouter(tags=["health"])


class PolicyMetaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_set_id: str
    rule_set_version: str
    base_policy_hash: str
    corridor_policy_hash: str
    combined_hash: str
    base_status: str
    corridor_status: str


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    service: str
    version: str
    policy: PolicyMetaResponse | None = None


class ReadinessResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ready: bool
    policy_loaded: bool
    db_ok: bool


def _policy_response() -> PolicyMetaResponse:
    meta = PolicyRegistry.meta()
    return PolicyMetaResponse(
        rule_set_id=meta.rule_set_id,
        rule_set_version=meta.rule_set_version,
        base_policy_hash=meta.base_policy_hash,
        corridor_policy_hash=meta.corridor_policy_hash,
        combined_hash=meta.combined_hash,
        base_status=meta.base_status,
        corridor_status=meta.corridor_status,
    )


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    policy: PolicyMetaResponse | None = None
    try:
        policy = _policy_response()
        gate_status = "ok"
    except PolicyNotReadyError:
        gate_status = "degraded"

    return HealthResponse(
        status=gate_status,
        service="noetfeld-os",
        version="0.3.0",
        policy=policy,
    )


@router.get("/readiness", response_model=ReadinessResponse)
async def readiness() -> ReadinessResponse:
    from database import init_db

    policy_loaded = True
    try:
        PolicyRegistry.ensure_ready()
    except PolicyNotReadyError:
        policy_loaded = False

    db_ok = True
    try:
        init_db()
    except Exception:
        db_ok = False

    ready = policy_loaded and db_ok
    if not ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=ReadinessResponse(
                ready=False,
                policy_loaded=policy_loaded,
                db_ok=db_ok,
            ).model_dump(),
        )

    return ReadinessResponse(ready=True, policy_loaded=True, db_ok=True)


@router.get("/v1/meta", response_model=PolicyMetaResponse)
async def policy_meta() -> PolicyMetaResponse:
    try:
        return _policy_response()
    except PolicyNotReadyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


__all__ = ["router"]
