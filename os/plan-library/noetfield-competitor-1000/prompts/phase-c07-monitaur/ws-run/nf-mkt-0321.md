# nf-mkt-0321 — Monitaur · Run history & proof

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-run
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

## Task (Critical — smallest shippable slice with receipt)

From https://www.monitaur.ai document Monitaur run/history UX: Document models; approval workflows; audit logs — map to `TLE evaluate + drift export + copilot pilot e2e`

## Implementation extraction

`Monitaur · Run history & proof` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0321`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `Monitaur` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
