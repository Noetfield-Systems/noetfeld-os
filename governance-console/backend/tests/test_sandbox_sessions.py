"""API tests for sandbox session persistence (ship-057)."""

from __future__ import annotations

import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

_test_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_test_db.name}"

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
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    _test_db.close()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_sandbox_session_create_get_patch(client: TestClient) -> None:
    create = client.post(
        "/api/v1/sandbox/sessions",
        json={"email": "dev@example.com", "org": "Acme"},
    )
    assert create.status_code == 201
    body = create.json()
    session_id = body["session_id"]
    assert body["email"] == "dev@example.com"
    assert body["tenant_id"].startswith("sandbox-")
    assert body["evaluates_limit"] == 50

    get_resp = client.get(f"/api/v1/sandbox/sessions/{session_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["org"] == "Acme"

    patch = client.patch(
        f"/api/v1/sandbox/sessions/{session_id}",
        json={"increment_evaluate": True, "trial_step": 4},
    )
    assert patch.status_code == 200
    assert patch.json()["evaluates_used"] == 1
    assert patch.json()["trial_step"] == 4
