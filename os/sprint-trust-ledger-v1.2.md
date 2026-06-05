# Sprint — Trust Ledger v1.2 (active)

**Status:** ship_now · **Plan:** [plan.json](./plan.json) · **Backlog:** [docs/spec/SPRINT_BACKLOG_WEEKS_0-8.md](../docs/spec/SPRINT_BACKLOG_WEEKS_0-8.md)

## Locked positioning

- Headline: AI Governance & Evidence for Copilot adoption
- Buyer line: audit trail Copilot deployments will be asked for later
- Mandate: ≥1 signed **TLE v1** per engagement
- Blueprint: [docs/spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md](../docs/spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md)

## Current sprint step (P0)

**Merge + verify** (`ship-p0-merge-001`):

1. Merge [PR #15](https://github.com/kazemnezhadsina144-dot/Noetfield/pull/15) to `main`
2. `make ship-verify` exit 0
3. Evidence: `scripts/verify-local-dev.sh`, `scripts/tle-smoke.sh`, `docs/ops/lane_a_sprint_map.md`

## Next (P1)

Implement paths in [docs/spec/openapi/trust-ledger-v0.yaml](../docs/spec/openapi/trust-ledger-v0.yaml) — task `ship-p1-ledger-003`.
