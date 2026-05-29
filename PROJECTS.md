# Projects — do not mix

| Project | Repository | This folder? |
|---------|------------|--------------|
| **Noetfield** | `Noetfield` (you are here) | Yes — all code, CI, deploy |
| **VIRLUX** | **Separate** VIRLUX repo | **No** — not built or deployed from here |

## Noetfield

- Governance execution infrastructure for regulated organizations.
- `www.noetfield.com` + `platform.noetfield.com`
- Work tracker: [`todolist/NEXT_MOVES.md`](todolist/NEXT_MOVES.md)

## VIRLUX

- **Different product:** Canadian B2B FX / payments (Interac, Circle, dashboard, etc.).
- **Do not** add VIRLUX features, env vars, or payment logic to this repository.
- **Do not** deploy Noetfield changes to VIRLUX hosts (or vice versa).
- If you need VIRLUX backlog notes stored here for convenience only: [`todolist/external/virlux/`](todolist/external/virlux/) — implement in the VIRLUX codebase.

When in doubt: **Noetfield = this repo. VIRLUX = other repo.**
