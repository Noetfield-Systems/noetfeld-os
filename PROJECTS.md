# Projects — locked boundaries

**Status:** Locked · **This repository and Cursor chat = Noetfield only.**

| Project | What it is | This repo / chat? |
|---------|------------|-------------------|
| **Noetfield** | Governance execution infrastructure · `www.noetfield.com` · `platform.noetfield.com` | **Yes — build, deploy, and track here** |
| **TrustField Technologies** | Separate parent / execution / corporate entity | **No** — reference only: [todolist/external/trustfield-technologies/](todolist/external/trustfield-technologies/) |
| **VIRLUX** | Separate Canadian B2B FX / payments product | **No** — reference only: [todolist/external/virlux/](todolist/external/virlux/) |

**Rule:** *Noetfield = this repo and this chat. TrustField and VIRLUX = other scopes — do not implement in Noetfield PRs.*

See also: [PROJECT_BOUNDARIES_LOCKED.md](PROJECT_BOUNDARIES_LOCKED.md)

---

## Noetfield (this repo)

- Pre-execution governance: policy, compliance logic, audit traces — **no custody, no payments** ([STRATEGIC_LOCK.md](STRATEGIC_LOCK.md)).
- **Future path:** [docs/strategy/noetfield-future-path.md](docs/strategy/noetfield-future-path.md)
- **Work tracker:** [todolist/NEXT_MOVES.md](todolist/NEXT_MOVES.md) · [todolist/noetfield-platform.md](todolist/noetfield-platform.md) · [todolist/noetfield-public-site.md](todolist/noetfield-public-site.md)

---

## TrustField Technologies (external — do not mix)

- Corporate strategy, Trust Brief delivery ops, RPAA/MSB, E-23 **vendor** packs for TrustField engagements.
- **Do not** add `TF-*` tasks to Noetfield code paths or Noetfield-focused chats.
- Notes live under [todolist/external/trustfield-technologies/](todolist/external/trustfield-technologies/) until a dedicated TrustField repo exists.

Historical SSOT mentioning both entities: `docs/SOURCE_OF_TRUTH/` — read-only context; **Noetfield product rules still governed by GCIP v4 and STRATEGIC_LOCK.**

---

## VIRLUX (external — do not mix)

- Interac, Circle, B2B payments — **separate codebase**.
- Tracker: [todolist/external/virlux/](todolist/external/virlux/)
- Never copy VIRLUX env vars, payment flows, or MSB marketing into Noetfield.
