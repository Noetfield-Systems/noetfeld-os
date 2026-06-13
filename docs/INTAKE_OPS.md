# Intake operations — &lt;24h response

**Inbox:** operations@noetfield.com (canonical — [packages/config/noetfield_config/intake.py](../packages/config/noetfield_config/intake.py))

## Platform wiring

## Platform + www wiring

| Setting | Where | Purpose |
|---------|-------|---------|
| `RESEND_API_KEY` | **Vercel www** + platform | Delivers every form to `operations@noetfield.com`; `Reply-To` = submitter |
| `INTAKE_EMAIL_TO` | Vercel www + platform | Default `operations@noetfield.com` |
| `INTAKE_AUTO_ACK_ENABLED` | Vercel www + platform | Instant receipt to submitter |
| `INTAKE_OPS_WEBHOOK_URL` | platform | Slack-compatible webhook (optional) |
| `GET /api/intake/health` | www or platform | `ops_email_configured` / `www_email_configured` |

## Answering intakes

1. **Form submit** → email lands in `operations@noetfield.com` with **Reply-To: submitter@…**
2. **Hit Reply** in Gmail/Outlook — your response goes directly to the prospect
3. **Templates:** [ops/templates/msb/INTAKE_RESPONSE_TEMPLATES.md](../ops/templates/msb/INTAKE_RESPONSE_TEMPLATES.md) — copy to `ops/private/msb/` via `./scripts/market-entry-bootstrap.sh`
4. **Direct email** to operations@ still works — same inbox if Google Workspace is configured

Templates for replies: copy [ops/templates/msb/INTAKE_RESPONSE_TEMPLATES.md](../ops/templates/msb/INTAKE_RESPONSE_TEMPLATES.md) to `ops/private/msb/` via `./scripts/market-entry-bootstrap.sh`.

## SLA (market entry)

1. **&lt;24h** — acknowledge intake; reference **RID** from submission (or assign `RID-…` via console / `governance_rid`).
2. **Same thread** — offer 30-min Shadow Week ([SHADOW_WEEK_DEMO.md](./SHADOW_WEEK_DEMO.md)).
3. **Trust Brief** — attach scope from [OFFERINGS_LOCKED.md](../OFFERINGS_LOCKED.md); invoice path for $10,000 CAD.
4. **Partner** — route to [/partners/](../partners/index.html) vector; no custom SKU promises.

## Intake API fields (for ops)

- `intake_id` — system id
- `request_id` — RID lineage (may be empty; prompt prospect to reuse one RID per thread)
- `vector` — e.g. `partner-msb`, `bank-pilot`, `copilot`
- `sku` — offering hint

Admin review (server secret): `GET /api/intake/recent` with `X-Admin-Secret` — see [PRACTICAL_PLAYBOOK.md](./PRACTICAL_PLAYBOOK.md).
