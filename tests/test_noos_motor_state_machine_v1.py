"""NF-NOOS-MOTOR-V1-FULL-RUNWAY Phase 3 — motor state machine invariant gate.

One test per enforced invariant (1-13) plus the happy path and the invalid
transition wall. Deterministic: clock is injected as ISO strings.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_motor_state_machine_v1 as m  # noqa: E402

T0 = "2026-07-18T00:00:00Z"
T1 = "2026-07-18T00:00:05Z"
T2 = "2026-07-18T00:00:10Z"
T3 = "2026-07-18T00:00:20Z"


def _run(**kw):
    return m.MotorExecution(task_kind="demo", payload={"x": 1}, now=T0, producer="test", **kw)


def _drive_to_completed():
    ex = _run()
    ex.plan(now=T0, dispatch_id="dsp_1").dispatch(now=T0)
    ex.claim(now=T0, owner="worker-A", lease_ttl_seconds=60).start(now=T1)
    ex.commit_output(now=T2, output={"result": 42}, artifact_uri="file:///out/42.json")
    ex.complete(now=T3)
    return ex


# ---- happy path ------------------------------------------------------------
def test_happy_path_reaches_completed():
    ex = _drive_to_completed()
    assert ex.state == m.COMPLETED
    assert ex.to_record()["is_terminal"] is True
    states = [h["state"] for h in ex.history]
    assert states == [m.ACCEPTED, m.PLANNED, m.DISPATCHED, m.CLAIMED, m.RUNNING, m.OUTPUT_COMMITTED, m.COMPLETED]


# ---- invariant 1: cannot complete before start -----------------------------
def test_inv1_cannot_complete_before_start():
    ex = _run()
    ex.plan(now=T0).dispatch(now=T0).claim(now=T0, owner="w", lease_ttl_seconds=60)
    # not started, no output committed
    with pytest.raises(m.InvalidTransition):
        ex.complete(now=T1)


def test_inv1_cannot_complete_without_output():
    ex = _run()
    ex.plan(now=T0).dispatch(now=T0).claim(now=T0, owner="w", lease_ttl_seconds=60).start(now=T1)
    with pytest.raises(m.InvalidTransition):
        ex.complete(now=T2)  # RUNNING -> COMPLETED not allowed (need OUTPUT_COMMITTED)


# ---- invariant 2: terminal cannot return to RUNNING ------------------------
def test_inv2_terminal_cannot_return_to_running():
    ex = _drive_to_completed()
    assert not m.can_transition(m.COMPLETED, m.RUNNING)
    with pytest.raises(m.InvalidTransition):
        ex.transition(m.RUNNING, now=T3)
    fex = _run()
    fex.fail(now=T1, error_code="boom", error_summary="x")
    assert not m.can_transition(m.FAILED, m.RUNNING)


# ---- invariant 3: duplicate idempotency key -> one logical run --------------
def test_inv3_duplicate_idempotency_key_dedupes():
    led = m.MotorLedger()
    a, created_a = led.submit(task_kind="demo", payload={"x": 1}, now=T0, producer="p")
    b, created_b = led.submit(task_kind="demo", payload={"x": 1}, now=T1, producer="p")
    assert created_a is True and created_b is False
    assert a.execution_id == b.execution_id  # same logical run
    c, created_c = led.submit(task_kind="demo", payload={"x": 2}, now=T1, producer="p")
    assert created_c is True and c.execution_id != a.execution_id


# ---- invariant 4: a lease has owner and expiry -----------------------------
def test_inv4_lease_has_owner_and_expiry():
    ex = _run()
    ex.plan(now=T0).dispatch(now=T0).claim(now=T0, owner="worker-A", lease_ttl_seconds=30)
    assert ex.lease["owner"] == "worker-A"
    assert ex.lease["expires_at"] == "2026-07-18T00:00:30Z"


# ---- invariant 5: expired lease recovered deterministically -----------------
def test_inv5_expired_lease_reclaim():
    ex = _run()
    ex.plan(now=T0).dispatch(now=T0).claim(now=T0, owner="worker-A", lease_ttl_seconds=30)
    assert ex.lease_expired(now="2026-07-18T00:00:29Z") is False
    assert ex.lease_expired(now="2026-07-18T00:00:31Z") is True
    ex.reclaim(now="2026-07-18T00:00:31Z", owner="worker-B", lease_ttl_seconds=30)
    assert ex.state == m.CLAIMED
    assert ex.lease["owner"] == "worker-B"
    with pytest.raises(m.InvalidTransition):  # not expired now
        ex.reclaim(now="2026-07-18T00:00:32Z", owner="worker-C", lease_ttl_seconds=30)


# ---- invariants 6 & 7: bounded, visible retry with backoff -----------------
def test_inv6_7_bounded_retry_and_backoff():
    assert m.backoff_seconds(0) == 5.0
    assert m.backoff_seconds(1) == 10.0
    assert m.backoff_seconds(2) == 20.0
    assert m.backoff_seconds(100) == 900.0  # capped
    ex = _run(max_retries=2)
    ex.plan(now=T0).dispatch(now=T0).claim(now=T0, owner="w", lease_ttl_seconds=60).start(now=T1)
    ex.fail(now=T2, error_code="e", error_summary="s")
    ex.schedule_retry(now=T2)
    assert ex.retry_count == 1
    ex.dispatch(now=T2)  # RETRY_SCHEDULED -> DISPATCHED
    ex.fail(now=T3, error_code="e", error_summary="s")
    ex.schedule_retry(now=T3)
    assert ex.retry_count == 2
    ex.dispatch(now=T3)
    ex.fail(now=T3, error_code="e", error_summary="s")
    with pytest.raises(m.InvalidTransition):  # budget exhausted
        ex.schedule_retry(now=T3)


# ---- invariant 8: terminal failure is recorded -----------------------------
def test_inv8_failure_recorded():
    ex = _run()
    ex.plan(now=T0).dispatch(now=T0).fail(now=T1, error_code="dispatch_lost", error_summary="no ack")
    rec = ex.to_record()
    assert rec["state"] == m.FAILED
    assert rec["error_code"] == "dispatch_lost"
    assert rec["error_summary"] == "no ack"


# ---- invariant 9: dead-letter inspectable and replayable -------------------
def test_inv9_dead_letter_inspectable_and_replayable():
    led = m.MotorLedger()
    ex, _ = led.submit(task_kind="demo", payload={"x": 1}, now=T0, producer="p", max_retries=0)
    ex.plan(now=T0).dispatch(now=T0).fail(now=T1, error_code="e", error_summary="s")
    ex.dead_letter(now=T1, reason="max_retries_exhausted")
    assert [d.execution_id for d in led.dead_letters()] == [ex.execution_id]
    child = led.replay(ex.execution_id, now=T2, payload={"x": 1})
    assert child.execution_id != ex.execution_id


# ---- invariant 10: replay preserves lineage --------------------------------
def test_inv10_replay_preserves_lineage():
    led = m.MotorLedger()
    ex, _ = led.submit(task_kind="demo", payload={"x": 1}, now=T0, producer="p")
    ex.plan(now=T0).dispatch(now=T0).fail(now=T1, error_code="e", error_summary="s")
    child = led.replay(ex.execution_id, now=T2, payload={"x": 1})
    assert child.root_execution_id == ex.root_execution_id
    assert child.correlation_id == ex.correlation_id
    assert child.attempt == ex.attempt + 1
    assert child.execution_origin == m.ORIGIN_REPLAY  # honestly labelled replay


# ---- invariant 11: repair never mutates historical organic provenance ------
def test_inv11_repair_does_not_rewrite_organic_provenance():
    ex = _run(execution_origin=m.ORIGIN_ORGANIC)
    ex.plan(now=T0).dispatch(now=T0).fail(now=T1, error_code="e", error_summary="s")
    ex.apply_repair(now=T2, repair_recipe="NF-MOTOR-RECEIPT-WRITER-REPAIR-001")
    assert ex.execution_origin == m.ORIGIN_ORGANIC  # unchanged
    assert ex.repairs[0]["recipe"] == "NF-MOTOR-RECEIPT-WRITER-REPAIR-001"
    with pytest.raises(m.ProvenanceViolation):
        ex.transition(m.REPLAY_REQUESTED, now=T3, execution_origin=m.ORIGIN_REPAIR)


# ---- invariant 12: output tied to the execution ----------------------------
def test_inv12_output_bound_to_execution():
    ex = _drive_to_completed()
    rec = ex.to_record()
    assert rec["output_hash"] == m.payload_hash({"result": 42})
    assert rec["artifact_uri"] == "file:///out/42.json"
    assert rec["execution_id"] and rec["input_hash"]


# ---- invariant 13: critic state derivable from the record ------------------
def test_inv13_record_is_complete_for_critic():
    rec = _drive_to_completed().to_record()
    required = {
        "execution_id", "attempt_id", "correlation_id", "dispatch_id", "idempotency_key",
        "producer", "execution_origin", "workflow_version", "schema_version", "state",
        "input_hash", "output_hash", "artifact_uri", "created_at", "updated_at",
    }
    assert required.issubset(rec.keys())


# ---- regression: terminal run must NOT be lease-reclaimable into RUNNING ---
def test_inv2_terminal_lease_expiry_cannot_reclaim_into_running():
    # Counterexample found by adversarial verification: a TIMED_OUT/FAILED run
    # still held its lease, so an expired lease let reclaim() force it back to
    # DISPATCHED -> CLAIMED -> RUNNING. Must now raise and never re-run.
    for terminal in ("time_out", "fail"):
        ex = _run()
        ex.plan(now=T0).dispatch(now=T0).claim(now=T0, owner="w1", lease_ttl_seconds=60)
        if terminal == "time_out":
            ex.time_out(now="2026-07-18T00:02:00Z")
        else:
            ex.fail(now="2026-07-18T00:02:00Z", error_code="e", error_summary="s")
        assert ex.state in m.TERMINAL_STATES
        assert ex.lease is None  # lease released on terminal entry
        with pytest.raises(m.InvalidTransition):
            ex.reclaim(now="2026-07-18T00:05:00Z", owner="w2", lease_ttl_seconds=60)
        assert ex.state != m.RUNNING


# ---- property: NO run-final state can reach RUNNING by any path ------------
def test_property_run_final_states_never_reach_running():
    for start in m.RUN_FINAL_STATES:
        # BFS over the transition graph from each run-final state.
        seen, frontier = {start}, [start]
        while frontier:
            s = frontier.pop()
            for nxt in m.VALID_TRANSITIONS.get(s, frozenset()):
                assert nxt != m.RUNNING, f"{start} can reach RUNNING via {s}->RUNNING"
                if nxt not in seen:
                    seen.add(nxt)
                    frontier.append(nxt)


def test_replay_from_dead_letter_is_new_attempt_not_same_object():
    led = m.MotorLedger()
    ex, _ = led.submit(task_kind="demo", payload={"x": 1}, now=T0, producer="p", max_retries=0)
    ex.plan(now=T0).dispatch(now=T0).fail(now=T1, error_code="e", error_summary="s")
    ex.dead_letter(now=T1, reason="exhausted")
    child = led.replay(ex.execution_id, now=T2, payload={"x": 1})
    assert child.execution_id != ex.execution_id  # new object
    assert ex.state in m.RUN_FINAL_STATES  # parent stays run-final (marked)
    # the dead-lettered parent object can never itself walk to RUNNING
    assert m.RUNNING not in m.VALID_TRANSITIONS[m.REPLAY_REQUESTED]


# ---- the invalid-transition wall (exhaustive) ------------------------------
def test_invalid_transitions_rejected_exhaustively():
    all_states = set(m.VALID_TRANSITIONS)
    for frm in all_states:
        for to in all_states:
            if to not in m.VALID_TRANSITIONS[frm]:
                ex = _run()
                ex.state = frm
                with pytest.raises(m.InvalidTransition):
                    ex.transition(to, now=T1)
