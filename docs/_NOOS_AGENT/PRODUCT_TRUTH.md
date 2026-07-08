<!-- NOOS-AGENT-DOC -->
# PRODUCT TRUTH — Noetfield OS
Date: 2026-07-05
Phase: 4 — Chain tools + CI hardening (live authority; SSOT build-order table tracks Phase 3 deliverables + Phase 4 ops)
Steps done: ~22 / 1000 · UPG plan: 30 / 63 backlog items done (see `UPGRADE_MANIFEST.json` + `data/noos-unified-upgrade-backlog-v1.json`)
**Next plan (locked):** `docs/_NOOS_AGENT/[NOOS-AGENT-20260706-033]_UNIFIED_NEXT_PLAN_NOOS_NOETFIELD_v1.md` — dual-track NOOS 48h + Noetfield public audit
Runtime: FastAPI + SQLite + .venv
Port: 8001 (local dev) · Railway gel-api (production)
Tests: 163 passing (noetfeld-os)
Built: API auth, rule_set_version, idempotency, health, TLE v1 export, board PDF stub, noetfield-gate CLI, unified deploy CLI (UPG-0203)
Runtime motor: CF cron → Railway `noos-loop-runner` (Option A; Fly executor destroyed)
Local smoke: 127.0.0.1:8001 /health OK · /readiness OK when uvicorn is running
Hosted: api.noetfield.com /health OK · /readiness OK (Railway gel-api)
Website live: www.noetfield.com 200 · /intelligence/ 200 · /services/agentic-cost-governance 200 · platform.noetfield.com/health 200
Website production: Cloudflare Pages `noetfield-www` + edge denylist worker (`noetfield-www-proxy` → Pages origin; Vercel retired)
Website E2E: `make verify-www-e2e` / live nerve N4 denylist probes — internal paths 404 on production via CF worker
Live nerve: website repo `governance/NOETFIELD_LIVE_NERVE_RECEIPT.json` — refresh with `make verify-live-nerve` before doc claims
NOOS sync gate: `bash scripts/check_noos_live_sync_gate.sh` → `docs/_NOOS_AGENT/live_sync/NOOS_LIVE_SYNC_RECEIPT.json`; scope via `NOOS_LIVE_SYNC_SCOPE=runtime|public|studio|foundation|ecosystem|all`. Ecosystem gate PASS when website nerve + gel-api + public probes green; studio skipped when repo absent on Mac.
PyPI: **LIVE** — `noetfield-gate` v0.1.0 + `sourcea-boot` v0.1.0
Gap: npm `@noetfield/gate` publish · UPG-0001 commercial send (founder gate) · UPG-NF-PUB-01 public-site audit · chatbot Phases 3–10
Built: demo-gel-5min-v1.sh · @noetfield/gate scaffold in packages/gate/
Commercial: ACG lane `PUBLIC_PAGE_LIVE + PROSPECT_PACKET_READY` · founder send pending (`FT-COMMERCIAL-SEND`)
