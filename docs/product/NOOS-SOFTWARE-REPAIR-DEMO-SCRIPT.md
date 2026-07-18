# NOOS Software Repair Runway — Live Demo Script

Sales demonstration procedure for the **Managed Pilot**. Every step below runs on
the offline, deterministic-local engine that is verified today. Follow the steps
in order; each command is exact and copy-pasteable.

**What the demo proves.** A customer submits a failing repository / failing test
command / reproducible defect. NOOS reproduces the failure against the real tests,
localizes the fault, searches for a bounded patch, re-runs the real tests to
verify, and returns a verified patch bundle + customer report + audit receipt.
**A human approves before any merge.** NOOS never auto-merges and never auto-deploys.

**What the demo does NOT claim.** No universal-language or universal-repository
support (pilot is Python `pytest` and Node `node:test` only). No guaranteed repair.
No autonomous deployment. No security certification. No reliability percentage.
A repaired job is a **customer outcome**, not proof that any production
infrastructure is live — the demo shows this separation explicitly in Part 4.

---

## 0. Pre-demo setup (do this before the customer joins)

```bash
cd /Users/sinakazemnezhad/Desktop/Noetfield-Systems/noos-software-repair
python3 --version          # Python 3 required (stdlib only; no third-party deps)
ruff --version             # required only for the lint-failure fixture (Part 1, defect 2)
```

Facts to state up front, plainly:

- **Compute cost today: $0.** The pilot runs a deterministic-local repair engine
  (`noos_repair_engine_v1`): fault-localized, bounded **mutation search**. Every
  candidate patch is applied in an isolated copy and re-run against the customer's
  real tests; only a candidate that turns the real tests green is proposed. The
  engine never fabricates a passing result.
- **Hosted-model calls are UNAVAILABLE today.** The model router is a
  provider-neutral, OpenAI-compatible adapter (DeepSeek / Moonshot /
  OpenAI-compatible) and is complete, but **no model-provider API key exists in any
  sanctioned environment**, so no real hosted-model call can be made right now.
  Enabling a hosted model is one command — `gh secret set DEEPSEEK_API_KEY` — with
  an estimated cost of **$0.001–$0.02 per repair (~2–8k tokens)**. Do not promise
  hosted behavior you cannot demonstrate; demo the deterministic-local engine.

**Recipe and hard limits** (recipe `software_repair_ci_v1`, version `1.0.0`,
status: pilot — `data/recipes/software_repair_ci_v1.json`):

- Supported stacks (pilot): **Python (`pytest`) and Node (`node:test`) only.**
- Limits: **max 3 changed files, 20 KB patch, 4 model calls, 3 repair attempts,
  300 s timeout**, max repo 50 MB, artifacts retained **30 days**.
- Forbidden paths NOOS will never touch: `.github/`, secrets, `*.pem`/`*.key`,
  `.env*`, `Dockerfile`, `deploy/`, `infrastructure/`, `*.tf`, lockfiles
  (`package-lock.json`, `poetry.lock`), `CODEOWNERS`, branch-protection, billing.
- Human-approval boundary (recipe-enforced): no auto-merge, no auto-deploy, no
  secret/credential change, no branch-protection change, no repository-ownership
  change, no billing change.

---

## 1. The three fixture defect classes

The pilot ships three real fixture repositories, one per defect class. Each has a
**real failing test suite (exit 1)** repaired to a **real passing suite (exit 0)**
by a verified patch. Job specs live in `fixtures/repair/jobs/`.

| # | Defect class | Fixture repo | Failing check | Patched file |
|---|---|---|---|---|
| 1 | Off-by-one range regression (`unit_test_regression`) | `fixtures/repair/py-unit-regression` | `python3 -m pytest tests -q` | `src/mathutil.py` |
| 2 | Unused-import lint failure — ruff F401 (`lint_type_failure`) | `fixtures/repair/py-lint-failure` | `ruff check src --output-format concise` | `src/textutil.py` |
| 3 | Wrong-operator data-aggregation defect (`integration_data_handling_defect`) | `fixtures/repair/py-integration-data` | `python3 -m pytest tests -q` | `src/aggregate.py` |

Defect 3's job spec sets `open_pr: true` — its delivery includes the exact
draft-PR command a human runs after approval (see Part 3).

---

## 2. Demo track A — CLI runner (simplest, fully scriptable)

Run each defect class end to end. `--json` prints the full machine result.

**Defect 1 — off-by-one range regression:**

```bash
python3 scripts/noos_software_repair_runner_v1.py \
  --job fixtures/repair/jobs/job1-unit-regression.json --json
```

**Defect 2 — unused-import lint failure (ruff F401):**

```bash
python3 scripts/noos_software_repair_runner_v1.py \
  --job fixtures/repair/jobs/job2-lint-failure.json --json
```

**Defect 3 — wrong-operator data-aggregation defect:**

```bash
python3 scripts/noos_software_repair_runner_v1.py \
  --job fixtures/repair/jobs/job3-integration-data.json --json
```

**What to point at in each result** (the JSON keys are literal):

- `job_status`: `repaired` on success; exit code is `0` when repaired, `1` otherwise.
- `tests_before` → `passed: false`, `exit_code: 1` (the real failure, reproduced).
- `tests_after` → `passed: true`, `exit_code: 0` (the real tests, now passing).
- `patch_path` / `patch_hash`: the verified unified-diff bundle and its SHA-256.
- `report_path`: the customer report (Markdown).
- `receipt_path`: the full audit receipt at
  `receipts/runway/software-repair-job-<execution_id>.json`.
- `receipt_origin`: `local_reference` — say this out loud; it matters in Part 4.

**Show the actual before → after, patch, report, and receipt** (substitute the
`execution_id` printed above, e.g. `exe_f72b385885fb4211`):

```bash
# The failing-then-passing evidence, captured verbatim in the receipt:
python3 -c "import json,sys; r=json.load(open(sys.argv[1])); \
print('BEFORE exit', r['tests_before']['exit_code'], '| passed', r['tests_before']['passed']); \
print('AFTER  exit', r['tests_after']['exit_code'],  '| passed', r['tests_after']['passed'])" \
  receipts/runway/software-repair-job-<execution_id>.json

# The verified patch (unified diff) and the human-readable customer report:
cat dist/repair-bundles/<execution_id>.patch
cat dist/repair-bundles/<execution_id>.report.md
```

**Optional talking point — the engine cannot fake a green.** The receipt records
`repaired.model_call.candidates_tried` (a real integer, e.g. 19 for defect 1): the
number of candidate patches the mutation search applied and re-tested against the
customer's real suite before one passed. `provider` is `deterministic-local`,
`model` is `fault-localized-mutation-search`, and `cost_usd` is `0.0`.

---

## 3. Demo track B — customer API + minimal UI

Same backend as the CLI, exposed over a narrow HTTP surface (Python standard
library only). Start the server (binds to `127.0.0.1:8811`):

```bash
python3 scripts/noos_software_repair_api_v1.py     # serves on 127.0.0.1:8811
```

**UI walkthrough (for a non-technical audience).** Open
`http://127.0.0.1:8811/` in a browser. The page is pre-filled with a commission.
Click **Submit repair commission**. Show:

- the result state (`repaired`) and the lifecycle chips
  (ACCEPTED → PLANNED → DISPATCHED → CLAIMED → RUNNING → OUTPUT_COMMITTED → COMPLETED);
- **Tests: before exit 1 → after PASSING**;
- the verified patch inline;
- the **report / receipt / cost** links.

The UI banner states the honest boundary: "A repaired job is a customer outcome,
**not** infrastructure liveness."

**API walkthrough (for a technical audience).** Every customer touchpoint is a
plain HTTP call — CLI/automation has full parity with the UI.

```bash
# Health:
curl -s http://127.0.0.1:8811/health

# Submit a commission (returns job_id, job_status, lifecycle, patch, verification):
JOB_ID=$(curl -s -X POST http://127.0.0.1:8811/repair/commissions \
  -H 'Content-Type: application/json' \
  --data-binary @fixtures/repair/jobs/job3-integration-data.json \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['job_id'])")
echo "job: $JOB_ID"

# Job state / full audit receipt:
curl -s http://127.0.0.1:8811/repair/jobs/$JOB_ID

# Lifecycle events:
curl -s http://127.0.0.1:8811/repair/jobs/$JOB_ID/events

# Verification evidence (tests-before failing / tests-after passing):
curl -s http://127.0.0.1:8811/repair/jobs/$JOB_ID/verification

# Artifacts (patch path + hash, report path, delivery):
curl -s http://127.0.0.1:8811/repair/jobs/$JOB_ID/artifacts

# Customer report (Markdown):
curl -s http://127.0.0.1:8811/repair/jobs/$JOB_ID/report

# Cost (model-call records + total; $0.00 on the deterministic-local engine):
curl -s http://127.0.0.1:8811/repair/jobs/$JOB_ID/cost

# Replay preserves lineage (returns a new execution linked by replay_of):
curl -s -X POST http://127.0.0.1:8811/repair/jobs/$JOB_ID/replay

# Cancel (pilot jobs run synchronously to terminal; cancel applies to queued
# jobs in the production build):
curl -s -X POST http://127.0.0.1:8811/repair/jobs/$JOB_ID/cancel
```

**Show the delivery boundary — draft PR vs. patch bundle (human-approval).** For
defect 3 (`open_pr: true`), inspect `delivery` on the receipt:

```bash
curl -s http://127.0.0.1:8811/repair/jobs/$JOB_ID/artifacts \
  | python3 -m json.tool
```

- `delivery.patch_bundle` — the downloadable, verified patch the customer receives.
- `delivery.draft_pr` — `null` in the pilot (no live GitHub push is performed).
- `delivery.pr_command` — the **exact** command a human runs *after approval* to
  open a **draft** PR against their own authorized repo. It creates a branch
  `noos/repair/<execution_id>`, applies the patch, commits, pushes, and runs
  `gh pr create --draft`. NOOS produces the command and the patch; **a person
  executes the merge path.** This is the human-approval boundary, made concrete.

Stop the server with `Ctrl-C` when finished.

---

## 4. Part 4 — a repaired job is NOT infrastructure liveness (say this explicitly)

This is the integrity moment of the demo. A green repair job proves the product
behaved correctly on the customer's code. It is `receipt_origin=local_reference`
and **can never establish that any production infrastructure is running.**
Customer-job success and infra liveness are **separate predicates** — the code
enforces the separation.

Run the production-liveness gate with the repaired job's own provenance values
(every generic health signal set to "true" on purpose):

```bash
python3 -c "import sys; sys.path.insert(0,'scripts'); \
import noos_observability_semantics_v1 as sem, json; \
print(json.dumps(sem.production_running_confirmed( \
  receipt_origin='local_reference', producer='noos-software-repair-runner-local', \
  execution_plane='local', dispatch_correlated=True, lifecycle_valid=True, \
  terminal_evidence_valid=True, freshness_within_slo=True), indent=2))"
```

Exact output:

```json
{
  "production_running_confirmed": false,
  "execution_state": "COMPLETION_UNPROVEN",
  "normalized_origin": "local_reference",
  "checks": {
    "origin_is_organic": false,
    "origin_is_production_eligible": false,
    "producer_allowlisted": false,
    "execution_plane_canonical": false,
    "dispatch_correlated": true,
    "lifecycle_valid": true,
    "terminal_evidence_valid": true,
    "freshness_within_slo": true
  },
  "failed_predicates": [
    "origin_is_organic",
    "origin_is_production_eligible",
    "producer_allowlisted",
    "execution_plane_canonical"
  ],
  "blocked_reason": "non_production_origin:local_reference"
}
```

**The point to make:** even with dispatch, lifecycle, terminal evidence, and
freshness all "true", `production_running_confirmed` is `false` because the origin
is `local_reference`, not `organic`. Production liveness requires an allowlisted
deployed producer on the canonical execution plane with a genuine organic
completion — a repair, replay, manual, migration, or local run can never pass this
gate. That is why a customer repair result is honest: it never masks itself as
deployed-system health.

---

## 5. Reliability, security, and data handling (state, don't overclaim)

**Reliability properties verified in the worktree suite** (348 tests passed —
report as a build-verification fact, not a field-reliability percentage): idempotent
deduplication, bounded retry with backoff, lease owner + expiry + reclaim,
dead-letter routing, replay that preserves lineage, output-hash integrity, and
BFS-proven terminal states that cannot resurrect.

**Security boundary:** no secrets are committed; the worker's network is limited to
the configured model endpoint; repair patches are confined to the recipe's allowed
paths; forbidden paths are never touched; **human approval is required before
merge.** *(No security certification is claimed.)*

**Data handling:** customer repository content is processed **transiently** in an
isolated worktree; produced artifacts are retained **30 days**.

**Support boundary:** this is a **managed pilot** — manually onboarded, best-effort.
**No SLA is claimed. No security certification is claimed.**

---

## 6. Protected / external items (do NOT demo as live — name them honestly)

These are real capabilities that are **gated, not active** in a sanctioned
environment today. Do not present any of them as running.

- **[EXTERNAL — requires a founder gate]** Hosted-model repair. The router is
  complete, but no model-provider API key exists in any sanctioned environment.
  Enable with `gh secret set DEEPSEEK_API_KEY`; estimated **$0.001–$0.02 per
  repair**. Until then, the demo uses the deterministic-local engine.
- **[PROTECTED — not applied]** Persistence migration `0021` is **additive and
  ready to apply but NOT applied** (production-gated). Do not apply it during a demo.
- **[PROTECTED — Railway token absent]** The canonical `http_loop` producer restore
  is protected and cannot be performed here.
- **[EXTERNAL — manual origin, NOT canonical organic]** A real sanctioned
  factory-autorun GitHub Actions run demonstrated that the Supabase sink + factory +
  projection are live today, but that run is **manual origin**, not canonical
  organic execution. It does not establish canonical production liveness (see Part 4).

---

## 7. One-page run order (cheat sheet)

```bash
cd /Users/sinakazemnezhad/Desktop/Noetfield-Systems/noos-software-repair

# A. CLI — all three defect classes, failing -> verified passing
python3 scripts/noos_software_repair_runner_v1.py --job fixtures/repair/jobs/job1-unit-regression.json --json
python3 scripts/noos_software_repair_runner_v1.py --job fixtures/repair/jobs/job2-lint-failure.json     --json
python3 scripts/noos_software_repair_runner_v1.py --job fixtures/repair/jobs/job3-integration-data.json --json

# B. API + UI (127.0.0.1:8811): submit, verification, artifacts, report, cost, replay
python3 scripts/noos_software_repair_api_v1.py

# C. Integrity: prove a repaired job does NOT confirm infra liveness
python3 -c "import sys; sys.path.insert(0,'scripts'); import noos_observability_semantics_v1 as sem, json; print(json.dumps(sem.production_running_confirmed(receipt_origin='local_reference', producer='noos-software-repair-runner-local', execution_plane='local', dispatch_correlated=True, lifecycle_valid=True, terminal_evidence_valid=True, freshness_within_slo=True), indent=2))"
```

---

SUBMITTED for independent verification (author != subject). canon_version: FOUNDER_CANON_v1+MACHINE_LOOPS_v1
