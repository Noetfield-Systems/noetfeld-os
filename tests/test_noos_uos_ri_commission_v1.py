"""UOS-RI: no mock passes, no second job on replay, no invented billing."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import noos_uos_ri_commission_v1 as uos  # noqa: E402


def packet():
    return {
        "tenant_id": "tenant-staging-proof",
        "entitlement_id": "ent-staging-proof",
        "runway_id": "research",
        "recipe_id": "vendor-decision-brief",
        "recipe_version": "0.1.0",
        "idempotency_key": "uos-ri-staging-proof-case-001",
        "budget_usd": 0.25,
        "input": {"goal": {"question": "Compare options"}},
    }


def test_invalid_packet_blocks_before_network(monkeypatch):
    monkeypatch.setattr(uos.runway, "preflight", lambda: (_ for _ in ()).throw(AssertionError("must not call")))
    row = uos.commission({"idempotency_key": "short"})
    assert row["status"] == "INVALID_AUTHORIZED_INTAKE"


def test_missing_hmac_blocks_before_dispatch(monkeypatch):
    monkeypatch.setattr(uos.runway, "preflight", lambda: {"ok": False, "verdict": "BLOCKED_RUNWAY_HMAC_SECRET_MISSING"})
    monkeypatch.setattr(uos.runway, "submit_intake", lambda _: (_ for _ in ()).throw(AssertionError("dispatch not permitted")))
    row = uos.commission(packet())
    assert row["status"] == "NOT_CONFIGURED"
    assert row["billed_cost_usd"] is None


def test_live_replay_readback_and_independent_receipt(monkeypatch):
    submissions = []
    monkeypatch.setattr(uos.runway, "preflight", lambda: {"ok": True})
    def submit(inbound):
        submissions.append(inbound)
        return {
            "ok": True,
            "body": {"data": {"job_id": "rj_0123456789abcdef0123456789abcdef"}},
            "intake": {**inbound, "requested_at": inbound.get("requested_at", "2026-11-15T06:00:00Z")},
        }
    monkeypatch.setattr(uos.runway, "submit_intake", submit)
    states = iter(["RUNNING", "SUCCEEDED"])
    monkeypatch.setattr(uos.runway, "get_job", lambda _id: {"ok": True, "body": {"state": next(states)}})
    calls = []
    def hmac(method, path):
        calls.append((method, path))
        if path.endswith("/events"):
            return {"ok": True, "body": {"events": [{"type": "completed"}]}}
        return {"ok": True, "body": {
            "receipt": {
                "independent": True,
                "verdict": "PASS",
                "verifier_id": "verifier-separate",
                "builder_id": "builder-original",
                "artifact_sha256": "a" * 64,
            },
            "usage": {"model": "deepseek-flash", "provider_request_id": "ds-prod-123", "usage_source": "DEEPSEEK_API_USAGE", "input_tokens": 92, "output_tokens": 24},
            "billing": {"billing_reconciled": True, "billed_usd": 0.0032},
        }}
    monkeypatch.setattr(uos.runway, "hmac_request", hmac)
    sleeps = []
    row = uos.commission(packet(), max_observations=2, poll_seconds=0, sleeper=sleeps.append)
    assert row["status"] == "VERIFIED_TECHNICAL_SUCCESS"
    assert row["replay_idempotent"] is True
    assert row["worker_restart_recovery_verified"] is False
    assert row["provider_execution_verified"] is True
    assert row["billed_cost_usd"] == 0.0032
    assert row["realized_roi"] is None
    assert len(submissions) == 2
    assert submissions[0]["idempotency_key"] == submissions[1]["idempotency_key"]
    assert len(calls) == 2


def test_unverified_model_self_report_never_claims_outcome_or_money(monkeypatch):
    monkeypatch.setattr(uos.runway, "preflight", lambda: {"ok": True})
    def submit(inbound):
        return {"ok": True, "body": {"job_id": "job_001"}, "intake": {**inbound, "requested_at": "2026-11-15T06:00:00Z"}}
    monkeypatch.setattr(uos.runway, "submit_intake", submit)
    monkeypatch.setattr(uos.runway, "get_job", lambda _id: {"ok": True, "body": {"status": "SUCCEEDED"}})
    monkeypatch.setattr(uos.runway, "hmac_request", lambda method, path: {"ok": True, "body": {
        "receipt": {"verdict": "PASS", "verifier_id": "builder", "builder_id": "builder", "artifact_sha256": "a" * 64},
        "billing": {"billing_reconciled": False, "billed_usd": 4.0},
    }})
    row = uos.commission(packet(), max_observations=1, sleeper=lambda _: None)
    assert row["status"] == "TERMINAL_UNVERIFIED_OR_FAILED"
    assert row["independent_verdict"] == "UNVERIFIED"
    assert row["billed_cost_usd"] is None
    assert row["cost_source"] == "UNKNOWN_NOT_ZERO"
    assert row["provider_execution_verified"] is False


def test_duplicate_ack_mismatch_stops_without_polling(monkeypatch):
    monkeypatch.setattr(uos.runway, "preflight", lambda: {"ok": True})
    ids = iter(("job_initial", "job_duplicate"))
    monkeypatch.setattr(uos.runway, "submit_intake", lambda inbound: {
        "ok": True, "body": {"job_id": next(ids)}, "intake": {**inbound, "requested_at": "2026-11-15T06:00:00Z"}
    })
    monkeypatch.setattr(uos.runway, "get_job", lambda _: (_ for _ in ()).throw(AssertionError("must not poll")))
    row = uos.commission(packet())
    assert row["status"] == "IDEMPOTENCY_RECONCILIATION_FAILED"
    assert row["replay_idempotent"] is None


def test_independent_receipt_without_real_provider_lineage_is_not_e2e(monkeypatch):
    monkeypatch.setattr(uos.runway, "preflight", lambda: {"ok": True})
    monkeypatch.setattr(uos.runway, "submit_intake", lambda x: {
        "ok": True, "body": {"job_id": "job_001"}, "intake": {**x, "requested_at": "2026-11-15T06:00:00Z"}
    })
    monkeypatch.setattr(uos.runway, "get_job", lambda _: {"ok": True, "body": {"state": "SUCCEEDED"}})
    monkeypatch.setattr(uos.runway, "hmac_request", lambda method, path: {"ok": True, "body": {
        "receipt": {
            "independent": True, "verdict": "PASS",
            "verifier_id": "separate-verifier", "builder_id": "builder",
            "artifact_sha256": "b" * 64
        },
        "usage": {"model": "deepseek-flash", "input_tokens": 22, "output_tokens": 15}
    }})
    row = uos.commission(packet(), max_observations=1)
    assert row["independent_verdict"] == "PASS"
    assert row["provider_execution_verified"] is False
    assert row["status"] == "MODEL_EXECUTION_EVIDENCE_MISSING"


def test_real_runway_terminal_SUCCEEDED_produces_artifact_metadata(monkeypatch):
    monkeypatch.setattr(uos.runway, "preflight", lambda: {"ok": True})
    monkeypatch.setattr(uos.runway, "submit_intake", lambda x: {
        "ok": True, "body": {"job_id": "rj_" + "a" * 32},
        "intake": {**x, "requested_at": "2026-11-15T06:00:00Z"}
    })
    monkeypatch.setattr(uos.runway, "get_job", lambda _: {"ok": True, "body": {"status": "SUCCEEDED"}})
    monkeypatch.setattr(uos.runway, "hmac_request", lambda method, path: {"ok": True, "body": {
        "status": "succeeded",
        "artifacts": [{"artifact_id": "pdf-1", "content_sha256": "b" * 64}],
    }})
    row = uos.commission(packet(), max_observations=1)
    assert row["runtime_terminal_state"] == "SUCCEEDED"
    assert row["runtime_result_readback"] is True
    assert row["runtime_artifact_digests"] == [{"artifact_id": "pdf-1", "sha256": "b" * 64}]
    assert row["status"] == "TERMINAL_UNVERIFIED_OR_FAILED"
    assert row["provider_execution_verified"] is False


def test_failed_live_intake_records_only_safe_status_not_secret(monkeypatch):
    monkeypatch.setattr(uos.runway, "preflight", lambda: {"ok": True})
    monkeypatch.setattr(uos.runway, "submit_intake", lambda _packet: {
        "ok": False, "status": 401,
        "body": {"error": "AUTH_FAILED", "detail": "SECRET_DO_NOT_LOG"},
    })
    result = uos.commission(packet())
    assert result["status"] == "INTAKE_UNCONFIRMED"
    assert result["intake_http_status"] == 401
    assert result["intake_error_code"] == "AUTH_FAILED"
    assert "SECRET_DO_NOT_LOG" not in str(result)


def test_nonce_rpc_missing_categorized_without_sensitive_sql(monkeypatch):
    monkeypatch.setattr(uos.runway, "preflight", lambda: {"ok": True})
    monkeypatch.setattr(uos.runway, "submit_intake", lambda _packet: {
        "ok": False, "status": 401,
        "body": {"error": "AUTH_FAILED", "detail": (
            "supabase rpc consume_runway_runtime_nonce_v1 HTTP 404: "
            "PGRST202 Could not find the function public.consume_runway_runtime_nonce_v1 "
            "internal-sensitive-identifier-SHOULD-NOT-PRINT"
        )},
    })
    result = uos.commission(packet())
    assert result["intake_http_status"] == 401
    assert result["intake_error_code"] == "AUTH_FAILED"
    assert result["auth_backend_category"] == "NONCE_RPC_MISSING"
    assert "internal-sensitive-identifier" not in str(result)


def test_nonce_rpc_http_code_sanitized_and_readable(monkeypatch):
    monkeypatch.setattr(uos.runway, "preflight", lambda: {"ok": True})
    monkeypatch.setattr(uos.runway, "submit_intake", lambda _packet: {
        "ok": False, "status": 401,
        "body": {"error": "AUTH_FAILED",
                 "detail": "supabase rpc consume_runway_runtime_nonce_v1 HTTP 404: "
                           'PGRST202 could not find this function secret-value-should-not-appear'},
    })
    result = uos.commission(packet())
    assert result["nonce_rpc_http_status"] == 404
    assert result["nonce_rpc_error_code"] == "PGRST202"
    assert "secret-value-should-not-appear" not in str(result)
