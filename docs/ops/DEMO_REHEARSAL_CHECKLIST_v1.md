# 5-minute demo rehearsal checklist (v1)

**Agent tag:** `NF-CLOUD-AGENT`  
**GTM priority:** #2 — killer demo  
**Entry URL:** `http://localhost:13080/copilot/demo/` (or staging)

---

## Pre-demo (5 min before)

- [ ] `./scripts/plan-with-no-asf-verify.sh` — PASS
- [ ] `make demo-url` or `NF_STAGING_URL` set for shareable link
- [ ] Browser tabs open: `/copilot/demo/`, `/cognitive-dashboard`, `/evaluate`, `/workspace/connectors`, `/workspace`
- [ ] Sample TLE visible: `/workspace/TLE-015DCFB8B953` or fresh pilot e2e draft

---

## Locked narrative (6 steps)

1. **Hook:** "Copilot adoption needs a board-ready decision record, not another chatbot."
2. **Evaluate** → RID + **confidence score** on `/result/{rid}`
3. **Connect** M365 (or three evidence types) → Evidence Index
4. **Draft TLE** → highlight confidence score and go/no-go
5. **Approve** sequential chain (CIO → Legal → Security)
6. **Export** board pack PDF + mention audit JSON for diligence

---

## Buyer personas (A/B talk track)

| Persona | Emphasize |
|---------|-----------|
| **CIO** | Risk meter, confidence %, go/no-go decision, audit RID |
| **Legal** | Immutable audit trail, export bundle JSON, conditions list |
| **Procurement** | `/copilot/procurement/`, one-click ZIP, NIST AI RMF references |
| **Board** | Board pack PDF, TLE sample report, category one-liner |

---

## Script A/B variants

**A (category):** "We produce the audit trail your Copilot deployment will be asked for later."

**B (outcome):** "Board-ready AI approval system — evidence, signed TLE, PDF in five minutes."

Use A for first touch; B if they ask "what do you sell?"

---

## Post-demo

- [ ] Send procurement pack link if buyer asks for diligence
- [ ] Log debrief in design-partner pipeline stage
- [ ] Update `reports/cursor-reply-latest.txt` if agent-run rehearsal

---

## Verify

```bash
./scripts/plan-with-no-asf-verify.sh
make verify-gtm   # optional before external share
```
