# MSB partner deploy and pilot keys

**Audience:** Founder / platform ops after merge to `main`.  
**Boundary:** Noetfield sells governance software to licensed MSBs — not MSB registration.

## 1. Merge and release

1. Merge [PR #11](https://github.com/kazemnezhadsina144-dot/Noetfield/pull/11) (institutional API + partner GTM) into `main`.
2. Tag or deploy from `main` per [GO_LIVE.md](./GO_LIVE.md).

## 2. Deploy surfaces

| Surface | Deploy |
|---------|--------|
| **www** | Static root — include `/partners/`, `/trust-ledger/`, `vector=partner-msb` intake |
| **platform** | API on `platform.noetfield.com:8001` (or container) |

```bash
make platform-migrate   # if postgres
# production container: see infrastructure/docker/
```

## 3. MSB pilot API keys (production)

In platform host `.env` (never commit secrets):

```bash
GOVERNANCE_PILOT_AUTH_REQUIRED=true
# tenant_uuid:secret per MSB sandbox — example:
GOVERNANCE_PILOT_API_KEYS=00000000-0000-4000-8000-000000000099:replace-with-msb-sandbox-secret
GOVERNANCE_WEBHOOK_URLS=https://msb-partner.example/webhooks/noetfield
GOVERNANCE_WEBHOOK_SECRET=replace-with-hmac-secret
```

MSB engineers call:

- `Authorization: Bearer <secret>` or `X-API-Key: <secret>`
- `POST /api/v1/governance/evaluate` with `mode: shadow` until MSB addendum signed

## 4. Smoke verification

```bash
PLATFORM_HEALTH_BASE=https://platform.noetfield.com ./scripts/deploy_platform_smoke.sh
```

Local pre-check:

```bash
make verify-final-lock
```

## 5. Private commercial pack

Run once on founder machine:

```bash
./scripts/bootstrap-private-ops.sh
./scripts/seed-msb-partner-pack.sh
```

Templates land in `ops/private/msb/` (gitignored).

## Related

- [msb-partner-playbook.md](./strategy/msb-partner-playbook.md)
- [MSB_STAGING_INTEGRATION.md](./MSB_STAGING_INTEGRATION.md)
- [SHADOW_WEEK_DEMO.md](./SHADOW_WEEK_DEMO.md)
