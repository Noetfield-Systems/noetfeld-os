# Noetfield Company Workforce Charter v1

**Status:** Internal operating design — registry and validation implementation  
**Version:** 1.0.0  
**Canonical machine registry:** `noetfield-org/COMPANY_WORKFORCE_REGISTRY_v1.json`  
**Schema:** `schemas/noetfield-company-workforce-v1.schema.json`  
**Authority:** Founder / CEO  
**Scope:** Noetfield Systems Inc. company workforce; not a public product specification

## 1. Purpose

Noetfield will operate as an **Agent-Native company**. Its organizational chart defines business responsibilities; the runtime assigns one or more governed digital workers to execute bounded tasks inside those responsibilities. Human and digital workers share operating objectives, task ownership, evidence, and performance measurement, but they do not share legal status or unrestricted authority.

This Charter implements an internal workforce layer on top of existing NOOS capabilities. It does not create a second scheduler, dispatcher, model router, memory platform, or governance stack.

## 2. Company boundary

This workforce serves the company described in the current company-strategy blueprint: an AI-native systems company and product studio operating three commercial fields—Enterprise AI Governance, Custom AI Motors & Operating Workflows, and Investor Workflows & Evidence-Based Audits—on an internal governed-execution layer.

The referenced company strategy blueprint is still marked pending SG ratification. This Charter does not ratify, amend, or supersede it. It also does not change Noetfield OS's product SSOT or public website claims.

The NOOS `AGENT_REGISTRY.md` remains the registry of repository-level agents and cross-repository synchronization roles. It is not the company employee chart. The new Company Workforce Registry defines business functions and maps them to existing NOOS workers where evidence supports that mapping.

## 3. Organization

```
Founder / CEO — H-001 (Human Principal)
│
├── N-01 Chief of Staff & Operations
│   ├── N-02 Strategic Intelligence & Opportunities
│   ├── N-03 Product & Engineering Delivery
│   └── N-06 Marketing & Communications
│
├── N-04 Assurance, Security & Independent Verification
│
├── N-05 Revenue & Strategic Partnerships
│   └── N-07 Community & Customer Success
│
└── N-08 Finance & Corporate Operations
```

This is a functional reporting model, not a claim that eight separate model processes are deployed. N-01 through N-08 are stable organizational seats. Each seat can be fulfilled by existing workers, one dedicated agent, or a bounded set of specialist workers. Specialist agents are normally ephemeral and subordinate to a seat owner.

### Current human capacity

- **H-001 Founder / CEO:** active human principal; retains company direction, capital, legal commitments, material risk acceptance, and autonomy-tier ratification.
- Future seats are conditional, not current headcount: Enterprise Commercial Lead, Platform & Security Engineer, and Solutions & Implementation Lead. They are added only when the relevant work volume and bottleneck are evidenced.

## 4. Digital-worker role contracts

Every digital-worker role must be instantiated from the machine-readable registry. Each run must bind:

1. **Identity:** stable role ID plus a unique runtime worker identity.
2. **Principal:** who issued or owns the mandate.
3. **Mandate:** objective, scope, target resources, constraints, acceptance conditions, and expiry.
4. **Context:** only the current task's relevant SSOT, role charter, task state, and retrieved evidence.
5. **Memory:** role-scoped durable facts and task-scoped state; no unrestricted cross-role memory.
6. **Tools:** explicit allowlist, provider route, and resource scope.
7. **Authority:** maximum action level and approval boundary.
8. **Evidence:** run ID, tool events, policy decisions, outputs, cost, and receipt/trace reference.
9. **Evaluation:** role-specific KPIs, quality checks, and adversarial tests.

A prompt alone is not an employment contract, authorization mechanism, or security boundary.

## 5. Eight company roles

| ID | Role | Primary value | Initial implementation state |
|---|---|---|---|
| N-01 | Chief of Staff & Operations Officer | Coordination and founder operating picture | Mapped to existing NOOS integrator/loops |
| N-02 | Strategic Intelligence & Opportunity Officer | Finds high-value market and ecosystem opportunities | Partial discovery workflow; full intelligence lane not yet verified |
| N-03 | Product & Engineering Delivery Officer | Converts priorities into tested product increments | Mapped to existing code-agent and worker-kernel capabilities |
| N-04 | Assurance, Security & Independent Verification Officer | Prevents unsafe, unverified, or unsupported work from shipping | Mapped to existing CI, critic, audit, and security checks |
| N-05 | Revenue & Strategic Partnerships Officer | Turns qualified opportunities into pipeline and partner progress | Existing commercial preparation; outbound remains Founder-gated |
| N-06 | Marketing & Communications Officer | Evidence-led positioning, content, and distribution | Draft/PR-only; no autonomous publishing |
| N-07 | Community & Customer Success Officer | Inbound response, onboarding, retention, and feedback | Not wired; requires inbox/helpdesk and approved knowledge |
| N-08 | Finance & Corporate Operations Officer | Financial visibility and administrative discipline | Not wired; read-only source required |

The authoritative responsibilities, context sources, memory boundaries, tool allowlists, approval conditions, forbidden actions, KPIs, and component references are in the JSON registry. Do not maintain a conflicting second copy in prompts or other documents.

## 6. Authority model

Company authority levels A0–A4 are distinct from NOOS executor tiers T0–T3.

| Level | Meaning | Digital-worker use |
|---|---|---|
| A0 | Observe | Read approved sources |
| A1 | Analyze and recommend | Produce findings and recommendations |
| A2 | Draft and write internal artifacts | Drafts, issues, internal records |
| A3 | Bounded reversible execution | Sandbox, branch, and approved internal workflows |
| A4 | External, financial, legal, production, or irreversible authority | Human-reserved; never autonomous |

No digital worker receives A4. High-impact acts require a specific human approval and an execution-time permit. Role definitions do not override repository-specific controls or the existing L17 routing matrix.

### Human approval is mandatory for

- Sending external commercial messages or replies.
- Publishing public content, press statements, or investor communications.
- Pricing, discounts, proposals, contracts, and partner commitments.
- Money movement, banking, tax, and legal filings.
- Production deployment, protected-branch release, or irreversible infrastructure changes.
- Weakening or changing laws, schemas, verifiers, or policy gates.
- Expanding model spend, worker authority, or autonomy tier.

## 7. Runtime and orchestration

Use the existing control plane:

- **Role and worker inventory:** this Company Workforce Registry plus the existing NOOS parallel-agent and repository registries.
- **Task arbitration and claims:** existing NOOS integrator protocol.
- **Bounded worker execution:** existing worker kernel and approved coding-agent surfaces.
- **Machine validation, critique, repair, and audit:** existing Machine Loops and CI.
- **Model selection and spend:** existing `config/model-router.yml`.
- **Tool routing:** existing `noetfield-org/ROUTING_MATRIX.md`.
- **Evidence:** existing receipt and trace systems.

Do not add another orchestrator. A company role is a functional owner and routing key; an executor tier describes which machine surface can perform the work.

### Execution modes

- **Event-driven:** run only when a verified event arrives (issue, PR, contact form, system alert).
- **Scheduled:** execute deterministic checks at a known cadence, and call an LLM only when analysis is needed.
- **Request-driven:** run for a Founder-approved or role-authorized task.
- **Long-running:** preserve explicit state, mandate expiry, budget, checkpoints, and cancellation. It is not an unbounded chat loop.

“24/7” means the service can receive and process authorized events continuously; it does not mean an LLM is continuously generating tokens.

## 8. Context, RAG, and memory

These concepts must remain separate:

- **Rules / Policy:** what the worker may or may not do; enforced outside the model.
- **Context:** the bounded information assembled for one run.
- **RAG:** retrieval of relevant, source-attributed documents for the current task.
- **Memory:** durable, approved facts or task state that can be reused.
- **Chunking:** an indexing/retrieval technique, not an authority or memory model.
- **Workflow:** the deterministic or semi-deterministic sequence connecting events, agents, and tools.
- **Agent loop:** the bounded observe–decide–act–evaluate cycle.

Use Company SSOT for company facts; role memory for domain knowledge; task memory for in-flight work; episodic history for dated events; and external knowledge for attributed sources. Do not put all company information into one unrestricted vector store. Do not store private chain-of-thought.

## 9. Role independence and separation of duties

- N-03 creates; N-04 independently verifies. The same execution identity must not author and approve a critical change.
- N-02 validates opportunity evidence; N-05 owns pipeline progression and outreach drafts.
- N-06 prepares public content; an authorized human approves publishing.
- N-07 can answer only from approved support knowledge once an inbound connector and privacy boundary exist.
- N-08 can prepare reports from approved records but never move money or submit statutory filings.
- N-01 coordinates; it does not override the mandate, policy, or independent verifier.

## 10. Activation order

1. **W0 — Register and validate:** completed in this implementation branch once CI passes.
2. **W1 — Reuse existing core capabilities:** verify N-01, N-03, and N-04 against live workers and receipts; do not redeploy duplicate systems.
3. **W2 — Build intelligence-to-revenue:** establish N-02 source watchlists and opportunity records; connect N-05 to a pipeline source. Continue to require human approval for all outbound messages.
4. **W3 — Build audience and customer operations:** N-06 drafts and PRs only; N-07 remains inactive until one inbound channel, approved support knowledge, identity, consent, and retention are defined.
5. **W4 — Finance visibility:** N-08 remains inactive until a read-only accounting source is approved and reconciled.

## 11. Performance and review

Evaluate roles by outcomes, not message count or token consumption. Role KPIs are specified in the registry. All roles also report reliability, cost per accepted outcome, human intervention rate, and policy violations. Unauthorized action attempts must be recorded; a successful result does not excuse a policy violation.

Review this registry when a role changes scope, a new connector is granted, a worker is promoted to a higher autonomy level, or a human seat is added. Increment the schema or registry version for breaking changes. Runtime activation requires evidence and must not be inferred from a registry status alone.

## 12. What this implementation does—and does not—activate

This branch adds the company workforce charter, machine-readable role registry, schema, semantic validator, regression tests, and CI enforcement. It maps known existing capabilities without launching new always-on LLM jobs or granting new external permissions.

No API key, CRM, email, helpdesk, accounting, or banking connector is assumed to exist. No production deployment or external communication is triggered by this implementation. Those steps require connector-specific authorization and their own verification.
