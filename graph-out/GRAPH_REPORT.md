# L0 Repo Graph Report — sina-governance-ssot

Generated (last indexed): `2026-07-09T07:05:07Z`
Total files: 962 · Total size: 23.4MB · Edges detected: 1337

**Read this file first.** Do not spawn broad repo-reading agents ("understand the repo", "map subsystem X", "audit Y") until you have read this report and, if you need more detail, queried the index with `python3 scripts/query_repo_graph_v1.py <subsystem-or-keyword>`. This report + a query response should answer routing questions ("which files touch X", "how big is subsystem Y") without opening every file in the subsystem.

## Subsystem map (sorted by size, descending)

| subsystem | files | size | largest files |
|---|---:|---:|---|
| docs/ | 95 | 19.3MB | `docs/run_patches/noetfield_run_patch_pack_10100_v1.jsonl`, `docs/run_patches/execution/noetfield_run_patch_execution_receipts_v1.jsonl`, `docs/ops/ECOSYSTEM_CONTROLLED_EXECUTION_1000_PLAN_DRAFT_v1.md`, `docs/_NOOS_AGENT/[NOOS-AGENT-20260608-004]_ROADMAP_1000_STEPS_10_PHASES.md`, `docs/run_patches/noetfield_run_patch_manifest_10100_v1.json`, `docs/ops/NOETFIELD_OS_CONTROL_SCOPE_DISCOVERY_REPORT_v1_20260629-1813.md` |
| videos/ | 12 | 1.5MB | `videos/noetfeld-governance-motion/snapshots/frame-02-at-5.0s.png`, `videos/noetfeld-governance-motion/snapshots/frame-01-at-2.5s.png`, `videos/noetfeld-governance-motion/snapshots/frame-03-at-7.5s.png`, `videos/noetfeld-governance-motion/snapshots/frame-04-at-10.0s.png`, `videos/noetfeld-governance-motion/snapshots/frame-00-at-0.0s.png`, `videos/noetfeld-governance-motion/snapshots/contact-sheet.jpg` |
| receipts/ | 455 | 1.0MB | `receipts/proof/noos-cf-railway-dispatch-verify-v1.json`, `receipts/proof/noos-machine-loops-upgrade-closeout-v1.json`, `receipts/proof/noos-loop-verify-all-v1.json`, `receipts/proof/noetfield-voyage-drift-patches/0002-feat-L8-Voyage-AI-semantic-drift-SourceA-pattern-for.patch`, `receipts/proof/noos-trustfield-observe-witness-v1.json`, `receipts/proof/noos-loop-baseline-audit-v1.json` |
| scripts/ | 155 | 799.7KB | `scripts/autorun_status_v1.py`, `scripts/noos_integrator_sync_v1.py`, `scripts/noos_machine_loops_v1.py`, `scripts/noos_loop_runner_v1.py`, `scripts/noos_integrator_daily_checklist_v1.py`, `scripts/open_noos_verified_window_v1.py` |
| data/ | 39 | 238.5KB | `data/noos-upgrade-planes-v1.json`, `data/noos-parallel-agent-registry-v1.json`, `data/noos-unified-upgrade-backlog-v1.json`, `data/noos-trigger-host-inventory-v1.json`, `data/trigger-registry-v1.json`, `data/autorun-workflows-v1.json` |
| noetfield-org/ | 20 | 130.5KB | `noetfield-org/receipts/NOOS_MODEL_OUTCOME_VERIFICATION_RECEIPT_2026-07-05.md`, `noetfield-org/MODEL_OUTCOME_VERIFICATION_LEDGER.md`, `noetfield-org/receipts/NOOS_SERVICE_LANE_REGISTRATION_2026-07-05.md`, `noetfield-org/receipts/NOOS_SERVICE_LANE_TICK_2026-07-05.md`, `noetfield-org/SYNC_RECEIPTS.md`, `noetfield-org/NOOS_CONTROL_PANEL_AUTHORITY_REPORT_2026-07-04.md` |
| tests/ | 38 | 91.3KB | `tests/test_noos_worker_kernel_v1.py`, `tests/test_autorun_status_v1.py`, `tests/test_phase2_decision.py`, `tests/test_cursor_local_mac_t2_v1.py`, `tests/test_cloud_inbox_worker_v1.py`, `tests/test_noos_integrator_sync_v1.py` |
| .github/ | 41 | 76.6KB | `.github/workflows/noos-factory-autorun.yml`, `.github/copilot-instructions.md`, `.github/workflows/noos-specialist.yml`, `.github/workflows/noos-self-heal.yml`, `.github/workflows/noos-cross-repo-orchestrator.yml`, `.github/workflows/noos-researcher.yml` |
| public_site/ | 15 | 37.1KB | `public_site/static/site.css`, `public_site/routes.py`, `public_site/content/trust-ledger/index.md`, `public_site/templates/base.html`, `public_site/content/gate/partners/index.md`, `public_site/static/cookies.js` |
| cloud/ | 9 | 25.7KB | `cloud/workers/noos-deadman-v1/src/index.js`, `cloud/workers/noos-loop-fleet-tick-v1/src/index.js`, `cloud/workers/noos-factory-autorun-tick-v1/src/index.js`, `cloud/workers/noos-loop-fleet-tick-v1/src/dispatch-table.json`, `cloud/workers/noos-deadman-v1/src/loop-intervals.json`, `cloud/workers/noos-deadman-v1/src/deadman-config.json` |
| ops/ | 13 | 25.4KB | `ops/railway/noos-loop-runner/server.py`, `ops/fly/noos-loop-executor/server.py`, `ops/fly/noos-self-heal-runner/server.py`, `ops/fly/noos-inbox-runner/server.py`, `ops/fly/noos-inbox-runner/fly.toml`, `ops/fly/noos-self-heal-runner/fly.toml` |
| noetfield_gate/ | 8 | 23.4KB | `noetfield_gate/boot.py`, `noetfield_gate/cli.py`, `noetfield_gate/decide.py`, `noetfield_gate/verify.py`, `noetfield_gate/policies/corridor_policy.json`, `noetfield_gate/intent_validate.py` |
| packages/ | 16 | 20.8KB | `packages/auth-core/package-lock.json`, `packages/gate/src/index.ts`, `packages/noetfield-gate/README.md`, `packages/gate/package-lock.json`, `packages/auth-core/src/middleware.test.ts`, `packages/auth-core/src/middleware.ts` |
| infrastructure/ | 7 | 10.4KB | `infrastructure/supabase/migrations/0015_stale_lane_pgcron_t8.sql`, `infrastructure/supabase/migrations/0018_security_advisor_warnings.sql`, `infrastructure/supabase/migrations/0017_enable_rls_machine_tables.sql`, `infrastructure/supabase/migrations/0016_noos_loop_registry.sql`, `infrastructure/supabase/migrations/0014_factory_cycle_status_degraded.sql`, `infrastructure/supabase/migrations/0013_noetfield_truth_log_schedule_register.sql` |
| export/ | 3 | 9.4KB | `export/tle_mapper.py`, `export/board_pdf.py`, `export/__init__.py` |
| portal/ | 2 | 4.2KB | `portal/routes.py`, `portal/schemas.py` |
| config/ | 2 | 3.7KB | `config/model-router.yml`, `config/noos-local.env.fill-me` |
| audit/ | 1 | 971B | `audit/audit_store.py` |
| fixtures/ | 2 | 488B | `fixtures/demo_intents/decline-dti.json`, `fixtures/demo_intents/approve.json` |
| (root files) | 29 | 76.9KB | `Makefile`, `database.py`, `AGENTS.md`, `decision_engine.py`, `router.py`, `risk_model.py` |

## Dependency / reference edges

1337 static repo-relative path references were detected across .py/.sh/.md/.json/.yaml/.yml/.jsonc files (best-effort regex scan, not a real import graph — this is a governance/docs-heavy repo, not a single-language codebase). Full edge list is in `graph_index_v1.json`; query by file or subsystem with the query script rather than reading it directly.

## Ignored directories

`.cache`, `.git`, `.noos_cache`, `.pytest_cache`, `.venv`, `.wrangler`, `__pycache__`, `build`, `dist`, `graph-out`, `node_modules`, `venv`

## Query command

```
python3 scripts/query_repo_graph_v1.py <subsystem-name|keyword|path-fragment>
```

## Rebuild command

```
python3 scripts/build_repo_graph_v1.py
```

Rebuild whenever the file layout changes materially (new subsystem, large doc/data additions) — this report drifts from truth otherwise. See `docs/L0_REPO_GRAPH_MEMORY_v1.md` for the token budget rule and the broad-read prevention rule.
