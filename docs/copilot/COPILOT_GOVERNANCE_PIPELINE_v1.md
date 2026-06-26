# Copilot Governance Pack pipeline — outreach & follow-up (v1)

**Agent tag:** `NF-CLOUD-AGENT`  
**GTM priority:** #1 — one real customer  
**Execution:** Agentic layer only — see [AGENTIC_COMMERCIAL_HANDOFF_v1.md](../ops/AGENTIC_COMMERCIAL_HANDOFF_v1.md) (`ship-design-partner-outreach-026` is **not** NF-CLOUD implement).  
**Sources:** `docs/strategy/NOETFIELD_GTM_60_DAY_LOCKED_v1.md`, `docs/copilot/DESIGN_PARTNER_SOW_OUTLINE.md`

---

## Pipeline stages

| Stage | Action | Success signal |
|-------|--------|----------------|
| 1. Target | Identify CIO / Head of AI / Compliance at regulated org evaluating Copilot | Named contact + LinkedIn/email |
| 2. Hook | Send one-liner: board-ready Copilot governance evidence layer | Reply or meeting booked |
| 3. Demo | Share `{{demo_url}}/copilot/demo/` — local tunnel (`make dev-local-tunnel-bg && make demo-url`) or staging (`NF_STAGING_URL`); see [STAGING_DEMO.md](../ops/STAGING_DEMO.md) | CIO understands without 45-min explanation |
| 4. Pilot | Send Copilot Governance Pack SOW outline; scope 2–4 week readiness pilot | Signed LOI or paid pilot ($2k–10k OK) |
| 5. Proof | Org uploads evidence, generates TLE, exports board PDF | PDF used in governance meeting |

---

## Follow-up email template (copy-ready)

**Subject:** Board-ready audit trail for your Copilot rollout

Hi {{name}},

Copilot adoption needs a **board-ready decision record** — signed TLE export for audit. Noetfield produces the audit trail your Copilot deployment will be asked for later — evaluate intent, index M365 evidence, and export a signed Trust Ledger Entry your board and procurement can defend.

**5-minute demo:** {{demo_url}}/copilot/demo/

If useful, we can run a Copilot Governance Pack pilot (2–4 weeks) with one signed TLE and board pack PDF — no payment execution, no custody claims.

Best,  
{{founder_name}}

---

## Canada / B.C. public-sector channel (AI for All)

**Use when:** Provincial or federal AI adoption programs, regulated public-sector Copilot pilots, or B.C. trust-framework conversations.

**Positioning:** Noetfield is the **governance evidence layer** for Copilot adoption — board-ready TLE, confidence score, audit export. Not payment rails, custody, or MSB execution.

| Asset | Path |
|-------|------|
| Full outreach copy + email blocks | [bc-ai-for-all-2026.md](../strategy/channel-outreach/bc-ai-for-all-2026.md) |
| 5-minute demo | `{{demo_url}}/copilot/demo/` |
| Diligence one-pager | [rpaa-positioning-onepager.md](../diligence/rpaa-positioning-onepager.md) |

**Subject:** Board-ready governance evidence for your Copilot / AI for All pilot

Hi {{name}},

As {{org}} evaluates responsible AI adoption, boards and procurement teams ask for a **defensible decision record** with exportable evidence. Noetfield produces signed Trust Ledger Entries with M365 evidence metadata, confidence scores, and board-pack PDF export. We stay in the governance lane only (no payment or custody claims).

**5-minute demo:** {{demo_url}}/copilot/demo/

**Canada context:** [AI for All outreach notes](../strategy/channel-outreach/bc-ai-for-all-2026.md)

If useful, I can share our one-page diligence summary and scope a 2–4 week Copilot Governance Pack pilot.

Best,  
{{founder_name}}

---

## CRM fields (minimal)

- `org`, `contact`, `stage`, `last_touch`, `demo_url_sent`, `tle_exported`, `board_pdf_used`

---

## Verify

```bash
./scripts/plan-with-no-asf-verify.sh
```
