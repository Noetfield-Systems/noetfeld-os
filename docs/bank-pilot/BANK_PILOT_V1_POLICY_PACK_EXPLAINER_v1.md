# bank-pilot-v1 Policy Pack — Buyer-Facing Explainer

**Version:** 1.0.0 · **Plan:** pf-0050 · **SKU:** NF-BP · **Pack ID:** `bank-pilot-v1`  
**Shipped:** `packages/policy-packs/bank-pilot-v1.json` · template `osfi-e23-bank`  
**Route:** `/bank-pilot/` · `/templates/`

---

## One line for procurement

`bank-pilot-v1` is Noetfield's **shadow-only** policy pack for FRFI governance simulation — pre-execution evaluate with confidence thresholds and human review on high-impact actions. **No payment, custody, or settlement authority.**

---

## What the pack enforces

| Control | Buyer meaning |
|---------|---------------|
| `confidence:min-threshold` | Decisions below **0.80** confidence require review |
| `human-review:high-impact` | High-impact actions need explicit human sign-off |
| `autonomy:no-silent-publication` | No autonomous publish without review chain |
| `inspectors:bounded-execution` | Inspector loops capped (limit: 2) |
| `bank:shadow-only` | **Read-only mode** — no financial execution |

---

## High-impact actions (human review required)

- `approve_workflow`
- `execute_inspector_action`
- `publish_report`
- `export_audit_package`

---

## Blocked autonomous actions

- All high-impact actions above
- Plus: `execute_payment` · `initiate_payment`

---

## Forbidden financial actions (never in Noetfield scope)

- `submit_payment_intent` · `initiate_payment` · `execute_payment`
- `route_settlement` · `settlement_orchestration` · `execute_transfer`
- `custody_move` · `fx_execution` · `corridor_route` · `treasury_route`

**Buyer line:** Noetfield does not move funds; licensed institutions execute externally.

---

## Evidence requirements (orientation)

| Requirement | Purpose |
|-------------|---------|
| `model_inventory_export` | AI model inventory for governance review |
| `third_party_ai_register` | Third-party AI vendor register |
| `audit_log_retention_policy` | Retention alignment for audit export |

Metadata-only orientation — buyer provides policy artifacts, not raw transaction data.

---

## OSFI E-23 adjacency

Pack template `osfi-e23-bank` supports **orientation** toward OSFI E-23 model risk evidence (May 2027) — independent-style decision records, not regulatory certification or OSFI program replacement.

---

## How to try it

| Path | Action |
|------|--------|
| Sandbox / console | Shadow evaluate via Governance Console |
| Template | `/templates/` → OSFI E-23 Bank Shadow |
| Intake | `/gate/intake/?vector=bank-pilot&interest=bank-pilot` |

---

## Not included (anti-paths)

- FINTRAC KYB pack (wrong SKU — not shipped)
- TrustField TF-001 RPAA delivery in same engagement
- `copilot-governance-v1` — separate pack for Copilot wedge (NF-RD)
- Fourth contract SKU

---

- [NF_BP_SHADOW_MODE_DOCS_v1.md](./NF_BP_SHADOW_MODE_DOCS_v1.md)
- [BANK_PILOT_DEMO.md](../BANK_PILOT_DEMO.md)
- Pack source: `packages/policy-packs/bank-pilot-v1.json`
- Pack source: `packages/policy-packs/bank-pilot-v1.json`
