# API License Schedule (template) — MSB Partner

**Attachment to:** Master services / pilot agreement  
**MSB Partner:** ____________________  
**Tenant ID:** ____________________

## Licensed API

| Endpoint | Purpose |
|----------|---------|
| `POST /api/v1/governance/evaluate` | Pre-execution policy decision |
| `GET /api/v1/governance/ledger` | Compliance log read |
| `GET /api/v1/governance/audit-export` | Procurement / audit slice |
| `POST /api/v1/governance/partner-signals` | Read-only operational signals |
| Webhooks | `governance.decision.recorded` |

## Authentication

- Keys issued as `tenant_uuid:secret` in `GOVERNANCE_PILOT_API_KEYS`  
- Rotation: 90 days or on compromise  
- MSB Partner: max ___ concurrent environments (staging + production)

## Mode

| Environment | Default mode |
|-------------|--------------|
| Staging | `shadow` |
| Production | `shadow` until Enforce Addendum executed |

## Fees (annual)

**Option A — Flat:** __________ CAD / year  
**Option B — Metered:** __________ CAD per 1,000 evaluate calls (minimum __________)

## Support

Business hours email: operations@noetfield.com · severity-1 platform outage: as per MSA.

## SLA (pilot tier)

- Platform availability target: 99.5% monthly (excludes scheduled maintenance)  
- No financial transaction SLA (Noetfield does not execute payments)

## Term

12 months, auto-renew unless 60-day notice.
