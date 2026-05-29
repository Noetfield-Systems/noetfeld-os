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
3. **TrustField Technologies** — **default scope for this Cursor chat**; corporate/execution work. Not the same as shipping Noetfield product code unless the user explicitly re-scopes.
4. **Noetfield** — separate product; do not implement in a TrustField-scoped chat.
5. Never copy VIRLUX env vars, Interac, Circle, or payment flows into TrustField or Noetfield code from the wrong repo.

When starting work, ask: *“Is this TrustField, Noetfield, or VIRLUX?”* Use the matching chat/repo.
