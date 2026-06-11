# Sources and verdicts index

**Agent tag:** `NF-CLOUD-AGENT`  
**Use:** Read before picking from GTM_PRIORITY_100 or QUICK_PICK.

---

## Locked strategy & GTM

| Doc | Path | Use in prompts |
|-----|------|----------------|
| GTM 60-day | `docs/strategy/NOETFIELD_GTM_60_DAY_LOCKED_v1.md` | Tier A/B/C fence; ≤3 tasks |
| Trust Ledger positioning | `docs/strategy/NOETFIELD_TRUST_LEDGER_POSITIONING_LOCKED_v1.2.md` | External one-liner |
| Copilot SME design | `docs/strategy/NOETFIELD_COPILOT_SME_SYSTEM_DESIGN_LOCKED_v1.md` | Lane A vs C |
| Governance Sources Book | `docs/references/GOVERNANCE_SOURCES_BOOK_v1.md` | Buyer citations |
| Sources handbook (locked) | `docs/references/GOVERNANCE_SOURCES_HANDBOOK_LOCKED_v1.md` | Diligence reviewers |
| Drift detection sources | `docs/references/GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md` | Continuous governance |

---

## Architecture verdict (GPT / FA synthesis)

| Doc | Path | Verdict summary |
|-----|------|-----------------|
| Postgres-first architecture | `docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-010/noetfield-architecture-verdict-postgres-first-fa.md` | Postgres + append-only audit; ship pilot path first |

**Agent rule:** Do not add scale infra (Kafka, multi-region) until one customer proof.

---

## Drift blueprints (locked, implementation later)

| Doc | Path |
|-----|------|
| Blueprints index | `docs/references/GOVERNANCE_DRIFT_BLUEPRINTS_INDEX_LOCKED_v1.md` |
| Drift engine | `docs/references/GOVERNANCE_DRIFT_ENGINE_BLUEPRINT_LOCKED_v1.md` |
| TLE for drift | `docs/references/TRUST_LEDGER_FOR_DRIFT_BLUEPRINT_LOCKED_v1.md` |
| LLM drift architecture | `docs/references/LLM_DRIFT_DETECTION_ARCHITECTURE_LOCKED_v1.md` |
| Enterprise framework | `docs/references/ENTERPRISE_GOVERNANCE_DRIFT_FRAMEWORK_LOCKED_v1.md` |

---

## Agent ops & critics

| Doc | Path |
|-----|------|
| Agent self-audit loop | `docs/ops/AGENT_SELF_AUDIT_LOOP_LOCKED_v1.md` |
| Agent memory | `.cursor/agent-memory/MEMORY_LOCKED.yaml` |
| Incidents registry | `.cursor/incidents/REGISTRY.md` |
| Doc tagging rule | `docs/ops/AGENT_DOC_TAGGING_LOCKED_v1.md` |

**INCIDENT-2026-06-06-001:** TrustField scope bleed — closed. Noetfield only.

---

## Honest GTM scorecard (founder lock)

| Area | Score |
|------|-------|
| GTM | 4/10 |
| Customer validation | 2/10 |

**Critic insight:** Product is pilot-ready; pack weight must shift to customer acquisition and demo rehearsal, not webhooks/Prometheus.

---

## Model comparison note

Best agent systems (Claude/GPT/Cursor-class) enforce: scope gate → locked memory → single verify bundle → ingest closeout. Noetfield ships all four. Gap is **GTM execution prompts** — this pack adds customer-acquisition, demo-ops, and agent-ops areas.
