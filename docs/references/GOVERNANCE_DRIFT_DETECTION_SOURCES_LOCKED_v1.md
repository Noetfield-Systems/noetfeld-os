# Governance Drift Detection Sources (LOCKED v1)

**Status:** LOCKED · **Plane:** REFERENCE · **Do not override without ASF + product signoff**  
**For:** Noetfield agents, founders, delivery, security, MLOps, GRC  
**Lane:** `noetfield_cloud`  
**Last reviewed:** 2026-06-04  
**Companion:** [GOVERNANCE_SOURCES_HANDBOOK_LOCKED_v1.md](./GOVERNANCE_SOURCES_HANDBOOK_LOCKED_v1.md) · [README.md](./README.md)

Curated **primary and industry-standard** sources for **governance drift detection**: when live behavior, configuration, data, or model outputs diverge from approved policy, baseline, or training assumptions. Use with the general governance handbook for buyer language and control design.

---

## 1. Drift taxonomy (use one term per conversation)

| Type | What drifts | Typical detection | Regulated buyer cares because |
|------|-------------|-------------------|-------------------------------|
| **Policy / control drift** | Security baselines vs actual config | CSPM, AWS Config, CM-6(3), GRC continuous monitoring | SSP/POA&M no longer matches reality |
| **Configuration / IaC drift** | Live cloud vs Terraform/CloudFormation desired state | OPA/Conftest on plans, scheduled drift scans, CFN drift API | Unauthorized change, shadow IT |
| **Data drift** | Input feature distributions vs training/baseline | PSI, KS test, Jensen–Shannon, embedding distance | Model still “runs” but on wrong population |
| **Concept drift** | Input→label relationship changes | Performance decay, error rate by cohort | Fraud/policy rules stop matching reality |
| **Model / performance drift** | Accuracy, calibration, override rates | Continuous quality metrics, dashboards | Silent wrong decisions |
| **Semantic / RAG drift** | Retrieved context vs ground truth; answer inconsistency | Embedding monitors, LLM-as-judge, index versioning | Copilot/RAG gives contradictory advice |
| **Epistemic / agent drift** | Multi-agent or doc corpus diverges from locked truth | Manifest hash, SOT reconciliation, human triage SLA | Wrong answers across chats without audit trail |
| **Adversarial / behavioral drift** | Model behavior under attack or prompt abuse | MITRE ATLAS techniques, OWASP LLM Top 10 | Security incident, not statistical shift |

**Noetfield wedge:** Pre-execution **governance drift** — policy intent, approval state, and evidence lineage drifting from signed TLE / RID baseline (see §8).

---

## 2. Reliability tiers (same as handbook)

| Tier | Examples in this doc |
|------|---------------------|
| **T1** | NIST AI RMF, NIST SP 800-53/171, EU AI Act Art. 72, ISO 42001 monitoring, EUR-Lex |
| **T2** | Microsoft Learn, AWS official docs (Config, Prescriptive Guidance) |
| **T3** | OWASP GenAI, MITRE ATLAS, OPA, COBIT, ENISA FAICP, Evidently/Deepchecks docs |
| **T4** | Consultancy blogs, Medium — **orientation only** |

---

## 3. AI governance & continuous monitoring (T1)

### 3.1 NIST AI RMF 1.0 — MEASURE + drift language

| Field | Value |
|-------|--------|
| **Authority** | NIST |
| **Tier** | T1 |

**What it says:** AI systems should be tested before deployment and **regularly while in operation**. The MEASURE function covers monitoring functionality, trustworthiness, and risk. Playbook explicitly names **data drift, model drift**, and need to reassess metrics when operational settings change.

**Primary links:**

- AI RMF PDF: https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf  
- MEASURE Playbook: https://airc.nist.gov/airmf-resources/playbook/measure/  
- MEASURE-2.4 (in-production behavior): https://learn.daydream.ai/requirements/nist-ai-rmf-airmf-61  

**Key playbook quote (paraphrase):** Production AI may encounter new risks as the environment evolves — often called **“drift”** — meaning systems no longer meet original design assumptions; **regular monitoring** enables faster intervention.

**Noetfield mapping:** `confidence_score` + TLE status transitions + audit-export by RID = buyer-visible **MANAGE** loop when evaluate outcomes drift from prior approvals.

---

### 3.2 NIST AI 600-1 — Generative AI Profile

| Field | Value |
|-------|--------|
| **Tier** | T1 |
| **Published** | July 2024 |

**Relevant risk areas:** Confabulation, information integrity, information security, human–AI configuration, data privacy — all can **worsen over time** without monitoring.

**Links:** https://doi.org/10.6028/NIST.AI.600-1 · https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf

**Noetfield mapping:** Copilot + RAG engagements — document **residual GAI risks** in TLE; use drift monitoring in Trust Brief deliverables.

---

### 3.3 ISO/IEC 42001:2023 — Monitoring & model drift

| Field | Value |
|-------|--------|
| **Tier** | T1 |

**What it says:** AIMS requires ongoing monitoring of AI system performance (accuracy, reliability, fairness) to detect **model drift**; management review considers trends and nonconformities. Annex A (industry guidance) treats **drift monitoring** as operational integrity, not optional.

**Links:**

- https://www.iso.org/standard/42001  
- https://www.iso.org/home/insights-news/resources/iso-42001-explained-what-it-is.html  

**Noetfield mapping:** Connector `last_sync` + evidence timestamps = **operational telemetry** narrative for AIMS audits (not certification claim).

---

### 3.4 EU AI Act — Post-market monitoring (Article 72)

| Field | Value |
|-------|--------|
| **Tier** | T1 (EU law) |
| **Applies to** | Providers of **high-risk** AI systems |

**What it says:** Providers must establish a documented **post-market monitoring system** that **actively and systematically** collects, documents, and analyses performance data over the **lifetime** of the system to evaluate **continuous compliance** with Chapter III requirements. Plan is part of technical documentation (Annex IV); Commission template expected per implementing act timeline in regulation.

**Primary links:**

- EUR-Lex regulation: https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng  
- Article 72 (readable): https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-72  
- https://artificialintelligenceact.eu/article/72/  

**Noetfield mapping:** TLE + evidence pack + connector sync = **deployer-side** documentation of monitoring outcomes for Copilot governance programs (distinct from provider CE marking).

---

### 3.5 OECD AI Principles — accountability & monitoring

**Link:** https://legalinstruments.oecd.org/api/print?ids=648&lang=en  

**Drift angle:** Accountability principle implies **measurement and review** over time; 2024 update addresses GenAI integrity and information risks that evolve in production.

---

## 4. Security, policy & configuration drift (T1–T3)

### 4.1 NIST SP 800-53 — CM-6(3) Unauthorized change detection

| Field | Value |
|-------|--------|
| **Tier** | T1 |
| **Control** | Configuration Management |

**What it requires:** Detect changes to configuration settings that were **not authorized**; baseline vs approved change records; alerts, tickets, closure evidence.

**Link:** https://learn.daydream.ai/requirements/nist-sp-800-53-n80053-298  
**Catalog:** https://csrc.nist.gov/projects/risk-management/sp800-53-controls/release-search  

**Noetfield mapping:** Immutable audit log + governance API change control — analog for **policy-as-code** baselines in pilot environments.

---

### 4.2 NIST SP 800-171 — Continuous monitoring (03.12.03)

**What it requires:** Ongoing signals that controls remain effective; identify **control degradation (control drift)**; POA&M and SSP aligned to deployed reality.

**Link:** https://learn.daydream.ai/requirements/nist-sp-800-171-n800171-95  

**Noetfield mapping:** `make ship-verify` + `verify-local-dev` as **internal** continuous check; export for customer CUI programs.

---

### 4.3 NIST Cybersecurity Framework — continuous improvement

**Practice:** Monitor security events and **policy drift**; periodic reassessment (industry implementation guides reference CSF + automation).

**Link:** https://www.nist.gov/cyberframework  

**Crosswalk:** ISACA *Implementing the NIST Cybersecurity Framework Using COBIT 2019* — https://www.isaca.org/resources/cobit

---

### 4.4 Open Policy Agent (OPA) — policy-as-code & drift prevention

| Field | Value |
|-------|--------|
| **Tier** | T3 (CNCF open source) |
| **Role** | Prevent drift at plan time; audit decisions |

**What it is:** Rego policies evaluate JSON (e.g. Terraform plan) **before apply**; audit trail per decision. **Live drift detection** requires pairing with scanners (Cloud Custodian, Steampipe) or cloud events — OPA alone does not scan live state.

**Primary links:**

- https://openpolicyagent.org/  
- Infrastructure drift + OPA patterns: https://policyascode.dev/guides/infrastructure-drift-detection/  

**Noetfield mapping:** Future: evaluate API requests against locked policy bundles; log denials to compliance log (governance drift **blocked** pre-execution).

---

### 4.5 AWS Config — configuration compliance & drift

| Field | Value |
|-------|--------|
| **Tier** | T2 |

**What it is:** Records configuration history; rules flag **noncompliant** resources when actual state deviates from desired; CloudFormation managed rule `CLOUDFORMATION_STACK_DRIFT_DETECTION_CHECK` for stack drift.

**Primary links:**

- How it works: https://docs.aws.amazon.com/config/latest/developerguide/how-does-config-work.html  
- CFN drift check: https://docs.aws.amazon.com/config/latest/developerguide/cloudformation-stack-drift-detection-check.html  
- Concept (re:Post): https://repost.aws/questions/QUFitQT-kTQ_CkqEZL758kjw/what-is-aws-config-drift  

**Noetfield mapping:** Reference architecture for customers deploying platform on AWS; not required for Noetfield product core.

---

## 5. ML & LLM production drift (T2–T3)

### 5.1 AWS Prescriptive Guidance — GenAI drift monitoring

| Field | Value |
|-------|--------|
| **Tier** | T2 |

**What it covers:** LLM performance degradation when inputs/behavior change; **multi-layer** detection — statistical embedding drift + **LLM-as-judge** semantic classification of drift cause (new topic, intent shift, complexity, language style).

**Link:** https://docs.aws.amazon.com/prescriptive-guidance/latest/gen-ai-lifecycle-operational-excellence/prod-monitoring-drift.html  

**Noetfield mapping:** Trust Brief **operating model** for Copilot monitoring; aligns with W56-3 confidence score and cohort review.

---

### 5.2 Data drift vs concept drift — definitions (industry reference)

| Concept | Definition source |
|---------|-------------------|
| **Data drift** | Shift in input (feature) distribution vs training |
| **Concept drift** | Shift in relationship between inputs and target |
| **Model drift** | Degraded predictive performance |

**T3 references (methods, not law):**

- Evidently AI — concept drift: https://www.evidentlyai.com/ml-in-production/concept-drift  
- Deepchecks drift guide (PSI, KS, Cramér’s V): https://docs.deepchecks.com/stable/user-guide/general/drift_guide.html  

**Metrics (widely cited):**

| Metric | Use |
|--------|-----|
| **PSI** (Population Stability Index) | Distribution shift; often &lt;0.1 stable, ≥0.25 significant (organizational thresholds vary) |
| **Kolmogorov–Smirnov** | Continuous feature comparison |
| **Wasserstein distance** | Magnitude of distributional change |

**Noetfield mapping:** Confidence score factors can cite **which drift class** was reviewed (data vs policy vs semantic) in TLE body.

---

### 5.3 OWASP Top 10 for LLM (2025) — behavioral “drift” into unsafe states

**Link:** https://genai.owasp.org/llm-top-10/  

**Relevant risks:** Prompt injection, sensitive disclosure, excessive agency, misinformation, unbounded consumption — production behavior can **drift into** these failure modes without statistical data drift.

**Noetfield mapping:** Evaluate API + pilot rate limits; diligence cross-link in [CONNECTORS_CONTROLS_v1.md](../diligence/CONNECTORS_CONTROLS_v1.md).

---

### 5.4 MITRE ATLAS — adversarial ML & AI system behavior

| Field | Value |
|-------|--------|
| **Tier** | T3 (MITRE-maintained) |

**What it is:** Tactics/techniques for attacks on AI systems (data poisoning, evasion, model theft, etc.) — complements statistical drift monitoring.

**Primary links:**

- https://atlas.mitre.org/  
- Fact sheet PDF: https://atlas.mitre.org/pdf-files/MITRE_ATLAS_Fact_Sheet.pdf  

**Noetfield mapping:** Bank Pilot threat modeling sessions; not a substitute for NIST MEASURE.

---

## 6. Semantic, RAG & epistemic drift (T2–T4)

### 6.1 Semantic drift in RAG (regulated risk)

**Problem:** Same question yields **contradictory** answers when retrieval corpus, embeddings, or prompts change — regulatory and trust exposure (especially financial services).

**T2/T3 sources:**

- AWS Prescriptive Guidance (Layer 2 semantic analysis): see §5.1  
- **T4 (orientation):** TrackAI semantic drift in RAG — https://trackai.dev/tracks/evaluations/hallucination/semantic-drift/  

**Mitigations cited in industry practice:** Index versioning (“commits”), deterministic retrieval config, automated consistency checks, human escalation.

**Noetfield mapping:** Signed TLE fixes **decision** for a point in time; ongoing semantic drift handled via **new evidence + new TLE**, not silent model updates.

---

### 6.2 Epistemic drift — multi-agent / document corpus

**In-repo concept (Noetfield North Star):** Multi-agent **epistemic drift** without observability — see [NORTH_STAR.md](../../NORTH_STAR.md) (OAS / truth system).

**In-repo operational rules (private SOT batches):** Examples in `docs/SOURCE_OF_TRUTH/` — `critical-drift-triage-sla-4h`, manifest hash mismatch → hard stop. Agents with `ops/private/sourceA/` sync may see full semi-notice; git agents use:

- `docs/SOURCE_OF_TRUTH/registry/active_rule_candidates.json` (rule keys: `critical-drift-triage-sla-4h`, manifest drift)  
- Uploaded specs: `docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-011/` (temporal governance, `drift_summary` in evidence packs)

**Noetfield mapping:** Trust Ledger is the **buyer-facing** anti-drift artifact; internal SOT engine is **not** the public product.

---

## 7. EU cybersecurity layer (T1)

### ENISA FAICP — Multilayer Framework for Good Cybersecurity Practices for AI

**Drift angle:** Continuous risk management over AI lifecycle; Layer II AI-specific practices include ongoing monitoring as environment changes.

**Links:**

- https://www.enisa.europa.eu/publications/multilayer-framework-for-good-cybersecurity-practices-for-ai  
- PDF: https://www.enisa.europa.eu/sites/default/files/publications/Multilayer%20Framework%20for%20Good%20Cybersecurity%20Practices%20for%20AI.pdf  

---

## 8. Noetfield control matrix (drift → artifact)

| Drift scenario | Detect with | Record in |
|----------------|-------------|-----------|
| Copilot policy decision differs from last approved TLE | Evaluate + human review | New TLE or Rejected status |
| Evidence metadata stale vs Purview | Connector `last_sync`, ingest timestamps | Connector sync API + diligence doc |
| RID thread inconsistent | Audit-export bundle | Compliance log |
| Approver chain incomplete | API 2-step approve | `PendingApproval` → blocked export |
| Marketing/docs diverge from PRODUCT_TRUTH | `make ship-verify`, semantic lock scripts | CI failure (agent fix) |
| Internal agent answers diverge from locked SOT | Manifest hash / drift_score (internal) | Founder triage — **not** customer API |

---

## 9. Reading order by role

### GRC / Legal (45 min)

1. EU AI Act Art. 72  
2. NIST AI RMF MEASURE Playbook (drift section)  
3. ISO 42001 monitoring explainer  
4. Noetfield [EVIDENCE_INTAKE_CONTRACT_v1.md](../diligence/EVIDENCE_INTAKE_CONTRACT_v1.md)

### ML / Platform (45 min)

1. AWS Prescriptive Guidance prod monitoring drift  
2. Evidently or Deepchecks drift guide (one)  
3. OWASP LLM Top 10  
4. MITRE ATLAS overview

### Bank examiner narrative (30 min)

1. FFIEC audit trail expectations — [GOVERNANCE_SOURCES_HANDBOOK_LOCKED_v1.md](./GOVERNANCE_SOURCES_HANDBOOK_LOCKED_v1.md) §8  
2. NIST SP 800-171 continuous monitoring  
3. Noetfield TLE + audit-export path — [BANK_PILOT_DEMO.md](../BANK_PILOT_DEMO.md)

---

## 10. Master bibliography (drift-focused)

```text
# AI governance monitoring
https://airc.nist.gov/airmf-resources/playbook/measure/
https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf
https://doi.org/10.6028/NIST.AI.600-1
https://www.iso.org/standard/42001
https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-72

# Security & config drift
https://csrc.nist.gov/projects/risk-management/sp800-53-controls/release-search
https://openpolicyagent.org/
https://docs.aws.amazon.com/config/latest/developerguide/how-does-config-work.html
https://policyascode.dev/guides/infrastructure-drift-detection/

# ML / LLM drift
https://docs.aws.amazon.com/prescriptive-guidance/latest/gen-ai-lifecycle-operational-excellence/prod-monitoring-drift.html
https://www.evidentlyai.com/ml-in-production/concept-drift
https://docs.deepchecks.com/stable/user-guide/general/drift_guide.html
https://genai.owasp.org/llm-top-10/
https://atlas.mitre.org/

# EU cyber
https://www.enisa.europa.eu/publications/multilayer-framework-for-good-cybersecurity-practices-for-ai
```

---

## 11. Excluded as primary sources

- Vendor marketing pages that define PSI thresholds without methodology  
- Single blog posts on “AI governance drift” without T1 anchor  
- Unmaintained awesome-lists  
- **Consultancy-only** policy drift pages (e.g. SecurView) — use NIST CM / 800-171 instead  

---

## 12. Version history

| Version | Date | Notes |
|---------|------|-------|
| v1 LOCKED | 2026-06-04 | Initial drift source book; paired with locked governance handbook |

**Next review:** EU post-market monitoring implementing act template · NIST AI RMF refresh · OWASP LLM 2026.
