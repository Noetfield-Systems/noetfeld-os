# Proof case — Copilot evaluate → TLE → board export (redacted v1)

**Status:** Public-safe redacted narrative for procurement and sales  
**Locked:** 2026-06-15  
**Live demo:** [https://www.noetfield.com/copilot/proof-case/](https://www.noetfield.com/copilot/proof-case/)  
**Samples:** [trust-ledger/sample-report/](https://www.noetfield.com/trust-ledger/sample-report/)

---

## Scenario (synthetic — structure matches production pilot)

**Organization:** Northstar Financial Group (synthetic) · financial services · Canada  
**Intent:** Copilot rollout to production M365 tenant — pre-execution governance check  
**Policy context:** Copilot Acceptable Use v3.2 published; stale v3.1 briefings invalidated  

---

## Timeline

| Step | Action | Artifact |
|------|--------|----------|
| 1 | Policy SSOT updated (guest sharing blocked in production scope) | `SSOT_CHANGED` event |
| 2 | 2 pending evaluations invalidated; re-brief queued | Invalidation list |
| 3 | `POST /evaluate` — actor: security-team, action: copilot_rollout | RID issued |
| 4 | Decision: **review** · confidence **0.80** · risk_score 20 | Evaluate response |
| 5 | TLE drafted from evaluate + evidence index | `TLE-015DCFB8B953` (sample) |
| 6 | Board PDF excerpt + procurement ZIP | export_integrity: **PASS** |

---

## Evaluate payload (redacted)

```json
{
  "actor": "security-team",
  "action": "copilot_rollout",
  "context": "Copilot rollout to production M365 tenant — re-briefed after policy v3.2",
  "metadata": {
    "policy_version": "3.2",
    "source": "copilot-governance-pilot"
  }
}
```

---

## Evaluate response (redacted)

```json
{
  "decision": "review",
  "risk_score": 20,
  "rid": "RID-SSOT-DEMO-1425",
  "policy_version": "3.2",
  "reason": ["Production Copilot rollout requires v3.2 evidence index and approver chain."],
  "conditions": ["Route to compliance owner with RID attached."]
}
```

---

## TLE receipt (sample fields)

| Field | Value |
|-------|-------|
| tle_id | TLE-015DCFB8B953 |
| decision | review |
| confidence_score | 0.80 |
| rid | RID-SSOT-DEMO-1425 |
| evidence_index | purview · entra · audit |
| export_integrity | PASS · fail closed on tamper |

Full YAML samples: `/trust-ledger/sample-report/samples/`

---

## Board digest excerpt (demo)

> Policy v3.2 published; 2 stale evaluations invalidated; fresh evaluate → **review** with signed receipt. SSOT change closes governance latency — agents re-brief on current policy. Signed TLE + board PDF for procurement — no execution or payment rails.

---

## Success signal (W3)

One org uses **board PDF in a real governance meeting** — Copilot Governance Pack ($2k–10k · 90 days).

---

## Reproduce

1. **Interactive:** [https://www.noetfield.com/copilot/demo/](https://www.noetfield.com/copilot/demo/)  
2. **CLI:** `python3 scripts/run_ssot_governance_demo.py` (repo)  
3. **Sandbox:** [https://www.noetfield.com/start/](https://www.noetfield.com/start/) — first evaluate returns RID  

---

**End redacted v1**
