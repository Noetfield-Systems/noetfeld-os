# Motor Registry v1.2

The recipe schema, job-record schema, first five recipes, and the invariant
validator for the Noetfield Motor. Everything here validates fail-closed:
`python3 motor/registry/validate.py`.

> **Maturity (honest):** this is the Motor's *machine-readable contract*, not
> the Motor *runtime*. There is no `Motor.run(recipe_id, inputs)` here yet — the
> registry declares what a future executor must enforce (sandbox provisioning,
> network allowlists, scoped credentials, budgets, transitions, promotion,
> outcome probe). Today those declarations are governed by validation, not by
> runtime containment. Do not call this a live executor.

## Layout

```
schema/recipe.schema.json   what every recipe must declare
schema/job.schema.json      one execution of a recipe = its receipt (v1.1)
recipes/*.yaml              the five recipes
jobs/MOTOR-WEB-001.json     Motor Proof Job #1, honest state (TRIAGE_REQUIRED)
validate.py                 v1.2 fail-closed invariant validator (exit 0/1)
tests/                      negative-transition tests — every invariant fails closed
```

## The design decision that matters

The job record's `states` object holds **seven separated truth fields** —
dispatch, execution, verification, evidence, authority, promotion, outcome
(plus optional recovery) — each with its own evidence pointer. No field may be
inferred from another. This is the schema-level encoding of the stale-loops
lesson: "no recent completion evidence" (evidence: STALE) and "the loop failed"
(execution: FAILED) are different facts, and the old cockpit's bug was
collapsing them. `UNPROVEN` / `STALE` / `DIVERGED` are distinct states that can
never become `FAILED`.

## What v1.1 → v1.2 hardened (vs the v1.0 draft)

v1.0 validated structure and enforced exactly one cross-field rule. The other
documented invariants were **prose, not executable constraints** — the
validator accepted `PROVEN` without evidence, `BLOCKED` without reason, invalid
datetimes, `RECEIPT_COMPLETE` over an unstarted promotion, and version
mismatches. v1.1 made each a hard failure. **v1.2** then closed the fail-closed
gaps an adversarial red-team found in v1.1 (all now carry regression tests):

- whitespace / zero-width `evidence_ref`/`reason` bypassed `minLength:1` → now
  rejected as blank (unicode + zero-width stripped);
- the promotion/outcome splits were skippable by **omitting** the sub-objects →
  on external recipes the split is now **required**, not optional;
- `states.evidence` was never checked at `RECEIPT_COMPLETE` → now must be PROVEN;
- a trailing newline slipped past the date-time format check and a lowercase
  `z` silently defeated timestamp ordering → strict date-time checker + `z`
  handling;
- a 41-char `production_sha` passed the `$`-anchored regex → `fullmatch`;
- plus recipe-side semantics, budget/trigger cross-checks, hash-format, and
  job-id/idempotency uniqueness.

Every invariant is proven by `tests/` (46 tests: negative-transition per
invariant + two rounds of adversarial red-team regressions + a positive
mirror). The validator was hardened across two adversarial red-team rounds:
round 1 found whitespace/zero-width and split-omission bypasses; round 2 found
the invisible-Unicode (Cf/Mn) class, non-adjacent timestamp ordering, and
date-only strings. `_meaningful` uses a category rule (require a visible
letter/number), not a denylist, so the whole invisible-character class is
closed — not an enumerated few:

| # | Invariant | Enforced by |
|---|---|---|
| I1 | `PROVEN`/`FAILED` require `evidence_ref` | schema (`if/then`) |
| I2 | `BLOCKED`/`FAILED`/`DIVERGED`/`UNPROVEN` require `reason` | schema (`if/then`) |
| I3 | every date-time is RFC3339 | schema + `FormatChecker` |
| R1 | job `recipe_id` exists | validate.py |
| I4 | job `recipe_version` == recipe `version` | validate.py |
| R2 | `outcome PROVEN` ⇒ `promotion PROVEN` | validate.py |
| I5a | `promotion PROVEN` ⇒ source PROVEN **and** runtime PROVEN/NA | validate.py |
| I5b | `outcome PROVEN` ⇒ observation PROVEN **and** attribution PROVEN | validate.py |
| I6 | external-proof recipe ⇒ ≥1 external check; `outcome PROVEN` needs a PASS external result | validate.py |
| I7 | `production_sha` set ⇔ runtime PROVEN, 40-hex; `candidate_sha` when execution PROVEN | validate.py |
| I8 | timestamp ordering; outcome ≥ 60s after promotion for external recipes | validate.py |
| I9 | `RECEIPT_COMPLETE` needs all truth fields terminal-proven, `cost.metered`, `receipt_hash`, and every recipe `receipt.required_fields` non-null | validate.py |

### Two schema splits the real website job forced

- **`promotion` → `source` + `runtime`.** "Merged to main" and "deployed to
  production" are different truths. A job can have `source: PROVEN` and
  `runtime: DIVERGED`.
- **`outcome` → `observation` + `attribution`.** Seeing new content on the live
  site is not proof that *this candidate SHA* produced it. The loop closes only
  when `attribution` is PROVEN (deployed SHA == candidate SHA).

## The five recipes

| Recipe | Kind | Founder gate |
|---|---|---|
| WEB-PUBLISH-001 | operational | merge + deploy |
| SOFTWARE-CHANGE-001 | operational | merge + deploy |
| INCIDENT-DIAGNOSE-001 (v1.1) | witness/control | none — cannot mutate the observed system |
| RECEIPT-WRITER-REPAIR-001 (v1.1) | machine-safe repair | writer-fix PR merge; **restart/redeploy explicitly founder-only** |
| DEPENDENCY-UPDATE-001 | scheduled autorun | merge; majors triaged |

**`mutation_policy`** (new in the two v1.1 recipes) resolves the "read-only
recipe that still writes a diagnosis receipt" contradiction: it declares
per-surface authority (`observed_system: deny`, `control_plane_receipts:
append_only`, `routing_queue: create_only`, …). "Read-only" now precisely means
read-only *with respect to the observed/production system*, never literally zero
writes — and RECEIPT-WRITER-REPAIR's `evidence_sink: full` coexists with
`production_write: false` without ambiguity.

## MOTOR-WEB-001 — honest state

`TRIAGE_REQUIRED`, not `AWAITING_AUTHORITY`. Build + CI are PROVEN; render
review, source merge, runtime deploy, and live outcome are UNPROVEN/DIVERGED.
`cost.metered=false` and the `T00:00:00Z` timestamps are flagged placeholders —
the v1.2 validator blocks `RECEIPT_COMPLETE` while `metered=false`. See the
record's `notes` for the exact close-out chain.

## Next wiring (out of scope for this PR)

- **Track D — NOOS route → recipe binding.** The NOOS route
  `receipt_writer_completion_evidence_repair` (from the observability-semantics
  change) should bind to `NF-MOTOR-RECEIPT-WRITER-REPAIR-001` with a registered
  machine owner. Until then, NOOS classifies correctly but does not auto-repair
  — which is the safe failure mode (correctly stopping beats wrongly
  restarting).
- **Unified `Motor.run(recipe_id, inputs)` executor** that turns these
  declarations into runtime containment (mounts, egress policy, scoped
  credentials, budget cutoffs).

## Adopting it

New job types start as a recipe PR against `recipe.schema.json` — founder review
of the recipe diff IS the policy review (recipes are L5 territory). CI runs
`validate.py` + `tests/` on any change under `motor/registry/`.
