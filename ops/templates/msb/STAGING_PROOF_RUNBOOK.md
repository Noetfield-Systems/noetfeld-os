# Staging proof runbook — first paid partner

**When:** After Trust Brief deposit or Shadow Pack signature.  
**Goal:** Partner runs shadow **evaluate** + **audit-export** in **their** environment with a shared RID.

Full technical steps: [MSB_STAGING_INTEGRATION.md](../../../docs/MSB_STAGING_INTEGRATION.md) · checklist: [STAGING_INTEGRATION_CHECKLIST.md](./STAGING_INTEGRATION_CHECKLIST.md).

---

## 1. Engage

| Item | Value |
|------|--------|
| Partner | |
| RID | `RID-MSB-STAGING-___` |
| Tenant UUID | (from pilot key) |
| Pilot key issued | ☐ |

## 2. Partner engineering

- [ ] `POST /api/v1/governance/evaluate` — `mode: shadow`, MSB-shaped action
- [ ] `GET /api/v1/governance/audit-export?request_id=<RID>`
- [ ] Optional: `POST /api/v1/governance/partner-signals` — read-only payload only
- [ ] Preset reference: `GET /api/v1/governance/scenario-presets/msb`

## 3. Evidence call (30 min)

- [ ] Show decision + `reason_code` + `policy_refs` on RID
- [ ] Show compliance log / export slice for procurement
- [ ] Confirm **their** payment API still owns execution

## 4. Close staging phase

- [ ] Sign-off email from partner compliance or CTO
- [ ] Annual license discussion ([API_LICENSE_SCHEDULE_TEMPLATE.md](./API_LICENSE_SCHEDULE_TEMPLATE.md))
- [ ] Update `OUTREACH_TRACKER.md` — Staging live = Yes

## Demo RID script

Use the same RID in Shadow Week, intake, and staging calls — [SHADOW_WEEK_DEMO.md](../../../docs/SHADOW_WEEK_DEMO.md).
