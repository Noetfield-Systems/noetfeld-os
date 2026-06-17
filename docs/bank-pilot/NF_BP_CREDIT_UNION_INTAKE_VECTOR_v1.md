# Bank Pilot — Credit Union Intake Vector (NF-BP)

**Version:** 1.0.0 · **Plan:** pf-0053 · **SKU:** NF-BP  
**Hub slot:** NP3-CU-001 · **Send policy:** Hub approve before outreach

---

## One line

Credit unions evaluating shadow governance route through the **`bank-pilot` intake vector** — read-only simulation, separate from Copilot wedge (`copilot-governance`) and TrustField MSB attestation.

---

## Canonical intake URL

| Param | Value |
|-------|-------|
| `vector` | `bank-pilot` |
| `interest` | `bank-pilot` |
| `segment` | `credit-union` |

**Primary URL:** `/trust-brief/intake/?vector=bank-pilot&interest=bank-pilot&segment=credit-union`

**Gateway alias:** `/gate/intake/?vector=bank-pilot&interest=bank-pilot&segment=credit-union&auto=1`

**Subject template:** `Noetfield — Bank Pilot inquiry (RID-…)` · inbox `operations@noetfield.com`

---

## Routing table

| Entry surface | CTA | Vector |
|---------------|-----|--------|
| `/bank-pilot/` | Discuss Bank Pilot | `bank-pilot` |
| `/gate/intake/` Bank Pilot card | Bank Pilot intake | `bank-pilot` |
| Credit union outreach (Hub) | Shadow pilot apply | `bank-pilot` + `segment=credit-union` |
| `/templates/` OSFI E-23 Bank Shadow | Request shadow pilot | `bank-pilot` |

**Do not route credit union MSB/RPAA evidence to this vector** — handoff to TrustField TF-001.

---

## Buyer profile

| Attribute | Credit union shadow pilot |
|-----------|---------------------------|
| Size | Provincial / federal CU · OSFI-adjacent |
| Pain | Copilot + data governance before production |
| SKU | NF-BP · `bank-pilot-v1` shadow only |
| Price band | CAD $2k–$10k orientation · 12-week pilot |
| Upgrade from | NF-RD Copilot Pack or NF-TB Trust Brief — separate SOWs |

---

## Intake form guidance (Hub)

1. Confirm **read-only shadow** scope — no payment or custody authority.
2. Capture: CU legal name · province · M365 Copilot status · target committee (board / risk / IT).
3. Attach: [NF_BP_SHADOW_MODE_DOCS_v1.md](./NF_BP_SHADOW_MODE_DOCS_v1.md) · [BANK_PILOT_DEMO.md](../BANK_PILOT_DEMO.md).
4. RID-thread all replies — footer `data-rid` on intake submit.
5. **Founder never sends** — Hub approves per `N_P3_HUB_QUEUE.yaml`.

---

## vs Copilot Governance Pack (NF-RD)

| Question | NF-RD Copilot Pack | NF-BP Bank Pilot |
|----------|-------------------|------------------|
| Primary hook | M365 Copilot rollout receipt | Institutional shadow simulation |
| Policy pack | `copilot-governance-v1` | `bank-pilot-v1` |
| Intake vector | `copilot-governance` | `bank-pilot` |
| Lead wedge | **Yes** — homepage primary CTA | Tertiary — institutional lane |

Credit unions may start on NF-RD; upgrade to NF-BP requires **separate SOW**.

---

## Anti-paths

- No FINTRAC KYB pack on Noetfield
- No TrustField TF-001 in same intake thread or SOW
- No payment rails · no custody · no MSB execution claims
- No fourth contract SKU

---

## Verify

```bash
test -f docs/bank-pilot/NF_BP_CREDIT_UNION_INTAKE_VECTOR_v1.md
grep -q 'vector=bank-pilot' docs/bank-pilot/NF_BP_CREDIT_UNION_INTAKE_VECTOR_v1.md
grep -q 'credit-union' docs/bank-pilot/NF_BP_CREDIT_UNION_INTAKE_VECTOR_v1.md
grep -q 'shadow' docs/bank-pilot/NF_BP_CREDIT_UNION_INTAKE_VECTOR_v1.md
```

---

## Related

- [CREDIT_UNION_COPILOT_PACK_v1.md](../copilot/CREDIT_UNION_COPILOT_PACK_v1.md)
- [NF_BP_SHADOW_MODE_DOCS_v1.md](./NF_BP_SHADOW_MODE_DOCS_v1.md)
- [COMMERCIAL_INBOX_PACKAGING_LOCKED_v1.md](../ops/COMMERCIAL_INBOX_PACKAGING_LOCKED_v1.md)
