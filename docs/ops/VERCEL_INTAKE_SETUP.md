# Vercel www — intake email go-live

**Inbox:** operations@noetfield.com  
**Google Workspace:** **ACTIVE** (2026-06-18) — mailbox live; direct email works  
**Status:** **DEFERRED post-factory** — enable Resend only after factory spine + portfolio waves complete  

> Founder law: factory first · email sending second · do not boot sessions into Resend setup.
**Canonical project:** `www` · scope `noetfield-systems`  
**One project only** — run `./scripts/auto-heal-www.sh` to dedupe, sync env, deploy, verify.

## Required (Production)

```bash
RESEND_API_KEY=re_xxxxxxxx
INTAKE_EMAIL_FROM=Noetfield Intake <notifications@noetfield.com>
INTAKE_EMAIL_TO=operations@noetfield.com
INTAKE_AUTO_ACK_ENABLED=true
```

Source of truth for keys: `~/.sina/secrets.env` (auto-heal reads and pushes to Vercel).

## Resend domain

1. [resend.com](https://resend.com) → Domains → add `noetfield.com`
2. Add DNS records Resend provides (SPF/DKIM)
3. Create API key with send permission

## Auto-heal (recommended)

```bash
cd /path/to/Noetfield
chmod +x scripts/auto-heal-www.sh
./scripts/auto-heal-www.sh
```

What it does:

1. Renames legacy `project-gc7lm` → `www` if needed  
2. Removes duplicate projects (`web`, `project-j43wr`)  
3. Syncs intake env from founder vault  
4. Deploys production  
5. Checks intake health on canonical URL + `www.noetfield.com`

Dry run: `HEAL_DRY_RUN=1 ./scripts/auto-heal-www.sh`

## Manual verify

```bash
./scripts/check-intake-health.sh
# expect: www_email_configured true, delivery_mode resend
```

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
