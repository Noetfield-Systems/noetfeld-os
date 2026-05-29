# Project boundaries (locked)

**Effective:** 2026-05-29  
**Tracking update:** Public repo uses [docs/ROADMAP.md](docs/ROADMAP.md) + Issues — not root `todolist/`.

## Lock

| Scope | Allowed in this repo/chat |
|-------|---------------------------|
| **Noetfield** product, www, platform API, CI, docs, `NF-*` in **Issues** | **Yes** |
| **TrustField Technologies** corporate / execution / `TF-*` | **No** — private ops or TrustField repo |
| **VIRLUX** payments / `VL-*` | **No** — VIRLUX repo only |

## Agent checklist (before every task)

1. Is the work **Noetfield** (`NF-*`, governance platform, public site)? → Proceed.
2. Is it **TrustField** or **VIRLUX**? → Stop; use the correct repo/chat.
3. Does the diff add payment rails, MSB claims, or recreate public `todolist/`? → Reject.
4. Never commit `ops/private/` (gitignored founder notes).

## Noetfield north star (one line)

Governance execution and AI policy enforcement **before** external execution — Noetfield never touches value ([PRODUCT_TRUTH.md](PRODUCT_TRUTH.md)).

**Public roadmap:** [docs/ROADMAP.md](docs/ROADMAP.md) · [docs/strategy/noetfield-future-path.md](docs/strategy/noetfield-future-path.md)  
**Execution:** [GitHub Issues](https://github.com/kazemnezhadsina144-dot/Noetfield/issues) · [ops/README.md](ops/README.md)
