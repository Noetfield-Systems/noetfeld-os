---
agent_tag: nf-local-repo-agent
agent_display: "[NF-LOCAL-REPO-AGENT]"
authored_at: "2026-06-08"
doc_id: repo-truth-corrections-locked-v1
---

> **Authored by:** [NF-LOCAL-REPO-AGENT] — 2026-06-08

# REPO_TRUTH corrections (Noetfield)

When chat claims disagree with disk, append a row here **and** to gitignored `ops/private/agent-reference/REPO_TRUTH_CORRECTIONS.md` on founder Mac.

| Date (UTC) | Claim (chat) | Disk truth | Evidence path |
|------------|--------------|------------|---------------|
| 2026-06-08 | Phase-0 ship ops batch | Implemented via PLAN WITH NO ASF phase-0 plan | `os/plan-library/noetfield-1000/REGISTRY.json` |
| 2026-06-10 | Full evaluate-vs-TLE ML platform | Partial: `POST /tle/diff/evaluate` + Drift Contract v0; not customer MLOps | `governance-console/backend/services/tle_service.py`, `docs/spec/PHASE_1_DRIFT_CONTRACT_v0_NOTE.md` |
| 2026-06-28 | Noetfield OS still Phase 1 local-only on `:8000` | Superseded by product truth: noetfeld-os is Phase 3, local port `8001`, Railway `gel-api`, hosted `api.noetfield.com` | `~/Projects/noetfeld-os/docs/_NOOS_AGENT/PRODUCT_TRUTH.md`, `docs/ops/NOETFIELD_OWNERSHIP_SYNC_CHARTER_LOCKED_v1.md` |
| 2026-06-28 | `api.noetfield.com` expected fail / future backlog | Superseded by execution receipt and inventory: `api.noetfield.com` is live on Railway `gel-api`; PyPI/npm/chatbot later phases remain open | `docs/ops/CLOUD_INVENTORY_LOCKED_v1.md`, `docs/ops/NOETFIELD_CLOUD_ORGANIZE_MASTER_PLAN_LOCKED_v1.md` |
| 2026-06-28 | `os/plan.json` queue prose is fresher than live status | Machine live status wins when timestamps differ; current live snapshot says no pending `next_tasks`, gate OK, context not stale | `reports/agent-auto/LIVE-STATUS.md`, `governance/OPS_LIVE_STATUS_LOCKED.json` |
| 2026-06-28 | Vercel project is `noetfield-systems/www` | Current www source/deploy truth is Vercel team `the-777-foundation`, project `noetfield`, GitHub `Noetfield-Systems/Noetfield` on `main` | `docs/ops/VERCEL_WWW_DEPLOY_LOCKED_v1.md`, `docs/ops/CLOUD_INVENTORY_LOCKED_v1.md` |
| 2026-06-28 | Public chat executive overview fixed by page copy / FAQ edit alone | False; live chat truth spans widget, Vercel proxy, public knowledge, platform retrieval, tests, deploy, and live smoke. Stale positioning existed in `data/chatbot/knowledge/positioning.md`; validator now fails closed. | `docs/ops/PUBLIC_CHAT_BEHAVIOR_RCA_AND_TRACKING_v1.md`, `scripts/verify-public-chat-truth.sh`, `tests/unit/test_chat_scenarios.py` |

**Rule:** disk wins · machine validators are truth.
