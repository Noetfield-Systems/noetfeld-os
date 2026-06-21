# nf-mkt-0069 — FairNow · Pricing & packaging

**Version:** 2 · **Tier:** T3 · **Workstream:** ws-pricing
**Stack:** Noetfield · **Competitor row:** 42 · **Phase:** phase-c02-fairnow
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | FairNow |
| Product | AI governance & compliance |
| What they sell | Centralize AI inventory, automate risk assessments and compliance workflows |
| Who buys | Enterprise compliance in financial services and HR |
| Pricing | Contact sales; no public pricing |
| How it runs | AI registry; automated bias tests; evidence collection |
| Source links | https://www.fairnow.ai |
| Portfolio lesson | Automated evidence collection for board packs |

## Task (Low — research, defer note, or compare-only)

Write competitor row evidence: FairNow pricing → our SKU → defer/shipped with path

## Implementation extraction

`FairNow · Pricing & packaging` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0069`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `FairNow` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
