# Vercel www — intake email go-live

**Inbox:** operations@noetfield.com  
**Project:** `web` · scope `noetfield-systems`

## Required (Production)

```bash
RESEND_API_KEY=re_xxxxxxxx
INTAKE_EMAIL_FROM=Noetfield Intake <notifications@noetfield.com>
INTAKE_EMAIL_TO=operations@noetfield.com
INTAKE_AUTO_ACK_ENABLED=true
```

## Resend domain

1. [resend.com](https://resend.com) → Domains → add `noetfield.com`
2. Add DNS records Resend provides (SPF/DKIM)
3. Create API key with send permission

## Set on Vercel

```bash
cd /path/to/Noetfield
npx vercel env add RESEND_API_KEY production --scope noetfield-systems
# repeat for INTAKE_EMAIL_FROM, INTAKE_EMAIL_TO, INTAKE_AUTO_ACK_ENABLED
npx vercel --prod --yes --scope noetfield-systems --project web
```

## Verify

```bash
./scripts/check-intake-health.sh
# or: curl -sS https://www.noetfield.com/api/intake/health | jq .
# expect: "www_email_configured": true, "enabled": true, "delivery_mode": "resend"
```

Submit [noetfield.com/contact/](https://www.noetfield.com/contact/) with a real email — ops inbox + auto-ack should arrive.

**Public ops checklist:** [noetfield.com/next/#next-ops](https://www.noetfield.com/next/#next-ops)

## Platform (optional persistence)

If platform intake is disabled in production, www still works when `RESEND_API_KEY` is set — forms email ops directly without platform storage.

Enable platform: set `PUBLIC_INTAKE_ENABLED=true` on platform.noetfield.com Render/env.

## Vectors routed to ops

| Vector | Label |
|--------|--------|
| `contact` | Contact |
| `copilot-governance` | Governance Pack apply |
| `investor-diligence` | Investor diligence vault |
| `work-with-us` | Work with Noetfield / Investor brief |
| `sandbox-signup` | Sandbox signup |

See [INTAKE_OPS.md](../INTAKE_OPS.md).
