# Trust Ledger Product Blueprint v1.2 (LOCKED)

**Status:** LOCKED · **Plane:** DESIGN · **Do not override without ASF + product signoff**

## Final positioning (locked)

**Noetfield is an AI Governance & Evidence layer for Copilot adoption, delivered today as structured procurement-grade assessments and evolving into a continuous Trust Ledger system.**

**Buyer line:** *We produce the audit trail your Copilot deployment will be asked for later.*

**Operational mandate:** Every engagement must produce at least one signed **Trust Ledger Entry (TLE v1)** — the canonical authorization record for Copilot adoption.

---

## 1. System design (modules) — v1.2

**Goal:** Minimal, decision-first product that produces canonical Trust Ledger Entries (TLEs) for procurement and governance signoff.

### Core modules

| Module | Purpose |
|--------|---------|
| **Trust Ledger Core** | Append-only store for TLEs; signed digests; exportable board packs |
| **Evidence Index** | Metadata catalog of ingested evidence (sources, hashes, retention) |
| **Evidence Intake Connector Layer** | Adapters: M365 Purview, Entra ID, M365 Audit Logs, SharePoint (+ optional) |
| **Decision Log UI (Trust Ledger Workspace v0)** | Read-only navigation, search, TLE viewer, PDF/Board Pack export |
| **TLE Generator** | Template engine: intake → TLE YAML/JSON + **Confidence Score** |
| **Procurement Asset Manager** | Evidence Intake Contract generator + ingestion rules UI |
| **Auth & Audit** | RBAC, signed approvals, immutable audit trail |

### Supporting modules (light)

- **Prompt Studio (templates only)** — structured JSON templates for TLE creation and evidence mapping
- **Minimal Reporting** — Board-ready PDF export and one-page risk summary

---

## 2. Execution flow (end-to-end)

1. **Engagement kickoff** — procurement pack signed; Evidence Intake Contract issued and accepted
2. **Connector onboarding** — metadata ingest per contract (metadata-only first)
3. **Evidence harvest** — Evidence Index: hashes, sensitivity tags, references
4. **TLE draft generation** — TLE Generator: template + evidence → TLE v1 + Confidence Score
5. **Approval chain** — CIO → Legal → Security signoff; signed approvals recorded
6. **Ledger write** — final TLE to Trust Ledger Core (signed digest, immutable)
7. **Delivery** — Workspace read-only; PDF/Board Pack; Procurement Authorization Pack
8. **Retention & audit** — retention rules enforced; audit logs exportable

---

## 3. Data objects (engineering-ready)

See:

- [schemas/tle-v1.schema.yaml](./schemas/tle-v1.schema.yaml)
- [examples/tle-v1-go.yaml](./examples/tle-v1-go.yaml)
- [examples/tle-v1-conditional.yaml](./examples/tle-v1-conditional.yaml)
- [examples/tle-v1-rejected.yaml](./examples/tle-v1-rejected.yaml)

### Evidence object (summary)

`evidence_id`, `source`, `title`, `hash`, `ingested_at`, `sensitivity`, `retention_policy`, `storage_ref`, `ingest_mode` (`metadata_only` | `full_capture`)

### Connector manifest (summary)

`connector_id`, `type`, `required_scopes`, `ingest_mode`, `last_sync`, `status`

### User / role (summary)

`user_id`, `name`, `email`, `roles` (CIO, Legal, Security, Auditor, Operator), `permissions`

---

## 4. Agents, roles & permissions

**Principles:** least privilege; read-only workspace; approvals signed and immutable.

| Role | Capabilities |
|------|----------------|
| **CIO (Owner)** | View TLEs; approve / conditional / reject; final signoff |
| **Legal** | Review evidence; approve / reject |
| **Security** | Validate controls; approve / reject; remediation conditions |
| **Operator (Noetfield)** | Onboarding, harvest, draft TLEs — **cannot sign** |
| **Auditor** | Read-only Evidence Index + TLEs; export audit bundles |
| **System Agent** | Confidence Score, connector sync, draft TLEs — **drafts only** |

**Permission matrix:** Draft → Operator, System Agent · Approve/Sign → CIO, Legal, Security · Read/export → granted roles

---

## 5. Risks / controls (operational)

| Risk | Control |
|------|---------|
| Evidence tampering / missing | Hash on ingest; references only; signed `audit_digest` per TLE |
| Unauthorized approvals | 2FA + key-backed signatures; role mapping in Intake Contract |
| Over-capture of sensitive data | metadata-only default; sensitivity exclusions; PII redaction |
| Misleading Confidence Score | Deterministic, auditable algorithm; provenance in UI |
| Perceived consulting vs product | Productize TLEs + workspace; public Intake Contract + TLE examples |

---

## 6. Implementation output (MVP)

### APIs (OpenAPI-ready)

Skeleton: [openapi/trust-ledger-v0.yaml](./openapi/trust-ledger-v0.yaml)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/connectors` | Register connector |
| POST | `/evidence/ingest` | Ingest evidence metadata |
| GET | `/evidence/{id}` | Fetch metadata (no raw PII) |
| POST | `/tle/draft` | Create TLE draft |
| POST | `/tle/{id}/approve` | Approver signs TLE |
| GET | `/tle/{id}` | Read TLE |
| GET | `/tle/{id}/export` | PDF / Board Pack |

### DB / storage (summary)

Tables: `users`, `roles`, `connectors`, `evidence_index`, `tle_entries`, `approvals`, `audit_logs`  
Storage: blob refs + hashes in DB; ledger digests via HSM/KMS

### UI screens (MVP)

Landing · Trust Ledger Workspace · Evidence Index · Connector Onboarding · Export

### Acceptance criteria (MVP)

- TLE draft from ingested evidence + template
- Two+ approvers sign; signed TLE immutable
- Purview + Entra ID metadata ingested and displayed
- PDF export with evidence index + signatures
- Hashes + `audit_digest` verifiable via KMS

---

## 7. 60-day sprint plan (executable)

**Week 0–2 (P0)** — TLE schema + 3 examples; homepage rewrite; Evidence Intake Contract v1 template

**Week 3–6 (P1)** — Ledger Core; Evidence Index + connectors; Workspace UI; TLE Generator + Confidence Score prototype

**Week 7–8 (P1)** — Approval chain + KMS stub; PDF export; 1–2 pilot engagements

---

## Alignment with repo law

- [PRODUCT_TRUTH.md](../../PRODUCT_TRUTH.md) — pre-execution governance, no payments
- [PROJECT_BOUNDARIES_LOCKED.md](../../PROJECT_BOUNDARIES_LOCKED.md)
- [os/plan.json](../../os/plan.json) — MVP done criteria
- Prior MVP map: [ALIGNMENT_WITH_MVP_v1.md](./ALIGNMENT_WITH_MVP_v1.md)
