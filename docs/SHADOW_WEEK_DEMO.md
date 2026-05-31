# Shadow Week — partner and bank demo kit (30 minutes)

**Audience:** Bank, licensed VASP/exchange, or PSP design partner.  
**Mode:** Shadow only — no execution authority in Noetfield.

## Prerequisites

- Platform health green ([GO_LIVE.md](./GO_LIVE.md))
- Pilot API key (or dev open auth)
- Same RID used across all steps

## Script

| Step | Time | Action |
|------|------|--------|
| 1 Positioning | 5 min | [PRODUCT_TRUTH.md](../PRODUCT_TRUTH.md) — control layer, not RPAA/MSB/PSP |
| 2 Partners story | 5 min | [www /partners/](/partners/) → layer cake (L3 control, L2 partner execution) |
| 3 Evaluate | 10 min | `POST /api/v1/governance/evaluate` with `mode: shadow`, `request_id: RID-SHADOW-WEEK-…` |
| 4 Trust Ledger | 5 min | `GET /api/v1/governance/audit-export?request_id=…` + console compliance log |
| 5 Partner signal (optional) | 5 min | `POST /api/v1/governance/partner-signals` with read-only payload (balance_snapshot) |
| 6 Intake close | 5 min | [intake](/trust-brief/intake/?vector=partner-exchange) with same RID → operations@ |

## Exchange preset (curl)

```bash
curl -sS -X POST "$PLATFORM/api/v1/governance/evaluate" \
  -H "Authorization: Bearer $PILOT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "00000000-0000-4000-8000-000000000001",
    "organization_id": "00000000-0000-4000-8000-000000000002",
    "action": "place_order_intent",
    "resource_type": "partner_exchange",
    "resource_id": "shadow-week-demo",
    "mode": "shadow",
    "request_id": "RID-SHADOW-WEEK-DEMO"
  }'
```

Preset JSON also available: `GET /api/v1/governance/scenario-presets/exchange`

## MSB / PSP variant

Use `scenario-presets/msb` and [MSB_STAGING_INTEGRATION.md](./MSB_STAGING_INTEGRATION.md). Intake: `?vector=partner-msb`.

## Read-only signal example

```bash
curl -sS -X POST "$PLATFORM/api/v1/governance/partner-signals" \
  -H "Authorization: Bearer $PILOT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "00000000-0000-4000-8000-000000000001",
    "organization_id": "00000000-0000-4000-8000-000000000002",
    "partner_id": "design-partner-staging",
    "signal_kind": "balance_snapshot",
    "request_id": "RID-SHADOW-WEEK-DEMO",
    "payload": {"asset": "CAD", "available": "read_only"}
  }'
```

## Do not demo

- Order placement through Noetfield
- Named exchange routing comparisons on public calls
- TrustField / VIRLUX products

## Follow-up

- [canada-stack-2027-onepager.html](./collateral/canada-stack-2027-onepager.html) (print)
- [canada-partner-gtm-2026.md](./strategy/canada-partner-gtm-2026.md)
