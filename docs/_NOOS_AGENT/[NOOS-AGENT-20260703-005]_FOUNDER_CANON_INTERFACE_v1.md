# [NOOS-AGENT-20260703-005] Founder Canon Interface v1

<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260703-005
doc_type: FOUNDER_CANON_INTERFACE
workspace_root: /Users/sinakazemnezhad/Projects/noetfeld-os
classification: INTERNAL — process law interface (NOOS binding)
related_registry: data/founder-trigger-ledger-v1.json
-->

**Version:** v1.1 · **Status:** ACTIVE (NOOS implementation binding)  
**Upstream canon:** Desktop `FOUNDER_CANON (1).md` — full text authority until committed to `sina-governance-SSOT`  
**NOOS implementation:** `data/noos-machine-loops-config-v1.json` · `scripts/noos_machine_loops_v1.py`

---

## 1. Goal

Reduce founder manual work toward **zero-founder operational validation**. Machines validate; founder is not QA, runtime, or escalation inbox.

## 2. North star

Sandbox-first autonomy · walls at boundary · machine validation · self-growth · self-healing · adversarial critique · outside audit · deterministic autorun earned step by step.

## 3. Intent filter (every new rule)

1. Reduces founder workload — or makes founder the runtime?
2. Replaces founder judgment with machine validation?
3. Boundary wall vs permission loop?
4. On failure, routes to repair/critique/audit/research — or back to founder?
5. Target vs frozen blocker?

Fail any → redesign or drop.

## 4. Authority

Goals grant zero execution authority. Authority flows: **canon → work order → dispatch**. Missing authority → `BLOCKED_WITH_REASON` into machine loop, never improvisation.

## 5. Operating model

**Autonomy inside sandbox. Hard walls at boundary. Receipt at exit.**

Dispatch line for all NOOS templates:

```text
LAWS: FOUNDER_CANON v1 + governed-autorun v3. Violations = BLOCKED_WITH_REASON.
```

Receipts carry `canon_version: FOUNDER_CANON_v1+MACHINE_LOOPS_v1`.

## 6. Failure routes to machines

`detect → contain → critique → audit → research → repair → validate → receipt → continue`

Escalation: critic, external verifier, outside audit — **not** founder by default.

## 7. Validation is earned autonomy

Ladder: manual dispatch → gates → sandbox cycles → machine receipts → external verify → critic → clean windows → limited autonomy → autorun. Unlock on receipts only.

## 8. Founder touchpoints (bootstrap exceptions)

Until earned away:

1. **Capital / legal** — spend, contracts, regulated actions
2. **Irreversible L5** — weakening verifiers, gates, laws, schemas
3. **Phase unlock** — new autonomy tier (one-click with evidence trail)

Ledger: `data/founder-trigger-ledger-v1.json` — every touchpoint has `retirement_condition` + `evidence_counter`.

## 9. Truth & memory

Live SSOT → repo state → dispatch → receipt → chat. Hidden state is a wall violation. Fresh context per loop actor (R1).

## 10. Violation law

Contain → receipt → critique → repair. Escalate to founder only per §8. Never hide or rewrite history.

---

**NOOS commands:** `make machine-status` · `make machine-reconcile` · `make machine-audit` · `make machine-verify`

**Related:** [MACHINE_LOOPS v1]([NOOS-AGENT-20260703-006]_MACHINE_LOOPS_v1.md) · [governed-autorun skill](../../.cursor/skills/governed-autorun/SKILL.md)
