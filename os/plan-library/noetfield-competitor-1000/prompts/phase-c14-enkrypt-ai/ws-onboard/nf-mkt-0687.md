# nf-mkt-0687 — Enkrypt AI · Onboarding & PLG

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-onboard
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

## Task (Medium — hardening, validator, docs)

Measure drop-off: list one friction point vs Enkrypt AI and fix

## Implementation extraction

`Enkrypt AI · Onboarding & PLG` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0687`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `Enkrypt AI` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
