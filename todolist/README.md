# Future work tracker (`todolist/`)

Use this folder to capture **every** suggestion, launch blocker, and “do later” item so nothing lives only in chat.

## How to add items

1. Pick the right file (or create `todolist/<topic>.md`).
2. Add one row to the table (or one checklist item) with:
   - **ID** — short slug, e.g. `NF-TELEGRAM-01`
   - **Status** — `blocked` | `todo` | `in_progress` | `done` | `wontfix`
   - **Owner** — `founder` | `engineering` | `legal` | `ops`
   - **Type** — `launch_blocker` | `code` | `ops` | `legal` | `nice_to_have`
3. Link to code/docs when relevant.
4. When done, set status to `done` and add **Completed** date in Notes.

## Files

| File | Scope |
|------|--------|
| [noetfield-platform.md](./noetfield-platform.md) | This repo — API, chat, Telegram, intake, deploy |
| [noetfield-public-site.md](./noetfield-public-site.md) | www, GTM, legal pages, SEO |
| [virlux-fintech.md](./virlux-fintech.md) | VIRLUX / payments product (separate codebase — founder backlog) |
| [virlux-ui-dev.md](./virlux-ui-dev.md) | VIRLUX marketing + dashboard UI, local dev |
| [archive/](./archive/) | Completed or cancelled items moved here quarterly |

## Status legend

- **launch_blocker** — Not a small bug; product cannot safely go live without it (founder, legal, or bank partner).
- **todo** — Planned engineering or ops work in repo.
- **blocked** — Waiting on external input (DNS, MSB registration, bank webhook, etc.).

## Quick index (open launch blockers)

See each file’s **Launch blockers** section. Update this line when closing items:

- Noetfield: production deploy + Telegram token + platform DNS — [noetfield-platform.md](./noetfield-platform.md)
- VIRLUX: Interac confirmation, KYC admin UI, httpOnly auth, legal, Circle prod — [virlux-fintech.md](./virlux-fintech.md)
