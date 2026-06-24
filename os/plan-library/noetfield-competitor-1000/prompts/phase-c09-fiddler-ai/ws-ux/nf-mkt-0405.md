# nf-mkt-0405 — Fiddler AI · Buyer-visible UX

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-ux
**Stack:** Noetfield · **Competitor row:** 49 · **Phase:** phase-c09-fiddler-ai
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Fiddler AI |
| Product | Model performance management |
| What they sell | Explainability and monitoring for ML models |
| Who buys | ML platform teams |
| Pricing | Enterprise custom |
| How it runs | Explain predictions; monitor drift; report |
| Source links | https://www.fiddler.ai |
| Portfolio lesson | Explainability on high-risk Copilot answers |

## Task (Medium — hardening, validator, docs)

Diff our public copy vs Fiddler AI pricing/product page — list 3 concrete gaps; fix highest P0 gap only

## Implementation extraction

`Fiddler AI · Buyer-visible UX` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0405`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `Fiddler AI` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
