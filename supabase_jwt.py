"""
Supabase Bearer JWT validation for portfolio API routes (Phase 4 auth W11).
"""

from __future__ import annotations

import os

import httpx
from fastapi import Header, HTTPException, status

from auth import AuthenticatedClient, KEY_STORE, require_scope


def _supabase_url() -> str:
    return (
        os.environ.get("NOETFIELD_SUPABASE_URL", "").strip()
        or os.environ.get("SUPABASE_URL", "").strip()
    ).rstrip("/")


def _supabase_anon_key() -> str:
    return (
        os.environ.get("NOETFIELD_SUPABASE_ANON_KEY", "").strip()
        or os.environ.get("SUPABASE_ANON_KEY", "").strip()
        or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY", "").strip()
    )


async def verify_supabase_bearer(authorization: str | None) -> dict[str, str]:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Bearer token or X-API-Key",
        )
    jwt = authorization.split(" ", 1)[1].strip()
    if not jwt:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Empty Bearer token")

    base = _supabase_url()
    anon = _supabase_anon_key()
    if not base or not anon:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="JWT verification not configured",
        )

    async with httpx.AsyncClient(timeout=12.0) as client:
        response = await client.get(
            f"{base}/auth/v1/user",
            headers={"Authorization": f"Bearer {jwt}", "apikey": anon},
        )

    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired JWT")

    payload = response.json()
    user = payload.get("user") if isinstance(payload, dict) else None
    if not isinstance(user, dict) or not user.get("id"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid JWT user")

    email = str(user.get("email") or "").strip().lower()
    return {"id": str(user["id"]), "email": email}


def _jwt_client(user: dict[str, str]) -> AuthenticatedClient:
    tenant = user["id"][:8]
    return AuthenticatedClient(
        key_id=f"jwt:{user['id'][:8]}",
        tenant_id=tenant,
        org_id=tenant,
        scopes=frozenset({"decision:write", "audit:read"}),
    )


def require_decision_write_or_jwt():
    api_dep = require_scope("decision:write")

    async def dependency(
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
        authorization: str | None = Header(default=None),
    ) -> AuthenticatedClient:
        if x_api_key:
            return await api_dep(x_api_key=x_api_key)
        user = await verify_supabase_bearer(authorization)
        return _jwt_client(user)

    return dependency


require_decision_write = require_decision_write_or_jwt()
