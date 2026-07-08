<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260707-008
doc_type: INTEGRATOR_DAILY_CHECKLIST
workspace_root: noetfeld-OS
-->

# NOOS Integrator — Daily Mandatory Checklist v1

**Authority:** Live probes at run time. Disk receipts are snapshots only — never use yesterday's JSON as today's truth.

## One law

```
CF Workers cron = PRIMARY 24/7 motor
GHA Enterprise  = SECONDARY witness + artifacts
Railway         = Tertiary parallel cloud-loop lanes
NOOS            = Observe, coordinate, repair, receipt — never duplicate TrustField product edits
```

## Run (every day, start of integrator session)

```bash
cd noetfeld-OS
make local-boot                    # optional: vault + lane hygiene
make integrator-daily              # mandatory — live checklist + receipt
```

Exit `0` = all checks pass. Exit `1` = fix queue printed — execute fixes before claiming green.

Receipt: `receipts/proof/noos-integrator-daily-checklist-v1.json` (overwritten each run with fresh `at` timestamp).

---

## Checklist items (machine IDs)

| ID | Tier | What | Live source | Fix if fail |
|----|------|------|-------------|-------------|
| **ICL-D01** | T0 | Vault + CF deploy token | `integrator-status` surfaces | `make cloud-vault-promote && make cloud-secrets-sync` |
| **ICL-D02** | T0 | Integrator mirror + no agent conflicts | `noos_integrator_mirror_check_v1.py` | `make local-sweep-stale` |
| **ICL-D03** | T0 | NOOS CF autorun motor sustain | `verify_noos_motor_sustain_v1.py` | `make motor-sustain-verify && make integrator-repair-autorun` |
| **ICL-D04** | T0 | NOOS autorun workflows critique | `autorun_status_v1.py --json` | `make integrator-repair-autorun` |
| **ICL-D05** | T0 | Machine loops audit chain | `noos_machine_loops_v1.py audit` | `make machine-reconcile` |
| **ICL-D06** | T1 | TrustField 11 layers (no red) | `observe_trustfield_parallel_layers_v1.py` | Route red layer → TrustField worker |
| **ICL-D07** | T0 | Loop registry deadman motors | `observe_trustfield_loop_registry_v1.py` | `record_sg_registry_witness_v1.py` + CF fleet `/tick` |
| **ICL-D08** | T0 | CF fleet tick health | `GET tf-cf-fleet-tick-v1/health` | `cf_deploy_fleet_tick_worker.sh` |
| **ICL-D09** | T1 | Railway plan-worker lanes | `GET plan-worker/health` | `railway_deploy_plan_worker.sh` |
| **ICL-D10** | T1 | GHA no billing gate (<12s fails) | `gh run list` per repo | Enterprise spending limit >$0; `gh run rerun` |
| **ICL-D11** | T2 | GHA real CI failures | runs with duration ≥12s | `gh run view --log-failed` — fix tests/scripts |
| **ICL-D12** | T0 | Org on Enterprise plan | `gh api orgs/Noetfield-Systems` | Attach org to `noetfield-systems-inc` enterprise |

---

## Distinguish billing vs real CI failure

| Signal | Billing gate | Real CI failure |
|--------|--------------|-----------------|
| Job duration | **<12 seconds** | **≥12 seconds** |
| Annotation | "payments failed / spending limit" | Step logs show test/script errors |
| Minutes used | ~0–10 (job never ran) | Normal runner time |
| Fix | Enterprise/org Billing → spending limit | Fix code; rerun workflow |

Org plan must be `enterprise`. July 2026 usage was **~5 minutes** — not minute exhaustion.

---

## Control panel surfaces (do not guess)

| Surface | Command | Closure token |
|---------|---------|---------------|
| Integrator unified | `make integrator-status` | `ok: true` all surfaces |
| Daily mandatory | `make integrator-daily` | `NOOS_INTEGRATOR_DAILY: green` |
| TrustField layers | `make observe-trustfield-layers` | `NOOS_TF_11_LAYERS: green` |
| TrustField registry | `make observe-trustfield-registry` | `NOOS_TF_LOOP_REGISTRY_OBSERVE: green` |
| NOOS autorun | `make autorun-status` | critique `overall_ok: true` |
| Machine loops | `make machine-status` | no FAILED_WITH_RECEIPT |

---

## Daily fix order (when red)

1. **ICL-D01–D05** — NOOS control plane (`integrator-repair-autorun`, motor sustain)
2. **ICL-D07–D08** — CF primary motors (fleet tick, registry witness)
3. **ICL-D09** — Railway lanes (redeploy plan-worker if lane false)
4. **ICL-D10–D12** — GHA billing vs CI (founder billing first, then worker CI fixes)
5. **ICL-D06** — TrustField layer red → enqueue TrustField worker handoff (no direct product edits from NOOS chat)

---

## Forbidden

- Closing the day from stale `receipts/proof/*` without re-running `make integrator-daily`
- Treating chat memory as live state
- Editing TrustField product/www from NOOS integrator lane (observe + handoff only)
- Re-running GHA marathons when CF primary already green (L-P4 delegate)

---

## Cron / automation hook (optional)

Schedule on Mac T2 or GHA secondary witness after billing green:

```bash
0 7,13,19 * * * cd /path/to/noetfeld-OS && make integrator-daily WRITE_RECEIPT=1
```

Add `WRITE_RECEIPT=1` to Makefile target if wired; default `--write-receipt` on `integrator-daily`.
