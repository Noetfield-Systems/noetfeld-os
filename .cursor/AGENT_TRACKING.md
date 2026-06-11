# Agent tracking (Noetfield)

**Read this first** for task priority. Do not create `todolist/` at the repository root.

**Every session (before edits):** `make agent-session-start` — loads `SESSION_CLOSEOUT_LATEST.md` + mandatory read chain (`noetfield_cloud`).

**After verify PASS:** `make ship-closeout` (or `make ingest-cursor-reply` then `make sync-sourceA`).

**Session end:** `make agent-session-close` — writes disk closeout for `noetfield_cloud`.

**Read order (cloud vs local):** [docs/ops/AGENT_READ_LINKS_LOCKED_v1.md](../docs/ops/AGENT_READ_LINKS_LOCKED_v1.md) § Cloud ship vs § Local documents — cloud uses this repo + `ready_to_paste_noetfield_cloud.txt`; local uses All-Documents lane.

**Chat ≠ disk:** append [docs/ops/REPO_TRUTH_CORRECTIONS_LOCKED_v1.md](../docs/ops/REPO_TRUTH_CORRECTIONS_LOCKED_v1.md) when claims disagree with validators.

## Self-audit loop (mandatory)

1. [docs/ops/AGENT_SELF_AUDIT_LOOP_LOCKED_v1.md](../docs/ops/AGENT_SELF_AUDIT_LOOP_LOCKED_v1.md)
2. [.cursor/agent-memory/MEMORY_LOCKED.yaml](agent-memory/MEMORY_LOCKED.yaml) — **session memory**
3. [.cursor/incidents/REGISTRY.md](incidents/REGISTRY.md) — **incident reports**
4. [.cursor/skills/](skills/) — scope gate, pre-commit, session report, incident filing
5. `./scripts/verify-agent-scope.sh` — run before every commit
6. [docs/ops/AGENT_DOC_TAGGING_LOCKED_v1.md](../docs/ops/AGENT_DOC_TAGGING_LOCKED_v1.md) — **tag + date on every agent doc**

**Law:** Noetfield only. **Never** TrustField / trustfield.ca / VIRLUX. See [INCIDENT-2026-06-06-001](incidents/INCIDENT-2026-06-06-001-trustfield-scope-bleed.md).

**Noetfield cloud (`noetfield_cloud`):** [docs/ops/AGENT_READ_LINKS_LOCKED_v1.md](../docs/ops/AGENT_READ_LINKS_LOCKED_v1.md) (§ Cloud ship) · [docs/ops/NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md](../docs/ops/NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md) · paste: [docs/ops/ready_to_paste_noetfield_cloud.txt](../docs/ops/ready_to_paste_noetfield_cloud.txt). Canonical index: Desktop `SourceA/founder/repo-agent-notices/AGENT_READ_LINKS_INDEX.md` — never repo → SourceA.

## Ship rule (ASF) — two different things

| What it is | Blocks shipping? |
|------------|------------------|
| **Ingest** — send your answer to the system (YAML + Prompt OS inbox / ingest scripts) | **No** — required **after** you ship |
| **Waiting for the next order** — pause until Prompt OS / M8 sends the next prompt | **Yes** — do **not** do this |

- **Ship from:** [os/plan.json](../os/plan.json) · [os/SHIP_NOW.md](../os/SHIP_NOW.md) — execute `next_tasks` and sprint backlog **without waiting** for the next chat order.
- **Ingest:** every completed session → system ([docs/spec/EXECUTION_TRUTH_AGENT_REPLY_LOCKED.md](../docs/spec/EXECUTION_TRUTH_AGENT_REPLY_LOCKED.md)).
- **Do not edit** Sina Prompt OS code. **Do not weaken** Prompt OS — it coordinates; Noetfield repo delivers.

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

## Confidential [AUTO] (gitignored — never quote publicly)

**Path:** `docs/internal/AUTO_CONFIDENTIAL_PORTFOLIO_POSITIONING.md`  
**Index:** `ops/private/agent-reference/AUTO_INDEX_LOCKED.md` (AUTO-002) when `ops/private/` on disk.

- **Read** when present on founder machine — internal portfolio/entity positioning only.
- **Never** commit, PR, www, Issues, buyer packs, or paste into public agent replies.
- Public surfaces: `PRODUCT_TRUTH.md` · `OFFERINGS_LOCKED.md` · `POSITIONING.md` only.

## Scope

[PROJECT_BOUNDARIES_LOCKED.md](../PROJECT_BOUNDARIES_LOCKED.md) — **Noetfield only** in this repo.
