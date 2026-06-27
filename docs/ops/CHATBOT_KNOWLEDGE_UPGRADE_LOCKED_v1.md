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

## 10 phases · 100 plans (roadmap)

### Phase 1 — Audit & SSOT map (001–010) ✅ partial

001–010 inventory, gap report, manifest — **done in this locked doc + live 10-scenario audit**.

### Phase 2 — Corpus expansion (011–020) ✅ done

011–016 GEL, developer, intelligence, trust, investor, site map — **shipped in Phase A**.

017–020 pricing-matrix from HTML, faq-live distill, sandbox doc merge, site-map auto — **open**.

### Phase 3 — Distillation pipeline (021–030) ⬜ next

021 `distill-www-to-knowledge.py`  
022 `distill-docs-allowlist.py`  
023 `distill-noetfeld-os-public.py`  
024 secret strip  
025 frontmatter (`lane`, `public`, `updated`)  
026 `make chatbot-refresh`  
027–030 CI freshness checks  

### Phase 4 — Postgres chunk sync (031–040) ⬜

031–040 extend `sync_knowledge_chunks.py`, deploy sync job, health chunk counts — **table exists, reader not wired**.

### Phase 5 — Vector RAG NF-ENG-12 (041–050) ⬜

041 pgvector embeddings  
042–050 hybrid retrieve, replace keyword-only at scale  

### Phase 6 — Prompt & policy (051–060) ✅ partial

051–055 multi-lane prompt — **done**  
056–060 session memory, Telegram parity, deprecate divergent www-local rules — **open**

### Phase 7 — Quality eval (061–070) ✅ partial

061–067 ten scenario tests — **done**  
068–070 expand to 100 questions, nightly eval, deploy gate — **open**

### Phase 8 — Live truth sync (071–080) ⬜

071–080 PRODUCT_TRUTH slice, api health cache, PyPI/npm link when live  

### Phase 9 — Smarter behaviors (081–090) ⬜

081 intent routing, 084 form-filling mode, 085 ecosystem health tool  

### Phase 10 — Operate (091–100) ⬜

091–100 owner, weekly refresh, metrics, exit: **90%+ P0 eval, &lt;5% “don’t know” on buyer/dev/investor**

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
