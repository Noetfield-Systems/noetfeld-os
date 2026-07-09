# [NOOS-AGENT-20260703-002] Cheap Worker Kernel v1

<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260703-002
doc_type: WORKER_KERNEL
workspace_root: /Users/sinakazemnezhad/Desktop/Noetfield-Systems/noetfeld-OS
classification: INTERNAL — headless governed worker kernel (not IDE/UI)
-->

**Status:** DECLARED · 2026-07-03  
**Scope:** Headless task router under `config/model-router.yml` — deterministic tools + tiered model proposals  
**Not:** IDE, UI, Copilot API, background loops, direct `main` edits, product code mutation

---

## Purpose

Route governed tasks to:

| Tier | Use | Spend |
|------|-----|-------|
| **T0** | grep, check, validate — local shell | $0 |
| **T1** | summarize, classify — free/cheap models | ≤ $0.01/run |
| **T2** | bounded patch **proposals** — sandbox only | ≤ $0.03/run |
| **T3** | premium exception — **founder approval required** | ≤ $0.05/run |

Deterministic checks decide pass/fail (L3/L5). Every run writes a receipt (L6 proof tier).

---

## Entrypoints

```bash
python3 scripts/noos_worker_kernel_v1.py --task-kind grep --payload '{"pattern":"kernel","path":"scripts"}' --json
python3 scripts/noos_worker_kernel_v1.py --task-kind patch_proposal --payload-file proposal.json --json
python3 scripts/noos_worker_kernel_v1.py --task-kind premium_analysis --founder-approval-token FOUNDER_APPROVED_T3 --json
pytest -q tests/test_noos_worker_kernel_v1.py
```

---

## Artifacts

| Path | Role |
|------|------|
| `config/model-router.yml` | Tier routing, budget, redaction, governance |
| `data/noos-worker-kernel-role-v1.json` | Role contract |
| `scripts/noos_worker_kernel_v1.py` | Orchestrator |
| `scripts/noos_model_router_v1.py` | T0–T3 routing + budget |
| `scripts/noos_patch_sandbox_v1.py` | Bounded patch sandbox |
| `scripts/noos_receipt_writer_v1.py` | Receipt emission |
| `receipts/proof/noos-worker-kernel-*.json` | Proof receipts |

---

## Governance law

- No secrets sent to model (`secret_redaction` in router config)
- Patches materialize under `.noos-runtime/worker-kernel/patches/` only
- Forbidden: `noetfield_gate/`, `scripts/verify_*`, laws docs, CODEOWNERS
- T3 blocked without `FOUNDER_APPROVED_T3` token
- `max_usd_per_run` enforced — exceed → `BLOCKED_WITH_REASON`

---

## v1 limits

- T1–T3 network LLM calls are **stubbed** — kernel records routing intent + cost estimate; wire OpenRouter/DeepSeek in a founder-gated follow-up
- No background loops — one shot per invocation
- Mission default: **M4** (kaizen / hygiene)
