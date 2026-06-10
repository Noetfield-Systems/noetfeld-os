from __future__ import annotations

import os

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import ConnectorRecord
from db.session import get_db
from schemas import ConnectorRegisterRequest, ConnectorResponse, ConnectorStatusResponse
from services.m365_connector_sync import ingest_m365_stub_evidence
from services.m365_oauth_stub import complete_mock_oauth, oauth_start_url, oauth_success_redirect_url
from services.tenant_service import resolve_tenant_id

router = APIRouter(prefix="/connectors", tags=["connectors"])


def _to_response(row: ConnectorRecord) -> ConnectorResponse:
    return ConnectorResponse(
        connector_id=row.connector_id,
        tenant_id=row.tenant_id,
        connector_type=row.connector_type,
        required_scopes=row.required_scopes or [],
        ingest_mode=row.ingest_mode,
        status=row.status,
        oauth_connected=bool((row.oauth_json or {}).get("connected_at")),
        created_at=row.created_at,
    )


@router.post("", response_model=ConnectorResponse, status_code=201)
def register_connector(
    body: ConnectorRegisterRequest,
    db: Session = Depends(get_db),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
) -> ConnectorResponse:
    tenant_id = resolve_tenant_id(x_tenant_id, db)
    existing = db.scalar(select(ConnectorRecord).where(ConnectorRecord.connector_id == body.connector_id))
    if existing is not None:
        raise HTTPException(status_code=409, detail="Duplicate connector_id")
    row = ConnectorRecord(
        connector_id=body.connector_id,
        tenant_id=tenant_id,
        connector_type=body.connector_type,
        required_scopes=body.required_scopes,
        ingest_mode=body.ingest_mode,
        status="registered",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_response(row)


@router.get("/{connector_id}/status", response_model=ConnectorStatusResponse)
def connector_status(
    connector_id: str,
    db: Session = Depends(get_db),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
) -> ConnectorStatusResponse:
    tenant_id = resolve_tenant_id(x_tenant_id, db)
    row = db.scalar(
        select(ConnectorRecord).where(
            ConnectorRecord.connector_id == connector_id,
            ConnectorRecord.tenant_id == tenant_id,
        )
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Connector not found")
    oauth = row.oauth_json or {}
    return ConnectorStatusResponse(
        connector_id=row.connector_id,
        status=row.status,
        oauth_connected=bool(oauth.get("connected_at")),
        last_sync=row.last_sync,
        scopes=oauth.get("scopes") or row.required_scopes or [],
    )


@router.get("/{connector_id}/oauth/start")
def oauth_start(
    connector_id: str,
    db: Session = Depends(get_db),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
) -> RedirectResponse:
    tenant_id = resolve_tenant_id(x_tenant_id, db)
    row = db.scalar(
        select(ConnectorRecord).where(
            ConnectorRecord.connector_id == connector_id,
            ConnectorRecord.tenant_id == tenant_id,
        )
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Connector not found")
    base = os.getenv("NF_PUBLIC_BASE_URL", "http://127.0.0.1:13080")
    url = oauth_start_url(connector_id, base)
    return RedirectResponse(url=url, status_code=302)


@router.get(
    "/{connector_id}/oauth/callback",
    response_model=None,
    responses={
        200: {"content": {"application/json": {}}},
        302: {"content": {"text/html": {}}, "description": "Redirect browser to workspace list"},
    },
)
def oauth_callback(
    connector_id: str,
    request: Request,
    db: Session = Depends(get_db),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
):
    tenant_id = resolve_tenant_id(x_tenant_id, db)
    row = db.scalar(
        select(ConnectorRecord).where(
            ConnectorRecord.connector_id == connector_id,
            ConnectorRecord.tenant_id == tenant_id,
        )
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Connector not found")
    try:
        complete_mock_oauth(db, row, code)
        evidence_ids = ingest_m365_stub_evidence(db, tenant_id=tenant_id, connector_id=connector_id)
        oauth = dict(row.oauth_json or {})
        oauth["last_ingested_evidence_ids"] = evidence_ids
        row.oauth_json = oauth
        db.add(row)
        db.commit()
        db.refresh(row)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    accept = (request.headers.get("accept") or "").lower()
    if "text/html" in accept and "application/json" not in accept.split(",")[0].strip():
        base = os.getenv("NF_PUBLIC_BASE_URL", "http://127.0.0.1:13080")
        return RedirectResponse(
            url=oauth_success_redirect_url(base, connector_id),
            status_code=302,
        )
    return _to_response(row)


@router.get("", response_model=list[ConnectorResponse])
def list_connectors(
    db: Session = Depends(get_db),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
) -> list[ConnectorResponse]:
    tenant_id = resolve_tenant_id(x_tenant_id, db)
    rows = db.scalars(select(ConnectorRecord).where(ConnectorRecord.tenant_id == tenant_id)).all()
    return [_to_response(r) for r in rows]
