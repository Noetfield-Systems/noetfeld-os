# Noetfield future plans library (NO ASF)

**Count:** 1000 plan stubs (regenerate with `python3 scripts/generate-future-plans.py`)  
**Canonical path:** `~/Desktop/Noetfield/os/plans/`  
**Cursor mirror:** `~/.cursor/plans/noetfield-os/` (index only; full library stays in repo)

## When you say “plan with no ASF”

Agents must:

1. **Not** wait for ASF commit, push, ingest, or SourceA edits.
2. Read [`REGISTRY.json`](./REGISTRY.json) or [`REGISTRY.md`](./REGISTRY.md).
3. Pick the highest-value **backlog** item matching current `os/SHIP_NOW.md` / sprint (prefer **T0** then **T1**, lower phase number when tied).
4. Open the plan file under `phase-*/T*/nf-future-*.md` and execute it (verify → ingest → sync → commit).
5. **Update** the plan front matter `status: done` and append a line to [`REGISTRY.json`](./REGISTRY.json) `plans[].status` (or re-run generator after editing templates).

## Organization

| Axis | Values |
|------|--------|
| **Phase** | `phase-0-ship-ops` … `phase-9-ecosystem-bridge` (10 phases × 100 plans) |
| **Tier** | `T0` Critical → `T3` Low (25 plans per phase×tier cell) |
| **ID** | `nf-future-0001` … `nf-future-1000` |

## Files

| File | Purpose |
|------|---------|
| `REGISTRY.json` | Machine index (all 1000 IDs, paths, phase, tier, domain) |
| `REGISTRY.md` | Human index |
| `phase-*/T*/nf-future-*.md` | Individual plan stubs |

## Active ship queue

Immediate work still flows through [`os/plan.json`](../plan.json) `next_tasks` and [`os/SHIP_NOW.md`](../SHIP_NOW.md). This library is the **long-term backlog**; move items into `next_tasks` when ready to implement.

## Maintenance

```bash
cd ~/Desktop/Noetfield
python3 scripts/generate-future-plans.py   # refresh all stubs + registry
```

After shipping a plan, set `status: done` in the plan markdown front matter and optionally add evidence paths. Do not delete plan files — history matters for ingest and audits.
