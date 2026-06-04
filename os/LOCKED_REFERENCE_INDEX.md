# Locked reference index (Noetfield)

| ID | Document | Use when |
|----|----------|----------|
| **`agent-read-links-v1`** | [docs/ops/AGENT_READ_LINKS_LOCKED_v1.md](../docs/ops/AGENT_READ_LINKS_LOCKED_v1.md) | **Full index** — hub :13020, mandatory chain 1–14, every repo separate, local vs cloud |
| **`agent-context-v1`** | [docs/ops/NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md](../docs/ops/NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md) | Ship/ingest rules, cloud vs local, diagnostics |
| **`trust-ledger-positioning-v1.2`** | [docs/strategy/NOETFIELD_TRUST_LEDGER_POSITIONING_LOCKED_v1.2.md](../docs/strategy/NOETFIELD_TRUST_LEDGER_POSITIONING_LOCKED_v1.2.md) | **Primary GTM + product direction** — TLE mandate, 60-day sprint |
| **`gtm-60-day-v1`** | [docs/strategy/NOETFIELD_GTM_60_DAY_LOCKED_v1.md](../docs/strategy/NOETFIELD_GTM_60_DAY_LOCKED_v1.md) | **CEO focus** — 1 customer, 5-min demo, 60-day fence, time allocation |
| **`governance-sources-book-v1`** | [docs/reference/GOVERNANCE_SOURCES_BOOK_v1.md](../docs/reference/GOVERNANCE_SOURCES_BOOK_v1.md) | **Citable frameworks** — NIST, OECD, ISO, EU AI Act, Microsoft, OWASP |
| **`governance-drift-sources-v1`** | [docs/reference/GOVERNANCE_DRIFT_DETECTION_SOURCES_v1.md](../docs/reference/GOVERNANCE_DRIFT_DETECTION_SOURCES_v1.md) | **Drift detection** — control/policy/config/model/agent drift, monitoring sources |
| `copilot-sme-system-design-v1` | [docs/strategy/NOETFIELD_COPILOT_SME_SYSTEM_DESIGN_LOCKED_v1.md](../docs/strategy/NOETFIELD_COPILOT_SME_SYSTEM_DESIGN_LOCKED_v1.md) | SME Copilot full architecture; Lane A vs B/C boundary analysis at top |
| Sprint backlog | [os/sprint-trust-ledger-v1.2.md](./sprint-trust-ledger-v1.2.md) | P0–P1 stories and dependency order |
| TLE schema + samples | [packages/schemas/tle-v1.schema.json](../packages/schemas/tle-v1.schema.json) · [docs/spec/samples/](../docs/spec/samples/) | Engineering handoff |
| TLE OpenAPI | [docs/spec/openapi/tle-v1.openapi.yaml](../docs/spec/openapi/tle-v1.openapi.yaml) | API implementation |
| MVP requirements | [os/plan.json](./plan.json) | Active tasks and done criteria |
| Tenant audit schema | [docs/spec/tenant-append-only-audit-schema-outline.md](../docs/spec/tenant-append-only-audit-schema-outline.md) | Phase 1B data model |
| TrustField conflict matrix | [docs/spec/trustfield-noetfield-conflict-matrix.md](../docs/spec/trustfield-noetfield-conflict-matrix.md) | Corpus vs product boundary |
| Phase 1B activation | [docs/spec/phase-1b-activation-checklist.md](../docs/spec/phase-1b-activation-checklist.md) | Migration gate |
| Copilot control catalog | [docs/spec/copilot-control-catalog.md](../docs/spec/copilot-control-catalog.md) | QuickScan / Readiness tests |
| Pilot runbook | [docs/spec/copilot-readiness-pilot-runbook.md](../docs/spec/copilot-readiness-pilot-runbook.md) | Design-partner E2E |
| Product truth | [PRODUCT_TRUTH.md](../PRODUCT_TRUTH.md) | Scope gate (no payments) |

**Rule:** Read the analysis section in each LOCKED doc before implementing. One task per ASF implement turn.
