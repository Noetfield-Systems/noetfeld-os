"""Phase 2 — authentication and fail-closed gate tests."""

from __future__ import annotations

from auth import KEY_STORE
from database import init_db
from tests.conftest import SAMPLE_PAYLOAD


def test_key_store_load_respects_monkeypatched_api_keys_path(temp_runtime):
    """Regression: uvicorn lifespan calls KEY_STORE.load() without a path."""
    _app, raw_key = temp_runtime
    init_db()
    KEY_STORE.load()
    client = KEY_STORE.authenticate(raw_key)
    assert client is not None
    assert client.key_id == "test-key"


def test_missing_api_key_returns_401(auth_headers):
    client, _headers = auth_headers
    response = client.post("/v1/decision", json=SAMPLE_PAYLOAD)
    assert response.status_code == 401


def test_invalid_api_key_returns_403(auth_headers):
    client, _headers = auth_headers
    response = client.post(
        "/v1/decision",
        json=SAMPLE_PAYLOAD,
        headers={"X-API-Key": "invalid-key"},
    )
    assert response.status_code == 403


def test_readiness_ok(auth_headers):
    client, headers = auth_headers
    response = client.get("/readiness", headers=headers)
    assert response.status_code == 200
    assert response.json()["ready"] is True


def test_health_includes_policy_meta(auth_headers):
    client, headers = auth_headers
    response = client.get("/health", headers=headers)
    body = response.json()
    assert body["status"] == "ok"
    assert body["policy"]["rule_set_version"] == "1.0.0"


def test_v1_meta(auth_headers):
    client, headers = auth_headers
    response = client.get("/v1/meta", headers=headers)
    assert response.status_code == 200
    assert response.json()["rule_set_id"] == "noetfeld-credit-v1"
