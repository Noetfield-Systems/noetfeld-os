"""Shared pytest fixtures for Noetfield OS Phase 2 tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import config
from auth import KEY_STORE, _hash_key
from database import init_db
from policy_meta import PolicyRegistry


SAMPLE_PAYLOAD = {
    "applicant_id": "app-001",
    "credit_score": 720,
    "monthly_debt": 1200.0,
    "monthly_income": 6000.0,
    "loan_amount": 250000.0,
    "collateral_value": 320000.0,
    "employment_history_years": 4.0,
    "liquid_reserves_months": 6.0,
}


@pytest.fixture()
def temp_runtime(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    keys_path = tmp_path / "api_keys.local.json"
    raw_key = "test-api-key-phase2"
    salt = "test-salt"
    payload = {
        "salt": salt,
        "keys": [
            {
                "key_id": "test-key",
                "key_hash": _hash_key(raw_key, salt=salt),
                "tenant_id": "tenant-test",
                "org_id": "org-test",
                "scopes": ["decision:write", "audit:read"],
            }
        ],
    }
    keys_path.write_text(json.dumps(payload), encoding="utf-8")

    monkeypatch.setattr(config, "DB_PATH", db_path)
    monkeypatch.setattr(config, "API_KEYS_PATH", keys_path)

    PolicyRegistry.reset()
    init_db()
    KEY_STORE.load(keys_path)
    PolicyRegistry.load()

    from run import create_app

    app = create_app()
    yield app, raw_key
    PolicyRegistry.reset()


@pytest.fixture()
def client(temp_runtime):
    from fastapi.testclient import TestClient

    app, raw_key = temp_runtime
    return TestClient(app), raw_key


@pytest.fixture()
def auth_headers(client):
    test_client, raw_key = client
    return test_client, {"X-API-Key": raw_key}
