<!-- NOOS-AGENT-DOC -->

# Retention / Dead-Letter Proposal — dispatch queue & diagnostic sink

Task: **NF-NOOS-OBSERVABILITY-SEMANTICS-001** (proposal only — no records deleted,
archived, or mutated in this task).

## 1. Orphaned dispatch-queue backlog

`.noos-runtime/machine-loops/dispatch-queue-v1.json` currently holds **8 pending
`noos-machine-repair-dispatch-v1` items**, all sourced from
`noos-outside-audit-*` receipts dated **2026-07-05** (~12 days old at diagnosis),
with `processed=[]` — nothing drains this local queue. The reconciler now
classifies them as `orphaned_backlog` (see `report_line` / `queue_breakdown`),
so `pending=8` is no longer mistaken for 8 live actionable items.

**Proposed control (requires founder gate — touches operational records):**

1. Add a **dead-letter lane**: move items classified `orphaned_backlog` for
   more than `orphan_backlog_age_days` (default 3) into a sibling
   `dead-letter-v1.json` with a `dead_lettered_at` stamp and the original
   `source_receipt_path`. Non-destructive: nothing is deleted; the record is
   relocated with provenance.
2. Add a **drainer or explicit retirement**: either wire a consumer that
   processes `actionable_pending`, or record a founder decision that the local
   queue is superseded by the cloud dispatch path and should be frozen.
3. Emit a reconcile receipt on each dead-letter move for auditability.

**Not done here** (per task scope): the 8 July-5 records remain in `pending`
untouched. This proposal is the follow-up work item.

## 2. `noos_deadman_runs` diagnostic sink retention

The diagnostic canary sink (`noos_deadman_runs`) is **append-only with no TTL or
cleanup** — it grows unbounded (>555 rows observed). It is a terminal audit log
(not read by liveness/dispatch/reconcile/recovery), so growth is a storage /
observability-hygiene concern, not a correctness one.

**Proposed control (schema/governance — founder-gated):**

- Add a rollup/retention policy: keep full-fidelity rows for N days (e.g. 30),
  then roll older rows into a daily summary (`run_count`, `stale_count` extrema)
  and prune the raw rows via a scheduled job.
- Alternatively, a Supabase `pg_cron` retention task with a documented window.

Both options are schema/governance (T3-class) changes and must go through the
verifier-freeze gate — **out of scope for this Builder task**, filed here as the
recommended next step.
