# nf-mkt-0354 — Arthur AI · Buyer-visible UX

**Version:** 2 · **Tier:** T1 · **Workstream:** ws-ux
**Stack:** Noetfield · **Competitor row:** 48 · **Phase:** phase-c08-arthur-ai
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Arthur AI |
| Product | AI performance monitoring |
| What they sell | Monitor model and LLM quality, bias, drift |
| Who buys | Model owners |
| Pricing | Enterprise custom |
| How it runs | Ingest outputs; dashboards; alerts |
| Source links | https://www.arthur.ai |
| Portfolio lesson | Drift alerts on Copilot outputs |

## Task (High — next sprint parity with competitor)

E2E or glance check: founder can see `Buyer-visible UX` outcome without Terminal; receipt timestamp on disk

## Implementation extraction

`Arthur AI · Buyer-visible UX` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0354`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `Arthur AI` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
