# Future work tracker (`todolist/`)

**Agent default for this chat: TrustField Technologies only.**  
Do **not** treat items below as TrustField work unless the user explicitly re-scopes.

## Project boundary

| | TrustField (this chat) | Noetfield (separate) | VIRLUX (separate) |
|--|------------------------|----------------------|-------------------|
| **Scope** | Corporate / execution / partnerships | Governance product + www + platform | B2B FX / payments |
| **Implement in this thread?** | Yes (when user asks) | **No** — use Noetfield-scoped chat/repo | **No** — VIRLUX repo |
| **Tracker IDs** | `TF-*` (add when needed) | `NF-*` | `VL-*` in [external/virlux/](./external/virlux/) |

Full rules: [../PROJECTS.md](../PROJECTS.md), [external/README.md](./external/README.md)

## Noetfield files (not TrustField chat scope)

These files track **Noetfield only** — do not execute them in a TrustField-scoped conversation:

| File | Scope |
|------|--------|
| [NEXT_MOVES.md](./NEXT_MOVES.md) | Noetfield P0/P1/P2 |
| [noetfield-platform.md](./noetfield-platform.md) | API, chat, Telegram, intake |
| [noetfield-public-site.md](./noetfield-public-site.md) | www, GTM, legal |

## External (not TrustField, not Noetfield implementation here)

| File | Scope |
|------|--------|
| [external/virlux/](./external/virlux/) | VIRLUX backlog — separate codebase |

## How to add items

1. **TrustField** → new `trustfield-*.md` or user-directed task (this chat)
2. **Noetfield** → only when user re-scopes; use `noetfield-*.md`
3. **VIRLUX** → [external/virlux/](./external/virlux/) only

Template: [_template.md](./_template.md)
