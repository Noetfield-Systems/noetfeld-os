# nf-mkt-0766 — Langfuse · Pricing & packaging

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-pricing
**Stack:** Noetfield · **Competitor row:** 56 · **Phase:** phase-c16-langfuse
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Langfuse |
| Product | LLM observability |
| What they sell | Traces, evals, prompts for LLM applications |
| Who buys | AI engineering |
| Pricing | Free 50k obs; Core $29/mo — https://langfuse.com/pricing |
| How it runs | OpenTelemetry traces; session tracking; cost dashboard |
| Source links | https://langfuse.com/pricing |
| Portfolio lesson | Per-action audit trail for Copilot runs |

## Task (Medium — hardening, validator, docs)

Document why buyers pay per Langfuse: Can't audit Copilot without per-action trail — tie to our offer in plain English

## Implementation extraction

`Langfuse · Pricing & packaging` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0766`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `Langfuse` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
