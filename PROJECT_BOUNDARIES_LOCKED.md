# Project boundaries (locked)

**Effective:** 2026-05-29  
**Tracking update:** Public repo uses [docs/ROADMAP.md](docs/ROADMAP.md) + Issues — not root `todolist/`.

## Lock

| Scope | Allowed in this repo/chat |
|-------|---------------------------|
| **Noetfield** product, www, platform API, CI, docs, `NF-*` in **Issues** | **Yes** |
| **TrustField Technologies** corporate / execution / `TF-*` | **No** — private ops or TrustField repo |
| **VIRLUX** payments / `VL-*` | **No** — VIRLUX repo only |

## Supabase split handoff

```yaml
supabase_split: "SourceA/Forge→portfolio-spine; Noetfield/TrustField→noetfield; Labs/Virlux→labs-sandbox; async events only; no cross-project joins; no secrets in repo."
```

For full authority, read SourceA `data/supabase-portfolio-tiers-v1.json`; this repo does not redefine ownership. Noetfield uses the `noetfield` Supabase project, schema `noetfield`. TrustField shares the same project but stays in schema `trustfield` and outside this repo's execution scope.

## Agent checklist (before every task)

1. Is the work **Noetfield** (`NF-*`, governance platform, public site)? → Proceed.
2. Is it **TrustField** or **VIRLUX**? → Stop; use the correct repo/chat.
3. Does the diff add payment rails, MSB claims, or recreate public `todolist/`? → Reject.
4. Never commit `ops/private/` (gitignored founder notes).

## Noetfield north star (one line)

Governance execution, AI policy enforcement, and risk intelligence **before** external execution — Noetfield never touches value ([PRODUCT_TRUTH.md](PRODUCT_TRUTH.md)). Other companies (TrustField, VIRLUX) are separate paths.

**Internal go-forward:** [docs/strategy/GO_FORWARD_NOW.md](docs/strategy/GO_FORWARD_NOW.md)

**Public roadmap:** [docs/ROADMAP.md](docs/ROADMAP.md) · [docs/strategy/noetfield-future-path.md](docs/strategy/noetfield-future-path.md)  
**Execution:** [GitHub Issues](https://github.com/Noetfield-Systems/Noetfield/issues) · [ops/README.md](ops/README.md)
