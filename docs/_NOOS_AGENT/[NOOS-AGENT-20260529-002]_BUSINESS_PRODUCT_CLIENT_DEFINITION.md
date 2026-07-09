# [NOOS-AGENT-20260529-002] Business, Product & Client Definition

<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260529-002
doc_type: PRODUCT_POSITIONING
workspace_root: /Users/sinakazemnezhad/Desktop/Noetfield-Systems/noetfeld-OS
classification: INTERNAL — canonical positioning for this sub-product
parent_brand: Noetfield Systems Inc. (noetfield.com)
product_codename: NOETFELD OS / Governance Execution Layer (GEL)
ecosystem_plane: DELIVERY — sub-product under Noetfield; not TrustField; not SinaaiRuntime
do_not_edit_from: other agents without NOOS-AGENT-DOC merge task
-->

**Status:** Agreed positioning — 2026-05-29  
**Audience:** ASF, sales, engineering, partner agents  
**Supersedes:** informal “financial API prototype” framing without parent-brand context

---

## 1. Agreement — relationship to Noetfield

**Yes, agreed.**

This project (`noetfeld-os`) is a **sub-product under Noetfield** — not a separate company, not TrustField, not the Sina mono runtime.

| Layer | Entity | Role |
|-------|--------|------|
| **Parent brand** | Noetfield Systems Inc. (`noetfield.com`) | Pre-execution governance infrastructure for regulated AI systems |
| **This sub-product** | **Noetfield OS** (Governance Execution Layer) | Runnable API + policy engine + audit spine for **operational decision governance** |
| **Sibling services** (Noetfield.com) | Trust Brief, Copilot Readiness, Trust Ledger | Assessment, packaging, board-ready evidence — **services + register** |
| **Explicitly not us** | TrustField Technologies (`trustfield.ca`) | RPAA / fintech **delivery** lane — partner or peer, not this codebase |

**One sentence placement:**

> Noetfield defines *why* governance must exist before execution; **Noetfield OS** is the *specialized runtime* that evaluates, scores, and logs governed decisions before any downstream system acts.

We are the **product engineering lane** for one narrow pathway inside Noetfield — not the whole Noetfield company story.

---

## 2. Industry pathway & field (pure specialization)

### Field we own

**Pre-execution governance for regulated operational decisions**

Specifically: systems where an organization must prove — to boards, auditors, or regulators — that **automated or AI-assisted decisions** were evaluated against **versioned policy** *before* money moves, accounts change, or customer-facing actions execute.

### Industry vertical (primary)

| Priority | Vertical | Why us |
|----------|----------|--------|
| **P1** | Canadian **banking & credit** (CU, regional bank, lending fintech) | Credit decisioning is the reference domain; OSFI / emerging AI governance pressure; non-custodial posture fits |
| **P2** | **Insurance & benefits** operational decisions | Same pattern: policy corridors, audit trail, no execution |
| **P3** | **Public-sector & crown-adjacent** AI operational gates | Procurement-friendly evidence; read-only pilot model on noetfield.com |
| **Defer** | General LLM chatbots, CRM, marketing AI | Out of scope — not our specialization |

### Geographic focus

**Canada first** (BC / national regulated enterprise), expandable to **US / UK** where pre-execution audit evidence is sellable — without claiming legal advice or licensing we do not hold.

### Category name (market)

We do **not** compete as:

- AI platform
- Lending origination system
- Payment processor
- Full GRC suite (OneTrust / Vanta class)

We compete as:

**Governance Execution Layer (GEL)** — a narrow category:

> *Infrastructure that simulates, evaluates, and audit-logs regulated decisions before execution systems run.*

---

## 3. Business definition

### Mission

Enable regulated organizations to **govern operational decisions before they execute**, with deterministic policy enforcement and audit-grade evidence — **without holding funds or executing transactions**.

### Business model

| Stream | Description | Typical buyer |
|--------|-------------|---------------|
| **API subscription** | Per-tenant access to GEL; tiered by decisions/month | Fintech, CU, internal enterprise AI team |
| **Pilot program** | 6-week governed sandbox + policy mapping + Trust Brief bundle | First logo / IRAP co-funded engagements |
| **Trust Ledger connector** | Export audit + drift events to board-ready register | Bank, enterprise compliance |
| **Implementation** | Policy JSON design, integration guide, read-only connector | SI partner, MSP (Microsoft ecosystem) |

### Revenue ladder (aligned to prior internal planning)

| Tier | Indicative | Purpose |
|------|------------|---------|
| Entry sandbox | ~$10K | Land first pilot |
| Standard pilot | ~$50K | Core services + GEL |
| Enterprise / IRAP program | ~$120K | Full build + validation |

### Non-negotiable business boundaries

1. **Non-custodial** — we return governance signals (APPROVE / REVIEW / DECLINE), not payment or settlement.
2. **Pre-execution only** — we do not trigger downstream execution; clients wire their own actuators.
3. **Evidence-first** — every decision produces an immutable audit row suitable for Trust Ledger export.
4. **Tenant isolation** — structural, not policy-only (Phase 1 production bar).

---

## 4. Product definition

### Product name (external)

**Noetfield Governance Execution Layer**  
Short: **Noetfield GEL** or **Noetfield OS** (engineering codename: `noetfeld-os` repo)

### What the product is

A **standalone FastAPI governance runtime** with:

| Capability | Description |
|------------|-------------|
| **Intent evaluation** | Structured input → scored decision + policy outcome |
| **Policy engine** | Versioned base policy + corridor rules (JSON today; tenant-scoped tomorrow) |
| **Risk scoring** | Explainable factor breakdown (credit domain first) |
| **Audit spine** | Append-only decision log with `request_id`, inputs, scores, outcome |
| **Governance API** | `POST /v1/decision`, `GET /portal/audits` (expand to `/drift`, `/replay`) |
| **Drift readiness** | Baseline versioning + drift detection (roadmap; see `NOOS-AGENT-20260529-001`) |

### Product SKUs (commercial packaging)

| SKU | Buyer | Includes |
|-----|-------|----------|
| **GEL Starter** | Fintech / CU pilot | API key, 1 policy set, 1K decisions/mo, audit portal |
| **GEL Standard** | Regulated enterprise | Multi-policy, tenant isolation, Postgres ledger, SLA |
| **GEL + Trust Ledger** | Bank / board-facing | GEL Standard + quarterly export + drift scoring |
| **Read-only pilot** | Noetfield.com bank pilot page | Simulation only; no execution authority |

### What we explicitly do not productize

- Loan origination UI
- Credit bureau integration (client brings data)
- Model training / LLM hosting
- Payment rails
- Full Copilot deployment (Noetfield services lane handles that)

---

## 5. Client target definition (ICP)

### Primary ICP — **Regulated Decision Operator**

**Organization profile**

- 50–5,000 employees
- Canada-based or Canada-operating regulated entity
- Deploying or planning **AI-assisted operational decisions** (credit, underwriting support, fraud triage, benefits eligibility)
- Board or compliance asking: *“Show us the log before the system acted.”*

**Buyer personas**

| Persona | Title (typical) | Cares about |
|---------|-----------------|-------------|
| **Economic buyer** | CRO, Head of Compliance, VP Risk | Audit defensibility, regulatory exposure |
| **Technical buyer** | Head of Engineering, Platform Lead | API integration, isolation, determinism |
| **Champion** | AI governance lead, internal audit | Policy versioning, drift, evidence packs |

**Trigger events**

- Copilot or internal AI pilot going to production
- OSFI / internal audit finding on AI explainability
- IRAP or innovation grant requiring Canadian IP
- Vendor asking for “governance layer” proof in RFP

### Secondary ICP — **Partner**

| Partner type | Value exchange |
|--------------|----------------|
| **Microsoft / MSP partner** | White-label governance assessment + GEL sandbox |
| **Systems integrator** | Implements connector; we provide API + policy templates |
| **TrustField** (peer) | RPAA delivery handoff where governance design ≠ execution delivery |

### Anti-ICP (do not pursue)

- Crypto / unregulated lending “move fast” shops wanting auto-approve without audit
- Startups needing a full LOS in 30 days
- Buyers requiring custody or payment initiation from our API
- General “build us ChatGPT” requests

---

## 6. Competitive positioning (specialization)

| Competitor class | They optimize for | We optimize for |
|------------------|-------------------|-----------------|
| **ML observability** (Arize, WhyLabs) | Model/data drift | **Policy + decision governance before execution** |
| **LLM guardrails** (Galileo-class) | Runtime LLM safety | **Regulated operational decision audit** (broader than chat) |
| **GRC platforms** (OneTrust, Vanta) | Control catalogs & attestations | **Per-decision enforcement log + replay** |
| **LOS / fintech cores** | Origination workflow | **Governance layer only** — integrate, don’t replace |

**Moat:** Pre-execution + non-custodial + Trust Ledger narrative + Canadian regulatory framing + **narrow depth** in governed decision evidence.

---

## 7. Professional identity (how we present)

### External one-liner

> **Noetfield OS** is the Governance Execution Layer for regulated operational decisions — evaluate policy, score risk, and produce audit-ready evidence before your systems execute.

### Elevator (30 seconds)

Noetfield is pre-execution governance infrastructure. **Noetfield OS** is the product that runs it: your applications send a decision intent, we apply versioned policy and explainable scoring, return APPROVE, REVIEW, or DECLINE, and write an immutable audit record. We never hold funds or execute transactions. Built for Canadian regulated enterprises that need board-grade evidence, not another AI model.

### Tagline options (pick one with ASF)

1. *Govern before you execute.*
2. *Audit-ready decisions, pre-execution.*
3. *The governance runtime for regulated AI.*

### Website placement (noetfield.com)

Suggested sub-page: **`noetfield.com/gel`** or **`noetfield.com/os`**

| Parent page | Sub-page (this product) |
|-------------|-------------------------|
| Trust Brief (assessment) | GEL Starter pilot |
| Trust Ledger (register) | GEL + Trust Ledger SKU |
| Bank pilot (read-only) | GEL simulation API |

---

## 8. Independence within Noetfield

**Technically independent**

- Own repo, own database, own API port (not SinaaiRuntime `:8000`)
- Must run with mono runtime **offline** (Phase 1 blueprint)

**Commercially part of Noetfield**

- Invoicing via Noetfield Systems Inc.
- Brand: “Noetfield Governance Execution Layer”
- Procurement: `procurement@noetfield.com`

**Professionally specialized**

- One job: **govern operational decisions pre-execution**
- One evidence model: **versioned policy + audit ledger + drift trajectory**
- One geography first: **Canada regulated enterprise**

---

## 9. Success metrics (12-month)

| Metric | Target |
|--------|--------|
| Paying pilots | 3+ regulated orgs |
| Decisions logged | 100K+ with full audit trail |
| Determinism / replay | 100% match on regression suite |
| Time to board-ready export | < 30 minutes from audit query |
| Drift detection | Critical drift triage < 4 hours (Noetfield v2 spec alignment) |

---

## 10. Agent mission statement (this chat)

**I am the `noetfeld-os-cursor-chat` agent.**

My mission is to build and document **Noetfield OS** — the Governance Execution Layer sub-product — with pure specialization in **pre-execution regulated decision governance**, professional product definition, and traceable agent-owned docs (`NOOS-AGENT-DOC`).

I do not expand scope into TrustField delivery, mono runtime orchestration, or general AI platforms unless ASF explicitly redirects.

---

*End of `NOOS-AGENT-20260529-002`. Search: `NOOS-AGENT-DOC`.*
