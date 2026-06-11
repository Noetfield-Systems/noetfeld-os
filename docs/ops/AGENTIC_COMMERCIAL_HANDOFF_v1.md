# Agentic commercial handoff — NF-CLOUD vs Hub (v1)

**Agent tag:** `NF-CLOUD-AGENT`  
**Authority:** [FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md](./FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md)

---

## Split of work

| Layer | Owns | Does not own |
|-------|------|--------------|
| **Agentic commercial** | Send outreach, tracker rows, book demos, RUN INBOX | Product code, www deploy |
| **Founder Hub** | Approve ASK, tap actions, control plane | Bulk disk edits in Noetfield repo |
| **NF-CLOUD** | Validators, GTM www, pipeline **copy** on disk | Email/call execution |

---

## GTM_NEXT item 026 (agentic only)

**ship-design-partner-outreach-026** — design-partner pipeline **execution**:

- Named CIO contact + demo URL sent
- CRM / tracker row updated
- **Implement in agentic layer** — not `cursor/no-asf-*` disk work in this repo

**NF-CLOUD evidence already on disk:**

- [DESIGN_PARTNER_PIPELINE_v1.md](../copilot/DESIGN_PARTNER_PIPELINE_v1.md)
- [BUYER_DEBRIEF_TEMPLATE_v1.md](../copilot/BUYER_DEBRIEF_TEMPLATE_v1.md)
- [bc-ai-for-all-2026.md](../strategy/channel-outreach/bc-ai-for-all-2026.md)
- [STAGING_DEMO.md](./STAGING_DEMO.md) + `make demo-url`

---

## Handoff checklist (agentic → founder)

1. Demo URL live (`make demo-url` or `NF_STAGING_URL`)
2. Pipeline doc + debrief template linked from pilot/demo
3. Founder approves send in Hub — **founder never dials/emails directly**
4. Post-demo: debrief template → tracker row

---

## Verify (NF-CLOUD only)

```bash
./scripts/plan-with-no-asf-verify.sh
```
