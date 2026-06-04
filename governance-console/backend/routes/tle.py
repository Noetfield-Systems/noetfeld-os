from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import HTMLResponse, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import TleEntry
from db.session import get_db
from schemas import TleApproveRequest, TleDetail, TleDraftRequest, TleSummary
from services.board_pack_pdf import render_board_pack_pdf
from services.rbac import can_approve_tle, resolve_workspace_role
from services.tenant_service import resolve_tenant_id
from services.tle_service import approve_step, board_pack_export, draft_from_evaluate

router = APIRouter(prefix="/tle", tags=["tle"])


def _to_summary(row: TleEntry) -> TleSummary:
    doc = row.document_json or {}
    return TleSummary(
        tle_id=row.tle_id,
        status=row.status,
        decision=str(doc.get("decision", "")),
        confidence_score=row.confidence_score,
        date=str(doc.get("date", "")),
        source_rid=row.source_rid,
        created_at=row.created_at,
    )


def _to_detail(row: TleEntry) -> TleDetail:
    return TleDetail(
        tle_id=row.tle_id,
        tenant_id=row.tenant_id,
        status=row.status,
        confidence_score=row.confidence_score,
        audit_digest=row.audit_digest,
        created_at=row.created_at,
        finalized_at=row.finalized_at,
        document=row.document_json,
    )


@router.post("/draft", response_model=TleDetail, status_code=201)
def create_draft(
    body: TleDraftRequest,
    db: Session = Depends(get_db),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
) -> TleDetail:
    tenant_id = resolve_tenant_id(x_tenant_id, db)
    try:
        row = draft_from_evaluate(
            db,
            tenant_id=tenant_id,
            source_rid=body.source_rid,
            evidence_ids=body.evidence_ids,
            owner=body.owner,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _to_detail(row)


@router.get("", response_model=list[TleSummary])
def list_tles(
    db: Session = Depends(get_db),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
    q: str | None = None,
    status: str | None = None,
) -> list[TleSummary]:
    tenant_id = resolve_tenant_id(x_tenant_id, db)
    rows = db.scalars(
        select(TleEntry).where(TleEntry.tenant_id == tenant_id).order_by(TleEntry.created_at.desc())
    ).all()
    out = [_to_summary(r) for r in rows]
    if status:
        st = status.strip().lower()
        out = [s for s in out if s.status.lower() == st]
    if q and q.strip():
        needle = q.strip().lower()
        out = [
            s
            for s in out
            if needle in s.tle_id.lower()
            or needle in s.decision.lower()
            or needle in s.status.lower()
            or (s.source_rid and needle in s.source_rid.lower())
            or needle in s.date
        ]
    return out


@router.get("/{tle_id}", response_model=TleDetail)
def get_tle(
    tle_id: str,
    db: Session = Depends(get_db),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
) -> TleDetail:
    tenant_id = resolve_tenant_id(x_tenant_id, db)
    row = db.scalar(select(TleEntry).where(TleEntry.tle_id == tle_id, TleEntry.tenant_id == tenant_id))
    if row is None:
        raise HTTPException(status_code=404, detail="TLE not found")
    return _to_detail(row)


@router.post("/{tle_id}/approve", response_model=TleDetail)
def approve_tle(
    tle_id: str,
    body: TleApproveRequest,
    db: Session = Depends(get_db),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
    x_role: str | None = Header(default=None, alias="X-Role"),
) -> TleDetail:
    role = resolve_workspace_role(x_role)
    if not can_approve_tle(role):
        raise HTTPException(status_code=403, detail="Approver role required")
    tenant_id = resolve_tenant_id(x_tenant_id, db)
    try:
        row = approve_step(
            db,
            tle_id=tle_id,
            tenant_id=tenant_id,
            approver_id=body.approver_id,
            decision=body.decision,
            conditions=body.conditions,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _to_detail(row)


@router.get("/{tle_id}/export", response_model=None)
def export_tle(
    tle_id: str,
    db: Session = Depends(get_db),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
    format: str = "json",
) -> dict | HTMLResponse | Response:
    tenant_id = resolve_tenant_id(x_tenant_id, db)
    row = db.scalar(select(TleEntry).where(TleEntry.tle_id == tle_id, TleEntry.tenant_id == tenant_id))
    if row is None:
        raise HTTPException(status_code=404, detail="TLE not found")
    pack = board_pack_export(row)
    if format == "pdf":
        pdf_bytes = render_board_pack_pdf(row)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{row.tle_id}-board-pack.pdf"'},
        )
    if format == "html":
        doc = pack["document"]
        html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/><title>Board Pack — {row.tle_id}</title>
<style>body{{font-family:system-ui;max-width:720px;margin:2rem auto;padding:0 1rem}}
h1{{font-size:1.25rem}}.meta{{color:#555;font-size:.9rem}}</style></head><body>
<h1>Trust Ledger Board Pack</h1>
<p class="meta">{row.tle_id} · {row.status} · confidence {row.confidence_score:.2f}</p>
<p><strong>Decision:</strong> {doc.get("decision")}</p>
<p><strong>Digest:</strong> {row.audit_digest or "pending"}</p>
<h2>Evidence ({pack["evidence_count"]})</h2>
<ul>{"".join(f"<li>{e.get('title')} ({e.get('source')})</li>" for e in doc.get("evidence", []))}</ul>
</body></html>"""
        return HTMLResponse(content=html)
    return pack
