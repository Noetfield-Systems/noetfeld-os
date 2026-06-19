"""Sandbox v2 API — provision, evaluate caps, export moment."""

import asyncio
import os

# Must set before api module loads cached Settings
os.environ.setdefault("INTAKE_PERSISTENCE", "memory")
os.environ.setdefault("RUNTIME_EVENT_STORE", "memory")
os.environ.setdefault("REDIS_SESSIONS_ENABLED", "false")

from contextlib import asynccontextmanager
from typing import AsyncIterator

from httpx import ASGITransport, AsyncClient

from noetfield_governance.api import app, startup_platform
from noetfield_governance.sandbox_service import (
    SandboxSession,
    build_board_export_pdf,
    provision_sandbox,
    reset_sandbox_memory_for_tests,
    sandbox_evaluate,
    validate_work_email,
)


@asynccontextmanager
async def sandbox_test_client() -> AsyncIterator[AsyncClient]:
    reset_sandbox_memory_for_tests()
    await startup_platform()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


def test_validate_work_email_rejects_consumer_domains() -> None:
    try:
        validate_work_email("user@gmail.com")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "work email" in str(exc).lower()


def test_build_board_export_pdf_watermark() -> None:
    session = SandboxSession(
        session_token="tok",
        tenant_id="sandbox-abc12345",
        email="dev@acme.com",
        org="Acme",
        api_key_preview="nf_sbx_test",
        mode="observe",
        evaluates_used=1,
        evaluates_limit=50,
        created_at="2026-06-03T00:00:00+00:00",
        expires_at="2026-06-17T00:00:00+00:00",
        trial_step=4,
        m365_connected=True,
        last_rid="RID-TEST-1234",
        factory_demos_run=[],
    )
    pdf = build_board_export_pdf(session)
    assert pdf.startswith(b"%PDF")
    assert b"SANDBOX ORIENTATION" in pdf


def test_sandbox_service_provision_evaluate_flow() -> None:
    async def run() -> None:
        reset_sandbox_memory_for_tests()
        session = await provision_sandbox(
            email="dev@acme-bank.com",
            org="Acme",
            client_key="test-client",
        )
        assert session.mode == "observe"
        result = await sandbox_evaluate(session.session_token)
        assert result["rid"].startswith("RID-")
        assert result["evaluates_used"] == 1

    asyncio.run(run())


def test_sandbox_health() -> None:
    async def run() -> None:
        async with sandbox_test_client() as client:
            response = await client.get("/api/sandbox/health")
            assert response.status_code == 200
            body = response.json()
            assert body["enabled"] is True
            assert body["mode"] == "observe"
            assert body["evaluate_limit"] == 50

    asyncio.run(run())


def test_sandbox_provision_rejects_free_email() -> None:
    async def run() -> None:
        async with sandbox_test_client() as client:
            response = await client.post(
                "/api/sandbox/provision",
                json={"email": "user@gmail.com", "org": "Test"},
            )
            assert response.status_code == 400

    asyncio.run(run())


def test_sandbox_provision_evaluate_export_flow() -> None:
    async def run() -> None:
        async with sandbox_test_client() as client:
            prov = await client.post(
                "/api/sandbox/provision",
                json={"email": "dev@acme-bank.com", "org": "Acme"},
            )
            assert prov.status_code == 200
            session = prov.json()
            token = session["session_token"]
            assert session["mode"] == "observe"
            assert session["tenant_id"].startswith("sandbox-")
            headers = {"X-Sandbox-Token": token}

            get_sess = await client.get("/api/sandbox/session", headers=headers)
            assert get_sess.status_code == 200

            ev = await client.post("/api/sandbox/evaluate", headers=headers)
            assert ev.status_code == 200
            rid = ev.json()["rid"]
            assert rid.startswith("RID-")

            demo = await client.post(
                "/api/sandbox/factory-demo",
                headers=headers,
                json={"factory_id": "copilot_governance_readiness_v1"},
            )
            assert demo.status_code == 200
            assert demo.json()["observe_only"] is True

            pdf = await client.get("/api/sandbox/export/board.pdf", headers=headers)
            assert pdf.status_code == 200
            assert pdf.content[:4] == b"%PDF"
            assert b"SANDBOX ORIENTATION" in pdf.content

    asyncio.run(run())


def test_sandbox_evaluate_requires_token() -> None:
    async def run() -> None:
        async with sandbox_test_client() as client:
            response = await client.post("/api/sandbox/evaluate")
            assert response.status_code == 401

    asyncio.run(run())
