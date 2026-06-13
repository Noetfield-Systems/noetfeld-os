# Governance Sources Handbook (LOCKED v1)

**Status:** LOCKED · **Plane:** REFERENCE · **Do not override without ASF + product signoff**  
**For:** Noetfield agents, founders, delivery, diligence  
**Lane:** `noetfield_cloud` · Copilot governance & Trust Ledger (TLE v1)  
**Last reviewed:** 2026-06-04  
**Index:** [README.md](./README.md) · **Companion:** [GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md](./GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md)

This is a **small reference book** of **real, primary, reliable** governance sources on the public web—not blog opinions. Use it to justify controls, map TLE fields to industry language, and brief buyers in one sentence: *we help you produce the audit trail regulators and boards already expect, aligned to these frameworks.*

---

## 1. How to use this handbook

### 1.1 Reliability tiers

| Tier | What it means | Use in diligence |
|------|----------------|------------------|
| **T1** | Statute, regulation, or formal standard body (NIST, ISO, EU, OECD, AICPA, FFIEC) | Cite directly in SOWs and board packs |
| **T2** | Vendor primary documentation (Microsoft Learn, Microsoft published PDFs) | Map product integration (Purview, Copilot audit) |
| **T3** | Industry frameworks (ISACA COBIT, OWASP) | Structure governance programs and security reviews |
| **T4** | Commentary, consultancies, news | Orientation only—confirm against T1/T2 |

### 1.2 Noetfield product mapping (quick)

| Buyer ask | Framework hook | Noetfield artifact |
|-----------|----------------|-------------------|
| “Prove who approved Copilot” | EU AI Act documentation · NIST GOVERN | Signed TLE + approval chain |
| “Show evidence we reviewed” | ISO 42001 risk & lifecycle | Evidence Index + `metadata_only` ingest |
| “What did users do in Copilot?” | Microsoft Purview audit | Connector manifest + Purview audit refs in evidence |
| “Are we SOC-ready?” | AICPA Trust Services Criteria | Append-only audit log + export by RID |
| “Bank examiner questions” | FFIEC IT Handbook (audit trails) | Audit-export + immutable TLE |
| “LLM security?” | OWASP LLM Top 10 · NIST AI 600-1 | Evaluate gates + confidence score (W56-3) |

### 1.3 What we do **not** claim

- Noetfield is **not** a law firm, auditor, or certifying body.
- Listing a source does **not** imply certification against it.
- **Pre-execution governance only**—no payments, custody, or MSB execution ([PRODUCT_TRUTH.md](../../PRODUCT_TRUTH.md)).

---

## 2. United States — AI risk & trustworthy AI

### 2.1 NIST AI Risk Management Framework (AI RMF 1.0)

| Field | Value |
|-------|--------|
| **Authority** | U.S. National Institute of Standards and Technology |
| **Tier** | T1 |
| **Published** | January 2023 (living document; review expected ~2028) |
| **Voluntary?** | Yes—widely adopted by enterprises and U.S. agencies |

**What it is:** Cross-sector framework to manage AI risks through four functions: **GOVERN**, **MAP**, **MEASURE**, **MANAGE**. Rights-preserving, use-case agnostic.

**Why it matters for Noetfield:** GOVERN maps to policies + roles (CIO, Legal, Security approvers in TLE). MAP/MEASURE map to evidence ingest and confidence score. MANAGE maps to approve/reject/conditional decisions and board-pack export.

**Primary links:**

- Overview: https://www.nist.gov/itl/ai-risk-management-framework  
- Publication (DOI): https://doi.org/10.6028/NIST.AI.100-1  
- PDF: https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf  
- AI RMF Core (AIRC): https://airc.nist.gov/airmf-resources/airmf/5-sec-core/  
- Playbook: https://www.nist.gov/itl/ai-risk-management-framework/nist-ai-rmf-playbook  
- Resource Center: https://airc.nist.gov/

**Noetfield alignment:** Trust Ledger workspace + multi-approve + PDF export operationalize **accountability** and **documentation** called for under GOVERN and MANAGE.

---

### 2.2 NIST Generative AI Profile (NIST AI 600-1)

| Field | Value |
|-------|--------|
| **Authority** | NIST (companion to AI RMF 1.0) |
| **Tier** | T1 |
| **Published** | July 2024 |

**What it is:** Profile for **generative AI** risks (confabulation, data privacy, information integrity, IP, harmful content, value chain, etc.) with suggested actions per RMF function.

**Primary links:**

- PDF: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf  
- DOI: https://doi.org/10.6028/NIST.AI.600-1  
- Announced via: https://www.nist.gov/itl/ai-risk-management-framework  

**Noetfield alignment:** Copilot rollout = GAI deployment. Use profile language in Trust Brief deliverables; map **confidence score** and **human oversight** to MEASURE/MANAGE mitigations for confabulation and misinformation.

---

## 3. International — principles & management systems

### 3.1 OECD AI Principles (Recommendation of the Council on AI)

| Field | Value |
|-------|--------|
| **Authority** | OECD Council (47 adherents incl. EU) |
| **Tier** | T1 (soft law / intergovernmental) |
| **Updated** | 2023–2024 (generative AI considerations) |

**What it is:** First intergovernmental standard for trustworthy AI—five values (inclusive growth, human rights/fairness, transparency, robustness/safety, accountability) plus five policy recommendations.

**Primary links:**

- Legal instrument text: https://legalinstruments.oecd.org/api/print?ids=648&lang=en  
- Press (2024 update): https://www.oecd.org/en/about/news/press-releases/2024/05/oecd-updates-ai-principles-to-stay-abreast-of-rapid-technological-developments.html  
- Policy observatory: https://oecd.ai/

**Noetfield alignment:** TLE **approval chain** and **transparency** fields support accountability and human-centred values without claiming OECD “certification.”

---

### 3.2 ISO/IEC 42001:2023 — AI management system (AIMS)

| Field | Value |
|-------|--------|
| **Authority** | ISO/IEC |
| **Tier** | T1 |
| **Published** | December 2023 |
| **Certification** | Voluntary third-party certification available |

**What it is:** First international **management system** standard for AI—Plan-Do-Check-Act for policies, risk, lifecycle, transparency, continual improvement.

**Primary links:**

- Standard page: https://www.iso.org/standard/42001  
- Explainer: https://www.iso.org/home/insights-news/resources/iso-42001-explained-what-it-is.html  
- AI management hub: https://www.iso.org/artificial-intelligence/ai-management-systems  
- Microsoft alignment (customer context): https://learn.microsoft.com/en-us/compliance/regulatory/offering-iso-42001  

**Noetfield alignment:** Trust Brief + TLE = **evidence of governance decisions** buyers can feed into AIMS audits. Document connector + evidence policies as **operational controls**, not full AIMS certification.

---

## 4. European Union — AI Act & cybersecurity

### 4.1 Regulation (EU) 2024/1689 (Artificial Intelligence Act)

| Field | Value |
|-------|--------|
| **Authority** | European Parliament and Council |
| **Tier** | T1 (binding in EU) |
| **Risk approach** | Prohibited practices · high-risk · transparency · GPAI |

**What it is:** Harmonised rules for placing on market, putting into service, and **use** of AI systems—including documentation, logging, human oversight, and post-market monitoring for **high-risk** AI.

**Primary links:**

- Official Journal (EUR-Lex): https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng  
- Summary (EUR-Lex): https://eur-lex.europa.eu/legal-content/EN/LSU/?uri=oj%3AL_202401689  
- Commission service desk (Annex III high-risk areas): https://ai-act-service-desk.ec.europa.eu/en/ai-act/annex-3  
- Readable articles (unofficial helper): https://artificialintelligenceact.eu/

**High-risk themes relevant to enterprises:** Critical infrastructure, employment, essential services, law enforcement (see Annex III). Many Copilot **internal** deployments may not be high-risk but **documentation discipline** still wins procurement.

**Noetfield alignment:** TLE + technical documentation pattern mirrors **Annex IV-style** “prove what you decided and why.” Register connectors and evidence sources in diligence pack.

---

### 4.2 ENISA — Multilayer Framework for Good Cybersecurity Practices for AI (FAICP)

| Field | Value |
|-------|--------|
| **Authority** | EU Agency for Cybersecurity (ENISA) |
| **Tier** | T1 (EU agency guidance) |
| **Published** | June 2023 |

**What it is:** Three layers—(I) baseline ICT security, (II) AI-specific security, (III) sector-specific—for securing AI systems aligned with AI Act expectations.

**Primary links:**

- Publication page: https://www.enisa.europa.eu/publications/multilayer-framework-for-good-cybersecurity-practices-for-ai  
- PDF: https://www.enisa.europa.eu/sites/default/files/publications/Multilayer%20Framework%20for%20Good%20Cybersecurity%20Practices%20for%20AI.pdf  

**Noetfield alignment:** Layer II maps to LLM risks (OWASP overlap). Layer I maps to pilot auth, rate limits, tenant isolation (NF-PLAN-0114).

---

## 5. Enterprise IT governance

### 5.1 COBIT 2019 (ISACA)

| Field | Value |
|-------|--------|
| **Authority** | ISACA |
| **Tier** | T3 (enterprise IT governance) |
| **Scope** | Enterprise governance of information and technology (EGIT) |

**What it is:** 40 governance/management objectives across Evaluate-Direct-Monitor, Align-Plan-Organize, Build-Acquire-Implement, Deliver-Service-Support, Monitor-Evaluate-Assess. Integrates with NIST Cybersecurity Framework mapping.

**Primary links:**

- Hub: https://www.isaca.org/resources/cobit  
- Complimentary downloads: https://www.isaca.org/resources/cobit (Framework, Design Guide, Implementation Guide)  
- NIST CSF mapping: *Implementing the NIST Cybersecurity Framework Using COBIT 2019* (linked from ISACA COBIT page)

**Noetfield alignment:** Position Trust Ledger as **evidence for EDM/APO processes**—board oversight of AI initiatives, not replacement for COBIT implementation.

---

## 6. AI application security (generative / LLM)

### 6.1 OWASP Top 10 for LLM Applications (2025)

| Field | Value |
|-------|--------|
| **Authority** | OWASP Gen AI Security Project |
| **Tier** | T3 (industry consensus) |
| **Current edition** | 2025 |

**Top risks (2025):** Prompt injection · Sensitive information disclosure · Supply chain · Data/model poisoning · Improper output handling · Excessive agency · System prompt leakage · Vector/embedding weaknesses · Misinformation · Unbounded consumption.

**Primary links:**

- Project home: https://owasp.org/www-project-top-10-for-large-language-model-applications/  
- Top 10 hub: https://genai.owasp.org/llm-top-10/  
- PDF (2025): https://owasp.org/www-project-top-10-for-large-language-model-applications/assets/PDF/OWASP-Top-10-for-LLMs-v2025.pdf  

**Noetfield alignment:** Pre-execution **evaluate** + metadata-only evidence reduces disclosure and agency risk; document mitigations in Bank Pilot / security diligence. Confidence score helps communicate **misinformation / confabulation** residual risk.

---

## 7. Microsoft ecosystem (Copilot buyers)

### 7.1 Microsoft 365 Copilot — data protection & auditing

| Field | Value |
|-------|--------|
| **Authority** | Microsoft (primary documentation) |
| **Tier** | T2 |

**What it is:** Copilot runs inside M365 boundary; interactions auditable via **Microsoft Purview** unified audit log; retention via Data Lifecycle Management; eDiscovery for investigations.

**Primary links:**

- Purview for M365 Copilot: https://learn.microsoft.com/en-us/purview/ai-m365-copilot  
- Data protection architecture: https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-architecture-data-protection-auditing  
- Generative AI + Purview overview: https://learn.microsoft.com/en-us/purview/ai-microsoft-purview  
- **Audit logs for Copilot:** https://learn.microsoft.com/en-us/purview/audit-copilot  
- Retention for Copilot: https://learn.microsoft.com/en-us/purview/retention-policies-copilot  

**Noetfield alignment:** [CONNECTORS_CONTROLS_v1.md](../diligence/CONNECTORS_CONTROLS_v1.md) — Purview connector type; evidence ingest references **audit metadata**, not message bodies. TLE cites Purview/Entra/M365 audit as sources per [EVIDENCE_INTAKE_CONTRACT_v1.md](../diligence/EVIDENCE_INTAKE_CONTRACT_v1.md).

---

### 7.2 Microsoft Responsible AI Standard v2

| Field | Value |
|-------|--------|
| **Authority** | Microsoft (published requirements) |
| **Tier** | T2 |
| **Published** | June 2022 (living document) |

**What it is:** Operational requirements for impact assessment, data governance, human oversight, fairness, safety—used internally for Microsoft AI products including Copilot.

**Primary links:**

- General Requirements PDF: https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/microsoft/final/en-us/microsoft-brand/documents/Microsoft-Responsible-AI-Standard-General-Requirements.pdf  
- Short link: https://aka.ms/RAI/Standard  
- Blog introduction: https://blogs.microsoft.com/on-the-issues/2022/06/21/microsofts-framework-for-building-ai-systems-responsibly/  
- Transparency Report 2025 (PDF): https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/microsoft/msc/documents/presentations/CSR/Responsible-AI-Transparency-Report-2025-vertical.pdf  

**Noetfield alignment:** Trust Brief **impact assessment** deliverable can reference same structure (accountability goals A1–A7 family) without claiming Microsoft compliance.

---

### 7.3 ISO/IEC 42001 — Microsoft compliance offering

**Link:** https://learn.microsoft.com/en-us/compliance/regulatory/offering-iso-42001  

Use when buyers ask how Microsoft cloud AI relates to ISO 42001—distinct from customer’s own AIMS scope.

---

## 8. Audit, assurance & regulated financial institutions

### 8.1 AICPA Trust Services Criteria (SOC 2)

| Field | Value |
|-------|--------|
| **Authority** | AICPA / CIMA |
| **Tier** | T1 (attestation criteria) |
| **Categories** | Security (required) · Availability · Processing integrity · Confidentiality · Privacy |

**What it is:** Control criteria for SOC 2 examinations over service organizations.

**Primary links:**

- Download (2022 points of focus): https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022  
- Criteria PDF: https://assets.ctfassets.net/rb9cdnjh59cm/72xv4p67HVXKp6CjWmjkPk/1cdbfa19f6307e2720396b66a6194dc9/trust-services-criteria-updated-copyright.pdf  

**Noetfield alignment:** Immutable audit log + RID-scoped **audit-export** support **Security** and **Confidentiality** narratives; TLE adds **processing integrity** story for AI **decisions** (not payments).

---

### 8.2 FFIEC IT Examination Handbook

| Field | Value |
|-------|--------|
| **Authority** | FFIEC member agencies (U.S. banking regulators) |
| **Tier** | T1 for U.S. banks / credit unions |
| **Format** | InfoBase booklets + examination procedures |

**What it is:** Supervisory expectations for IT governance, audit, development, operations. Emphasizes **complete audit trails**, board oversight, independent IT audit.

**Primary links:**

- InfoBase home: https://ithandbook.ffiec.gov/  
- Audit — Board & senior management: https://ithandbook.ffiec.gov/it-booklets/audit/it-audit-roles-and-responsibilities/board-of-directors-and-senior-management  
- Audit — Appendix A (examination procedures): https://ithandbook.ffiec.gov/it-booklets/audit/appendix-a-examination-procedures  
- Development — Appendix A (change audit trails): https://ithandbook.ffiec.gov/it-booklets/development-acquisition-and-maintenance/appendix-a-examination-procedures/  
- Management booklet (PDF): https://www.ffiec.gov/sites/default/files/media/press-releases/2015/2015-it-examination-handbook-management-booklet.pdf  

**Noetfield alignment:** [BANK_PILOT_DEMO.md](../BANK_PILOT_DEMO.md) — shadow evaluate + audit-export + TLE as **documented authorization trail** for AI operational intent (not core banking payments).

---

## 9. Noetfield in-repo contracts (synthetic but binding for delivery)

These are **your** buyer-facing artifacts—cite alongside external frameworks:

| Document | Path |
|----------|------|
| Evidence Intake Contract v1 | [docs/diligence/EVIDENCE_INTAKE_CONTRACT_v1.md](../diligence/EVIDENCE_INTAKE_CONTRACT_v1.md) |
| Connectors Controls v1 | [docs/diligence/CONNECTORS_CONTROLS_v1.md](../diligence/CONNECTORS_CONTROLS_v1.md) |
| Trust Ledger blueprint | [docs/spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md](../spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md) |
| TLE schema | [docs/spec/schemas/tle-v1.schema.yaml](../spec/schemas/tle-v1.schema.yaml) |
| OpenAPI (design) | [docs/spec/openapi/trust-ledger-v0.yaml](../spec/openapi/trust-ledger-v0.yaml) |
| RPAA positioning | [docs/diligence/rpaa-positioning-onepager.md](../diligence/rpaa-positioning-onepager.md) |

---

## 10. Suggested reading order by role

### Founder / GTM (30 minutes)

1. OECD AI Principles overview (accountability language)  
2. NIST AI RMF one-pager + AI 600-1 executive summary  
3. Microsoft Purview audit-copilot page (demo script)  
4. In-repo Trust Ledger www + Trust Brief pricing ([GTM_COPYBOOK.md](../GTM_COPYBOOK.md))

### Agent implementing product (60 minutes)

1. [TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md](../spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md)  
2. NIST AI RMF Core — GOVERN + MANAGE  
3. OWASP LLM Top 10 2025  
4. Microsoft Copilot architecture + audit docs  
5. This handbook §9 in-repo contracts  

### Bank / regulated diligence (90 minutes)

1. FFIEC audit booklet excerpts (audit trails, board oversight)  
2. SOC 2 Trust Services Criteria — Security  
3. EU AI Act EUR-Lex summary + Annex III awareness  
4. ENISA FAICP Layer II  
5. Noetfield sample export + [BANK_PILOT_DEMO.md](../BANK_PILOT_DEMO.md)

---

## 11. Master bibliography (copy-paste URLs)

```text
# US AI risk
https://www.nist.gov/itl/ai-risk-management-framework
https://doi.org/10.6028/NIST.AI.100-1
https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf
https://airc.nist.gov/
https://doi.org/10.6028/NIST.AI.600-1
https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf

# International
https://legalinstruments.oecd.org/api/print?ids=648&lang=en
https://www.iso.org/standard/42001

# EU law & security
https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng
https://ai-act-service-desk.ec.europa.eu/en/ai-act/annex-3
https://www.enisa.europa.eu/publications/multilayer-framework-for-good-cybersecurity-practices-for-ai

# IT governance & security
https://www.isaca.org/resources/cobit
https://genai.owasp.org/llm-top-10/

# Microsoft Copilot
https://learn.microsoft.com/en-us/purview/audit-copilot
https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-architecture-data-protection-auditing
https://aka.ms/RAI/Standard

# Assurance & banking
https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022
https://ithandbook.ffiec.gov/
```

---

## 12. Sources intentionally excluded

Do **not** treat these as primary governance evidence without a T1/T2 anchor:

- Random “AI governance checklist” blogs and LinkedIn posts  
- Unverified GitHub awesome-lists without links to primary law/standards  
- Vendor whitepapers that restate NIST/ISO without publishing auditable controls  
- **Noetfield vendor comparison marketing** pages  

When adding new sources to v1.1, require: **named authority**, **stable URL**, **publication date**, and **one-sentence Noetfield mapping**.

---

## 13. Related locked reference

**Governance drift detection** (policy drift, model/data/concept drift, semantic RAG drift, config drift): [GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md](./GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md)

---

## 14. Version history

| Version | Date | Notes |
|---------|------|-------|
| v1 LOCKED | 2026-06-04 | Initial handbook: 20+ primary sources; filename locked |

**Next review triggers:** NIST AI RMF major revision · EU AI Act implementing acts · OWASP LLM Top 10 2026 · ISO 42001 amendment.
