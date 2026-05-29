# External projects (not Noetfield)

**Do not implement TrustField or VIRLUX work in the Noetfield repo or Noetfield-scoped chat.**

These folders are **founder reference notes** until each entity has its own repository.

| Project | What it is | Tracker | Noetfield repo? |
|---------|------------|---------|-----------------|
| **Noetfield** | Governance execution infrastructure | [../NEXT_MOVES.md](../NEXT_MOVES.md) | **Yes — this repo** |
| **TrustField Technologies** | Corporate execution, partnerships, Trust Brief ops | [trustfield-technologies/](./trustfield-technologies/) | **No** |
| **VIRLUX** | Canadian B2B FX / payments | [virlux/](./virlux/) | **No** |

## Rules for agents and humans

1. **Noetfield PRs/commits** — only `NF-*` and Noetfield product paths.
2. **TrustField** — [trustfield-technologies/](./trustfield-technologies/) only; use a **TrustField-scoped** chat/repo to implement.
3. **VIRLUX** — [virlux/](./virlux/) only; implement in the **VIRLUX repository**.
4. Never copy payment rails, MSB claims, or TrustField corporate strategy into Noetfield `services/` or www.
5. Historical SSOT mentioning multiple entities (`docs/SOURCE_OF_TRUTH/`) is context only — [STRATEGIC_LOCK.md](../../STRATEGIC_LOCK.md) wins for Noetfield product.

When starting work, ask: *“Is this Noetfield, TrustField, or VIRLUX?”* Only **Noetfield** belongs here.

**Noetfield future path:** [../../docs/strategy/noetfield-future-path.md](../../docs/strategy/noetfield-future-path.md)
