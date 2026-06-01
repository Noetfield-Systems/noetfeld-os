# Agent tracking (Noetfield)

**Read this first** for task priority. Do not create `todolist/` at the repository root.

## Where work lives

| Priority | Location | When |
|----------|----------|------|
| 1 | **`ops/private/todolist/`** | Present on founder machine (gitignored — **never commit**) |
| 2 | **GitHub Issues** | Always (especially cloud agents / fresh clones) |
| 3 | **[docs/ROADMAP.md](../docs/ROADMAP.md)** | Public horizons only — no P0 secrets |

## If `ops/private/` exists (local workspace)

Read in order:

1. `ops/private/todolist/NEXT_MOVES.md` — P0/P1/P2
2. `ops/private/todolist/noetfield-platform.md` — platform `NF-ENG-*`
3. `ops/private/todolist/noetfield-public-site.md` — www `NF-WWW-*`
4. `ops/private/docs/GO_LIVE_CHECKLIST.md` — founder deploy steps
5. `ops/private/docs/LEGAL_REVIEW_CHECKLIST.md` — legal sign-off

**Do not** copy TrustField or VIRLUX items from `ops/private/todolist/external/` into Noetfield code.

**Sina MonoRepo SSOT (internal, gitignored):** Desktop `SourceA/SINA_OS_SSOT_LOCKED.md` and `PHASE1_UNIFIED_BLUEPRINT_v2_3.md` are **read-only for agents** — ASF edits on Mac only. After bootstrap, agents may read a local mirror under `ops/private/sourceA/` (founder sync) plus `NOETFIELD_REPO_ALIGNMENT.md`. Never commit `ops/private/`. Never modify Desktop SourceA files.

## If `ops/private/` is missing (cloud agent)

1. Use **GitHub Issues** — labels: `launch`, `legal`, `engineering`, `NF-P0`
2. Use issue templates under `.github/ISSUE_TEMPLATE/`
3. Use [docs/strategy/noetfield-future-path.md](../docs/strategy/noetfield-future-path.md) for strategy
4. Do **not** recreate private markdown in the public tree

Seed locally: `./scripts/bootstrap-private-ops.sh` · MSB pack: `./scripts/seed-msb-partner-pack.sh`

**MSB partner channel:** [docs/strategy/msb-partner-playbook.md](../docs/strategy/msb-partner-playbook.md) · deploy [docs/MSB_DEPLOY_AND_PILOT.md](../docs/MSB_DEPLOY_AND_PILOT.md)

## Internal doctrine (agents with `ops/private/` only)

**Not in git.** Read only if present after founder bootstrap:

- `ops/private/sourceA/AUTO_CONFLICT_ENGINE_V3_LOCKED.md` (mirror)
- Desktop canonical: `~/Desktop/SourceA/AUTO_CONFLICT_ENGINE_V3_LOCKED.md`

Do not copy this doctrine into `docs/`, www, or commits. Cross-plane notes use `[DESIGN]` `[EXECUTION]` `[DELIVERY]` when relevant.

## Scope

[PROJECT_BOUNDARIES_LOCKED.md](../PROJECT_BOUNDARIES_LOCKED.md) — **Noetfield only** in this repo.
