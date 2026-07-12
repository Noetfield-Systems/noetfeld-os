# AGENTS.md — noetfeld-os repo

<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-AGENTS-MD
doc_type: AGENT_ENTRYPOINT
workspace_root: /Users/sinakazemnezhad/Desktop/Noetfield-Systems/noetfeld-OS
-->

## L0 repo graph memory — broad-read gate

**Read before broad reads:** `graph-out/GRAPH_REPORT.md` · query: `python3 scripts/query_repo_graph_v1.py <term>` · design: `docs/L0_REPO_GRAPH_MEMORY_v1.md`

Do not spawn a broad "understand the repo", "map subsystem X", "architecture
review", or "audit Y" task (multi-agent or single-agent) by reading files
directly as the first step. First read `graph-out/GRAPH_REPORT.md` (compact
subsystem map) and, for anything it doesn't answer, run
`python3 scripts/query_repo_graph_v1.py <subsystem-or-keyword>` (bounded output,
no full file reads). Only open — or delegate reading of — the specific files the
graph names as relevant. Token budget: orientation (the report plus a few
targeted queries) should cost a few thousand tokens, not the hundreds of
thousands a blind multi-agent understand pass costs. If the graph is missing or
stale, rebuild first with `python3 scripts/build_repo_graph_v1.py` (zero-token)
rather than falling back to a blind read. Verify wiring:
`bash scripts/verify_l0_repo_graph_memory_v1.sh`.

## If you are a Claude Code agent in this repo

Root **`CLAUDE.md`** is the Claude Code activation surface (NOOS identity,
commit-pinned authority, runtime map, project rules, `noos-architect` /
`noos-integrator` agents under `.claude/`). It binds to this file — the two
surfaces must not contradict. Verify wiring:
`bash scripts/noos_claude_activation_doctor_v1.sh`.

## If you are a Cursor agent in **this repo** (`noetfeld-os`)

0. Read **`docs/_NOOS_AGENT/NOETFIELD_UNIFIED_MASTER_v1_LOCKED.md`** + **`NOETFIELD_OS_SSOT_v1_LOCKED.md`** + **`PRODUCT_TRUTH.md`**
0b. Commercial / NW1 tasks: also read **`[NOOS-AGENT-20260615-010]_BUSINESS_STRATEGY_PROOF_DENSITY_v1.md`**
0c. Build / upgrade tasks: read **`[NOOS-AGENT-20260615-014]_UPGRADE_PLAN_300_STEPS_v1.md`** + track in **`UPGRADE_MANIFEST.json`**
1. Read **`docs/_NOOS_AGENT/[NOOS-AGENT-20260608-005]_ORIENTATION_START_HERE.md`**
2. Search tagged docs: `grep -r "NOOS-AGENT-DOC" docs/_NOOS_AGENT/`
3. Check `docs/_NOOS_AGENT/MANIFEST.json` for trace IDs before editing any essay or internal note.

### Cursor Local Mac (T2)

- Open lane: `make local-lane TASK=<task-id> SCOPE=path1,path2`
- Session digest: `make local-status`
- Boot: `make local-boot` (optional receipt: `make local-boot WRITE_RECEIPT=1`)
- Operator card: **`docs/_NOOS_AGENT/[NOOS-AGENT-20260703-004]_CURSOR_LOCAL_MAC_OPERATOR_v1.md`**
- Subagent: `.cursor/agents/noetfield-os-local-operator.md`
- Claim before edit: `bash scripts/noos_local_claim_lane_v1.sh <task-id> <paths...>` (or `AGENT_ID=copilot-cli-mac IDE=copilot-cli`)
- Long session: `make local-heartbeat TASK=<task-id>`
- Stale claims: `make local-sweep-stale`
- Closeout: `make local-closeout TASK=<task-id>` (optional receipt: `WRITE_RECEIPT=1`)
- Cannot `git checkout main`? Run `bash scripts/noos_mac_worktree_sync_v1.sh`

### Scheduled jobs (zero-founder process)

- Canon: **`docs/_NOOS_AGENT/[NOOS-AGENT-20260703-005]_FOUNDER_CANON_INTERFACE_v1.md`**
- Loops: **`docs/_NOOS_AGENT/[NOOS-AGENT-20260703-006]_MACHINE_LOOPS_v1.md`**
- Status: `make machine-status` · reconcile: `make machine-reconcile` · audit: `make machine-audit`
- Merge gate: `make machine-validate-merge` · skill: `.cursor/skills/machine-loops/SKILL.md`
- **PR conflicts (MANDATORY LOCKED):** `.cursor/skills/pr-conflict-resolver/SKILL.md` · law: **`docs/_NOOS_AGENT/[NOOS-AGENT-20260708-001]_PR_CONFLICT_RESOLVER_MANDATORY_v1_LOCKED.md`** · verify: `make pr-conflict-verify` · eval app: `~/Desktop/PR-Conflict-Resolver-Report.app`
- Default: route failures to critic/repair/research — not founder

### Live sync / nerve gate

- Before claiming current Noetfield live state, run `bash scripts/check_noos_live_sync_gate.sh`. The wrapper refreshes the website live nerve first; do not rely on an old receipt unless you are explicitly doing read-only archaeology.
- The gate is scope-aware. Set `NOOS_LIVE_SYNC_SCOPE=runtime|public|studio|foundation|ecosystem|all` when the task has a narrow focus. Default scope is `ecosystem`.
- This NOOS receipt consumes the fresh website live nerve receipt, SourceA live surfaces, Noetfield GEL/API health, public website health, and Studio Supabase boundary existence.
- `DEGRADED` means the selected scope's required surfaces are usable but warnings remain; do not report "fully green" until warnings are repaired.

### Dirty-tree closeout

- Before committing or ending implementation work, run `bash scripts/check_noos_clean_tree.sh` after validators/tests pass.
- Do not commit routine run-patch execution churn from `docs/run_patches/execution/*`.
- Treat `docs/run_patches/noetfield_run_patch_manifest_10100_v1.json` runtime metadata churn as generated unless an explicit receipt snapshot is being closed.
- If `run_noetfield_factory_loop_v1.py` is active, stop and classify the writer before claiming the repo is clean.

### Integrator coordination

- Before starting overlapping implementation work, read the integrator summary: `python3 scripts/noos_integrator_sync_v1.py summary --json`
- Before parallel agent work, run conflict check: `python3 scripts/noos_agent_conflict_check_v1.py --json`
- Register/claim through `scripts/noos_integrator_sync_v1.py` before editing shared code paths across multiple IDE agents.
- Respect `scope_files` conflicts. If another non-stale agent owns the same files, do not proceed silently.
- Repo-local runtime state is primary; `~/.sina/noos-integrator-state-v1.json` is the cross-worktree/home mirror for other IDEs on the same Mac.

### SAVE / LOCK routing in this repo

- If ASF says `SAVE`, `SAVE AND LOCK`, `LOCK`, or `FILE` for Noetfield / Noetfield OS / noetfeld-os work, the file belongs in this repo, not SourceA.
- Agent-authored internal docs go under `docs/_NOOS_AGENT/` with a `NOOS-AGENT-DOC` block, `[NOOS-AGENT-YYYYMMDD-NNN]_` filename prefix, and a `MANIFEST.json` row.
- Product code changes stay in this repo's code paths. Do not save Noetfield implementation docs into `~/Desktop/Noetfield-Systems/SourceA/docs/` unless ASF explicitly names that SourceA path.

## If you are a **different** agent (mono, Noetfield Runtime, SourceA, TrustField)

- **Do not** edit `docs/_NOOS_AGENT/**` unless your task explicitly says merge from `NOOS-AGENT-DOC`.
- Use your own tag (`NFRT-AGENT-DOC`, etc.) in your own repo/lane.
- Ecosystem SSOT: `~/Desktop/Noetfield-Systems/SourceA/brain-os/law/SINA_OS_SSOT_LOCKED.md` (DESIGN plane).

## This repo's role

FastAPI governance decisioning prototype (DELIVERY lane). Isolated from SinaaiRuntime `:8000`.

## Noetfield OS repo policy

Noetfield OS is a separate operating/runtime system, not TrustField and not SourceA.

Allowed scope: GEL/runtime, gates, logs, TLE, control process, runtime docs, and operating-system-level governance mechanics.

Hard rules:

- Do not mix Noetfield OS with TrustField architecture, deploy, compliance, or messaging.
- Do not use SourceA as active storage.
- Do not import product-specific Noetfield or TrustField files unless explicitly documented as an interface.
- Noetfield OS may connect through contracts, exports, and manifests only.
- Work lane-by-lane only, max 20-40 files per pass, with one atomic commit per coherent lane.
- Generated/evidence outputs must be handled as snapshot plus manifest.

Before work:

- Run `git status --short`, confirm branch, and count dirty files.
- State the target lane.
- Classify dirty files as `COMMIT`, `RESTORE`, `DELETE`, `SNAPSHOT`, `QUARANTINE`, or `LEAVE`.
- Quarantine SourceA, Noetfield product, or TrustField product files found inside this repo unless they are explicit interface artifacts.

## Tagged internal references (this agent)

| trace_id | document |
|----------|----------|
| `NOETFIELD-UNIFIED-MASTER-V1` | **Unified Master — read first** |
| `NOETFIELD-OS-SSOT-V1` | **Product SSOT — build/GTM law** |
| `NOOS-AGENT-PRODUCT-TRUTH` | **Live product state** |
| `NOOS-AGENT-20260608-005` | ORIENTATION — session start |
| `NOOS-AGENT-20260615-006` | **90-day execution plan (active)** |
| `NOOS-AGENT-20260529-002` | Business, product & client definition |
| `NOOS-AGENT-20260615-007` | Glossary, plane tags & anti-ICP |
| `NOOS-AGENT-20260608-003` | Ten market success models |
| `NOOS-AGENT-20260529-001` | Governance drift essay |
| `NOOS-AGENT-20260608-004` | 1000-step roadmap |
| `NOOS-AGENT-20260615-008` | noetfield.com/gel URL structure (draft) |
| `NOOS-AGENT-20260615-009` | Pitch & PDF alignment notes |
| `NOOS-AGENT-20260615-010` | **Business strategy — proof density & NW1/SW1 motion** |
| `NOOS-AGENT-20260615-011` | **Founding pilot one-pager — NW1 Copilot attach** |
| `NOOS-AGENT-20260615-013` | **Founding pilot one-pager — SW1 agents attach** |
| `NOOS-AGENT-20260615-012` | **Chain tools — `noetfield gate` / `noetfield decide`** |
| `NOOS-AGENT-20260615-014` | **300-step upgrade plan — UPG-0001–0300** |
| `NOOS-AGENT-20260703-001` | **Integrator agent protocol — local cross-IDE task sync** |
