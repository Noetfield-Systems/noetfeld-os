# [NOOS-AGENT-20260608-005] ORIENTATION — Start Here

<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260608-005
doc_type: ORIENTATION
workspace_root: /Users/sinakazemnezhad/Desktop/Noetfield-Systems/noetfeld-OS
classification: INTERNAL — read first in every new session
-->

**Read this first.** 60-second scan → full picture.

---

## 1. What this is

| | |
|---|---|
| **Repo** | `/Users/sinakazemnezhad/Desktop/Noetfield-Systems/noetfeld-OS` |
| **Product** | **Noetfield OS** — Governance Execution Layer (GEL) |
| **Parent brand** | [Noetfield Systems Inc.](https://noetfield.com) — pre-execution governance |
| **Agent** | `noetfeld-os-cursor-chat` (this Cursor chat lane) |
| **Search tag** | `NOOS-AGENT-DOC` |

**One sentence:** A standalone API that **evaluates regulated decisions before execution**, returns APPROVE / REVIEW / DECLINE, and writes an **audit trail** — non-custodial, no payments.

---

## 2. Where we sit in the ecosystem

```
ASF (you — final authority)
  └── Sina OS [DESIGN]          ~/Desktop/sourceA/SINA_OS_SSOT_LOCKED.md
        └── Noetfield [brand]   noetfield.com
              └── Noetfield OS [DELIVERY]  ← THIS REPO
        └── SinaaiRuntime [EXECUTION]  :8000 (mono — do NOT merge into)
        └── TrustField [peer company]  trustfield.ca (separate — not us)
```

**Three planes** (Auto-Conflict Engine v3):

| Plane | Authority | This repo |
|-------|-----------|-----------|
| DESIGN | Desktop SourceA SSOT | Subordinate — read, don't override |
| EXECUTION | SinaaiRuntime :8000 | Isolated — never a submodule |
| DELIVERY | This code + NOOS docs | **Canonical for our output** |

**Mac Cursor Local (T2):** Operator card `[NOOS-AGENT-20260703-004]_CURSOR_LOCAL_MAC_OPERATOR_v1.md` · open lane: `make local-lane TASK=... SCOPE=...` · subagent: `.cursor/agents/noetfield-os-local-operator.md`

---

## 3. What is built (code today)

```
noetfeld-os/
├── config.py              # thresholds, weights, paths
├── database.py            # SQLite audit (→ Postgres planned)
├── policy_loader.py       # base + corridor JSON policies
├── base_policy.json
├── corridor_policy.json
├── risk_model.py          # feature engineering + scoring
├── decision_engine.py     # policy + corridors + audit
├── router.py              # POST /v1/decision
├── portal/routes.py       # GET /portal/audits
├── audit/audit_store.py
├── run.py                 # FastAPI entrypoint
└── docs/_NOOS_AGENT/      # agent-owned intelligence (tagged)
```

**Run locally:**

```bash
cd ~/Desktop/Noetfield-Systems/noetfeld-OS
python3 scripts/mint_api_key.py
.venv/bin/uvicorn run:app --reload --port 8001
# Docs: http://localhost:8001/docs
```

**Status:** Phase 2 pre-execution gate — auth, `rule_set_version`, idempotency, health probes.

---

## 4. What is NOT built yet (honest gaps)

| Gap | Roadmap phase |
|-----|---------------|
| Postgres append-only audit | Phase 3 |
| Full tenant RLS | Phase 4 |
| Rate limiting per API key | Phase 2.7 |
| Board export bundle | Phase 3 |
| `GET /drift` + drift engine | Phase 5 |
| `api.noetfield.com` production hardening | Phase 7; host is live, hardening remains |
| First paying pilot | Phase 9 |

---

## 5. Agent document vault (read order)

| Order | trace_id | Document | Purpose |
|-------|----------|----------|---------|
| **0** | `NOETFIELD-UNIFIED-MASTER-V1` | **NOETFIELD_UNIFIED_MASTER_v1_LOCKED.md** | Map all Noetfield content |
| **1** | `NOETFIELD-OS-SSOT-V1` | **NOETFIELD_OS_SSOT_v1_LOCKED.md** | Product SSOT — build/GTM |
| **2** | `NOOS-AGENT-PRODUCT-TRUTH` | **PRODUCT_TRUTH.md** | Live code state |
| **0b** | `NOOS-AGENT-20260705-029` | **Living System 99-Plan LOCKED** | Loop autonomy · CF/Railway · deadman |
| **0c** | `NOOS-AGENT-20260706-031` | **Deadman Telegram lane LOCKED** | Never @Gateway_A · send_alerts off |
| **0d** | `NOOS-AGENT-20260706-032` | **Stale doc register** | Superseded plans — do not execute |
| 3 | `NOOS-AGENT-20260608-005` | **This file** | Repo orientation |
| 2 | `NOOS-AGENT-20260529-002` | Business & ICP definition | Who we are / who we sell to |
| 3 | `NOOS-AGENT-20260608-003` | 10 market success models | Learn from market (not battle) |
| 4 | `NOOS-AGENT-20260529-001` | Governance drift essay | Drift engine thesis |
| 5 | `NOOS-AGENT-20260608-004` | **1000-step roadmap** | Execution plan |
| — | `ROADMAP_MANIFEST.json` | Step completion tracker | Mark done steps here |

**Vault path:** `docs/_NOOS_AGENT/`  
**Index:** `docs/_NOOS_AGENT/MANIFEST.json`  
**Entrypoint:** `AGENTS.md` (repo root)

**Rule:** Other agents must **not** edit `_NOOS_AGENT/` without explicit merge task. They use their own tags (`NFRT-AGENT-DOC`, etc.).

---

## 6. Product positioning (30 seconds)

- **Category:** Governance Execution Layer (GEL)
- **Field:** Pre-execution governance for **regulated operational decisions**
- **Geography:** Canada first (BC CUs, lending fintech, enterprise)
- **SKUs:** GEL Starter → GEL Standard → GEL + Trust Ledger
- **Not us:** Full GRC (OneTrust), agent tool proxy (WhiteFin), LLM hosting, lending core, payments

**External line:** *Noetfield OS evaluates policy, scores risk, and produces audit-ready evidence before your systems execute.*

---

## 7. Roadmap at a glance (10 phases)

| Phase | Focus | Market lens |
|-------|-------|-------------|
| 1 | Declare & baseline | Credo + OneTrust |
| 2 | Pre-execution gate | Exogram + WhiteFin + Execlave |
| 3 | Audit & Trust Ledger | FairNow + Credo |
| 4 | Tenant & determinism | Fiddler + Holistic |
| 5 | Drift engine | Galileo |
| 6 | Canadian vertical | Holistic + Fiddler FS |
| 7 | Developer PLG | Execlave + Exogram |
| 8 | Partner channels | OneTrust + IBM |
| 9 | Enterprise pilot | Fiddler + FairNow |
| 10 | Category leadership | All ten |

**You are here:** **Phase 2 in progress** — core gate shipped (auth, versioning, idempotency, health); rate limits + export next.

**Next practical steps:** Follow `NOOS-AGENT-20260615-006` weeks 5–6 — audit export + CU policy pack.

---

## 8. Golden rules (non-negotiable)

1. **Non-custodial** — governance signals only  
2. **Pre-execution** — never trigger downstream execution  
3. **Fail closed** — if gate fails, no unchecked decisions  
4. **Append-only audit** — evidence is the product  
5. **Version everything** — policy, rules, baselines  
6. **Tag docs** — `NOOS-AGENT-DOC` on every agent artifact  
7. **Canada first** — depth over global breadth  
8. **Evidence > dashboards**  
9. **Stay narrow** — GEL only, not full GRC  
10. **ASF decides structure** — registry + announcement for ecosystem changes  

---

## 9. Other artifacts (non-agent)

| Path | What |
|------|------|
| `docs/output/external/` | Grant PDFs, pitch decks (IRAP/partners) |
| `docs/output/internal/` | Internal PDFs + reality check |
| `docs/scripts/build_documents.py` | Regenerate PDFs |
| `~/Desktop/Noetfield-Documents-*` | Desktop copy of grant materials |
| `~/Desktop/sourceA/` | Ecosystem SSOT (DESIGN — read only) |

---

## 10. Who to ask for what

| Question | Where |
|----------|-------|
| Ecosystem structure / phases | `~/Desktop/sourceA/SINA_OS_SSOT_LOCKED.md` |
| Cross-plane conflicts | `~/Desktop/sourceA/AUTO_CONFLICT_ENGINE_V3_LOCKED.md` |
| Product scope & ICP | `NOOS-AGENT-20260529-002` |
| Market examples | `NOOS-AGENT-20260608-003` |
| What to build next | `NOOS-AGENT-20260608-004` (roadmap) |
| Structural registry change | ASF → mono registry + announcement |

---

## 11. Session checklist (agents)

- [ ] Read this orientation  
- [ ] Grep `NOOS-AGENT-DOC` before editing vault docs  
- [ ] Confirm task is DELIVERY-lane (this repo), not mono Runtime  
- [ ] Do not claim "production Noetfield" until Phase 9 exit criteria  
- [ ] Tag new docs + update `MANIFEST.json`  
- [ ] Mark completed roadmap steps in `ROADMAP_MANIFEST.json`  

---

*End of ORIENTATION — `NOOS-AGENT-20260608-005`*
