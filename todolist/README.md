# Future work tracker (`todolist/`)

**This folder tracks work for the Noetfield repository.**  
VIRLUX is a **different product** — see [external/virlux/](./external/virlux/) (notes only; code is elsewhere).

## Project boundary

| | Noetfield (this repo) | VIRLUX (separate) |
|--|----------------------|-------------------|
| **Product** | Governance execution infrastructure | B2B FX / payments |
| **Domains** | `www.noetfield.com`, `platform.noetfield.com` | VIRLUX app hosts (not here) |
| **IDs** | `NF-*` | `VL-*` in external tracker |
| **Implement here?** | Yes | **No** |

Full rules: [external/README.md](./external/README.md)

## How to add items

1. **Noetfield** → `noetfield-*.md` or [NEXT_MOVES.md](./NEXT_MOVES.md)
2. **VIRLUX** → [external/virlux/](./external/virlux/) only (do not add VIRLUX tasks to Noetfield code)
3. Use **ID**, **Status**, **Owner**, **Type** — see [_template.md](./_template.md)

## Files (Noetfield — start here)

| File | Scope |
|------|--------|
| **[NEXT_MOVES.md](./NEXT_MOVES.md)** | Prioritized P0/P1/P2 for **Noetfield only** |
| [noetfield-platform.md](./noetfield-platform.md) | API, chat, Telegram, intake, deploy |
| [noetfield-public-site.md](./noetfield-public-site.md) | www, GTM, legal, SEO |
| [archive/](./archive/) | Completed items |

## External (not this repo)

| File | Scope |
|------|--------|
| [external/virlux/](./external/virlux/) | VIRLUX backlog — **separate codebase** |

## Quick index (Noetfield launch blockers)

- Platform deploy, secrets, DNS, Telegram, LLM — [noetfield-platform.md](./noetfield-platform.md)
- www deploy, legal pages — [noetfield-public-site.md](./noetfield-public-site.md)

VIRLUX blockers are listed only under [external/virlux/fintech.md](./external/virlux/fintech.md).
