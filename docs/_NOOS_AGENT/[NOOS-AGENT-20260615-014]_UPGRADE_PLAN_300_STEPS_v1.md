# [NOOS-AGENT-20260615-014] 300-Step Upgrade Plan — Next Upgrades

<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260615-014
doc_type: UPGRADE_PLAN_300
workspace_root: /Users/sinakazemnezhad/Desktop/Noetfield-Systems/noetfeld-OS
classification: INTERNAL — sprint-grade upgrade track
authority: NOETFIELD_OS_SSOT_v1_LOCKED.md, NOOS-AGENT-20260608-004 (master roadmap)
related_docs: NOOS-AGENT-20260615-006, NOOS-AGENT-20260615-010, NOOS-AGENT-20260615-012, PRODUCT_TRUTH.md
manifest: docs/_NOOS_AGENT/UPGRADE_MANIFEST.json
-->

**Status:** Active · 2026-06-15  
**Scope:** Next upgrades from Phase 3 partial → pilot-ready GEL + chain tools + first design partner  
**Step IDs:** `UPG-0001` … `UPG-0300`  
**Tracking:** `UPGRADE_MANIFEST.json`

---

## How to use this plan

| Rule | Detail |
|------|--------|
| **Sprint source** | Pick next unblocked `UPG-*` from current phase; mark done in `UPGRADE_MANIFEST.json` |
| **Master map** | Each UPG maps loosely to master roadmap steps 0194+ (see phase headers) |
| **Frozen zone** | UPG-0001–0030 only until NW1 + SW1 sent (doc 010) |
| **Proof bar** | Any demo/pilot step must show full chain <5 min cold start |
| **Port law** | GEL stays `:8001`; never merge into mono `:8000` |

**Win condition (UPG-0300 exit):** Hosted GEL · signed TLE · chain tools on PyPI · 1 active design partner · W1 demo on disk.

---

## Phase 1 — Unblock & Ship (UPG-0001–0050)

*Master map: commercial Phase 0 + deploy + demo assets · Weeks 1–4*

### 1.1 Commercial unblock (Day 1)

- **UPG-0001:** Founder sends NW1 email — battle card + doc 011 attach — screenshot receipt
- **UPG-0002:** Log NW1 send in `~/.sina/nw1-outbound-send-receipt-v1.json` with timestamp + attach hash
- **UPG-0003:** Send one SW1 message — doc 013 + `noetfield gate` quickstart link
- **UPG-0004:** Log SW1 send receipt JSON under `~/.noetfield/sw1-outbound-receipt-v1.json`
- **UPG-0005:** Record W1 proof demo — `demo-enforcement-5min-v1.sh` — publish video file path in receipt
- **UPG-0006:** Name 10 ICP accounts against doc 010 scorecard — store in `.agent-private/icp-list-v1.json`
- **UPG-0007:** Schedule 15-min live demo date in NW1 reply template
- **UPG-0008:** Fix `www.noetfield.com` DNS — CNAME to `d2e47b585a01bc61.vercel-dns-017.com`
- **UPG-0009:** Re-run `scripts/check_noetfield_com_e2e.py` — all routes green on www
- **UPG-0010:** Verify `/copilot/proof-case/` live on www after DNS cutover

### 1.2 Cloud ship alignment

- **UPG-0011:** Sync Vercel production env — Resend intake keys on canonical project
- **UPG-0012:** Deploy `vercel.json` rewrites — `/health`, `/evaluate` → API routes
- **UPG-0013:** Confirm `www.noetfield.com` parity checklist vs www post-cutover
- **UPG-0014:** Add tamper-evident copy to `index.html` if drifted
- **UPG-0015:** Stage `platform.noetfield.com` DNS record — document blocker if any
- **UPG-0016:** Document cloud ship vs GEL repo boundary in PRODUCT_TRUTH
- **UPG-0017:** Add production URL table to doc 010 §6 — update after cutover
- **UPG-0018:** Create `scripts/check_production_urls.sh` — curl smoke for www + gc7lm
- **UPG-0019:** Wire check script into CI or pre-release checklist
- **UPG-0020:** Capture before/after E2E report JSON in vault exports folder

### 1.3 Demo & proof assets

- **UPG-0021:** Script `scripts/demo-gel-5min-v1.sh` — gate → decide → portal export
- **UPG-0022:** Add BLOCK case to demo script — corridor DTI decline path
- **UPG-0023:** Add tamper-FAIL step — mutate export hash · show verification fail
- **UPG-0024:** Add replay step — same request_id → deterministic outcome
- **UPG-0025:** Time demo script — assert total <300s on clean machine
- **UPG-0026:** Write demo speaker notes — `docs/demo/GEL_5MIN_SPEAKER_NOTES_v1.md`
- **UPG-0027:** Export demo intent JSON fixtures — `fixtures/demo_intents/`
- **UPG-0028:** Add `--sample-block` flag to `noetfield decide` CLI
- **UPG-0029:** Record screen capture with speaker notes timing markers
- **UPG-0030:** Publish demo video link in doc 011 and doc 013 (when ready)

### 1.4 Vault & strategy hygiene

- **UPG-0031:** Run `check_noetfield_business_strategy.sh` — green
- **UPG-0032:** Run `check_noos_agent_docs.sh` — all NOOS-AGENT-DOC tags valid
- **UPG-0033:** Resolve ASF pending steps 0009–0010 or document deferral
- **UPG-0034:** Update ROADMAP_MANIFEST notes with UPG plan reference
- **UPG-0035:** Add UPG-014 to AGENTS.md read order for build tasks
- **UPG-0036:** Reconcile PRODUCT_TRUTH test count with pytest output
- **UPG-0037:** Pin Python 3.12 in `.python-version` or README
- **UPG-0038:** Document `pip install -e .` requires Python ≥3.11 + setuptools≥68
- **UPG-0039:** Add CONTRIBUTING section for UPG step completion PR format
- **UPG-0040:** Create `docs/_NOOS_AGENT/UPGRADE_CHANGELOG.md` — log completed UPG batches

### 1.5 Pre-deploy GEL checklist

- **UPG-0041:** Audit `requirements.txt` pins — no floating versions
- **UPG-0042:** Add `Dockerfile` for GEL — single-stage, non-root user
- **UPG-0043:** Add `docker-compose.yml` — GEL + optional Postgres stub
- **UPG-0044:** Health probe script for container — `/readiness` exit 0
- **UPG-0045:** Document env vars — `NOETFIELD_API_KEY`, `DB_PATH`, policy paths
- **UPG-0046:** Add `.env.example` without secrets
- **UPG-0047:** Verify `run.py` binds `0.0.0.0:8001` for container deploy
- **UPG-0048:** Load-test smoke — 100 sequential `/v1/decision` under 30s local
- **UPG-0049:** Document minimum RAM/CPU for pilot sandbox
- **UPG-0050:** Phase 1 exit review — NW1+SW1 sent · demo on disk · deploy checklist ready

---

## Phase 2 — GEL Core Hardening (UPG-0051–0100)

*Master map: Phase 2 remainder 0194–0200 + 0116–0160 · Weeks 3–8*

### 2.1 API contract & docs

- **UPG-0051:** Publish `docs/integration/quickstart.md` — curl + Python + CLI
- **UPG-0052:** Add curl examples for APPROVE / REVIEW / DECLINE paths
- **UPG-0053:** Export Postman collection JSON — `docs/integration/noetfield-gel-v1.postman.json`
- **UPG-0054:** Document retry policy — 503/429 exponential backoff
- **UPG-0055:** Document webhook callback pattern — client executes after APPROVE
- **UPG-0056:** Add ALLOW/DENY/ESCALATE alias table to OpenAPI description
- **UPG-0057:** Freeze `/v1/decision` request schema — changelog entry
- **UPG-0058:** Add request body max size guard (413) — Step 0116
- **UPG-0059:** Add numeric range validation at engine layer — Step 0117
- **UPG-0060:** Add decide() timeout budget — fail closed on overrun — Step 0118

### 2.2 Engine & corridor hardening

- **UPG-0061:** Refactor decide() pipeline stages with logged stage outputs — Step 0111
- **UPG-0062:** Test corridor DECLINE overrides high composite score — Step 0113
- **UPG-0063:** Test policy-only path when no corridor breach — Step 0114
- **UPG-0064:** Implement policy status enum draft/active/superseded — Step 0121
- **UPG-0065:** Reject decisions on non-active policy without override — Step 0122
- **UPG-0066:** Corridor rule priority when multiple breach — Step 0123
- **UPG-0067:** Add `policy_packs/cu_pilot_v1.json` conservative corridors
- **UPG-0068:** CLI to load alternate policy pack for demo — env `NOETFIELD_POLICY_DIR`
- **UPG-0069:** Benchmark decide() p50/p95 — 10K synthetic requests — Step 0120
- **UPG-0070:** Document latency SLO — p95 <200ms local, <500ms hosted target

### 2.3 Auth, idempotency & errors

- **UPG-0071:** Rate limit middleware — token bucket per API key — Step 0161
- **UPG-0072:** Return 429 with Retry-After header
- **UPG-0073:** Per-tenant rate limit config stub in api_keys table
- **UPG-0074:** Structured error codes enum — match OpenAPI components — Step 0186
- **UPG-0075:** Pydantic field-level validation errors in 422 body — Step 0187
- **UPG-0076:** Audit log decision=ERROR on engine failure — Step 0188
- **UPG-0077:** Runbook POLICY_LOAD_FAIL — Step 0189
- **UPG-0078:** Runbook DB unavailable fail-closed — Step 0190
- **UPG-0079:** Idempotency conflict test — duplicate request_id returns 409 + same body
- **UPG-0080:** Document idempotency window — 24h default

### 2.4 Observability & meta

- **UPG-0081:** Expand `/v1/meta` — policy hashes, version, uptime, build git sha
- **UPG-0082:** Add `/metrics` Prometheus stub — request count, latency histogram
- **UPG-0083:** Request logging middleware — request_id, tenant_id, latency_ms
- **UPG-0084:** Correlation ID propagation — X-Request-ID echo — Step 0108
- **UPG-0085:** Startup policy load log line — combined_hash + rule_set_version
- **UPG-0086:** Graceful shutdown — drain in-flight requests
- **UPG-0087:** Liveness vs readiness split documented in health.py
- **UPG-0088:** Add version to all JSON error responses
- **UPG-0089:** Integration test — full decide flow with auth + idempotency
- **UPG-0090:** pytest coverage report baseline — target ≥80% on engine module

### 2.5 Python client & TTFD

- **UPG-0091:** Ship `noetfield_gel.py` client with `decide()` wrapper — Step 0191
- **UPG-0092:** Client handles 401/409/429/503 with typed exceptions
- **UPG-0093:** Measure TTFD — new dev to first decision <15 min — Step 0200
- **UPG-0094:** Add `scripts/onboard_dev.sh` — venv + key mint + sample decide
- **UPG-0095:** TypeScript fetch wrapper example — Step 0193 — `docs/integration/decide.ts`
- **UPG-0096:** Sample fake LOS integration script — calls GEL before funding — Step 0198
- **UPG-0097:** Sample read-only bank core simulation — Step 0199
- **UPG-0098:** Contract stability pledge doc — no breaking /v1/ post first customer — Step 0110
- **UPG-0099:** OpenAPI examples for CU credit case — Step 0109
- **UPG-0100:** Phase 2 exit — all Phase 2 master steps ≤0200 mapped done or deferred with reason

---

## Phase 3 — Evidence & Trust Ledger (UPG-0101–0150)

*Master map: Phase 3 0201–0300 · Evidence is the product*

### 3.1 TLE & export hardening

- **UPG-0101:** TLE v1 schema version field + migration note
- **UPG-0102:** TLE export includes policy_pack_version + combined_hash
- **UPG-0103:** TLE export includes full factor breakdown per audit row
- **UPG-0104:** TLE export JSON schema file — `schemas/tle-v1.schema.json`
- **UPG-0105:** Validate export output against JSON schema in pytest
- **UPG-0106:** Board PDF — replace stub with branded template (logo, footer, date)
- **UPG-0107:** Board PDF — executive summary section auto-generated from audit stats
- **UPG-0108:** Board PDF — ASCII-safe unicode policy for fpdf2
- **UPG-0109:** Procurement ZIP bundle — TLE JSON + board PDF + policy hashes + README
- **UPG-0110:** `GET /portal/audits/{id}/export.zip` endpoint

### 3.2 Signing & tamper evidence

- **UPG-0111:** Define receipt signing key model — ed25519 dev keys
- **UPG-0112:** Sign TLE export payload — detached signature block
- **UPG-0113:** `scripts/verify_tle_signature.py` — PASS/FAIL exit code
- **UPG-0114:** Wire tamper-FAIL into demo — flip byte · verification fails
- **UPG-0115:** Document signing key rotation procedure
- **UPG-0116:** Store public key fingerprint in `/v1/meta`
- **UPG-0117:** Audit row includes content_hash of inputs
- **UPG-0118:** Chain hash — each audit row links to previous row hash
- **UPG-0119:** Verify chain integrity CLI — `noetfield verify-chain`
- **UPG-0120:** Map signing pattern to SourceA receipt schema — alignment doc

### 3.3 Replay & RID continuity

- **UPG-0121:** Store input snapshot JSON on every audit insert — Step 0281
- **UPG-0122:** `GET /portal/audits/by-request/{request_id}` — full replay payload
- **UPG-0123:** Replay endpoint reproduces decision without re-scoring option (read-only)
- **UPG-0124:** Replay endpoint with re-score — detect policy drift vs original
- **UPG-0125:** Document RID continuity narrative for sales — Step 0251
- **UPG-0126:** Test deterministic replay — same input + policy → same outcome
- **UPG-0127:** Test drift detection — same input + new policy → version bump flagged
- **UPG-0128:** Export includes request_id index for board pack
- **UPG-0129:** Portal UI shows policy version per row (if portal exists)
- **UPG-0130:** Add replay section to W1 demo script

### 3.4 Compliance mapping

- **UPG-0131:** Map audit fields to ISO 42001 control tags — Step 0291
- **UPG-0132:** Map audit fields to EU AI Act transparency tags — Step 0292
- **UPG-0133:** Compliance tag filter on portal export
- **UPG-0134:** Compliance appendix page in board PDF
- **UPG-0135:** PII inventory on audit payloads — Step 0271
- **UPG-0136:** Redact applicant_id option on export — Step 0275
- **UPG-0137:** Tokenize sensitive fields config flag
- **UPG-0138:** Retention policy doc — 7-year default — Step 0261
- **UPG-0139:** Legal-hold flag on audit row schema stub
- **UPG-0140:** Export manifest lists redaction mode applied

### 3.5 Postgres path (durability)

- **UPG-0141:** Postgres schema design doc — audit tables — Step 0201
- **UPG-0142:** SQLAlchemy models mirroring SQLite audit schema
- **UPG-0143:** Dual-write adapter — SQLite default, Postgres optional env
- **UPG-0144:** Migration script SQLite → Postgres one-way
- **UPG-0145:** Append-only triggers on Postgres — Step 0211
- **UPG-0146:** Test UPDATE/DELETE blocked on audit table — Step 0214
- **UPG-0147:** Connection pool + health check for Postgres readiness
- **UPG-0148:** Benchmark audit insert rate — 1K rows/s target local PG
- **UPG-0149:** Document when to switch pilot from SQLite to Postgres
- **UPG-0150:** Phase 3 exit — TLE signed · ZIP export · replay proven · PG path documented

---

## Phase 4 — Chain Tools & SDK (UPG-0151–0200)

*Master map: doc 012 chain tools + integration layer · Graphify-class publish*

### 4.1 noetfield-gate package hardening

- **UPG-0151:** PyPI package metadata polish — classifiers, project URLs
- **UPG-0152:** `noetfield gate --json` stdout mode for CI
- **UPG-0153:** `noetfield gate --strict` fails on skipped API check when URL set
- **UPG-0154:** Gate check for pytest suite passing — optional G6
- **UPG-0155:** Gate check for PRODUCT_TRUTH phase alignment
- **UPG-0156:** `noetfield decide --file` schema validation against OpenAPI
- **UPG-0157:** Receipt writes to `~/.noetfield/receipts/` with dated subfolders
- **UPG-0158:** `noetfield verify` subcommand — chain + signature + gate report
- **UPG-0159:** Integration test — gate PASS on clean repo in CI
- **UPG-0160:** Integration test — decide against live test server in CI

### 4.2 Publish & distribute

- **UPG-0161:** Publish `noetfield-gate` to TestPyPI — dry run
- **UPG-0162:** Publish `noetfield-gate` to PyPI production
- **UPG-0163:** GitHub release workflow — tag + sdist + wheel
- **UPG-0164:** 3-line README on PyPI pointing to full docs
- **UPG-0165:** npm package `@noetfield/gate` — fetch wrapper for `/v1/decision`
- **UPG-0166:** npm package typed response — DecisionReceipt interface
- **UPG-0167:** npm publish to registry — private or public per legal
- **UPG-0168:** GitHub Action example — run `noetfield gate` before agent job
- **UPG-0169:** Pre-commit hook example in docs
- **UPG-0170:** Homebrew tap stub document (future)

### 4.3 Hosted API (`api.noetfield.com`)

- **UPG-0171:** Provision `api.noetfield.com` DNS → GEL host
- **UPG-0172:** TLS cert — auto-renew
- **UPG-0173:** Deploy GEL container to production host (Fly.io / Railway / VPS)
- **UPG-0174:** Production secrets — API keys in vault, not repo
- **UPG-0175:** Production policy pack pinned — semver tagged
- **UPG-0176:** Hosted `/readiness` probed by `noetfield gate` in docs
- **UPG-0177:** Hosted rate limits — stricter than local
- **UPG-0178:** API key minting flow for design partners
- **UPG-0179:** Usage metering stub — decisions per key per day
- **UPG-0180:** Status page stub — status.noetfield.com

### 4.4 Developer experience

- **UPG-0181:** SW1 quickstart repo badge — "TTFD <5 min"
- **UPG-0182:** Devcontainer config — `.devcontainer/devcontainer.json`
- **UPG-0183:** VS Code launch config — debug `run.py`
- **UPG-0184:** Makefile — `make test`, `make gate`, `make demo`
- **UPG-0185:** API changelog — `CHANGELOG.md` semver sections
- **UPG-0186:** Breaking change policy doc
- **UPG-0187:** Design partner sandbox API key tier — lower rate limit
- **UPG-0188:** Sandbox vs production base URL env convention
- **UPG-0189:** `noetfield.com/gel` page content from doc 008 — ship or stage
- **UPG-0190:** Link gel page to PyPI + npm + quickstart

### 4.5 CI/CD for this repo

- **UPG-0191:** GitHub Actions — pytest on push
- **UPG-0192:** GitHub Actions — `check_noos_agent_docs.sh`
- **UPG-0193:** GitHub Actions — `check_noetfield_business_strategy.sh`
- **UPG-0194:** GitHub Actions — `noetfield gate` must PASS
- **UPG-0195:** Dependabot or renovate for Python deps
- **UPG-0196:** SBOM export — pip-audit or cyclonedx
- **UPG-0197:** Secret scan — gitleaks in CI
- **UPG-0198:** Release on tag — PyPI + GitHub artifacts
- **UPG-0199:** Staging environment — staging.api.noetfield.com
- **UPG-0200:** Phase 4 exit — PyPI live · hosted API smoke green · npm example runs

---

## Phase 5 — Tenant & Production (UPG-0201–0250)

*Master map: Phase 4 0301–0400 seeds · FI-ready isolation*

### 5.1 Tenant model

- **UPG-0201:** Tenant entity schema — id, name, status, created_at
- **UPG-0202:** API key maps to tenant_id — enforce on every decision
- **UPG-0203:** Audit rows scoped by tenant_id — query filter
- **UPG-0204:** Portal routes require tenant scope
- **UPG-0205:** Cross-tenant access returns 404 not 403 — no leakage
- **UPG-0206:** Tenant admin CLI — create / revoke keys
- **UPG-0207:** Tenant onboarding checklist doc for design partners
- **UPG-0208:** Default tenant for local dev — document clearly
- **UPG-0209:** Tenant-specific policy pack path option
- **UPG-0210:** Test tenant isolation — two tenants, no cross-read

### 5.2 Auth hardening

- **UPG-0211:** API key rotation — two valid keys overlap window
- **UPG-0212:** Revoked key list persisted
- **UPG-0213:** Key scopes — decide:write vs portal:read
- **UPG-0214:** Optional mTLS doc for enterprise tier
- **UPG-0215:** JWT bearer auth stub for future embed
- **UPG-0216:** Audit log auth failures without revealing key validity
- **UPG-0217:** Brute-force throttle on auth failures
- **UPG-0218:** Hash API keys at rest — bcrypt or sha256+salt
- **UPG-0219:** Never log raw API keys — lint rule
- **UPG-0220:** Security review checklist — OWASP API top 10

### 5.3 Postgres production

- **UPG-0221:** Production Postgres on hosted provider
- **UPG-0222:** Row-level security policies — Step 0321
- **UPG-0223:** RLS bypass attempt test — must fail
- **UPG-0224:** Automated backups — daily, 30-day retention
- **UPG-0225:** Point-in-time recovery documented
- **UPG-0226:** Connection string via env — never in repo
- **UPG-0227:** Read replica stub for portal export heavy queries
- **UPG-0228:** Migration runner — alembic or sql migrations folder
- **UPG-0229:** Zero-downtime migration playbook
- **UPG-0230:** Postgres readiness gate in `/readiness`

### 5.4 Reliability & SLO

- **UPG-0231:** SLO doc — 99.5% uptime pilot tier
- **UPG-0232:** Error budget policy
- **UPG-0233:** Pager/on-call runbook stub
- **UPG-0234:** Synthetic probe every 5m against `/health`
- **UPG-0235:** Alert on policy load failure
- **UPG-0236:** Alert on decide error rate >1%
- **UPG-0237:** Graceful degradation — read-only portal if write DB down
- **UPG-0238:** Circuit breaker on external deps (if any added)
- **UPG-0239:** Load test — 50 RPS sustained 5 min
- **UPG-0240:** Capacity plan — decisions/day per instance

### 5.5 Policy lifecycle

- **UPG-0241:** Policy pack upload API — admin only
- **UPG-0242:** Policy activation workflow — draft → active → superseded
- **UPG-0243:** Decisions record which policy hash was used — already partial, harden
- **UPG-0244:** Policy diff view — what changed between versions
- **UPG-0245:** Emergency rollback — reactivate previous pack
- **UPG-0246:** Policy change audit log separate from decision audit
- **UPG-0247:** Notify design partner on policy version bump webhook
- **UPG-0248:** Freeze policy during pilot option — flag
- **UPG-0249:** Export includes policy version history appendix
- **UPG-0250:** Phase 5 exit — tenant isolation proven · PG production · SLO doc live

---

## Phase 6 — Pilot Revenue & Scale (UPG-0251–0300)

*Master map: GTM execution + embed seeds + enterprise pull · doc 010 phases 1–3*

### 6.1 Design partner operations

- **UPG-0251:** Design partner agreement template — shadow mode, metric, refund clause
- **UPG-0252:** Success metric worksheet — one number agreed up front
- **UPG-0253:** Weekly pilot check-in agenda doc
- **UPG-0254:** Pilot onboarding runbook — keys, gate, first decide, export
- **UPG-0255:** Shadow mode integration guide — sidecar pattern
- **UPG-0256:** Capture "what closed them" interview template
- **UPG-0257:** Case study outline — problem, proof chain, metric, quote
- **UPG-0258:** Reference logo permission form
- **UPG-0259:** Deposit invoice / Stripe link — CAD $2K
- **UPG-0260:** Conversion to annual pricing calculator — NF-RD band

### 6.2 Second & third design partners

- **UPG-0261:** Repeat NW1 motion with proven message — approval gated
- **UPG-0262:** Repeat SW1 motion with PyPI link — approval gated
- **UPG-0263:** Score 10 new accounts on ICP rubric — doc 010 §4
- **UPG-0264:** 3 discovery calls logged — `.agent-private/`
- **UPG-0265:** Pipeline CRM minimal — spreadsheet or Notion, not n8n yet
- **UPG-0266:** CASL unsubscribe path on any sequence
- **UPG-0267:** Second paid design partner signed
- **UPG-0268:** Third design partner signed
- **UPG-0269:** 3 DPs milestone — doc 010 Phase 2
- **UPG-0270:** Raise narrative one-pager — proof + logos + metric

### 6.3 Embed & open-core seeds

- **UPG-0271:** LangGraph middleware example — call `/v1/decision` pre-node
- **UPG-0272:** CrewAI hook example
- **UPG-0273:** MCP tool wrapper — `noetfield_decide` tool spec
- **UPG-0274:** Temporal activity pattern doc — decide before side effect
- **UPG-0275:** Open-core boundary doc — what's free vs hosted
- **UPG-0276:** GitHub public mirror plan — enforcement core only
- **UPG-0277:** First external GitHub star campaign — after Eval-1 stable
- **UPG-0278:** Embed design partner conversation — orchestrator buyer
- **UPG-0279:** Partner integration checklist
- **UPG-0280:** SI channel seed list — Phase 3 prep only

### 6.4 Enterprise readiness (pull-only)

- **UPG-0281:** SOC 2 readiness gap assessment — lightweight
- **UPG-0282:** Data processing agreement template
- **UPG-0283:** Subprocessor list doc
- **UPG-0284:** Pen test scope doc — when revenue justifies
- **UPG-0285:** BC PIPA / privacy FAQ for buyers
- **UPG-0286:** Insurance / E&O broker conversation notes
- **UPG-0287:** Enterprise security questionnaire pre-fill — 80% answers
- **UPG-0288:** VPC deploy guide — customer-managed option
- **UPG-0289:** SLA draft — annual tier only
- **UPG-0290:** Do not start SOC 2 audit until enterprise pull — guard doc

### 6.5 Exit & continuity

- **UPG-0291:** PRODUCT_TRUTH update — phase, tests, gaps at UPG-0300
- **UPG-0292:** Master roadmap sync — mark mapped master steps complete
- **UPG-0293:** UPGRADE_MANIFEST.json — ≥200/300 complete or waived
- **UPG-0294:** W3 economic signal — CAD ≥2K deposited
- **UPG-0295:** NW1 deal signal — first design partner reference
- **UPG-0296:** SW2 signal — first Buyer 1 credit card (SourceA lane) tracked
- **UPG-0297:** Record retrospective — what worked in 300 plan
- **UPG-0298:** Draft next 300 plan (UPG-0301+) or resume master 0501+
- **UPG-0299:** Council brief — proof density delivered yes/no
- **UPG-0300:** **Plan exit review** — hosted GEL · signed TLE · PyPI gate · 1+ active DP · W1 on disk

---

## Appendix A — Priority queue (if blocked)

When frozen or blocked, work this order:

1. UPG-0051–0060 (docs + contract — no deploy needed)
2. UPG-0151–0160 (gate hardening — local only)
3. UPG-0101–0110 (TLE/ZIP — high buyer value)
4. UPG-0191–0194 (CI — protects everything)
5. UPG-0021–0025 (demo script — unblocks W1)

## Appendix B — Master roadmap crosswalk

| UPG phase | Master steps (approx) |
|-----------|----------------------|
| 1 | Commercial + deploy prep |
| 2 | 0194–0200, 0116–0160 |
| 3 | 0201–0300 |
| 4 | 012 chain tools + 0191–0193 |
| 5 | 0301–0400 seeds |
| 6 | GTM doc 010 phases 1–3 |

## Appendix C — Step completion format

```json
{
  "step": "UPG-0042",
  "completed_at": "2026-06-20",
  "evidence": "Dockerfile merged, CI build green",
  "agent": "noetfeld-os-cursor-chat"
}
```

Append completed entries to `UPGRADE_MANIFEST.json` → `completed_steps` array.

---

*End of 300-step upgrade plan. Next review: when UPG-0050 or first design partner signs.*
