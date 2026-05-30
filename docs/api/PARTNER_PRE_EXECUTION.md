# Partner pre-execution integration (design)

## Pattern

Accredited integrators and bank PSPs call **Noetfield evaluate** before their own execution layer:

```mermaid
sequenceDiagram
  participant Bank as Bank orchestrator
  participant NF as Noetfield evaluate API
  participant PSP as Partner execution

  Bank->>NF: POST /api/v1/governance/evaluate (shadow|enforce)
  NF-->>Bank: decision + request_id + policy_refs
  alt allowed
    Bank->>PSP: execute (outside Noetfield)
  else rejected
    Bank->>Bank: block + audit export
  end
```

## Webhook: `governance.decision.recorded`

When `GOVERNANCE_WEBHOOK_URLS` is set, each evaluate emits:

```json
{
  "event": "governance.decision.recorded",
  "data": {
    "request_id": "RID-…",
    "correlation_id": "bank-run-123",
    "tenant_id": "…",
    "decision": "REJECT",
    "allowed": false,
    "reason_code": "…",
    "policy_refs": ["…"],
    "mode": "shadow"
  }
}
```

- **No PII** in the default payload.
- Optional **HMAC** via `GOVERNANCE_WEBHOOK_SECRET` → header `X-Noetfield-Signature: sha256=…`.

## Licensed MSB / PSP pattern

MSBs and RPAA-supervised PSPs call evaluate **before** their own payment or remittance APIs. Noetfield never places orders or holds funds.

```mermaid
sequenceDiagram
  participant App as MSB_application
  participant NF as Noetfield_evaluate
  participant Pay as MSB_payment_API

  App->>NF: evaluate initiate_transfer_intent msb_payment shadow
  NF-->>App: allowed + RID
  alt allowed
    App->>Pay: licensed_execution_only
    App->>NF: partner-signals read_only
  end
```

- Preset: `GET /api/v1/governance/scenario-presets/msb`
- Guide: [MSB_STAGING_INTEGRATION.md](../MSB_STAGING_INTEGRATION.md)
- Intake: `vector=partner-msb`

## SIEM / GRC

Map `reason_code` and `policy_refs` to ServiceNow, Archer, or Splunk using `request_id` as the correlation key shared with intake (`POST /api/intake`) and ops email.

## Enterprise tier (deferred in code)

- mTLS client certificates per tenant
- Per-tenant policy packs with Postgres RLS
- Signed webhook replay protection

Track engineering work in GitHub Issues (`engineering`), not public root trackers.
