# Intake operations — &lt;24h response

**Inbox:** operations@noetfield.com (canonical — [packages/config/noetfield_config/intake.py](../packages/config/noetfield_config/intake.py))

## Platform wiring

| Setting | Purpose |
|---------|---------|
| `INTAKE_OPS_WEBHOOK_URL` | Slack-compatible webhook; fires on each `POST /api/intake` |
| `GET /api/intake/health` | Confirms `ops_webhook_configured` |

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
