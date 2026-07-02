---
name: governed-autorun
description: Design, run, audit, and repair 24/7 multi-workflow autonomous execution systems — parallel sandboxes, cron loops, queue motors, receipt-backed cycles, ROI-governed spend, deterministic loops, and self-improving pipelines under one reconciler. Use when building or fixing autorun loops, cron workers, batch queues, multi-sandbox orchestration, cycle receipts, sink invariants, verification gates, cost/ROI attribution, deterministic loop design (L13/D1-D8), or auditing agent reports.
---

# Governed Autorun v3 (repo copy)

**Canonical laws:** `docs/GOVERNED_AUTORUN_LAWS_v3.md`  
**References:** `docs/governed-autorun/references/`

Adopted from governed-autorun skill v3 (2026-07-02). NOOS loop specialist: `.cursor/agents/noetfield-os-loop-specialist.md`.

## Quick law index

L1 ONE reconciler · L2 IDLE_NO_WORK healthy · L3 reason on every gate · L4 external verify · L5 verifier freeze · L6 commit before deploy · L7 founder_blocked · L8 sink ack · L9 fail-closed refill · L10 shared sink reads · L11 cost/ROI · L12 drift · **L13 deterministic loops (D1–D8)**

## NOOS-specific overlays

- Proof receipts: `receipts/proof/` (not `.noos-runtime/`)
- Schedule proof: Supabase `noetfield_truth_log` via `make schedule-verify`
- Loop fleet: `data/noos-24-7-loops-v1.json` + CF `repository_dispatch`

Read `docs/GOVERNED_AUTORUN_LAWS_v3.md` for full text.
