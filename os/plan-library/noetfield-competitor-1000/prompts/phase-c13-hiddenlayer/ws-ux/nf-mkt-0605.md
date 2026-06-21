# nf-mkt-0605 — HiddenLayer · Buyer-visible UX

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-ux
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

## Task (Medium — hardening, validator, docs)

Diff our public copy vs HiddenLayer pricing/product page — list 3 concrete gaps; fix highest P0 gap only

## Implementation extraction

`HiddenLayer · Buyer-visible UX` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0605`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `HiddenLayer` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
