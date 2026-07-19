"""Repair fix 1 — the actual root-cause closure.

The liveness heartbeat (upsert_loop_liveness) used to be gated behind cycle
success: `if state_after in ("COMPLETE", "IDLE_NO_WORK")`. A cycle that
completed its steps fine but whose Supabase sink write failed (sink_acked
=False -> state_after="BLOCKED_WITH_REASON") silently skipped the heartbeat
entirely — even though the loop genuinely ticked and Railway was genuinely
alive. This is what let noos_loop_registry.last_fired_at go stale for hours
without any visible error. These tests directly encode that the heartbeat is
now called unconditionally, with the real state, on every code path.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import noos_loop_runner_v1 as runner  # noqa: E402
import noos_vault_paths_v1  # noqa: E402


@pytest.fixture(autouse=True)
def _isolated_runtime(tmp_path, monkeypatch):
    """Redirect RUNTIME so the test never writes into the real repo tree, and
    ensure no real Supabase credentials leak in from the environment (sink_cycle
    must naturally fail-closed to BLOCKED_WITH_REASON without them)."""
    monkeypatch.setattr(runner, "RUNTIME", tmp_path)
    monkeypatch.setattr(noos_vault_paths_v1, "load_platform_env", lambda: {})
    for key in (
        "NOETFIELD_SUPABASE_URL",
        "SUPABASE_URL",
        "NOETFIELD_SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
    ):
        monkeypatch.delenv(key, raising=False)


def _recording_liveness_stub(calls: list[dict[str, Any]]):
    def _stub(**kwargs):
        calls.append(kwargs)
        return {"ok": True}

    return _stub


def _passing_step_loop(loop_id: str) -> dict[str, Any]:
    return {
        "id": loop_id,
        "event_type": f"test_{loop_id}_tick",
        "interval_minutes": 5,
        "steps": [{"name": "noop", "cmd": ["python3", "-c", "print('ok')"]}],
    }


def test_heartbeat_called_when_sink_write_fails(monkeypatch) -> None:
    """The core bug: cycle succeeds, sink is unreachable (no Supabase env
    configured, mirroring a transient outage) -> state_after must be
    BLOCKED_WITH_REASON, and the heartbeat must STILL have been called with
    that real state — not silently skipped."""
    calls: list[dict[str, Any]] = []
    monkeypatch.setattr(runner, "upsert_loop_liveness", _recording_liveness_stub(calls))
    monkeypatch.setattr(runner, "sync_meta_liveness_rows", lambda: {"ok": True})

    cycle = runner.execute_loop(_passing_step_loop("liveness-decouple-a"), self_heal=False)

    assert cycle["state_after"] == "BLOCKED_WITH_REASON"
    assert cycle["d4"]["sink_acked"] is False
    assert len(calls) == 1, "upsert_loop_liveness must be called exactly once, unconditionally"
    assert calls[0]["last_cycle_status"] == "BLOCKED_WITH_REASON"
    assert calls[0]["loop_id"] == "liveness-decouple-a"
    assert cycle["liveness_upsert"] == {"ok": True}


def test_heartbeat_called_on_step_failure(monkeypatch) -> None:
    """A genuinely failing step (execute_ok=False) -> FAILED_WITH_RECEIPT.
    Heartbeat must still fire with the real state."""
    calls: list[dict[str, Any]] = []
    monkeypatch.setattr(runner, "upsert_loop_liveness", _recording_liveness_stub(calls))
    monkeypatch.setattr(runner, "sync_meta_liveness_rows", lambda: {"ok": True})

    failing_loop = {
        "id": "liveness-decouple-b",
        "event_type": "test_liveness_decouple_b_tick",
        "interval_minutes": 5,
        "steps": [{"name": "boom", "cmd": ["python3", "-c", "import sys; sys.exit(1)"]}],
    }
    cycle = runner.execute_loop(failing_loop, self_heal=False)

    assert cycle["state_after"] == "FAILED_WITH_RECEIPT"
    assert len(calls) == 1
    assert calls[0]["last_cycle_status"] == "FAILED_WITH_RECEIPT"


def test_heartbeat_still_called_on_success_path(monkeypatch) -> None:
    """Success path must be unaffected: still one call, still the right state.
    (This is the byte-identical-behavior claim from the repair plan.)"""
    calls: list[dict[str, Any]] = []
    monkeypatch.setattr(runner, "upsert_loop_liveness", _recording_liveness_stub(calls))
    monkeypatch.setattr(runner, "sync_meta_liveness_rows", lambda: {"ok": True})
    monkeypatch.setattr(runner, "sink_cycle", lambda cycle, *, factory_id: {"ok": True})

    cycle = runner.execute_loop(_passing_step_loop("liveness-decouple-c"), self_heal=False)

    assert cycle["state_after"] == "COMPLETE"
    assert len(calls) == 1
    assert calls[0]["last_cycle_status"] == "COMPLETE"


def test_no_work_loop_still_heartbeats(monkeypatch) -> None:
    """A loop with zero steps takes the no_work=True / IDLE_NO_WORK branch,
    which never touches advance_state at all — must still heartbeat."""
    calls: list[dict[str, Any]] = []
    monkeypatch.setattr(runner, "upsert_loop_liveness", _recording_liveness_stub(calls))
    monkeypatch.setattr(runner, "sync_meta_liveness_rows", lambda: {"ok": True})

    empty_loop = {
        "id": "liveness-decouple-d",
        "event_type": "test_liveness_decouple_d_tick",
        "interval_minutes": 5,
        "steps": [],
    }
    cycle = runner.execute_loop(empty_loop, self_heal=False)

    assert cycle["state_after"] == "IDLE_NO_WORK"
    assert len(calls) == 1
    assert calls[0]["last_cycle_status"] == "IDLE_NO_WORK"


def test_cas_rejection_branch_still_heartbeats(monkeypatch) -> None:
    """The smaller, second instance of the same bug: a CAS collision took an
    early return that used to skip the heartbeat entirely."""
    calls: list[dict[str, Any]] = []
    monkeypatch.setattr(runner, "upsert_loop_liveness", _recording_liveness_stub(calls))
    monkeypatch.setattr(runner, "acquire_cycle_number", lambda loop_id: (None, {"reason": "cas_mismatch"}))

    cycle = runner.execute_loop(_passing_step_loop("liveness-decouple-e"), self_heal=False)

    assert cycle["state_after"] == "BLOCKED_WITH_REASON"
    assert cycle["blocker_reason"] == "cas_rejected:cas_mismatch"
    assert len(calls) == 1
    assert calls[0]["last_cycle_status"] == "BLOCKED_WITH_REASON"
    assert cycle["liveness_upsert"] == {"ok": True}
