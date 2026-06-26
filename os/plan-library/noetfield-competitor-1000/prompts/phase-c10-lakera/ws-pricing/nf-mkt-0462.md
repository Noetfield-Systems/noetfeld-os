# nf-mkt-0462 — Lakera · Pricing & packaging

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-pricing
**Stack:** Noetfield · **Competitor row:** 50 · **Phase:** phase-c10-lakera
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Lakera |
| Product | LLM firewall |
| What they sell | Runtime security for GenAI applications |
| Who buys | AppSec teams |
| Pricing | Enterprise custom |
| How it runs | API guard scans prompts; block/allow log |
| Source links | https://www.lakera.ai |
| Portfolio lesson | Block/allow log per prompt at dispatch |

## Task (Critical — smallest shippable slice with receipt)

Map Lakera revenue model (API + enterprise) to our `CAD $2K shadow pilot → annual design partner` tier names — no hidden fees theater

## Implementation extraction

`Lakera · Pricing & packaging` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0462`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `Lakera` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
