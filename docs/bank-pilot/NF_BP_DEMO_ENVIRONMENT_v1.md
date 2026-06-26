# Bank Pilot — Demo Environment (Synthetic Data Only)

**Version:** 1.0.0 · **Plan:** pf-0054 · **SKU:** NF-BP · **Policy pack:** `bank-pilot-v1`  
**Law:** Synthetic fixtures only — no production customer data in demos

---

## One line

Bank Pilot demos run in **shadow mode** with **synthetic operational intents** — Governance Console or API evaluate produces RID-keyed audit lineage without touching real accounts or payment systems.

---

## Demo surfaces

| Surface | URL | Use |
|---------|-----|-----|
| Public www | `/bank-pilot/` | Positioning · 5 min |
| Governance Console | `/console/` → `platform.noetfield.com/console` | Live shadow evaluate · 15 min |
| Gate intake | `/gate/intake/?vector=bank-pilot` | Intake close · 5 min |
| API (platform) | `POST /api/v1/governance/evaluate` | Technical buyers · 10 min |

**Local dev:** `http://localhost:8001/console` per [GO_LIVE.md](../GO_LIVE.md)

---

## Synthetic sample intents (safe to demo)

Use these fixtures — **never** paste real customer PII, account numbers, or transaction data.

| Intent ID | Description | Expected outcome |
|-----------|-------------|------------------|
| `BP-DEMO-001` | Approve internal AI policy draft for Copilot rollout | REQUIRE_HUMAN_REVIEW |
| `BP-DEMO-002` | Export audit package for board committee | PROCEED (shadow) |
| `BP-DEMO-003` | Initiate payment to external vendor | REJECT · forbidden financial |
| `BP-DEMO-004` | Publish regulatory report without review chain | REQUIRE_HUMAN_REVIEW |
| `BP-DEMO-005` | Shadow evaluate third-party AI vendor onboarding | PROCEED or REVIEW |

**Sample API body (shadow):**

```json
{
  "mode": "shadow",
  "policy_pack_id": "bank-pilot-v1",
  "intent": "Evaluate Copilot scope expansion for retail banking division",
  "context": { "fixture_id": "BP-DEMO-001", "synthetic": true }
}
```

---

## Demo flow (30 min)

1. Open `/bank-pilot/` — emphasize read-only · no execution rights.
2. Console — submit `BP-DEMO-001`; show confidence score + compliance log.
3. Submit `BP-DEMO-003` — show **REJECT** on forbidden financial action.
4. Export audit: `GET /api/v1/governance/audit-export?request_id=RID-…`
5. Close with intake `vector=bank-pilot` — RID threads to `operations@noetfield.com`.

Full script: [BANK_PILOT_DEMO.md](../BANK_PILOT_DEMO.md)

---

## Environment prerequisites

| Requirement | Purpose |
|-------------|---------|
| Platform deployed | Credible evaluate + export |
| `RUNTIME_EVENT_STORE=postgres` | Audit lineage for pilot credibility |
| `bank-pilot-v1` pack loaded | Shadow-only controls enforced |
| Synthetic flag in context | Marks demo fixtures in compliance log |

---

## Explicit exclusions (demo)

- No real payment initiation · no custody · no settlement
- No production M365 tenant credentials on shared screens
- No TrustField or VIRLUX product demos in same session
- No customer data export — synthetic fixtures only

---

## Verify

```bash
test -f docs/bank-pilot/NF_BP_DEMO_ENVIRONMENT_v1.md
grep -q 'synthetic' docs/bank-pilot/NF_BP_DEMO_ENVIRONMENT_v1.md
grep -q 'shadow' docs/bank-pilot/NF_BP_DEMO_ENVIRONMENT_v1.md
grep -q 'bank-pilot-v1' docs/bank-pilot/NF_BP_DEMO_ENVIRONMENT_v1.md
```

---

## Related

- [BANK_PILOT_DEMO.md](../BANK_PILOT_DEMO.md)
- [NF_BP_SHADOW_MODE_DOCS_v1.md](./NF_BP_SHADOW_MODE_DOCS_v1.md)
- [BANK_PILOT_V1_POLICY_PACK_EXPLAINER_v1.md](./BANK_PILOT_V1_POLICY_PACK_EXPLAINER_v1.md)
