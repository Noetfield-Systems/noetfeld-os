<!--
NOOS-AGENT-DOC
agent_id: claude-code-noos
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260715-001
doc_type: FOUNDER_CHECKLIST
workspace_root: /Users/sinakazemnezhad/Desktop/Noetfield-Systems/noetfeld-OS
lock_state: DRAFT_v1
status: SUBMITTED for independent verification
canon_version: FOUNDER_CANON_v1+MACHINE_LOOPS_v1
-->

# Motor Repair + Event-Based Redesign — Founder Checklist v1

**Plan:** `/Users/sinakazemnezhad/.claude/plans/indexed-yawning-tome.md`
**Lane:** `repair/motor-heartbeat-decouple-v1` · **Date:** 2026-07-15

## Why this document exists

Every code-only fix from the plan is landed and committed on
`repair/motor-heartbeat-decouple-v1` (5 commits, 20 new tests, full suite
green). What's left touches `data/*.json` registries, a Supabase migration,
or an account-level setting — all explicitly founder-gated per CLAUDE.md's
L5 rule and this repo's Supabase-migration rule. Nothing below has been
applied. Everything is prepared, verified where verifiable without
production access, and waiting on you.

## 1. Fix 6 — Deadman restart budget (config-only, zero code)

**File:** `data/noos-deadman-config-v1.json` — one line:
```diff
-  "restart_attempts_max": 1,
+  "restart_attempts_max": 5,
```
Zero code change required — both the live CF worker
(`cloud/workers/noos-deadman-v1/src/index.js`) and the tested Python mirror
(`scripts/noos_deadman_v1.py`, see `tests/test_noos_deadman_v1.py
::test_restart_attempts_capped`) already implement "cap at N" correctly via
array slicing. With 14 targets at 30-min cadence, this bounds a full-fleet
outage to ~90 min to fully clear instead of up to ~7 hours. After editing,
redeploy: `bash scripts/deploy_noos_deadman_cf_v1.sh`.

**Do NOT flip `telegram_lane.send_alerts` to `true` in the same edit** —
that specific field is `LOCKED_v1` under
`docs/_NOOS_AGENT/[NOOS-AGENT-20260706-031]_DEADMAN_TELEGRAM_LANE_LOCKED_v1.md`
and needs its own separate checklist (below, §6).

## 2. Fix 7 — Incident logging (Supabase migration + code, prepared but uncommitted)

Two files exist on disk, **not committed**:
- `infrastructure/supabase/migrations/0019_noos_incident_log.sql` — creates
  `noos_incident_log` (id, occurred_at, source, loop_id, event_type,
  severity, message, detail, run_id), RLS enabled, service_role-only —
  follows the exact pattern already used for `noos_loop_registry` /
  `noos_deadman_runs` in `0016_noos_loop_registry.sql` +
  `0017_enable_rls_machine_tables.sql`.
- `scripts/noos_incident_log_v1.py` — one fail-open `log_incident()` helper
  (broad `except Exception` deliberate — logging must never crash the
  caller). Not yet imported anywhere; the two intended call sites
  (`execute_loop()` in `scripts/noos_loop_runner_v1.py` on any non-success
  state, and the `except Exception` block already added to
  `ops/railway/noos-loop-runner/server.py do_POST` — see that file's
  `TODO(repair fix 7...)` comment) are ready to re-wire in a follow-up
  commit once the migration is applied.

**To apply:** review the migration SQL, run it via your existing Supabase
migration flow (`supabase db push` or equivalent — check for a
migration-runner script/Makefile target first), then say the word and I'll
land the two call-site diffs in a normal commit (they're ordinary Python,
not gated — only the migration itself needed your review).

## 3. Event Phase 1a — GitHub App webhook activation (account-level)

On `github.com/settings/apps/noetfield-motor` (org App settings):
1. Toggle **Webhook: Active**.
2. **Webhook URL:** `https://noos-loop-github-events-v1.sina-kazemnezhad-ca.workers.dev/webhook/github`
   (worker code is committed on the lane branch; deploying it is §5 below).
3. **Webhook secret:** generate a new random secret (e.g.
   `openssl rand -hex 32`). This becomes `MOTOR_APP_WEBHOOK_SECRET` — store
   it in `~/.noetfield-secrets/` alongside `MOTOR_APP_PRIVATE_KEY` (same
   custody pattern documented in `noetfield-org/MACHINE_IDENTITY_BINDING_v1.md`),
   and also add it as a GitHub Actions secret (`MOTOR_APP_WEBHOOK_SECRET`)
   on this repo so the existing gated deploy workflow can pick it up.
4. **Subscribe to events:** `push`, `workflow_run`, `issues`,
   `pull_request` — cheap to subscribe to all four now even though Phase 1's
   rule table only maps two (`push`, `workflow_run`); avoids a second
   round-trip through this settings screen later.

This is the exact action the org's own binding doc already anticipated:
*"the App's webhook is registered inactive... Activating the event-driven
brain later is an App-settings toggle, not a re-registration."*

## 4. Event Phase 2 — Supabase Database Webhook for the inbox queue (project-level)

Supabase Dashboard → Database → Webhooks → Create a new hook:
- **Table:** `noetfield_worker_inbox_queue`
- **Events:** `INSERT` only
- **Type:** HTTP Request, **Method:** `POST`
- **URL:** `https://noos-loop-runner-production.up.railway.app/loop`
- **HTTP Headers:** `Content-Type: application/json`,
  `X-NOOS-Loop-Secret: <the same NOOS_LOOP_SECRET value already in use>`
- **HTTP Body:** static JSON —
  `{"event_type": "noos_inbox_loop_tick", "dispatch_id": "inbox", "handler": "loop", "source": "supabase_db_webhook"}`
- **Timeout:** 5000ms

`cloud_inbox_worker_v1.py`'s drain always re-queries top-priority pending
regardless of which row triggered it — no code change needed on the Railway
side. After creating it, tell me and I'll (a) insert a real test row to
confirm the round-trip, and (b) write the audit receipt
`receipts/proof/noos-supabase-db-webhook-inbox-v1.json` (dashboard config
has no git artifact otherwise).

## 5. Deploying Event Phase 1 (needs §3's secret first)

Once `MOTOR_APP_WEBHOOK_SECRET` exists (§3), either:
- Push to `main` — the existing `deploy-noos-cloud-workers-v1.yml` picks it
  up automatically as a new conditional step (already skips cleanly today
  since the secret isn't set yet), gated by the workflow's existing
  `environment: production` founder-reviewer requirement, or
- Run locally: `make loop-github-events-deploy` (needs
  `MOTOR_APP_WEBHOOK_SECRET` + `NOOS_LOOP_SECRET` in your shell env).

Then verify: `make verify-github-webhook-receiver` (signs a synthetic
SourceA push, confirms the worker dispatched it, polls
`noos_loop_registry` to confirm the downstream tick actually landed).

## 6. Deadman Telegram alert activation (separate, already-LOCKED checklist)

Not part of this repair pass — flagging because Fix 6 (§1) makes the
deadman more effective at self-healing, which is the prerequisite this
LOCKED doc's own checklist names before the alert flip makes sense:
1. Provision a dedicated Telegram bot (never `Gateway_A`/`NFProbeBot`/
   `NoetfieldOpsBot` — hard-blocked in `validateTelegramLane()`).
2. Set `DEADMAN_TELEGRAM_BOT_TOKEN` / `DEADMAN_TELEGRAM_CHAT_ID`, redeploy
   with `ALLOW_DEADMAN_TELEGRAM_SECRET_UPLOAD=1 bash scripts/deploy_noos_deadman_cf_v1.sh`.
3. `python3 scripts/verify_noos_deadman_telegram_lane_v1.py --fail-on-forbidden`.
4. Only then flip `telegram_lane.send_alerts` to `true` in
   `data/noos-deadman-config-v1.json` and redeploy.

## 7. Event Phase 3 + 4 — trigger registry + cadence demotion (bundle as one PR)

Not yet drafted as a diff (holding until §3/§4 are actually live, so the
registry entries describe real infrastructure rather than aspirational
ones). When ready: 3 new `"kind": "event"` entries in
`data/trigger-registry-v1.json`, 2 new probe types in
`scripts/sandbox_health_sweep_v1.py` (fetch-only-worker and
receipt-file-backed — neither type exists yet, so these two registry
entries would otherwise show spurious sweep failures), and per-target
`interval_minutes` demotion in `data/noos-cf-dispatch-table-v1.json`
(`inbox` 5→20 min, `sourcea_observe` 30→60 min — only these two, the other
12 targets have no verified event source in this pass). All `data/*.json`
— will be a PR for your review, never a direct commit.

## Status summary

| Item | State |
|---|---|
| Repair fixes 1–5 (root cause + hardening) | **Landed**, 5 commits, 20 tests, on `repair/motor-heartbeat-decouple-v1` |
| Repair fix 6 (deadman budget) | Prepared above (§1) — 1-line diff, your call |
| Repair fix 7 (incident logging) | Prepared on disk, uncommitted (§2) — needs migration review |
| Event Phase 1 (webhook receiver code) | **Landed** on the lane branch — needs §3 (secret) + deploy (§5) |
| Event Phase 2 (inbox DB webhook) | Checklist ready (§4) |
| Event Phase 3+4 (registry + cadence) | Deferred until §3/§4 live (§7) |

LAWS: FOUNDER_CANON v1 + governed-autorun v3. Violations = BLOCKED_WITH_REASON.
