# nf-mkt-0590 — Cranium · Onboarding & PLG

**Version:** 2 · **Tier:** T3 · **Workstream:** ws-onboard
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

Close nf-mkt-0590 with onboarding evidence + verify PASS

## Implementation extraction

`Cranium · Onboarding & PLG` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0590`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `Cranium` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
