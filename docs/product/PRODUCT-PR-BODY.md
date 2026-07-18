# NOOS Software Repair Runway v1 — Managed Pilot RC (DRAFT, do not merge)

Base `main` · Head `nf-noos-software-repair-runway-v1`. **Draft.** No auto-merge/deploy.

## Architecture
Customer commission → recipe `software_repair_ci_v1` → isolated worktree →
reproduce → classify → plan (**GitHub Models** via `GITHUB_TOKEN`/`models:read`, no
new secret; deterministic fallback) → bounded test-verified patch → draft PR or
patch bundle → audit receipt. Motor FSM (idempotency/lease/retry/dead-letter/replay)
is internal.

## Product-specific canonical producer (§2)
`github_actions_software_repair_v1` on plane `github_actions`. `receipt_origin=organic`
requires **all 15 conditions** incl. an authoritative Supabase commission+job — the
GitHub event name alone is never provenance (`product_organic_confirmed`).

## Separation from Railway platform health (§1)
Three independent health domains: **A** platform_loop (Railway `http_loop`, may stay
degraded — separate incident), **B** product (this chain), **C** customer_job.
Railway is **not** a release gate for Software Repair.

## Migration 0021
Additive; **NOT applied** (production Supabase). `production` env is currently
*unprotected*, so the machine did not auto-apply — this is a deliberate founder step.

## GitHub Models permission
Trusted planning job uses `permissions: { contents: read, models: read }` + `GITHUB_TOKEN`.

## Trust-zone security (§5)
intake+plan (read+models) / execute+verify (`permissions: {}`, no token) / finalize
(pr:write only). Pilot repos restricted to NOOS-owned/allowlisted.

## Repository scope
Python(pytest) verified model-primary; Node(node:test) available, acceptance pending.

## Tests
Full worktree suite **358 passed** (health, provenance, repair pipeline, motor invariants).

## Three acceptance jobs
2 **model-primary** repairs via GitHub Models verified (gpt-4o-mini; A: off-by-one, B: data-handling; each exit 1→0). Job C (non-fixture, deployed-chain organic) pending Supabase persistence.

## Rollback
Delete branch; migration 0021 reversible (DROP block).

## Deployment steps + exact founder approvals
1. Apply migration 0021 to production Supabase (authoritative persistence) — the single foundational unlock for organic product cycles.
2. Register `software-repair-run-v1.yml` (`data/noos-parallel-agent-registry-v1.json`, L5) + move to `.github/workflows/`, merge.
3. Deploy the Gateway customer surface (Cloudflare/Flask).

SUBMITTED for independent verification. canon_version: FOUNDER_CANON_v1+MACHINE_LOOPS_v1

🤖 Generated with [Claude Code](https://claude.com/claude-code)
