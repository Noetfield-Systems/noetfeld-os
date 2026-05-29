# Canada trust and procurement copy (API + www)

Use this language in vendor DD, DPAs, and public API documentation.

## Data processing

- **Region:** Canada-first processing for pilot and production engagements (contract-specific residency schedule).
- **Subprocessors:** Listed in the executed DPA and secure vendor pack — not in the public git tree.
- **Intake:** `POST /api/intake` records engagement metadata only; avoid confidential payloads in public forms.

## OSFI E-23 (third-party AI)

- **Shadow mode:** Bank Pilot uses `mode: shadow` on `POST /api/v1/governance/evaluate` — policy decisions without execution rights inside Noetfield.
- **Evidence:** `GET /api/v1/governance/vendor-evidence` and `GET /api/v1/governance/audit-export` feed vendor due diligence.

## Consumer-Driven Banking (CDB)

Noetfield provides **policy and consent governance adjacency** before partner execution. We do **not** offer open-banking write APIs, screen-scraping, or payment initiation inside this product.

## Non-PSP statement

Noetfield does not execute payments, hold customer funds, or operate as a money services business or payment service provider. Accredited partners and bank PSPs execute outside this boundary.
