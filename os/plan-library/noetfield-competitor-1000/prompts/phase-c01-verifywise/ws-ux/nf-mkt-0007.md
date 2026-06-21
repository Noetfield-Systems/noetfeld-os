# nf-mkt-0007 — VerifyWise · Buyer-visible UX

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-ux
**Stack:** Noetfield · **Competitor row:** 41 · **Phase:** phase-c01-verifywise
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | VerifyWise |
| Product | AI governance platform |
| What they sell | Register, assess, govern, and monitor AI systems — EU AI Act, ISO 42001, NIST |
| Who buys | SMB to enterprise compliance teams |
| Pricing | Free start; Enterprise Plus custom — https://verifywise.ai/pricing |
| How it runs | Registry → risk assessment → policy enforcement → audit export |
| Source links | https://verifywise.ai · https://verifywise.ai/pricing |
| Portfolio lesson | AI system inventory + one-click board export for Copilot programs |

## Task (Medium — hardening, validator, docs)

Document who buys (SMB to enterprise compliance teams) vs our ICP one sentence on `os/plan-library/NOETFIELD-PRIORITY.md` row for VerifyWise

## Implementation extraction

`VerifyWise · Buyer-visible UX` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0007`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `VerifyWise` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
