# NF-UNIFIED-MOTOR-ISSUE-CI-OWNERSHIP-V1 — SG architectural addendum (proposal)

**Status:** `SG_REVIEW_REQUIRED`
**Origin:** advisor role-map directive, relayed by the founder 2026-07-17.
**Authored by:** NOOS (`claude-code-noos`), lane `NOOS-LANE-issue-ci-ownership`.
**Custody:** SG **defines** this role map → NOOS **operationalizes** (this PR drafts the
operational artifacts) → verifier proves. NOOS does not ratify its own governance; SG
review + founder merge activate it.

This is a **small architectural addendum**: it names owners for GitHub-issue / CI-failure /
incident intake so Noetfield has one accountable manager, the correct specialist per
failure class, and no omnipotent agent that can diagnose, fix, approve, and promote its
own work. It does not create a sixth resident cloud agent.

## Decision (for SG ratification)

```yaml
decision_id: NF-UNIFIED-MOTOR-ISSUE-CI-OWNERSHIP-V1
status: SG_REVIEW_REQUIRED
issue_manager:
  canonical_owner: noetfield:noos.portfolio-owner
  capability_id: noetfield:noos.issue-manager
  responsibilities: [intake, deduplication, classification, prioritization, routing, closure_evidence]
ci_reliability:
  owner: noetfield:noos.ci-reliability-owner
  implementation: profile_of_noos_owner_initially
  responsibilities: [workflow_health, flake_classification, infrastructure_failure_routing, baseline_candidate_comparison]
candidate_repair:
  owner: noetfield:sandbox.builder-owner
  recipe: NF-MOTOR-CI-REPAIR-001
job_compilation:
  owner: noetfield:sourcea.dispatch-owner
verification:
  default: deterministic_ci
  semantic_review: proportional_to_risk
promotion:
  authority: founder_or_explicit_sg_policy
forbidden: [self_approval, check_bypass, silent_test_weakening, unauthorized_secret_change, unauthorized_production_trigger_change]
```

## Final answer (advisor, verbatim intent)

- **NOOS Portfolio Owner must be the Issue Manager.**
- **The SANDBOX Builder Owner must solve candidate-caused CI failures** using bounded
  repair workers such as Codex Cloud or Codex SDK (Codex is the worker adapter — not the
  institutional CI owner).
- **A CI Reliability Owner profile under NOOS** must handle flaky tests, workflow defects,
  runner failures, and CI infrastructure — not ordinary code fixes.
- **SourceA compiles the repair job, CI verifies it, SG governs authority, and the founder
  approves** any change to secrets, production permissions, deployment triggers, merging,
  or deployment.

## What NOOS operationalized in this PR (proposal, not activation)

| Artifact | Path | State |
|---|---|---|
| Canonical roles registry | `data/noos-canonical-roles-v1.json` | `PROPOSED_SG_REVIEW` |
| Operational binding | `noetfield-org/ISSUE_CI_OWNERSHIP_OPERATIONAL_BINDING_v1.md` | PROPOSED |
| CI-repair Motor recipe | `motor/registry/recipes/NF-MOTOR-CI-REPAIR-001.yaml` | validated, `NOT_WIRED` |
| Route binding | `motor/registry/bindings/noos-route-map-v1.json` → `ci_failure_candidate_repair` | `NOT_WIRED` (safe: classify + stop) |
| Recipe-count test | `motor/registry/tests/test_motor_registry_invariants.py` | `== 5` → `== 6` (inventory, not a weakening) |

`NOT_WIRED` is deliberate and safe: NOOS classifies and surfaces a candidate-caused CI
failure but no registered machine owner auto-executes the repair yet — correctly stopping
beats wrongly repairing. Wiring a machine owner is a later, separately-gated step.

## What SG must decide

1. Ratify the five canonical role IDs and the `issue-manager` / `ci-reliability-owner`
   capability-vs-agent framing (profile of `portfolio-owner`, not new residents).
2. Confirm the failure-class → owner routing table (§2 of the operational binding).
3. Confirm `NF-MOTOR-CI-REPAIR-001` authority split (machine may repair candidate; founder
   gates merge/deploy/secret/CI-config/authority changes).
4. Confirm promotion authority = `founder_or_explicit_sg_policy`.
5. Whether/when to WIRE the route (register a machine owner) — a later gate.

### Named SoD risk for SG (surfaced by adversarial verification)

Because `portfolio-owner` hosts **both** the Issue Manager (classifier + closure-evidence
confirmer) **and** the CI Reliability Owner (adjudicator for flaky / workflow-logic / infra
classes), for those **non-candidate** classes one identity classifies the fault domain,
adjudicates it, and confirms closure. This is the advisor's intended "capability/profile,
not a new agent" framing, and it is currently **inert** (everything PROPOSED / NOT_WIRED),
but it is a real separation-of-duties concentration. Both hats are already stripped of
merge / deploy / check-bypass / mark-success, and workflow edits touching permissions /
secrets / triggers stay founder-gated. **SG should explicitly bless (or split) this dual
hat, and — before any future WIRING of a CI-Reliability remediation path — require it to
carry the same external-verifier + founder-gate discipline that `NF-MOTOR-CI-REPAIR-001`
already carries for the candidate path.** No CI-Reliability executor/recipe is defined in
this PR (correctly: classify-and-stop, not auto-repair).

## Custody / gating

Recipes are L5 / founder-gated artifacts — the recipe diff **is** the policy review.
Role-map ratification is SG's. This addendum and the operationalization artifacts are
**SUBMITTED for independent verification**; they carry no PASS/DONE verdict of their own.

`LAWS: FOUNDER_CANON v1 + governed-autorun v3. Violations = BLOCKED_WITH_REASON.`
`canon_version: FOUNDER_CANON_v1+MACHINE_LOOPS_v1`
