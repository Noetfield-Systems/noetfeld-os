# NOOS Software Repair Runway — Managed Pilot

**A customer submits a failing repository, failing CI run, failing test, or
reproducible defect. NOOS reproduces it, plans a fix, repairs it under real
tests, and returns a verified draft PR or patch bundle plus a customer report
and audit receipts. A human approves before any merge — NOOS never auto-merges
and never auto-deploys.**

---

## Product promise

NOOS accepts a reproducible software defect and returns a **test-verified**
candidate fix together with the evidence for it. The engine only proposes a
patch when that patch makes the customer's real failing tests pass in an
isolated copy of the repository. It does not fabricate a passing result, and it
does not cross the human-approval boundary: merge, deploy, and any change to
secrets, branch protection, ownership, or billing remain the customer's action.

This is a **managed pilot**: manual onboarding, best-effort turnaround, no SLA.

## Customer problem

A team has a failing build, a red test, or a reproducible bug and wants a
concrete, evidence-backed fix to review — not a suggestion that may or may not
compile, and not an automated agent that merges or deploys on its own. The
customer needs three things a bare model call does not give them: (1) proof the
proposed patch actually turns the failing tests green, (2) a bounded, auditable
change that touches only allowed paths, and (3) a hard stop before anything
irreversible happens.

## Who it is for

Teams running **Python (pytest)** or **Node (`node:test`)** projects who can
supply a reproducible failure and who want a reviewed, test-verified draft fix
delivered with receipts, while keeping merge and deploy under their own control.
It is a fit when the defect is reproducible from the submitted repository and
tests; it is not a fit for non-reproducible issues or stacks outside the pilot
matrix below.

## Exact v1 feature set (what is proven)

Proven today on real fixtures, offline / `local_reference`, test-verified:

- **Three real fixture repair jobs across three defect classes**, each moving
  from real failing tests (exit 1) to a real verified patch to tests passing
  (exit 0):
  1. off-by-one range regression
  2. unused-import lint failure (ruff `F401`)
  3. wrong-operator data-aggregation defect
- **Repair engine (`noos_repair_engine_v1`)** — fault-localized, bounded
  **mutation search**. Every candidate patch is re-run against the customer's
  real tests in an isolated copy of the repository; only a candidate that makes
  those tests pass is proposed. The engine never fabricates a green result.
- **Recipe `software_repair_ci_v1`, v1.0.0** — the governing recipe for the
  pilot, with the limits and forbidden paths listed under
  [Reliability model](#reliability-model) and [Security boundary](#security-boundary).
- **Customer API + minimal UI** (Python stdlib HTTP): submit commission, read
  job state, read events, fetch artifacts, fetch report, fetch verification,
  read cost, replay, cancel. End-to-end verified.
- **Provider-neutral model router** — an OpenAI-compatible adapter
  (DeepSeek / Moonshot / OpenAI-compatible) is **complete**. See
  [Current limitations](#current-limitations) for why no hosted-model call runs
  today.

## Input contract

The customer submits a **reproducible defect** in one of these forms:

- a failing repository,
- a failing CI run,
- a failing test, or
- a reproducible defect.

The submission must be reproducible from what is provided: the engine reproduces
the failure (real tests exit non-zero) before it attempts any repair. If the
failure cannot be reproduced from the submitted material, there is nothing for
the engine to verify a fix against.

Submission is made through the customer API / UI (`submit commission`).

## Output contract

On a successful repair job, NOOS returns:

- a **verified draft PR or patch bundle** — a candidate change that made the
  real failing tests pass (exit 0) in an isolated copy,
- a **customer report**,
- **audit receipts**, and
- retrievable **job state, events, artifacts, verification record, and cost**
  via the API.

The output is a **draft for human review**. NOOS does not merge it and does not
deploy it. Every output artifact is hash-integrity protected (see
[Reliability model](#reliability-model)).

## Supported stacks (pilot only)

The pilot supports exactly two stacks. There is **no universal-language claim**.

| Stack | Test runner | Status |
|---|---|---|
| Python | `pytest` | Supported (pilot) |
| Node | `node:test` | Supported (pilot) |
| Any other language / runner | — | Not supported in the pilot |

## Reliability model

Recipe-enforced execution limits (`software_repair_ci_v1`):

| Limit | Value |
|---|---|
| Max changed files | 3 |
| Max patch size | 20 KB |
| Max model calls | 4 |
| Max repair attempts | 3 |
| Timeout | 300 s |

Verified reliability properties of the job runtime:

- **Idempotency dedupe** on submission.
- **Bounded retry with backoff.**
- **Lease** with owner, expiry, and reclaim.
- **Dead-letter** path for jobs that cannot proceed.
- **Replay preserves lineage.**
- **Output hash integrity** on artifacts.
- **Terminal states cannot resurrect** (proven by BFS over the state graph).

The full worktree suite reports **348 passed**.

## Provenance model (job success ≠ infra liveness)

Provenance is tracked so that a green repair result can never be mistaken for a
live production system. This is a **corrected** model:

- Repair-job success carries **`receipt_origin=local_reference`** and can
  **never** establish production liveness.
- **Customer-job success** and **infrastructure liveness** are **separate
  predicates**. A passing repair job says a patch made the tests green in an
  isolated copy; it does not say any production surface is live.
- A **real sanctioned factory-autorun GitHub Actions run** proved the Supabase
  sink + factory + projection are **LIVE today** — but that run is **manual
  origin, not canonical organic**, and it is a separate fact from any repair
  job's success.

## Recovery model

Recovery is built from the reliability primitives above:

- **Retry** is bounded with backoff.
- **Leases** have an owner, an expiry, and a reclaim path, so a stalled or lost
  worker's job can be reclaimed rather than stranded.
- **Replay** re-runs a job while **preserving its lineage**, so a replay is
  auditable and does not masquerade as a fresh organic run.
- **Dead-letter** captures jobs that cannot proceed instead of silently dropping
  them.
- **Cancel** is available to the customer through the API.
- **Terminal states cannot resurrect** — a job that reached a terminal state
  stays terminal (BFS-proven).

## Security boundary

- **No secrets are committed.**
- The worker's **network access is limited to the configured model endpoint**.
- **Repair patches are confined to the recipe's allowed paths.**
- **Forbidden paths are never touched.** Forbidden paths and areas:
  `.github`, secrets, keys, `.env`, `Dockerfile`, deploy, infrastructure,
  `*.tf`, lockfiles, `CODEOWNERS`, branch-protection, billing.
- **Human approval is required before merge.** The human-approval boundary means
  NOOS performs no merge, no deploy, no secret change, no branch-protection
  change, no ownership change, and no billing change.

> **Note:** No security certification is claimed.

## Data-handling policy

- Customer repository content is processed **transiently in an isolated
  worktree** for the duration of the job.
- **Artifacts are retained for 30 days** (see below).
- The worker's network is limited to the configured model endpoint; customer
  content is not sent to endpoints outside that boundary.

## Artifact retention (30 days)

Job artifacts are retained for **30 days**.

## Current limitations

- **Pilot stacks only:** Python (`pytest`) and Node (`node:test`). No other
  language or test runner is supported. No universal-language claim.
- **No hosted-model call today.** The model router / OpenAI-compatible adapter
  is complete, but **no model-provider API key exists in any sanctioned
  environment**, so a real hosted-model call is **unavailable today**. The pilot
  runs the **deterministic-local engine** ($0, compute-only).
  - *(Protected / operator step — hosted enablement):* run
    `gh secret set DEEPSEEK_API_KEY`. Estimated hosted cost is **$0.001–$0.02
    per repair (~2–8k tokens)**.
- **Persistence migration not applied.** *(Production-gated)* additive migration
  **0021** is **ready-to-apply but not applied**.
- **Canonical producer restore is protected.** *(External / Railway token
  absent)* restoring the canonical `http_loop` producer is a **PROTECTED** step
  and cannot be performed here.
- **Reproducibility required.** A defect that cannot be reproduced from the
  submitted repository and tests cannot be verified and therefore cannot be
  repaired by this engine.
- Repairs are bounded by the recipe limits (max 3 changed files, 20 KB patch,
  4 model calls, 3 repair attempts, 300 s), so defects requiring a larger or
  broader change fall outside the pilot envelope.

## Support boundary

- **Managed pilot, manually onboarded.**
- **Best-effort** turnaround; **no SLA** is claimed.
- **No security certification** is claimed.
- No reliability metric beyond what is measured in this document is claimed.

## Commands

```bash
# Run a single repair job against a job spec, JSON output:
python3 scripts/noos_software_repair_runner_v1.py --job <spec> --json

# Start the customer API + minimal UI (serves on :8811):
python3 scripts/noos_software_repair_api_v1.py
```

---

SUBMITTED for independent verification (author != subject).
canon_version: FOUNDER_CANON_v1+MACHINE_LOOPS_v1
