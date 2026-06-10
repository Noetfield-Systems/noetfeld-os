from __future__ import annotations

import os
import secrets
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from db.models import ConnectorRecord


def oauth_start_url(connector_id: str, base_url: str) -> str:
    state = secrets.token_urlsafe(16)
    return f"{base_url.rstrip('/')}/connectors/{connector_id}/oauth/callback?state={state}&code=dev-mock"


def oauth_success_redirect_url(base_url: str, connector_id: str) -> str:
    return f"{base_url.rstrip('/')}/workspace?connected={connector_id}"


def complete_mock_oauth(db: Session, row: ConnectorRecord, code: str | None) -> ConnectorRecord:
    mock_token = os.getenv("NF_M365_MOCK_TOKEN", "dev-mock-token-do-not-use-in-prod")
    if code and code != "dev-mock" and not os.getenv("NF_M365_ALLOW_ANY_CODE"):
        raise ValueError("Invalid OAuth code (dev: use code=dev-mock)")
    row.oauth_json = {
        "provider": "m365",
        "access_token_ref": "env:NF_M365_MOCK_TOKEN",
        "token_preview": mock_token[:8] + "…",
        "connected_at": datetime.now(timezone.utc).isoformat(),
        "scopes": row.required_scopes or [],
    }
    row.status = "connected"
    row.last_sync = datetime.now(timezone.utc)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
