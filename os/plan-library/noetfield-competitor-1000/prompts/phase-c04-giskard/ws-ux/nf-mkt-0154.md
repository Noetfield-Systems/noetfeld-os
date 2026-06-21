# nf-mkt-0154 — Giskard · Buyer-visible UX

**Version:** 2 · **Tier:** T1 · **Workstream:** ws-ux
**Stack:** Noetfield · **Competitor row:** 44 · **Phase:** phase-c04-giskard
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Giskard |
| Product | LLM agent testing |
| What they sell | Test AI agents to catch issues before production |
| Who buys | ML and AI QA engineers |
| Pricing | OSS free; Hub contact sales |
| How it runs | Test library in CI; Hub for continuous red-team |
| Source links | https://www.giskard.ai |
| Portfolio lesson | Pre-prod Copilot/agent regression tests |

## Task (High — next sprint parity with competitor)

E2E or glance check: founder can see `Buyer-visible UX` outcome without Terminal; receipt timestamp on disk

## Implementation extraction

`Giskard · Buyer-visible UX` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0154`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `Giskard` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
