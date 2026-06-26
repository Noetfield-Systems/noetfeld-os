"""Phase 3 — evidence export + TLE mapping tests."""

from __future__ import annotations

import json
import re

import pytest

from export.tle_mapper import audit_to_tle_v1, build_export_bundle
from tests.conftest import SAMPLE_PAYLOAD


TLE_ID_PATTERN = re.compile(r"^TLE-[A-Z0-9-]+$")
DIGEST_PATTERN = re.compile(r"^sha256:[a-f0-9]{64}$")


def _post_decision(auth_headers):
    client, headers = auth_headers
    resp = client.post("/v1/decision", json=SAMPLE_PAYLOAD, headers=headers)
    assert resp.status_code == 200
    return resp.json()


def test_tle_mapper_required_fields():
    record = {
        "id": 42,
        "request_id": "req-phase3-001",
        "tenant_id": "tenant-test",
        "applicant_id": "app-001",
        "decision": "APPROVE",
        "composite_score": 78.5,
        "created_at": "2026-05-29T12:00:00+00:00",
        "input_payload": SAMPLE_PAYLOAD,
        "corridor_breaches": [],
        "rule_set_id": "noetfeld-credit-v1",
        "rule_set_version": "1.0.0",
        "policy_base_hash": "abc123",
        "policy_corridor_hash": "def456",
    }
    tle = audit_to_tle_v1(record)
    assert TLE_ID_PATTERN.match(tle["tle_id"])
    assert tle["status"] == "Approved"
    assert 0 <= tle["confidence_score"] <= 1
    assert len(tle["evidence"]) >= 1
    assert len(tle["approval_chain"]) >= 1
    assert DIGEST_PATTERN.match(tle["audit_digest"])


def test_decline_maps_to_rejected():
    record = {
        "id": 7,
        "request_id": "req-decline",
        "tenant_id": "t1",
        "applicant_id": "a1",
        "decision": "DECLINE",
        "composite_score": 30.0,
        "created_at": "2026-05-29T12:00:00+00:00",
        "input_payload": {},
        "corridor_breaches": ["dti_ratio"],
        "rule_set_id": "noetfeld-credit-v1",
        "rule_set_version": "1.0.0",
        "policy_base_hash": "x",
        "policy_corridor_hash": "y",
    }
    tle = audit_to_tle_v1(record)
    assert tle["status"] == "Rejected"
    assert any("dti_ratio" in r["description"] for r in tle["risk_summary"])


def test_export_json_endpoint(auth_headers):
    decision = _post_decision(auth_headers)
    client, headers = auth_headers
    audit_id = decision["audit_id"]

    resp = client.get(f"/portal/audits/{audit_id}/export", headers=headers)
    assert resp.status_code == 200
    bundle = resp.json()
    assert bundle["export_version"] == "1.0"
    assert bundle["request_id"] == decision["request_id"]
    assert bundle["tle_v1"]["source_rid"] == decision["request_id"]
    assert DIGEST_PATTERN.match(bundle["tle_v1"]["audit_digest"])


def test_export_by_request_id(auth_headers):
    decision = _post_decision(auth_headers)
    client, headers = auth_headers

    resp = client.get(
        f"/portal/audits/by-request/{decision['request_id']}/export",
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["audit_id"] == decision["audit_id"]


def test_export_pdf_endpoint(auth_headers):
    decision = _post_decision(auth_headers)
    client, headers = auth_headers

    resp = client.get(f"/portal/audits/{decision['audit_id']}/export.pdf", headers=headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content[:4] == b"%PDF"


def test_export_tenant_isolation(auth_headers):
    decision = _post_decision(auth_headers)
    client, _headers = auth_headers

    resp = client.get(
        f"/portal/audits/{decision['audit_id']}/export",
        headers={"X-API-Key": "wrong-key"},
    )
    assert resp.status_code in (401, 403, 404)


def test_build_export_bundle_shape():
    record = {
        "id": 1,
        "request_id": "r1",
        "tenant_id": "t1",
        "applicant_id": "a1",
        "decision": "REVIEW",
        "composite_score": 55.0,
        "created_at": "2026-05-29T12:00:00+00:00",
        "input_payload": {},
        "corridor_breaches": [],
        "rule_set_id": "noetfeld-credit-v1",
        "rule_set_version": "1.0.0",
        "policy_base_hash": "b",
        "policy_corridor_hash": "c",
        "policy_decision": "REVIEW",
        "corridor_decision": None,
        "score_breakdown": {"credit": 0.5},
    }
    bundle = build_export_bundle(record)
    assert bundle["tle_v1"]["status"] == "Conditional"
    assert "audit" in bundle and "tle_v1" in bundle
