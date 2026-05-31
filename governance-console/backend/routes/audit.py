from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import AuditLog
from db.session import get_db
from schemas import AuditRecord

router = APIRouter(tags=["audit"])


def _to_record(row: AuditLog) -> AuditRecord:
    return AuditRecord(
        id=row.id,
        rid=row.rid,
        actor=row.actor,
        action=row.action,
        context=row.context,
        metadata=row.metadata_json or {},
        decision=row.decision,
        risk_score=row.risk_score,
        reason=row.reason or [],
        conditions=row.conditions or [],
        timestamp=row.created_at,
    )


@router.get("/audit", response_model=list[AuditRecord])
def list_audit(
    db: Session = Depends(get_db),
    q: str | None = Query(None, description="Search RID substring"),
    limit: int = Query(100, ge=1, le=500),
) -> list[AuditRecord]:
    stmt = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    if q:
        stmt = stmt.where(AuditLog.rid.ilike(f"%{q.strip()}%"))
    rows = db.scalars(stmt).all()
    return [_to_record(r) for r in rows]


@router.get("/audit/{rid}", response_model=AuditRecord)
def get_audit(rid: str, db: Session = Depends(get_db)) -> AuditRecord:
    normalized = rid.strip().upper()
    row = db.scalar(select(AuditLog).where(AuditLog.rid == normalized))
    if row is None:
        raise HTTPException(status_code=404, detail=f"No audit record for {rid}")
    return _to_record(row)
