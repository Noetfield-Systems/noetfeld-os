# Partner control layer

## What is the Partner Integration Program?

A **program**, not a fourth product. Licensed banks, VASPs, exchanges, and PSPs embed Noetfield's **pre-execution evaluate API** and **Trust Ledger** audit export. Noetfield does not execute trades, hold custody, or operate as an MSB or RPAA registrant.

## How do exchanges integrate?

Partners call `POST /api/v1/governance/evaluate` before their own licensed APIs act. Optional **read-only** operational signals (balances, order status, risk flags) may be ingested — Noetfield never places orders.

## Trust Ledger

Immutable governance compliance log: decisions, policy references, and Request ID (RID) lineage. Export via `/api/v1/governance/audit-export` for vendor due diligence.

## Canada regulation (adjacency)

- **OSFI E-23** (May 2027): third-party AI governance evidence
- **Consumer-Driven Banking**: policy before partner execution — not open-banking write inside Noetfield
- **Stablecoin Act**: governance evidence for issuers/PSPs — Noetfield does not issue stablecoins

## Engagement

Partner intake: `/partners/` or `/gate/intake/?vector=partner-gateway`. Email: operations@noetfield.com with your RID if you have one.
