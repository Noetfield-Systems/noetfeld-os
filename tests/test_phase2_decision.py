"""Phase 2 — decision gate, idempotency, and deterministic replay."""

from __future__ import annotations

from auth import AuthenticatedClient
from decision_engine import decide
from policy_meta import PolicyRegistry
from tests.conftest import SAMPLE_PAYLOAD


def test_decision_returns_rule_set_version(auth_headers):
    client, headers = auth_headers
    response = client.post("/v1/decision", json=SAMPLE_PAYLOAD, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["rule_set_version"] == "1.0.0"
    assert body["tenant_id"] == "tenant-test"
    assert body["provenance"]["final_source"] in {"policy", "corridor"}
    assert response.headers["X-Request-ID"] == body["request_id"]


def test_idempotent_request_id(auth_headers):
    client, headers = auth_headers
    payload = {**SAMPLE_PAYLOAD, "request_id": "rid-idempotent-001"}
    first = client.post("/v1/decision", json=payload, headers=headers)
    second = client.post("/v1/decision", json=payload, headers=headers)
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["audit_id"] == second.json()["audit_id"]


def test_conflicting_request_id_returns_409(auth_headers):
    client, headers = auth_headers
    base = {**SAMPLE_PAYLOAD, "request_id": "rid-conflict-001"}
    first = client.post("/v1/decision", json=base, headers=headers)
    changed = {**base, "credit_score": 680}
    second = client.post("/v1/decision", json=changed, headers=headers)
    assert first.status_code == 200
    assert second.status_code == 409


def test_get_decision_by_request_id(auth_headers):
    client, headers = auth_headers
    payload = {**SAMPLE_PAYLOAD, "request_id": "rid-read-001"}
    created = client.post("/v1/decision", json=payload, headers=headers)
    fetched = client.get("/v1/decision/rid-read-001", headers=headers)
    assert created.status_code == 200
    assert fetched.status_code == 200
    assert fetched.json()["audit_id"] == created.json()["audit_id"]


def test_portal_audits_scoped_to_tenant(auth_headers):
    client, headers = auth_headers
    created = client.post("/v1/decision", json=SAMPLE_PAYLOAD, headers=headers)
    assert created.status_code == 200
    audits = client.get("/portal/audits", headers=headers)
    assert audits.status_code == 200
    assert len(audits.json()) >= 1
    assert all(row["tenant_id"] == "tenant-test" for row in audits.json())


def test_deterministic_replay_same_outcome(temp_runtime):
    _app, raw_key = temp_runtime
    client = AuthenticatedClient(
        key_id="test-key",
        tenant_id="tenant-test",
        org_id="org-test",
        scopes=frozenset({"decision:write", "audit:read"}),
    )
    PolicyRegistry.load()
    first = decide(
        payload={k: v for k, v in SAMPLE_PAYLOAD.items() if k != "applicant_id"},
        applicant_id=SAMPLE_PAYLOAD["applicant_id"],
        client=client,
        request_id="replay-001",
    )
    second = decide(
        payload={k: v for k, v in SAMPLE_PAYLOAD.items() if k != "applicant_id"},
        applicant_id=SAMPLE_PAYLOAD["applicant_id"],
        client=client,
        request_id="replay-002",
    )
    assert first.decision == second.decision
    assert first.composite_score == second.composite_score
    assert first.score_breakdown == second.score_breakdown


def test_corridor_decline_overrides_high_score(temp_runtime):
    client = AuthenticatedClient(
        key_id="test-key",
        tenant_id="tenant-test",
        org_id="org-test",
        scopes=frozenset({"decision:write"}),
    )
    payload = {
        "credit_score": 800,
        "monthly_debt": 4200.0,
        "monthly_income": 6000.0,
        "loan_amount": 250000.0,
        "collateral_value": 320000.0,
        "employment_history_years": 8.0,
        "liquid_reserves_months": 12.0,
    }
    result = decide(
        payload=payload,
        applicant_id="app-high-dti",
        client=client,
        request_id="corridor-decline-001",
    )
    assert result.decision == "DECLINE"
    assert result.corridor_decision == "DECLINE"
    assert result.provenance.final_source == "corridor"
