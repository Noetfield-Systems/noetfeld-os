---
id: nf-future-0879
phase: phase-8-staging-prod
tier: T3
priority: P3
status: done
lane: lane_a
domain: copilot
no_asf: true
nf_plan_id: NF-PLAN-0879
generator: scripts/generate-future-plans.py
---

# Harden copilot for staging prod (T3, #0879)

**Phase:** phase-8-staging-prod — Staging, Render/CF deploy, observability, SLOs  
**Tier:** T3 — Low — research / optional  
**Lane:** A (Copilot governance & evidence). Lane C (payments/custody) out of scope.

## Outcome

Harden **copilot** capabilities so Noetfield moves toward long-term Trust Ledger + Copilot readiness without waiting for external dispatch.

## Build (stub)

- Identify touchpoints under `governance-console/`, `scripts/`, `docs/spec/`, or `copilot/`.
- Add or extend API/UI/tests only in `~/Desktop/Noetfield`.
- Do not edit `SinaPromptOS` or Desktop `SourceA`.

## Verify

```bash
make dev-local
make verify-local-dev
pytest governance-console/backend/tests/ -q
```

## Agent closeout (no ASF)

1. Read `docs/ops/AGENT_READ_LINKS_LOCKED_v1.md` → `os/SHIP_NOW.md`.
2. Implement; run verify; update this plan `status: done` in front matter.
3. `reports/cursor-reply-latest.txt` + `ingest-cursor-reply.sh noetfield`.
4. `./scripts/sync-sourceA-desktop.sh`; commit on `cursor/bank-grade-fullstack-37f0`.

## Dependencies

- Prior phase items in same domain may be required.
- Locked positioning: `docs/strategy/NOETFIELD_TRUST_LEDGER_POSITIONING_LOCKED_v1.2.md`.
