# nf-mkt-0415 — Fiddler AI · Pricing & packaging

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-pricing
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

Compare Fiddler AI PLG motion (Explainability wedge) vs our onboarding — one adoption fix on `Procurement pack + demo-to-SOW path`

## Implementation extraction

`Fiddler AI · Pricing & packaging` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0415`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `Fiddler AI` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
