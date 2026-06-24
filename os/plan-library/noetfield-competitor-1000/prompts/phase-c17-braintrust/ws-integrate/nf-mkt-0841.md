# nf-mkt-0841 — Braintrust · Integrations & API

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-integrate
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

List Braintrust integrations/APIs from https://www.braintrust.dev or docs — pick one we can wire this quarter

## Implementation extraction

`Braintrust · Integrations & API` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0841`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `Braintrust` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
