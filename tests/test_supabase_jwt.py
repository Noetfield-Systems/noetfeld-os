"""Tests for Supabase JWT auth path (W11 Phase 4)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from supabase_jwt import verify_supabase_bearer


@pytest.mark.asyncio
async def test_verify_supabase_bearer_missing_header():
    with pytest.raises(HTTPException) as exc:
        await verify_supabase_bearer(None)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_verify_supabase_bearer_valid(monkeypatch):
    monkeypatch.setenv("NOETFIELD_SUPABASE_URL", "https://tkgpapowwplupyekpivy.supabase.co")
    monkeypatch.setenv("NOETFIELD_SUPABASE_ANON_KEY", "anon-test")

    class FakeResp:
        status_code = 200

        def json(self):
            return {"user": {"id": "uid-1", "email": "user@example.com"}}

    with patch("supabase_jwt.httpx.AsyncClient") as mock_client:
        instance = mock_client.return_value.__aenter__.return_value
        instance.get = AsyncMock(return_value=FakeResp())
        user = await verify_supabase_bearer("Bearer jwt-token")
        assert user["email"] == "user@example.com"
