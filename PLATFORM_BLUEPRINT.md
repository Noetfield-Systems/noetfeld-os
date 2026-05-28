# Noetfield Platform Blueprint

## 1. Purpose of this document

This document is the architecture constitution for Noetfield's transition from a
brand and presentation-layer repository into an enterprise AI governance
platform.

The current repository is a vision, narrative, and static frontend layer. The
target platform is a real-time AI governance operating system for regulated
organizations. This blueprint defines the product identity, system boundaries,
core architecture, domain model, event model, security posture, deployment
model, and phased roadmap that future implementation should follow.

This document should be updated deliberately when core platform assumptions
change. Product pages, services, data models, and AI capabilities should align
with this blueprint unless the blueprint itself is revised.

## 2. Current state

The repository currently contains:

- Brand and narrative layer
- Static landing pages
- AI governance positioning
- Service offering structure
- Conceptual Trust Ledger material
- Static frontend shell
- Prototype fintech and payments concepts
- External intake and payment links

The repository is currently best understood as:

> AI governance vision platform

It is not yet:

> AI governance operating system

The next stage must introduce a durable operational core before significant
feature expansion. Without that foundation, the platform risks accumulating
duplicated abstractions, inconsistent governance models, workflow debt, AI
chaos, security debt, and weak auditability.

## 3. Vision

Noetfield is AI trust infrastructure for regulated organizations.

The platform gives enterprises a live, auditable governance system for AI
systems, AI agents, models, vendors, policies, controls, evidence, approvals,
human oversight, incidents, and board reporting.

The highest-level product vision is:

> A real-time AI Governance Operating System for regulated enterprises.

The platform should behave less like a static compliance dashboard and more
like a living governance runtime:

- Every meaningful action is attributable.
- Every governance decision is versioned.
- Every AI-assisted output is reviewable.
- Every workflow has state and ownership.
- Every policy decision has evidence.
- Every audit package can be reconstructed.
- Every enterprise deployment can prove who did what, when, why, and under
  which policy context.

## 4. Product positioning

### 4.1 Primary positioning

Noetfield should be positioned as:

> AI Trust Infrastructure for regulated organizations.

The first target market should be regulated enterprises, not banks only.
Banking-grade architecture should shape the system from day one, but the market
positioning should remain broad enough to support:

- Financial services
- Fintech
- Healthcare
- Insurance
- Government
- Legal and compliance teams
- Enterprises in the Microsoft ecosystem

This avoids premature over-specialization while preserving the ability to meet
bank-grade requirements.

### 4.2 Strategic wedge

The strongest initial wedge is:

> Microsoft Copilot Governance

Rationale:

- Enterprises already use Microsoft 365.
- Copilot adoption is accelerating.
- Security and compliance teams lack visibility.
- Boards need understandable reporting.
- Procurement needs defensible controls.
- Microsoft Entra ID and Microsoft Graph provide a natural integration path.

The Copilot wedge should lead into the broader AI governance platform, not
remain a standalone consulting offer.

### 4.3 Product hierarchy

Recommended structure:

- Noetfield: company and platform identity
- Trust Ledger: core governance memory and audit engine
- Copilot Governance: first wedge product and module
- AI Inventory: system-of-record module for AI systems and agents
- Evidence Vault: evidence and artifact lifecycle module
- Policy Engine: obligations, controls, rules, exceptions, and approvals
- Board Reporting: executive and regulatory reporting module
- Runtime Command Center: real-time governance operations layer

### 4.4 Fintech and payments material

Existing fintech and payments material should not be treated as the primary
identity of Noetfield.

It should be reframed as:

> A regulated-industry governance demo.

Potential framing:

- AI governance for payments workflows
- Vendor oversight for fintech systems
- Model governance for transaction monitoring
- Human oversight for regulated financial automation
- Evidence and auditability for high-risk operational AI

This preserves useful prior work while removing brand confusion.

## 5. Core principles

The platform should follow these principles.

### 5.1 Auditability first

Auditability is a first-class product feature, not an afterthought. The system
must be able to reconstruct governance history from durable records.

### 5.2 Humans govern, AI assists

AI can summarize, classify, recommend, and draft. Humans approve, own, override,
and remain accountable for governance decisions.

### 5.3 Workflow-first, agent-later

The system should begin with deterministic workflows, approval chains, policy
checks, and evidence lifecycle management. AI agents can later operate inside
approved workflows with clear boundaries.

### 5.4 Event-centric architecture

Important actions should emit canonical governance events. Events form the
backbone of audit, reporting, real-time updates, integrations, and automation.

### 5.5 Deterministic governance

Every action should be:

- Attributable
- Timestamped
- Versioned
- Reviewable
- Reversible where business rules allow
- Exportable
- Linked to policy and evidence context

### 5.6 Tenant isolation by design

Multi-tenancy, single-tenancy, and isolated enterprise deployment must be
considered from the beginning. Tenant boundaries should be visible in identity,
data, events, storage, logs, configuration, and integrations.

### 5.7 Compliance mapping is structured data

Compliance obligations, control mappings, evidence requirements, and framework
relationships should be modeled as structured data, not page copy or ad hoc
text.

### 5.8 AI outputs are governed artifacts

Prompts, retrieved context, model outputs, evaluations, human reviews, and final
decisions should be treated as governed artifacts with retention, access
control, and audit trails.

## 6. Non-goals

The platform should not become:

- A generic chatbot product
- An autonomous agent playground
- A blockchain-first compliance system
- A collection of disconnected dashboards
- A large microservice estate before domain boundaries are proven
- A generic AI SaaS application without governance depth
- A consulting-only site with no operational core

The platform should be:

- Event-centric
- Governance-centric
- Workflow-centric
- Audit-centric
- Enterprise-ready
- AI-assisted, not AI-uncontrolled

## 7. Recommended technical stack

### 7.1 Public site

The public site can remain static in the near term, but the target stack should
be:

- Next.js
- React
- TypeScript
- Tailwind CSS
- Static generation for marketing pages
- Structured metadata and SEO
- Conversion-focused intake flows

### 7.2 Governance application frontend

Recommended application frontend:

- Next.js
- React
- TypeScript
- Tailwind CSS
- TanStack Query for server state
- Recharts or equivalent for operational reporting
- Zustand only where lightweight client state is useful

Frontend responsibilities:

- Tenant-aware navigation
- Governance work queues
- AI inventory management
- Evidence lifecycle UI
- Policy and control management
- Approval workflows
- Live command center views
- Board report builders
- Audit package exports

### 7.3 Backend

Recommended primary backend:

- Python
- FastAPI
- PostgreSQL
- Redis
- Celery, Dramatiq, or equivalent task processing
- Temporal or equivalent workflow engine when workflow complexity requires it

Rationale:

- Strong AI and data ecosystem
- Fast API development
- Clear typing support
- Good fit for orchestration and compliance automation
- Easier integration with model evaluation and document intelligence pipelines

### 7.4 Infrastructure

Recommended strategic cloud:

- Microsoft Azure

Rationale:

- Entra ID alignment
- Microsoft 365 and Copilot ecosystem
- Enterprise procurement fit
- Strong adoption in financial services, government, and regulated enterprises
- Azure OpenAI deployment path

The architecture should remain portable enough to support AWS, private cloud,
or sovereign deployment when enterprise requirements demand it.

## 8. Logical system architecture

The platform should be organized around these logical components.

### 8.1 Public Site

Responsibilities:

- Market positioning
- Product education
- Lead capture
- Procurement confidence
- Case studies
- Security and compliance posture
- Conversion to intake or platform trial

### 8.2 Identity Service

Responsibilities:

- Authentication
- SSO integration
- MFA enforcement
- Session and device controls
- User and group synchronization
- Service accounts
- API keys
- Tenant membership
- Role and attribute assignment

### 8.3 Governance Service

Responsibilities:

- AI system registry
- Vendor registry
- Control library
- Policy library
- Obligation mapping
- Risk classification
- Exceptions and waivers
- Regulatory framework mappings

### 8.4 Trust Ledger Service

Responsibilities:

- Append-only governance events
- Evidence history
- Approval history
- Policy version history
- Risk state transitions
- AI output review history
- Audit reconstruction
- Tamper-evident export packages

### 8.5 Workflow Engine

Responsibilities:

- Approval chains
- Evidence review workflows
- Incident workflows
- Policy exception workflows
- Escalations
- SLAs and due dates
- State machines
- Human task queues
- Workflow event emission

### 8.6 AI Runtime Service

Responsibilities:

- Model routing
- Prompt templates
- Retrieval context management
- Prompt and output logging
- AI evaluation
- Citation generation
- Human review chains
- Safety boundaries
- Usage monitoring
- AI-assisted drafting and summarization

### 8.7 Evidence Service

Responsibilities:

- Evidence upload
- Evidence metadata
- Evidence expiry
- Versioning
- Retention rules
- Access control
- Document extraction
- Evidence-to-control mapping
- Evidence package export

### 8.8 Reporting Service

Responsibilities:

- Board reports
- Executive summaries
- Regulatory mappings
- Control status reports
- Risk heatmaps
- Audit evidence packages
- Point-in-time snapshots
- Scheduled exports

### 8.9 Realtime Service

Responsibilities:

- WebSocket or server-sent event delivery
- Live workflow updates
- Live control health
- Live incident status
- Live evidence freshness
- Live AI activity monitoring
- Event stream fan-out to user interfaces

### 8.10 Integration Layer

Responsibilities:

- Microsoft Graph connectors
- Entra ID connectors
- ServiceNow connectors
- Jira connectors
- Slack and Teams notifications
- SIEM integrations
- GRC platform integrations
- Webhooks
- Enterprise API integration

### 8.11 Observability Platform

Responsibilities:

- Application logs
- Security logs
- Audit logs
- Metrics
- Traces
- Workflow execution monitoring
- AI usage monitoring
- Event bus monitoring
- Alerting

## 9. Domain model

The domain model should be explicit and stable. Early shortcuts here will create
audit and workflow problems later.

### 9.1 Core entities

| Entity | Purpose |
| --- | --- |
| Organization | Customer or enterprise boundary. |
| Tenant | Deployment and data-isolation boundary within or for an organization. |
| User | Human actor in governance workflows. |
| Group | Identity provider or internal grouping of users. |
| Role | Permission bundle such as admin, owner, reviewer, auditor. |
| Attribute | ABAC input such as region, business unit, data class, or clearance. |
| AI System | Governed AI-enabled system, workflow, application, or agent. |
| AI Agent | Autonomous or semi-autonomous AI actor inside a governed system. |
| Model | Foundation model, fine-tuned model, classifier, or deterministic model. |
| Dataset | Data asset used by an AI system or model. |
| Vendor | External provider, SaaS platform, model provider, or service partner. |
| Policy | Internal policy governing acceptable AI use and controls. |
| Control | Specific control requirement linked to obligations and evidence. |
| Obligation | Requirement from a framework, regulation, contract, or internal policy. |
| Framework | NIST AI RMF, ISO 42001, EU AI Act, SOC 2, OSFI, FFIEC, etc. |
| Risk | Identified risk with owner, severity, likelihood, and mitigation. |
| Evidence | File, record, attestation, integration signal, or generated artifact. |
| Approval | Human decision linked to a policy, workflow, evidence item, or risk. |
| Incident | Governance, security, model, policy, or operational event requiring response. |
| Exception | Approved deviation from a policy or control. |
| Workflow | Stateful process involving tasks, approvals, events, and outcomes. |
| Board Report | Executive-ready point-in-time governance report. |
| Audit Package | Exportable evidence bundle for auditors, regulators, or procurement. |
| Governance Event | Immutable event emitted by a meaningful system or human action. |

### 9.2 AI System attributes

An AI System should include:

- Name
- Description
- Business owner
- Technical owner
- Business unit
- Jurisdiction
- Use case
- User population
- Data classification
- Model dependencies
- Vendor dependencies
- Risk tier
- Regulatory scope
- Human oversight requirements
- Control mappings
- Evidence requirements
- Current lifecycle stage
- Last review date
- Next review date
- Current governance status

### 9.3 Evidence attributes

Evidence should include:

- Tenant
- Evidence type
- Source system
- Related entity
- Related control
- File or object reference
- Hash
- Version
- Owner
- Reviewer
- Created timestamp
- Expiry timestamp
- Retention policy
- Access policy
- Review status
- Extraction metadata
- Linked governance events

### 9.4 Policy attributes

Policies should include:

- Tenant
- Policy name
- Policy type
- Version
- Effective date
- Owner
- Approver
- Applicable systems
- Applicable roles
- Applicable jurisdictions
- Related obligations
- Control mappings
- Exception rules
- Review cadence
- Retirement status

## 10. Event model

The Governance Event Engine is the most important missing system.

Without it, the product becomes dashboards. With it, the product becomes a
governance runtime.

### 10.1 Event principles

Events should be:

- Append-only
- Tenant-scoped
- Actor-attributed
- Timestamped by the platform
- Schema-versioned
- Correlated to workflows and requests
- Linked to affected entities
- Safe to replay for reporting projections
- Exportable for audit

### 10.2 Event envelope

Every event should include at minimum:

- event_id
- event_type
- event_version
- tenant_id
- organization_id
- actor_type
- actor_id
- actor_display_name
- source_service
- source_request_id
- correlation_id
- causation_id
- occurred_at
- received_at
- entity_type
- entity_id
- policy_context
- risk_context
- payload
- integrity_hash

### 10.3 Canonical governance events

Initial event types should include:

| Event | Description |
| --- | --- |
| AI_SYSTEM_REGISTERED | A governed AI system was added to the inventory. |
| AI_SYSTEM_UPDATED | Metadata or ownership changed. |
| AI_SYSTEM_RETIRED | A system was retired from active use. |
| AI_AGENT_REGISTERED | A governed AI agent was registered. |
| MODEL_REGISTERED | A model dependency was registered. |
| MODEL_CHANGED | A system changed model, provider, or model version. |
| DATASET_LINKED | A dataset was linked to an AI system. |
| VENDOR_REGISTERED | A vendor was added. |
| VENDOR_REVIEW_REQUESTED | Vendor governance review began. |
| VENDOR_APPROVED | Vendor approval was granted. |
| VENDOR_REJECTED | Vendor approval was denied. |
| POLICY_CREATED | A new policy draft was created. |
| POLICY_UPDATED | A policy draft or active policy changed. |
| POLICY_APPROVED | A policy was approved. |
| POLICY_RETIRED | A policy was retired. |
| CONTROL_MAPPED | A control was mapped to an obligation or system. |
| CONTROL_FAILED | A control failed or became non-compliant. |
| CONTROL_REMEDIATED | A failed control was remediated. |
| EVIDENCE_UPLOADED | Evidence was added to the platform. |
| EVIDENCE_REVIEWED | Evidence was reviewed by a human. |
| EVIDENCE_APPROVED | Evidence was accepted for a control or audit package. |
| EVIDENCE_REJECTED | Evidence was rejected. |
| EVIDENCE_EXPIRED | Evidence passed its expiry threshold. |
| RISK_IDENTIFIED | A new risk was registered. |
| RISK_SCORE_CHANGED | Risk rating changed. |
| RISK_ACCEPTED | A risk was accepted by an accountable owner. |
| RISK_MITIGATED | A risk was mitigated. |
| APPROVAL_REQUESTED | A human approval was requested. |
| APPROVAL_GRANTED | Approval was granted. |
| APPROVAL_DENIED | Approval was denied. |
| HUMAN_OVERRIDE | A human overrode an automated or AI-assisted recommendation. |
| WORKFLOW_STARTED | A governance workflow started. |
| WORKFLOW_STEP_COMPLETED | A workflow step was completed. |
| WORKFLOW_ESCALATED | A workflow escalated due to rules or delay. |
| WORKFLOW_COMPLETED | A workflow completed. |
| INCIDENT_OPENED | A governance or AI incident was opened. |
| INCIDENT_UPDATED | Incident status or details changed. |
| INCIDENT_RESOLVED | Incident was resolved. |
| AI_PROMPT_SUBMITTED | A governed AI prompt was submitted. |
| AI_OUTPUT_GENERATED | A model output was generated. |
| AI_OUTPUT_EVALUATED | An output was evaluated by automated checks. |
| AI_OUTPUT_REVIEWED | A human reviewed an AI output. |
| AI_RECOMMENDATION_ACCEPTED | An AI recommendation was accepted. |
| AI_RECOMMENDATION_REJECTED | An AI recommendation was rejected. |
| BOARD_REPORT_GENERATED | A board report was generated. |
| AUDIT_PACKAGE_EXPORTED | An audit package was exported. |
| INTEGRATION_CONNECTED | A tenant integration was connected. |
| INTEGRATION_SYNC_COMPLETED | Integration sync completed. |
| INTEGRATION_SYNC_FAILED | Integration sync failed. |

### 10.4 Event projections

Events should feed read models for:

- AI inventory status
- Control health
- Evidence freshness
- Workflow queues
- Audit trails
- Board reporting
- Risk heatmaps
- Vendor status
- AI usage monitoring
- Integration health

## 11. Trust Ledger architecture

Trust Ledger is the durable governance memory layer of Noetfield.

It is not merely a table of records. It is the append-only history of governance
decisions, evidence, risk state, approvals, AI outputs, and workflow execution.

### 11.1 Responsibilities

Trust Ledger should provide:

- Append-only event history
- Tamper-evident event integrity
- Versioned entity history
- Point-in-time reconstruction
- Evidence lineage
- Approval lineage
- AI output lineage
- Control and obligation lineage
- Exportable audit packages
- Ledger-aware reporting

### 11.2 Storage model

Recommended initial storage:

- PostgreSQL as primary system of record
- Append-only event table partitioned by tenant and time
- Separate read models for query-heavy application views
- Object storage for evidence files and large artifacts
- Hashes for evidence and exported packages

Long-term enhancements may include:

- WORM-compatible storage
- External notarization for high-assurance exports
- Dedicated audit warehouse
- Customer-owned key support

### 11.3 Integrity model

Ledger records should support:

- Event hashes
- Previous-event hash chains per tenant or stream
- Evidence file hashes
- Export package manifests
- Actor attribution
- Service attribution
- Immutable timestamps
- Retention rules

## 12. Identity and access model

Enterprise readiness depends on the identity layer.

### 12.1 Required capabilities

The platform should support:

- SSO
- MFA
- RBAC
- ABAC
- Tenant isolation
- Scoped API keys
- Service accounts
- Session controls
- Device context where available
- User lifecycle synchronization
- Just-in-time provisioning
- Approval chains tied to roles and attributes

### 12.2 Initial identity integrations

Priority order:

1. Microsoft Entra ID
2. SAML 2.0
3. OIDC
4. SCIM provisioning

### 12.3 Role examples

Initial roles may include:

- Tenant administrator
- Governance administrator
- AI system owner
- Business owner
- Risk reviewer
- Evidence contributor
- Evidence reviewer
- Policy owner
- Auditor
- Board/report viewer
- Integration administrator
- API service account

### 12.4 ABAC attributes

Important attributes:

- Business unit
- Jurisdiction
- Data classification
- System risk tier
- Regulatory scope
- Employment status
- Clearance level
- Vendor access status
- Break-glass status

## 13. AI governance runtime

The AI runtime should augment governance workflows. It should not become an
ungoverned autonomous layer.

### 13.1 AI runtime capabilities

The runtime should support:

- Model routing
- Prompt template management
- Retrieval-augmented generation
- Context citation
- Prompt logging
- Output logging
- Automated output evaluation
- Human review queues
- Redaction and data-loss controls
- Usage analytics
- Model/provider policy enforcement
- Tenant-specific AI configuration

### 13.2 Governed AI use cases

Initial use cases:

- Vendor questionnaire analysis
- Evidence summarization
- Control mapping suggestions
- AI system risk classification
- Policy gap analysis
- Board report drafting
- Copilot readiness assessment
- Regulatory impact summaries
- Remediation recommendations

### 13.3 Safety boundaries

AI outputs should:

- Include citations where source material is used
- Show confidence or review status where appropriate
- Require human approval for consequential governance decisions
- Never silently change authoritative records
- Emit events for prompt submission, output generation, evaluation, and review
- Respect tenant policy for model providers and data handling

### 13.4 Model strategy

Recommended approach:

- Model router abstraction
- Azure OpenAI as the default enterprise path
- Optional support for OpenAI, Anthropic, or private models
- Tenant-level model policy configuration
- Evaluation harness for high-risk prompts and outputs

## 14. Workflow engine

Workflow governance should come before broad agent automation.

### 14.1 Initial workflows

The platform should support:

- AI system registration
- AI system review and approval
- Vendor assessment
- Evidence review
- Policy approval
- Control exception approval
- Risk acceptance
- Incident response
- Board report review
- Audit package approval

### 14.2 Workflow requirements

Workflows should support:

- State machines
- Human tasks
- Conditional routing
- Escalations
- Due dates
- Delegation
- Separation of duties
- Event emission
- Audit reconstruction
- Integration triggers

### 14.3 Workflow and AI

AI may operate inside workflows to:

- Draft summaries
- Recommend risk tiers
- Suggest controls
- Extract evidence facts
- Identify missing documents
- Recommend reviewers

AI should not bypass workflow ownership, approval chains, or audit controls.

## 15. Multi-tenant model

The platform should support hybrid commercial and enterprise deployment.

### 15.1 Tenant types

Supported deployment targets:

- Cloud multi-tenant SaaS
- Dedicated single-tenant cloud
- Enterprise-managed cloud deployment
- Isolated regulated deployment
- Sovereign deployment later

### 15.2 Tenant boundaries

Tenant isolation must apply to:

- Database rows and schemas
- Object storage
- Event streams
- Search indexes
- Cache keys
- Logs
- Metrics labels
- AI prompts and outputs
- Integration credentials
- Encryption keys where required

### 15.3 Tenant configuration

Each tenant should have configurable:

- Identity provider
- Allowed model providers
- Data retention rules
- Evidence retention rules
- Regulatory frameworks
- Risk scoring model
- Approval policies
- Integration settings
- Export controls
- Region and residency requirements

## 16. Security baseline

Security must be designed into the first operational version.

### 16.1 Required controls

Baseline requirements:

- Encryption in transit
- Encryption at rest
- KMS-backed key management
- Secrets management
- Tenant isolation tests
- SSO and MFA support
- RBAC and ABAC enforcement
- Immutable audit logging
- Centralized application logging
- Security event monitoring
- Rate limiting
- Backups
- Restore testing
- Retention policies
- Incident response process
- Secure software development lifecycle
- Dependency scanning
- Infrastructure-as-code review

### 16.2 Sensitive data handling

The platform should classify and protect:

- Personal data
- Business confidential data
- Regulated data
- AI prompts
- AI outputs
- Evidence documents
- Vendor assessment documents
- Board reports
- Integration credentials
- Security logs

### 16.3 Compliance baseline

Recommended framework sequence:

Phase 1:

- NIST AI RMF
- ISO 42001

Phase 2:

- EU AI Act
- SOC 2

Phase 3:

- OSFI
- FFIEC
- Banking-specific mappings

The platform data model should not hard-code a single framework. Frameworks,
obligations, controls, and mappings should be structured and extensible.

## 17. Integration layer

Integrations should feed the governance event engine and evidence lifecycle.

### 17.1 Priority integrations

Initial priority:

- Microsoft Graph
- Microsoft Entra ID
- Microsoft 365 audit and activity signals where available
- Microsoft Teams notifications
- SharePoint and OneDrive evidence sources

Secondary integrations:

- ServiceNow
- Jira
- Confluence
- Slack
- SIEM systems such as Microsoft Sentinel or Splunk
- GRC platforms
- Cloud providers
- Vendor management systems

### 17.2 Integration principles

Integrations should:

- Be tenant-scoped
- Use scoped credentials
- Emit sync events
- Produce evidence records where relevant
- Maintain sync health state
- Fail safely
- Support manual review for consequential changes
- Avoid silently changing authoritative governance records

## 18. Reporting and board layer

Board reporting should translate operational governance into executive-grade
oversight.

### 18.1 Report types

Initial report types:

- AI inventory report
- AI risk posture report
- Copilot governance readiness report
- Control health report
- Evidence freshness report
- Vendor AI risk report
- Incident and exception report
- Board AI oversight memo
- Audit evidence package

### 18.2 Reporting requirements

Reports should be:

- Point-in-time
- Reproducible
- Linked to source evidence
- Linked to ledger events
- Exportable
- Versioned
- Reviewable before release
- Access-controlled

## 19. Deployment modes

The business model should be hybrid.

### 19.1 SaaS

For:

- Mid-market customers
- AI governance teams
- Compliance operations
- Faster pilots

Characteristics:

- Multi-tenant
- Shared operational platform
- Tenant-specific configuration
- Standard integrations
- Standard security baseline

### 19.2 Enterprise deployment

For:

- Banks
- Government
- Healthcare
- Sensitive enterprises

Characteristics:

- Dedicated tenant
- Customer-specific region
- Customer-controlled identity
- Enhanced key management
- Custom integrations
- Stronger data residency and isolation controls

### 19.3 Sovereign deployment

Later option for:

- Public sector
- Highly regulated industries
- National data residency requirements

Characteristics:

- Sovereign cloud
- Strict residency
- Customer-specific operations model
- Additional compliance mappings

## 20. Phased roadmap

### Phase 1: Foundation and Trust Ledger

Primary goal:

Build the operational foundation.

Scope:

- Product identity cleanup
- Public site alignment around AI Trust Infrastructure
- Application shell
- Tenant model
- Identity model
- Initial RBAC
- AI system inventory
- Trust Ledger event envelope
- Append-only governance event store
- Basic evidence records
- NIST AI RMF and ISO 42001 baseline model
- Initial Copilot Governance data model

Exit criteria:

- Tenants can register AI systems.
- Users can authenticate and act under roles.
- Meaningful actions emit governance events.
- Trust Ledger can reconstruct basic history.
- Evidence can be linked to systems and controls.

### Phase 2: Governance workflows

Primary goal:

Turn records into governed processes.

Scope:

- Workflow engine
- Approval chains
- Evidence review
- Vendor review
- Policy approval
- Risk acceptance
- Exception handling
- Control mapping
- Workflow event projections

Exit criteria:

- Governance work has owners, states, approvals, and audit history.
- Human review is embedded in consequential decisions.
- Control and evidence lifecycle can be managed end to end.

### Phase 3: AI governance runtime

Primary goal:

Add AI assistance inside controlled workflows.

Scope:

- Model router
- Azure OpenAI integration path
- Prompt and output logging
- Evidence summarization
- Vendor questionnaire analysis
- Control mapping suggestions
- Risk classification assistance
- Human review of AI outputs
- Evaluation and safety checks

Exit criteria:

- AI can assist governance tasks.
- AI outputs are logged, reviewed, cited, and auditable.
- AI cannot silently mutate authoritative governance records.

### Phase 4: Realtime command center

Primary goal:

Make governance operational and live.

Scope:

- Realtime event streams
- Live control health
- Live evidence freshness
- Live workflow queues
- Live Copilot Governance status
- Incident monitoring
- Integration health monitoring
- Executive dashboards

Exit criteria:

- Governance teams can monitor risk, evidence, workflows, and incidents in
  real time.
- Operational views are backed by the event engine and ledger.

### Phase 5: Sector-specific modules

Primary goal:

Extend the platform into regulated verticals.

Scope:

- Banking mappings
- OSFI mappings
- FFIEC mappings
- Healthcare mappings
- Insurance mappings
- Government mappings
- Regulated-industry demos, including fintech/payment governance

Exit criteria:

- The core platform remains shared.
- Vertical modules add mappings, workflows, reports, and integrations without
  forking the governance model.

## 21. First implementation boundaries

The first implementation should avoid premature complexity.

Recommended first build boundary:

- One application frontend
- One backend API
- PostgreSQL as primary store
- Redis for queues/cache
- Object storage for evidence
- Append-only governance_events table
- Initial read models for inventory and workflows
- Entra ID/OIDC-ready identity abstraction
- Minimal but real RBAC
- NIST AI RMF and ISO 42001 seed framework data

Do not begin with:

- Many microservices
- Blockchain
- Autonomous agent swarms
- A chatbot-first interface
- Hard-coded banking-only assumptions
- Unstructured compliance copy as the source of truth

## 22. Open decisions

These decisions should be finalized before large implementation work:

1. First application framework and repo structure.
2. Whether public site and application live in one monorepo or split later.
3. Initial identity provider implementation.
4. Exact event store schema and integrity model.
5. Whether Temporal is introduced in Phase 1 or deferred until workflow
   complexity requires it.
6. Initial evidence storage provider.
7. Initial reporting/export format.
8. Initial Microsoft Graph integration scope.
9. Tenant isolation strategy for SaaS versus dedicated deployments.
10. Customer-owned key requirements for enterprise deployments.

## 23. Decision summary

This blueprint adopts the following strategic decisions:

- Primary market: regulated enterprises.
- Architecture standard: banking-grade from day one.
- Business model: hybrid SaaS and enterprise deployment.
- First wedge: Microsoft Copilot Governance.
- Core engine: Trust Ledger.
- First compliance baseline: NIST AI RMF and ISO 42001.
- Governance style: workflow-first, AI-agent-later.
- Architecture style: event-centric and audit-centric.
- Existing fintech/payment material: reframe as regulated-industry governance
  demo material.

The core platform thesis is:

> Noetfield becomes valuable by building governance memory and an enterprise
> trust graph, not by simply wrapping an LLM in a user interface.

