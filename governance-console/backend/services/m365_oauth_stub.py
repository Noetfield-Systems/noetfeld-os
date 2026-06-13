from __future__ import annotations

import os
import secrets
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from db.models import ConnectorRecord


class ConnectorEnvError(Exception):
    """Required M365 connector environment variables are missing."""


def _is_non_local_base() -> bool:
    raw = os.getenv("NF_PUBLIC_BASE_URL", "").strip()
    if not raw:
        return False
    lower = raw.lower()
    return "localhost" not in lower and "127.0.0.1" not in lower


def _strict_connector_env() -> bool:
    if os.getenv("NF_M365_REQUIRE_ENV", "0").strip() == "1":
        return True
    return _is_non_local_base()


def ensure_m365_connector_env() -> None:
    if not _strict_connector_env():
        return
    missing: list[str] = []
    if not os.getenv("NF_M365_MOCK_TOKEN", "").strip():
        missing.append("NF_M365_MOCK_TOKEN")
    if os.getenv("NF_M365_REQUIRE_ENV", "0").strip() == "1" and not os.getenv("NF_PUBLIC_BASE_URL", "").strip():
        missing.append("NF_PUBLIC_BASE_URL")
    if missing:
        vars_str = ", ".join(missing)
        raise ConnectorEnvError(
            f"M365 connector unavailable: missing {vars_str}. "
            "Set in the API process environment — see docs/LOCAL_DEV.md#trust-ledger-dev-options."
        )


def oauth_start_url(connector_id: str, base_url: str) -> str:
    state = secrets.token_urlsafe(16)
    return f"{base_url.rstrip('/')}/connectors/{connector_id}/oauth/callback?state={state}&code=dev-mock"


def oauth_success_redirect_url(base_url: str, connector_id: str) -> str:
    return f"{base_url.rstrip('/')}/workspace?connected={connector_id}"


def complete_mock_oauth(db: Session, row: ConnectorRecord, code: str | None) -> ConnectorRecord:
    ensure_m365_connector_env()
    mock_token = os.getenv("NF_M365_MOCK_TOKEN", "dev-mock-token-do-not-use-in-prod")
    if code and code != "dev-mock" and not os.getenv("NF_M365_ALLOW_ANY_CODE"):
        raise ValueError(
            "Invalid OAuth code (dev: use code=dev-mock, or set NF_M365_ALLOW_ANY_CODE=1)"
        )
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
