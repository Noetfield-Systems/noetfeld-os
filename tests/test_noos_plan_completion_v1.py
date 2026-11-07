"""Deterministic plan-completion compiler + dispatch + HMAC contract tests."""

from __future__ import annotations

import hashlib
import hmac
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_plan_completion_dispatch_v1 as dispatch  # noqa: E402
import noos_runway_supervision_adapter_v1 as runway  # noqa: E402
import noos_unified_backlog_compiler_v1 as compiler  # noqa: E402


def test_deepseek_pin_locked():
    row = runway.verify_deepseek_pin()
    assert row["ok"] is True
    assert row["cheap_primary"] == "deepseek-v4-flash"
    assert row["standard_fallback"] == "deepseek-v4-pro"


def test_hmac_sign_stable():
    body = b'{"a":1}'
    sig = runway.sign_hmac_request(
        secret="x" * 32,
        method="POST",
        path="/v1/jobs",
        timestamp="2026-07-19T00:00:00Z",
        nonce="n" * 16,
        body=body,
    )
    body_hash = hashlib.sha256(body).hexdigest()
    canonical = f"POST\n/v1/jobs\n2026-07-19T00:00:00Z\n{'n' * 16}\n{body_hash}"
    expected = hmac.new(b"x" * 32, canonical.encode(), hashlib.sha256).hexdigest()
    assert sig == expected


def test_compile_unified_backlog(tmp_path, monkeypatch):
    monkeypatch.chdir(ROOT)
    row = compiler.compile_backlog(write=True)
    assert row["ok"] is True
    assert "READY" in row["counts"]
    assert "FOUNDER_BLOCKED" in row["counts"]
    assert row["counts"]["READY"] + row["counts"]["COMPLETE"] + row["counts"]["FOUNDER_BLOCKED"] + row[
        "counts"
    ]["BLOCKED_WITH_REASON"] + row["counts"].get("DISPATCHED", 0) == len(row["items"])
    # D1: every item has op_key
    assert all(len(i["op_key"]) == 64 for i in row["items"])
    # Founder items never READY
    assert all(i["status"] != "READY" or i["authority_class"] != "FOUNDER" for i in row["items"])


def test_dispatch_dry_run_never_mutates_or_fabricates_job(monkeypatch):
    monkeypatch.chdir(ROOT)
    monkeypatch.delenv("NOOS_PLAN_COMPLETION_LIVE_INTAKE", raising=False)
    compiler.compile_backlog(write=True)
    dispatch.observe_inflight(write=True)  # reset historical synthetic dry-run entries
    compiler.compile_backlog(write=True)
    first = dispatch.dispatch_once(write=True, allow_dry_run=True)
    assert first["ok"] is True
    assert first["verdict"] in {"DRY_RUN_ONLY", "IDLE_NO_WORK", "THROTTLED_INFLIGHT"}
    assert first.get("job_id") is None
    if first["verdict"] == "DRY_RUN_ONLY":
        op = first["selected"]["op_key"]
        backlog = json.loads((ROOT / ".noos-runtime/plan-completion/backlog-v1.json").read_text())
        matched = [i for i in backlog["items"] if i["op_key"] == op]
        assert matched and matched[0]["status"] == "READY"
        assert not matched[0].get("job_id")
        observed = dispatch.observe_inflight(write=True)
        assert op not in observed.get("completed", [])
        backlog_after = json.loads((ROOT / ".noos-runtime/plan-completion/backlog-v1.json").read_text())
        matched_after = [i for i in backlog_after["items"] if i["op_key"] == op]
        assert matched_after and matched_after[0]["status"] == "READY"


def test_contract_hmac_not_bearer():
    contract = json.loads((ROOT / "data/noetfield-runway-contract-v1.json").read_text())
    auth = contract["required_runtime"]["auth_interface"]
    assert "NOETFIELD-HMAC" in auth
    assert contract["required_runtime"]["endpoints"]["intake"] == "POST /v1/jobs"
    assert "dispatch_repair" not in contract["required_runtime"]["endpoints"]


def test_role_dispatch_produces_preview_artifact_without_bypassing_canonical_dispatch(monkeypatch):
    monkeypatch.chdir(ROOT)
    monkeypatch.delenv("NOOS_PLAN_COMPLETION_LIVE_INTAKE", raising=False)
    import noos_role_runway_dispatch_v1 as role_dispatch

    row = role_dispatch.dispatch_role("research", subject="unit-test")
    assert row["ok"] is True
    assert row["status"] == "PREVIEW_ONLY"
    assert row["productive"] is False
    assert row["dispatch"]["dry_run"] is True
    assert row["dispatch"]["job_id"] is None
    assert row["value_class"] == "risk_reduction"
    assert Path(ROOT / row["receipt_path"]).is_file()


def test_route_map_wired():
    doc = json.loads((ROOT / "motor/registry/bindings/noos-route-map-v1.json").read_text())
    statuses = {b["noos_route"]: b["status"] for b in doc["bindings"]}
    assert statuses["observer_reconciliation"] == "WIRED"
    assert statuses["monitoring_availability"] == "WIRED"
    assert statuses["ci_failure_candidate_repair"] == "WIRED"
    assert statuses["plan_completion_intake"] == "WIRED"


def test_runtime_state_preserved_across_compile_without_fake_completion(monkeypatch):
    monkeypatch.chdir(ROOT)
    monkeypatch.delenv("NOOS_PLAN_COMPLETION_LIVE_INTAKE", raising=False)
    compiler.compile_backlog(write=True)
    dispatch.observe_inflight(write=True)
    compiler.compile_backlog(write=True)
    first = dispatch.dispatch_once(write=True, allow_dry_run=True)
    if first["verdict"] != "DRY_RUN_ONLY":
        return
    op = first["selected"]["op_key"]
    again = compiler.compile_backlog(write=True)
    matched = [i for i in again["items"] if i["op_key"] == op]
    assert matched and matched[0]["status"] == "READY"
    obs = dispatch.observe_inflight(write=True)
    assert op not in obs["completed"]
    final = compiler.compile_backlog(write=True)
    matched2 = [i for i in final["items"] if i["op_key"] == op]
    assert matched2 and matched2[0]["status"] == "READY"


def test_mark_complete_requires_verified_runway_receipt(monkeypatch):
    monkeypatch.chdir(ROOT)
    compiler.compile_backlog(write=True)
    backlog_path = ROOT / ".noos-runtime/plan-completion/backlog-v1.json"
    backlog = json.loads(backlog_path.read_text())
    item = next(i for i in backlog["items"] if i.get("status") == "READY")
    item["status"] = "DISPATCHED"
    item["job_id"] = "rj_" + "a" * 32
    item["dry_run"] = False
    backlog_path.write_text(json.dumps(backlog, indent=2) + "\n")
    result = dispatch.mark_complete(
        op_key=item["op_key"],
        write=False,
        observation={
            "job_id": item["job_id"],
            "op_key": item["op_key"],
            "state": "SUCCEEDED",
            "verification_verdict": "SUCCEEDED",
            "verified_at": "2026-11-06T00:00:00Z",
        },
    )
    assert result["ok"] is False
    assert result["verdict"] == "BLOCKED_TERMINAL_EVIDENCE_REQUIRED"


def test_supabase_sink_skips_without_env(monkeypatch):
    monkeypatch.chdir(ROOT)
    monkeypatch.delenv("NOETFIELD_SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    import noos_plan_completion_supabase_sink_v1 as sink

    row = sink.sync_compile([])
    assert row.get("skipped") is True



def test_runway_adapter_uses_canonical_jobs_route(monkeypatch):
    captured = {}

    def fake_request(method, path, *, payload=None, timeout=runway.HTTP_TIMEOUT):
        captured["method"] = method
        captured["path"] = path
        captured["payload"] = payload
        return {"ok": True, "status": 202, "body": {"job_id": "rj_" + "b" * 32, "status": "QUEUED", "created": True}}

    monkeypatch.setattr(runway, "hmac_request", fake_request)
    monkeypatch.setenv("NOETFIELD_RUNWAY_API_URL", "https://runtime.example")
    monkeypatch.setenv("NOETFIELD_RUNWAY_API_SECRET", "secret")
    row = runway.submit_intake({
        "runway_id": "research",
        "recipe_id": "vendor-decision-brief",
        "recipe_version": "0.1.0",
        "idempotency_key": "op-key-12345678",
        "requested_at": "2026-11-06T00:00:00Z",
        "budget_usd": 0.25,
        "input": {"goal": {"title": "test"}},
    })
    assert captured["method"] == "POST"
    assert captured["path"] == "/v1/jobs"
    assert captured["payload"]["schema_version"] == "1.0"
    assert captured["payload"]["idempotency_key"] == "op-key-12345678"
    assert row["expected_op_key"] == "op-key-12345678"
