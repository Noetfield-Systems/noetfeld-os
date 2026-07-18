# NOOS Software Repair Runway v1 — Managed Pilot RC (DRAFT — do not merge)

Base `main` · Head `nf-noos-software-repair-runway-v1` @ `75f042ce`. **Draft.**
No auto-merge, no customer-code deploy. This is the complete integrated product PR
that gives the whole Software Repair product an independent GEL CI run on `main`.

## Product promise
A customer submits a failing repository / CI / test / reproducible defect; NOOS
reproduces it, plans a repair (model-generated), executes in isolation, verifies
with real tests, and returns a **test-verified** draft PR or patch bundle + audit
receipt. Human approval before merge; NOOS never auto-merges or deploys customer code.

## Customer input / output
- **In:** authorized repo (NOOS-owned / allowlisted), reproducible failure, target branch, constraints.
- **Out:** diagnosis, bounded repair attempt, verified patch, passing-test evidence, draft PR or patch bundle, audit receipt.

## Architecture
commission → recipe `software_repair_ci_v1` → isolated worktree → reproduce →
classify → plan (**GitHub Models** via `GITHUB_TOKEN`+`models:read`, no new secret;
deterministic fallback) → bounded verified patch → draft PR/patch bundle → receipt.
Motor FSM (idempotency/lease/retry/dead-letter/replay) is internal.

## Exact branch and commit
`nf-noos-software-repair-runway-v1` @ `75f042cece20…` (merge-base `291789bc`).

## Relation to the review-slice PRs
- **PR #85** (foundation → main): the Motor foundation; **contained** in this branch's history.
- **PR #86** (provenance classifier correction → main): its classifier behavior is present here (this branch predates the §1-§6 live-projection refinements on #86 — see reconciliation receipt; no divergent classifier is merged).
- **PR #84** (repair demo → this product branch): a real draft repair PR; stays as demo evidence.

## Migration 0021
`infrastructure/supabase/migrations/0021_software_repair_runway.sql` — additive,
**NOT applied** (production Supabase). Reversible (DROP block).

## Product-specific GitHub Actions producer
`github_actions_software_repair_v1` on plane `github_actions`. `receipt_origin=organic`
requires all 16 conditions incl. an authoritative Supabase commission+job
(`noos_software_repair_health_v1.product_organic_confirmed`); GitHub event name alone is never provenance.

## Model-provider design
Provider-neutral router; `github_models` default (endpoint `models.github.ai`,
`GITHUB_TOKEN`+`models:read`), records model/hashes/tokens/latency/cost/schema-valid;
deterministic-local fallback. Verified: 2 real model-primary repairs (`gpt-4o-mini`).

## Trust-zone security
intake+plan (`contents:read`+`models:read`) / execute+verify (`permissions: {}`, no token) /
finalize (`pull-requests:write` only). `docs/product/proposed-workflows/software-repair-run-v1.yml`.

## Supported pilot repositories
NOOS-owned / explicitly allowlisted only. No arbitrary-public-repo claim.

## Local test evidence
Full worktree suite **358 passed** (health, provenance, repair pipeline, motor invariants, reliability).

## Known activation steps (founder-owned)
1. Apply migration 0021 to production Supabase (authoritative persistence).
2. Register `software-repair-run-v1.yml` (L5 registry) + merge; deploy the Gateway surface.

## Rollback
Delete branch; migration 0021 reversible.

## Platform-health separation
Railway `http_loop` platform health is **separate** and is **not** a Software Repair
product release gate (`noos_software_repair_health_v1` — 3 independent domains).

SUBMITTED for independent verification. canon_version: FOUNDER_CANON_v1+MACHINE_LOOPS_v1

🤖 Generated with [Claude Code](https://claude.com/claude-code)
