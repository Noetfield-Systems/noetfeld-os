<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260629-022
doc_type: SYSTEM_FIX_AND_UPGRADE_100_PLAN
workspace_root: /Users/sinakazemnezhad/Desktop/Noetfield-Systems/noetfeld-OS
classification: INTERNAL - system repair and upgrade register
authority: PRODUCT_TRUTH.md, NOOS-AGENT-20260629-021, NOOS live sync gate, SourceA nerve receipts
-->

# System Fix + Upgrade 100 Plan - v1

**Status:** LOCKED FOR DECISION  
**Created:** 2026-06-29  
**Scope:** NOOS, website/platform sync, SourceA nerve dependency, Studio boundary, validators, stale docs, generated receipt policy  
**Trace:** `NOOS-AGENT-20260629-022`

---

## Current Diagnosis

The system is usable but not fully green. NOOS, GEL runtime, website live nerve, platform health, and Studio boundary are OK. The live sync gate remains `DEGRADED` because:

1. SourceA session gate is not green (`mirror_poison_validate`, `entry_gate_worker`).
2. Website meaning is inconsistent: homepage is titled "Noetfield Intelligence", but `/intelligence/` is 404.
3. Studio has local Cmd+Z experiment files outside the committed boundary work.
4. Generated run-patch receipts can dirty the NOOS repo if a runner writes state.
5. PyPI/npm and chatbot phases 3-10 remain product gaps, not leaks.

This plan converts those observations into 100 decision-ready fixes. `Agent` means the agent can execute if no new product choice is needed. `Founder` means ASF must decide direction. `Owning repo` means work belongs outside `noetfeld-os`.

---

## Phase 1 - Clean Truth + Dirty Tree Discipline (001-010)

| ID | Plan | Owner | Verify |
|---|---|---|---|
| 001 | Make `git status -sb` clean at start and end of every NOOS implementation turn. | Agent | `git status -sb` |
| 002 | Add a no-generated-churn rule for `docs/run_patches/execution/*` unless closing an approved run. | Agent | Review `.gitignore` or receipt policy |
| 003 | Split immutable run-pack manifest data from mutable `latest_trigger_run` state. | Agent | JSON schema check |
| 004 | Add `scripts/check_noos_clean_tree.sh` for clean tree + no writer process checks. | Agent | Script exit 0 |
| 005 | Gate commits on `git diff --check`, NOOS doc tags, tests, and clean generated receipts. | Agent | Combined check script |
| 006 | Record "generated receipt snapshot policy" in run-patch control doc. | Founder | Doc decision row |
| 007 | Decide whether generated execution receipts are stored in git or external archive only. | Founder | Updated policy |
| 008 | Add warning if `run_noetfield_factory_loop_v1.py` is active during commit prep. | Agent | Script detects process |
| 009 | Add "dirty-tree closeout" section to `AGENTS.md`. | Agent | Manual review |
| 010 | Add a repo cleanup checklist to `PRODUCT_TRUTH.md` only when workflow changes materially. | Agent | Doc tag check |

## Phase 2 - NOOS Live Sync Gate Hardening (011-020)

| ID | Plan | Owner | Verify |
|---|---|---|---|
| 011 | Keep `scripts/noos_live_sync_gate.py` as the single NOOS live-state reader. | Agent | `python3 scripts/noos_live_sync_gate.py --json` |
| 012 | Add scope-specific strict modes: `runtime`, `public`, `studio`, `foundation`, `ecosystem`, `all`. | Agent | `NOOS_LIVE_SYNC_SCOPE=runtime ...` |
| 013 | Make `check_noos_live_sync_gate.sh` read-only by default unless `--write` is explicit. | Agent | No dirty receipt after check |
| 014 | Add stale receipt max-age fail for website live nerve when scope is `public` or `ecosystem`. | Agent | Simulated stale receipt |
| 015 | Add SourceA session gate warning detail summary without dumping huge receipt bodies. | Agent | Receipt size remains bounded |
| 016 | Add Studio boundary command result only when `--full` is set. | Agent | Fast mode stable |
| 017 | Add exact next action per warning, not just warning names. | Agent | Receipt `next_actions` |
| 018 | Add live sync receipt hash to `PRODUCT_TRUTH.md` only on material updates. | Agent | Manual review |
| 019 | Add CI-safe mode that skips external network but validates schema. | Agent | `--offline-schema` |
| 020 | Define PASS/DEGRADED/FAIL semantics in one canonical doc and link from rules. | Agent | Manifest + doc tags |

## Phase 3 - Website Intelligence Drift (021-030)

| ID | Plan | Owner | Verify |
|---|---|---|---|
| 021 | Decide whether primary nav `Intelligence` means `Home` or a real `/intelligence/` hub. | Founder | Decision receipt |
| 022 | If `Home`, update website nav/copy/tests in website repo, not NOOS. | Owning repo | Website tests |
| 023 | If `/intelligence/`, build a real hub page in website repo. | Owning repo | `curl /intelligence/` 200 |
| 024 | Keep NOOS from editing website route files unless explicitly assigned. | Agent | Handoff doc |
| 025 | Update NOOS `PRODUCT_TRUTH.md` after website decision lands. | Agent | Live sync gate |
| 026 | Remove 404 warning from NOOS gate only after live `/intelligence/` or nav rename ships. | Agent | Gate warning absent |
| 027 | Add a website route meaning map: `/`, `/gel/`, `/runtime/`, `/trust-ledger/`, `/intelligence/`. | Owning repo | Static verify |
| 028 | Ensure chatbot knowledge mirrors the final route meaning. | Owning repo | Chat eval |
| 029 | Add regression: no primary nav item points to a missing page. | Owning repo | Website validator |
| 030 | Add NOOS cross-repo warning if website route meaning changes without `PRODUCT_TRUTH.md` update. | Agent | Live sync receipt |

## Phase 4 - SourceA Nerve Dependency Repair (031-040)

| ID | Plan | Owner | Verify |
|---|---|---|---|
| 031 | Treat SourceA session gate failure as ecosystem warning, not NOOS runtime failure. | Agent | NOOS gate DEGRADED |
| 032 | Identify exact SourceA failing steps: `mirror_poison_validate`, `entry_gate_worker`. | Owning repo | SourceA receipt |
| 033 | Open SourceA repair task for `INCIDENT-041` poison hits. | Owning repo | SourceA incident doc |
| 034 | Repair `entry_gate_worker` failure in SourceA, not NOOS. | Owning repo | SourceA gate OK |
| 035 | Add NOOS wording: do not claim full ecosystem green when SourceA gate is red. | Agent | AGENTS/rule check |
| 036 | Keep GEL runtime claims independent from SourceA worker block. | Agent | PRODUCT_TRUTH wording |
| 037 | Add a foundation scope in NOOS gate that returns FAIL when SourceA gate fails. | Agent | Scope test |
| 038 | Add ecosystem scope that returns DEGRADED for SourceA-only warning. | Agent | Scope test |
| 039 | Add a compact SourceA warning summary to NOOS receipt. | Agent | Receipt under size limit |
| 040 | Remove SourceA warning only after fresh SourceA session receipt is green. | Owning repo | Receipt `ok=true` |

## Phase 5 - Studio Local Dirty State (041-050)

| ID | Plan | Owner | Verify |
|---|---|---|---|
| 041 | Decide whether to keep, commit, or discard the Studio Cmd+Z experiment. | Founder | Decision |
| 042 | If keep, test Cmd+Z in Cursor vs Studio and write a precise bug scope. | Owning repo | Manual + unit test |
| 043 | If discard, restore `macos/StudioIdeShell.swift` and `src/app/layout.tsx`. | Owning repo | Studio clean tree |
| 044 | If commit, separate desktop undo bridge from Supabase boundary commits. | Owning repo | Git log split |
| 045 | Add Studio clean-tree check to NOOS live sync only as warning, not NOOS failure. | Agent | NOOS gate |
| 046 | Keep Studio Supabase boundary as authoritative for Studio data only. | Agent/Owning repo | Boundary check |
| 047 | Add "Studio dirty local work is not NOOS dirty state" clarification to handoff. | Agent | Handoff doc |
| 048 | Verify Studio `npm test` after any boundary or undo decision. | Owning repo | 112+ tests |
| 049 | Add Studio command result to NOOS gate only under `--full`. | Agent | Fast gate stable |
| 050 | Avoid mentioning Studio as public product until launch gate is defined. | Founder | Public copy review |

## Phase 6 - Validator Mesh + Node Graph (051-060)

| ID | Plan | Owner | Verify |
|---|---|---|---|
| 051 | Create a validator map that lists every NOOS gate, input, output, and owner. | Agent | New doc |
| 052 | Add node IDs for NOOS repo, GEL runtime, public website, platform, SourceA, Studio. | Agent | Live sync schema |
| 053 | Add G0-G3 change class labels to NOOS implementation docs. | Agent | Doc grep |
| 054 | For G1 changes, require one focused validator. | Agent | Checklist |
| 055 | For G2 changes, require validator plus cross-lane receipt. | Agent | Checklist |
| 056 | For G3 gate rewrites, require full NOOS tests and live sync gate. | Agent | Checklist |
| 057 | Add a validator for missing MANIFEST rows after new NOOS docs. | Agent | Script |
| 058 | Add a validator for stale "Phase 1/prototype/future API" claims. | Agent | Regex report |
| 059 | Add a validator for public URL claims that are now live/404. | Agent | HTTP check |
| 060 | Add a compact validator dashboard output for final replies. | Agent | CLI output |

## Phase 7 - Stale + Misleading Docs Cleanup (061-070)

| ID | Plan | Owner | Verify |
|---|---|---|---|
| 061 | Search NOOS docs for stale `Phase 1`, `future`, `not deployed`, and `DNS blocker` claims. | Agent | Stale report |
| 062 | Update only docs where live receipts prove the new state. | Agent | Diff review |
| 063 | Mark uncertain stale claims as `NEEDS DECISION` rather than rewriting. | Agent | Decision rows |
| 064 | Add a doc footer standard: last verified command + date for mutable live-state docs. | Agent | Doc template |
| 065 | Reconcile `PRODUCT_TRUTH.md` test count after every runtime test change. | Agent | Pytest output |
| 066 | Add `api.noetfield.com` health/readiness proof to the cloud organize doc. | Agent | Curl proof |
| 067 | Add PyPI/npm blockers as explicit gaps in every relevant GTM doc. | Agent | Grep |
| 068 | Remove website implementation ownership from NOOS docs unless handoff-only. | Agent | Handoff compliance |
| 069 | Keep SourceA as engine pattern, not default Noetfield implementation storage. | Agent | Rule/doc check |
| 070 | Create a stale-doc report before every large doc commit. | Agent | Script output |

## Phase 8 - Public/Private Leak Defense (071-080)

| ID | Plan | Owner | Verify |
|---|---|---|---|
| 071 | Keep `.env`, secrets, keys, tokens out of all NOOS receipts and docs. | Agent | Secret scan |
| 072 | Add scanner for internal SourceA paths in public-facing NOOS/public_site output. | Agent | Leak report |
| 073 | Decide whether `public_site/` is active or legacy. | Founder | Decision |
| 074 | If legacy, mark `public_site/` as legacy in README and exclude public claims from it. | Agent | README |
| 075 | If active, add validators for corporate identity claims before publish. | Agent | Public-site test |
| 076 | Do not publish "SourceA flagship" wording without founder/public identity approval. | Founder | Copy lock |
| 077 | Block TrustField claims in NOOS public output unless cross-lane approved. | Agent | Grep |
| 078 | Add `NOOS_PUBLIC_SAFE_COPY.md` for allowed external phrasing. | Agent | New doc |
| 079 | Add a leak check to live sync `--full`. | Agent | Full gate |
| 080 | Keep internal run-patch receipts out of public website knowledge. | Agent/Owning repo | Chat knowledge manifest |

## Phase 9 - Product Gaps: PyPI, npm, Chatbot RAG (081-090)

| ID | Plan | Owner | Verify |
|---|---|---|---|
| 081 | Publish PyPI `noetfield-gate` after token/trusted publisher is available. | Founder/Agent | PyPI page |
| 082 | Link `/gel/` to PyPI only after package is live. | Owning repo | Website verify |
| 083 | Build npm `@noetfield/gate` wrapper after PyPI is live. | Agent | npm pack/test |
| 084 | Add npm gap to `PRODUCT_TRUTH.md` until shipped. | Agent | Doc grep |
| 085 | Continue chatbot Phase 3 distillation beyond pricing/FAQ. | Owning repo | Chatbot tests |
| 086 | Implement chatbot Phase 4 chunk sync manifest. | Owning repo | Sync report |
| 087 | Implement chatbot Phase 5 pgvector hybrid retrieval only after corpus > 40k chars. | Owning repo | Eval recall |
| 088 | Expand live chat eval to 100 canonical questions. | Owning repo | Eval JSON |
| 089 | Add live eval report pointer to NOOS only when runtime/GEL questions are affected. | Agent | Handoff doc |
| 090 | Keep chatbot deterministic fallbacks narrow; retrieval/model remains primary. | Owning repo | Chat tests |

## Phase 10 - Operating Cadence + Exit Criteria (091-100)

| ID | Plan | Owner | Verify |
|---|---|---|---|
| 091 | Define daily NOOS closeout: clean tree, live sync scope, tests run, warnings. | Agent | Closeout template |
| 092 | Define weekly cross-repo sync: website nerve, NOOS gate, Studio boundary, SourceA session gate. | Agent/Owning repos | Weekly receipt |
| 093 | Add "do not leave dirty tree" rule to every active NOOS execution checklist. | Agent | Rule grep |
| 094 | Add future decision queue section to `PRODUCT_TRUTH.md` only for unresolved founder decisions. | Agent | Doc review |
| 095 | Add owner labels to every known warning: Founder, NOOS, Website, SourceA, Studio. | Agent | Gate receipt |
| 096 | Add escalation: FAIL blocks claims; DEGRADED allows scoped work with warnings. | Agent | Gate docs |
| 097 | Add post-commit check: clean tree + branch ahead count + no generated churn. | Agent | Script |
| 098 | Add push/deploy policy: no push/deploy unless founder asks or plan says so. | Agent | AGENTS.md |
| 099 | Exit when NOOS gate `ecosystem` is PASS, SourceA session gate green, `/intelligence/` resolved, Studio clean, and PyPI/npm gap decisions recorded. | Founder/Agent | Live sync PASS |
| 100 | Create v2 plan only after at least 50 of these rows have evidence receipts or explicit deferrals. | Agent | Plan manifest |

---

## Immediate Recommended Order

1. Keep repo clean after this doc is committed.
2. Fix generated receipt policy and clean-tree validator first.
3. Decide `/intelligence/` route vs Home rename.
4. Repair SourceA session gate in SourceA.
5. Resolve Studio Cmd+Z dirty files.
6. Continue PyPI/npm and chatbot RAG as product gaps.

## Non-Negotiable Claims Rule

Do not say "whole system fully green" while `NOOS_LIVE_SYNC` is `DEGRADED`. Say: "Noetfield required runtime/public surfaces are usable; ecosystem is degraded by SourceA session gate and `/intelligence/` route drift."

---

## Cleanup Closeout - 2026-06-29

**Closed in NOOS:**

- `001` clean start/end rule enforced by `scripts/check_noos_clean_tree.sh`.
- `002` generated run-patch churn policy recorded in run-patch control doc and `AGENTS.md`.
- `004` clean-tree guard added.
- `005` commit gate now includes doc tags, tests, diff check, manifest JSON, and clean-tree guard.
- `008` factory-loop writer detection added to the clean-tree guard.
- `009` dirty-tree closeout section added to `AGENTS.md`.
- `061-062` stale live-state scan run; misleading API-local-only claims corrected.
- `065` `PRODUCT_TRUTH.md` UPG count reconciled to `UPGRADE_MANIFEST.json`.
- `097` post-commit clean-tree check added through `scripts/check_noos_clean_tree.sh`.

**Still open by authority boundary:**

- `/intelligence/` route drift remains a website/founder decision.
- SourceA session gate repair remains in SourceA.
- Studio Cmd+Z experiment cleanup remains in Studio/founder decision scope.
- PyPI token/trusted publisher remains founder/API credential scope.
- npm SDK and chatbot RAG remain product backlog, not dirty-tree blockers.

