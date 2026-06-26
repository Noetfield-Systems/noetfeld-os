# nf-mkt-0244 — Promptfoo · Integrations & API

**Version:** 2 · **Tier:** T1 · **Workstream:** ws-integrate
**Stack:** Noetfield · **Competitor row:** 45 · **Phase:** phase-c05-promptfoo
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Promptfoo |
| Product | LLM security eval |
| What they sell | Red-team and eval prompts, agents, RAG in CI |
| Who buys | DevSec and platform teams |
| Pricing | Community free; enterprise custom |
| How it runs | CLI matrix evals; 50+ attack plugins |
| Source links | https://www.promptfoo.dev |
| Portfolio lesson | Microsoft Copilot plugin eval gate in CI |

## Task (High — next sprint parity with competitor)

Add signed webhook/event/async pattern — no cross-project DB joins

## Implementation extraction

`Promptfoo · Integrations & API` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0244`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `Promptfoo` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
