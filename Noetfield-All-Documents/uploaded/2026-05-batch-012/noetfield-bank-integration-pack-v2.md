# Noetfield Bank Integration Pack v2.0

Document key: `noetfield-bank-integration-pack-v2`

**Canonical regulated-financial governance SOT.** Canada-safe (RPAA / FINTRAC / OSFI boundary-aligned).
Non-custodial, non-execution, pre-execution governance coordination only.

## Position

Enterprise → Noetfield L0–L5 + SEOP → GHP → NIG → Bank/PSP/MSB → settlement rails

## Artifacts

- **CDA** — internal governance normalization (no accounts, routing, payment, settlement fields)
- **GHP** — institution-facing handoff (governance metadata only)
- **Enforcement envelope** — governance-state metadata, NOT execution triggers

## NIG

Translation/normalization boundary only. Forbidden: execution routing, transaction trigger, settlement.

## NF-CHAIN-LOCK

`H = SHA-256(L0_state + L4_snapshot + system_version)` — mismatch → C3 HARD STOP

## Regulatory

NOT MSB/PSP/custodian/settlement operator. Execution authority exclusively external institutions.
