# Production pilot API keys

Server-side only — never commit secrets. See [.env.example](../.env.example).

## Enable pilot auth

On **platform.noetfield.com** (not www):

```bash
GOVERNANCE_PILOT_AUTH_REQUIRED=true
GOVERNANCE_PILOT_API_KEYS=<tenant_uuid>:<secret>[,<tenant_uuid2>:<secret2>]
```

Format: comma-separated `tenant_id:secret` pairs. The `tenant_id` must match JSON body `tenant_id` on evaluate.

## Issue a prospect key (example)

1. Generate secret: `openssl rand -hex 24`
2. Pick stable tenant UUID for the prospect sandbox (or use org id from engagement letter).
3. Add to `GOVERNANCE_PILOT_API_KEYS` and redeploy/restart platform.
4. Send prospect: `Authorization: Bearer <tenant_uuid>:<secret>` (same string as env entry).

## Verify

```bash
export PLATFORM=https://platform.noetfield.com
export PILOT_API_KEY='00000000-0000-4000-8000-000000000099:your-secret'

curl -sS -X POST "$PLATFORM/api/v1/governance/evaluate" \
  -H "Authorization: Bearer $PILOT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "00000000-0000-4000-8000-000000000099",
    "organization_id": "00000000-0000-4000-8000-000000000002",
    "action": "initiate_transfer_intent",
    "resource_type": "partner_msb",
    "resource_id": "pilot-smoke",
    "mode": "shadow",
    "request_id": "RID-PILOT-SMOKE-001"
  }'
```

## Optional

- `GOVERNANCE_WEBHOOK_URLS` — comma-separated URLs for `governance.decision.recorded`
- `INTAKE_OPS_WEBHOOK_URL` — Slack (or compatible) for new intakes → [INTAKE_OPS.md](./INTAKE_OPS.md)
