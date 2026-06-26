# nf-mkt-0166 — Giskard · Pricing & packaging

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-pricing
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

## Task (Medium — hardening, validator, docs)

Document why buyers pay per Giskard: Copilot plugins fail silently without pre-prod tests — tie to our offer in plain English

## Implementation extraction

`Giskard · Pricing & packaging` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0166`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `Giskard` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
