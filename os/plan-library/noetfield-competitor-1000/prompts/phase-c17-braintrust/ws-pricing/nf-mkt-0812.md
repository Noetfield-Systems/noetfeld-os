# nf-mkt-0812 — Braintrust · Pricing & packaging

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-pricing
**Stack:** Noetfield · **Competitor row:** 57 · **Phase:** phase-c17-braintrust
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Braintrust |
| Product | Eval platform |
| What they sell | Evals and logging for AI products in production |
| Who buys | AI product teams |
| Pricing | From ~$249/mo |
| How it runs | Log production; run eval suites; compare versions |
| Source links | https://www.braintrust.dev |
| Portfolio lesson | Board metric: pass rate trend over time |

## Task (Critical — smallest shippable slice with receipt)

Map Braintrust revenue model (Platform + usage) to our `CAD $2K shadow pilot → annual design partner` tier names — no hidden fees theater

## Implementation extraction

`Braintrust · Pricing & packaging` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0812`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `Braintrust` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
