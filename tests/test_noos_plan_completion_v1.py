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
        path="/v1/intake",
        timestamp="2026-07-19T00:00:00Z",
        nonce="n" * 16,
        body=body,
    )
    body_hash = hashlib.sha256(body).hexdigest()
    canonical = f"POST\n/v1/intake\n2026-07-19T00:00:00Z\n{'n' * 16}\n{body_hash}"
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


def test_dispatch_idempotent_dry_run(monkeypatch):
    monkeypatch.chdir(ROOT)
    monkeypatch.delenv("NOOS_PLAN_COMPLETION_LIVE_INTAKE", raising=False)
    compiler.compile_backlog(write=True)
    first = dispatch.dispatch_once(write=True, allow_dry_run=True)
    assert first["ok"] is True
    assert first["verdict"] in {"DISPATCHED", "IDLE_NO_WORK", "THROTTLED_INFLIGHT"}
    if first["verdict"] == "DISPATCHED":
        op = first["selected"]["op_key"]
        second = dispatch.dispatch_once(write=True, allow_dry_run=True)
        # concurrency max 1 → throttle or next item, never duplicate same op_key as READY
        backlog = json.loads((ROOT / ".noos-runtime/plan-completion/backlog-v1.json").read_text())
        matched = [i for i in backlog["items"] if i["op_key"] == op]
        assert matched and matched[0]["status"] == "DISPATCHED"
        assert second["ok"] is True


def test_contract_hmac_not_bearer():
    contract = json.loads((ROOT / "data/noetfield-runway-contract-v1.json").read_text())
    auth = contract["required_runtime"]["auth_interface"]
    assert "NOETFIELD-HMAC" in auth
    assert contract["required_runtime"]["endpoints"]["intake"] == "POST /v1/intake"
    assert "dispatch_repair" not in contract["required_runtime"]["endpoints"]


def test_role_dispatch_produces_artifact(monkeypatch):
    monkeypatch.chdir(ROOT)
    import noos_role_runway_dispatch_v1 as role_dispatch

    row = role_dispatch.dispatch_role("research", subject="unit-test")
    assert row["ok"] is True
    assert row["productive"] is True
    assert row["value_class"] == "risk_reduction"
    assert Path(ROOT / row["receipt_path"]).is_file()


def test_route_map_wired():
    doc = json.loads((ROOT / "motor/registry/bindings/noos-route-map-v1.json").read_text())
    statuses = {b["noos_route"]: b["status"] for b in doc["bindings"]}
    assert statuses["observer_reconciliation"] == "WIRED"
    assert statuses["monitoring_availability"] == "WIRED"
    assert statuses["ci_failure_candidate_repair"] == "WIRED"
    assert statuses["plan_completion_intake"] == "WIRED"
