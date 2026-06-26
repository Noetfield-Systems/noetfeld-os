# nf-mkt-0805 — Braintrust · Buyer-visible UX

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-ux
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

## Task (Medium — hardening, validator, docs)

Diff our public copy vs Braintrust pricing/product page — list 3 concrete gaps; fix highest P0 gap only

## Implementation extraction

`Braintrust · Buyer-visible UX` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0805`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `Braintrust` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
