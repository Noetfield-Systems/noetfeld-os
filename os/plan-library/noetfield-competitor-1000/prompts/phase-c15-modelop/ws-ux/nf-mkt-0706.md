# nf-mkt-0706 — ModelOp · Buyer-visible UX

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-ux
**Stack:** Noetfield · **Competitor row:** 55 · **Phase:** phase-c15-modelop
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | ModelOp |
| Product | Model governance |
| What they sell | Enterprise AI governance for banks and insurance |
| Who buys | Bank/insurance compliance |
| Pricing | Enterprise custom |
| How it runs | Model inventory; governance workflows; reporting |
| Source links | https://www.modelop.com |
| Portfolio lesson | Enterprise AI registry pattern |

## Task (Medium — hardening, validator, docs)

Add `TLE evaluate + drift export + copilot pilot e2e` mock row labeled mock_only until live — match ModelOp run/history metaphor not invented name

## Implementation extraction

`ModelOp · Buyer-visible UX` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0706`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `ModelOp` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
