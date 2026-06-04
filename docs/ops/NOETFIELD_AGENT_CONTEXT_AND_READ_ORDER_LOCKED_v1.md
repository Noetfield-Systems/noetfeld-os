# Noetfield Agent Context & Read Order (LOCKED v1)

**Status:** LOCKED — every Noetfield Cursor agent reads this before implement  
**Locked:** 2026-06-04  
**Authority:** ASF  
**Path:** `docs/ops/NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md`  
**Full link index (all repos):** [AGENT_READ_LINKS_LOCKED_v1.md](./AGENT_READ_LINKS_LOCKED_v1.md) · SourceA `founder/repo-agent-notices/AGENT_READ_LINKS_INDEX.md`

---

## 1. One-line truth

**Smarter agent = read more sources in order — not a better model than your repo.**

Intelligence comes from: **this repo (right branch + disk)** + **SourceA law** + **ship plan** + **ingest reporting** + **conversation handoff** — not from bypassing `os/plan.json` or editing SinaPromptOS.

---

## 2. Two workspaces (do not confuse)

| Agent id (SourceA) | Open folder | Role |
|--------------------|-------------|------|
| **noetfield_cloud** | `~/Desktop/Noetfield` | **Ship code** — APIs, UI, `:13080`, tests |
| **noetfield_local** | `~/Desktop/Noetfield-All-Documents` | **Docs archive** — not runnable stack |

**Implementation SSOT:** `~/Desktop/Noetfield` only.  
**Never** treat All-Documents as the running product unless explicitly copying docs into the implementation repo.

---

## 3. Git vs disk vs cloud (Mac gap analysis)

| Layer | What it is |
|-------|------------|
| **`main`** | Older; most DELIVERY/TLE work is on feature branch until PR merges |
| **`cursor/bank-grade-fullstack-37f0`** | Feature branch (PR #15) — ship rules, TLE, workspace |
| **Working tree (uncommitted)** | May be **ahead of last commit** — always `git status` before assuming remote = truth |
| **Cloud Cursor workspace** | Same branch + optional `ops/private/sourceA/` + **chat summary** — not “smarter model” |

**Forbidden assumption:** “GitHub main has everything the cloud agent knows.”

---

## 4. Mandatory read order (every implement session)

Read in order; skip only if path missing (note in reply).

### A — Ecosystem law (SourceA, not in git)

| # | Source | Path |
|---|--------|------|
| A1 | SSOT master (read-only) | `~/Desktop/SourceA/SINA_OS_SSOT_LOCKED.md` |
| A2 | Auto Conflict Engine v3 | `~/Desktop/SourceA/AUTO_CONFLICT_ENGINE_V3_LOCKED.md` |
| A3 | FAST TRACK (parallel lanes) | `~/Desktop/SourceA/SINAAI_FAST_TRACK_FORCE_MAJEURE_LOCKED_v1.md` |
| A4 | YAML ingest law | `~/Desktop/SourceA/SINAAI_AGENT_YAML_INGEST_LOCKED_v1.md` |
| A5 | Agent output contract | `~/Desktop/SourceA/AGENT_OUTPUT_CONTRACT_v1.yaml` |
| A6 | Ecosystem status (generated) | `~/Desktop/SourceA/ECOSYSTEM_STATUS.md` |
| A7 | Execution truth (generated) | `~/Desktop/SourceA/EXECUTION_TRUTH.json` → `repos.noetfield` |
| A8 | Global priority (generated) | `~/Desktop/SourceA/GLOBAL_PRIORITY.json` |

**In-repo mirror (after founder sync):** `ops/private/sourceA/` — same files, gitignored.

```bash
./scripts/bootstrap-private-ops.sh    # once
./scripts/sync-sourceA-desktop.sh       # Desktop → ops/private/sourceA/
```

### B — Noetfield ship authority (this repo)

| # | Source | Path |
|---|--------|------|
| B1 | **Ship queue** | `os/SHIP_NOW.md` |
| B2 | **Tasks + done** | `os/plan.json` |
| B3 | Sprint backlog | `os/sprint-trust-ledger-v1.2.md` |
| B4 | Locked index | `os/LOCKED_REFERENCE_INDEX.md` |
| B5 | Product scope gate | `PRODUCT_TRUTH.md` |
| B6 | Boundaries | `PROJECT_BOUNDARIES_LOCKED.md` |
| B7 | **Positioning v1.2** | `docs/strategy/NOETFIELD_TRUST_LEDGER_POSITIONING_LOCKED_v1.2.md` |
| B8 | TLE v1.2 pack | `docs/strategy/NOETFIELD_COPILOT_TLE_V12_LOCKED.md` (if present) |
| B9 | SME design (Lane A/B/C) | `docs/strategy/NOETFIELD_COPILOT_SME_SYSTEM_DESIGN_LOCKED_v1.md` |
| B10 | Agent tracking | `.cursor/AGENT_TRACKING.md` |
| B11 | Cursor rules | `.cursor/rules/noetfield-ship-first.mdc`, `noetfield-ingest-yaml.mdc`, `noetfield-no-asf-plans.mdc` |
| B12 | **Future plans (1000, NO ASF)** | `os/plans/REGISTRY.json`, `os/plans/README.md` |

### C — Engineering handoff (when touching product)

| # | Source | Path |
|---|--------|------|
| C1 | TLE schema | `packages/schemas/tle-v1.schema.json` |
| C2 | TLE OpenAPI | `docs/spec/openapi/tle-v1.openapi.yaml` |
| C3 | TLE samples | `docs/spec/samples/tle-*.yaml` |
| C4 | Local dev | `docs/LOCAL_DEV.md`, `docs/ops/STAGING_DEMO.md` |
| C5 | Tenant audit outline | `docs/spec/tenant-append-only-audit-schema-outline.md` |

---

## 5. Operating rules (LOCKED)

| Rule | Meaning |
|------|---------|
| **Ship** | Next work from `os/plan.json` / `os/SHIP_NOW.md` — **do not stop** waiting for next Prompt OS / M8 dispatch order |
| **Ingest** | **Send answer to system** — YAML footer + `reports/cursor-reply-latest.txt` after VERIFY — **required** |
| **Do not edit** | `~/Desktop/SinaPromptOS/**` — no weakening ingest/dispatch |
| **Do not edit** | `~/Desktop/SourceA/**` — read-only; ASF maintains law |
| **FAST TRACK** | Repo blockers in SourceA are **local notes** — other lanes continue |
| **Lane C** | No payments / custody / finance ledger in Noetfield |
| **Ports** | Local demo `:13080`; DevBridge desk uses **3004+** (not 3000–3003) per SourceA port board |

---

## 6. VERIFY (product)

```bash
cd ~/Desktop/Noetfield
make dev-local
make verify-local-dev
make tle-smoke
.venv/bin/python scripts/validate-tle-samples.py
cd governance-console/backend && ../../.venv/bin/python -m pytest tests/test_tle_flow.py -q
```

Demo URLs: http://localhost:13080/ · `/workspace` · `/trust-ledger/sample-report/`

---

## 7. Ingest (report to ecosystem — founder Mac)

```bash
~/Desktop/SinaPromptOS/scripts/ingest-cursor-reply.sh noetfield \
  ~/Desktop/Noetfield/reports/cursor-reply-latest.txt
```

Then founder cycle refreshes `SourceA/EXECUTION_TRUTH.json` (agents do not hand-edit SourceA).

**YAML must include:** `reported_at` (ISO8601 UTC), `repo: noetfield`, `verify_passed`, `task`, `status`.

---

## 8. Why SourceA still says “spec section 3” for Noetfield

Generated files (`ECOSYSTEM_STATUS.md`, `FEEDBACK_AGGREGATE.json`) lag until **ingest + publish cycle** after latest `cursor-reply-latest.txt`.  
**Product truth** = `os/plan.json` + disk on `cursor/bank-grade-fullstack-37f0`, not stale rank #6 alone.

---

## 9. Cloud vs local checklist (ASF diagnostic)

| Check | Command / path |
|-------|----------------|
| Branch | `git branch --show-current` → expect `cursor/bank-grade-fullstack-37f0` |
| Uncommitted ship work | `git status` |
| Private mirror | `ls ops/private/sourceA/` |
| Desktop SourceA | `ls ~/Desktop/SourceA/SINA_OS_SSOT_LOCKED.md` |
| Ship doc | `test -f os/SHIP_NOW.md` |
| TLE API | `test -f governance-console/backend/routes/tle.py` |

---

## 10. Agent acknowledgment (optional in reply)

```text
READ ORDER ACK — NOETFIELD_AGENT_CONTEXT_LOCKED_v1
- Read SHIP_NOW + plan.json + positioning lock before code.
- Ship without waiting for next Prompt OS order.
- Ingest YAML + cursor-reply after VERIFY.
- Did not edit SourceA or SinaPromptOS.
```

---

**Maintainer:** ASF updates this file when ecosystem law or ship model changes. Agents cite `NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1` in plan/evidence when onboarding.
