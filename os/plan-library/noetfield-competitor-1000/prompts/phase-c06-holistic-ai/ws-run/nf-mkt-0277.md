# nf-mkt-0277 — Holistic AI · Run history & proof

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-run
**Stack:** Noetfield · **Competitor row:** 46 · **Phase:** phase-c06-holistic-ai
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Holistic AI |
| Product | AI risk platform |
| What they sell | Enterprise AI risk scoring and governance dashboard |
| Who buys | Chief Risk Officers |
| Pricing | Enterprise custom |
| How it runs | Inventory; risk score; monitor drift |
| Source links | https://www.holisticai.com |
| Portfolio lesson | Copilot use-case risk register |

## Task (Medium — hardening, validator, docs)

Attribute infra vs agent failure class on failed run (Anthropic noise pattern)

## Implementation extraction

`Holistic AI · Run history & proof` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0277`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `Holistic AI` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
