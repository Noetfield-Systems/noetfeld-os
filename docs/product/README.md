# NOOS Motor v1

**Deterministic workflow execution with verifiable organic completion evidence,
recovery, and auditable outputs.**

The Motor runs a job through an explicit lifecycle and proves it happened with
**organic** completion evidence — a repair/replay/manual touch can never read as
live execution. Every output is content-hashed and bound to the run that made it.

## 60-second start

```bash
./bin/noos install     # stdlib-only; no network, no secrets
./bin/noos demo        # real input -> real output artifact + receipt
./bin/noos verify      # 3 local organic cycles + masking regression + failure path
./bin/noos package     # build the versioned release bundle + manifest
./bin/noos status <execution_id>   # retrieve output + provenance + integrity
```

The offline reference path runs today. The production cloud organic chain
(`cloud_trigger=http_loop` on Railway → Supabase) is `EXTERNAL_ACTIVATION_REQUIRED`
— it needs cloud credentials not present on a build host.

## What it fixes

The completion classifier keyed on receipt **age only**, so repair-labeled rows
kept a stalled loop reporting a false `RUNNING_CONFIRMED`. Classification is now
**provenance-aware**: `RUNNING_CONFIRMED` requires fresh **organic** evidence;
repair rows classify as `DEGRADED_REPAIR_SUSTAINED` and escalate instead of
masking the stall.

## Docs

| Doc | What |
|---|---|
| [Product definition](NOOS-MOTOR-V1.md) | promise, contracts, limitations, boundaries |
| [Architecture](NOOS-MOTOR-V1-ARCHITECTURE.md) | the full chain + lifecycle diagrams |
| [Quick start](NOOS-MOTOR-V1-QUICKSTART.md) | five-minute walk-through |
| [Runbook](NOOS-MOTOR-V1-RUNBOOK.md) | operate, health-check, migrate, roll back |
| [Receipt schema](NOOS-MOTOR-V1-RECEIPT-SCHEMA.md) | every provenance/lifecycle field |
| [Release notes](NOOS-MOTOR-V1-RELEASE-NOTES.md) | what shipped, what's external |
| [Troubleshooting](NOOS-MOTOR-V1-TROUBLESHOOTING.md) | symptom → cause → action |
| [Runway ledger](../runway/NOOS-MOTOR-V1-FULL-RUNWAY.md) | the full build record + evidence |

SUBMITTED for independent verification (author != subject).
canon_version: FOUNDER_CANON_v1+MACHINE_LOOPS_v1
