"""
Portal export routes — evidence bundle + board PDF (Phase 3).
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import JSONResponse

from auth import AuthenticatedClient, require_audit_read
from database import get_audit, get_audit_by_id, get_audit_by_request_id
from export.board_pdf import render_board_pdf
from export.tle_mapper import build_export_bundle
from portal.schemas import AuditRecord


router = APIRouter(prefix="/portal", tags=["portal"])


def _tenant_audit_or_404(audit_id: int, client: AuthenticatedClient) -> dict:
    record = get_audit_by_id(audit_id)
    if record is None or record.get("tenant_id") != client.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit not found")
    return record


def _tenant_audit_by_request_or_404(request_id: str, client: AuthenticatedClient) -> dict:
    record = get_audit_by_request_id(request_id)
    if record is None or record.get("tenant_id") != client.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit not found")
    return record


@router.get("/audits", response_model=list[AuditRecord])
async def list_audits(
    client: AuthenticatedClient = Depends(require_audit_read),
    request_id: str | None = Query(default=None),
    applicant_id: str | None = Query(default=None),
    decision: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[AuditRecord]:
    rows = get_audit(
        request_id=request_id,
        applicant_id=applicant_id,
        tenant_id=client.tenant_id,
        decision=decision,
        limit=limit,
        offset=offset,
    )
    records: list[AuditRecord] = []
    for row in rows:
        row["created_at"] = datetime.fromisoformat(row["created_at"])
        records.append(AuditRecord.model_validate(row))
    return records


@router.get("/audits/{audit_id}/export")
async def export_audit_json(
    audit_id: int,
    client: AuthenticatedClient = Depends(require_audit_read),
) -> JSONResponse:
    record = _tenant_audit_or_404(audit_id, client)
    bundle = build_export_bundle(record)
    return JSONResponse(content=bundle)


@router.get("/audits/{audit_id}/export.pdf")
async def export_audit_pdf(
    audit_id: int,
    client: AuthenticatedClient = Depends(require_audit_read),
) -> Response:
    record = _tenant_audit_or_404(audit_id, client)
    bundle = build_export_bundle(record)
    pdf_bytes = render_board_pdf(bundle)
    filename = f"{bundle['tle_v1']['tle_id']}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/audits/by-request/{request_id}/export")
async def export_by_request_json(
    request_id: str,
    client: AuthenticatedClient = Depends(require_audit_read),
) -> JSONResponse:
    record = _tenant_audit_by_request_or_404(request_id, client)
    return JSONResponse(content=build_export_bundle(record))


__all__ = ["router"]
