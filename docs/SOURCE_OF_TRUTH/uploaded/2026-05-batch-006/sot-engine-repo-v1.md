# SoT Engine Repository v1.0

Document key: `sot-engine-repo-v1`

## Stack

FastAPI (`app/`), `sot_miner/` (pattern detection, extractor, validator, scheduler), Supabase (`execution_logs`, `sot_rules`), Telegram integration.

## Core loop

Log execution → detect frequency ≥3 → extract rules → validate → policy inject.

## Registry

Implementation scaffold; superseded as normative architecture by `sot-engine-auto-running-architecture-v1`.
