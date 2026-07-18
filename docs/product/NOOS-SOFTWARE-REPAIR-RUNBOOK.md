# NOOS Software Repair Runway — Operations & Incident Runbook

Managed-pilot runbook for the **NOOS Software Repair Runway**. A customer
submits a failing repository, failing CI run, failing test, or reproducible
defect; NOOS reproduces it, plans, repairs it (test-verified), and returns a
**verified draft PR or patch bundle** plus a customer report and audit
receipts. **Human approval is required before merge — NOOS never auto-merges
and never auto-deploys.**

This document covers day-to-day operation and incident handling: health
checks, reading job states, failure and recovery paths (idempotency, retry,
dead-letter, replay), the production-gated migration `0021` apply/rollback
workflow, the external canonical-producer restore, the provenance rule that
keeps repair evidence from false-greening production, and incident escalation.

Every step that requires cloud credentials or a founder gate is marked
**EXTERNAL_ACTIVATION_REQUIRED** or **PROTECTED** and does **not** run on the
build host by default.

**Operating posture (facts, not promises).** This is a *managed pilot*:
customers are onboarded manually, support is best-effort, and **no SLA is
claimed**. No security certification is claimed. Supported stacks are
**Python (`pytest`)** and **Node (`node:test`)** only — there is no
universal-language capability. The pilot runs on the deterministic-local
repair engine at **$0 compute cost** (see §7); a hosted model call is
unavailable today because no model-provider API key exists in any sanctioned
environment.

---

## 0. Component map

| Component | Entry point | Notes |
|---|---|---|
| Repair runner (CLI) | `python3 scripts/noos_software_repair_runner_v1.py --job <spec> --json` | Single-job execution; emits JSON. |
| Customer API + minimal UI | `python3 scripts/noos_software_repair_api_v1.py` | stdlib HTTP, serves on **:8811**. |
| Repair engine | `noos_repair_engine_v1` | Fault-localized bounded mutation search. |
| Recipe | `software_repair_ci_v1` **v1.0.0** | Limits + allowed/forbidden paths (§1). |
| Model router | provider-neutral OpenAI-compatible adapter | Complete; hosted call unavailable today (§7). |
| Persistence schema | migration `0021_software_repair_runway.sql` | **READY-TO-APPLY, NOT applied** (§5). |

The API exposes these operations over the pilot lifecycle: **submit
commission, read job state, read events, read artifacts, read report, read
verification, read cost, replay, cancel**. This surface has been verified
end-to-end.

---

## 1. Recipe limits & path boundaries (`software_repair_ci_v1` v1.0.0)

These are hard limits enforced by the recipe. An operator reading a job should
confirm the job stayed inside them.

**Resource limits (per job):**

- Max **3** changed files
- Max **20 KB** patch size
- Max **4** model calls
- Max **3** repair attempts
- **300 s** timeout

**Forbidden paths (never touched by a repair patch):**

```
.github/            secrets / keys / .env
Dockerfile          deploy / infrastructure
*.tf                lockfiles
CODEOWNERS          branch-protection
billing
```

**Human-approval boundary.** No merge, no deploy, no secret change, no
branch-protection change, no ownership change, and no billing change is
performed by NOOS. Any job whose only viable fix would require touching a
forbidden path or crossing this boundary is reported as **out-of-scope**, not
force-fitted.

If a job report shows a change outside the allowed paths or above these
limits, treat it as a **P1 integrity incident** (§8) — the recipe guard should
make this impossible, so its appearance means the guard was bypassed.

---

## 2. Health checks

All health checks below are **local and offline** — they need no cloud
credentials and no model-provider key.

**2.1 Engine + recipe self-check (single fixture job):**

```
python3 scripts/noos_software_repair_runner_v1.py --job <spec> --json
```

Expected: JSON output describing a repair job that moved a real failing test
suite (exit 1) to passing (exit 0) via a verified patch, within the §1 limits.

**2.2 Reference fixtures (3 defect classes, proven today):**

The pilot is backed by three real fixture repair jobs, each a distinct defect
class, each with a real failing test → verified patch → passing test:

1. Off-by-one range regression
2. Unused-import lint failure (`ruff` **F401**)
3. Wrong-operator data-aggregation defect

A green fixture run confirms the fault-localization + mutation-search loop is
intact.

**2.3 API + UI liveness:**

```
python3 scripts/noos_software_repair_api_v1.py     # serves API + minimal UI on :8811
```

Then exercise the surface: submit a commission, poll job state, read events,
fetch the report, fetch verification, fetch cost. A healthy API answers each of
these operations for a submitted job.

**2.4 Full regression suite:**

Run the worktree test suite. The current known-good baseline is **348 tests
passing**. A count below baseline, or any failure, blocks pilot operation until
resolved.

---

## 3. Reading job states

The **job-state** endpoint returns the canonical state string for a job; the
**events** endpoint returns the ordered lifecycle log; the **verification** and
**cost** endpoints return the proof and the spend. The phases below describe
the *guaranteed semantics* an operator must rely on, independent of exact label
strings.

| Phase | What it means | Operator action |
|---|---|---|
| **Accepted / deduped** | Commission received; an idempotency key deduplicates re-submissions (§4.1). | None — a duplicate submit returns the original job, it does not fork a second one. |
| **Leased / running** | A worker holds a lease with an **owner** and an **expiry**; the repair loop is executing inside an isolated worktree copy. | Watch the lease expiry; if it lapses the job is reclaimable (§4.3). |
| **Succeeded (verified)** | The mutation search found a candidate that made the **real** tests pass; a draft PR / patch bundle, report, and receipts are available. | Read verification + cost, then route to the human-approval step before any merge. |
| **Failed** | No candidate within the §1 limits made the tests pass, or the job hit a limit/timeout. | Read the report for the reason; a failure is an honest "no verified fix," never a fabricated green. |
| **Dead-letter** | The job exhausted bounded retries and was parked for inspection (§4.4). | Inspect the events log; decide replay vs. close. |
| **Cancelled** | The commission was cancelled via the cancel operation. | Terminal — see below. |

**Terminal states are immutable.** Succeeded, Failed, Dead-letter, and
Cancelled are terminal: a terminal job **cannot resurrect** into an active
state. This property is BFS-proven over the state machine. If you observe a
terminal job transition back to running, treat it as a **P1 integrity
incident** (§8).

**Reading the proof for a succeeded job:**

- **verification** — shows the before/after test result (fail → pass) that
  justifies the patch.
- **report** — the customer-facing summary (defect, plan, changed files,
  result).
- **cost** — compute/token cost. On the deterministic-local engine this is
  **$0** (§7).
- **artifacts** — the draft PR / patch bundle and audit receipts.

---

## 4. Failure & recovery

The runway is built for safe re-execution. The four primitives below are
verified by the regression suite and are the operator's recovery toolkit.

### 4.1 Idempotency (dedupe)

Each commission carries an idempotency key. Re-submitting the same commission
returns the **existing** job instead of creating a second one. **Recovery
action:** if a client retried a submit after a network blip, confirm via the
job-state endpoint that only one job exists for that key. No manual cleanup of
duplicates should ever be needed — if duplicates exist, escalate (§8).

### 4.2 Bounded retry + backoff

Transient step failures are retried with backoff, **bounded** — retries do not
loop forever. **Recovery action:** none while retries remain; a job that keeps
failing transiently will eventually move to dead-letter (§4.4) rather than
spin.

### 4.3 Lease owner + expiry + reclaim

A running job is protected by a lease with an explicit **owner** and
**expiry**. If a worker dies mid-job, the lease expires and the job becomes
**reclaimable** by another worker. **Recovery action:** for a job stuck in
"leased/running" past its expiry, confirm the lease has lapsed, then allow
reclaim. Do **not** hand-force a second worker onto a job whose lease is still
valid — that is what the owner+expiry check prevents.

### 4.4 Dead-letter

A job that exhausts bounded retries is moved to **dead-letter** — parked, not
lost. **Recovery action:** read the events log to find the failing step,
decide whether the cause is transient (replay, §4.5) or structural (close the
job and report out-of-scope to the customer).

### 4.5 Replay (preserves lineage)

A job can be **replayed**. Replay **preserves lineage** — the replayed run is
linked to its origin, not laundered into a fresh unrelated job. **Recovery
action:** replay a dead-lettered or failed job after the transient cause is
cleared; then verify the replay's lineage points back to the original
commission.

### 4.6 Output hash integrity

Job outputs carry an integrity hash. **Recovery action:** if a stored artifact
no longer matches its recorded hash, do not ship it — treat it as a **P1
integrity incident** (§8).

---

## 5. Migration `0021` — apply & rollback (PRODUCTION-GATED)

**Status today: READY-TO-APPLY, NOT applied.** Migration
`0021_software_repair_runway.sql` is **additive only** and creates the
persistence objects (`repair_jobs`, `repair_commissions`). It is a *proposed
workflow*, not a live governed workflow, and applying it is founder-gated.

> **Do not apply this migration from the build host or an agent session.** It
> requires the protected `production` environment and founder approval.

### 5.1 Apply — the proposed workflow (`supabase-migrate-v1`)

The delivered workflow (`docs/product/proposed-workflows/supabase-migrate-v1.yml`)
is additive-only, guarded against destructive SQL, and gated on the protected
`production` environment. Founder activation sequence:

1. Move the file to `.github/workflows/supabase-migrate-v1.yml`.
2. Register it in `data/noos-parallel-agent-registry-v1.json` — an
   **L5-frozen registry (founder gate)**; the machine does not edit it.
3. Merge to the default branch (founder gate).
4. Dispatch:
   ```
   gh workflow run supabase-migrate-v1.yml -f migration=0021_software_repair_runway.sql
   ```
5. **Approve the pending `production` environment gate.** A dispatched run
   *waits* here for founder approval before it can touch the database.

The workflow's own guards enforce: additive-allowlist membership, rejection of
any `DROP` / `TRUNCATE` / `DELETE FROM` / `ALTER … DROP` outside comments, and
a post-apply verification query
(`select to_regclass('public.repair_jobs'), to_regclass('public.repair_commissions');`).

Until every step above is done, the schema state is
**`PROTECTED_ENVIRONMENT_APPROVAL_REQUIRED`**.

### 5.2 Rollback

Because `0021` is **additive only**, the safe rollback is to leave the new
objects in place (they are unused until the runway persists to them) or, if a
founder explicitly requires removal, to author a **separate, additive
forward-migration** under founder gate that drops the new objects. A rollback
that issues destructive SQL is **not** permitted through `supabase-migrate-v1`
— its guard refuses destructive statements. Never hand-run destructive SQL
against `production`; route any removal through the same protected,
founder-approved workflow path.

---

## 6. Canonical producer restore — Railway (EXTERNAL_ACTIVATION_REQUIRED)

**Status today: PROTECTED — the Railway token is absent on the build host.**

Restoring the canonical `http_loop` producer is an **external** operation that
needs a Railway credential which does not exist in any sanctioned build
environment. It cannot be performed from an agent session or the build host.

- The producer restore is **founder-gated** and requires the Railway token,
  which lives outside the repo.
- A **sanctioned factory-autorun GitHub Actions run** has proven that the
  Supabase **sink + factory + projection are LIVE today** — but that run is of
  **manual origin**, i.e. **NOT canonical organic** liveness. Manual-origin
  liveness does **not** substitute for the canonical `http_loop` producer.
- Until the producer is restored under founder gate, treat canonical organic
  liveness as **not established**; report `evidence-insufficient` rather than
  asserting the loop is running.

Do not mark the runway "fully live" on the strength of the manual factory run.
The distinction is load-bearing and is covered next.

---

## 7. Model router & cost posture

The model router is a **provider-neutral, OpenAI-compatible** adapter
(DeepSeek / Moonshot / any OpenAI-compatible endpoint) and is **complete**.

- **No model-provider API key exists in any sanctioned environment**, so a real
  **hosted-model call is UNAVAILABLE today.**
- The pilot therefore runs on the **deterministic-local repair engine** at
  **$0 compute cost**. Every candidate patch is re-run against the customer's
  real tests in an isolated copy; only a candidate that makes the tests pass is
  proposed. The engine **never fabricates a green.**
- **Exact hosted enablement (founder action):**
  ```
  gh secret set DEEPSEEK_API_KEY
  ```
- **Estimated hosted cost** once enabled: **$0.001–$0.02 per repair**
  (~2–8k tokens). This is an estimate, not a measured production figure.

Reading the **cost** endpoint on a job run under the local engine will show
**$0**; a non-zero cost implies a hosted path was enabled and should be
reconciled against the estimate above.

---

## 8. Provenance rule — repair evidence can NEVER false-green production

This is the single most important operational invariant on the runway.

- A successful **repair job** carries **`receipt_origin=local_reference`**.
  A `local_reference` success **can NEVER establish production liveness.**
- **Customer-job success** and **infrastructure liveness** are **separate
  predicates.** A green repair job says the *repair loop* worked on that job;
  it says **nothing** about whether the production producer, sink, or
  projection are live.
- Consequently: **never** use a passing repair job (or a batch of them) as
  evidence that the canonical producer (§6) is running. A stack of green
  `local_reference` receipts is still zero evidence of organic production
  liveness.

**Operator check.** When a status view or report claims production is "live,"
confirm the claim is backed by an **infra-liveness** predicate (a canonical
`http_loop` producer signal), **not** by repair-job receipts. If the only
support is repair-job success, the correct verdict is **evidence-insufficient**
— report it as such. A report that collapses these two predicates is a
**false-green** and is a P1 integrity incident.

---

## 9. Security & data-handling boundary

- **No secrets committed** to the repo.
- Worker **network access is limited to the configured model endpoint** — and
  today, with no model key set, no external model traffic occurs at all.
- Repair patches are **confined to the recipe's allowed paths**; the
  **forbidden paths (§1) are never touched.**
- **Human approval is required before merge** — no merge, deploy, secret,
  branch-protection, ownership, or billing change is performed by NOOS.
- **Data handling:** customer repository content is processed **transiently in
  an isolated worktree**; **artifacts are retained for 30 days.**
- **No security certification is claimed.** This is a managed pilot with a
  documented boundary, not a certified service.

---

## 10. Incident escalation

Classify, then act. Founder-gated actions (deploy, merge to main, spend,
external/commercial sends, L5/verifier changes, schema/governance merges) are
**never** self-approved by an agent — they route to the founder gate.

| Severity | Trigger | First action |
|---|---|---|
| **P1 — integrity** | Terminal job resurrected; patch outside allowed paths or over §1 limits; output hash mismatch; a report false-greens production (§8); duplicate jobs for one idempotency key. | Stop shipping the affected artifact. Preserve the job's events + receipts. Escalate to founder gate. Do **not** weaken the check that caught it. |
| **P2 — availability** | API on :8811 unresponsive; regression suite below the 348 baseline; jobs stuck past lease expiry not reclaiming. | Re-run health checks (§2). Recover via the §4 primitives (reclaim / replay). Record the failing step. |
| **P3 — capacity / scope** | Job legitimately fails within limits; defect needs a forbidden-path change; unsupported stack (not Python `pytest` / Node `node:test`). | Report **out-of-scope** or **no-verified-fix** to the customer honestly. No override of §1. |
| **External-blocked** | Migration `0021` apply (§5); canonical producer restore (§6); hosted model enablement (§7). | These are **EXTERNAL_ACTIVATION_REQUIRED / PROTECTED**. Do not attempt from the build host — route to the founder with the exact activation steps documented above. |

**Escalation discipline.** A failing agent **fixes the system, never weakens
the test.** Builders write **"SUBMITTED for independent verification"** — a
PASS/DONE verdict comes only from a deterministic gate or an independent
verifier (author ≠ subject), never from the party that did the work. No DONE
claim without a receipt id.

---

*SUBMITTED for independent verification (author != subject). canon_version: FOUNDER_CANON_v1+MACHINE_LOOPS_v1*
