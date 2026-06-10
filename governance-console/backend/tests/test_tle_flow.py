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
from db.models import EvidenceIndex, PILOT_TENANT_ID  # noqa: E402
from db.session import get_db  # noqa: E402
from main import app  # noqa: E402
from services.evidence_hash import CONTENT_HASH_RE, content_hash_for_metadata  # noqa: E402

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


def test_evidence_ingest_invalid_hash_rejected():
    eid = f"EV-BAD-{uuid.uuid4().hex[:8].upper()}"
    r = client.post(
        "/evidence/ingest",
        headers=TENANT_HEADER,
        json={
            "evidence_id": eid,
            "source": "Manual",
            "title": "Bad hash evidence",
            "content_hash": "sha256:deadbeef",
        },
    )
    assert r.status_code == 422


def test_evidence_ingest_valid_hash():
    eid = f"EV-GOOD-{uuid.uuid4().hex[:8].upper()}"
    content_hash = content_hash_for_metadata(
        evidence_id=eid,
        source="Manual",
        title="Valid hash evidence",
        storage_ref="test/local",
    )
    r = client.post(
        "/evidence/ingest",
        headers=TENANT_HEADER,
        json={
            "evidence_id": eid,
            "source": "Manual",
            "title": "Valid hash evidence",
            "content_hash": content_hash,
            "storage_ref": "test/local",
        },
    )
    assert r.status_code == 201
    assert r.json()["evidence_id"] == eid


def test_evidence_ingest_and_list_connectors():
    eid = f"EV-TEST-{uuid.uuid4().hex[:8].upper()}"
    content_hash = content_hash_for_metadata(
        evidence_id=eid,
        source="Manual",
        title="Test evidence",
    )
    r = client.post(
        "/evidence/ingest",
        headers=TENANT_HEADER,
        json={
            "evidence_id": eid,
            "source": "Manual",
            "title": "Test evidence",
            "content_hash": content_hash,
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


def test_tle_draft_drift_contract_v0():
    r1 = client.post(
        "/tle/draft",
        headers=TENANT_HEADER,
        json={"evidence_ids": ["EV-PURVIEW-001", "EV-ENTRA-001", "EV-AUDIT-001"]},
    )
    assert r1.status_code == 201
    baseline = r1.json()
    assert baseline["document"]["drift_class"] == "initial"
    assert baseline["document"]["baseline_tle_id"] is None

    r2 = client.post(
        "/tle/draft",
        headers=TENANT_HEADER,
        json={
            "evidence_ids": ["EV-PURVIEW-001", "EV-ENTRA-001", "EV-AUDIT-001"],
            "baseline_tle_id": baseline["tle_id"],
        },
    )
    assert r2.status_code == 201
    follow = r2.json()
    assert follow["document"]["baseline_tle_id"] == baseline["tle_id"]
    assert follow["document"]["drift_class"] == "stable"
    assert follow["document"]["delta_summary"]["drift_class"] == "stable"
    assert follow["document"]["severity"] == "Low"

    bad = client.post(
        "/tle/draft",
        headers=TENANT_HEADER,
        json={
            "evidence_ids": ["EV-PURVIEW-001"],
            "baseline_tle_id": "TLE-NOT-FOUND",
        },
    )
    assert bad.status_code == 400


def test_tle_diff_evaluate_vs_last():
    r1 = client.post(
        "/tle/draft",
        headers=TENANT_HEADER,
        json={"evidence_ids": ["EV-PURVIEW-001", "EV-ENTRA-001", "EV-AUDIT-001"]},
    )
    assert r1.status_code == 201
    baseline_id = r1.json()["tle_id"]

    diff0 = client.post(
        "/tle/diff/evaluate",
        headers=TENANT_HEADER,
        json={"evidence_ids": ["EV-PURVIEW-001"]},
    )
    assert diff0.status_code == 200
    body0 = diff0.json()
    assert body0["helper"] == "evaluate_vs_last_tle_v0"
    assert body0["last_tle_id"] == baseline_id
    assert body0["drift_class"] in ("minor", "material")
    assert "EV-ENTRA-001" in body0["evidence_removed"]
    assert "EV-AUDIT-001" in body0["evidence_removed"]

    diff1 = client.post(
        "/tle/diff/evaluate",
        headers=TENANT_HEADER,
        json={"evidence_ids": ["EV-PURVIEW-001", "EV-ENTRA-001", "EV-AUDIT-001"]},
    )
    assert diff1.status_code == 200
    body1 = diff1.json()
    assert body1["last_tle_id"] == baseline_id
    assert body1["drift_class"] == "stable"
    assert body1["evidence_added"] == []
    assert body1["evidence_removed"] == []


def test_diff_evaluate_empty_baseline():
    from services.tle_service import build_delta_summary, drift_severity

    summary = build_delta_summary(
        drift_class="initial",
        baseline_tle_id=None,
        baseline_score=None,
        new_score=0.83,
        evidence_added=[],
        evidence_removed=[],
    )
    assert summary["drift_class"] == "initial"
    assert summary["baseline_tle_id"] is None
    assert drift_severity("initial") == "Low"

    diff = client.post(
        "/tle/diff/evaluate",
        headers=TENANT_HEADER,
        json={"evidence_ids": ["EV-PURVIEW-001"]},
    )
    assert diff.status_code == 200
    assert "severity" in diff.json()
    assert "delta_summary" in diff.json()


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


def test_oauth_callback_html_redirects_to_workspace():
    cid = f"m365-html-{uuid.uuid4().hex[:8]}"
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
        headers={**TENANT_HEADER, "Accept": "text/html"},
        params={"code": "dev-mock", "state": "html"},
        follow_redirects=False,
    )
    assert cb.status_code == 302
    location = cb.headers.get("location", "")
    assert f"/workspace?connected={cid}" in location


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
    evidence = draft.json()["document"]["evidence"]
    assert len(evidence) == 3
    for item in evidence:
        assert CONTENT_HASH_RE.match(item["metadata"]["hash"])

    db = TestingSessionLocal()
    try:
        for eid in (
            "EV-PURVIEW-COPILOT-LABELS",
            "EV-ENTRA-CA-COPILOT",
            "EV-SPO-SITE-POLICY",
        ):
            row = db.get(EvidenceIndex, eid)
            assert row is not None
            assert CONTENT_HASH_RE.match(row.content_hash)
    finally:
        db.close()


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
    assert export["signature_block"]["digest_version"] == "v2"
    assert len(export["signature_block"]["signatures"]) == 3
    assert export.get("audit_digest_link") is not None
    assert export.get("confidence_score", 0) > 0
    assert "drift_contract" in export
    pdf = client.get(f"/tle/{tle_id}/export?format=pdf", headers=TENANT_HEADER)
    assert pdf.status_code == 200
    assert len(pdf.content) > 800
    assert pdf.content[:4] == b"%PDF"


def test_export_procurement_zip():
    import io
    import zipfile

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
    resp = client.get(f"/tle/{tle_id}/export?format=zip", headers=TENANT_HEADER)
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/zip")
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        names = set(zf.namelist())
        assert "board_pack.json" in names
        assert "board_pack.pdf" in names
        assert "README-procurement.txt" in names
        assert b"%PDF" in zf.read("board_pack.pdf")[:8]
