# AIA ↔ TLE Field Mapping (v1)

| Field | Value |
|-------|--------|
| **Doc id** | `noetfield-aia-tle-mapping-v1` |
| **Parent** | [FEDERAL_GOVERNANCE_PACK_v1.md](./FEDERAL_GOVERNANCE_PACK_v1.md) |
| **Updated** | 2026-06-02 |

**Purpose:** Orientation crosswalk between Treasury Board **Algorithmic Impact Assessment (AIA)** fields and Noetfield **Trust Ledger Entry (TLE v1)** exports. TLE artifacts are **supplementary** — they do not replace completing, peer-reviewing, or publishing an AIA on Open Government.

**AIA structure reference:** [Canada.ca — Algorithmic Impact Assessment](https://www.canada.ca/en/government/system/digital-government/digital-government-innovations/responsible-use-ai/algorithmic-impact-assessment.html) (risk questionnaire + mitigation questionnaire + impact level I–IV).

---

## 1. Mapping legend

| Symbol | Meaning |
|--------|---------|
| **Direct** | TLE field or export slice maps cleanly to AIA table row |
| **Partial** | TLE supports narrative; human AIA author completes remainder |
| **Orientation** | Citation or checklist only — not auto-filled |
| **N/A** | Outside Noetfield product scope |

---

## 2. Project identification

| AIA section / field | TLE v1 / export field | Coverage | Notes |
|---------------------|----------------------|----------|-------|
| Project name | `metadata.project_name` | Partial | Set in evaluate context or workspace |
| Department / institution | `metadata.tenant_org` | Partial | From intake; not verified against GC directory |
| System name / version | `metadata.system_id` · `tle.version` | Direct | RID + version on every export |
| Automated decision? (ADS scope) | `metadata.ads_scope` · evaluate `action` | Partial | Buyer declares ADS vs gen-AI-only |
| Impact level (I–IV) | `metadata.impact_level` | Orientation | Noetfield does not assign level — buyer/TBS |
| AIA publication status | Export README + `published_aia_url` | Orientation | Link field optional in procurement ZIP |

---

## 3. Risk areas (AIA risk questionnaire — orientation)

The AIA risk tool uses themed questions across rights, health, economic interests, and similar domains. Below maps **governance evidence types** Noetfield can attach — not individual AIA question IDs (which change with tool versions).

| AIA risk theme | TLE / evidence artifact | Coverage | Buyer action |
|----------------|-------------------------|----------|--------------|
| **Transparency & explanation** | TLE decision narrative · approval chain | Direct | Paste summary into AIA narrative fields |
| **Data quality & bias** | Evidence index refs (Purview labels, DLP) | Partial | Metadata only — no model training audit |
| **Rights & freedoms** | Evaluate deny/review decisions log | Partial | Shadow-mode receipts before production |
| **Health & safety** | Policy rule IDs · human-in-the-loop flag | Partial | Department validates domain fit |
| **Economic interests** | Audit export slice · RID lineage | Partial | Supports accountability, not economic modeling |
| **Continuity of service** | Change-notification export hook | Orientation | Spec — not production SLA |
| **Reversibility / appeal** | TLE `decision` + `review_required` | Partial | Maps to HITL / escalation narrative |
| **Privacy (PIA linkage)** | `metadata.pia_reference` | Orientation | Link to departmental PIA — not created by Noetfield |

---

## 4. Mitigation measures (AIA mitigation questionnaire)

| AIA mitigation theme | TLE / Noetfield control | Coverage | Notes |
|----------------------|-------------------------|----------|-------|
| **Human oversight** | Approval chain · `approver_ids` · timestamps | Direct | Core TLE v1 field set |
| **Monitoring & logging** | Audit log export · connector ingest receipts | Direct | Metadata M365 + governance API |
| **Staff training** | Orientation only | N/A | Departmental LMS — cite in AIA manually |
| **Documentation & record-keeping** | Procurement ZIP · board PDF · README | Direct | Tamper-fail integrity on export |
| **Third-party / vendor diligence** | Sources Book citations in ZIP | Partial | Framework orientation — not vendor audit |
| **Security controls** | Purview · Entra · Defender metadata index | Partial | See [GC_COPILOT_PIN_CHECKLIST_v1.md](./GC_COPILOT_PIN_CHECKLIST_v1.md) |
| **Scheduled review / update** | TLE version history · `review_due` | Partial | Aligns with ADM §6.1.3 update cadence |
| **Peer review support** | Export bundle for peer reviewers | Partial | Jan 2025 [Guide to Peer Review](https://www.canada.ca/en/government/system/digital-government/digital-government-innovations/responsible-use-ai/progress.html) — human process |

---

## 5. Impact level artifact matrix

| ADM impact level | Typical GC approval | Noetfield export satisfies (orientation) |
|------------------|---------------------|------------------------------------------|
| **Level I** | Departmental | TLE + PIN checklist + evaluate log |
| **Level II** | Deputy head (Dept) | Above + board PDF + AIA supplementary appendix |
| **Level III** | Deputy head (Dept) + TBS notification | Above + explicit HITL evidence + change log |
| **Level IV** | TBS approval required | **Partial only** — Noetfield does not substitute TBS sign-off |

---

## 6. TLE export bundle → AIA workflow

```text
1. Complete departmental AIA draft (official tool)
2. Run Noetfield evaluate on Copilot/Studio operational intents
3. Approve TLE v1 → generates signed receipt + evidence index
4. Attach procurement ZIP / board PDF as supplementary AIA appendix
5. Peer review → publish to Open Government (departmental process)
6. Register entry in GC AI Register (if in scope)
```

---

## 7. Sample metadata block (YAML orientation)

```yaml
# Orientation only — not a shipped schema guarantee
metadata:
  lane: federal
  project_name: "GC Copilot rollout — Department X"
  system_id: "m365-copilot-dept-x"
  ads_scope: false  # gen-AI assistance; not ADS — buyer validates
  impact_level: null  # assigned by department / AIA tool
  published_aia_url: ""
  pia_reference: ""
evidence_index:
  - connector: m365-purview
    ref: "label-policy-summary"
  - connector: m365-entra
    ref: "conditional-access-baseline"
decision:
  outcome: allow  # allow | deny | review
  confidence_score: 0.82
  rid: "RID-EXAMPLE"
```

---

## 8. Limits

- Noetfield does **not** auto-populate the AIA web tool or assign impact levels.
- Metadata-only M365 — no full content exfiltration for bias or quality analysis.
- Copilot for Work scope is **unclassified** per PIN — mapping assumes departmental scope confirmation.
- Question-level mapping to all 65+ risk and 41+ mitigation items requires departmental GRC pairing in engagement.

---

## 9. Related

| Doc | Role |
|-----|------|
| [FEDERAL_GOVERNANCE_PACK_v1.md](./FEDERAL_GOVERNANCE_PACK_v1.md) | Lane SSOT |
| [GC_COPILOT_PIN_CHECKLIST_v1.md](./GC_COPILOT_PIN_CHECKLIST_v1.md) | M365 PIN controls |
| [GOVERNANCE_SOURCES_BOOK_v1.md](../reference/GOVERNANCE_SOURCES_BOOK_v1.md) | Framework citations for ZIP |
