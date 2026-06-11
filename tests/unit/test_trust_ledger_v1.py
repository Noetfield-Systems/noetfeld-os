"""Trust Ledger v1 API — evidence, connectors, TLE lifecycle."""

import asyncio
import os
from uuid import uuid4

from tests.unit.test_governance_v1 import governance_test_client


def test_trust_ledger_connectors() -> None:
    async def run() -> None:
        async with governance_test_client() as client:
            cid = f"conn-{uuid4().hex[:8]}"
            reg = await client.post(
                "/api/v1/connectors",
                json={
                    "connector_id": cid,
                    "type": "Purview",
                    "required_scopes": ["Audit.Read"],
                    "ingest_mode": "metadata_only",
                },
            )
            assert reg.status_code == 201
            assert reg.json()["connector_id"] == cid

            got = await client.get(f"/api/v1/connectors/{cid}")
            assert got.status_code == 200
            assert got.json()["type"] == "Purview"
            assert got.json()["status"] == "registered"
            assert got.json()["last_sync"] is None

            sync = await client.post(
                f"/api/v1/connectors/{cid}/sync",
                json={"status": "active", "records_synced": 3},
            )
            assert sync.status_code == 200
            body = sync.json()
            assert body["status"] == "active"
            assert body["last_sync"] is not None

            got2 = await client.get(f"/api/v1/connectors/{cid}")
            assert got2.json()["status"] == "active"
            assert got2.json()["last_sync"] is not None

    asyncio.run(run())


def _approve_payload(approver: str) -> dict[str, str]:
    return {
        "approver_id": approver,
        "status": "Approved",
        "signature_hash": "sig:testhash000000000000000000000000000000000000000000",
        "key_id": "kms-test-01",
    }


def test_trust_ledger_multi_approve_then_immutable() -> None:
    os.environ["TLE_REQUIRED_APPROVALS"] = "2"

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
            assert body["status"] == "PendingApproval"

            first = await client.post(
                f"/api/v1/tle/{tle_id}/approve",
                json=_approve_payload("usr-legal-001"),
            )
            assert first.status_code == 200
            assert first.json()["status"] == "PendingApproval"

            second = await client.post(
                f"/api/v1/tle/{tle_id}/approve",
                json=_approve_payload("usr-legal-002"),
            )
            assert second.status_code == 200
            assert second.json()["status"] == "Approved"

            third = await client.post(
                f"/api/v1/tle/{tle_id}/approve",
                json=_approve_payload("usr-legal-003"),
            )
            assert third.status_code == 409

            listed = await client.get("/api/v1/tle", params={"status": "Approved"})
            assert listed.status_code == 200
            ids = [item["tle_id"] for item in listed.json()["items"]]
            assert tle_id in ids

    asyncio.run(run())


def test_trust_ledger_pdf_export() -> None:
    os.environ["TLE_REQUIRED_APPROVALS"] = "2"

    async def run() -> None:
        async with governance_test_client() as client:
            ev_id = f"ev-pdf-{uuid4().hex[:8]}"
            await client.post(
                "/api/v1/evidence/ingest",
                json={
                    "evidence_id": ev_id,
                    "source": "Purview",
                    "title": "PDF test",
                    "hash": "sha256:abcdef0123456789abcdef01",
                    "ingest_mode": "metadata_only",
                },
            )
            draft = await client.post(
                "/api/v1/tle/draft",
                json={
                    "template_id": "copilot-go-no-go-v1",
                    "evidence_ids": [ev_id],
                },
            )
            tle_id = draft.json()["tle_id"]
            await client.post(f"/api/v1/tle/{tle_id}/approve", json=_approve_payload("a1"))
            await client.post(f"/api/v1/tle/{tle_id}/approve", json=_approve_payload("a2"))

            export = await client.get(f"/api/v1/tle/{tle_id}/export")
            assert export.status_code == 200
            assert export.headers.get("content-type", "").startswith("application/pdf")
            assert export.content[:4] == b"%PDF"

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


def test_trust_ledger_draft_confidence_score() -> None:
    async def run() -> None:
        async with governance_test_client() as client:
            ev_id = f"ev-conf-{uuid4().hex[:8]}"
            await client.post(
                "/api/v1/evidence/ingest",
                json={
                    "evidence_id": ev_id,
                    "source": "Purview",
                    "title": "Confidence test",
                    "hash": "sha256:abcdef0123456789abcdef01",
                    "ingest_mode": "metadata_only",
                },
            )
            draft = await client.post(
                "/api/v1/tle/draft",
                json={
                    "template_id": "copilot-go-no-go-v1",
                    "evidence_ids": [ev_id],
                    "decision": "Test confidence",
                },
            )
            assert draft.status_code == 201
            body = draft.json()
            assert "confidence_score" in body
            assert 0.0 <= body["confidence_score"] <= 1.0
            factors = body.get("confidence_factors") or []
            assert len(factors) >= 3
            assert body.get("confidence_method") == "deterministic-v0"

            got = await client.get(f"/api/v1/tle/{body['tle_id']}")
            assert got.status_code == 200
            assert got.json()["confidence_score"] == body["confidence_score"]

    asyncio.run(run())


def test_trust_ledger_list_evidence() -> None:
    async def run() -> None:
        async with governance_test_client() as client:
            ev_id = f"ev-list-{uuid4().hex[:8]}"
            await client.post(
                "/api/v1/evidence/ingest",
                json={
                    "evidence_id": ev_id,
                    "source": "EntraID",
                    "title": "List test",
                    "hash": "sha256:abcdef0123456789abcdef01",
                    "ingest_mode": "metadata_only",
                },
            )
            listed = await client.get("/api/v1/evidence", params={"limit": 10})
            assert listed.status_code == 200
            assert listed.json()["count"] >= 1

    asyncio.run(run())
