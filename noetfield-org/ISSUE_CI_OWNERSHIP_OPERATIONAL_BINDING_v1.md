# Issue & CI Ownership — NOOS Operational Binding v1

**Status:** PROPOSED — pending SG ratification of `NF-UNIFIED-MOTOR-ISSUE-CI-OWNERSHIP-V1`
and founder merge of the operationalization PR. Not active authority until both land.
**Kind:** OPERATIONAL_BINDING (NOOS operationalizes; SG defines; this is not Library SSOT).
**Decision:** `NF-UNIFIED-MOTOR-ISSUE-CI-OWNERSHIP-V1` (`docs/_NOOS_AGENT/[NOOS-AGENT-20260717-001]_NF-UNIFIED-MOTOR-ISSUE-CI-OWNERSHIP-V1.md`)
**Registry:** `data/noos-canonical-roles-v1.json` · **Recipe:** `motor/registry/recipes/NF-MOTOR-CI-REPAIR-001.yaml`
**Route:** `motor/registry/bindings/noos-route-map-v1.json` → `ci_failure_candidate_repair` (NOT_WIRED)

This binding operationalizes the advisor role map for GitHub-issue / CI-failure /
incident ownership. It gives Noetfield **one accountable manager**, the **correct
specialist per failure class**, and **no omnipotent agent** that can diagnose, fix,
approve, and promote its own work.

## 1. Roles (canonical IDs)

| Role ID | Title | Owns |
|---|---|---|
| `noetfield:noos.portfolio-owner` | NOOS Portfolio Continuation Owner | parent identity; hosts the two capabilities below |
| `noetfield:noos.issue-manager` | NOOS Issue Manager | intake · dedup · classify · route · closure-evidence (capability of portfolio-owner, **not** a new cloud agent) |
| `noetfield:noos.ci-reliability-owner` | NOOS CI Reliability Owner | CI-system health, flaky tests, workflow defects, runner faults (profile under NOOS) |
| `noetfield:sandbox.builder-owner` | SANDBOX Builder Owner | candidate-caused CI **repair** via `NF-MOTOR-CI-REPAIR-001` + bounded worker |
| `noetfield:sourcea.dispatch-owner` | SourceA Dispatch Owner | compiles the bounded repair job |

The **Issue Manager** does not normally edit code. It confirms evidence-based closure —
a green rerun alone does **not** close an issue whose original failure was flaky or whose
cause is unknown.

## 2. Intake → routing flow

```text
GitHub issue / failed check / incident
        ↓
  NOOS Issue Manager  (classify · deduplicate · prioritize · resolve owner)
        ↓  route by fault domain
candidate-caused        → SANDBOX Builder Owner → SourceA compiles job → Motor NF-MOTOR-CI-REPAIR-001
workflow/runner/flaky   → CI Reliability Owner
secret / authority      → SG + founder gate
production promotion     → Release Owner
external outage         → retry / backoff / observe (no code patch by default)
```

**Do not give every CI failure to the Builder.** Classify first; the correct solver
depends on the fault domain:

| Failure class | Owning solver |
|---|---|
| Candidate code or test regression | SANDBOX Builder Owner |
| Stale test contract from an intentional change | SANDBOX Builder Owner |
| Formatting / lint / type / build error | SANDBOX Builder Owner |
| GitHub Actions workflow logic defect | CI Reliability Owner (founder-gated if deployment authority changes) |
| Runner outage / GitHub infra failure | NOOS Platform Operations route |
| Secret missing / expired / mis-scoped | SG/Secrets authority route (founder-gated) |
| Production deployment workflow failure | Release / Promotion Owner |
| Flaky / nondeterministic test | CI Reliability Owner |
| External service outage | Observe + retry per policy; no code patch by default |
| Security finding | Security recipe + focused independent review |
| Unsupported / ambiguous | **Stop and escalate; do not guess** |

## 3. Issue lifecycle

```text
DETECTED → INGESTED → DEDUPLICATED → CLASSIFIED → OWNER_ASSIGNED → RECIPE_SELECTED
→ SANDBOXED → REPAIR_IN_PROGRESS → CI_RECHECKING → RESOLVED_CANDIDATE
→ PROMOTION_AUTHORIZED → CLOSED_WITH_EVIDENCE
```
Terminal alternatives: `BLOCKED_AUTHORITY` · `BLOCKED_EXTERNAL` · `DUPLICATE` ·
`NOT_REPRODUCIBLE` · `SUPERSEDED` · `WONT_FIX_WITH_REASON`.

## 4. Separation of duties (no omnipotent agent)

```text
Issue Manager          = decides what the problem is and who owns it
SourceA Dispatch Owner = compiles the bounded repair job
SANDBOX Builder Owner  = owns code repair execution (bounded worker: Codex Cloud/SDK)
CI Reliability Owner   = owns CI-system faults and flaky infrastructure
CI itself              = deterministic verification
Verifier               = reviews only when risk justifies it
Founder                = approves consequential authority or promotion changes
```
The Issue Manager must **never** silently classify, patch, verify, approve, and merge
its own work. Codex is the **worker adapter — not the institutional CI owner**.

## 5. The CI-repair recipe

`NF-MOTOR-CI-REPAIR-001` (v1.0.0) is the bounded executor for **candidate-caused** CI
failures only. It runs in a `git_worktree` sandbox (`production_write: false`), may
inspect logs / reproduce / modify the candidate branch / add-or-update tests / rerun /
push / update the PR — and is **forbidden** to weaken required checks, modify secrets,
broaden deployment authority, force-push, merge, or deploy. Success requires the exact
failed check to pass externally with no required check weakened; promotion is
founder-merge only. Recipes are L5 / founder-gated: the recipe diff **is** the policy
review.

## 6. Forbidden (all roles)

`self_approval` · `check_bypass` · `silent_test_weakening` ·
`unauthorized_secret_change` · `unauthorized_production_trigger_change`.

When a workflow edit changes permissions, secrets, environments, branch triggers, or
production targets → **founder / SG authority required**.

---
SUBMITTED for independent verification. NOOS operationalizes; SG ratifies the decision;
the founder merges. `LAWS: FOUNDER_CANON v1 + governed-autorun v3. Violations = BLOCKED_WITH_REASON.`
