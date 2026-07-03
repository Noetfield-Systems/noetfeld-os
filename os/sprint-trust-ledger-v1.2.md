# Sprint — Trust Ledger v1.2 (active)

**Status:** ship_now · **Plan:** [plan.json](./plan.json) · **Backlog:** [docs/spec/SPRINT_BACKLOG_WEEKS_0-8.md](../docs/spec/SPRINT_BACKLOG_WEEKS_0-8.md)

## Locked positioning

- Headline: AI Governance & Evidence for Copilot adoption
- Buyer line: audit trail Copilot deployments will be asked for later
- Mandate: ≥1 signed **TLE v1** per engagement
- Blueprint: [docs/spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md](../docs/spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md)

## Current sprint step (P0)

**Merge + verify** (`ship-p0-merge-001`):

1. Merge [PR #15](https://github.com/Noetfield-Systems/Noetfield/pull/15) to `main`
2. `make ship-verify` exit 0
3. Evidence: `scripts/verify-local-dev.sh`, `scripts/tle-smoke.sh`, `docs/ops/lane_a_sprint_map.md`

## P1 agent-complete (no ASF)

- Evidence + TLE lifecycle + **connectors** + **list** + **2-step approve** + **PDF export**
- Migrations: `0006_trust_ledger_tle.sql`, `0007_trust_ledger_connectors.sql`
- CI: `.github/workflows/trust-ledger-ci.yml`
- Verify: `./scripts/tle-smoke.sh` · `./scripts/tle-smoke.sh --api` · `pytest tests/unit/test_trust_ledger_v1.py`

## ASF-only (not agent)

- Production WAVE0 smoke — [docs/WAVE0_SHIP_CHECKLIST.md](../docs/WAVE0_SHIP_CHECKLIST.md)
- Live pilot W78-3

## Next (optional agent)

Workspace UI polish, confidence score UI, connector live sync — [docs/spec/openapi/trust-ledger-v0.yaml](../docs/spec/openapi/trust-ledger-v0.yaml).
