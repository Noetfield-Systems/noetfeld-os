# Living System Upgrade Propagation (LSUP) v1

**Status:** DESIGN — founder review  
**Date:** 2026-07-13  
**Canonical root:** `noetfeld-OS/noetfield-org/`  
**Problem this solves:** A law changes (e.g. production www surface, retired platform, new brain taxonomy) but only one doc lane updates. Agents read stale nodes → wrong actions (deploy to dead platform, edit stale path, recommend forbidden surface).

**Goal:** Every upgrade is a **single declared bundle** that propagates across **all wired nodes** with **proof**, not hope.

---

## Core idea

Treat the ecosystem as a **living graph**, not a folder tree.

| Concept | Meaning |
|---------|---------|
| **Law** | One atomic truth change (`LAW-20260713-001`: www production = Cloudflare static www only) |
| **Node** | Any surface that can drift: repo, doc lane, script, workflow, agent entrypoint, live URL probe, graph edge, receipt |
| **Blast radius** | Explicit list of nodes that must change when a law lands |
| **Upgrade bundle** | Law + blast radius + apply rules + verify gates + closeout receipt |
| **Propagation run** | Mutex → apply → verify all nodes → emit receipt or fail closed |
| **Drift** | Any node still matching old truth after closeout |

**Rule:** No law is "done" until the propagation receipt is green or founder waives specific nodes with reason.

---

## Why single-doc law changes fail (case study)

What went wrong was not missing a "RETIRED" label — it was **no propagation graph**:

```
Law changed (founder) ──► 1 doc updated
                              │
                    47 other nodes untouched
                              │
                    next agent reads any stale node
                              │
                    wrong deploy recommendation
```

LSUP inverts this:

```
Law declared ──► blast radius computed ──► all nodes patched or scanned
                              │
                    verify gates run (forbidden, paths, live probes)
                              │
                    closeout receipt ──► DOC_INDEX version bump
                              │
                    agents blocked until green (integrator mutex)
```

---

## Architecture (4 layers)

### Layer 1 — Law registry (declare once)

**File:** `noetfield-org/system-laws/SYSTEM_LAW_REGISTRY_v1.json`  
**Schema:** `noos-system-law-v1`

```json
{
  "law_id": "LAW-20260713-001",
  "title": "Noetfield www production surface",
  "truth": "Cloudflare Pages noetfield-www + edge worker only",
  "forbidden_tokens": [],
  "supersedes": [],
  "effective_at": "2026-07-05T00:00:00Z",
  "blast_radius_template": "www-production-surface-v1"
}
```

Laws are **small**. Bundles reference one or more laws.

**Existing hooks to extend:**
- `FORBIDDEN_MARKERS.txt` → generated from laws with `forbidden_tokens`
- `NOETFIELD_STRATEGY_LOCK_RECEIPT_v1.json` → references law IDs
- `DOC_INDEX_v1.md` → lists active law IDs + registry version

---

### Layer 2 — Blast radius map (know every node)

**File:** `noetfield-org/system-laws/BLAST_RADIUS_MAP_v1.json`  
**Schema:** `noos-blast-radius-v1`

Templates name **node classes**, not one-off file lists:

| Template | Node classes |
|----------|--------------|
| `www-production-surface-v1` | agent entrypoints, ops runbooks, service lanes, routing matrix, handoff docs, live sync receipt fields, graph script edges, CI workflow names, public URL probes |
| `forbidden-token-v1` | all markdown/json in scoped repos, agent instructions, copilot manifests, run patch manifest surfaces |
| `canonical-path-v1` | DOC_INDEX, stale pointers, README redirects, integrator scope paths |
| `brain-taxonomy-v1` | public copy, proof JSON, strategy blueprint, chatbot knowledge bundles |

Each **node** record:

```json
{
  "node_id": "noos-agents-md",
  "class": "agent_entrypoint",
  "path": "noetfeld-OS/AGENTS.md",
  "repo": "noetfeld-OS",
  "verify": ["forbidden_scan", "grep_truth"],
  "apply": ["search_replace", "manual_waiver_only"]
}
```

**Workspace scope (Noetfield-Systems container):**

| Repo | Plane | Integrator lane |
|------|-------|-----------------|
| `noetfeld-OS` | NOOS / integrator | primary |
| `Noetfield` | www / public | website |
| `SourceA` | delivery / brain | sourcea |
| `sina-governance-SSOT` | SG spine | governance |
| `TrustField-Technologies` | separate venture | trustfield |
| `noetfield-studio-ide` | sandbox IDE | studio |
| `SinaaiMonoRepo` | platform utils | platform |

Cross-repo propagation is **not** git monorepo magic — it is **integrator-orchestrated fan-out** with per-repo receipts.

---

### Layer 3 — Propagation engine (apply + verify)

**Script (proposed):** `scripts/noos_living_system_propagate_v1.py`  
**Make target:** `make law-propagate BUNDLE=<id>`

**Run phases (always same order):**

```
1. PREFLIGHT
   - integrator claim: scope=law-propagation, mutex=all blast-radius repos
   - live sync gate (scope=ecosystem) — baseline snapshot
   - git status per repo — classify dirty (COMMIT/LEAVE/WAIVE)

2. APPLY
   - For each node in bundle:
       - auto: search_replace / sed rules from bundle
       - manual: emit waiver request (founder-only nodes)
   - Bump FORBIDDEN_MARKERS from law registry
   - Bump DOC_INDEX law version + active law list

3. VERIFY (fail closed)
   - forbidden_scan: no token outside marker file (all scoped repos)
   - path_canonical: stale pointers absent
   - truth_grep: required phrases present in entrypoints
   - test_forbidden_markers.py (expanded)
   - live_sync gate (scope from bundle)
   - loop_registry_reconcile (if bundle touches motors)
   - graph stale check (rebuild if script names changed)

4. CLOSEOUT
   - Write receipts/proof/noos-law-propagation-<bundle-id>-v1.json
   - Append noetfield-org/SYNC_RECEIPTS.md
   - Release integrator mutex
   - If any verify FAIL → receipt status DEGRADED, block agent deploy claims
```

**Existing scripts composed (not replaced):**

| Step | Existing tool |
|------|---------------|
| Mutex | `noos_integrator_sync_v1.py claim` |
| Live baseline | `check_noos_live_sync_gate.sh` |
| Plane export | `noos_upgrade_manifest_publish_v1.py` |
| Registry | `noos_loop_registry_reconcile_v1.py` |
| Drift | `noos_deploy_drift_kaizen_v1.py` |
| Receipt chain | `noos_receipt_chain_v1` (if present) |
| Forbidden | `tests/test_forbidden_markers.py` (expand) |

---

### Layer 4 — Agent firewall (stop stale reads)

Agents don't get to "discover" truth by grep roulette.

**Mandatory read order (already started in AGENTS.md):**

1. `noetfield-org/DOC_INDEX_v1.md` — registry version + active laws
2. `noetfield-org/FORBIDDEN_MARKERS.txt`
3. `noetfield-org/system-laws/SYSTEM_LAW_REGISTRY_v1.json` — if task touches infra/www/brain
4. Latest propagation receipt for relevant law IDs

**Hard blocks (CI + local):**

| Gate | Blocks |
|------|--------|
| `make law-drift-check` | Any forbidden token outside marker file |
| `make law-entrypoint-check` | AGENTS.md / DOC_INDEX / PRODUCT_TRUTH contradict active law registry |
| Integrator claim | Parallel edits during open propagation run |
| Pre-deploy (founder) | Live sync + propagation receipt freshness |

**Stale path kill switch:** Any doc pointing to workspace-root `noetfield-org/` fails `path_canonical` gate.

---

## Upgrade bundle format

**File:** `noetfield-org/system-laws/bundles/BUNDLE-20260713-001-www-surface.json`  
**Schema:** `noos-law-upgrade-bundle-v1`

```json
{
  "bundle_id": "BUNDLE-20260713-001",
  "laws": ["LAW-20260713-001"],
  "blast_radius_template": "www-production-surface-v1",
  "apply_rules": [
    {"pattern": "OBSOLETE_WWW_DEPLOY", "replacement": "Cloudflare www deploy", "glob": "**/*.md"},
    {"pattern": "OBSOLETE_WWW_STATIC", "replacement": "Cloudflare static www"}
  ],
  "required_truth_phrases": [
    {"path": "noetfeld-OS/AGENTS.md", "must_contain": "Cloudflare static www"},
    {"path": "noetfeld-OS/docs/ops/NOOS_CLOUDFLARE_WWW_DEPLOY_v1.md", "must_contain": "Cloudflare Pages"}
  ],
  "verify_scopes": ["public", "ecosystem"],
  "founder_waivers": [],
  "agent_deploy": "ALLOWED_VIA_CLOUDFLARE_WWW"
}
```

**Bundle types:**

| Type | Example | Who runs |
|------|---------|----------|
| `law-replacement` | Remove forbidden platform refs | Agent prepares bundle; founder approves propagate |
| `canonical-path` | Move docs to correct repo path | Agent + founder |
| `brain-taxonomy` | Lock brain names in public copy | Agent prepares; SG ratifies in Lane B |
| `live-surface` | New public URL / route | Agent deploy via approved www path |

---

## Real-time vs batch

**Real-time** in a living system means **continuous drift detection**, not instant git push to 8 repos.

| Mode | Trigger | Latency |
|------|---------|---------|
| **Event** | Law registry version bump | Propagation run within same session |
| **Continuous** | Hourly integrator witness + forbidden scan | Catches manual edits / agent drift |
| **Pre-agent** | Cursor session boot reads DOC_INDEX version vs last receipt | Blocks if stale |
| **Pre-founder-deploy** | Live sync + propagation receipt | Hard gate |

True "all nodes at once" = **one bundle, one mutex, one closeout receipt** — not 47 chat acknowledgments.

---

## Phased build (smallest valid path)

### v0.1 — Law registry + drift scanner (this week)

- [x] Create `system-laws/SYSTEM_LAW_REGISTRY_v1.json` with first 3 laws (www surface, canonical noetfield-org path, agent deploy authority)
- [x] Create `BLAST_RADIUS_MAP_v1.json` with agent entrypoint + ops doc node classes
- [x] Expand `test_forbidden_markers.py` → read all markers from file, scan `noetfeld-OS/**` agent docs
- [x] Add `scripts/noos_law_drift_check_v1.py` + `make law-drift-check`
- [x] Wire `make law-drift-check` into integrator daily witness

**Done when:** CI fails if forbidden token appears outside marker file.

### v0.2 — Bundle + propagate CLI

- [ ] Bundle schema + one worked example (www surface bundle — retroactive receipt)
- [ ] `noos_living_system_propagate_v1.py` — preflight/verify/closeout (apply rules optional; verify mandatory)
- [ ] Propagation receipt schema `noos-law-propagation-receipt-v1`
- [ ] DOC_INDEX shows registry version + last propagation receipt ID

**Done when:** One command proves all entrypoints agree with law registry.

### v0.3 — Cross-repo fan-out

- [ ] Extend blast radius to `Noetfield/`, `SourceA/`, `sina-governance-SSOT/` read-only scan + waiver list
- [ ] Integrator mutex across workspace repos during propagation
- [ ] Per-repo sub-receipts merged into workspace closeout

**Done when:** Single bundle verifies sibling repos, not just noetfeld-OS.

### v0.4 — Living nerve hook

- [ ] `NOOS_LIVE_SYNC_SCOPE=law` — fails if propagation receipt older than law registry version
- [ ] Graph rebuild auto-trigger when blast radius includes script/workflow nodes
- [ ] Machine loop `law-drift-repair` routes to critic (not founder) for doc-only fixes

**Done when:** Degraded live sync until propagation green — agents cannot claim "fully green."

---

## Operating rules (locked intent)

1. **Retire = remove**, not label. Forbidden tokens live only in `FORBIDDEN_MARKERS.txt` (generated from law registry).
2. **No law without blast radius.** If you can't name the nodes, the law isn't ready.
3. **No closeout without verify.** Chat acknowledgment is not a receipt.
4. **Agents deploy via approved path; founder approves propagation bundles** for cross-cutting law changes.
5. **Stale pointers are bugs** — `path_canonical` gate treats them like forbidden tokens.
6. **SG ratification (Lane B) parallel to propagation** — content can be ready while SG reconciles; propagation covers agent-facing truth, not canon ratification.

---

## Relationship to existing NOOS pieces

```
                    ┌─────────────────────┐
                    │  SYSTEM_LAW_REGISTRY │
                    └──────────┬──────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         ▼                     ▼                     ▼
  FORBIDDEN_MARKERS      DOC_INDEX vN          UPGRADE_MANIFEST
         │                     │                     │
         └──────────┬──────────┴──────────┬──────────┘
                    ▼                     ▼
           law-drift-check          integrator mutex
                    │                     │
                    └──────────┬──────────┘
                               ▼
                    propagation closeout receipt
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
              live sync gate         agent entrypoints
```

LSUP is the **missing orchestration layer** — not a replacement for integrator, live sync, or upgrade manifest. It **binds them to declared law**.

---

## First laws to register (proposed)

| Law ID | Truth |
|--------|-------|
| `LAW-20260705-001` | Noetfield www = Cloudflare Pages `noetfield-www` + edge worker |
| `LAW-20260713-001` | Canonical NOOS control docs = `noetfeld-OS/noetfield-org/` only |
| `LAW-20260713-002` | Agents deploy via approved Cloudflare www path |
| `LAW-20260713-003` | Brain taxonomy — no unqualified "Brain" in public copy |
| `LAW-20260704-001` | NOOS = integrator; Studio IDE = sandbox manager only |

---

## Next action (founder)

1. Review this design — approve v0.1 scope or cut.
2. If approved: agent implements v0.1 (registry + drift scanner + expanded forbidden test) in one scoped commit.
3. Emit retroactive closeout receipt for www-surface law (documents today's purge as first propagation run).

**No production deploy. No SG ratification required for v0.1 tooling.**
