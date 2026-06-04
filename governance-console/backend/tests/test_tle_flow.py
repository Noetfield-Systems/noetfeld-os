"""TLE v1 API flow tests."""

from __future__ import annotations

import os
import tempfile
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

_test_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_test_db.name}"

from db.bootstrap import init_schema, migrate_audit_logs_to_events, seed_pilot_evidence  # noqa: E402
from db.models import PILOT_TENANT_ID  # noqa: E402
from db.session import get_db  # noqa: E402
from main import app  # noqa: E402

engine = create_engine(
    os.environ["DATABASE_URL"],
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_schema()
    db = TestingSessionLocal()
    try:
        migrate_audit_logs_to_events(db)
        seed_pilot_evidence(db)
    finally:
        db.close()
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


client = TestClient(app)
TENANT_HEADER = {"X-Tenant-ID": str(PILOT_TENANT_ID)}


def test_evidence_ingest_and_list_connectors():
    eid = f"EV-TEST-{uuid.uuid4().hex[:8].upper()}"
    r = client.post(
        "/evidence/ingest",
        headers=TENANT_HEADER,
        json={
            "evidence_id": eid,
            "source": "Manual",
            "title": "Test evidence",
            "content_hash": "sha256:deadbeef",
        },
    )
    assert r.status_code == 201
    assert r.json()["evidence_id"] == eid

    cid = f"conn-{uuid.uuid4().hex[:8]}"
    r2 = client.post(
        "/connectors",
        headers=TENANT_HEADER,
        json={
            "connector_id": cid,
            "connector_type": "m365_purview",
            "required_scopes": ["Purview.Read"],
        },
    )
    assert r2.status_code == 201

    r3 = client.get("/connectors", headers=TENANT_HEADER)
    assert r3.status_code == 200
    assert any(c["connector_id"] == cid for c in r3.json())


def test_tle_draft_approve_export():
    r = client.post(
        "/tle/draft",
        headers=TENANT_HEADER,
        json={"evidence_ids": ["EV-PURVIEW-001", "EV-ENTRA-001", "EV-AUDIT-001"]},
    )
    assert r.status_code == 201
    body = r.json()
    tle_id = body["tle_id"]
    assert body["status"] == "Draft"
    assert 0 <= body["confidence_score"] <= 1

    for approver in ("cio-001", "legal-001", "sec-001"):
        ar = client.post(
            f"/tle/{tle_id}/approve",
            headers=TENANT_HEADER,
            json={"approver_id": approver, "decision": "Approved"},
        )
        assert ar.status_code == 200

    final = client.get(f"/tle/{tle_id}", headers=TENANT_HEADER).json()
    assert final["status"] in ("Approved", "Conditional")
    assert final["audit_digest"] is not None
    assert final["audit_digest"].startswith("sha256:")

    export = client.get(f"/tle/{tle_id}/export", headers=TENANT_HEADER)
    assert export.status_code == 200
    assert export.json()["export_type"] == "board_pack_v1"

    pdf = client.get(f"/tle/{tle_id}/export?format=pdf", headers=TENANT_HEADER)
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"
    assert pdf.content[:4] == b"%PDF"


def test_viewer_cannot_approve():
    r = client.post(
        "/tle/draft",
        headers=TENANT_HEADER,
        json={"evidence_ids": ["EV-PURVIEW-001", "EV-ENTRA-001", "EV-AUDIT-001"]},
    )
    tle_id = r.json()["tle_id"]
    denied = client.post(
        f"/tle/{tle_id}/approve",
        headers={**TENANT_HEADER, "X-Role": "viewer"},
        json={"approver_id": "cio-001", "decision": "Approved"},
    )
    assert denied.status_code == 403


def test_m365_oauth_mock_flow():
    cid = f"m365-{uuid.uuid4().hex[:8]}"
    reg = client.post(
        "/connectors",
        headers=TENANT_HEADER,
        json={
            "connector_id": cid,
            "connector_type": "m365_purview",
            "required_scopes": ["Purview.Read"],
        },
    )
    assert reg.status_code == 201
    cb = client.get(
        f"/connectors/{cid}/oauth/callback",
        headers=TENANT_HEADER,
        params={"code": "dev-mock", "state": "test"},
    )
    assert cb.status_code == 200
    assert cb.json()["oauth_connected"] is True
    st = client.get(f"/connectors/{cid}/status", headers=TENANT_HEADER)
    assert st.json()["oauth_connected"] is True


def test_oauth_callback_ingests_evidence():
    cid = f"m365-ingest-{uuid.uuid4().hex[:8]}"
    client.post(
        "/connectors",
        headers=TENANT_HEADER,
        json={
            "connector_id": cid,
            "connector_type": "m365_purview",
            "required_scopes": ["Purview.Read"],
        },
    )
    client.get(
        f"/connectors/{cid}/oauth/callback",
        headers=TENANT_HEADER,
        params={"code": "dev-mock", "state": "ingest"},
    )
    draft = client.post(
        "/tle/draft",
        headers=TENANT_HEADER,
        json={
            "evidence_ids": [
                "EV-PURVIEW-COPILOT-LABELS",
                "EV-ENTRA-CA-COPILOT",
                "EV-SPO-SITE-POLICY",
            ],
        },
    )
    assert draft.status_code == 201
    assert len(draft.json()["document"]["evidence"]) == 3


def test_out_of_order_approval_denied():
    r = client.post(
        "/tle/draft",
        headers=TENANT_HEADER,
        json={"evidence_ids": ["EV-PURVIEW-001", "EV-ENTRA-001", "EV-AUDIT-001"]},
    )
    tle_id = r.json()["tle_id"]
    denied = client.post(
        f"/tle/{tle_id}/approve",
        headers=TENANT_HEADER,
        json={"approver_id": "legal-001", "decision": "Approved"},
    )
    assert denied.status_code == 403
    ok = client.post(
        f"/tle/{tle_id}/approve",
        headers=TENANT_HEADER,
        json={"approver_id": "cio-001", "decision": "Approved"},
    )
    assert ok.status_code == 200


def test_export_includes_signature_block():
    r = client.post(
        "/tle/draft",
        headers=TENANT_HEADER,
        json={"evidence_ids": ["EV-PURVIEW-001", "EV-ENTRA-001", "EV-AUDIT-001"]},
    )
    tle_id = r.json()["tle_id"]
    for approver in ("cio-001", "legal-001", "sec-001"):
        client.post(
            f"/tle/{tle_id}/approve",
            headers=TENANT_HEADER,
            json={"approver_id": approver, "decision": "Approved"},
        )
    export = client.get(f"/tle/{tle_id}/export", headers=TENANT_HEADER).json()
    assert "signature_block" in export
    assert export["signature_block"]["key_id"]
    assert len(export["signature_block"]["signatures"]) == 3
    pdf = client.get(f"/tle/{tle_id}/export?format=pdf", headers=TENANT_HEADER)
    assert pdf.status_code == 200
    assert len(pdf.content) > 800
