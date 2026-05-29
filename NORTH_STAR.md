# Noetfield North Star

**Status:** Production alignment constitution · **Supremacy:** GCIP v4 (L0) overrides all documents, code comments, marketing copy, and partner decks on conflict.

**Public product sentence (locked):** see [PRODUCT_TRUTH.md](PRODUCT_TRUTH.md). **Revenue tiers:** [OFFERINGS_LOCKED.md](OFFERINGS_LOCKED.md). **Strategic boundaries:** [STRATEGIC_LOCK.md](STRATEGIC_LOCK.md).

## What Noetfield is

Noetfield is **Governance Execution & AI Policy Enforcement Infrastructure** for regulated organizations (pre-execution layer for institutional AI systems and enterprise workflows).

It is a **coordination and instruction layer** that:

- structures intent and workflow metadata before external execution;
- applies policy and compliance logic deterministically;
- produces audit-ready decision traces and governance signals;
- reduces governance latency and manual pre-execution friction.

## What Noetfield is not

Noetfield does **not**:

- hold, custody, or control funds or stored value;
- initiate, authorize, route, or execute payments or transfers;
- perform settlement, FX execution, or transaction processing;
- operate as a PSP, money transmitter, wallet, or financial intermediary;
- select how money moves (no corridor routing product).

All value movement, conversion, and settlement are performed exclusively by **licensed third-party institutions** when a customer uses those institutions directly.

## Core principle

> **Noetfield never touches value—only policy, compliance logic, and traceability about decisions that may later be executed elsewhere.**

## Managed domains (in scope)

| Domain | Description |
|--------|-------------|
| **Policy** | Institution-configurable rules, guardrails, prohibited actions |
| **Compliance logic** | Pre-execution validation, human-review gates, veto boundaries |
| **Decision traceability** | Immutable audit lineage, Request ID (RID) continuity |
| **Governance latency** | STP preparation, shadow-run parity, evidence packaging |

## Revenue-ready offerings (public GTM)

Only these three are **contractable** public offerings:

1. **Trust Brief** — 6-week governance audit + AI risk mapping engagement  
2. **Copilot Readiness Pack** — enterprise AI compliance + policy alignment (M365 Copilot)  
3. **Bank Pilot v6.1** — read-only visibility + governance overlay (no execution authority)

See [OFFERINGS.md](OFFERINGS.md) for scope boundaries.

## Document hierarchy (L0 → L5)

| Layer | Authority |
|-------|-----------|
| **L0** | `noetfield-constitution-gcip-v4` — constitutional law |
| **L1** | Product kernel annex v4 EN — commercial expression under L0 |
| **Corporate copy** | `noetfield-corporate-definition-governance-v2-1` — partner/grant language |
| **Bank SME** | SME visibility read-only pilot blueprint |
| **Bank enterprise** | Enterprise bank pilot brief v6.1 |
| **v3 MVP** | Separate product track — linear orchestration demo (not L0 identity) |
| **AI OS target** | Control plane spec — roadmap only |

## FINAL LOCK public semantics (GTM)

| Do not use | Use instead |
|------------|-------------|
| routing (sales/intake) | governance flow · lane assignment |
| procurement (visible copy) | engagement intake |
| invoice / PO | engagement artifact |
| payment intent | *(remove)* |
| card payment (Stripe) | commercial license (card) |

Stripe: **commercial software licensing / service subscription only**, with disclaimer that Noetfield performs no custody, payment routing, or money transmission.

**Domain:** `noetfield.com` = institutional only · `platform.noetfield.com` = demos/runtime.

## Prohibited public language

Do not use on `noetfield.com`, Gate, or sales collateral:

- cross-border payments, payment intent, remittance, treasury routing;
- settlement orchestration, corridor, NDAX/Circle route comparison;
- MSB orchestration identity, meta-gateway PSP framing;
- “selects how money moves” or routing engine for funds.

## Cognitive OS hierarchy (internal — batch 020)

Single executable truth system for **multi-agent epistemic drift**:

| Layer | Repo path | Authority |
|-------|-----------|-----------|
| **L0** | `L0-law/`, GCIP v4, this file | Immutable — owner only |
| **L1** | `L1-operational/`, `services/` | Execution — obeys L0 |
| **L2** | `L2-knowledge/strategy/noetfield/` | Knowledge — never executes |
| **L3** | `L3-external/`, `reference-products/` | Sandbox — promote via OAS |
| **Archive** | `_archive/`, SOT prohibited | Cold storage |

**OAS (Opinion Arbitration):** claim extraction → conflict graph → alignment scoring → Golden Edge synthesis → **owner ratification**.  
Canonical specs: `noetfield-sot-master-document-v1`, `noetfield-unified-cognitive-governance-system-v1` · `governance/strategy-alignment-map.json`

## Engineering alignment

- **Public site:** static HTML at repo root — governance narrative only  
- **Runtime:** FastAPI governance core + Golden Edge v3 evaluate API (`:8001`)  
- **Knowledge:** `L2-knowledge/` — production vs reference-product separation  
- **Registry:** `docs/SOURCE_OF_TRUTH/registry/` — internal SOT inventory  

## Change control

Any change that introduces execution authority, fund touch, or payment semantics requires:

1. L0 constitutional amendment (not marketing edit), and  
2. legal/regulatory review before deploy.

Until then, **GCIP v4 + this North Star** govern all execution and GTM decisions.
