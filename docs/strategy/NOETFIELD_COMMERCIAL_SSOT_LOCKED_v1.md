# Noetfield Commercial SSOT (LOCKED v1)

| Field | Value |
|-------|--------|
| **Agent tag** | `[NF-LOCAL-REPO-AGENT]` |
| **Doc id** | `noetfield-commercial-ssot-v1` |
| **Locked** | 2026-06-12 |
| **Authority** | ASF product strategy · subordinate to [PRODUCT_TRUTH.md](../../PRODUCT_TRUTH.md) |
| **Supersedes** | Informal “three equal products” framing |

---

## 0. Buyer one-liner (public — use on www, outreach, demos)

> **Noetfield governs Copilot execution — invalid changes blocked, allowed changes receipted, tamper fails on export.**

We are the **AI Governance & Evidence layer** for Microsoft 365 Copilot adoption: evaluate operational intent, index metadata-only M365 evidence, produce signed **Trust Ledger Entries (TLE v1)**, and export board-ready diligence artifacts.

**We do not:** initiate payments, hold custody, route money, or replace Microsoft Purview/DLP.

---

## 1. Internal architecture (agents + founder only — never buyer-facing)

```text
┌─────────────────────────────────────────────────────────────┐
│  COMMERCIAL FRONTS (buyers see, pay, sign SOW)               │
│  noetfield.com (PRIMARY) · trustfield.ca (backup wedge)      │
├─────────────────────────────────────────────────────────────┤
│  PORTFOLIO ENGINE (L1 — not a public SKU)                    │
│  Pre-LLM gate · policy BLOCK/ALLOW · receipt spine ·       │
│  tamper FAIL · validators · one write path · agentic ops   │
├─────────────────────────────────────────────────────────────┤
│  PROOF LAYER (shipped in this repo)                          │
│  governance API · TLE lifecycle · audit export · www GTM     │
└─────────────────────────────────────────────────────────────┘
```

| Layer | Role | Buyer hears |
|-------|------|-------------|
| **Noetfield** | Primary earning company **now** | Copilot governance · CISO/GRC/M365 |
| **TrustField** | Second commercial front | MSB/regulated receipt wedge (separate site) |
| **Portfolio engine** | Backend motor | **Nothing** — credibility flows up to Noetfield |

**W3 economic signal:** deposit ≥ CAD 2K or signed LOI/SOW on **Noetfield design partner** — not “sell the engine as SKU.”

---

## 2. Who we sell to (ICP)

| Persona | Pain | Noetfield package |
|---------|------|-------------------|
| **CISO / Head of AI** | Copilot rollout ahead of evidence | Copilot Governance Pack · design partner |
| **GRC / Compliance** | Board asks for defensible decision record | TLE v1 + board pack PDF |
| **Procurement / Legal** | Diligence ZIP, framework citations | Procurement pack · Sources Book alignment |
| **CIO / M365 owner** | Purview configured but not packaged for audit | Evidence index (metadata only) |

**Primary geo (30-day):** Vancouver regulated SMB — healthcare **or** legal/accounting Trust Brief wedge.

---

## 3. Contract offerings (locked — three only)

See [OFFERINGS_LOCKED.md](../../OFFERINGS_LOCKED.md).

| SKU | Price band | Deliverable |
|-----|------------|-------------|
| **Trust Brief** | $10,000 · 6 weeks | Governance audit + policy map + risk exposure |
| **Copilot Governance Pack** | Design partner $2k–10k pilot | Block + record + export (TLE + board PDF) |
| **Bank Pilot** | Custom | Read-only shadow simulation — no execution authority |

**Primary CTA (contract):** [Request Governance Brief](/trust-brief/intake/) · `operations@noetfield.com`

**Self-serve CTA (access):** [Start free sandbox](/start/) — no sales call · 14-day · 50 evaluates

---

## 3b. Packaging funnel (v16 — Sumsub-class)

See [WWW_V16_PACKAGING_PLAN_LOCKED_v1.md](../WWW_V16_PACKAGING_PLAN_LOCKED_v1.md) · [COMMERCIAL_INBOX_PACKAGING_LOCKED_v1.md](../ops/COMMERCIAL_INBOX_PACKAGING_LOCKED_v1.md).

| Stage | Buyer action | Mode |
|-------|--------------|------|
| **Try** | Sign up on `/start/` | Sandbox · mock M365 |
| **Prove** | Evaluate → TLE sample → export orientation | Sandbox |
| **Apply** | Design partner program | Production path |
| **Buy** | Trust Brief or Bank Pilot SOW | Contract SKU |

**Published tiers:** `/pricing/` · **Agentic workflows:** investigate → triage → draft TLE → act on low-risk (human approvers on high-risk).

---

## 4. Governance execution loop (buyer language)

Maps to shipped product + portfolio engine behavior — **do not name internal engine brands**.

| Step | Buyer sees | Shipped artifact |
|------|------------|------------------|
| **1. Evaluate** | Pre-execution allow / deny / review | `POST /evaluate` · confidence score |
| **2. Decide** | Policy + human approval chain | TLE approval chain |
| **3. Record** | Immutable RID + evidence index | `audit_events` · M365 connector metadata |
| **4. Export** | Board PDF · procurement ZIP | `trust_ledger_pdf` · procurement pack |
| **5. Prove** | Tamper-evident digest | Signed TLE · FAIL-closed verify scripts |

**Demo sentence:** *“Show me the record your auditor would accept before Copilot touches production data.”*

---

## 5. Design partner program (90-day commercial path)

| Week | Milestone | Proof |
|------|-----------|-------|
| 0–2 | Named CIO contact · demo URL live | `make demo-url` · pipeline stage 1–2 |
| 3–6 | Pilot SOW · M365 evidence connected | TLE v1 approved |
| 7–10 | Board PDF in governance meeting | Partner success signal (GTM locked) |
| 11–12 | LOI / deposit ≥ CAD 2K | W3 PASS bar |

**Docs:** [DESIGN_PARTNER_PIPELINE_v1.md](../copilot/DESIGN_PARTNER_PIPELINE_v1.md) · [DESIGN_PARTNER_SOW_OUTLINE.md](../copilot/DESIGN_PARTNER_SOW_OUTLINE.md)

**Execution:** Agentic outreach layer — [AGENTIC_COMMERCIAL_HANDOFF_v1.md](../ops/AGENTIC_COMMERCIAL_HANDOFF_v1.md) · founder Hub approve before send.

---

## 6. Framework & diligence (high-grade SME provider)

| Framework | Noetfield artifact |
|-----------|-------------------|
| NIST AI RMF Govern / Manage | TLE approval chain + board pack |
| ISO/IEC 42001-style evidence | Evidence index + audit export |
| Microsoft Purview / M365 | Connector ingest → evidence IDs in TLE |
| EU AI Act / OECD (orientation) | [GOVERNANCE_SOURCES_BOOK_v1.md](../reference/GOVERNANCE_SOURCES_BOOK_v1.md) Part A |

**Buyer pack index:** [PROCUREMENT_ONE_PAGER.md](../copilot/PROCUREMENT_ONE_PAGER.md) · [rpaa-positioning-onepager.md](../diligence/rpaa-positioning-onepager.md)

---

## 7. Embedded portfolio capabilities (what Noetfield ships vs references)

| Capability | In Noetfield repo | Buyer-facing |
|------------|-------------------|--------------|
| Trust Ledger / TLE v1 | **Shipped** code + www | Yes |
| Governance evaluate API | **Shipped** | Yes |
| M365 evidence connectors | **Shipped** (metadata) | Yes |
| Drift detection blueprints | Locked docs + roadmap | Orientation |
| SME automation governance | [ai-automation/](/ai-automation/) Lane B reference | Governance-first only |
| Agentic commercial send | Handoff to agentic layer | Never NF-CLOUD implement |
| Payment / custody / MSB execution | **Forbidden** | TrustField separate brand |

---

## 8. External messaging matrix

| Audience | Say | Never say |
|----------|-----|-----------|
| **Buyer** | Copilot governance · audit trail · TLE · board export | “Trust OS” · “Decision Cloud” · engine SKU |
| **Investor / founder** | Noetfield is first commercial product on governed execution stack | Three equal products competing |
| **Procurement** | Metadata-only evidence · no payment claims | Custody · settlement · routing |

---

## 9. www surface map (commercial)

| Path | Purpose |
|------|---------|
| `/` | Hero · offerings · design partner CTA |
| `/copilot/` | Copilot Governance Pack hub |
| `/copilot/sme/` | SME provider grade pack (CISO/GRC) |
| `/copilot/demo/` | 5-minute demo script |
| `/copilot/pilot/` | Design-partner checklist |
| `/copilot/procurement/` | Diligence buyer pack |
| `/trust-brief/` | Trust Brief SKU |
| `/workspace/` | TLE workspace |
| `/ai-automation/` | Lane B operator reference (not new SKU) |

---

## 10. Verify (commercial truth)

```bash
make verify-gtm          # pre-demo bundle
make ship-verify         # cloud superset
./scripts/verify-agent-scope.sh
```

**DONE** for commercial claims = verify PASS + demo URL live + cursor-reply SHA current.

---

## 11. Agent instruction

When ASF says **implement** from this SSOT:

1. Pick **one** Lane A task · cite section in YAML evidence  
2. Never implement payment execution in this repo  
3. Never put portfolio engine brand on www  
4. Agentic outreach = handoff doc only  

---

**END**
