# Locked reference index (Noetfield)

**Purpose:** Single index of committed LOCKED docs agents must not override without ASF.

| Layer | Document | Path |
|-------|----------|------|
| Agent team sync (cloud bridge) | Agent team sync LOCKED v1 | [docs/ops/NOETFIELD_AGENT_TEAM_SYNC_LOCKED_v1.md](../docs/ops/NOETFIELD_AGENT_TEAM_SYNC_LOCKED_v1.md) |
| Agent context | Read order LOCKED v1 | [docs/ops/NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md](../docs/ops/NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md) |
| Agent links | Read links LOCKED v1 | [docs/ops/AGENT_READ_LINKS_LOCKED_v1.md](../docs/ops/AGENT_READ_LINKS_LOCKED_v1.md) |
| Ship plan | plan.json | [os/plan.json](./plan.json) |
| Ship now | SHIP_NOW | [os/SHIP_NOW.md](./SHIP_NOW.md) |
| Product truth | PRODUCT_TRUTH | [PRODUCT_TRUTH.md](../PRODUCT_TRUTH.md) |
| Offerings | OFFERINGS_LOCKED | [OFFERINGS_LOCKED.md](../OFFERINGS_LOCKED.md) |
| Boundaries | PROJECT_BOUNDARIES_LOCKED | [PROJECT_BOUNDARIES_LOCKED.md](../PROJECT_BOUNDARIES_LOCKED.md) |
| TLE blueprint | Trust Ledger LOCKED v1.2 | [docs/spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md](../docs/spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md) |
| Drift sources | Governance drift LOCKED v1 | [docs/references/GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md](../docs/references/GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md) |
| Sources handbook | Governance handbook LOCKED v1 | [docs/references/GOVERNANCE_SOURCES_HANDBOOK_LOCKED_v1.md](../docs/references/GOVERNANCE_SOURCES_HANDBOOK_LOCKED_v1.md) |
| Agent reply truth | Execution truth LOCKED | [docs/spec/EXECUTION_TRUTH_AGENT_REPLY_LOCKED.md](../docs/spec/EXECUTION_TRUTH_AGENT_REPLY_LOCKED.md) |
| PLAN WITH NO ASF | QUICK_PICK | [docs/ops/plans/no-asf/QUICK_PICK.md](../docs/ops/plans/no-asf/QUICK_PICK.md) |

**Private (gitignored):** `ops/private/agent-reference/` — full NKUE/UKE, locked plans, team state. See team sync doc § Private paths.

**Verify gate:** `make ship-verify`

| v1 | 2026-06-06 |
