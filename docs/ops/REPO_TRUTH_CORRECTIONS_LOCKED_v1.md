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

**Rule:** disk wins · machine validators are truth.
