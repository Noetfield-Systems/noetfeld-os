# Inforcer Complement Battlecard (MSP v1)

| Field | Value |
|-------|--------|
| **Agent tag** | `[NF-LOCAL-REPO-AGENT]` |
| **Doc id** | `noetfield-inforcer-complement-v1` |
| **Parent** | [MSP_GOVERNANCE_PACK_v1.md](./MSP_GOVERNANCE_PACK_v1.md) |
| **Updated** | 2026-06-02 |
| **Audience** | MSP practice leads · security engineers · partner managers |

**One-liner:** **Inforcer configures Purview at scale; Noetfield receipts governance decisions.**

Not a competitive teardown — Inforcer is the **Phase 1** standard for 1000+ MSPs. Noetfield attaches at **Phase 2** when the buyer needs signed audit evidence.

---

## 1. Side-by-side

| Dimension | Inforcer (Phase 1) | Noetfield (Phase 2) |
|-----------|-------------------|---------------------|
| **Primary job** | Multi-tenant Purview policy management | Governance evaluate + TLE receipts |
| **Copilot readiness** | Assessment reports · gap identification | Readiness → Record pilot scope |
| **Deploy labels / DLP** | **Yes** — push baselines | **No** — metadata index only |
| **Intune · CA · Defender** | **Yes** | Complement via evidence refs |
| **Go/no-go record** | Report recommendations | **Signed TLE v1 + export** |
| **Board / procurement PDF** | Readiness report export | Board pack + procurement ZIP |
| **Tamper-evident export** | Vendor report | Integrity-fail closed bundle |
| **Multi-tenant dashboard** | **Yes** — core product | Per-tenant workspace (partner view TBD) |
| **Pricing model** | Platform subscription | Pilot + MRR via MSP wholesale |

---

## 2. When to lead with Inforcer (Phase 1 only)

- Tenant has **no** sensitivity labels or Copilot-aware DLP.
- MSP is standardizing Purview across 20+ tenants.
- Buyer question: “Are we Copilot-ready?” — not yet “Can we prove governance?”
- Revenue: high-margin remediation + Purview Suite CSP attach.

**Talk track:** “We use Inforcer [or Lighthouse/CIPP] to get you ready. When you’re ready to **enable Copilot with a defensible record**, we add Noetfield Phase 2.”

---

## 3. When to attach Noetfield (Phase 2)

- Readiness report is **green** (or exceptions signed) and Copilot licenses purchased.
- Customer board / insurance / enterprise client asks for **audit trail**.
- Copilot Studio agents entering production.
- MSP wants **recurring MRR** beyond one-time readiness project.
- Regulated end customer (healthcare, legal, finance) in MSP tenant base.

**Talk track:** “Readiness got you safe to turn it on. Noetfield **receipts every governance decision** — invalid blocked, allowed exported, tamper fails closed.”

---

## 4. Objection handling

| Objection | Response |
|-----------|----------|
| “Inforcer already has reports.” | Reports ≠ **signed decision record**. TLE is for boards and procurement diligence. |
| “We don’t need another tool.” | Phase 2 only on tenants that **scale Copilot** — not every tenant. |
| “Can Noetfield deploy Purview?” | **No** — that’s your Inforcer practice. We complement. |
| “Customer wants one vendor.” | MSP is single throat to choke — **you** prime; Noetfield sub. |
| “Is Noetfield competing for Inforcer?” | **No partnership conflict** — different layer; refer Phase 1 to Inforcer if needed. |

---

## 5. Joint workflow

```text
Inforcer assessment (tenant A..N)
        │
        ▼
MSP remediation (labels, DLP, CA)
        │
        ▼
Readiness report archived
        │
        ▼
Noetfield Phase 2 kickoff (tenant ID + report)
        │
        ▼
Evaluate → TLE → Export → MSP QBR
```

See [READINESS_TO_RECORD_MAPPING_v1.md](./READINESS_TO_RECORD_MAPPING_v1.md) for field mapping.

---

## 6. Also complements (not replaces)

| Tool | Phase 1 role | Noetfield relationship |
|------|--------------|------------------------|
| **Microsoft Lighthouse** | Free baselines · GDAP | Same Phase 1 slot |
| **CIPP** | Multi-tenant admin | Same Phase 1 slot |
| **AvePoint Elements** | AI-ready Intune extension | Readiness partner · Phase 2 attach |
| **Cloudiway** | White-label readiness | Assessment vendor · Phase 2 attach |
| **Microsoft OSS assessment** | Free CSV export | Import per mapping doc |

---

## 7. Proof points (Noetfield)

- Buyer line: *Invalid changes blocked, allowed changes receipted, tamper fails on export.*
- Live demo: `/copilot/demo/?msp=1`
- Samples: `/trust-ledger/sample-report/`
- Procurement: `/copilot/procurement/`
- Metadata-only M365 — [CANADA_TRUST.md](../api/CANADA_TRUST.md)

---

## 8. Partner next step

- Partner intake: `/trust-brief/intake/?interest=msp`
- Email: `operations@noetfield.com`
- Enablement: [PHASE1_PHASE2_RACI_v1.md](./PHASE1_PHASE2_RACI_v1.md)

**External:** [Inforcer — Microsoft Purview for MSPs](https://www.inforcer.com/microsoft-purview-policy-management)

---

## 9. Do not say

- “Replace Inforcer with Noetfield”
- “Noetfield deploys Purview faster than Inforcer”
- “We are a Microsoft-certified Copilot readiness platform”
- Payment, custody, or cross-tenant Copilot claims
