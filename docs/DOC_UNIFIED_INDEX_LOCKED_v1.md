# Noetfield unified documentation index (LOCKED v1)

| Field | Value |
|-------|--------|
| **Status** | LOCKED — single navigation SSOT for docs, agent memory, plans, and skills |
| **Updated** | 2026-06-13 |
| **Router** | [README.md](./README.md) |
| **Verify** | `make verify-doc-ssot` |
| **Reports** | [`reports/README.md`](../reports/README.md) — ephemeral ingest/handoff only |

---

## 1. Read this first (every agent session)

| Order | Asset | Path |
|-------|-------|------|
| 1 | Agent memory | `.cursor/agent-memory/MEMORY_LOCKED.yaml` |
| 1b | Cursor layer | `.cursor/README.md` — skills + rules index |
| 2 | Incidents | `.cursor/incidents/REGISTRY.md` |
| 3 | Agent tracking | `.cursor/AGENT_TRACKING.md` |
| 4 | Read order | `docs/ops/NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md` |
| 5 | Link chain | `docs/ops/AGENT_READ_LINKS_LOCKED_v1.md` |
| 6 | Domain index | `os/LOCKED_REFERENCE_INDEX.md` |
| 7 | Boundaries | `PROJECT_BOUNDARIES_LOCKED.md` |

**Skills (`.cursor/skills/`):** SKILL-001 scope · SKILL-006 ask-before-implement · SKILL-007 conflict resolution · SKILL-008 commercial boundary.

**Rules (`.cursor/rules/`):** scope, read-order, ship-first, no-asf-plans, ask-before-edit, self-audit.

---

## 2. Execution authority (what to ship)

| Layer | Canonical | Notes |
|-------|-----------|-------|
| **Next task picker** | `docs/ops/NOETFIELD_PROMPT_PACK_V14_WISE_LOCKED_v1.md` | `make pick-wise` |
| **Quick pick entry** | `docs/ops/plans/no-asf/QUICK_PICK.md` | When founder says PLAN WITH NO ASF |
| **Active sprint** | `os/SHIP_NOW.md` + `os/plan.json` | P0 ship queue |
| **GTM next** | `docs/ops/plans/no-asf/GTM_NEXT.md` | Bounded cloud implement |
| **500 catalog** | `docs/ops/plans/catalog-500.json` | Machine SSOT for WISE ids |

**Superseded pickers:** v12 redesign · v13 SMART · `pick-tier1-smart` (alias → `pick-wise` only).

**1000-plan registries (different jobs):**

| Registry | Path | Use |
|----------|------|-----|
| NF-PLAN grid | `docs/ops/plans/registry.json` | Long-term backlog + status sync |
| nf-1000 library | `os/plan-library/noetfield-1000/` | Locked prompt stubs + `pick-noetfield-no-asf-plan` |
| nf-future stubs | `os/plans/phase-*/` | Legacy phase grid |

`docs/ops/plans/INDEX.md` **1000/1000 done** = registry completeness, **not** “no work left”. Active ship = `plan.json` + `GTM_NEXT`.

---

## 3. Product & commercial

| Domain | Canonical |
|--------|-----------|
| Product truth | `PRODUCT_TRUTH.md` |
| Offerings | `OFFERINGS_LOCKED.md` |
| Commercial SSOT | `docs/strategy/NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md` |
| TLE product | `docs/spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md` |
| GTM 60-day | `docs/strategy/NOETFIELD_GTM_60_DAY_LOCKED_v1.md` |
| Trust Ledger positioning | `docs/strategy/NOETFIELD_TRUST_LEDGER_POSITIONING_LOCKED_v1.2.md` |

---

## 4. WWW & design

| Domain | Canonical |
|--------|-----------|
| Design patterns R1–R25 | `docs/DESIGN_REFERENCE_GOALS_LOCKED_v1.md` |
| **Packaging program (v16)** | `docs/WWW_V16_PACKAGING_PLAN_LOCKED_v1.md` |
| **Tier-1 UI masterplan (v18)** | `docs/WWW_V18_TIER1_UI_MASTERPLAN_LOCKED_v1.md` |
| **Tier-1 UI roadmap (v17)** | `docs/WWW_V17_TIER1_UI_UPGRADES_LOCKED_v1.md` (superseded) |
| Institutional 100-step program | `docs/WWW_V13_INSTITUTIONAL_100_PLAN_LOCKED_v1.md` |
| Stylesheets | `assets/noetfield-www.css` (v16) imports v14 light + v15 ref + v16 packaging |
| Generator | `scripts/rebuild-www-v6.py` (`WWW_VER=16`) |
| Copy SSOT | `docs/GTM_COPYBOOK.md` |
| Inbox routing | `docs/ops/COMMERCIAL_INBOX_PACKAGING_LOCKED_v1.md` |

**Superseded:** `WWW_V12_MASTER_PLAN_LOCKED_v1.md` (historical lane map only).

---

## 5. Governance references

**Canonical library:** `docs/references/` — prefer `*_LOCKED_v1.md` files.

| Doc | Path |
|-----|------|
| Hub | `docs/references/README.md` |
| Sources handbook | `docs/references/GOVERNANCE_SOURCES_HANDBOOK_LOCKED_v1.md` |
| Drift sources | `docs/references/GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md` |
| Blueprints index | `docs/references/GOVERNANCE_DRIFT_BLUEPRINTS_INDEX_LOCKED_v1.md` |

**Redirect only:** `docs/reference/` → use `docs/references/`.

---

## 6. Lane hubs (buyer docs)

| Lane | SSOT |
|------|------|
| Federal | `docs/federal/FEDERAL_GOVERNANCE_PACK_v1.md` |
| MSP | `docs/msp/MSP_GOVERNANCE_PACK_v1.md` |
| SME / Copilot | `docs/strategy/NOETFIELD_COPILOT_SME_SYSTEM_DESIGN_LOCKED_v1.md` |

---

## 7. Roadmaps (do not confuse)

| Doc | Audience |
|-----|----------|
| `docs/ROADMAP.md` | Public horizons |
| `docs/strategy/noetfield-future-path.md` | Product strategy |
| `ops/private/MARKET_SUCCESS_1000_ROADMAP_LOCKED_v3.md` | Founder-only (gitignored) |
| `os/plan.json` | Active engineering tasks |

---

## 8. Private ops (founder machine — gitignored)

| Canonical | Path |
|-----------|------|
| Private agent reference | `ops/private/agent-reference/` |
| Checklists (still in docs/) | `ops/private/docs/GO_LIVE_CHECKLIST.md` · `LEGAL_REVIEW_CHECKLIST.md` |
| Todolist | `ops/private/todolist/NEXT_MOVES.md` |

**Superseded:** `ops/private/docs/*` duplicates → use `agent-reference/`.

---

## 9. Mirrors (read-only — do not edit)

Batch uploads exist in multiple mirrors for cognition layers:

- `docs/SOURCE_OF_TRUTH/uploaded/` — **canonical in git**
- `L2-knowledge/strategy/` — layer mirror
- `Noetfield-All-Documents/uploaded/` — nested mirror

Edit product code and LOCKED docs in primary paths only; do not fork batch content.

---

## 10. Maintenance

After doc moves or picker bumps:

```bash
make verify-doc-ssot
make verify-agent-scope
```

When adding a new LOCKED doc: register in `os/LOCKED_REFERENCE_INDEX.md` and this file § relevant section.
