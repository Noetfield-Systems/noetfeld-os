"""Institutional governance v1 API."""

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


def test_governance_v1_evaluate_and_ledger() -> None:
    tenant_id = uuid4()
    org_id = uuid4()

    async def run() -> None:
        async with governance_test_client() as client:
            evaluate = await client.post(
                "/api/v1/governance/evaluate",
                json={
                    "tenant_id": str(tenant_id),
                    "organization_id": str(org_id),
                    "action": "submit_payment_intent",
                    "resource_type": "probe",
                    "resource_id": "v1-test",
                    "mode": "shadow",
                },
            )
            assert evaluate.status_code == 200
            body = evaluate.json()
            assert body["request_id"].startswith("RID-")
            assert body["mode"] == "shadow"
            assert body["decision"] == "REJECT"
            assert "non_psp_boundary" in body

            ledger = await client.get(
                "/api/v1/governance/ledger",
                params={"tenant_id": str(tenant_id), "request_id": body["request_id"]},
            )
            assert ledger.status_code == 200
            assert ledger.json()["api_version"] == "v1"

            export = await client.get(
                "/api/v1/governance/audit-export",
                params={"request_id": body["request_id"]},
            )
            assert export.status_code == 200
            assert export.json()["export_type"] == "governance_audit"

    asyncio.run(run())


def test_governance_vendor_evidence() -> None:
    async def run() -> None:
        async with governance_test_client() as client:
            response = await client.get("/api/v1/governance/vendor-evidence")
            assert response.status_code == 200
            body = response.json()
            assert body["pack"] == "e23-vendor-evidence-starter"
            assert "non_psp_statement" in body

    asyncio.run(run())


def test_api_status_endpoint() -> None:
    async def run() -> None:
        async with governance_test_client() as client:
            response = await client.get("/api/status")
            assert response.status_code == 200
            body = response.json()
            assert "ecosystem" in body
            assert "status_page" in body

    asyncio.run(run())


def test_governance_v1_evaluate_deterministic_replay() -> None:
    """Same payload twice yields the same decision (AN3-style guard)."""
    tenant_id = uuid4()
    org_id = uuid4()
    payload = {
        "tenant_id": str(tenant_id),
        "organization_id": str(org_id),
        "action": "submit_payment_intent",
        "resource_type": "determinism-probe",
        "resource_id": "replay-1",
        "mode": "shadow",
    }

    async def run() -> None:
        async with governance_test_client() as client:
            first = await client.post("/api/v1/governance/evaluate", json=payload)
            second = await client.post("/api/v1/governance/evaluate", json=payload)
            assert first.status_code == 200
            assert second.status_code == 200
            a = first.json()
            b = second.json()
            assert a["decision"] == b["decision"]
            assert a["allowed"] == b["allowed"]
            assert a["reason_code"] == b["reason_code"]

    asyncio.run(run())


def test_public_openapi_filters_internal_paths() -> None:
    from noetfield_governance.api import app

    schema = app.openapi()
    paths = set(schema.get("paths", {}))
    assert "/api/v1/governance/evaluate" in paths
    assert "/api/intake" in paths or any(p.startswith("/api/intake") for p in paths)
    assert "/ingestion/manual" not in paths
    assert "/v3/evaluate" not in paths
