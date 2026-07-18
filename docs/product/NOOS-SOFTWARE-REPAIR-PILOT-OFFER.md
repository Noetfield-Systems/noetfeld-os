# NOOS Software Repair Runway — Managed Pilot Offer

**Status:** Pilot offer + founder-editable pricing proposal
**Recipe:** `software_repair_ci_v1` (recipe_version `1.0.0`, status `pilot`)
**Scope of this document:** what the pilot does, what the customer provides and
receives, the per-job cost model, and a **founder-editable** pricing and
gross-margin proposal. Prices below are placeholders for the founder to set —
they are not committed rates.

---

## 1. What the pilot is

The NOOS Software Repair Runway is a **managed pilot**. A customer submits a
failing repository, a failing CI run, a failing test, or a reproducible defect.
NOOS then:

1. **Reproduces** the failure in an isolated worktree copy.
2. **Plans** and **repairs** the defect with a test-verified patch.
3. **Returns** a verified draft PR or patch bundle, a customer report, and audit
   receipts.

**Human approval is required before merge.** NOOS never auto-merges and never
auto-deploys. The repair is delivered as a draft PR or patch bundle for a human
to review and merge.

---

## 2. What is proven today (offline / `local_reference`)

The following are real, test-verified facts from the pilot runner. They are
recorded with `receipt_origin = local_reference`.

- **3 real fixture repair jobs across 3 defect classes**, each with real failing
  tests (process exit 1) → a real verified patch → tests passing (process exit 0):
  1. Off-by-one range regression (`fixtures/repair/py-unit-regression`,
     `job1-unit-regression.json`)
  2. Unused-import lint failure — ruff `F401`
     (`fixtures/repair/py-lint-failure`, `job2-lint-failure.json`)
  3. Wrong-operator data-aggregation defect
     (`fixtures/repair/py-integration-data`, `job3-integration-data.json`)
- **Repair engine** (`noos_repair_engine_v1`): fault-localized, **bounded
  mutation search**. Every candidate patch is re-run against the customer's real
  tests in an isolated copy; only a candidate that makes the tests pass is
  proposed. The engine does not fabricate a passing result — a proposed patch is
  one that was observed to turn the real test suite from failing to passing.
- **Customer API + minimal UI** (Python stdlib HTTP): submit commission, read job
  state, events, artifacts, report, verification, cost, replay, and cancel.
  End-to-end verified.
- **Reliability properties** (verified in the worktree test suite — **348 passed**):
  idempotency dedupe, bounded retry with backoff, lease owner + expiry + reclaim,
  dead-letter handling, replay that preserves lineage, output-hash integrity, and
  terminal states that cannot resurrect (BFS-proven).

### Provenance boundary (important, do not overstate)

A repair **job** succeeding is a **customer outcome** recorded as
`receipt_origin = local_reference`. It can **never** establish production
liveness. Customer-job success and infrastructure liveness are **separate
predicates**. Do not read a green repair job as "the production service is up."

---

## 3. Supported stacks and limits (pilot scope)

The pilot is **narrow by design**. There is **no** universal-language or
universal-repository claim.

**Supported stacks (pilot only):**

| Language | Test runner | Discovery command |
|---|---|---|
| Python | pytest | `pytest -q` |
| Node | `node --test` (node:test) | `node --test` |

**Per-job limits (from the recipe):**

| Limit | Value |
|---|---|
| Max repository size | 50 MB |
| Max changed files | 3 |
| Max patch size | 20,000 bytes (20 KB) |
| Max model calls | 4 |
| Max repair attempts | 3 |
| Execution timeout | 300 s |
| Per model-call timeout | 60 s |
| Artifact retention | 30 days |

**Allowed patch paths:** `src/**`, `lib/**`, `app/**`, `tests/**`, `test/**`,
and `*.py`, `*.js`, `*.ts`.

**Forbidden paths (never touched):** `.github/**`, any `secrets*`, `*.pem`,
`*.key`, `.env*`, `Dockerfile`, `deploy/**`, `infrastructure/**`, `*.tf`,
`package-lock.json`, `poetry.lock`, `.git/**`, `CODEOWNERS`,
`branch-protection*`, `billing*`.

**Human-approval boundary (the pilot will not cross these):** no auto-merge,
no auto-deploy, no secret/credential change, no branch-protection change, no
repository-ownership change, no billing change, no modification of forbidden
paths.

---

## 4. What the customer provides / receives

**The customer provides:**

- A failing input: a repository (Python/pytest or Node/node:test), a failing CI
  run, a failing test, or a reproducible defect that fits the supported stacks
  and the limits above.
- Authorization to access the submitted repository content for the duration of
  the job.
- A human reviewer to approve (or decline) the returned draft PR / patch bundle
  before any merge.

**The customer receives:**

- A **verified draft PR or patch bundle** (patch that was observed to turn the
  real test suite from failing to passing, within the stated limits).
- A **customer report** describing the failure, the repair, and the verification.
- **Audit receipts** for the job.
- If no verified patch is found within the limits, the job terminates without a
  fabricated fix; the customer receives the report and receipts documenting the
  attempt.

---

## 5. Per-job cost model

Two execution modes exist. The pilot runs on the **deterministic-local** engine.

### 5a. Deterministic-local engine (pilot default) — **$0 compute**

The pilot uses the deterministic-local repair engine. It performs bounded
mutation search against the customer's real tests. **Compute cost to NOOS: $0**
(local execution only; no model-provider spend).

> **No hosted-model API key exists in any sanctioned environment today, so a real
> hosted-model call is UNAVAILABLE.** The pilot therefore runs $0 compute-only on
> the deterministic-local engine.

### 5b. Hosted-model mode (optional, not enabled) — estimated $0.001–$0.02 / repair

The model router is a **provider-neutral, OpenAI-compatible adapter**
(DeepSeek / Moonshot / any OpenAI-compatible provider). The adapter is complete.

- **Estimated hosted cost:** **$0.001–$0.02 per repair** (≈ 2,000–8,000 tokens).
  This is an **estimate**, not a measured billed figure — no hosted call has been
  billed, because no key is configured.
- **[EXTERNAL / PROTECTED — founder action required to enable]** Hosted mode is
  enabled by setting a provider key, e.g. `gh secret set DEEPSEEK_API_KEY`. Until
  a key is set in a sanctioned environment, hosted mode stays unavailable and the
  pilot remains on the $0 deterministic-local engine.

### Cost summary

| Mode | Compute cost to NOOS | Availability today |
|---|---|---|
| Deterministic-local (pilot default) | **$0 / repair** | Available |
| Hosted model | **Est. $0.001–$0.02 / repair** (≈2–8k tokens) | **Not enabled** (no API key set) |

---

## 6. Pricing proposal (founder-editable — **PROPOSAL ONLY**)

> **These figures are a PROPOSAL for the founder to set.** They are not committed
> prices and no billing is wired. The first pilot requires **no payment
> automation** — invoicing/collection, if any, is handled manually by the founder
> outside this system.

Suggested per-job placeholder structure (edit the numbers):

| Line item | Placeholder | Notes |
|---|---|---|
| Pilot price per repair job | **$[FOUNDER_SETS]** | e.g. a flat per-job fee, founder-set |
| Successful-repair-only pricing? | **$[FOUNDER_DECIDES]** | Founder may choose to charge only when a verified patch is delivered |
| Pilot package (N jobs) | **$[FOUNDER_SETS]** | Optional bundle for a manually onboarded pilot customer |

Guidance for setting the number: since the deterministic-local engine costs **$0
compute** and hosted mode is estimated at **$0.001–$0.02/repair**, essentially any
positive per-job price yields a high compute gross margin. The real costs to price
against are **founder/operator time** for manual onboarding and review, not
compute (see §7).

---

## 7. Gross-margin model (simple, illustrative)

Gross margin per job, on the compute basis:

```
gross_margin_per_job = price_per_job − compute_cost_per_job

Deterministic-local (pilot default):
    compute_cost_per_job = $0
    gross_margin_per_job = price_per_job − $0 = price_per_job   (≈100% on compute)

Hosted mode (if later enabled):
    compute_cost_per_job = $0.001 … $0.02   (estimate)
    gross_margin_per_job = price_per_job − ($0.001 … $0.02)
```

Worked illustration (placeholder price only — **founder sets the real price**):

| Price/job (placeholder) | Mode | Compute cost | Gross margin/job | Gross margin % (compute) |
|---|---|---|---|---|
| $25 | Deterministic-local | $0 | $25.00 | ~100% |
| $25 | Hosted (est high $0.02) | $0.02 | $24.98 | ~99.9% |
| $50 | Deterministic-local | $0 | $50.00 | ~100% |

**Caveat (not a hidden cost — stated plainly):** this model covers **compute
cost only**. It excludes founder/operator time for manual onboarding, review, and
support, which is the dominant real cost of the managed pilot. Compute
gross-margin percentages above are not a claim about net margin or
profitability.

---

## 8. Security and data handling boundary

- **No secrets committed.** No provider API key exists in any sanctioned
  environment.
- **Worker network** is limited to the configured model-provider endpoint;
  repair patches may not add network calls to forbidden hosts.
- **Repair patches are confined** to the recipe's allowed paths; forbidden paths
  are never touched.
- **Human approval before merge** — no auto-merge, no auto-deploy.
- **Data handling:** customer repository content is processed **transiently** in
  an isolated worktree. Artifacts are retained **30 days**.
- **No security certification is claimed.** The items above describe the pilot's
  operating boundary; they are not a compliance or certification statement.

---

## 9. Support boundary

- Managed pilot, **manually onboarded**.
- **Best-effort** support. **No SLA is claimed.**
- No uptime, latency, or repair-rate guarantee is claimed. The proven results in
  §2 are fixture results with `receipt_origin = local_reference`, not a
  reliability guarantee for arbitrary customer repositories.

---

## 10. Protected / external items (not enabled today)

Marked clearly so no live claim is implied:

- **[EXTERNAL — founder action]** Hosted-model mode requires a provider key:
  `gh secret set DEEPSEEK_API_KEY`. No key is set in any sanctioned environment,
  so hosted mode is unavailable today.
- **[GATED — not applied]** Additive persistence migration `0021`
  (`0021_software_repair_runway.sql`) is **ready-to-apply but NOT applied**
  (production-gated).
- **[PROTECTED]** The canonical `http_loop` producer restore is protected; the
  Railway token is absent. This is separate from repair-job execution.
- **[NON-CANONICAL LIVENESS]** A real sanctioned factory-autorun GitHub Actions
  run proved the Supabase sink + factory + projection are **LIVE today**, but by
  **manual origin** — this is **not** canonical organic liveness. Per §2, a repair
  job's success never establishes production liveness regardless.

---

## 11. Commands (reference)

Run a single repair job (JSON output):

```
python3 scripts/noos_software_repair_runner_v1.py --job <job-spec> --json
```

Start the customer API + minimal UI (listens on `:8811`):

```
python3 scripts/noos_software_repair_api_v1.py
```

---

SUBMITTED for independent verification (author != subject). canon_version: FOUNDER_CANON_v1+MACHINE_LOOPS_v1
