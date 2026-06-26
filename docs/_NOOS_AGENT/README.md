# NOOS Agent Document Vault

<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-VAULT-README
doc_type: AGENT_VAULT_INDEX
workspace_root: /Users/sinakazemnezhad/Projects/noetfeld-os
-->

**Owner:** This Cursor chat agent only (`noetfeld-os-cursor-chat`)  
**Repo:** `Projects/noetfeld-os`  
**Search token:** `NOOS-AGENT-DOC`

---

## Rule for all agents

1. **Only documents in `docs/_NOOS_AGENT/` with a `NOOS-AGENT-DOC` block belong to this chat agent.**
2. **Do not edit, merge, or overwrite tagged files from another agent lane** (e.g. `NFRT-AGENT-DOC`, SourceA locks, mono SSOT).
3. **Every new doc from this agent must include:**
   - HTML comment block: `NOOS-AGENT-DOC` + `trace_id`
   - Filename prefix: `[NOOS-AGENT-YYYYMMDD-NNN]_`
   - Entry in `MANIFEST.json`
4. **Trace IDs** are monotonic per day: `NOOS-AGENT-20260529-001`, `-002`, etc.

---

## Tag block template (copy into every doc)

```html
<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-YYYYMMDD-NNN
doc_type: INTERNAL_AGENT_REFERENCE | PRODUCT_NOTE | RUNBOOK
workspace_root: /Users/sinakazemnezhad/Projects/noetfeld-os
classification: INTERNAL
related_code: policy_loader.py, decision_engine.py
-->
```

---

## Document index

See `MANIFEST.json` for machine-readable trace registry.

| trace_id | file | summary |
|----------|------|---------|
| `NOOS-AGENT-20260608-005` | `[NOOS-AGENT-20260608-005]_ORIENTATION_START_HERE.md` | **Start here every session** |
| `NOOS-AGENT-20260615-006` | `[NOOS-AGENT-20260615-006]_NINETY_DAY_EXECUTION_PLAN.md` | **Active 90-day plan** |
| `NOOS-AGENT-20260529-002` | `[NOOS-AGENT-20260529-002]_BUSINESS_PRODUCT_CLIENT_DEFINITION.md` | Business, product & ICP |
| `NOOS-AGENT-20260615-007` | `[NOOS-AGENT-20260615-007]_GLOSSARY_AND_PLANE_TAGS.md` | GEL glossary + plane tags |
| `NOOS-AGENT-20260615-008` | `[NOOS-AGENT-20260615-008]_GEL_WEB_URL_STRUCTURE.md` | noetfield.com/gel draft IA |
| `NOOS-AGENT-20260615-009` | `[NOOS-AGENT-20260615-009]_PITCH_ALIGNMENT_NOTES.md` | PDF/pitch drift flags |
| `NOOS-AGENT-20260615-010` | `[NOOS-AGENT-20260615-010]_BUSINESS_STRATEGY_PROOF_DENSITY_v1.md` | **Proof-density commercial strategy (2 PAGER merged)** |
| `NOOS-AGENT-20260615-011` | `[NOOS-AGENT-20260615-011]_FOUNDING_PILOT_ONEPAGER_EXTERNAL_v1.md` | **NW1 Copilot buyer one-pager** |
| `NOOS-AGENT-20260615-013` | `[NOOS-AGENT-20260615-013]_FOUNDING_PILOT_ONEPAGER_AGENTS_v1.md` | **SW1 agents buyer one-pager** |
| `NOOS-AGENT-20260615-012` | `[NOOS-AGENT-20260615-012]_CHAIN_TOOLS_STRATEGY_v1.md` | Chain tools (noetfield-gate) |
| `NOOS-AGENT-20260615-014` | `[NOOS-AGENT-20260615-014]_UPGRADE_PLAN_300_STEPS_v1.md` | **300-step upgrade plan (UPG-0001–0300)** |
| `NOOS-AGENT-20260608-004` | `[NOOS-AGENT-20260608-004]_ROADMAP_1000_STEPS_10_PHASES.md` | 1000-step roadmap |

---

## Relationship to other planes

| Plane | Authority | This vault |
|-------|-----------|------------|
| DESIGN | `Desktop/sourceA/SINA_OS_SSOT_LOCKED.md` | Subordinate — cites, does not override |
| DELIVERY | This repo code + tagged agent docs | **Canonical for this agent's written output** |
| Other agents | `NFRT-AGENT-DOC`, etc. | Separate — search by tag, do not mix |

---

*Other agents: grep `NOOS-AGENT-DOC` in this repo before assuming doc ownership.*
