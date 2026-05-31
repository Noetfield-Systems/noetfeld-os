# MSB staging integration checklist (design partner)

Use with [MSB_STAGING_INTEGRATION.md](../../docs/MSB_STAGING_INTEGRATION.md).

## Pre-flight

- [ ] NDA signed  
- [ ] Shadow Pack SOW signed (or Trust Brief in flight)  
- [ ] Pilot API key issued (`tenant_uuid:secret`)  
- [ ] MSB staging URLs whitelisted for CORS if browser console used  

## Integration

- [ ] `POST /api/v1/governance/evaluate` — `initiate_transfer_intent` / `msb_payment` — `mode: shadow`  
- [ ] Shared RID across evaluate, signals, intake email  
- [ ] MSB app calls evaluate **before** MSB payment API (staging)  
- [ ] `POST /api/v1/governance/partner-signals` — read-only payload only  
- [ ] `GET /api/v1/governance/audit-export?request_id=` — sample for compliance  
- [ ] Webhook endpoint tested (optional)  

## Sign-off

- [ ] MSB engineering lead sign-off on shadow flow  
- [ ] MSB compliance acknowledges Noetfield non-execution boundary  
- [ ] Annual API license proposal sent  

**Target go-live (enforce):** __________ (requires addendum)
