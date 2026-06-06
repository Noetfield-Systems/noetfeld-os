"""NF-PLAN-0110 — workspace UI pilot scopes and rate limits."""

from __future__ import annotations

import asyncio
import os
from uuid import uuid4

from noetfield_config import get_settings
from noetfield_governance.governance_pilot_limits import reset_memory_rate_limits_for_tests
from noetfield_governance.pilot_auth import _parse_pilot_keys

from tests.unit.test_governance_v1 import governance_test_client


def _reload_settings() -> None:
    get_settings.cache_clear()


def test_parse_pilot_keys_with_workspace_scopes() -> None:
    keys = _parse_pilot_keys("read-only:workspace:read,writer:workspace:write|workspace:read")
    assert keys["read-only"][1] == frozenset({"workspace:read"})
    assert keys["writer"][1] == frozenset({"workspace:write", "workspace:read"})


def test_workspace_read_scope_allows_list() -> None:
    os.environ["GOVERNANCE_PILOT_AUTH_REQUIRED"] = "true"
    os.environ["GOVERNANCE_PILOT_API_KEYS"] = "reader:workspace:read"
    os.environ["GOVERNANCE_WORKSPACE_UI_RATE_LIMIT_PER_MIN"] = "0"
    _reload_settings()
    reset_memory_rate_limits_for_tests()

    async def run() -> None:
        async with governance_test_client() as client:
            response = await client.get(
                "/api/v1/tle",
                headers={"Authorization": "Bearer reader"},
            )
            assert response.status_code == 200

    try:
        asyncio.run(run())
    finally:
        os.environ.pop("GOVERNANCE_PILOT_AUTH_REQUIRED", None)
        os.environ.pop("GOVERNANCE_PILOT_API_KEYS", None)
        os.environ.pop("GOVERNANCE_WORKSPACE_UI_RATE_LIMIT_PER_MIN", None)
        _reload_settings()
        reset_memory_rate_limits_for_tests()


def test_workspace_read_scope_blocks_draft() -> None:
    os.environ["GOVERNANCE_PILOT_AUTH_REQUIRED"] = "true"
    os.environ["GOVERNANCE_PILOT_API_KEYS"] = "reader:workspace:read,admin:workspace:admin"
    os.environ["GOVERNANCE_WORKSPACE_UI_RATE_LIMIT_PER_MIN"] = "0"
    _reload_settings()
    reset_memory_rate_limits_for_tests()

    async def run() -> None:
        async with governance_test_client() as client:
            ev_id = f"ev-scope-{uuid4().hex[:8]}"
            ingest = await client.post(
                "/api/v1/evidence/ingest",
                headers={"Authorization": "Bearer admin"},
                json={
                    "evidence_id": ev_id,
                    "source": "Purview",
                    "title": "scope test",
                    "hash": "sha256:abcdef0123456789abcdef01",
                    "ingest_mode": "metadata_only",
                },
            )
            assert ingest.status_code == 201
            response = await client.post(
                "/api/v1/tle/draft",
                headers={"Authorization": "Bearer reader"},
                json={
                    "template_id": "copilot-go-no-go-v1",
                    "evidence_ids": [ev_id],
                },
            )
            assert response.status_code == 403

    try:
        asyncio.run(run())
    finally:
        os.environ.pop("GOVERNANCE_PILOT_AUTH_REQUIRED", None)
        os.environ.pop("GOVERNANCE_PILOT_API_KEYS", None)
        os.environ.pop("GOVERNANCE_WORKSPACE_UI_RATE_LIMIT_PER_MIN", None)
        _reload_settings()
        reset_memory_rate_limits_for_tests()


def test_workspace_ui_rate_limit_returns_429() -> None:
    os.environ["GOVERNANCE_PILOT_AUTH_REQUIRED"] = "true"
    os.environ["GOVERNANCE_PILOT_API_KEYS"] = "reader:workspace:read"
    os.environ["GOVERNANCE_WORKSPACE_UI_RATE_LIMIT_PER_MIN"] = "2"
    _reload_settings()
    reset_memory_rate_limits_for_tests()

    async def run() -> None:
        async with governance_test_client() as client:
            headers = {"Authorization": "Bearer reader"}
            assert (await client.get("/api/v1/tle", headers=headers)).status_code == 200
            assert (await client.get("/api/v1/tle", headers=headers)).status_code == 200
            third = await client.get("/api/v1/tle", headers=headers)
            assert third.status_code == 429

    try:
        asyncio.run(run())
    finally:
        os.environ.pop("GOVERNANCE_PILOT_AUTH_REQUIRED", None)
        os.environ.pop("GOVERNANCE_PILOT_API_KEYS", None)
        os.environ.pop("GOVERNANCE_WORKSPACE_UI_RATE_LIMIT_PER_MIN", None)
        _reload_settings()
        reset_memory_rate_limits_for_tests()
