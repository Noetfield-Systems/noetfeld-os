# CHATBOT KNOWLEDGE UPGRADE — LOCKED v1

**Status:** LOCKED  
**Date:** 2026-06-26  
**Scope:** www.noetfield.com public assistant (`POST /api/public/chat`)  
**Trace:** `NOETFIELD-CHATBOT-KNOWLEDGE-V1`  
**Locked by:** noetfeld-os-cursor-chat

---

## Problem statement (live audit 2026-06-26)

Ten real client scenarios tested against **production** www chat (platform-proxy + OpenRouter):

| # | Scenario | Live result before upgrade |
|---|----------|----------------------------|
| 1 | Mortgage broker / pricing | OK — missed Diagnostic Sprint |
| 2 | GEL vs homepage | **FAIL** — denied GEL acronym |
| 3 | PyPI org / noetfield-gate | **FAIL** — denied package exists |
| 4 | Copilot governance | OK |
| 5 | Bank shadow mode | OK |
| 6 | Sandbox limits | OK |
| 7 | No custody | OK |
| 8 | Investor diligence | Weak — no `/investors/diligence/` |
| 9 | Trust Ledger vs Trust Brief | Partial |
| 10 | Contact + RID | OK |

**Cause:** ~10 KB FAQ corpus, stale `FINAL_PUBLIC_SITE.md`, prompt “three offerings only”, no GEL/developer KB. Postgres `knowledge_chunks` synced but **not read at inference** (NF-ENG-12 deferred).

**Goal:** Public assistant answers **public Noetfield truth** with citations — not Cursor-grade repo access, but no anti-hallucinations on GEL/PyPI.

---

## Architecture target

```
SSOT markdown + www distill → lane-tagged chunks → hybrid retrieve → grounded LLM → 10-scenario eval gate
```

| Layer | Path | Role |
|-------|------|------|
| Knowledge | `data/chatbot/knowledge/*.md` | Public-safe corpus |
| Loader | `chatbot_knowledge.py` | Lane detect + forced include + keyword rank |
| Prompt | `public_chat.py` | Multi-audience lanes, GEL/PyPI explicit |
| Proxy | `api/public/chat/index.js` | www → platform LLM |
| Future | `knowledge_chunks` + pgvector | NF-ENG-12 |

---

## Executed in repo (2026-06-26) — Phase A

**Not live until `platform.noetfield.com` redeploy.**

### New knowledge files

| File | Lane |
|------|------|
| `gel-runtime.md` | GEL, /gel/, api.noetfield.com |
| `developer-tools.md` | PyPI, noetfield-gate, org form templates |
| `site-surfaces.md` | Hosts, URLs, intake |
| `intelligence-lane.md` | Diagnostic Sprint, SME |
| `trust-ledger-public.md` | TLE vs Trust Brief |
| `investor-public.md` | /investors/diligence/ |

### Code

- `chatbot_knowledge.py` — lane detection, forced sections, 32k budget, removed stale `FINAL_PUBLIC_SITE.md`
- `public_chat.py` — prompt rewrite (GEL public, PyPI package exists, multi-audience)
- `faq.md` — GEL section added
- `tests/unit/test_chat_scenarios.py` — 10 scenario retrieval tests (11 pass)
- `docs/CHATBOT_SETUP.md` — source list updated

### Local verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield
PYTHONPATH=services/governance:services/events:packages/config \
  python3 -m pytest tests/unit/test_chat_scenarios.py tests/unit/test_chat_quality.py -q
```

---

## 10 phases · 100 plans (full register)

Status key: **DONE** · **PARTIAL** · **OPEN**

### Phase 1 — Audit & SSOT map (001–010)

| ID | Plan | Status |
|----|------|--------|
| 001 | Inventory chatbot code paths (`public_chat.py`, `chatbot_knowledge.py`, Vercel proxy, widget) | DONE |
| 002 | Document live deploy path www → Vercel → platform LLM | DONE |
| 003 | Map indexed files vs live www pages (`/`, `/gel/`, `/pricing/`, `/faq/`) | DONE |
| 004 | Flag stale sources (`FINAL_PUBLIC_SITE.md`) for removal | DONE |
| 005 | List public-safe vs internal-only docs under `docs/` | DONE |
| 006 | Define `data/chatbot/MANIFEST.json` (source, lane, freshness) | DONE |
| 007 | Cross-link OFFERINGS_LOCKED, L0-law, commercial SSOT | PARTIAL |
| 008 | Pull public distill list from noetfeld-os (README, gate docs, PRODUCT_TRUTH slice) | PARTIAL |
| 009 | Baseline `/api/public/chat/health` metrics in locked doc | DONE |
| 010 | Publish gap report — 10 live client scenarios | DONE |

### Phase 2 — Knowledge corpus expansion (011–020)

| ID | Plan | Status |
|----|------|--------|
| 011 | Add `gel-runtime.md` (GEL, /gel/, api.noetfield.com) | DONE |
| 012 | Add `developer-tools.md` (noetfield-gate, PyPI org templates) | DONE |
| 013 | Add `intelligence-lane.md` (Diagnostic Sprint, SME) | DONE |
| 014 | Add `pricing-matrix.md` synced from `/pricing/` HTML | OPEN |
| 015 | Add `faq-live.md` distilled from `/faq/index.html` | OPEN |
| 016 | Add `sandbox-freemium.md` merge from FREEMIUM_POLICY | PARTIAL |
| 017 | Add `trust-ledger-public.md` | DONE |
| 018 | Add `copilot-pack.md` from pilot pricing + procurement FAQ | OPEN |
| 019 | Add `bank-pilot-shadow.md` from shadow-mode docs | PARTIAL |
| 020 | Add `site-surfaces.md` (hosts, routes, investor paths) | DONE |

### Phase 3 — Distillation pipeline (021–030)

| ID | Plan | Status |
|----|------|--------|
| 021 | Script `scripts/distill-www-to-knowledge.py` (HTML → markdown chunks) | OPEN |
| 022 | Script `scripts/distill-docs-to-knowledge.py` (allowlist paths) | OPEN |
| 023 | Script `scripts/distill-external-repo.py` (noetfeld-os public files) | OPEN |
| 024 | Strip secrets and internal paths from distilled chunks | OPEN |
| 025 | Frontmatter: `lane`, `updated`, `source_path`, `public:true` | OPEN |
| 026 | Target `make chatbot-refresh` (distill + validate) | OPEN |
| 027 | CI: live www pricing matches `pricing-matrix.md` | OPEN |
| 028 | CI fail if manifest source missing or stale vs source file | OPEN |
| 029 | Expose `knowledge_bundle_version` on chat health endpoint | OPEN |
| 030 | Remove hard dependency on stale `_EXTRA_MD` sources | PARTIAL |

### Phase 4 — Chunking & Postgres sync (031–040)

| ID | Plan | Status |
|----|------|--------|
| 031 | Extend `sync_knowledge_chunks.py` to read MANIFEST + all knowledge dirs | PARTIAL |
| 032 | Chunk by `##` with max ~2k tokens, 100-token overlap | OPEN |
| 033 | Store `lane`, `url_citations`, `content_hash` per chunk | OPEN |
| 034 | Add `knowledge_sync_runs` audit table | OPEN |
| 035 | Wire `make platform-sync-knowledge` into deploy runbook | OPEN |
| 036 | Health reports chunk count by lane | OPEN |
| 037 | Soft-delete chunks when source file removed | OPEN |
| 038 | Nightly sync job on Railway/platform | OPEN |
| 039 | Backfill from L2-knowledge allowlist only (not raw 151 files) | OPEN |
| 040 | Operator doc section in RUNBOOK (already stub — expand) | PARTIAL |

### Phase 5 — Vector RAG NF-ENG-12 (041–050)

| ID | Plan | Status |
|----|------|--------|
| 041 | Enable pgvector on `knowledge_chunks.embedding` | OPEN |
| 042 | Embed chunks (OpenRouter or Gemini embedding model) | OPEN |
| 043 | Implement `retrieve_chunks(question, k=8, lanes=auto)` | OPEN |
| 044 | Hybrid retrieve: vector + keyword + pinned core | OPEN |
| 045 | Replace keyword-only overflow in `select_relevant_excerpt` | OPEN |
| 046 | Raise effective context budget to 32k ranked chunks only | PARTIAL |
| 047 | Return chunk `source_path` + www URL in citations | OPEN |
| 048 | Log retrieval scores to Langfuse | OPEN |
| 049 | A/B shadow: keyword-only vs hybrid | OPEN |
| 050 | Ship hybrid default when recall@8 beats baseline on eval | OPEN |

### Phase 6 — Prompt & policy upgrade (051–060)

| ID | Plan | Status |
|----|------|--------|
| 051 | Replace “three offerings only” with locked SKU list from manifest | DONE |
| 052 | Add lanes: buyer / developer / partner / investor in system prompt | DONE |
| 053 | Allow procedural answers (PyPI org, sandbox steps) from developer KB | DONE |
| 054 | Keep hard bans: no invented pricing, no custody claims, no secrets | DONE |
| 055 | Add homepage vs GEL compare instruction | DONE |
| 056 | Multi-turn session summary (last 3 turns) | OPEN |
| 057 | Align Telegram bot to same retrieval path | OPEN |
| 058 | Deprecate divergent www-local regex rules — shared module or proxy-only | OPEN |
| 059 | Widget shows citation links (www paths, not just doc labels) | OPEN |
| 060 | Welcome message reflects buyer + GEL + developer lanes | OPEN |

### Phase 7 — Quality & eval (061–070)

| ID | Plan | Status |
|----|------|--------|
| 061 | Expand eval suite toward 100 canonical questions | PARTIAL |
| 062 | Buckets: pricing, GEL, gate CLI, intake, regulatory, anti-ICP | PARTIAL |
| 063 | Golden answers with required + forbidden phrases | OPEN |
| 064 | Nightly eval against live LLM on staging | OPEN |
| 065 | Score groundedness, citation present, no hallucinated prices | OPEN |
| 066 | Block deploy if P0 bucket score &lt; 90% | OPEN |
| 067 | Regression: PyPI org question must not refuse | DONE |
| 068 | Regression: GEL acronym question must not deny GEL | DONE |
| 069 | Publish `chat_eval_last_run.json` in reports | OPEN |
| 070 | Founder review queue for failed eval questions | OPEN |

### Phase 8 — Live truth sync (071–080)

| ID | Plan | Status |
|----|------|--------|
| 071 | Weekly PRODUCT_TRUTH public slice → developer KB | OPEN |
| 072 | Cache `api.noetfield.com/health` in `live-surfaces.json` for bot | OPEN |
| 073 | Bot states API up/down from cache (not hallucinated) | OPEN |
| 074 | Sync www E2E smoke into knowledge freshness metadata | OPEN |
| 075 | Auto-update “what ships today” from `/gel/` into `gel-runtime.md` | OPEN |
| 076 | Link PyPI package page when live | OPEN |
| 077 | Link npm `@noetfield/gate` when shipped | OPEN |
| 078 | Studio IDE mention gated until public launch | OPEN |
| 079 | Cloud inventory public summary (hosts only) | OPEN |
| 080 | Manifest `freshness_sla_hours: 168` with stale alerts | OPEN |

### Phase 9 — Smarter behaviors (081–090)

| ID | Plan | Status |
|----|------|--------|
| 081 | Intent classifier before retrieve (buyer / developer / off-topic) | PARTIAL |
| 082 | Off-topic: redirect politely, no fake KB coverage | OPEN |
| 083 | Structured reply blocks: Pricing / Intake / Docs links | OPEN |
| 084 | Form-filling mode (“Organization Description”, “Anticipated usage”) | PARTIAL |
| 085 | Tool: inject `GET /api/ecosystem/health` when user asks platform status | OPEN |
| 086 | Tool: search www sitemap for page links | OPEN |
| 087 | Rate-limit by lane | OPEN |
| 088 | Thumbs feedback → Langfuse + failed eval queue | OPEN |
| 089 | Session RID tie-in with footer Request ID | OPEN |
| 090 | Partner/investor lanes route to correct intake URLs | PARTIAL |

### Phase 10 — Operate & scale (091–100)

| ID | Plan | Status |
|----|------|--------|
| 091 | Name `CHATBOT_KNOWLEDGE_OWNER` in RUNBOOK | OPEN |
| 092 | Weekly `make chatbot-refresh` (distill + sync + eval) | OPEN |
| 093 | Monthly prune unused chunks | OPEN |
| 094 | Quarterly SSOT reconciliation with OFFERINGS_LOCKED | OPEN |
| 095 | Document anti-pattern: no raw 4,600-file dump | DONE |
| 096 | Train ops: edit SSOT → distill → sync → eval | OPEN |
| 097 | Public changelog: “Assistant knowledge updated YYYY-MM-DD” | OPEN |
| 098 | Metrics: deflection rate, intake conversion, “don’t know” rate | OPEN |
| 099 | Phase 2: authenticated console assistant (separate KB) | OPEN |
| 100 | **Exit:** 90%+ P0 eval, &lt;5% “don’t know” on buyer/dev/investor | OPEN |

### Register summary (2026-06-26)

| Status | Count |
|--------|------:|
| DONE | 22 |
| PARTIAL | 14 |
| OPEN | 64 |
| **Total** | **100** |

**Executed code (Phase A)** covers ~22 DONE + 14 PARTIAL — **not** all 100 plans implemented. Phases 3–5 and most of 8–10 remain OPEN until distill, deploy, pgvector, and eval scale ship.

---

## 10 phases · 100 plans (roadmap summary)

<details>
<summary>Collapsed phase summary (same register as above)</summary>

Phase 1 partial ✅ · Phase 2 mixed (011–017,020 done; 014–015,018 open) · Phase 3–5 open · Phase 6–7 partial · Phase 8–10 open.

</details>

---

## Remaining from past master plan (cloud organize Phase 8)

| Item | Status | Blocker |
|------|--------|---------|
| PyPI `noetfield-gate` publish | Built, not live on PyPI | `PYPI_API_TOKEN` or trusted publisher |
| npm `@noetfield/gate` | Not started | After PyPI |
| Studio PNG/SVG export | **Done** (`f668cee` studio-ide) | — |
| **Chatbot knowledge upgrade** | **Code done, not deployed** | Platform redeploy |
| pgvector RAG | Deferred NF-ENG-12 | Phase 5 |
| Gel page ↔ PyPI/npm links | www `/gel/` exists | Publish packages first |

---

## Next steps (ordered)

### P0 — Ship what is already built

1. **Commit + push** Noetfield chatbot changes (this repo).
2. **Redeploy `platform.noetfield.com`** (governance FastAPI) so live chat loads new KB + prompt.
3. **Re-run 10 live scenarios** (curl or `check_noetfield_com_e2e.py` extend).
4. **PyPI:** add org + token or trusted publisher → `bash scripts/publish-gate-pypi.sh prod` (noetfeld-os).

### P1 — Close knowledge drift

5. Phase 3 distill scripts — pricing + faq from live HTML.
6. Remove/replace any remaining stale `_EXTRA_MD` sources.
7. Expand eval to **100 canonical questions** + deploy gate.

### P2 — Scale retrieval

8. Wire `sync_knowledge_chunks` on deploy.
9. NF-ENG-12 pgvector hybrid RAG when corpus &gt; 40k chars.

### P3 — GTM alignment

10. Link `/gel/` to live PyPI when published.
11. npm `@noetfield/gate` wrapper.
12. Weekly `make chatbot-refresh` in RUNBOOK.

---

## Live verification (after platform deploy)

```bash
curl -sS https://www.noetfield.com/api/public/chat/health | python3 -m json.tool
# expect knowledge.chars > 20000, knowledge_files >= 11

curl -sS -X POST https://www.noetfield.com/api/public/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"What is GEL and how is it different from the homepage?"}'
# must mention Governance Execution Layer and /gel/
```

---

## Non-goals

- Chatbot will **not** access private repos, agent vault, or run code like Cursor.
- Internal-only docs under `docs/ops/**` stay out of public KB unless distilled.
- Do not dump 4,600+ markdown files raw into context — allowlist + distill only.

---

**Related:** `docs/CHATBOT_SETUP.md` · `docs/PRODUCT_DEFERRED.md` (NF-ENG-12) · `docs/ops/NOETFIELD_CLOUD_ORGANIZE_MASTER_PLAN_LOCKED_v1.md`
