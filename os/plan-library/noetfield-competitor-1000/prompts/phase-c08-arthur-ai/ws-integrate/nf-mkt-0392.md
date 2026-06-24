# nf-mkt-0392 — Arthur AI · Integrations & API

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-integrate
**Stack:** Noetfield · **Competitor row:** 48 · **Phase:** phase-c08-arthur-ai
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Arthur AI |
| Product | AI performance monitoring |
| What they sell | Monitor model and LLM quality, bias, drift |
| Who buys | Model owners |
| Pricing | Enterprise custom |
| How it runs | Ingest outputs; dashboards; alerts |
| Source links | https://www.arthur.ai |
| Portfolio lesson | Drift alerts on Copilot outputs |

## Task (Critical — smallest shippable slice with receipt)

Spec `M365/Google evidence connectors` contract: input → policy gate → output + receipt

## Implementation extraction

`Arthur AI · Integrations & API` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0392`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `Arthur AI` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
