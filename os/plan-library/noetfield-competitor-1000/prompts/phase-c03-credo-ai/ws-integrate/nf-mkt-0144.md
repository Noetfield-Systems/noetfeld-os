# nf-mkt-0144 — Credo AI · Integrations & API

**Version:** 2 · **Tier:** T1 · **Workstream:** ws-integrate
**Stack:** Noetfield · **Competitor row:** 43 · **Phase:** phase-c03-credo-ai
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Credo AI |
| Product | AI governance platform |
| What they sell | Discover, assess, and govern every AI agent, model, and application continuously |
| Who buys | Fortune 500 and regulated enterprises |
| Pricing | Contact sales; six-figure contracts typical (market) |
| How it runs | AI Registry + Policy Engine + Risk Intelligence |
| Source links | https://www.credo.ai |
| Portfolio lesson | Board-ready audit pack pattern for NW1 Copilot wedge |

## Task (High — next sprint parity with competitor)

Add signed webhook/event/async pattern — no cross-project DB joins

## Implementation extraction

`Credo AI · Integrations & API` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm
```

## Closeout

1. `status: done` in REGISTRY.json for `nf-mkt-0144`
2. Evidence row in `AGENT-AUTO-NOETFIELD` PRIORITY/AUDIT with `Credo AI` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-NOETFIELD
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
