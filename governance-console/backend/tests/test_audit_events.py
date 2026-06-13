"""API tests for tenant-scoped audit_events (Trust Ledger Bridge v1)."""

from __future__ import annotations

import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Isolate test DB before importing app modules
_test_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_test_db.name}"

from db.bootstrap import init_schema, migrate_audit_logs_to_events  # noqa: E402
from db.models import Base  # noqa: E402
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
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        migrate_audit_logs_to_events(db)
    finally:
        db.close()
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    _test_db.close()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_evaluate_returns_tenant_and_rid(client: TestClient) -> None:
    resp = client.post(
        "/evaluate",
        json={
            "actor": "test:unit",
            "action": "copilot_quickscan",
            "context": "unit test evaluate",
            "metadata": {},
        },
        headers={"X-Tenant-ID": "copilot-pilot-01"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["decision"] in {"allow", "deny", "review"}
    assert body["rid"].startswith("RID-")
    assert body["tenant_id"] == "00000000-0000-4000-8000-000000000101"


def test_evaluate_includes_confidence_factors_and_risk_summary(client: TestClient) -> None:
    low = client.post(
        "/evaluate",
        json={
            "actor": "test:unit",
            "action": "copilot_quickscan",
            "context": "unit test evaluate low risk path",
            "metadata": {},
        },
        headers={"X-Tenant-ID": "copilot-pilot-01"},
    )
    assert low.status_code == 200
    body = low.json()
    assert len(body["confidence_factors"]) >= 2
    assert body["confidence_factors"][0]["factor"] == "governance_risk"
    risk_factor = next(f for f in body["confidence_factors"] if f["factor"] == "risk_summary")
    assert risk_factor["weight"] == 0.0
    assert len(body["risk_summary"]) == 1
    assert body["risk_summary"][0]["severity"] == "Low"
    assert body["risk_summary"][0]["id"].startswith("RISK-")

    high = client.post(
        "/evaluate",
        json={
            "actor": "test:unit",
            "action": "payment transfer",
            "context": "unknown unverified context",
            "metadata": {"high_risk": True, "pii_exposure": True},
        },
        headers={"X-Tenant-ID": "copilot-pilot-01"},
    )
    assert high.status_code == 200
    high_body = high.json()
    assert high_body["risk_summary"][0]["severity"] in {"High", "Medium"}
    assert high_body["risk_score"] >= 40


def test_audit_export_bundle(client: TestClient) -> None:
    client.post(
        "/evaluate",
        json={
            "actor": "test:export",
            "action": "audit_export_smoke",
            "context": "export test",
            "metadata": {},
        },
        headers={"X-Tenant-ID": "copilot-pilot-01"},
    )
    resp = client.get("/audit/export", headers={"X-Tenant-ID": "copilot-pilot-01"})
    assert resp.status_code == 200
    bundle = resp.json()
    assert bundle["event_count"] >= 1
    assert bundle["events"][0]["integrity_hash"] is not None


def test_get_audit_by_rid(client: TestClient) -> None:
    post = client.post(
        "/evaluate",
        json={
            "actor": "test:rid",
            "action": "lookup",
            "context": "rid lookup test",
            "metadata": {},
        },
        headers={"X-Tenant-ID": "copilot-pilot-01"},
    )
    rid = post.json()["rid"]
    resp = client.get(f"/audit/{rid}", headers={"X-Tenant-ID": "copilot-pilot-01"})
    assert resp.status_code == 200
    assert resp.json()["rid"] == rid
