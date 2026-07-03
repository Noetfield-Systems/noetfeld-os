# Copilot instructions — Noetfield-Systems/noetfeld-os

## Repo identity

- Treat `Noetfield-Systems/noetfeld-os` as the canonical active repo slug.
- Treat `kazemnezhadsina144[-]dot` as a **forbidden active-config marker**.
- If the pre-migration personal slug (see `noetfield-org/FORBIDDEN_MARKERS.txt`) appears in active config, migrate it or flag it explicitly.
- Historical docs and locked receipts may preserve legacy values when they are archaeology rather than active config.

## Parallel agent law (read before any edit)

Living-system governance: `docs/_NOOS_AGENT/[NOOS-AGENT-20260703-003]_PARALLEL_AGENT_GOVERNANCE_v1.md`

Registry: `data/noos-parallel-agent-registry-v1.json`

| Tier | Who | Rule |
|------|-----|------|
| T0 | GitHub Actions, CF cron, worker kernel | Deterministic machine execution only |
| T1 | **You (Copilot coding agent)** | Kaizen patches inside fenced paths |
| T2 | Cursor chat / Copilot CLI | Must integrator-claim before shared paths |
| T3 | Cursor Automations, integrator | Read/narrate; delegate machine proof to GHA |

### L-P5 — integrator claim (T1/T2)

Before editing shared scope files, the human operator or local agent runs:

```bash
python3 scripts/noos_integrator_sync_v1.py claim --agent-id <id> --task-id <id> --scope-file <path>
```

Use `data/noos-integrator-role-v1.json` only as coordination support; do not create a second coordination doctrine.

### L-P7 — Copilot fences (you)

- **Allowed:** `scripts/` (except `scripts/verify_*`), `docs/_NOOS_AGENT/`, `tests/`, `config/` — machine_safe Kaizen only.
- **Forbidden:** `scripts/verify_*`, `noetfield_gate/`, `docs/GOVERNED_AUTORUN_LAWS_v3.md`, trigger/mission/parallel registries, CODEOWNERS-fenced verifier paths.
- Open PRs only; never merge. `gel-ci` + scoped tests must pass.
- Use issue template: `.github/ISSUE_TEMPLATE/copilot-kaizen-machine-safe.yml` with `op_key` + `mission_id`.

### Conflict check (boot)

```bash
python3 scripts/noos_agent_conflict_check_v1.py --json
python3 scripts/verify_living_system_governance_v1.py --json
```

Do not duplicate work owned by GHA loops, self-heal pipeline stages, or Cursor Automations listed in the parallel registry.

## GHA + integrator coordination

- GHA owns schedules, deploy chains, loop fleet, and self-heal pipeline (audit → heal → research → specialist → orchestrator).
- Integrator arbitration: one writer to `.noos-runtime/integrator/`; hourly sync audit is **read-only**.
- Worker kernel (`scripts/noos_worker_kernel_v1.py`) routes one-shot T0 tasks; it does not replace GHA or automations.
