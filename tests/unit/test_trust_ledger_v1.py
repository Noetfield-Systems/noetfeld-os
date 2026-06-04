"""Trust Ledger v1 API — evidence ingest and TLE draft/approve."""

import asyncio
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from noetfield_governance.api import app, startup_platform
from tests.unit.test_governance_v1 import governance_test_client


def test_trust_ledger_draft_approve_immutable() -> None:
    async def run() -> None:
        async with governance_test_client() as client:
            ev_id = f"ev-test-{uuid4().hex[:8]}"
            ingest = await client.post(
                "/api/v1/evidence/ingest",
                json={
                    "evidence_id": ev_id,
                    "source": "Purview",
                    "title": "Test evidence",
                    "hash": "sha256:abcdef0123456789",
                    "ingest_mode": "metadata_only",
                },
            )
            assert ingest.status_code == 201
            draft = await client.post(
                "/api/v1/tle/draft",
                json={
                    "template_id": "copilot-go-no-go-v1",
                    "evidence_ids": [ev_id],
                    "owner_id": "usr-test-001",
                    "decision": "Pilot Copilot rollout",
                },
            )
            assert draft.status_code == 201
            body = draft.json()
            tle_id = body["tle_id"]
            assert body["status"] == "Draft"

            fetched = await client.get(f"/api/v1/tle/{tle_id}")
            assert fetched.status_code == 200
            assert fetched.json()["tle_id"] == tle_id

            approve = await client.post(
                f"/api/v1/tle/{tle_id}/approve",
                json={
                    "approver_id": "usr-legal-001",
                    "status": "Approved",
                    "signature_hash": "sig:testhash000000000000000000000000000000000000000000",
                    "key_id": "kms-test-01",
                },
            )
            assert approve.status_code == 200
            assert approve.json()["status"] == "Approved"

            second = await client.post(
                f"/api/v1/tle/{tle_id}/approve",
                json={
                    "approver_id": "usr-legal-002",
                    "status": "Approved",
                    "signature_hash": "sig:testhash111111111111111111111111111111111111111111",
                    "key_id": "kms-test-02",
                },
            )
            assert second.status_code == 409

    asyncio.run(run())


def test_trust_ledger_missing_evidence() -> None:
    async def run() -> None:
        async with governance_test_client() as client:
            draft = await client.post(
                "/api/v1/tle/draft",
                json={
                    "template_id": "copilot-go-no-go-v1",
                    "evidence_ids": ["ev-does-not-exist"],
                },
            )
            assert draft.status_code == 400

    asyncio.run(run())
