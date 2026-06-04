# SHIP NOW — Noetfield

**ASF directive:** Ship from `os/plan.json`. Ingest = send answer to system (required). Do not edit SinaPromptOS.

## Active queue (`next_tasks`)

Empty — Next Wave 023–027 shipped. Pull new tasks from sprint or founder order.

## Latest wave (shipped 2026-06-04)

| ID | Outcome |
|----|---------|
| nf-pilot-p1-9-023 | `scripts/copilot-pilot-e2e.sh` + `/copilot/pilot/` |
| nf-pdf-board-pack-024 | `GET /tle/{id}/export?format=pdf` + workspace PDF link |
| nf-m365-oauth-025 | Connector OAuth mock + `/workspace/connectors` |
| nf-workspace-rbac-026 | `X-Role` / `NF_DEV_ROLE` viewer vs approver |
| nf-staging-deploy-027 | `docs/ops/STAGING_DEMO.md` + `scripts/staging-smoke.sh` |

## Already shipped

TLE v1 APIs, `/workspace`, sample report, `tle-smoke`, M365 stub script, procurement, agent read locks, `AGENT_READ_LINKS_LOCKED_v1.md`.

## Verify

```bash
make dev-local && make verify-local-dev && make tle-smoke
make copilot-pilot-e2e
pytest governance-console/backend/tests/test_tle_flow.py -q
```
