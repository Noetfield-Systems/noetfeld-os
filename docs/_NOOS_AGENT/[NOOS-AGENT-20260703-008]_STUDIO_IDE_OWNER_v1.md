<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260703-008
doc_type: STUDIO_IDE_OWNER
workspace_root: /Users/sinakazemnezhad/Projects/noetfeld-os
classification: INTERNAL — Studio IDE Owner charter v1
-->

# Noetfield Studio IDE Owner v1

**Status:** LOCKED charter · **Owner lane:** Studio product · **Executor:** T2 local  
**Date:** 2026-07-04  
**Canonical repo:** `~/Desktop/Noetfield/noetfield-studio-ide/`  
**NOOS observe-only repo:** `~/Projects/noetfeld-os/` (boundary, sync, kernel plans — not Studio code)

---

## Mandate

Build the full **local-first, cheap-worker, model-agnostic Agentic IDE** using NOOS kernel/sandbox doctrine as handoff input — not as host runtime.

Studio IDE Owner v1 owns:

1. Product implementation in `noetfield-studio-ide` (UI, routing, providers, sandbox, receipts local)
2. Local worker runtime (Node/Playwright/Vitest on Mac — free/cheap compute)
3. Model-agnostic provider layer (Gemini today; extensible store)
4. Boundary compliance (`npm run boundary:check`, Supabase split)
5. Evidence spine (unit, E2E, local receipts) closing PATCH-046/048/049/050
6. **v1 master build plan** (required before website nerve `N11_STUDIO_BOUNDARY` wiring)

---

## Do not

| Rule | Reason |
|------|--------|
| Absorb Studio into `noetfeld-os` | Locked architecture; `repo-policy.json` quarantines `noetfield-studio-ide/**` |
| Make GitHub the worker runtime | GitHub is mirror/storage only |
| Depend on Cursor | Target is standalone local Agentic IDE |
| Start public launch | Founder gate; internal workbench only |
| Change founder gate | NOOS observes; Owner does not override L5/founder locks |
| Delete duplicate clone yet | `~/Desktop/Noetfield-Systems/noetfield-studio-ide/` may hold unique experiments |
| Wire `N11_STUDIO_BOUNDARY` on website nerve | **Held** until this Owner ships v1 master build plan |

---

## Architecture (locked)

```
Founder Mac (local-first)
  └── noetfield-studio-ide/     ← Studio IDE Owner v1 (product truth)
  └── noetfeld-os/              ← NOOS (boundary, live sync, kernel handoff, tool broker)
  └── Noetfield/ www repo       ← public surfaces (N11 held)

GitHub (Noetfield-Systems/*)    ← mirror/storage only — not execution
```

**NOOS live sync:** `NOOS_LIVE_SYNC_SCOPE=studio` → `STUDIO_SUPABASE_BOUNDARY` (currently **ok: true**).  
**Handoff docs:** `NOOS-AGENT-20260627-016`, `NOOS-AGENT-20260628-019`, `NOOS-AGENT-20260703-007` (tool broker for cheap-worker wall).

---

## Current-state reconciliation (2026-07-04)

| Area | State | Evidence |
|------|-------|----------|
| Move off SourceA | **Done** | Separate repo, port 3005, `AGENTS.md` |
| Private GitHub mirror | **Done** | Org: `Noetfield-Systems/noetfield-studio-ide`; founder mirror on canonical `origin` |
| Supabase boundary | **Done** | `6cd42c9`, `boundary:check` PASS, NOOS live sync ok |
| Gemini provider parity | **Done** | `252808a`, cloud plan Phase 8 |
| PNG/SVG export | **Done** | `f668cee`, `visual-export*.ts` |
| Workspace map | **Done** | `NOETFIELD_OS_WORKSPACE.md` updated 2026-07-04 |
| PATCH manifest 041–050 | **Reconciled** | 6 done · 3 partial · 1 pending (see table) |
| Duplicate clone | **Drift risk** | Diverged after `f668cee`; unique sandbox-kernel + gate CI staged |
| Public launch | **Blocked** | Founder gate |
| N11 website nerve | **Held** | Awaits v1 master build plan |
| Cheap-worker kernel in Studio | **Not in canonical** | Experiments only on duplicate clone |

---

## Drift list

### Canonical clone (product truth)

- **Path:** `~/Desktop/Noetfield/noetfield-studio-ide/`
- **HEAD:** `6cd42c9` — Supabase boundary enforced
- **Remote:** `kazemnezhadsina144-dot/noetfield-studio-ide` (founder mirror; ahead 2)
- **Unique since shared `f668cee`:** boundary module, SQL policy, `boundary:check`, `AGENTS.md`, boundary architecture doc

### Duplicate clone (drift risk — do not delete)

- **Path:** `~/Desktop/Noetfield-Systems/noetfield-studio-ide/`
- **HEAD:** `f95a6ca` — L5/kernel_meta sandbox revert/reapply cycle
- **Remote:** `Noetfield-Systems/noetfield-studio-ide` (org mirror)
- **Missing from canonical:** Supabase boundary commits (`96bff32`, `6cd42c9`)
- **Unique tracked work (since `f668cee`):**
  - `.noetfield/skills/noos-multi-sandbox-kernel/`
  - `.noetfield/skills/agentic-sandbox-orchestration/`
  - `.noetfield/agents/coding-agent/`
  - `src/lib/agent-registry-server.ts`, agent toolbar/selector components
  - `scripts/create-agent.mjs`, `docs/CREATE_AGENT_WORKFLOW.md`
- **Unique staged (uncommitted):**
  - `.agent-policy/command_allowlist.json`
  - `.githooks/pre-commit`, `.githooks/commit-msg`
  - `.github/workflows/gate-build.yml`
  - `scripts/gates/check-gates.sh`, `scripts/install-githooks.sh`

**Owner action (next lane, not this pass):** Cherry-pick or re-implement valuable duplicate experiments into canonical; then archive duplicate with receipt.

### URL reference drift (resolved this pass)

| Surface | Before | After |
|---------|--------|-------|
| `REPO_REGISTRY.md` | Org URL only | Org URL + canonical local path + duplicate warning |
| `NOETFIELD_OS_WORKSPACE.md` | `kazemnezhadsina144-dot/*` | `Noetfield-Systems/*` as org mirror; founder mirror noted for Studio |
| Studio `README.md` | Still lists founder mirror only | Owner should align on next Studio doc pass |

---

## PATCH-041–050 status table

Reconciled against `NOOS-AGENT-20260626-015` execution receipt + canonical repo HEAD.

| Patch | Focus | Status | Receipt / evidence |
|-------|-------|--------|-------------------|
| PATCH-041 | Desktop launch + port 3005 guard | **done** | Phase 2B; `port.lock.json`, README, workspace map |
| PATCH-042 | Provider store Gemini parity | **done** | Phase 8; commit `252808a` |
| PATCH-043 | Studio Supabase boundary module | **done** | `NOOS-AGENT-20260627-016`; `96bff32`/`6cd42c9`; live sync ok |
| PATCH-044 | PNG export proof path | **done** | Phase 8; `f668cee` |
| PATCH-045 | SVG export proof path | **done** | Phase 8; `f668cee` |
| PATCH-046 | Admin settings persistence | **partial** | `studio-store.ts` + admin panel exist; patch receipt not filed |
| PATCH-047 | Workspace map handoff | **done** | Phase 2B step 2.13; map updated 2026-07-04 |
| PATCH-048 | Studio unit test evidence | **partial** | 96 passed 2026-06-26; needs fresh 2026-07 receipt |
| PATCH-049 | Studio E2E evidence | **partial** | 33 passed 2026-06-26; needs fresh 2026-07 receipt |
| PATCH-050 | Local receipt hygiene | **pending** | Owner defines receipt spine in v1 build plan |

Manifest updated: `docs/run_patches/noetfield_run_patch_manifest_10100_v1.json`

---

## v1 master build plan outline

Studio IDE Owner v1 must produce this plan before `N11_STUDIO_BOUNDARY` wiring or duplicate-clone deletion.

### Phase 0 — Read chain (mandatory)

1. This charter (`NOOS-AGENT-20260703-008`)
2. `NOOS-AGENT-20260627-016` (Supabase boundary)
3. `NOOS-AGENT-20260703-007` (tool broker — cheap-worker wall)
4. `noetfield-studio-ide/docs/HANDOFF_NEW_AGENT_CHAT_LOCKED_v1.md`
5. `noetfield-studio-ide/docs/roadmap/UPGRADE_BACKLOG.md`

### Phase 1 — Close partial patches

- PATCH-046: admin persistence proof + regression test receipt
- PATCH-048/049: run `npm run test:all` on canonical; file dated receipt under `.noetfield/receipts/`
- PATCH-050: define local receipt schema (build, test, boundary, provider probe)

### Phase 2 — Cheap-worker runtime (local-first)

- Model-agnostic provider router (extend beyond Gemini)
- Local sandbox executor (file tree, gate-before-write, diff preview — P0 backlog)
- NOOS tool-broker handoff for allowlisted shell (read plans from `noetfeld-os`; execute in Studio sandbox)
- No Cursor dependency; no GitHub Actions as runtime

### Phase 3 — Sandbox doctrine merge

- Evaluate duplicate-clone experiments (`noos-multi-sandbox-kernel`, agent registry, gate CI)
- Port only what fits local-first doctrine into canonical
- Reject GitHub-as-runtime patterns

### Phase 4 — Agentic IDE v1 feature set

- 3-pane UI hardening (explorer · editor · agent)
- Intent routing tests (inform / execute / edit)
- Verification gate before file commits
- Visual export receipts (PNG/SVG) in normal workflow
- Admin diagnostics without leaking secrets

### Phase 5 — Evidence + hygiene

- Unit + E2E green on canonical HEAD
- `boundary:check` in CI script locally (not GitHub worker runtime)
- Receipt index manifest in Studio repo
- Push mirror to `Noetfield-Systems/noetfield-studio-ide` (storage sync only)

### Phase 6 — NOOS handback (unblocks N11)

- Deliver v1 master build plan receipt to NOOS agent vault
- NOOS may then wire website nerve `N11_STUDIO_BOUNDARY` (read-only boundary status surface)
- Still no public launch without founder gate

---

## Stop condition (this pass)

This document completes the requested reconciliation lane. No duplicate deletion, no N11 wiring, no Studio code edits, no public launch.

**Next owner session starts at:** Phase 1 of v1 master build plan (partial patch close + fresh test receipt).

**Locked by:** noetfeld-os-cursor-chat · 2026-07-04
