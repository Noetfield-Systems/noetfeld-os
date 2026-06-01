# Staging environment (NF-ENG-15)

## Purpose

Preview www changes against a non-production platform API before updating production.

## Suggested hosts

| Surface | Example host |
|---------|----------------|
| www (staging) | `staging-www.noetfield.com` or Pages preview URL |
| platform (staging) | `staging-platform.noetfield.com` |

## Configuration

On **staging platform**, set in `.env`:

```bash
PUBLIC_CHAT_CORS_ORIGINS=https://staging-www.noetfield.com,https://www.noetfield.com,http://localhost:8080
PUBLIC_CHAT_API_BASE=https://staging-platform.noetfield.com
```

On **staging www**, set in HTML or ecosystem publish:

```html
<meta name="nf-chat-api-base" content="https://staging-platform.noetfield.com" />
```

```bash
PUBLIC_CHAT_API_BASE=https://staging-platform.noetfield.com \
TELEGRAM_BOT_USERNAME=YourStagingBot \
python3 scripts/publish_ecosystem_config.py
```

## Verify staging

```bash
PLATFORM_HEALTH_BASE=https://staging-platform.noetfield.com ./scripts/deploy_platform_smoke.sh
```

## Governance pilot on staging

Use the same `/api/v1/governance/*` surface as production ([GOVERNANCE_PILOT_RUNBOOK.md](./GOVERNANCE_PILOT_RUNBOOK.md)).

```bash
export PLATFORM=https://staging-platform.noetfield.com
export PILOT_KEY="staging-pilot-key"
# evaluate + audit-export per runbook
./scripts/trust_brief_audit_export.sh --request-id RID-... --platform "$PLATFORM"
```

After first paid deal, run `ops/private/msb/STAGING_PROOF_RUNBOOK.md` (from `./scripts/market-entry-bootstrap.sh`).

## Postgres backup drill (staging)

Quarterly restore exercise before bank diligence:

1. `pg_dump` from production (see [POSTGRES_OPERATIONS.md](./POSTGRES_OPERATIONS.md)).
2. Restore to staging database; run `make platform-migrate` if needed.
3. Confirm `GET /api/v1/governance/ledger` returns entries on staging.
4. Record date + operator in private ops log.

## Status alignment

- www: [status/index.html](../status/index.html) polls `GET /api/status` on platform host.
- Staging status page should use `staging-platform.noetfield.com` when that host exists.

## Edge / WAF (deferred)

CDN WAF and edge rate limits: [PRODUCT_DEFERRED.md](./PRODUCT_DEFERRED.md) NF-ENG-16 — enable when traffic or abuse signals warrant.

## CI note

Production deploy workflow is manual/`workflow_dispatch` until cloud credentials are wired ([.github/workflows/platform-deploy.yml](../.github/workflows/platform-deploy.yml)).
