"""Governance Console v1 API: /v3/evaluate audit trail and /v3/ledger."""

import asyncio
from uuid import uuid4

from contextlib import asynccontextmanager
from typing import AsyncIterator

from httpx import ASGITransport, AsyncClient

from noetfield_governance.api import app, startup_platform


@asynccontextmanager
async def governance_test_client() -> AsyncIterator[AsyncClient]:
    """HTTPX ASGI transport does not run FastAPI startup; wire platform startup explicitly."""
    await startup_platform()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


def test_v3_ledger_empty_in_memory_mode() -> None:
    async def run() -> None:
        async with governance_test_client() as client:
            response = await client.get("/v3/ledger")
            assert response.status_code == 200
            body = response.json()
            assert body["immutable"] is True
            assert body["source"] == "audit_log"
            assert isinstance(body["entries"], list)

    asyncio.run(run())


def test_v3_evaluate_writes_ledger_entry() -> None:
    tenant_id = uuid4()
    org_id = uuid4()

    async def run() -> None:
        async with governance_test_client() as client:
            evaluate = await client.post(
                "/v3/evaluate",
                json={
                    "tenant_id": str(tenant_id),
                    "organization_id": str(org_id),
                    "action": "submit_payment_intent",
                    "resource_type": "probe",
                    "resource_id": "console-test-1",
                },
            )
            assert evaluate.status_code == 200
            result = evaluate.json()
            assert result["decision"] == "REJECT"

            ledger = await client.get("/v3/ledger", params={"tenant_id": str(tenant_id)})
            assert ledger.status_code == 200
            entries = ledger.json()["entries"]
            assert len(entries) >= 1
            actions = {e["action"] for e in entries}
            assert "POLICY_EVALUATED" in actions

    asyncio.run(run())


def test_governance_console_html_served() -> None:
    async def run() -> None:
        async with governance_test_client() as client:
            response = await client.get("/console")
            assert response.status_code == 200
            assert "Governance Evaluation Interface" in response.text
            assert "Submit Intent" in response.text
            assert "Compliance log" in response.text

    asyncio.run(run())
