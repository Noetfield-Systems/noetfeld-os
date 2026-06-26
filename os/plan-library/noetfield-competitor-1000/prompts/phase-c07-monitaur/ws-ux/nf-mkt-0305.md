# nf-mkt-0305 — Monitaur · Buyer-visible UX

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-ux
**Stack:** Noetfield · **Competitor row:** 47 · **Phase:** phase-c07-monitaur
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Monitaur |
| Product | ML governance |
| What they sell | End-to-end ML governance lifecycle |
| Who buys | Regulated industries |
| Pricing | Enterprise custom |
| How it runs | Document models; approval workflows; audit logs |
| Source links | https://www.monitaur.ai |
| Portfolio lesson | Approval workflow per AI system |

## Task (Medium — hardening, validator, docs)

Diff our public copy vs Monitaur pricing/product page — list 3 concrete gaps; fix highest P0 gap only

## Implementation extraction

`Monitaur · Buyer-visible UX` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0305`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `Monitaur` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
