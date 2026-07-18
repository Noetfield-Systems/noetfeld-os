# NOOS Software Repair Runway — Quick Start (Managed Pilot)

**Time to first result:** about five minutes with a bundled fixture.
**Recipe:** `software_repair_ci_v1` v1.0.0 (status: pilot).

This guide walks you through submitting a repair commission two ways — from the
command line and from the HTTP API / minimal UI — retrieving the verified patch,
report, verification evidence, and cost, and authorizing NOOS to work on your
repository.

---

## 1. What this is (and what it never does)

You submit a **failing repository, failing CI run, failing test command, or a
reproducible defect**. NOOS then:

1. **Reproduces** the failure in an isolated copy of your code (records the
   real failing exit code — tests *before*).
2. **Classifies and plans** the defect.
3. **Repairs** it with a fault-localized, bounded mutation search. Every
   candidate patch is re-run against your real tests in an isolated copy;
   **only a candidate that makes the tests pass is proposed**. The engine does
   not fabricate a passing result.
4. **Returns** a verified patch bundle (or a **draft** pull request, if you
   explicitly authorize one), a customer report, verification evidence, and an
   audit receipt.

**Human-approval boundary — NOOS never does these for you:**

- No auto-merge and no auto-deploy.
- No secret / credential change.
- No branch-protection change.
- No repository-ownership change.
- No billing change.
- No modification of forbidden paths (see §9).

A repaired job is a **draft** you review and merge yourself.

---

## 2. Pilot scope (read before you submit)

The pilot is deliberately narrow. There is **no universal-language or
universal-repository claim.**

| Item | Pilot support |
|---|---|
| Languages / test runners | **Python (`pytest`) and Node (`node --test`) only** |
| Failure inputs accepted | failing test command, failing CI run id, reproducible defect description |
| Repository sources | a GitHub repo you authorize, or a bundled local fixture |
| Max repository size | 50 MB |
| Max changed files per repair | 3 |
| Max patch size | 20 KB |
| Max model calls | 4 |
| Max repair attempts | 3 |
| Execution timeout | 300 s (per-model-call 60 s) |
| Artifact retention | 30 days |

If your stack or defect falls outside this table, the pilot is not yet a fit —
that is a scope statement, not a failure.

---

## 3. Prerequisites

- Python 3 (the runner and API use only the Python standard library).
- The `noos-software-repair` repository checked out locally.
- For a real repair against your own code: a GitHub repository you can grant
  read+write access to (see §8). To just try the flow, use a bundled fixture —
  no external access required.

The pilot runs on a **deterministic local engine** with **$0 compute cost**. A
hosted model provider is **not enabled** in any sanctioned pilot environment
today (see §10).

---

## 4. Five-minute quick start

### Path A — command line, against a bundled fixture

The repo ships three real fixture commissions you can run immediately:

```bash
# from the repo root
python3 scripts/noos_software_repair_runner_v1.py \
  --job fixtures/repair/jobs/job1-unit-regression.json \
  --json
```

This runs one commission end to end and prints a JSON result. On success you
will see (field names shown; values differ per run):

```json
{
  "ok": true,
  "job_status": "repaired",
  "execution_id": "exe_...",
  "state": "COMPLETED",
  "receipt_path": "receipts/runway/software-repair-job-exe_....json",
  "patch_path": "dist/repair-bundles/...",
  "patch_hash": "...",
  "report_path": "...",
  "delivery": "...",
  "tests_before": { "exit_code": 1 },
  "tests_after":  { "passed": true }
}
```

The process exits `0` when `job_status` is `repaired`, non-zero otherwise.

The three bundled fixtures cover three real defect classes, each verified from a
real failing test (exit 1) to a real passing test (exit 0):

| Fixture job | Defect class |
|---|---|
| `job1-unit-regression.json` | off-by-one range regression (unit test) |
| `job2-lint-failure.json` | unused-import lint failure (ruff `F401`) |
| `job3-integration-data.json` | wrong-operator data-aggregation defect (opens a **draft** PR when authorized) |

### Path B — HTTP API and minimal UI

Start the service (binds to `127.0.0.1:8811`; API and UI share one backend, so
CLI, API, and UI have full parity):

```bash
python3 scripts/noos_software_repair_api_v1.py       # serves on :8811
# custom port: python3 scripts/noos_software_repair_api_v1.py 9000
```

- **UI:** open <http://127.0.0.1:8811/> in a browser, edit the pre-filled
  commission, and click **Submit repair commission**. The UI shows the
  lifecycle states, the repaired/unrepaired outcome, the before→after test
  result, and the verified patch, with links to the report, receipt, and cost.
- **Health check:** `GET http://127.0.0.1:8811/health`
- **Submit a commission:**

```bash
curl -s http://127.0.0.1:8811/repair/commissions \
  -H 'Content-Type: application/json' \
  --data-binary @fixtures/repair/jobs/job1-unit-regression.json
```

The response includes a `job_id` (the execution id) you use to retrieve
everything in §7.

> Pilot note: submissions run **synchronously** (fixture jobs take seconds). A
> production build would enqueue and stream progress instead.

---

## 5. Anatomy of a commission (sample input)

A commission is a small JSON job spec. Here is a real bundled example
(`fixtures/repair/jobs/job1-unit-regression.json`):

```json
{
  "commission_id": "SR-JOB-1-unit-regression",
  "customer_id": "fixture-customer",
  "recipe_id": "software_repair_ci_v1",
  "recipe_version": "1.0.0",
  "repository": {
    "kind": "local_fixture",
    "path": "fixtures/repair/py-unit-regression",
    "base_commit": "fixture-base",
    "target_branch": "main"
  },
  "failure": {
    "kind": "failing_test_command",
    "test_command": ["python3", "-m", "pytest", "tests", "-q"],
    "allowed_files": ["src/mathutil.py"]
  },
  "open_pr": false,
  "defect_class": "unit_test_regression"
}
```

**Field reference:**

| Field | Required | Notes |
|---|---|---|
| `commission_id` | yes | Your identifier for this job. |
| `recipe_id` | yes | Must be `software_repair_ci_v1`. |
| `repository.kind` | yes | `github` (your repo) or `local_fixture` (bundled). |
| `repository.path` / repo ref | yes | Fixture path, or your authorized GitHub repo. |
| `repository.target_branch` | — | Base branch; never modified in place (see §8). |
| `failure.test_command` | yes | The command that reproduces the failure. Wins over auto-discovery. |
| `failure.allowed_files` | — | Narrows where the repair may edit, within recipe allowed paths. |
| `open_pr` | — | `true` requests a **draft** PR (requires PR authorization); otherwise a patch bundle. |
| `defect_class` | — | Your declared class; NOOS also classifies independently. |

For your own repository, set `repository.kind` to `github` and reference the
repo you authorized in §8.

---

## 6. Lifecycle states

Each commission is tracked by a deterministic state machine. The success path
is:

```
ACCEPTED → PLANNED → DISPATCHED → CLAIMED → RUNNING → OUTPUT_COMMITTED → COMPLETED
```

- **Terminal success:** `COMPLETED` (with repair outcome `job_status: repaired`).
- **Terminal alternatives:** `FAILED`, `TIMED_OUT`, `CANCELLED`,
  `DEAD_LETTERED` (with repair outcome `job_status: unrepaired`).
- A terminal state is final: it cannot resurrect into `RUNNING`. Recovery goes
  through the explicit **replay** path, which starts a new execution and
  preserves lineage back to the original.

Note two distinct signals: `state` is the motor lifecycle state above;
`job_status` (`repaired` / `unrepaired`) is the repair outcome.

---

## 7. Retrieving patch, report, verification, and cost

### Command line

The runner result (§4) already contains `receipt_path`, `patch_path`,
`patch_hash`, and `report_path`. Open those files directly. The receipt under
`receipts/runway/` is the full audit record: lifecycle history, hashes, and
model-call records.

### API endpoints

For a submitted `job_id`:

| Endpoint | Returns |
|---|---|
| `GET /repair/jobs/<job_id>` | Full audit receipt (lifecycle, hashes, model calls). |
| `GET /repair/jobs/<job_id>/events` | Lifecycle state history. |
| `GET /repair/jobs/<job_id>/artifacts` | `patch_path`, `report_path`, `patch_hash`, `delivery`. |
| `GET /repair/jobs/<job_id>/report` | Customer report (Markdown): root cause, changed file, test evidence, patch. |
| `GET /repair/jobs/<job_id>/verification` | `tests_before` and `tests_after` (captured output + exit codes). |
| `GET /repair/jobs/<job_id>/cost` | Per-call model records and `total_cost_usd`. |
| `POST /repair/jobs/<job_id>/replay` | New execution, lineage preserved (`replay_of`). |
| `POST /repair/jobs/<job_id>/cancel` | Pilot jobs run synchronously to a terminal state; cancel applies to queued jobs in the production build. |

The **verification evidence** is the proof to check first: `tests_before`
shows the real failing exit code, `tests_after` shows the passing result. The
patch bundle carries an output hash for integrity.

---

## 8. Repository authorization guide

You stay in control of scope and of the merge.

**What you grant.** For a real repair against your own code, authorize
**read + write** access to **one specific GitHub repository**. NOOS operates
only on the repository you name in the commission. It never touches a
repository it was not explicitly given.

**How your code is handled.** Your repository content is processed
**transiently** inside an isolated worktree for the duration of the job. All
changes happen on an isolated branch `noos/repair/<job_id>`; the base branch and
`main` are **never modified in place**. Artifacts are retained for **30 days**.

**Delivery — patch bundle by default, draft PR only on request.**

- Default (`open_pr: false`, or PR not authorized): NOOS produces a downloadable
  **patch bundle** — nothing is pushed to your repo.
- On request (`open_pr: true` **and** you granted `pr:write`): NOOS opens a
  **draft** pull request from the `noos/repair/<job_id>` branch. It is a draft:
  you review, approve, and merge. NOOS does not merge it.

**The merge is always yours.** Human approval is required before merge. NOOS
never auto-merges, never auto-deploys, and never changes secrets,
branch-protection, ownership, or billing.

---

## 9. Forbidden and allowed paths

The repair is confined to the recipe's allowed paths, and these paths are
**never touched**, regardless of the commission:

**Forbidden (never modified):**
`.github/**`, any `secrets*`, `*.pem`, `*.key`, `.env*`, `Dockerfile`,
`deploy/**`, `infrastructure/**`, `*.tf`, `package-lock.json`, `poetry.lock`,
`.git/**`, `CODEOWNERS`, `branch-protection*`, `billing*`.

**Allowed (repair may edit, within your `allowed_files`):**
`src/**`, `lib/**`, `app/**`, `tests/**`, `test/**`, and top-level
`*.py` / `*.js` / `*.ts`.

If a repair would require editing a forbidden path, the pilot does not do it.

---

## 10. Model execution and cost

- **Today (pilot):** repairs run on a **deterministic local engine**. Compute
  cost is **$0**. Cost queries return `total_cost_usd: 0` with no model-call
  records.
- **Model router:** a provider-neutral, OpenAI-compatible adapter (works with
  DeepSeek / Moonshot / any OpenAI-compatible endpoint) is implemented. However,
  **no model-provider API key exists in any sanctioned pilot environment**, so a
  real hosted-model call is **not available today**.
- **Hosted enablement is a protected operator action** (not part of customer
  onboarding): an operator sets the provider key via
  `gh secret set DEEPSEEK_API_KEY`. Estimated hosted cost is **$0.001–$0.02 per
  repair** (~2–8k tokens). This estimate is not a committed price.

---

## 11. Security, data handling, and support boundaries

- **Secrets:** none are committed to the repository.
- **Network:** the worker has no outbound network except the configured model
  provider endpoint; repair patches may not add network calls to forbidden
  hosts.
- **Scope confinement:** patches are confined to recipe allowed paths; forbidden
  paths are never touched; human approval precedes any merge.
- **Data handling:** your repo content is processed transiently in an isolated
  worktree; artifacts are retained 30 days.
- **Support:** this is a **manually onboarded managed pilot**, delivered on a
  **best-effort** basis. **No SLA is claimed. No security certification is
  claimed.**

---

## 12. Provenance (important)

A repaired **job** is a **customer outcome** — it means your tests went from
failing to passing on a verified patch. It is recorded with
`receipt_origin: local_reference` and **can never, by itself, establish
production infrastructure liveness.** Customer-job success and infrastructure
liveness are separate predicates, and the tooling keeps them separate.

---

*SUBMITTED for independent verification (author != subject). canon_version: FOUNDER_CANON_v1+MACHINE_LOOPS_v1*
