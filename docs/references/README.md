# External governance references (agent index)

**Status:** LOCKED index · Update only with ASF + product signoff when adding new reference books.

| Book | Path | Use when |
|------|------|----------|
| **Governance sources** | [GOVERNANCE_SOURCES_HANDBOOK_LOCKED_v1.md](./GOVERNANCE_SOURCES_HANDBOOK_LOCKED_v1.md) | Frameworks, Copilot/Purview, SOC 2, FFIEC, EU AI Act, NIST, ISO 42001 |
| **Drift detection** | [GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md](./GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md) | Policy/config/model/data/semantic drift, continuous monitoring, post-market surveillance |

**Reliability rule:** Prefer **Tier 1** (official law/standards/government) and **Tier 2** (vendor primary docs). Tier 3–4 = orientation only.

**Related in-repo:**

| Topic | Path |
|-------|------|
| Agent read order | [docs/ops/AGENT_READ_LINKS_LOCKED_v1.md](../ops/AGENT_READ_LINKS_LOCKED_v1.md) |
| Evidence contract | [docs/diligence/EVIDENCE_INTAKE_CONTRACT_v1.md](../diligence/EVIDENCE_INTAKE_CONTRACT_v1.md) |
| Connectors controls | [docs/diligence/CONNECTORS_CONTROLS_v1.md](../diligence/CONNECTORS_CONTROLS_v1.md) |
| Trust Ledger blueprint | [docs/spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md](../spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md) |
| TLE schema | [docs/spec/schemas/tle-v1.schema.yaml](../spec/schemas/tle-v1.schema.yaml) |

**Filename policy:** New reference books use `*_LOCKED_v1.md` suffix. Do not rename locked files without founder approval.

**Maintenance:** Bump `Last reviewed` in each book; add changelog section. Regenerate links if primary URLs move (prefer DOI / standards body canonical URLs).
