# External projects (not this repository)

**Do not implement VIRLUX work in the Noetfield repo.**  
These files are **founder notes only** — kept here so ideas from chat are not lost.

| Project | What it is | Where code lives | Tracker |
|---------|------------|------------------|---------|
| **VIRLUX** | Canadian B2B FX / payments fintech | **Separate repo** (e.g. local `Virlux` project) | [virlux/](./virlux/) |
| **Noetfield** | Governance execution infrastructure (this repo) | `kazemnezhadsina144-dot/Noetfield` | [../noetfield-platform.md](../noetfield-platform.md) |

## Rules for agents and humans

1. **Noetfield PRs/commits** — only `NF-*` items and paths under this monolith.
2. **VIRLUX** — track under `todolist/external/virlux/`; implement in the **VIRLUX repository**.
3. **TrustField** — strategic docs only; not a deploy target in either product UI unless explicitly scoped.
4. Never copy VIRLUX env vars, Interac, Circle, or payment flows into Noetfield platform code.

When starting work, ask: *“Is this Noetfield or VIRLUX?”* If VIRLUX, stop and switch repos.
