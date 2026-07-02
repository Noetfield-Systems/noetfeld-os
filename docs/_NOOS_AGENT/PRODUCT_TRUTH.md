<!-- NOOS-AGENT-DOC -->
# PRODUCT TRUTH — Noetfield OS
Date: 2026-06-29
Phase: 3 — Evidence export + TLE mapping
Steps done: ~22 / 1000 · UPG plan: 8 / 300 evidence-backed rows closed (see `UPGRADE_MANIFEST.json`)
Runtime: FastAPI + SQLite + .venv
Port: 8001 (local dev) · Railway gel-api (production)
Tests: 26 passing
Built: API auth, rule_set_version, idempotency, health, TLE v1 export, board PDF stub, noetfield-gate CLI
Local smoke: 127.0.0.1:8001 /health OK · /readiness OK when uvicorn is running
Hosted: api.noetfield.com /health OK · /readiness OK (Railway gel-api)
Website live: www.noetfield.com 200 · gate/trust-ledger/status 200 · platform.noetfield.com/health 200
Website drift: live homepage is titled "Noetfield Intelligence"; /intelligence/ is 404 while /intelligence/intake/ is used as a diagnostic CTA. Website repo owns nav/page implementation.
Website E2E: current website repo `make verify-www-e2e` PASS after live nerve hardening; internal/static truth paths 404 on production.
Live nerve: website repo `governance/NOETFIELD_LIVE_NERVE_RECEIPT.json` PASS across www output, www chat, platform chat, and api.noetfield.com readiness.
NOOS sync gate: `bash scripts/check_noos_live_sync_gate.sh` refreshes the website live nerve, then writes `docs/_NOOS_AGENT/live_sync/NOOS_LIVE_SYNC_RECEIPT.json`; set `NOOS_LIVE_SYNC_SCOPE=runtime|public|studio|foundation|ecosystem|all` for focused truth. Current ecosystem gate DEGRADED only because SourceA session gate is not green and `/intelligence/` is 404.
PyPI: **LIVE** — `noetfield-gate` v0.1.0 + `sourcea-boot` v0.1.0 on PyPI (org migration pending)
Gap: npm `@noetfield/gate` · chatbot Phases 3–10 (distill, pgvector RAG)
Commercial: NOOS-AGENT-20260615-010 strategy (2 PAGER) + 011 NW1 + 013 SW1 one-pagers in vault
