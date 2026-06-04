# Tenant + append-only audit schema outline (Phase 1B design)

**Status:** DESIGN — markdown only until ASF activates implementation  
**Task:** `nf-tenant-audit-schema-002`  
**Plane:** Noetfield governance data model  
**Last updated:** 2026-06-03  

---

## Purpose

Define the **minimum** multi-tenant data model and **append-only** audit ledger for Noetfield pilots (bank shadow, Copilot governance, Trust Brief evidence). Aligns with MVP requirements in [os/plan.json](../../os/plan.json) and existing event contract [packages/schemas/governance_event.schema.json](../../packages/schemas/governance_event.schema.json).

**Out of scope:** payment rails, custody, settlement, FX, TrustField/VIRLUX tables.

---

## Design principles

| Principle | Rule |
|-----------|------|
| **Tenant isolation** | Every row carries `tenant_id`; API keys and RLS scoped to tenant |
| **Append-only audit** | `audit_events` — INSERT only; no UPDATE/DELETE on production paths |
| **RID as external key** | `rid` (e.g. `RID-{uuid}`) is client-facing; internal `event_id` is UUID |
| **Evaluation snapshot** | Each evaluate writes one immutable snapshot + optional domain events |
| **Export-ready** | `audit_export_slices` materialized view or query contract for diligence packs |

---

## Entity outline

### 1. `tenants`

| Column | Type | Notes |
|--------|------|--------|
| `tenant_id` | UUID PK | Issued at onboarding |
| `slug` | string unique | e.g. `pilot-bank-01` |
| `display_name` | string | Institution label |
| `status` | enum | `active`, `suspended`, `pilot` |
| `created_at` | timestamptz | |
| `metadata` | jsonb | Plan tier, region, contact ref (no PII vault) |

### 2. `organizations` (optional sub-scope within tenant)

| Column | Type | Notes |
|--------|------|--------|
| `organization_id` | UUID PK | Maps to `organization_id` in governance events |
| `tenant_id` | UUID FK → tenants | |
| `name` | string | Business unit / subsidiary |
| `created_at` | timestamptz | |

### 3. `audit_events` (append-only ledger)

| Column | Type | Notes |
|--------|------|--------|
| `event_id` | UUID PK | Internal immutable id |
| `tenant_id` | UUID FK | Required |
| `organization_id` | UUID FK nullable | |
| `rid` | string unique per tenant | External compliance reference |
| `event_type` | string | `governance.evaluate`, `governance.review`, `policy.pack_applied` |
| `actor` | string | Service/human identifier (v1 flat; v2 structured actor object) |
| `action` | string | Operational intent action |
| `context` | text | Justification / scope |
| `metadata` | jsonb | Opaque client context |
| `decision` | enum | `allow`, `deny`, `review` |
| `risk_score` | int 0–100 | |
| `reason` | jsonb array | Policy reason strings |
| `conditions` | jsonb array | Execution conditions |
| `integrity_hash` | string nullable | SHA-256 chain optional Phase 1B+ |
| `recorded_at` | timestamptz | Server receipt time (immutable) |

**Constraints:** `REVOKE UPDATE, DELETE` on role `app_runtime`; inserts via stored procedure or service layer only.

### 4. `policy_packs` (tenant-bound, versioned read)

| Column | Type | Notes |
|--------|------|--------|
| `pack_id` | UUID PK | |
| `tenant_id` | UUID FK | |
| `version` | string | Semver |
| `rules` | jsonb | Policy definition (design-time) |
| `effective_from` | timestamptz | |
| `retired_at` | timestamptz nullable | |

### 5. `api_keys` (pilot auth)

| Column | Type | Notes |
|--------|------|--------|
| `key_id` | UUID PK | |
| `tenant_id` | UUID FK | |
| `key_hash` | string | Never store plaintext |
| `scopes` | text[] | `evaluate`, `audit:read`, `export` |
| `created_at` | timestamptz | |
| `revoked_at` | timestamptz nullable | |

---

## RID format (locked for pilots)

```
RID-{short_uuid}-{checksum}
```

Example: `RID-39631619-92361CE4` (matches governance-console dev API today).

---

## API mapping (conceptual — no new routes in this doc)

| HTTP | Writes to | Read model |
|------|-----------|------------|
| `POST /evaluate` | `audit_events` row + response DTO | — |
| `GET /audit` | — | List by tenant, filter `q` on rid/actor/action |
| `GET /audit/{rid}` | — | Single snapshot |
| `GET /api/v1/governance/audit-export` | — | Redacted export slice (platform console) |

---

## Alignment with existing artifacts

| Artifact | Relationship |
|----------|----------------|
| [governance-console/backend/db/models.py](../../governance-console/backend/db/models.py) | v1 single-table `audit_logs` — migrate to `audit_events` + `tenant_id` in Phase 1B |
| [governance_event.schema.json](../../packages/schemas/governance_event.schema.json) | Event envelope superset; audit row is evaluate outcome projection |
| [PRODUCT_TRUTH.md](../../PRODUCT_TRUTH.md) | Pre-execution only; no execution rights column |
| [PROJECT_BOUNDARIES_LOCKED.md](../../PROJECT_BOUNDARIES_LOCKED.md) | No TrustField/VIRLUX foreign keys |

---

## Phase 1B activation checklist (implementation — ASF gate)

- [ ] Alembic migration: `tenants`, `organizations`, `audit_events`
- [ ] RLS policies on Postgres (`tenant_id = current_setting('app.tenant_id')`)
- [ ] Backfill script from SQLite dev `audit_logs`
- [ ] Update evaluate handler to require `tenant_id` header or API key
- [ ] `make verify-local-dev` extended with tenant-scoped smoke
- [ ] Diligence sample export uses new `rid` + `recorded_at` fields

---

## Verification (design task)

```bash
test -f docs/spec/tenant-append-only-audit-schema-outline.md
grep -q "append-only" docs/spec/tenant-append-only-audit-schema-outline.md
grep -q "tenant_id" docs/spec/tenant-append-only-audit-schema-outline.md
```

Expected: all commands exit 0.
