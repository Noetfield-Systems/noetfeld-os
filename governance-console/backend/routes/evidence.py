from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import EvidenceIndex
from db.session import get_db
from schemas import EvidenceIngestRequest, EvidenceIngestResponse
from services.evidence_hash import validate_content_hash
from services.tenant_service import resolve_tenant_id

router = APIRouter(prefix="/evidence", tags=["evidence"])


@router.post("/ingest", response_model=EvidenceIngestResponse, status_code=201)
def ingest_evidence(
    body: EvidenceIngestRequest,
    db: Session = Depends(get_db),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
) -> EvidenceIngestResponse:
    tenant_id = resolve_tenant_id(x_tenant_id, db)
    try:
        content_hash = validate_content_hash(body.content_hash)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    existing = db.scalar(select(EvidenceIndex).where(EvidenceIndex.evidence_id == body.evidence_id))
    if existing is not None:
        raise HTTPException(status_code=409, detail="Duplicate evidence_id")
    ingested_at = datetime.now(timezone.utc)
    row = EvidenceIndex(
        evidence_id=body.evidence_id,
        tenant_id=tenant_id,
        source=body.source,
        title=body.title,
        content_hash=content_hash,
        sensitivity=body.sensitivity,
        retention_policy=body.retention_policy,
        storage_ref=body.storage_ref,
        ingest_mode=body.ingest_mode,
        link=body.link,
        ingested_at=ingested_at,
        metadata_json=body.metadata,
    )
    db.add(row)
    db.commit()
    return EvidenceIngestResponse(
        evidence_id=row.evidence_id,
        tenant_id=tenant_id,
        ingested_at=ingested_at,
    )
