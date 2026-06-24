# nf-mkt-0650 — HiddenLayer · Integrations & API

**Version:** 2 · **Tier:** T3 · **Workstream:** ws-integrate
**Stack:** Noetfield · **Competitor row:** 53 · **Phase:** phase-c13-hiddenlayer
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | HiddenLayer |
| Product | ML security |
| What they sell | Model security and threat detection for AI |
| Who buys | Security operations |
| Pricing | Enterprise custom |
| How it runs | Monitor models; detect adversarial attacks |
| Source links | https://hiddenlayer.com |
| Portfolio lesson | Threat detection on AI apps |

## Task (Low — research, defer note, or compare-only)

Close nf-mkt-0650: integration receipt + verify PASS + https://hiddenlayer.com

## Implementation extraction

`HiddenLayer · Integrations & API` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0650`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `HiddenLayer` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
