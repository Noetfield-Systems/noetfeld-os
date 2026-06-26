# nf-mkt-0947 — OneTrust · Integrations & API

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-integrate
**Stack:** Noetfield · **Competitor row:** 59 · **Phase:** phase-c19-onetrust
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | OneTrust |
| Product | Privacy + AI governance |
| What they sell | Privacy, GRC, and AI governance modules |
| Who buys | Privacy and GRC leaders |
| Pricing | Enterprise custom |
| How it runs | DPIA; AI use register; policy workflows |
| Source links | https://www.onetrust.com |
| Portfolio lesson | DPIA + AI use register (pattern) |

## Task (Medium — hardening, validator, docs)

Rate-limit + retry policy copied from OneTrust operating model (DPIA; AI use register; policy workflows)

## Implementation extraction

`OneTrust · Integrations & API` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0947`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `OneTrust` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
