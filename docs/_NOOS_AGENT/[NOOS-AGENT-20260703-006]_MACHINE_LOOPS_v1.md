# [NOOS-AGENT-20260703-006] Machine Loops v1

<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260703-006
doc_type: MACHINE_LOOPS
workspace_root: /Users/sinakazemnezhad/Desktop/Noetfield-Systems/noetfeld-OS
classification: INTERNAL — zero-founder operational mechanics
related_registry: data/noos-machine-loops-config-v1.json
-->

**Version:** v1.1 · **Status:** ACTIVE (E2E wired in NOOS)  
**Upstream:** Desktop `MACHINE_LOOPS_v1.md`  
**Canon interface:** [FOUNDER_CANON_INTERFACE v1]([NOOS-AGENT-20260703-005]_FOUNDER_CANON_INTERFACE_v1.md)

---

## 0. Structural rules

**R1 — Fresh context per role.** Worker, critic, auditor, researcher, repairer each start fresh: canon pointer + dispatch + live repo state only.

**R2 — Machine dispatch from templates.** Templates in `.agent-policy/dispatch-templates/` (G6-protected). Reconciler instantiates from receipts/queue via `scripts/noos_machine_loops_v1.py reconcile`.

---

## Loop map (E2E)

| Loop | Entry | Receipt schema |
|------|-------|----------------|
| Worker | `make local-lane` / worker kernel | `noos-worker-kernel-receipt-v1` |
| Machine validation | `make machine-validate-merge` | `noos-machine-merge-validation-v1` |
| Adversarial critic | `make machine-critic` / gel-ci | `noos-machine-critic-receipt-v1` |
| Self-repair | `make machine-reconcile` | `noos-machine-repair-dispatch-v1` |
| Outside audit | `make machine-audit` / weekly GHA | `noos-outside-audit-receipt-v1` |
| Deep research | `make machine-research` | `noos-research-memo-v1` |
| Kaizen | governed-autorun §Kaizen | `noos-kaizen-*` |
| Autonomy expansion | `make machine-status` | `data/founder-trigger-ledger-v1.json` |

---

## Merge authority (T0–T3)

| Tier | Class | Authority |
|------|-------|-----------|
| T0 | docs, tests, receipts | machine on CI+critic |
| T1 | scoped app code | machine on CI+critic |
| T2 | deps, config, CI | machine + second critic |
| T3 | schema, gates, governance | founder |

Bootstrap: `FT-MERGE-T0-T1` in trigger ledger — 5 cycles founder-reviewed, then machine per shadow-decision counter.

---

## Failure flow

```
failure → contain → critic → repair (fresh lane) → [2× fail] → research + audit
→ external validate → receipt → merge by tier → continue
→ founder ONLY: capital/legal ∨ irreversible-L5 ∨ phase unlock (with memo)
```

---

## Build order (status)

1. ✅ Worker loop + walls — local-lane, worker kernel
2. ✅ Critic + machine merge T0–T1 — `noos_machine_loops_v1.py critic|validate-merge` + gel-ci
3. ✅ Repair templates + reconciler — `repair-lane-v1.json` + `reconcile`
4. ✅ Research memos — `research-memo-v1.json` + `research-memo`
5. ✅ Outside audit + receipt chain — `audit` + `noos_receipt_chain_v1.py`
6. ✅ Trigger ledger + shadow decisions — `founder-trigger-ledger-v1.json` + `record-shadow`

---

## Commands

```bash
make machine-status          # autonomy + ledger digest
make machine-reconcile       # auto-dispatch from failure receipts
make machine-audit           # trailing-window outside audit
make machine-verify          # structural E2E check (gel-ci)
make machine-validate-merge  # T0–T3 merge gate
make machine-critic RECEIPT=receipts/proof/....json
make machine-research QUESTION="..." [RECEIPT=...]
```

Skill: `.cursor/skills/machine-loops/SKILL.md`  
Subagent: loop-specialist for T0/T3 automation; local-operator for T2 lanes.
