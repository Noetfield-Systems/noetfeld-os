# Bank Pilot — demo path (read-only)

**SKU:** Bank Pilot v6.1 — governance simulation only. No execution rights.

## Audience

Design partner at a bank or credit union evaluating pre-execution governance before OSFI E-23 (May 2027).

## 30-minute demo script

1. **Positioning (5 min)** — Noetfield never touches value; policy and audit traces only ([PRODUCT_TRUTH.md](../PRODUCT_TRUTH.md)).
2. **Public site (5 min)** — [Enterprise](/enterprise/) → three offerings → [gate intake](/gate/intake/) Bank Pilot vector.
3. **Governance Console (15 min)** — Open simulation:
   - From [www `/console/`](/console/) → redirects to `platform.noetfield.com/console` (or local `:8001/console`)
   - Submit sample intent; show allow / review / reject and compliance log
   - Emphasize **shadow mode** — no payment or custody authority
4. **Intake (5 min)** — Submit [trust-brief intake](/trust-brief/intake/?vector=bank-pilot) with RID; confirm `operations@noetfield.com` workflow.

## Technical prerequisites

- Platform deployed per [GO_LIVE.md](./GO_LIVE.md)
- `RUNTIME_EVENT_STORE=postgres` for credible audit lineage in pilot

## What not to demo

- Payment rails, FX, or open-banking write access
- TrustField or VIRLUX products (separate entities)

## Follow-up artifact

Send bank pack references from `docs/SOURCE_OF_TRUTH/` (institutional narrative) under NDA — not raw internal GCIP terms on public pages.
