---
id: nf-future-0618
phase: phase-6-compliance-scale
tier: T0
priority: P0
status: backlog
lane: lane_a
domain: rag
no_asf: true
generator: scripts/generate-future-plans.py
---

# Ship rag for compliance scale (T0, #0618)

**Phase:** phase-6-compliance-scale — Controls catalog, risk registers, compliance dashboard  
**Tier:** T0 — Critical — blocks ship or pilot  
**Lane:** A (Copilot governance & evidence). Lane C (payments/custody) out of scope.

## Outcome

Ship **rag** capabilities so Noetfield moves toward long-term Trust Ledger + Copilot readiness without waiting for external dispatch.

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
