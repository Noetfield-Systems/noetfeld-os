# Noetfield Company Growth Engine v1 — Runbook

**Status:** Implemented, manual/on-demand only  
**Roles:** N-02 Strategic Intelligence · N-05 Revenue & Partnerships  
**Entry point:** `scripts/noetfield_company_growth_engine_v1.py`  
**State:** SQLite, default ignored path `.noos-runtime/workforce/company-growth-v1.sqlite3`

## What this actually does

1. Reads a short allowlist of public RSS/Atom sources (NIST, GitHub Changelog, OpenAI News, Microsoft Security).
2. Deduplicates source items by publisher + canonical URL and preserves observed source links.
3. Sends selected source items to the existing NOOS T1 model route through OpenRouter when `OPENROUTER_API_KEY` is present.
4. Validates model output against a JSON Schema and rejects citations the source item did not supply.
5. Labels every model result as a research signal requiring human review. It cannot create a qualified opportunity automatically.
6. Stores account-level opportunity records in an internal pipeline with deterministic score inputs, evidence references, next actions, and stage-transition gates.
7. Emits machine-readable receipts in the existing `receipts/proof/` evidence surface.

## Current best-practice choices

- Start with one bounded intelligence workflow; do not create a swarm of agents for a single research problem.
- Deterministic ingestion, deduplication, validation, scoring, budget enforcement, and state changes stay in code.
- Model calls are isolated, structured, tool-less, and explicitly treat source content as untrusted data.
- The model cannot contact prospects, create opportunities, claim customer intent, invent budgets, or move a pipeline stage.
- Opportunity scoring returns `insufficient_evidence` when any input is missing; it never silently fills unknowns.
- Pipeline advancement requires evidence of buyer validation, a real meeting reference, documented discovery outcome, scope, success metric, and founder review.
- Closed-won and external-send actions are deliberately not autonomous transitions.
- Model execution follows the existing `config/model-router.yml` T1 route, per-run ceiling, and rolling daily ceiling. A run reserves the T1 per-run cap before making a provider call.
- Feed redirects, non-HTTPS URLs, unapproved domains, IP-literal URLs, non-public DNS results, oversized payloads, DTDs, and XML entity declarations are rejected.
- The local database is idempotent and lives in a gitignored runtime directory. Do not run it from an ephemeral container and call it persistent.

## Commands

Validate sources and schemas without network or model calls:

```bash
python3 scripts/noetfield_company_growth_engine_v1.py validate --json
```

Ingest the allowlisted RSS feeds (this command performs outbound GET requests to those sources):

```bash
python3 scripts/noetfield_company_growth_engine_v1.py fetch --json
```

Analyze up to ten new signals with the configured T1 model (requires `OPENROUTER_API_KEY`):

```bash
python3 scripts/noetfield_company_growth_engine_v1.py analyze --limit 10 --json
```

List source signals and reviewed analysis:

```bash
python3 scripts/noetfield_company_growth_engine_v1.py signals --limit 30 --json
```

Create an opportunity from an internally validated JSON record:

```bash
python3 scripts/noetfield_company_growth_engine_v1.py opportunity-add --record path/to/opportunity.json --json
```

List the revenue pipeline:

```bash
python3 scripts/noetfield_company_growth_engine_v1.py opportunities --json
```

Advance a record only with a JSON evidence object satisfying the transition gate:

```bash
python3 scripts/noetfield_company_growth_engine_v1.py opportunity-advance --id opp_ID --to researching --evidence path/to/evidence.json --json
```

Set `NOETFIELD_WORKFORCE_DB` to a durable approved path before using the CLI in another runtime. The database contains internal account/opportunity data and must not be committed to Git.

## Required runtime configuration

- `OPENROUTER_API_KEY`: provider credential in the approved secret store; never in Git, JSON config, agent prompts, or receipt payloads.
- Optional `OPENROUTER_MODEL`: overrides the T1 model only when accompanied by `OPENROUTER_MODEL_MAX_USD_PER_1K_TOKENS`; otherwise blocked.
- `NOETFIELD_WORKFORCE_DB`: durable SQLite path or future approved database mount.

No credentials were provisioned as part of this change. A missing key causes analysis to return `BLOCKED`; the system does not fall back to fake model output.

## Why there is no scheduled job yet

The default store is local SQLite and the current NOOS worker-kernel T1 path has historically been stubbed. The live intelligence provider adapter is now implemented, but no durable shared database or approved secret binding was verified for the hosted runtime. A recurring job would lose state on ephemeral storage and could repeatedly ingest/analyze duplicate items. Keep this on-demand until a persistent store and secret path are validated; then schedule the deterministic fetch and bounded analysis through existing NOOS loops, not a new scheduler.

## Explicitly out of scope

- CRM/email/calendar/helpdesk connectors.
- Prospect contact scraping or personal-data enrichment.
- Automated outbound communication, marketing publication, proposals, pricing, contracts, or payments.
- Automatic qualification, pipeline stage advancement, or closed-won claims from model output.
- Public product marketing or claims that this engine is a customer-facing SaaS product.
