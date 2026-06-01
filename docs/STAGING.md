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

## CI note

Production deploy workflow is manual/`workflow_dispatch` until cloud credentials are wired ([.github/workflows/platform-deploy.yml](../.github/workflows/platform-deploy.yml)).
