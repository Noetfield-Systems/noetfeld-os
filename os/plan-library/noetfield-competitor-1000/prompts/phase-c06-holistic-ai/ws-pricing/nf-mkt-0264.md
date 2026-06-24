# nf-mkt-0264 — Holistic AI · Pricing & packaging

**Version:** 2 · **Tier:** T1 · **Workstream:** ws-pricing
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

Label free vs paid honestly (Copilot audit vocabulary — not SourceA motor wording); never claim production without receipt

## Implementation extraction

`Holistic AI · Pricing & packaging` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0264`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `Holistic AI` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
