"""Governance v1 partner-signals API."""

import asyncio
from uuid import uuid4

from contextlib import asynccontextmanager
from typing import AsyncIterator

from httpx import ASGITransport, AsyncClient

from noetfield_governance.api import app, startup_platform


@asynccontextmanager
async def governance_test_client() -> AsyncIterator[AsyncClient]:
    await startup_platform()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


def test_partner_signals_ingest_read_only() -> None:
    tenant_id = uuid4()
    org_id = uuid4()

    async def run() -> None:
        async with governance_test_client() as client:
            response = await client.post(
                "/api/v1/governance/partner-signals",
                json={
                    "tenant_id": str(tenant_id),
                    "organization_id": str(org_id),
                    "partner_id": "test-partner",
                    "signal_kind": "balance_snapshot",
                    "payload": {"note": "read_only"},
                },
            )
            assert response.status_code == 200
            body = response.json()
            assert body["read_only"] is True
            assert "signal_id" in body

    asyncio.run(run())


def test_partner_signals_rejects_execution_payload() -> None:
    tenant_id = uuid4()
    org_id = uuid4()

    async def run() -> None:
        async with governance_test_client() as client:
            response = await client.post(
                "/api/v1/governance/partner-signals",
                json={
                    "tenant_id": str(tenant_id),
                    "organization_id": str(org_id),
                    "partner_id": "test-partner",
                    "signal_kind": "bad",
                    "payload": {"place_order": True},
                },
            )
            assert response.status_code == 400

    asyncio.run(run())


def test_scenario_preset_exchange() -> None:
    async def run() -> None:
        async with governance_test_client() as client:
            response = await client.get("/api/v1/governance/scenario-presets/exchange")
            assert response.status_code == 200
            assert response.json()["resource_type"] == "partner_exchange"

    asyncio.run(run())


def test_scenario_preset_msb() -> None:
    async def run() -> None:
        async with governance_test_client() as client:
            response = await client.get("/api/v1/governance/scenario-presets/msb")
            assert response.status_code == 200
            assert response.json()["resource_type"] == "msb_payment"

    asyncio.run(run())
