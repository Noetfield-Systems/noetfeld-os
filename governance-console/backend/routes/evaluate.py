from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from db.models import AuditEvent
from db.session import get_db
from schemas import EvaluateRequest, EvaluateResponse
from services.governance_engine import evaluate_intent
from services.integrity import audit_integrity_hash
from services.tenant_service import resolve_tenant_id

router = APIRouter(tags=["evaluate"])


@router.post("/evaluate", response_model=EvaluateResponse)
def post_evaluate(
    body: EvaluateRequest,
    db: Session = Depends(get_db),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
) -> EvaluateResponse:
    tenant_id = resolve_tenant_id(x_tenant_id, db)
    result = evaluate_intent(
        actor=body.actor,
        action=body.action,
        context=body.context,
        metadata=body.metadata,
    )
    recorded_at = datetime.now(timezone.utc)
    payload = {
        "tenant_id": str(tenant_id),
        "rid": result.rid,
        "actor": body.actor.strip(),
        "action": body.action.strip(),
        "decision": result.decision,
        "risk_score": result.risk_score,
        "recorded_at": recorded_at.isoformat(),
    }
    row = AuditEvent(
        tenant_id=tenant_id,
        rid=result.rid,
        event_type="governance.evaluate",
        actor=body.actor.strip(),
        action=body.action.strip(),
        context=body.context,
        metadata_json=body.metadata,
        decision=result.decision,
        risk_score=result.risk_score,
        reason=result.reason,
        conditions=result.conditions,
        integrity_hash=audit_integrity_hash(payload),
        recorded_at=recorded_at,
    )
    db.add(row)
    db.commit()
    return EvaluateResponse(
        decision=result.decision,
        risk_score=result.risk_score,
        reason=result.reason,
        conditions=result.conditions,
        rid=result.rid,
        tenant_id=tenant_id,
    )
