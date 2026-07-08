# NOOS Motor Restart Recipes v1

Machine-safe motor restart recipes for Phase C of the Living System 99-Plan.

## Registry

- `data/noos-motor-restart-recipes-v1.json` — recipe definitions
- `scripts/noos_motor_restart_v1.py` — executor (fail-closed on `founder_gated`)

## Machine-safe motors

| Recipe id | Motor | Gate |
|-----------|-------|------|
| `cf-loop-motor` | CF `noos-loop-fleet-tick-v1` | machine_safe |
| `cf-deadman` | CF `noos-deadman-v1` | machine_safe |
| `railway-loop-runner` | Railway `noos-loop-runner` | machine_safe |
| `fly-inbox-motor` | Fly inbox | founder_gated |

## Operator commands

```bash
make motor-status
python3 scripts/noos_motor_restart_v1.py --recipe cf-loop-motor --dry-run
make motor-restart RECIPE=cf-loop-motor
```

## Deadman wiring

When loop runner `/health` fails, deadman POSTs to Railway `/motor-restart` with `recipe_id=railway-loop-runner` (capped by `restart_attempts_max`).

Receipts land under `receipts/proof/noos-motor-restart-<recipe>-<UTC>.json`.
