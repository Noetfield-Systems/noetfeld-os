# L0 Repo Graph Memory v1 — NOOS (noetfeld-OS)

**Status:** ACTIVE — rolled out from the `sina-governance-SSOT` pilot. Custom
stdlib-only script: no deploy, no database, no LLM calls, no network (see that
repo's `docs/GRAPH_TOOL_DECISION_v1.md` for why Graphiti/Graphify were rejected).

## Why

Gives agents a compact, static subsystem + file + reference map to query **before**
opening files, so "understand the repo" / audit / map passes don't re-read the tree.

## Pieces

| Piece | Path |
|---|---|
| Graph builder | `scripts/build_repo_graph_v1.py` |
| Graph query | `scripts/query_repo_graph_v1.py` |
| Compact report (read first) | `graph-out/GRAPH_REPORT.md` |
| Full index (committed — small here) | `graph-out/graph_index_v1.json` |
| Verifier | `scripts/verify_l0_repo_graph_memory_v1.sh` |
| Broad-read gate | `AGENTS.md` (§ "L0 repo graph memory — broad-read gate") |

## Commands

```
python3 scripts/build_repo_graph_v1.py                 # build/refresh (zero-token)
python3 scripts/query_repo_graph_v1.py <subsystem|keyword>
bash scripts/verify_l0_repo_graph_memory_v1.sh         # PASS/FAIL receipt in receipts/
```

## NOOS tuning

- `SUBSYSTEM_DIRS` lists NOOS's 19 top-level subsystems (audit, cloud, config,
  data, docs, export, fixtures, infrastructure, noetfield-org, noetfield_gate,
  ops, packages, portal, public_site, receipts, scripts, tests, videos, .github).
- Repo is small (~960 files) so the full index (~326KB) is committed, unlike the
  large SourceA/Noetfield clones where it is gitignored.
- Builder is symlink-hardened (shared template with SourceA).
- Verifier keyword check uses `README` (present repo-wide).

All paths are repo-relative; the tool indexes **this** clone
(`~/Desktop/Noetfield-Systems/noetfeld-OS`), never an outside `~/Projects` copy.
