from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.models import AuditLog
from db.session import get_db
from schemas import EvaluateRequest, EvaluateResponse
from services.governance_engine import evaluate_intent

router = APIRouter(tags=["evaluate"])


@router.post("/evaluate", response_model=EvaluateResponse)
def post_evaluate(body: EvaluateRequest, db: Session = Depends(get_db)) -> EvaluateResponse:
    result = evaluate_intent(
        actor=body.actor,
        action=body.action,
        context=body.context,
        metadata=body.metadata,
    )
    row = AuditLog(
        rid=result.rid,
        actor=body.actor.strip(),
        action=body.action.strip(),
        context=body.context,
        metadata_json=body.metadata,
        decision=result.decision,
        risk_score=result.risk_score,
        reason=result.reason,
        conditions=result.conditions,
    )
    db.add(row)
    db.commit()
    return EvaluateResponse(
        decision=result.decision,
        risk_score=result.risk_score,
        reason=result.reason,
        conditions=result.conditions,
        rid=result.rid,
    )
