# SKILL-003 — Session end report

**When:** Before ending a work session or after completing a user task.

## Steps

1. Copy [.cursor/reports/SESSION_REPORT_TEMPLATE.md](../reports/SESSION_REPORT_TEMPLATE.md) → `.cursor/reports/YYYY-MM-DD-<slug>.md` (optional, for multi-step sessions).
2. Fill all required fields.
3. List `verify_commands_run` with exit codes.
4. If new mistake pattern → bump [.cursor/agent-memory/MEMORY_LOCKED.yaml](../agent-memory/MEMORY_LOCKED.yaml) `version` + add `lessons` entry.
5. Optional YAML footer for Prompt OS ingest — [EXECUTION_TRUTH_AGENT_REPLY_LOCKED.md](../../docs/spec/EXECUTION_TRUTH_AGENT_REPLY_LOCKED.md).

## Minimum reply to user

Include:

- What shipped (Noetfield only)
- `scope_confirmed: noetfield_only`
- Verify commands run
- Open incidents (if any)

## Never include in public summary

- Contents of `docs/internal/` or `ops/private/`
- TrustField implementation offers
