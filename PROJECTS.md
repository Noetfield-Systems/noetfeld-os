# Projects — locked boundaries

**Status:** Locked · **This repository and Cursor chat = Noetfield only.**

| Project | What it is | This repo / chat? |
|---------|------------|-------------------|
| **Noetfield** | Governance execution infrastructure · `www.noetfield.com` · `platform.noetfield.com` | **Yes — build, deploy, and track here** |
| **TrustField Technologies** | Separate parent / execution / corporate entity | **No** — private ops notes or TrustField repo |
| **VIRLUX** | Separate Canadian B2B FX / payments product | **No** — VIRLUX codebase only |

**Rule:** *Noetfield = this repo and this chat. TrustField and VIRLUX = other scopes — do not implement in Noetfield PRs.*

See also: [PROJECT_BOUNDARIES_LOCKED.md](PROJECT_BOUNDARIES_LOCKED.md)

---

## Noetfield (this repo)

- Pre-execution governance: policy, compliance logic, audit traces — **no custody, no payments** ([STRATEGIC_LOCK.md](STRATEGIC_LOCK.md)).
- **Public roadmap:** [docs/ROADMAP.md](docs/ROADMAP.md) · [docs/strategy/noetfield-future-path.md](docs/strategy/noetfield-future-path.md)
- **Team tracking:** [GitHub Issues](https://github.com/kazemnezhadsina144-dot/Noetfield/issues) · [ops/README.md](ops/README.md)

---

## TrustField Technologies (external — do not mix)

- Corporate / execution entity — **not** tracked in public Noetfield markdown.
- Use a **TrustField-scoped** private repo or local `ops/private/` (gitignored).

Historical SSOT mentioning both entities: `docs/SOURCE_OF_TRUTH/` — read-only context; **Noetfield product rules still governed by GCIP v4 and STRATEGIC_LOCK.**

---

## VIRLUX (external — do not mix)

- Interac, Circle, B2B payments — **separate codebase**.
- Never copy VIRLUX env vars, payment flows, or MSB marketing into Noetfield.
