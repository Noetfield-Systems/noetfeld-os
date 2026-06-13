# Noetfield documentation hub

**Start here.** One router — no hunting across folders.

| I need… | Go to |
|---------|--------|
| **Full SSOT map (agents + humans)** | [DOC_UNIFIED_INDEX_LOCKED_v1.md](./DOC_UNIFIED_INDEX_LOCKED_v1.md) |
| **Domain index (lanes, product, www)** | [../os/LOCKED_REFERENCE_INDEX.md](../os/LOCKED_REFERENCE_INDEX.md) |
| **Agent session read order** | [ops/NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md](./ops/NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md) |
| **Agent link chain (1–14)** | [ops/AGENT_READ_LINKS_LOCKED_v1.md](./ops/AGENT_READ_LINKS_LOCKED_v1.md) |
| **Memory + incidents** | [../.cursor/README.md](../.cursor/README.md) · [../.cursor/agent-memory/MEMORY_LOCKED.yaml](../.cursor/agent-memory/MEMORY_LOCKED.yaml) · [../.cursor/incidents/REGISTRY.md](../.cursor/incidents/REGISTRY.md) |
| **Pick next task (no ASF)** | [ops/plans/no-asf/QUICK_PICK.md](./ops/plans/no-asf/QUICK_PICK.md) → `make pick-wise` |
| **Active ship queue** | [../os/SHIP_NOW.md](../os/SHIP_NOW.md) · [../os/plan.json](../os/plan.json) |
| **Commercial / SKUs** | [strategy/NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md](./strategy/NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md) · [../OFFERINGS_LOCKED.md](../OFFERINGS_LOCKED.md) |
| **WWW / UI design** | [DESIGN_REFERENCE_GOALS_LOCKED_v1.md](./DESIGN_REFERENCE_GOALS_LOCKED_v1.md) · [WWW_V13_INSTITUTIONAL_100_PLAN_LOCKED_v1.md](./WWW_V13_INSTITUTIONAL_100_PLAN_LOCKED_v1.md) |
| **Governance / drift refs** | [references/README.md](./references/README.md) |
| **Product / TLE spec** | [spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md](./spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md) |
| **Public roadmap** | [ROADMAP.md](./ROADMAP.md) |
| **Local dev** | [LOCAL_DEV.md](./LOCAL_DEV.md) |

## Subdirectories

| Dir | Role |
|-----|------|
| `ops/` | Agent locks, prompt packs, plan registry |
| `strategy/` | GTM, commercial, lane strategy |
| `spec/` | Product engineering specs |
| `references/` | **Canonical** governance/drift library (`reference/` is redirect-only) |
| `federal/` · `msp/` · `copilot/` | Lane buyer docs |
| `api/` | OpenAPI and partner API docs |
| `SOURCE_OF_TRUTH/` | Constitutional uploads (archived batches) |

## Superseded (reference only)

| Doc | Use instead |
|-----|-------------|
| `WWW_V12_MASTER_PLAN_LOCKED_v1.md` | `WWW_V13_INSTITUTIONAL_100_PLAN_LOCKED_v1.md` |
| `NOETFIELD_PROMPT_PACK_V12_*` · `V13_SMART_*` | `NOETFIELD_PROMPT_PACK_V14_WISE_LOCKED_v1.md` |
| `docs/reference/*` | `docs/references/*_LOCKED_v1.md` |
| `OFFERINGS.md` | `OFFERINGS_LOCKED.md` |

**Verify:** `make verify-doc-ssot`
