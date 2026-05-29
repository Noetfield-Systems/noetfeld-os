# Noetfield L3 Execution Engine (EGS v2.0)

Document key: `noetfield-l3-execution-engine-egs-v2`

Enforcement-only runtime. **Subordinate to** `noetfield-bank-integration-pack-v2` on all execution boundaries.

## Rules

- R1: L2 supremacy — cannot override REJECT
- R3: Execute forward only if APPROVE + SAFE + INSIDE + valid SoT binding
- R4–R5: No internal financial logic; external banks/PSP/MSB execute EFT/FX/settlement

Logs immutable audit per action. Does NOT evaluate intent or mutate CDA/PHO.
