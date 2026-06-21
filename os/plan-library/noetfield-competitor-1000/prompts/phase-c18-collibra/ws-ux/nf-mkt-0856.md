# nf-mkt-0856 — Collibra · Buyer-visible UX

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-ux
**Stack:** Noetfield · **Competitor row:** 58 · **Phase:** phase-c18-collibra
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Collibra |
| Product | Data + AI governance |
| What they sell | Data governance extended to AI assets |
| Who buys | Data governance teams |
| Pricing | Enterprise custom |
| How it runs | Catalog data and AI; lineage; policy |
| Source links | https://www.collibra.com |
| Portfolio lesson | Data lineage on AI outputs (pattern) |

## Task (Medium — hardening, validator, docs)

Add `TLE evaluate + drift export + copilot pilot e2e` mock row labeled mock_only until live — match Collibra run/history metaphor not invented name

## Implementation extraction

`Collibra · Buyer-visible UX` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0856`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `Collibra` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
