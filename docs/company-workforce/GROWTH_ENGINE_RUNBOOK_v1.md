# Noetfield Company Growth Engine v1 — Runbook

**Status:** Implemented, manual/on-demand only  
**Roles:** N-02 Strategic Intelligence · N-05 Revenue & Partnerships  
**Entry point:** `scripts/noetfield_company_growth_engine_v1.py`  
**State:** SQLite, default ignored path `.noos-runtime/workforce/company-growth-v1.sqlite3`

## What this actually does

1. Reads a short allowlist of public RSS/Atom sources (NIST, GitHub Changelog, OpenAI News, Microsoft Security).
2. Deduplicates source items by publisher + canonical URL and preserves observed source links.
3. Sends selected source items to the existing NOOS T1 model route through OpenRouter when `OPENROUTER_API_KEY` is present.
4. Validates the source registry and model output against JSON Schemas and rejects citations the source item did not supply.
5. Records per-run traces with role ID, source/prompt/output hashes, model, cost reservation, policy decision, and tool-call count. Raw prompts, private reasoning, and credentials are not stored in the trace.
6. Labels every model result as a research signal requiring human review. It cannot create a qualified opportunity automatically.
7. Stores account-level opportunity records in an internal pipeline with deterministic score inputs, evidence references, next actions, and stage-transition gates.
8. Emits machine-readable receipts in the existing `receipts/proof/` evidence surface.

## Current best-practice choices

- Start with one bounded intelligence workflow; do not create a swarm of agents for a single research problem.
- Deterministic ingestion, deduplication, validation, scoring, budget enforcement, and state changes stay in code.
- Model calls are isolated, structured, tool-less, and explicitly treat source content as untrusted data.
- The model cannot contact prospects, create opportunities, claim customer intent, invent budgets, or move a pipeline stage.
- Opportunity scoring returns `insufficient_evidence` when any input is missing; it never silently fills unknowns.
- Pipeline advancement requires evidence of buyer validation, a real meeting reference, documented discovery outcome, scope, success metric, and founder review.
- Closed-won and external-send actions are deliberately not autonomous transitions.
- Model execution follows the existing `config/model-router.yml` T1 route, per-run ceiling, and rolling daily ceiling. A run reserves the T1 per-run cap before making a provider call.
- Pipeline qualification requires confirmed buyer validation, at least two independent source IDs, direct customer evidence (interview/email/meeting note), a Founder approval secret, and a recorded H-001 review note.
- Proposal readiness requires confirmed buyer validation, a verified or approved budget, the proposal draft, and explicit commercial assumptions. It remains a Founder review queue, not an approved external proposal.
- The Founder secret is not stored in the database or evidence bundle.
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

Inspect N-02 traces (metadata and hashes only):

```bash
python3 scripts/noetfield_company_growth_engine_v1.py traces --limit 30 --json
```

Most N-05 pipeline updates are evidence-driven and do not require Founder intervention. The `qualified` transition is different: it asserts that a real buyer, problem, and access path have been validated, so it requires the Founder-controlled environment, `NOETFIELD_PIPELINE_APPROVAL_TOKEN` provisioned by an approved secret manager, and a hidden token prompt. Do not put the token in the evidence file or terminal command. The evidence object must include the required review note and `"reviewer_id": "H-001"`. Marking a proposal `proposal_ready_for_founder_review` only queues it for review; it does not approve or send it.

```bash
python3 scripts/noetfield_company_growth_engine_v1.py opportunity-advance --id opp_ID --to researching --evidence path/to/evidence.json --json
```

Set `NOETFIELD_WORKFORCE_DB` to a durable approved path before using the CLI in another runtime. The database contains internal account/opportunity data and must not be committed to Git.

## Required runtime configuration

- `OPENROUTER_API_KEY`: provider credential in the approved secret store; never in Git, JSON config, agent prompts, or receipt payloads.
- Model identity and pricing are taken only from `config/model-router.yml`. Environment-based model overrides are disabled.
- `NOETFIELD_PIPELINE_APPROVAL_TOKEN`: Founder-only expected secret, provisioned in the approved runtime environment. It is checked against a hidden interactive prompt only when N-05 requests the `qualified` stage. It is never passed on the command line or stored in evidence JSON, SQLite, or receipts.
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
