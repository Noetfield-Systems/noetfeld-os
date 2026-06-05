# Evidence Intake Contract v1

**Between:** Customer (“Client”) and Noetfield Systems (“Provider”)  
**Purpose:** Define metadata-only evidence ingestion for Copilot governance assessments and Trust Ledger Entries (TLE v1).

---

## 1. Scope

Provider will ingest **metadata only** from the following required sources unless Client opts in to expanded capture in writing:

| Source | Default mode |
|--------|----------------|
| Microsoft Purview (sensitivity labels, policies) | metadata_only |
| Microsoft Entra ID (Conditional Access, group membership summaries) | metadata_only |
| Microsoft 365 Unified Audit Log (Copilot-related events) | metadata_only |
| SharePoint (site labels, sharing flags) | metadata_only |

**Out of scope:** payment data, custody, message bodies, full document content (unless addendum signed).

---

## 2. Client responsibilities

- Grant least-privilege app registration / service principal scopes listed in Connector Manifest
- Designate approvers: CIO (owner), Legal, Security
- Provide engagement RID and pilot tenant IDs
- Confirm no production Copilot rollout before Go/No-Go TLE unless written waiver

---

## 3. Provider deliverables

- Evidence Index catalog (hashes, timestamps, source, sensitivity label)
- ≥1 signed **TLE v1** per engagement phase (Go, Conditional, or Rejected)
- Board Pack PDF export (evidence index + approval chain + audit digest reference)
- Retention per Section 5

---

## 4. Ingestion rules

- Default: **metadata_only**; `full_capture` requires signed addendum
- PII redaction pipeline applied before any expanded capture
- Excluded: sources not listed in contract; consumer personal devices

---

## 5. Retention & audit

- Evidence metadata: **90 days** default (configurable in SOW)
- TLE entries: duration of engagement + **7 years** archive option
- Client may request audit bundle export by RID at any time during engagement

---

## 6. Security

- Evidence hashed at ingest; `audit_digest` per TLE via KMS
- Approver sign-off requires role-mapped identity + 2FA
- Noetfield does not initiate payments or execute transactions on Client systems

---

## 7. Acceptance

Engagement accepted when:

1. This contract is signed  
2. Connector onboarding complete  
3. First TLE draft delivered within **10 business days** of kickoff  

**Signature blocks:** _[Client]_ _[Provider]_ _Date_

---

**Related:** [TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md](../spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md) · [tle-v1-go.yaml](../spec/examples/tle-v1-go.yaml)
