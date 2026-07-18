# NOOS Software Repair Runway v1 — Execution Ledger

**Task:** NF-NOOS-SOFTWARE-REPAIR-RUNWAY-V1 · **Branch:** `nf-noos-software-repair-runway-v1`
(isolated worktree off the Motor foundation, commit `f52cd6b0`)
`canon_version: FOUNDER_CANON_v1+MACHINE_LOOPS_v1`

> Builder ledger. Every claim is **SUBMITTED for independent verification**
> (author ≠ subject). No self-issued PASS. Deterministic gates (pytest) + the
> receipts under `receipts/runway/` are the evidence.

## The correction being executed

The earlier `digest` executor was **Motor-foundation validation, not the finished
customer product.** The sellable product is **NOOS Software Repair Runway v1**: a
customer submits a failing repo/CI/test/defect; NOOS analyses, reproduces, plans,
repairs (model-proposed, test-verified), and returns a verified draft PR or patch
bundle + report + audit receipts. The Motor is internal infrastructure.

Two founder corrections accepted and applied:
1. **Provenance:** local-reference cycles were mislabelled `receipt_origin=organic`.
   Fixed — `organic` is now production-canonical only; a strict
   `production_running_confirmed()` gate requires organic + producer allowlist +
   canonical plane + real dispatch + lifecycle + terminal evidence + freshness.
2. **Remote paths:** "no local credentials" was incomplete. `gh` is authed
   (`repo`+`workflow`, admin) so sanctioned workflows/PRs/releases are usable.
   See [`software-repair-v1-cloud-route-discovery.json`](../../receipts/runway/software-repair-v1-cloud-route-discovery.json).

## Reality boundaries (honest)

| Capability | Status |
|---|---|
| `gh` dispatch workflows / draft PR / draft release | ✅ available (admin, `workflow` scope) |
| Supabase secrets in Actions | ✅ present → migration via a gated workflow |
| Model provider key | ❌ absent everywhere → adapter + secret-injection action; deterministic-local engine for offline proof |
| Railway/Fly token (canonical `http_loop` producer restart) | ❌ absent everywhere → PROTECTED/EXTERNAL |
| `production` environment | 🔒 protected → deployments wait for founder approval |

## Phases

| # | Phase | State |
|---|---|---|
| 1 | Accept + regression-test foundation (327 green) | ✅ |
| 2 | Provenance correction + production allowlist | ✅ committed `632d4e82` |
| 3 | Remote route discovery | ✅ receipt written |
| 4 | Authoritative persistence schema (migration + gated apply workflow) | in progress |
| 5 | Canonical producer restore (Railway-token-gated) | PROTECTED |
| 6 | Recipe registry `software_repair_ci_v1` | in progress |
| 7 | Software repair runner + 3 real fixture jobs | in progress |
| 8 | Model router (adapter + deterministic-local + secret-injection action) | in progress |
| 9 | Customer API/UI | in progress |
| 10 | Reliability + masking regression on repair pipeline | in progress |
| 11 | Durable release + product PR + pilot package | in progress |

## Material mutations log (append-only)

| UTC | Phase | Change |
|---|---|---|
| 2026-07-18T05:00Z | 1 | Isolated worktree; foundation regression 327 passed |
| 2026-07-18T05:20Z | 2 | Provenance correction committed `632d4e82` (12 gate tests) |
| 2026-07-18T05:25Z | 3 | Cloud-route discovery receipt (gh authed; Railway/model-key absent) |
