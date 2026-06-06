---
id: nf-future-0237
phase: phase-2-evidence-connectors
tier: T1
priority: P1
status: backlog
lane: lane_a
domain: sample
no_asf: true
generator: scripts/generate-future-plans.py
---

# Document sample for evidence connectors (T1, #0237)

**Phase:** phase-2-evidence-connectors — Evidence index, M365/Google connectors, intake  
**Tier:** T1 — High — next sprint candidate  
**Lane:** A (Copilot governance & evidence). Lane C (payments/custody) out of scope.

## Outcome

Document **sample** capabilities so Noetfield moves toward long-term Trust Ledger + Copilot readiness without waiting for external dispatch.

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
