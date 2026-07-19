"""Tests for durable NOOS health incident supervision (Missions 2 + 4)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_health_incident_v1 as inc  # noqa: E402


def _transport(tmp_path) -> inc.FileDurableTransport:
    return inc.FileDurableTransport(tmp_path / "incidents.json")


def test_routing_owner_boundaries():
    assert inc.route_for("integrator_status")["owner"] == "noos"
    assert inc.route_for("trustfield_registry")["owner"] == "trustfield"
    assert inc.route_for("sourcea_cloud_queue")["owner"] == "sourcea"
    assert inc.route_for("trustfield_partner_access")["owner"] == "railway"
    # unknown → default noos triage
    assert inc.route_for("totally_unknown_key")["owner"] == "noos"


def test_incident_has_all_required_bindings(tmp_path):
    i = inc.make_incident(
        fix_queue_key="integrator_status",
        source_receipt="receipts/proof/x.json",
        source_run_url="https://github.com/o/r/actions/runs/1",
        source_sha="abc123",
    )
    row = i.to_row()
    for key in (
        "incident_id", "idempotency_key", "source_receipt", "source_run_url", "source_sha",
        "failure_type", "target_owner", "target_repository", "handler_id", "authority_class",
        "attempt", "retry_ceiling", "state", "worker_run_id", "terminal_receipt",
    ):
        assert key in row, f"missing binding {key}"
    assert row["state"] == inc.STATE_OPEN


def test_persist_is_idempotent(tmp_path):
    t = _transport(tmp_path)
    i = inc.make_incident(fix_queue_key="integrator_status", source_sha="sha1", source_run_url="run1")
    r1 = inc.persist_incident(i, transport=t)
    r2 = inc.persist_incident(i, transport=t)
    assert r1["duplicate"] is False
    assert r2["duplicate"] is True
    assert len(t.list_open()) == 1


def test_distinct_source_sha_distinct_incident(tmp_path):
    t = _transport(tmp_path)
    a = inc.make_incident(fix_queue_key="integrator_status", source_sha="shaA")
    b = inc.make_incident(fix_queue_key="integrator_status", source_sha="shaB")
    assert a.idempotency_key != b.idempotency_key
    inc.persist_incident(a, transport=t)
    inc.persist_incident(b, transport=t)
    assert len(t.list_open()) == 2


def test_incident_survives_process_restart(tmp_path):
    path = tmp_path / "incidents.json"
    i = inc.make_incident(fix_queue_key="integrator_status", source_sha="sha1")
    inc.persist_incident(i, transport=inc.FileDurableTransport(path))
    # Fresh transport instance = simulated new process/GHA run.
    reopened = inc.read_open_incidents(transport=inc.FileDurableTransport(path))
    assert reopened["actionable"] == 1
    assert reopened["open"][0]["incident_id"] == i.incident_id


def test_reconciler_reads_durable_actionable(tmp_path):
    t = _transport(tmp_path)
    res = inc.file_from_fix_queue(
        ["integrator_status", "autorun_critique"],
        source_receipt="r.json", source_run_url="run1", source_sha="sha1",
        transport=t,
    )
    assert res["count"] == 2
    assert inc.read_open_incidents(transport=t)["actionable"] == 2


def test_dispatch_requires_run_id_to_resolve(tmp_path):
    t = _transport(tmp_path)
    i = inc.make_incident(fix_queue_key="integrator_status", source_sha="sha1")
    inc.persist_incident(i, transport=t)
    # handler returns ok but NO run_id → must not resolve
    handlers = {i.handler_id: lambda _row: {"ok": True, "run_id": None}}
    res = inc.dispatch_incident(i.to_row(), transport=t, handlers=handlers)
    assert res["ok"] is False
    assert res["state"] != inc.STATE_RESOLVED

    # handler returns a concrete run id → resolves, records worker_run_id
    handlers = {i.handler_id: lambda _row: {"ok": True, "run_id": "noos-run-42"}}
    res2 = inc.dispatch_incident(i.to_row(), transport=t, handlers=handlers)
    assert res2["ok"] is True
    assert res2["state"] == inc.STATE_RESOLVED
    assert res2["worker_run_id"] == "noos-run-42"
    # terminal read-back
    assert inc.read_open_incidents(transport=t)["actionable"] == 0


def test_handler_unavailable_then_retry_exhaustion(tmp_path):
    t = _transport(tmp_path)
    i = inc.make_incident(fix_queue_key="integrator_status", source_sha="sha1", retry_ceiling=2)
    inc.persist_incident(i, transport=t)
    row = i.to_row()
    r1 = inc.dispatch_incident(row, transport=t, handlers={})  # attempt 1
    assert r1["state"] == inc.STATE_OPEN and r1["attempt"] == 1
    row["attempt"] = 1
    r2 = inc.dispatch_incident(row, transport=t, handlers={})  # attempt 2 == ceiling
    assert r2["state"] == inc.STATE_RETRY_EXHAUSTED
    assert r2["founder_escalation"] is False


def test_cross_repo_owner_without_endpoint_blocks(tmp_path):
    t = _transport(tmp_path)
    i = inc.make_incident(fix_queue_key="trustfield_registry", source_sha="sha1")
    inc.persist_incident(i, transport=t)
    res = inc.dispatch_incident(i.to_row(), transport=t, handlers={}, owner_endpoints={})
    assert res["state"] == inc.STATE_BLOCKED_EXTERNAL
    assert res["verdict"] == "BLOCKED_EXTERNAL_OWNER_ENDPOINT"
    assert res["founder_escalation"] is False


def test_cross_repo_owner_with_endpoint_dispatches(tmp_path):
    t = _transport(tmp_path)
    i = inc.make_incident(fix_queue_key="trustfield_registry", source_sha="sha1")
    inc.persist_incident(i, transport=t)
    endpoints = {i.handler_id: lambda _row: {"ok": True, "run_id": "tf-job-7"}}
    res = inc.dispatch_incident(i.to_row(), transport=t, owner_endpoints=endpoints)
    assert res["ok"] is True
    assert res["worker_run_id"] == "tf-job-7"


def test_founder_escalation_suppressed_for_ordinary_failures(tmp_path):
    t = _transport(tmp_path)
    i = inc.make_incident(fix_queue_key="integrator_status", source_sha="sha1", retry_ceiling=1)
    inc.persist_incident(i, transport=t)
    res = inc.dispatch_incident(i.to_row(), transport=t, handlers={})
    assert res.get("founder_escalation") is False


def test_supabase_blocker_when_unconfigured(monkeypatch):
    for v in ("NOETFIELD_SUPABASE_URL", "SUPABASE_URL", "NOETFIELD_SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_SERVICE_ROLE_KEY"):
        monkeypatch.delenv(v, raising=False)
    i = inc.make_incident(fix_queue_key="integrator_status", source_sha="sha1")
    res = inc.persist_incident(i)  # no transport → default → None
    assert res["ok"] is False
    assert res["verdict"] == "BLOCKED_DURABLE_STORE_NOT_CONFIGURED"
    assert "NOETFIELD_SUPABASE_URL" in res["missing"]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
