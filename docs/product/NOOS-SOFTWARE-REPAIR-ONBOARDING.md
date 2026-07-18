# NOOS Software Repair Runway — Customer Onboarding (Managed Pilot)

This guide onboards a customer to the **NOOS Software Repair Runway** managed
pilot. You submit a failing repository, failing CI run, failing test, or a
reproducible defect. NOOS reproduces the failure, plans a fix, produces a
**test-verified** patch, and returns a verified draft pull request (or a patch
bundle) plus a customer report and audit receipts.

**Human approval is required before merge. NOOS never auto-merges and never
auto-deploys.**

This is a **manually onboarded managed pilot**. It is best-effort. There is
**no SLA** and **no security certification** is claimed. The scope below is the
literal scope: statements here describe what the pilot does today, not aspirations.

---

## 1. What the pilot does (and does not) do

**Does:**

- Reproduces a failing test / CI / defect in an isolated worktree.
- Fault-localizes, then runs a **bounded mutation search** (`noos_repair_engine_v1`):
  every candidate patch is re-run against your **real tests** in an isolated copy.
  Only a candidate that turns the failing tests green is proposed. The engine does
  not fabricate a passing result — a proposal always carries real before/after test
  output and exit codes.
- Returns a verified patch, a customer report, verification evidence, a cost record,
  and a full audit receipt.

**Does not:**

- Does not support arbitrary languages. The pilot supports **Python (`pytest`)**
  and **Node (`node --test`)** only. There is **no universal-language or
  universal-repository claim**.
- Does not guarantee a repair. If no candidate within the bounds makes the tests
  pass, the job ends without a proposed patch and reports that honestly.
- Does not merge, deploy, change secrets, change branch protection, change
  repository ownership, or change billing. See §6.

---

## 2. Prerequisites

To run against a **local fixture** (no external access required), you need:

- Python 3.12+ (the runner and API are Python standard library only; no
  third-party dependency is required for the local reference path).
- The repository checkout containing the runner and API scripts.

To run against **your own GitHub repository** (customer-authorized), you also need:

- A GitHub repository where the failure reproduces.
- **[EXTERNAL / CUSTOMER ACTION]** Repository authorization: `read` access is
  required to reproduce; `write` (branch push) and `pr:write` are required only
  if you want a draft PR opened rather than a downloadable patch bundle. NOOS
  **never touches a repository it was not explicitly given.**
- A failing input that reproduces (see §4).

Optional (only if you want model-proposed repairs beyond the deterministic
engine): a model-provider API key. See §7. **No model-provider key is required
for the pilot** — the default engine is deterministic and runs at $0 compute cost.

---

## 3. Authorizing a repository

Supported repository sources (`accepted_repository_providers`): `github` and
`local_fixture`.

### 3a. Local fixture (fastest path, fully offline)

Point a commission at a bundled fixture. No external network or credentials are
used. This is the recommended first run.

```json
{
  "commission_id": "SR-DEMO-1",
  "customer_id": "your-id",
  "recipe_id": "software_repair_ci_v1",
  "recipe_version": "1.0.0",
  "defect_class": "unit_test_regression",
  "repository": {"kind": "local_fixture", "path": "fixtures/repair/py-unit-regression"},
  "failure": {"test_command": ["python3", "-m", "pytest", "tests", "-q"],
              "allowed_files": ["src/mathutil.py"]}
}
```

### 3b. Your GitHub repository (customer-authorized)

- **[EXTERNAL / CUSTOMER ACTION]** You grant access to the specific repository.
  The pilot is manually onboarded; access scope is confirmed with you before any
  run. Grant the **narrowest** access that fits your intended output: `read` for a
  patch bundle, `read` + branch `write` + `pr:write` for a draft PR.
- NOOS operates only on the repository you name. All work happens on an isolated
  branch (`noos/repair/<job_id>`); the base branch and `main` are **never modified
  in place**.

---

## 4. Defining the failure input

A commission must carry one of the accepted failure inputs
(`accepted_failure_inputs`):

| Input | Field | Meaning |
|---|---|---|
| Failing test command | `failing_test_command` | The exact command that exits non-zero today (e.g. `python3 -m pytest tests -q` or `node --test`). |
| Failing CI run | `failing_ci_run_id` | The identifier of a CI run that failed. |
| Reproducible defect | `reproducible_defect_description` | A description precise enough to write/point at a failing test. |

Guidance:

- **A concrete failing test command is the strongest input.** The engine's entire
  guarantee is "candidate must make the real test pass," so it needs a real test to
  run. If you supply only a defect description, onboarding will help turn it into a
  failing test first.
- If you know which files may change, list them in `failure.allowed_files` to
  narrow the search. This is bounded further by the recipe constraints in §5.
- Test discovery: an explicit test command in the job spec always wins; otherwise
  the default is `pytest -q` (Python) or `node --test` (Node).

**Proven defect classes in the pilot fixtures** (real failing tests → verified
patch → passing tests, each verified locally):

1. Off-by-one range regression (unit-test regression).
2. Unused-import lint failure (`ruff` F401).
3. Wrong-operator data-aggregation defect.

These are the classes demonstrated end-to-end today. Other defects within the
supported stacks may work but are not pre-proven; the pilot reports honestly when
a repair is not found.

---

## 5. Constraints (recipe `software_repair_ci_v1` v1.0.0)

Every job runs under fixed bounds. A proposal that would exceed any bound is not
produced.

| Constraint | Limit |
|---|---|
| Supported stacks | Python (`pytest`), Node (`node --test`) **only** |
| Max changed files | 3 |
| Max patch size | 20 KB (20000 bytes) |
| Max model calls | 4 |
| Max repair attempts | 3 |
| Execution timeout | 300 s |
| Per-model-call timeout | 60 s |
| Max repository size | 50 MB |
| Artifact retention | 30 days |

**Allowed paths** (patches confined here): `src/**`, `lib/**`, `app/**`, `*.py`,
`*.js`, `*.ts`, `tests/**`, `test/**`.

**Forbidden paths (never touched):** `.github/**`, `**/secrets*`, `**/*.pem`,
`**/*.key`, `**/.env*`, `**/Dockerfile`, `**/deploy/**`, `**/infrastructure/**`,
`**/*.tf`, `**/package-lock.json`, `**/poetry.lock`, `**/.git/**`,
`**/CODEOWNERS`, `**/branch-protection*`, `**/billing*`.

If a candidate patch proposes a change to a forbidden path, it is rejected.

---

## 6. What NOOS returns, and the human-approval boundary

### 6a. Deliverables

On a successful job you receive:

- **Verified patch** — a unified diff constrained to the allowed paths and the
  size/file limits above.
- **Verification evidence** — captured **tests-before** (failing) and
  **tests-after** (passing) output and exit codes.
- **Customer report** — root cause, changed files, test evidence, provenance, cost.
- **Audit receipt** — full lifecycle, content hashes, and per-model-call records.
- **Delivery** — a **draft PR URL** (only when the job grants `pr:write` and
  `open_pr=true`) **or** a downloadable **patch bundle** path otherwise.

### 6b. Human-approval-before-merge boundary (hard limit)

NOOS stops at a verified proposal. The following are **outside** what NOOS does and
require a human:

- **No auto-merge.** A draft PR is opened as a draft; a human reviews and merges.
- **No auto-deploy.**
- No secret / credential change.
- No branch-protection change.
- No repository-ownership change.
- No billing change.
- No modification of the forbidden paths in §5.

Merging the proposed change is always **your** decision and **your** action.

### 6c. Provenance (important, honest limit)

A repair job succeeding is a **customer outcome**. It is recorded with
`receipt_origin = local_reference` for pilot runs and **can never, by itself,
establish production/infrastructure liveness**. Customer-job success and
infrastructure liveness are **separate predicates** — the report and UI keep them
separate and will not present one as the other.

---

## 7. Running a job

### 7a. CLI

```
python3 scripts/noos_software_repair_runner_v1.py --job <job-spec.json> --json
```

### 7b. Customer API + minimal UI

```
python3 scripts/noos_software_repair_api_v1.py
```

Serves an API and a minimal UI on `http://localhost:8811`. The API and UI share one
backend, so CLI and automation have full parity. The documented operations are:
submit a commission, read job state, read events, read artifacts, read the report,
read verification evidence, read cost, replay (preserving lineage), and cancel.
Submit a commission with:

```
POST /repair/commissions          # body: the commission JSON from §3
GET  /repair/jobs/<job_id>        # job state + audit receipt
GET  /repair/jobs/<job_id>/report # customer report
GET  /repair/jobs/<job_id>/cost   # cost record
```

Pilot note: submission runs synchronously (jobs take seconds). A production build
would enqueue and stream progress.

---

## 8. Cost and the exact hosted-model enablement step

### 8a. Default: deterministic engine, $0 compute

By default the pilot uses the **deterministic-local** repair engine
(fault-localized bounded mutation search). It makes **no hosted-model call** and
has **$0 compute cost**. This is the path exercised in every proven fixture job.

### 8b. Optional: model-proposed repairs (hosted model)

The model router is a **provider-neutral, OpenAI-compatible adapter** (works with
DeepSeek / Moonshot / any OpenAI-compatible endpoint). The hosted path is
**complete but idle**: **no model-provider API key exists in any sanctioned
environment today**, so a real hosted-model call is **unavailable** until a key is
provisioned. Until then, the deterministic engine is used regardless.

**[EXTERNAL / FOUNDER ACTION — enables the hosted path]** To enable real
model-proposed repairs, set a provider secret:

```
gh secret set DEEPSEEK_API_KEY --repo Noetfield-Systems/noetfeld-OS
# (or MOONSHOT_API_KEY / OPENAI_API_KEY for an OpenAI-compatible endpoint)
```

Once a key is present, model calls are real, low-temperature, and every call is
recorded (provider, model, purpose, input hash, output hash). A model-proposed
patch is still held to the **same** verification bar: it must make the real tests
pass and must not touch forbidden paths, or it is rejected.

**Estimated hosted cost** (only when a key is enabled): approximately
**$0.001–$0.02 per repair** (~2,000–8,000 tokens). This is an estimate, not a
measured or guaranteed figure.

---

## 9. Persistence and infrastructure (status, for transparency)

- **[PROTECTED / FOUNDER-GATED]** Authoritative persistence is additive migration
  `0021_software_repair_runway.sql`. It is **READY-TO-APPLY but NOT applied**;
  applying a Supabase migration is a schema (T3-class) change and is founder-gated
  via the protected `production` environment:
  `gh workflow run supabase-migrate-v1.yml -f migration=0021_software_repair_runway.sql`.
- **[PROTECTED]** The canonical `http_loop` producer restore is protected (the
  Railway token is absent in sanctioned environments).
- A sanctioned factory-autorun GitHub Actions run demonstrated that the Supabase
  sink + factory + projection are reachable (manual origin — **not** a canonical
  organic run). This does not change the provenance limit in §6c.

None of the above is required to run a pilot repair job on a local fixture or an
authorized repository via the local reference path.

---

## 10. Security and data handling (as-is, no certification claimed)

- No secrets are committed to the repository.
- The worker's outbound network is limited to the configured model-provider
  endpoint (and none at all on the default deterministic path).
- Repair patches are confined to the recipe's allowed paths; forbidden paths are
  never touched.
- Human approval is required before merge (§6b).
- **Data handling:** your repository content is processed **transiently** in an
  isolated worktree; artifacts are retained for **30 days**.
- **Support boundary:** managed pilot, manually onboarded, best-effort. **No SLA**
  is claimed and **no security certification** is claimed.

---

## 11. Onboarding checklist

1. Confirm your stack is Python (`pytest`) or Node (`node --test`).
2. Choose a source: local fixture (§3a) or your authorized GitHub repo (§3b).
3. Prepare a failing input — ideally an exact failing test command (§4).
4. Confirm you accept the constraints in §5 and the approval boundary in §6b.
5. Run via CLI (§7a) or API/UI (§7b).
6. Review the returned patch, verification evidence, report, and receipt.
7. **You** decide whether to merge. NOOS does not.
8. (Optional) If you want model-proposed repairs, arrange the hosted-model
   enablement in §8b.

---

SUBMITTED for independent verification (author != subject). canon_version: FOUNDER_CANON_v1+MACHINE_LOOPS_v1
