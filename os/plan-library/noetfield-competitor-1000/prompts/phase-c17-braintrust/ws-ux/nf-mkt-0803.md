# nf-mkt-0803 — Braintrust · Buyer-visible UX

**Version:** 2 · **Tier:** T1 · **Workstream:** ws-ux
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

## Task (High — next sprint parity with competitor)

Add `Noetfield NW1 Copilot governance + board pack` UI field or copy block implementing smallest slice of `Board metric: pass rate trend over time`; preserve honest tier label

## Implementation extraction

`Braintrust · Buyer-visible UX` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0803`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `Braintrust` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
