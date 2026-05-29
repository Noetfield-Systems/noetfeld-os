# Source-of-Truth Registry

This registry organizes uploaded Noetfield blueprint documents into a governed
inventory.

## Files

- `source_document_inventory.json` lists every uploaded source document.
- `source_of_truth_registry.json` records active source-of-truth decisions by
  domain.
- `active_rule_candidates.json` extracts design rules that can become active
  runtime policy.

## Current active decisions

- Context Graph: `wp01-context-graph-runtime-edition-v2`
- NPL: `wp03-npl-formal-grammar-2026-05-npl-1`
- Developer OS strategy: `orchestration-policy-layer-source-of-truth-2026`
- Work packages: `developer-os-addendum-work-packages-2026`
- Security Agent: `security-agent-source-persian-normalized` as active
  reference pending formal WP-05 specification
- AI-native development guidelines: `perplexity-ai-native-development-guidelines`
  as architecture reference, with Grok retained as tooling reference
- Operator workflow: `cursor-ide-shortcuts-m5-pro-2026` as reference only
- POSA GTM: `posa-saas-first-100-users-launch-strategy-v1` as external product
  reference only
- POSA system: `posa-v3-0-source-of-truth` as active POSA root SOT
- POSA revenue subsystem: `posa-v3-1-autonomous-revenue-system` as active
  revenue subsystem SOT
- POSA memory subsystem: `posa-digital-twin-training-memory-implementation-v1`
  as active memory subsystem SOT
- Shopify Price Intelligence: `shopify-price-intelligence-system-v1` as a
  separate product reference only
- Personal agent lineage: PAAS v1, PAES v1, and POSA v2 are historical
  predecessors resolved to `posa-v3-0-source-of-truth`
- Context Resonance Theory: `context-resonance-theory-paper` as active
  theoretical reference
- AIE Protocol (normative): `aie-protocol-full-technical-whitepaper` as active protocol SOT
- AIE tokenomics: `aie-protocol-tokenomics-mathematical-model-v1` as active tokenomics SOT
- AIE repo layout: `aie-protocol-full-production-repo-structure` as implementation scaffold reference
- AIE module detail: `aie-protocol-smart-contract-cosmos-architecture` as module reference under the whitepaper
- AIIS platform: `aiis-investor-whitepaper-agentic-intelligence-infrastructure` as separate product lineage
- Agentic systems manifesto: `manifesto-agentic-systems-design` as active theory reference
- Architecture of Meaning book: `architecture-of-meaning-book-proposal` as separate knowledge product only


## Database loading

Apply migrations first:

```bash
make apply-migrations
```

Dry-run inventory load:

```bash
PYTHONPATH=packages/types:packages/config:services/events:services/ledger:services/graph:services/governance:services/signals:services/workflow:services/ai-runtime:services/inspectors:services/identity:services/copilot-governance \
  python3 scripts/ingest_source_inventory.py --dry-run
```

Load into PostgreSQL:

```bash
PYTHONPATH=packages/types:packages/config:services/events:services/ledger:services/graph:services/governance:services/signals:services/workflow:services/ai-runtime:services/inspectors:services/identity:services/copilot-governance \
  DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/noetfield \
  python3 scripts/ingest_source_inventory.py
```

