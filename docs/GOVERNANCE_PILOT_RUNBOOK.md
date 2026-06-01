# Governance pilot runbook (production)

**Production host:** `https://platform.noetfield.com` (port **8001** on origin)  
**API surface:** `/api/v1/governance/*` only — not `governance-console/` (dev sandbox).

**Auth:** Pilot API key when `GOVERNANCE_PILOT_AUTH_REQUIRED=true` ([PRODUCTION_PILOT_KEYS.md](./PRODUCTION_PILOT_KEYS.md)).

---

## RID rules

- Format: `RID-` + uppercase alphanumeric (see `governance_rid.normalize_rid`).
- Generate: omit `request_id` on evaluate (server assigns) or pass existing RID from intake.
- **One RID per engagement thread** — reuse across intake, evaluate, audit-export, ops email.

---

## Evaluate (shadow pilot)

```bash
export PLATFORM=https://platform.noetfield.com
export PILOT_KEY="your-pilot-key"

curl -sS -X POST "$PLATFORM/api/v1/governance/evaluate" \
  -H "Authorization: Bearer $PILOT_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "00000000-0000-4000-8000-000000000001",
    "organization_id": "00000000-0000-4000-8000-000000000002",
    "action": "submit_payment_intent",
    "resource_type": "shadow_probe",
    "resource_id": "week-1",
    "mode": "shadow",
    "actor_type": "system"
  }' | python3 -m json.tool
```

Expect `decision` / `allowed` / `request_id` (RID). Payment-like actions should **REJECT** under Noetfield boundary (non-PSP).

---

## Ledger

```bash
curl -sS "$PLATFORM/api/v1/governance/ledger?request_id=RID-..." \
  -H "Authorization: Bearer $PILOT_KEY" | python3 -m json.tool
```

---

## Audit export (Trust Brief deliverable)

```bash
./scripts/trust_brief_audit_export.sh --request-id RID-... --out ./exports/
```

Or:

```bash
curl -sS "$PLATFORM/api/v1/governance/audit-export?request_id=RID-..." \
  -H "Authorization: Bearer $PILOT_KEY" | python3 -m json.tool
```

---

## Console (UI)

| Surface | URL |
|---------|-----|
| www redirect | https://www.noetfield.com/console/ → platform `/console` |
| Platform UI | https://platform.noetfield.com/console |

---

## Health

```bash
PLATFORM_HEALTH_BASE=https://platform.noetfield.com ./scripts/deploy_platform_smoke.sh
curl -sS https://platform.noetfield.com/api/status | python3 -m json.tool
```

---

## Not production

| Path | Role |
|------|------|
| `governance-console/` (repo) | Local/Docker MVP — E2E only |
| `/v3/evaluate` | Internal demo — not in public OpenAPI |

See [RUNBOOK.md](./RUNBOOK.md) · [docs/api/](./api/) · [SHADOW_WEEK_DEMO.md](./SHADOW_WEEK_DEMO.md).
