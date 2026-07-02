# Deterministic Loop Core (D1–D8)

Same inputs must produce same state transitions and same receipts. Every rule below maps to a real incident class.

## D1 — Idempotency keys everywhere

Every side-effecting operation carries a deterministic key derived from content, never from time or randomness:

`op_key = hash(workflow_id + plan_id + attempt_no)`

Sinks upsert on op_key. Replays, retries, and backfills converge to one row instead of duplicating or dropping.

*Incident class fixed: double-write races, alternate-ID sink drops, backfill dupes.*

## D2 — Single writer per state cell

Each mutable state (queue head, batch pointer, registry) has exactly ONE writer process. Everyone else reads.

Writer advances via compare-and-swap: `advance(expected_head, new_head)` — mismatch = REJECTED receipt, never silent overwrite. A CAS rejection is the system working, not an error to suppress.

*Incident class fixed: Mac-vs-Railway pointer regression, split-brain state.*

## D3 — IDs from actuals, never inference

Next ID = max(actual committed IDs) + 1. Never from summaries, claimed ranges, or generator memory.

Post-write validator: claimed range == actual rows, fail closed.

*Incident class fixed: phantom CLOUD-SEC-7402–7466.*

## D4 — Advance is a pure function of acks

`advance := f(execute_ok AND validate_ok AND sink_acked)` — one boolean expression, no partial paths. Any input false → no advance + BLOCKED receipt with the failing term named.

*Incident class fixed: advance_decoupled_from_supabase_ack (23 lost rows).*

## D5 — Event-sourced truth, derived state

Append-only event log is the only authored truth. Current state = fold(events). Receipts and dashboards are DERIVED from the log, never hand-authored.

Determinism test (run in CI): replay the event log → rebuilt state must byte-match live state files. Mismatch = DRIFT receipt.

*Incident class fixed: summary-lies, report-line contradicting its own JSON.*

## D6 — Randomness and time quarantined

- Jitter/backoff allowed ONLY at the scheduling edge; the chosen value is recorded in the receipt (replayable).
- One clock source per receipt (started_at/finished_at at edges); no wall-clock branching inside a cycle.
- No `now()` in ID or key derivation.

## D7 — LLM output is a proposal, not a transition

Non-deterministic components (LLM calls) never mutate state directly. Flow: LLM proposes → deterministic validator (schema + rubric) accepts/rejects → only accepted proposals enter the event log. Temperature pinned; schema-invalid output = deterministic REJECT + retry with same op_key.

*Incident class fixed: agent prose becoming state.*

## D8 — Deterministic verification

A verify is a pure function of (url, markers, hash_algo, redirect_policy=OFF, min_delay). Two runners with the same spec must return the same verdict; divergence between runners = escalation receipt (environment fork detected), not a re-roll.

*Incident class fixed: agent "public fetch" seeing different internet than external fetch.*

## Legal state transitions (the only ones)

```
IDLE_NO_WORK      -> RUNNING            (work admitted by rubric)
RUNNING           -> COMPLETE           (D4 true)
RUNNING           -> FAILED_WITH_RECEIPT (execute/validate false)
RUNNING           -> BLOCKED_WITH_REASON (sink unacked / gate NO)
any               -> TRIAGE_REQUIRED    (dirty cap / invariant break)
any               -> THROTTLED_ROI      (L11 rule)
BLOCKED/THROTTLED -> IDLE_NO_WORK       (blocker cleared, receipt)
```

Any transition not in this table = malformed, reconciler rejects it. State files carry `transition_log_tail` so the last 5 transitions are auditable inline.

## Fencing for stale locks

Lock = {holder_id, fencing_token(monotonic), acquired_at}. Recovery increments the token; writes carrying an old token are rejected at the sink. Stale-lock recovery becomes deterministic instead of "hope the old process died."

## CI determinism gate (add to external-verify)

1. Replay test (D5) green
2. Idempotency test: run the same op twice, assert one row
3. CAS test: concurrent advance, assert exactly one winner + one REJECTED receipt
4. Transition test: fuzz illegal transitions, assert all rejected
