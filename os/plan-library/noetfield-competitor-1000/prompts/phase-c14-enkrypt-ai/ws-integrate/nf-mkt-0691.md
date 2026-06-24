# nf-mkt-0691 — Enkrypt AI · Integrations & API

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-integrate
**Stack:** Noetfield · **Competitor row:** 54 · **Phase:** phase-c14-enkrypt-ai
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Enkrypt AI |
| Product | LLM firewall |
| What they sell | Secure gateway for LLM applications |
| Who buys | Security teams |
| Pricing | Startup tiers |
| How it runs | Proxy LLM calls; policy enforcement log |
| Source links | https://www.enkryptai.com |
| Portfolio lesson | Policy enforcement log per call |

## Task (Critical — smallest shippable slice with receipt)

List Enkrypt AI integrations/APIs from https://www.enkryptai.com or docs — pick one we can wire this quarter

## Implementation extraction

`Enkrypt AI · Integrations & API` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0691`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `Enkrypt AI` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
