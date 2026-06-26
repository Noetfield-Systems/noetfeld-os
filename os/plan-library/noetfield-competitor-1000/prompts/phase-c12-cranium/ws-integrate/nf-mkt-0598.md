# nf-mkt-0598 — Cranium · Integrations & API

**Version:** 2 · **Tier:** T3 · **Workstream:** ws-integrate
**Stack:** Noetfield · **Competitor row:** 52 · **Phase:** phase-c12-cranium
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Cranium |
| Product | AI security platform |
| What they sell | AI asset visibility and third-party AI risk |
| Who buys | Security teams |
| Pricing | Enterprise custom |
| How it runs | Discover AI assets; assess vendor AI risk |
| Source links | https://cranium.ai |
| Portfolio lesson | Third-party AI inventory |

## Task (Low — research, defer note, or compare-only)

Validate adapter with one fixture test or validator script

## Implementation extraction

`Cranium · Integrations & API` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0598`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `Cranium` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
