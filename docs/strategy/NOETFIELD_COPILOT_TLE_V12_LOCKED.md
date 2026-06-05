# Noetfield Copilot — TLE v1.2 Positioning & Blueprint (LOCKED)

**Status:** LOCKED  
**Locked:** 2026-06-03  
**Authority:** ASF / product strategy  
**Path:** `docs/strategy/NOETFIELD_COPILOT_TLE_V12_LOCKED.md`  
**Supersedes:** Informal v1.2 chat positioning only — does not supersede [NOETFIELD_COPILOT_SME_SYSTEM_DESIGN_LOCKED_v1.md](./NOETFIELD_COPILOT_SME_SYSTEM_DESIGN_LOCKED_v1.md)  
**Related:** [PRODUCT_TRUTH.md](../../PRODUCT_TRUTH.md) · [copilot-sme-system-design-v1](../spec/copilot-control-catalog.md) · [tenant-append-only-audit-schema-outline.md](../spec/tenant-append-only-audit-schema-outline.md)

---

## Agent analysis (read first)

### Product truth (one line)

> **Noetfield is an AI Governance & Evidence layer for Copilot adoption** — procurement-grade assessments today, continuous Trust Ledger via **Trust Ledger Entry v1 (TLE v1)**.

**Buyer line:** *We produce the audit trail your Copilot deployment will be asked for later.*

### Mandate

Every Noetfield Copilot engagement produces **at least one signed TLE v1** — Go, Conditional, or Rejected.

### Lane boundary (unchanged)

| Lane | Scope | Noetfield repo? |
|------|-------|-----------------|
| **A** | Pre-execution governance, evidence index, TLE, approval chain, audit export | **Yes** |
| **B** | Partner payment / disbursement execution | **No** — external systems |
| **C** | Full finance ledger, member portal, payment reconciliation at scale | **Design only** |

M365 connector ingest is **metadata-only** by default (`ingest_mode: metadata_only`). No raw document content or PII blobs in Noetfield DB.

### Canonical artifact: TLE v1

The **Trust Ledger Entry (TLE v1)** is the procurement-grade authorization record. It binds:

- Decision headline + status (`Approved` | `Conditional` | `Rejected` | `Draft`)
- Deterministic **Confidence Score** (0.00–1.00) with auditable factor weights
- Evidence references (hash + timestamp + source — not raw content)
- Risk summary + control pass/fail narrative
- Approval chain (CIO / Legal / Security minimum)
- Signatures + `audit_digest` (sha256 chain)

**Schema:** `packages/schemas/tle-v1.schema.json`  
**Samples:** `docs/spec/samples/tle-go-approved.yaml`, `tle-conditional.yaml`, `tle-rejected.yaml`

### v1.2 module map (60-day sprint)

| Week | Module | Deliverable |
|------|--------|-------------|
| 0–2 | **Lock & schemas** | This doc, TLE/Evidence/Connector schemas, 3 YAML examples, Evidence Intake Contract, OpenAPI skeleton |
| 3–4 | **Evidence Index** | `evidence_index` table, `POST /evidence/ingest`, connector registry `POST /connectors` |
| 5–6 | **TLE Generator** | `POST /tle/draft` template engine, deterministic Confidence Score |
| 5–6 | **Trust Ledger Workspace** | `/workspace` UI — evidence list, draft TLE, approval status |
| 7–8 | **Approval + export** | Approval chain UI, KMS stub signing, PDF Board Pack export |
| 7–8 | **Pilot E2E** | Design-partner runbook update, `verify-tle-integrity.sh` |

### API surface (skeleton)

See `docs/spec/openapi/tle-v1.openapi.yaml`:

- `POST /evidence/ingest` — metadata-only evidence intake
- `POST /connectors` — register M365 connector manifest
- `POST /tle/draft` — generate draft TLE from evidence + control results
- `GET /tle/{tle_id}` — retrieve signed TLE
- `POST /tle/{tle_id}/approve` — approval step + signature
- `GET /tle/{tle_id}/export` — PDF Board Pack

### Confidence Score (deterministic v1)

```
confidence_score = Σ (factor_weight × factor_value)
```

Default factors (weights must sum to 1.0):

| Factor | Weight | Source |
|--------|--------|--------|
| `required_evidence_coverage` | 0.40 | Evidence index vs required connector set |
| `control_pass_rate` | 0.35 | Copilot control catalog test results |
| `sensitivity_boundary_compliance` | 0.25 | Purview / label boundary checks |

Score is **reproducible** from stored inputs — no LLM randomness in v1.

### Evidence object

Standalone evidence records use `packages/schemas/evidence.schema.json`.  
Intake contract: `docs/spec/evidence-intake-contract-v1.md`.

### Connector manifest

M365 connectors register via `packages/schemas/connector-manifest.schema.json`.  
Read-only scopes only; `ingest_mode` defaults to `metadata_only`.

### Future agent instruction

When ASF says **implement** from this lock:

1. Pick **one** task from `os/plan.json` v1.2 sprint (`nf-tle-v12-lock-011` … `nf-copilot-pilot-tle-017`)
2. Do not implement Lane B/C payment execution
3. Every pilot must produce a valid TLE v1 YAML against schema before marking E2E done

---

## Positioning copy (locked)

**Homepage hero (Trust Ledger):**

> Governance & evidence for Microsoft Copilot — before you deploy, not after the audit.

**Procurement one-pager headline:**

> Trust Ledger Entry (TLE) — the signed authorization record your Copilot rollout needs.

**Three outcomes we document:**

1. **Go** — deployment authorized with controls attested
2. **Conditional** — limited pilot with remediation conditions
3. **Rejected** — material control failures documented for re-planning

---

## Schema registry

| Artifact | Path |
|----------|------|
| TLE v1 | `packages/schemas/tle-v1.schema.json` |
| Evidence | `packages/schemas/evidence.schema.json` |
| Connector manifest | `packages/schemas/connector-manifest.schema.json` |
| OpenAPI | `docs/spec/openapi/tle-v1.openapi.yaml` |
| Evidence intake contract | `docs/spec/evidence-intake-contract-v1.md` |
| Validation | `scripts/validate-tle-schemas.sh` |

---

## Acceptance criteria (Week 0–2 lock)

- [x] TLE v1 JSON Schema published
- [x] Evidence + Connector JSON Schemas published
- [x] Three YAML samples (Go / Conditional / Rejected)
- [x] Evidence Intake Contract v1
- [x] OpenAPI skeleton
- [x] `validate-tle-schemas.sh` in Makefile
- [x] Locked reference registered in `os/plan.json`
