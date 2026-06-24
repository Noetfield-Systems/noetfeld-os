# Metadata-Only Evidence Index

**Version:** 1.0.0 · **Plan:** pf-0072 · **SKU:** — (platform) · **Phase:** 7  
**Law:** Purview complement — not replacement · metadata-only · no mailbox custody

---

## One line

`evidence_index` in TLE v1 maps to **Purview · Entra · Audit** metadata connectors — assume Microsoft admin tools deployed; Noetfield indexes evidence IDs only.

---

## Index fields (TLE v1)

| Source | Metadata captured | Noetfield role |
|--------|-------------------|----------------|
| **Purview** | Labels · DLP posture · sensitivity | Complement — index IDs in `evidence_index` |
| **Entra ID** | CA policies · group membership signals | Complement — no identity admin |
| **M365 Audit** | Admin · Copilot audit events | Complement — no content capture |

**TLE field:** `evidence_index: purview · entra · audit`

---

## Positioning law

| Claim | Allowed |
|-------|---------|
| Assume Purview deployed | Yes |
| Replace Purview administration | **No** |
| Index metadata only | Yes |
| Full mailbox / content surveillance | **No** |
| Board go/no-go receipt layer | Yes |

Cross-ref: [CONNECTORS_CONTROLS_v1.md](./CONNECTORS_CONTROLS_v1.md) · [EVIDENCE_INTAKE_CONTRACT_v1.md](./EVIDENCE_INTAKE_CONTRACT_v1.md)

---

## www alignment

- `/federal/` — proof card → this SSOT
- `/bank-pilot/` · `/copilot/procurement/` — metadata-only scope badges
- Live proof hero — `evidence_index` in receipt mock

---

## Not in scope

- Production Purview OAuth secrets in public repo
- TrustField custody or payment evidence
- FINTRAC transaction monitoring

---

## Verify

```bash
test -f docs/diligence/NF_METADATA_EVIDENCE_INDEX_v1.md
grep -q 'NF_METADATA_EVIDENCE_INDEX' federal/index.html
grep -q 'Purview' docs/diligence/NF_METADATA_EVIDENCE_INDEX_v1.md
```
