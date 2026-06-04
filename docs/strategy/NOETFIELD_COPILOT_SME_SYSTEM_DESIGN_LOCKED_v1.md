# Noetfield Copilot for SMEs — System Design (LOCKED v1)

**Status:** LOCKED — reference for future plan, architecture, and phased build  
**Role:** Convert user request into executable governance + operations system (SME scale)  
**Locked:** 2026-06-03  
**Authority:** ASF / product strategy  
**Path:** `docs/strategy/NOETFIELD_COPILOT_SME_SYSTEM_DESIGN_LOCKED_v1.md`  
**Supersedes:** Informal chat-only versions of this spec  

**Related locks:** [PRODUCT_TRUTH.md](../../PRODUCT_TRUTH.md) · [PROJECT_BOUNDARIES_LOCKED.md](../../PROJECT_BOUNDARIES_LOCKED.md) · [OFFERINGS_LOCKED.md](../../OFFERINGS_LOCKED.md) · [tenant-append-only-audit-schema-outline.md](../spec/tenant-append-only-audit-schema-outline.md)

---

## Agent analysis (read first)

### What this document is

A **full-stack SME operating model** spanning finance ledger, workflow, compliance, AI agents, and knowledge/RAG — with MVP→90-day roadmap and ship-ready artifacts (OpenAPI, DDL, DSL, tests).

### Noetfield boundary alignment (critical)

Per [PRODUCT_TRUTH.md](../../PRODUCT_TRUTH.md), **Noetfield does not** run payment rails, custody, settlement, FX, or money transmission. This locked spec is therefore split into three lanes:

| Lane | Domains in this doc | Noetfield repo? |
|------|---------------------|-----------------|
| **A — Noetfield core (build here)** | Compliance/Governance, AI Automation (guardrails + audit), Knowledge/Decisions (evidence-first Q&A), Cross-domain controls, Trust Ledger Bridge (signed intent + append-only) | **Yes** — aligns with Copilot Governance Pack, Bank Pilot shadow, governance console |
| **B — Partner / external execution** | Finance/Ledger payments connector, loan disbursement, treasury disbursement approval touching funds | **No** — partner MSB/bank/credit union systems execute; Noetfield pre-execution only |
| **C — Future SME product line (gated)** | Full Finance/Ledger module, member portal contributions, payment reconciliation at scale | **Design only** until ASF activates separate SKU or registry entry |

### Noetfield MVP extraction (executable subset from this lock)

Use this subset for `os/plan.json` and engineering until Lane C is activated:

1. **Policy Repository + Control Registry + Risk Register** (Compliance domain) — markdown/schema first, then API  
2. **Workflow Engine lite** — onboard → assess → signoff → ledger write (Operations domain, no payments)  
3. **Agent Framework** — preflight, scoped permissions, agent run audit, human-in-the-loop (AI domain)  
4. **Trust Ledger Bridge** — RID, signed digest, evidence index (already in flight: `audit_events`, `/evaluate`)  
5. **Knowledge/RAG** — evidence-first answers; block without verified source (Phase 3.5+ per [noetfield-future-path.md](./noetfield-future-path.md))  

### Conflicts to resolve with ASF (not blockers for Lane A)

| Item in spec | Noetfield lock | Resolution |
|--------------|----------------|------------|
| Payments Connector, EFT, mobile money | No payments | Connector = **read-only** feeds for reconciliation evidence; execution external |
| Loan disbursement / Treasury Agent approve funds | No custody | Treasury Agent = **governance signoff** only; disbursement in partner system |
| “Trust Ledger” as blockchain | Not required | **Signed records + append-only store** (spec already says this) |
| Multi-member ledger at MVP | Heavy for v1 | Pilot: **audit_events + export**; full ledger Phase C |

### Implementation roadmap mapping (this doc → repo)

| Spec milestone | Maps to |
|----------------|---------|
| Week 0–2 append-only ledger | `docs/spec/tenant-append-only-audit-schema-outline.md`, governance-console |
| Week 3–6 workflow + evidence | `governance-console`, `services/workflow`, Copilot quickscan flows |
| Week 7–10 agents + compliance engine | `services/governance`, `services/copilot-governance`, Agent manifests |
| Week 11–12 pilot | [docs/GOVERNANCE_PILOT_RUNBOOK.md](../GOVERNANCE_PILOT_RUNBOOK.md), Bank Pilot, Copilot pack |

### Future agent instruction

When ASF says **implement** from this lock: pick **one** Lane A module task in `os/plan.json`; do not implement Lane B payment execution in Noetfield repo; cite this file section in YAML evidence.

---

## Output contract (unchanged from source)

For each domain: **System Design (modules)** · **Execution Flow** · **Data Objects** · **Agents** · **Risks/Controls** · **Implementation Output**.

**Assumptions:** SME scale · Microsoft 365 + cloud storage · phased rollout MVP → automation · no clarifying questions.

---

# Domain specifications (locked source)

## Finance / Ledger

### System Design (modules)

- **Ledger Core** — multi-member ledger, transactions, balances, reconciliation engine.
- **Contributions & Loans** — member contributions, loan issuance, repayment schedules.
- **Payments Connector** — payment rails (card, EFT, mobile money) and reconciliation adapters.
- **Compliance & Privacy** — POPIA/GDPR mapping, PII encryption, retention policies.
- **Analytics & Reporting** — contribution trends, delinquency, cashflow, audit exports.
- **Trust Ledger Bridge** — signed intent records and evidence pointers (not blockchain; signed records + append-only store).

### Execution Flow

1. Member Onboard → create member record; capture KYC minimal fields; generate member ID.
2. Contribution Event → create transaction; validate against schedule; store evidence (receipt, bank reference).
3. Payment Reconciliation → ingest payment feed; match transactions; flag mismatches.
4. Loan Lifecycle → create loan object; amortization schedule; record disbursement and repayments.
5. Monthly Close → run reconciliation, generate board-ready report, write immutable ledger entry with evidence links.
6. Audit Request → export ledger slice + evidence bundle; mark verification status.

### Data Objects

- **Member:** member_id; name; contact; KYC_hash; consent_flags; role.
- **Transaction:** tx_id; member_id; amount; type; timestamp; payment_ref; evidence_links.
- **Loan:** loan_id; member_id; principal; schedule; status; collateral_ref.
- **ReconciliationRecord:** rec_id; tx_id; payment_feed_id; match_status; exception_reason.
- **LedgerEntry:** entry_id; period; summary; signed_digest; evidence_index.
- **AuditBundle:** bundle_id; entries[]; signatures[]; export_hash.

### Agents

| Agent | Permissions / actions |
|-------|------------------------|
| Finance Agent (operator) | create transactions; initiate reconciliations; view PII masked |
| Treasury Agent (approver) | approve disbursements/loans; sign ledger entries |
| Auditor (read-only) | read ledger, download audit bundles, mark verification |
| Member Portal (limited) | submit contributions; view own balance; download receipts |
| System Agent (automated) | ingest payment feeds; auto-match; reconciliation suggestions |

**Permissions:** RBAC least privilege; dual-approval for high-value transactions.

### Risks / Controls

- Payment mismatches → automated reconciliation + exception queue + SLA.
- Unauthorized ledger edits → append-only entries + signed digests + change audit trail.
- PII leakage → field-level encryption, tokenization, access logging.
- Late repayments → delinquency alerts; grace periods; escalation workflow.

### Implementation Output

- OpenAPI: Member, Transaction, Loan, Reconciliation, LedgerEntry.
- DB schema: normalized tables.
- Events: `contribution.created`, `payment.feed.ingested`, `reconciliation.completed`.
- MVP UI: Member Onboard; Contribution Entry; Reconciliation Dashboard; Monthly Close export.
- Acceptance: contribution → payment feed → reconciliation → signed ledger entry.

---

## Operations / Workflow

### System Design (modules)

- Workflow Engine — state machine (onboard → contribution → audit).
- Task & Action Manager — assign, track, escalate; SLA timers.
- Evidence Capture — attachments, links, connector ingestion.
- Notification & Escalation — email/SMS/webhook; retry policies.
- Audit Trail & Immutable Writes — append-only event log per state change.

### Execution Flow

1. Trigger starts workflow (e.g. monthly close).
2. Collect Evidence tasks (bank statements, receipts).
3. Human steps with deadlines; upload evidence or mark complete.
4. Automated validation (totals, signatures, policy rules).
5. Decision: pass → ledger entry; fail → remediation + escalate.
6. Close: final audit record + notify stakeholders.

### Data Objects

- **WorkflowInstance:** id; type; state; owner; created_at; due_at.
- **Task:** task_id; workflow_id; owner; status; sla_deadline; evidence_links.
- **Evidence:** evidence_id; source; hash; storage_ref; ingestion_timestamp.
- **EventLog:** event_id; workflow_id; actor; action; timestamp.

### Agents

- Workflow Operator — create/modify workflows; dashboards.
- Task Owner — perform tasks; upload evidence; extensions.
- Verifier — validations; verification status.
- Escalation Agent (system) — auto-escalate overdue tasks.

### Risks / Controls

- Task drift → SLA timers, auto-escalation, KPIs.
- Evidence tampering → hashing, immutability, access logs.
- Orphan workflows → periodic reconciliation job.

### Implementation Output

- Workflow DSL (JSON): states, transitions, validations.
- Task API: create/assign/update; attach evidence.
- Connectors: bank feeds, SharePoint, OneDrive, email.
- Runbook: SLA, escalation matrix, onboarding checklist.

---

## Compliance / Risk / Governance

### System Design (modules)

- Policy Repository — canonical policies, versions, effective dates.
- Control Registry — controls mapped to policies and risks.
- Risk Register — likelihood, impact, owner, mitigation.
- Compliance Engine — evaluate artifacts against policies.
- Verification & Signoff — human signoff + cryptographic signatures.

### Execution Flow

1. Policy Publish → versioned store; notify subscribers.
2. Control Mapping → clauses + evidence requirements.
3. Assessment → compliance checks on artifacts.
4. Exception Handling → risk object + remediation tasks.
5. Signoff → owners sign; record in Trust Ledger.

### Data Objects

- **Policy:** policy_id; title; text_ref; version; effective_date; owner.
- **Control:** control_id; policy_id; description; test_procedure; evidence_requirements.
- **Risk:** risk_id; description; likelihood; impact; owner; status.
- **AssessmentResult:** assessment_id; artifact_id; control_id; result; evidence_links.

### Agents

- Policy Owner — CRUD policies; approve mappings.
- Control Tester — tests; evidence; pass/fail.
- Risk Manager — risks; mitigations.
- Compliance Officer — engine runs; approve exceptions.

### Risks / Controls

- Policy drift → lifecycle + review reminders + re-approval.
- False pass → independent testers; sampling; audits.
- Unauthorized policy changes → versioning + dual-approval + ledgered signoff.

### Implementation Output

- Policy JSON schema + evidence requirements.
- Control test runner API.
- Compliance dashboard heatmap.
- Signoff artifact format (who, when, evidence refs, signature hash).

---

## AI Automation / Agents

### System Design (modules)

- Agent Framework — permissions, scopes, tool-call validation.
- Prompt Studio — JSON templates (Goal, Context, Sources, Constraints, Output, Verification).
- Execution Guardrails — runtime policy enforcement.
- Agent Audit Trail — inputs, outputs, tool calls, evidence.
- Human-in-the-loop UI — approve/reject high-risk actions.

### Execution Flow

1. Agent Request via Prompt Studio.
2. Preflight: scope, permissions, policy constraints.
3. Execute tasks (board brief, control mapping).
4. Verification: evidence + control tests.
5. Human approval if required.
6. Ledger write: output + evidence + agent metadata.

### Data Objects

- **AgentProfile:** agent_id; version; allowed_actions; data_scopes; owner.
- **AgentRun:** run_id; agent_id; prompt_json; inputs; outputs; tool_calls; status.
- **ToolCallRecord:** call_id; run_id; tool_name; params_hash; response_ref.
- **VerificationRecord:** verification_id; run_id; checks[]; status.

### Agents

- Board Agent — board packs; human signoff for final.
- Risk Agent — draft risk objects.
- Policy Agent — draft policies; owner approval.
- Audit Agent — audit plans; schedule tasks.

**Permissions:** scoped tokens; least privilege; deny-by-default; immutable versioning.

### Risks / Controls

- Agent overreach → guardrails; deny-by-default.
- Non-verifiable outputs → evidence links + verification before ledger write.
- Model drift → versioning; re-certification; test harness.

### Implementation Output

- Agent manifest (YAML/JSON).
- Prompt Studio library (`board_brief.json`, `risk_assessment.json`, `policy_draft.json`).
- Agent run API: preflight + post-run verification.
- Agent audit UI: history, diff, replay, signoff.

---

## Knowledge / Documents / Decisions

### System Design (modules)

- Knowledge Graph — RAG index (policies, minutes, evidence, controls).
- Semantic Search — vector store + metadata filters.
- Decision Store — canonical decisions + evidence.
- Answering Engine — Answer + Evidence + Sources + Confidence + Verification.
- Provenance Layer — source pointers, extraction method, verification steps.

### Execution Flow

1. Ingest documents with metadata + vectors.
2. Query → RAG pipeline.
3. Retrieve top-k with evidence links.
4. Synthesize with evidence mapping + confidence.
5. Verify (current policy? signed decision?).
6. Store QueryRecord for audit.

### Data Objects

- **Doc:** doc_id; title; type; source_ref; vector; last_verified.
- **Decision:** decision_id; summary; owners; date; evidence_links; status.
- **QueryRecord:** query_id; user; query_text; answer; evidence_refs; confidence; verification_status.

### Agents

- Knowledge Curator — approve sources; verification cadence.
- Decision Owner — confirm answers affecting policy/controls.
- Consumer — query; request evidence bundle.

### Risks / Controls

- Hallucination → never-return-without-evidence; verified source required.
- Stale sources → last_verified TTL; block expired.
- Sensitive exposure → PII redaction; access filters.

### Implementation Output

- Ingestion pipeline + vectorizer + verification tagger.
- RAG config (k, reranker, synthesis templates).
- Answer schema: `{answer, evidence[], sources[], confidence, verification_status}`.
- QueryRecord retention + export API.

---

## Cross-domain operational controls (global)

1. **Immutable ledger writes** — final decisions, signoffs, policy changes → signed ledger entry + evidence refs.
2. **RBAC + approval matrix** — dual-approval for high-risk; policy table maps roles → actions.
3. **Evidence-first rule** — no assertive financial/compliance/decision output without evidence + verification status.
4. **Human-in-the-loop thresholds** — monetary/compliance severity → forced manual approval.
5. **Monitoring & KPIs** — task SLA, reconciliation accuracy, agent pass-rate, knowledge freshness.

---

## Implementation roadmap (MVP → 90 days)

| Window | Milestones |
|--------|------------|
| **Week 0–2** | DB schemas, API stubs Member/Transaction/Workflow; Prompt Studio skeletons; append-only ledger store |
| **Week 3–6** | Payment ingestion + reconciliation; workflow + evidence; basic knowledge index |
| **Week 7–10** | Agent framework + audit; compliance engine + control runner; RAG + verification hooks |
| **Week 11–12** | Pilot 1–2 SMEs QuickScan→Readiness; RBAC, encryption, audit exports; E2E acceptance tests |

---

## Deliverables (ready-to-ship)

- OpenAPI all domain endpoints
- DB migrations + ERD
- Prompt Studio template library (JSON)
- Agent manifests (BoardAgent v1, RiskAgent v1)
- Workflow DSL (`MonthlyClose.workflow.json`)
- Acceptance tests (Cypress/Postman)
- Pilot runbook + onboarding checklist

---

## Operational assumptions (inferred)

- Microsoft 365 + cloud storage; connectors: OneDrive, SharePoint, bank CSV, email.
- Signing: HSM or cloud KMS.
- Scale: single-tenant pilot → multi-tenant RBAC Phase 5.

---

## Next engineering handoff (on request)

Convert any single domain into sprint backlog (stories, acceptance criteria, OpenAPI, DDL, wireframes).

---

**END — LOCKED v1. Do not edit without ASF unlock.**
