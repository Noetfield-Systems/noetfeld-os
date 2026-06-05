# Evidence Intake Contract v1

**Status:** Draft contract — Week 0–2 lock  
**Schema:** `packages/schemas/evidence.schema.json`  
**API:** `POST /evidence/ingest` (see `docs/spec/openapi/tle-v1.openapi.yaml`)

---

## Purpose

Define how external systems (M365 connectors, manual upload, SaaS feeds) deliver **metadata-only** evidence into Noetfield's Evidence Index for TLE generation.

Noetfield stores **hashes, timestamps, titles, and references** — not raw document bodies or PII payloads.

---

## Intake modes

| Mode | Description | Default |
|------|-------------|---------|
| `metadata_only` | Hash, title, source link, sensitivity label, timestamp | **Yes** |
| `full_capture` | Encrypted blob reference in tenant-controlled storage (`storage_ref`) | Opt-in only |

Lane A pilots use **`metadata_only` only**.

---

## Required fields

| Field | Type | Notes |
|-------|------|-------|
| `evidence_id` | string | Pattern `^EV-[A-Z0-9-]+$` — caller or server-generated |
| `source` | enum | `Purview`, `EntraID`, `AuditLog`, `SharePoint`, `Endpoint`, `SaaS`, `Manual` |
| `title` | string | Human-readable label for audit export |
| `hash` | string | `sha256:<64 hex chars>` — content or export file digest |
| `ingested_at` | ISO 8601 | Server-set on ingest |
| `ingest_mode` | enum | `metadata_only` or `full_capture` |

## Optional fields

| Field | Type | Notes |
|-------|------|-------|
| `tenant_id` | uuid | Multi-tenant isolation |
| `connector_id` | string | Links to registered connector manifest |
| `sensitivity` | enum | `Public`, `Internal`, `Confidential`, `HighlyConfidential` |
| `retention_policy` | string | e.g. `90d`, `1y` — informational in v1 |
| `storage_ref` | string | External blob URI — never inline content |
| `link` | uri | Deep link to source system (Purview, Entra, etc.) |
| `metadata` | object | Connector-specific key/value (no raw PII) |

---

## Request example

```json
{
  "evidence_id": "EV-PURVIEW-001",
  "source": "Purview",
  "title": "DLP policy export — Copilot data boundaries",
  "hash": "sha256:a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
  "ingest_mode": "metadata_only",
  "connector_id": "CONN-PURVIEW-001",
  "sensitivity": "Internal",
  "link": "https://compliance.microsoft.com/purview/dlp/policies/copilot-boundary",
  "metadata": {
    "export_type": "dlp_policy_snapshot",
    "policy_count": 6
  }
}
```

---

## Response

```json
{
  "evidence_id": "EV-PURVIEW-001",
  "ingested_at": "2026-06-03T12:00:00Z",
  "status": "indexed"
}
```

HTTP `201 Created` on success. `409 Conflict` if `evidence_id` already exists for tenant.

---

## Validation rules

1. `hash` must match `^sha256:[a-f0-9]{64}$`
2. `ingest_mode: full_capture` requires `storage_ref`
3. `connector_id` must reference an `active` connector for the tenant (Week 3+ enforcement)
4. Reject payloads containing inline `content`, `body`, or base64 document fields

---

## Connector registration (prerequisite)

Before bulk ingest, register connector via `POST /connectors` using `packages/schemas/connector-manifest.schema.json`.

Required scopes are **read-only** Graph/API permissions. See `docs/spec/connectors-m365-v1.md`.

---

## TLE binding

Evidence records are referenced inside TLE v1 as embedded refs:

```yaml
evidence:
  - evidence_id: EV-PURVIEW-001
    source: Purview
    title: "DLP policy export — Copilot data boundaries"
    metadata:
      timestamp: "2026-06-02T14:30:00Z"
      hash: "sha256:a1b2c3..."
```

The TLE `audit_digest` covers TLE body + evidence ref hashes.

---

## Out of scope (v1)

- Real-time streaming ingest (batch/sync only)
- Content indexing or RAG over evidence blobs
- Cross-tenant evidence sharing
- Payment or financial transaction evidence (Lane C)
