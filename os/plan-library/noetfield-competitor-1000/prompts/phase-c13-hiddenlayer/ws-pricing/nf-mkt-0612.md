# nf-mkt-0612 — HiddenLayer · Pricing & packaging

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-pricing
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

## Task (Critical — smallest shippable slice with receipt)

Map HiddenLayer revenue model (Annual enterprise) to our `CAD $2K shadow pilot → annual design partner` tier names — no hidden fees theater

## Implementation extraction

`HiddenLayer · Pricing & packaging` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0612`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `HiddenLayer` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
