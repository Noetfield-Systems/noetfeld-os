from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.models import SandboxSession
from db.session import get_db
from schemas import SandboxSessionCreate, SandboxSessionPatch, SandboxSessionResponse

router = APIRouter(prefix="/api/v1/sandbox", tags=["sandbox"])

LIMIT_EVALUATES = 50
TRIAL_DAYS = 14


def _new_tenant_id() -> str:
    return "sandbox-" + secrets.token_hex(4)


def _to_response(row: SandboxSession) -> SandboxSessionResponse:
    return SandboxSessionResponse(
        session_id=row.session_id,
        email=row.email,
        org=row.org,
        tenant_id=row.tenant_id,
        api_key_preview=row.api_key_preview,
        mode=row.mode,
        evaluates_used=row.evaluates_used,
        evaluates_limit=row.evaluates_limit,
        trial_step=row.trial_step,
        m365_connected=row.m365_connected,
        created_at=row.created_at,
        expires_at=row.expires_at,
    )


def _get_session_or_404(session_id: uuid.UUID, db: Session) -> SandboxSession:
    row = db.get(SandboxSession, session_id)
    if row is None:
        raise HTTPException(status_code=404, detail="session not found")
    expires = row.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="session expired")
    return row


@router.post("/sessions", response_model=SandboxSessionResponse, status_code=201)
def create_session(body: SandboxSessionCreate, db: Session = Depends(get_db)) -> SandboxSessionResponse:
    now = datetime.now(timezone.utc)
    row = SandboxSession(
        email=body.email.strip(),
        org=(body.org or "Sandbox org").strip() or "Sandbox org",
        tenant_id=_new_tenant_id(),
        api_key_preview="nf_sbx_" + secrets.token_hex(4),
        evaluates_limit=LIMIT_EVALUATES,
        expires_at=now + timedelta(days=TRIAL_DAYS),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_response(row)


@router.get("/sessions/{session_id}", response_model=SandboxSessionResponse)
def get_session(session_id: uuid.UUID, db: Session = Depends(get_db)) -> SandboxSessionResponse:
    return _to_response(_get_session_or_404(session_id, db))


@router.patch("/sessions/{session_id}", response_model=SandboxSessionResponse)
def patch_session(
    session_id: uuid.UUID,
    body: SandboxSessionPatch,
    db: Session = Depends(get_db),
) -> SandboxSessionResponse:
    row = _get_session_or_404(session_id, db)
    if body.increment_evaluate:
        row.evaluates_used = min(row.evaluates_limit, row.evaluates_used + 1)
        row.trial_step = max(row.trial_step, 4)
    if body.evaluates_used is not None:
        row.evaluates_used = min(row.evaluates_limit, body.evaluates_used)
    if body.trial_step is not None:
        row.trial_step = max(row.trial_step, body.trial_step)
    if body.m365_connected is not None:
        row.m365_connected = body.m365_connected
    db.commit()
    db.refresh(row)
    return _to_response(row)
