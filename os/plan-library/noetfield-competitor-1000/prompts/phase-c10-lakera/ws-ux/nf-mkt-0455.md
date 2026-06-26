# nf-mkt-0455 — Lakera · Buyer-visible UX

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-ux
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

## Task (Medium — hardening, validator, docs)

Diff our public copy vs Lakera pricing/product page — list 3 concrete gaps; fix highest P0 gap only

## Implementation extraction

`Lakera · Buyer-visible UX` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0455`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `Lakera` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
