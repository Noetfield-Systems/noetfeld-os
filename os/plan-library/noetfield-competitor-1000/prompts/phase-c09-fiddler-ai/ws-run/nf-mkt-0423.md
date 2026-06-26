# nf-mkt-0423 — Fiddler AI · Run history & proof

**Version:** 2 · **Tier:** T1 · **Workstream:** ws-run
**Stack:** Noetfield · **Competitor row:** 49 · **Phase:** phase-c09-fiddler-ai
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Fiddler AI |
| Product | Model performance management |
| What they sell | Explainability and monitoring for ML models |
| Who buys | ML platform teams |
| Pricing | Enterprise custom |
| How it runs | Explain predictions; monitor drift; report |
| Source links | https://www.fiddler.ai |
| Portfolio lesson | Explainability on high-risk Copilot answers |

## Task (High — next sprint parity with competitor)

Implement smallest `TLE evaluate + drift export + copilot pilot e2e` slice — PASS/FAIL + one step log; mock_only ok with label

## Implementation extraction

`Fiddler AI · Run history & proof` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0423`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `Fiddler AI` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
