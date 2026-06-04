# Operations tracking (Noetfield)

## Agent entry point (read first)

**[.cursor/AGENT_TRACKING.md](../.cursor/AGENT_TRACKING.md)** — where Cursor/cloud agents find tasks safely.

---

## Public vs private

| Location | Visibility | Contents |
|----------|------------|----------|
| [.cursor/AGENT_TRACKING.md](../.cursor/AGENT_TRACKING.md) | **Public** | Agent workflow (no secrets) |
| [docs/ROADMAP.md](../docs/ROADMAP.md) | **Public** | Horizons + shipped summary |
| [GitHub Issues](https://github.com/kazemnezhadsina144-dot/Noetfield/issues) | **Team** | `NF-*` execution, PR links |
| **`ops/private/`** | **Gitignored** | Full `todolist/`, go-live + legal checklists, **`sourceA/`** (Sina OS SSOT mirror) |

**Never commit `ops/private/`.**

---

## First-time setup (founder machine)

```bash
./scripts/bootstrap-private-ops.sh
./scripts/seed-msb-partner-pack.sh
```

Creates `ops/private/todolist/` and `ops/private/docs/` from git history when available.  
MSB commercial templates (SOW, one-pager, outreach tracker) copy from [ops/templates/msb/](templates/msb/) → `ops/private/msb/`.

---

## GitHub Issues

Labels: `launch`, `legal`, `engineering`, `NF-P0` — templates in `.github/ISSUE_TEMPLATE/`.

Use Issues when agents run in ephemeral cloud workspaces without `ops/private/`.

---

## Other entities (not Noetfield)

| Entity | Tracking |
|--------|----------|
| **TrustField** | TrustField repo or `ops/private/todolist/external/trustfield-technologies/` |
| **VIRLUX** | VIRLUX repo or `ops/private/todolist/external/virlux/` |
