# NOOS Factory Autorun Deprecation Path (UPG-0207)

**Status:** Documented deprecation path (loop fleet covers factory scope)  
**Date:** 2026-07-05  
**Authority:** NOOS machine loops upgrade lane step 10

## Current motors

| Motor | Role | Status |
|-------|------|--------|
| `noos-loop-fleet-tick-v1` (CF) | Primary — repository_dispatch every 5m | Active |
| GitHub `schedule` cron | ~~Backup trigger on each loop workflow~~ | **Removed 2026-07-05** (duplicate spend) |
| `noos-factory-autorun-tick-v1` | Legacy monolith factory autorun | Deprecation candidate |
| Fly `noos-inbox-runner` | Secondary always-on inbox drain (UPG-0201) | Scaffolded |
| Fly `noos-self-heal-runner` | Sub-minute self-heal (UPG-0206) | Scaffolded |

## Deprecation criteria (UPG-0207)

Retire `noos-factory-autorun` monolith when **all** are true:

1. `LOOP-VERIFY-ALL` — 7/7 core domain loops VERIFIED (or documented STALE_ALLOWED for SourceA observe)
2. CF fleet motor health URL returns 200
3. Fly inbox runner `/health` and `/ready` pass external probe
4. Fly self-heal runner reaction interval ≤ 60s with heartbeat receipts
5. No production dependency on `noetfield-factory-v1-*` factory_id sinks for loop cycles

## Motor restart (Phase C — UPG-LS-04/05)

When CF loop motor or Railway loop-runner `/health` fails, deadman triggers machine-safe restart recipes:

- Registry: `data/noos-motor-restart-recipes-v1.json`
- Executor: `scripts/noos_motor_restart_v1.py` · Railway `POST /motor-restart`
- Runbook: `docs/ops/NOOS_MOTOR_RESTART_RECIPES_v1.md`
- Drill receipt: `receipts/proof/noos-motor-restart-drill-v1.json`

## Action (not yet executed)

- Do **not** delete `.github/workflows/noos-factory-autorun.yml` until Fly secondary motors are deployed and verified live.
- Mark workflow `workflow_dispatch: false` only after founder/machine merge gate approves retirement receipt.

## Evidence

- Baseline: `receipts/proof/noos-loop-baseline-audit-v1.json`
- Registry reconcile: `receipts/proof/noos-loop-registry-reconcile-v1.json`
- Loop verify: `receipts/proof/noos-loop-verify-all-v1.json`
- Closeout: `receipts/proof/noos-machine-loops-upgrade-closeout-v1.json`
