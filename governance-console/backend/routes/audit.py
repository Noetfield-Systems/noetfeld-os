from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import AuditEvent
from db.session import get_db
from schemas import AuditExportBundle, AuditRecord
from services.tenant_service import resolve_tenant_id

router = APIRouter(tags=["audit"])


def _to_record(row: AuditEvent) -> AuditRecord:
    return AuditRecord(
        id=row.event_id,
        tenant_id=row.tenant_id,
        rid=row.rid,
        actor=row.actor,
        action=row.action,
        context=row.context,
        metadata=row.metadata_json or {},
        decision=row.decision,
        risk_score=row.risk_score,
        reason=row.reason or [],
        conditions=row.conditions or [],
        integrity_hash=row.integrity_hash,
        timestamp=row.recorded_at,
    )


@router.get("/audit", response_model=list[AuditRecord])
def list_audit(
    db: Session = Depends(get_db),
    q: str | None = Query(None, description="Search RID substring"),
    limit: int = Query(100, ge=1, le=500),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
) -> list[AuditRecord]:
    tenant_id = resolve_tenant_id(x_tenant_id, db)
    stmt = (
        select(AuditEvent)
        .where(AuditEvent.tenant_id == tenant_id)
        .order_by(AuditEvent.recorded_at.desc())
        .limit(limit)
    )
    if q:
        stmt = stmt.where(AuditEvent.rid.ilike(f"%{q.strip()}%"))
    rows = db.scalars(stmt).all()
    return [_to_record(r) for r in rows]


@router.get("/audit/export", response_model=AuditExportBundle)
def export_audit(
    db: Session = Depends(get_db),
    limit: int = Query(500, ge=1, le=2000),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
) -> AuditExportBundle:
    tenant_id = resolve_tenant_id(x_tenant_id, db)
    rows = db.scalars(
        select(AuditEvent)
        .where(AuditEvent.tenant_id == tenant_id)
        .order_by(AuditEvent.recorded_at.asc())
        .limit(limit)
    ).all()
    records = [_to_record(r) for r in rows]
    return AuditExportBundle(
        tenant_id=tenant_id,
        exported_at=datetime.now(timezone.utc),
        event_count=len(records),
        events=records,
    )


@router.get("/audit/{rid}", response_model=AuditRecord)
def get_audit(
    rid: str,
    db: Session = Depends(get_db),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
) -> AuditRecord:
    tenant_id = resolve_tenant_id(x_tenant_id, db)
    normalized = rid.strip().upper()
    row = db.scalar(
        select(AuditEvent).where(
            AuditEvent.tenant_id == tenant_id,
            AuditEvent.rid == normalized,
        )
    )
    if row is None:
        raise HTTPException(status_code=404, detail=f"No audit record for {rid}")
    return _to_record(row)
