"""NF-PLAN-0102 — docs diligence happy path + 409 guards."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from uuid import uuid4

from tests.unit.test_governance_v1 import governance_test_client

ROOT = Path(__file__).resolve().parents[2]
DILIGENCE = ROOT / "docs" / "diligence"


def _approve_payload(approver: str) -> dict[str, str]:
    return {
        "approver_id": approver,
        "status": "Approved",
        "signature_hash": "sig:testhash000000000000000000000000000000000000000000",
        "key_id": "kms-test-01",
    }


def test_diligence_pack_artifacts_exist() -> None:
    required = [
        DILIGENCE / "README.md",
        DILIGENCE / "EVIDENCE_INTAKE_CONTRACT_v1.md",
        DILIGENCE / "CONNECTORS_CONTROLS_v1.md",
        DILIGENCE / "sample-audit-export.redacted.json",
        DILIGENCE / "rpaa-positioning-onepager.md",
    ]
    for path in required:
        assert path.is_file(), f"missing diligence artifact: {path}"
    sample = json.loads((DILIGENCE / "sample-audit-export.redacted.json").read_text(encoding="utf-8"))
    assert sample.get("export_type") == "governance_audit"


def test_diligence_demo_path_evaluate_to_audit_export() -> None:
    """docs/diligence/README.md demo path: evaluate → audit-export by RID."""

    async def run() -> None:
        async with governance_test_client() as client:
            evaluate = await client.post(
                "/api/v1/governance/evaluate",
                json={
                    "tenant_id": str(uuid4()),
                    "organization_id": str(uuid4()),
                    "action": "copilot_rollout_intent",
                    "resource_type": "diligence-probe",
                    "resource_id": "integration-0102",
                    "mode": "shadow",
                },
            )
            assert evaluate.status_code == 200
            rid = evaluate.json()["request_id"]
            assert rid.startswith("RID-")

            export = await client.get(
                "/api/v1/governance/audit-export",
                params={"request_id": rid},
            )
            assert export.status_code == 200
            pack = export.json()
            assert pack["export_type"] == "governance_audit"
            assert pack["request_id"] == rid
            assert "boundary_statement" in pack
            assert pack["entry_count"] >= 1

    asyncio.run(run())


def test_diligence_vendor_evidence_endpoint() -> None:
    async def run() -> None:
        async with governance_test_client() as client:
            response = await client.get("/api/v1/governance/vendor-evidence")
            assert response.status_code == 200
            body = response.json()
            assert body["pack"] == "e23-vendor-evidence-starter"
            assert "audit-export" in json.dumps(body)

    asyncio.run(run())


def test_diligence_tle_export_409_before_approval() -> None:
    async def run() -> None:
        async with governance_test_client() as client:
            ev_id = f"ev-diligence-{uuid4().hex[:8]}"
            ingest = await client.post(
                "/api/v1/evidence/ingest",
                json={
                    "evidence_id": ev_id,
                    "source": "Purview",
                    "title": "Diligence integration evidence",
                    "hash": "sha256:abcdef0123456789abcdef01",
                    "ingest_mode": "metadata_only",
                },
            )
            assert ingest.status_code == 201
            draft = await client.post(
                "/api/v1/tle/draft",
                json={
                    "template_id": "copilot-go-no-go-v1",
                    "evidence_ids": [ev_id],
                },
            )
            assert draft.status_code == 201
            tle_id = draft.json()["tle_id"]

            export = await client.get(f"/api/v1/tle/{tle_id}/export")
            assert export.status_code == 409

    asyncio.run(run())


def test_diligence_tle_approve_409_after_immutable() -> None:
    os.environ["TLE_REQUIRED_APPROVALS"] = "2"

    async def run() -> None:
        async with governance_test_client() as client:
            ev_id = f"ev-immutable-{uuid4().hex[:8]}"
            await client.post(
                "/api/v1/evidence/ingest",
                json={
                    "evidence_id": ev_id,
                    "source": "Purview",
                    "title": "Immutable guard evidence",
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
            await client.post(f"/api/v1/tle/{tle_id}/approve", json=_approve_payload("usr-1"))
            await client.post(f"/api/v1/tle/{tle_id}/approve", json=_approve_payload("usr-2"))

            third = await client.post(f"/api/v1/tle/{tle_id}/approve", json=_approve_payload("usr-3"))
            assert third.status_code == 409

    asyncio.run(run())
