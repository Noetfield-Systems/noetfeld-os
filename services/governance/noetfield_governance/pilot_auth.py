"""Pilot API key authentication for governance v1 routes."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from fastapi import HTTPException, Request
from pydantic import SecretStr

from noetfield_config import get_settings


@dataclass(frozen=True)
class PilotAuthContext:
    """Resolved pilot credentials for a governance API call."""

    tenant_id: UUID | None
    key_label: str = "pilot"


def _parse_pilot_keys(raw: str) -> dict[str, UUID | None]:
    """Map secret -> optional bound tenant_id."""
    mapping: dict[str, UUID | None] = {}
    for part in raw.split(","):
        token = part.strip()
        if not token:
            continue
        if ":" in token:
            tenant_part, secret = token.split(":", 1)
            try:
                mapping[secret.strip()] = UUID(tenant_part.strip())
            except ValueError:
                continue
        else:
            mapping[token] = None
    return mapping


def _extract_bearer(request: Request) -> str | None:
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip() or None
    return request.headers.get("X-API-Key", "").strip() or None


def _secret(value: SecretStr | None) -> str:
    return value.get_secret_value().strip() if value else ""


async def require_pilot_auth(request: Request) -> PilotAuthContext:
    settings = get_settings()
    if not settings.governance_pilot_auth_required:
        return PilotAuthContext(tenant_id=None, key_label="open-pilot-dev")

    keys = _parse_pilot_keys(settings.governance_pilot_api_keys)
    if not keys:
        raise HTTPException(
            status_code=503,
            detail="Governance pilot authentication is required but no keys are configured",
        )

    presented = _extract_bearer(request)
    if not presented or presented not in keys:
        raise HTTPException(status_code=401, detail="Invalid or missing pilot API key")

    return PilotAuthContext(tenant_id=keys[presented], key_label="pilot")


def assert_tenant_allowed(auth: PilotAuthContext, tenant_id: UUID) -> None:
    if auth.tenant_id is not None and auth.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="API key is not authorized for this tenant_id")
