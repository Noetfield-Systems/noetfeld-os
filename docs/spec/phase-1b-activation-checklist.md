# Phase 1B activation checklist (ASF gate)

**Task:** `nf-phase1b-scaffold-004`  
**Status:** DESIGN — gate before production migrations  
**Last updated:** 2026-06-03  

---

## Preconditions

- [ ] [tenant-append-only-audit-schema-outline.md](./tenant-append-only-audit-schema-outline.md) reviewed
- [ ] [trustfield-noetfield-conflict-matrix.md](./trustfield-noetfield-conflict-matrix.md) acknowledged
- [ ] `make verify-local-dev` green on branch
- [ ] PR #15 or successor reviewed for local dev + proxy routing

---

## API routing (standalone, not :8000)

| Surface | Port | Notes |
|---------|------|--------|
| Unified dev entry | **13080** | `dev-unified-proxy.py` — canonical |
| Governance console API | **18002** | Internal; proxied at `/evaluate`, `/audit` |
| Platform governance v1 | **8001** | `/api/v1/governance/*` — separate from mono :8000 |
| Legacy mono API | **8000** | **Do not** bind Noetfield pilot here |

---

## Implementation steps (1B)

1. [ ] Deploy `tenants` + `audit_events` tables (SQLite dev + Postgres staging)
2. [ ] Migrate existing `audit_logs` rows → `audit_events` with default pilot tenant
3. [ ] Require `X-Tenant-ID` header (or dev default) on `POST /evaluate`
4. [ ] Add `integrity_hash` on insert (SHA-256 canonical JSON)
5. [ ] `GET /audit/export` — tenant-scoped bundle JSON
6. [ ] Extend `verify-local-dev.sh` — tenant_id present in export
7. [ ] RLS policies on Postgres (staging only)
8. [ ] Update [GOVERNANCE_PILOT_RUNBOOK.md](../GOVERNANCE_PILOT_RUNBOOK.md) with tenant header docs

---

## Rollback

- Feature flag `NF_USE_AUDIT_EVENTS=0` falls back to `audit_logs` table (dev only) until cutover complete

---

## Out of scope for 1B

- Payment tables, member ledger, loan lifecycle
- Full compliance engine (Phase 2 schemas only until ASF activates)
- Production multi-tenant billing

---

**END**
