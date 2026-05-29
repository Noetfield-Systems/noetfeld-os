# Operations tracking (Noetfield)

## Public vs private

| Location | Visibility | Contents |
|----------|------------|----------|
| [docs/ROADMAP.md](../docs/ROADMAP.md) | **Public** | Horizons + shipped summary |
| [docs/strategy/noetfield-future-path.md](../docs/strategy/noetfield-future-path.md) | **Public** | Product strategy |
| [GitHub Issues](https://github.com/kazemnezhadsina144-dot/Noetfield/issues) | **Team** (repo visibility) | `NF-*` execution, PR links |
| **`ops/private/`** | **Local only** (gitignored) | Full markdown trackers, founder go-live detail |

**Do not** commit `ops/private/` — it is listed in `.gitignore`.

---

## First-time setup (founder machine)

If you had trackers before this layout, they may already exist locally under `ops/private/` after pulling the boundary fix branch.

Otherwise:

```bash
mkdir -p ops/private
# Restore from your backup, or recreate issues from templates:
gh issue list
```

Run once to seed private folder from repo history (if you still have old `todolist/` in a prior commit):

```bash
./scripts/bootstrap-private-ops.sh
```

---

## GitHub Issues (recommended)

Use labels:

| Label | Use |
|-------|-----|
| `launch` | DNS, deploy, secrets, smoke |
| `legal` | privacy/terms review |
| `engineering` | code, CI, platform |
| `NF-P0` | launch blocker |

Create issues from templates: **New issue** → Launch blocker / Engineering / Legal.

**Agents (Cursor):** read [`.cursor/rules/noetfield-scope.mdc`](../.cursor/rules/noetfield-scope.mdc) and open Issues; do not recreate `todolist/` at repo root.

---

## Other entities (not in this repo)

| Entity | Tracking |
|--------|----------|
| **TrustField Technologies** | Private TrustField repo or `ops/private/todolist/external/trustfield-technologies/` locally |
| **VIRLUX** | VIRLUX codebase + local `ops/private/todolist/external/virlux/` |

Never add TrustField or VIRLUX tasks to public Noetfield Issues without explicit scope.
