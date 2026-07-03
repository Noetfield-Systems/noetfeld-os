# Routing Matrix

Status: active
Plane: L17 org sync

## L17 route map

| Surface | Tier | Route role | Allowed actions | Notes |
|---|---|---|---|---|
| GitHub Actions | T0 | execute | CI, schedules, deterministic loop dispatch, verification | machine-only route |
| Copilot | T1 | implement | repo-local coding, tests, PR preparation | branch-scoped |
| Cursor local | T2 | local operator | local repo edits, inspections, operational glue | `make local-lane`, `make local-status`, `make local-closeout` |
| Codex | T3 reasoning | reason | plan, audit, architecture, synthesis, coordination support | reasoning route only |
| Cloud integrator | T3 merge | merge | arbitration, sync-plane summaries, merge-oriented coordination | merge route only |

## Routing law

- T0 executes.
- T1 implements.
- T2 operates locally.
- T3 reasoning plans and audits.
- T3 merge coordinates cross-repo sync.

The integrator protocol supports this matrix; it does not replace it.
