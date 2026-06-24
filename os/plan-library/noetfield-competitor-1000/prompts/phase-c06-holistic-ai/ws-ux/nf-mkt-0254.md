# nf-mkt-0254 — Holistic AI · Buyer-visible UX

**Version:** 2 · **Tier:** T1 · **Workstream:** ws-ux
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

## Task (High — next sprint parity with competitor)

E2E or glance check: founder can see `Buyer-visible UX` outcome without Terminal; receipt timestamp on disk

## Implementation extraction

`Holistic AI · Buyer-visible UX` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0254`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `Holistic AI` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
