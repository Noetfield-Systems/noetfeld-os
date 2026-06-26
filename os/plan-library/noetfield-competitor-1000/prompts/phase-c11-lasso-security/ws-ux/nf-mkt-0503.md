# nf-mkt-0503 — Lasso Security · Buyer-visible UX

**Version:** 2 · **Tier:** T1 · **Workstream:** ws-ux
**Stack:** Noetfield · **Competitor row:** 51 · **Phase:** phase-c11-lasso-security
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Lasso Security |
| Product | GenAI security |
| What they sell | Shadow AI discovery and GenAI app protection |
| Who buys | CISO |
| Pricing | Custom tiers |
| How it runs | Scan enterprise; policy enforcement |
| Source links | https://www.lasso.security |
| Portfolio lesson | Shadow Copilot discovery for NW1 |

## Task (High — next sprint parity with competitor)

Add `Noetfield NW1 Copilot governance + board pack` UI field or copy block implementing smallest slice of `Shadow Copilot discovery for NW1`; preserve honest tier label

## Implementation extraction

`Lasso Security · Buyer-visible UX` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0503`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `Lasso Security` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
