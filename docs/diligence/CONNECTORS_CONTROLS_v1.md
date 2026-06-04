# Connectors Controls v1

**Between:** Customer (“Client”) and Noetfield Systems (“Provider”)  
**Purpose:** Define operational and security controls for Trust Ledger **connector registration** and **heartbeat/sync** (metadata-only, no live M365 OAuth in pilot).

---

## 1. Scope

| Control area | Pilot behavior |
|--------------|----------------|
| Connector types | Purview, Entra ID, M365 Audit (metadata_only default) |
| Registration | `POST /api/v1/connectors` — manifest with `connector_id`, scopes, ingest_mode |
| Operational status | `POST /api/v1/connectors/{id}/sync` — updates `last_sync` and `status` (stub; no OAuth secrets in repo) |
| Evidence linkage | Connector sync does not ingest raw content; evidence via `POST /api/v1/evidence/ingest` |

**Out of scope:** payment rails, custody, production Purview app secrets (ASF deployment lane).

---

## 2. Client responsibilities

- Maintain least-privilege app registration per Connector Manifest
- Run connector sync jobs on agreed schedule (or Provider-managed stub in pilot)
- Notify Provider on scope changes or tenant boundary moves
- Do not enable `full_capture` without signed Evidence Intake addendum

---

## 3. Provider deliverables

- Registered connector record with `registered_at`, `status`, `last_sync` visible via API and Governance Console
- Diligence cross-reference: [EVIDENCE_INTAKE_CONTRACT_v1.md](EVIDENCE_INTAKE_CONTRACT_v1.md)
- OpenAPI: `docs/spec/openapi/trust-ledger-v0.yaml` · platform `/docs` (filtered public schema includes trust-ledger paths)

---

## 4. Status model

| Status | Meaning |
|--------|---------|
| `registered` | Manifest accepted; no sync yet |
| `active` | Last heartbeat/sync recorded |
| `error` | Sync reported failure (operator follow-up) |

Sync payload (stub): `{ "status": "active" \| "error", "records_synced": number }`.

---

## 5. Security

- No connector credentials stored in application repository
- Sync endpoint rate-limited with other governance pilot routes
- Connector IDs are tenant-scoped in production (tenant isolation tests: follow-up NF-PLAN-0114)

---

## 6. Verification (agent-only)

```bash
python3 -m pytest tests/unit/test_trust_ledger_v1.py -q
./scripts/tle-smoke.sh --api --connectors-sync   # requires make dev-local
```

Governance Console read-only workspace: `http://localhost:13080/trust-ledger` (unified dev proxy).
