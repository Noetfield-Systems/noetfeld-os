# nf-mkt-0771 — Langfuse · Run history & proof

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-run
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

## Task (Critical — smallest shippable slice with receipt)

From https://langfuse.com/pricing document Langfuse run/history UX: OpenTelemetry traces; session tracking; cost dashboard — map to `TLE evaluate + drift export + copilot pilot e2e`

## Implementation extraction

`Langfuse · Run history & proof` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0771`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `Langfuse` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
