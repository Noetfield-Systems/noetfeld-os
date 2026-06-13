---
agent_tag: nf-local-repo-agent
agent_display: "[NF-LOCAL-REPO-AGENT]"
authored_at: "2026-06-06"
doc_id: noetfield-1000-prompt-library-locked-v1
---

> **Authored by:** [NF-LOCAL-REPO-AGENT] — 2026-06-06

# Noetfield 1000 prompt library (LOCKED v1)

**Trigger:** `PLAN WITH NO ASF`  
**Library:** `os/plan-library/noetfield-1000/`  
**Registry:** `os/plan-library/noetfield-1000/REGISTRY.json` (1000 prompt-ready entries)  
**Generic stubs (history):** `os/plans/nf-future-*` — do not regenerate with `generate-future-plans.py`

---

## Pick next prompt

```bash
cd ~/Desktop/Noetfield
make pick-no-asf-plan
# or
python3 scripts/pick-noetfield-no-asf-plan.py --tier T0 --limit 1 --prompt
```

## Implement one turn (no fluff)

1. Copy **Agent prompt** from picked `nf-XXXX.md` file
2. Implement minimal scope for that task only
3. `make verify-gtm` (or verify command in prompt)
4. Set `status: done` in prompt front matter
5. `reports/cursor-reply-latest.txt` — `agent_tag` + `reported_at` YAML
6. `~/Desktop/SinaPromptOS/scripts/ingest-cursor-reply.sh noetfield reports/cursor-reply-latest.txt`
7. `./scripts/sync-sourceA-desktop.sh`
8. `python3 scripts/sync-noetfield-plans-status.py` (optional nf-future mirror)

## Validate library

```bash
make validate-noetfield-1000
```

## Regenerate (sources changed)

```bash
make generate-noetfield-1000
make sync-noetfield-plans-status
```

---

## Phase map (10 × 4 × 25 = 1000)

| Phase | Focus |
|-------|--------|
| phase-0-ship-ops | Ingest, self-audit, verify-gtm, agent tagging |
| phase-1-tle-core | Drift Contract v0, evaluate-vs-TLE, risk_summary |
| phase-2-evidence-connectors | M365 mock, evidence hash, connectors UX |
| phase-3-workspace-enterprise | Workspace diligence, RBAC, exports |
| phase-4-agents-automation | Copilot pilot E2E, ai-automation, static GTM |
| phase-5-knowledge-rag | Policy/RAG research — no over-build |
| phase-6-compliance-scale | Citations, controls, drift metrics docs |
| phase-7-pilot-gtm | Design partner, demo, procurement, homepage |
| phase-8-staging-prod | demo-url, staging-smoke, observability |
| phase-9-ecosystem-bridge | SourceA sync, global lane, cloud/local parity |

---

## Source validation

| File | Role |
|------|------|
| `SOURCES_INDEX.yaml` | Authority paths + exists_on_disk |
| `VALIDATION_MATRIX.md` | Critics, shipped waves, world-model T3 |
| `LOCKED_MANIFEST.md` | Grid proof + stats |

---

## Global hub

Lane registered in `~/.cursor/plans/no-asf-library/` — see `repo_lanes.noetfield` in global `REGISTRY.json`.

**Do not** edit `[NF-CLOUD-AGENT]` authored sections in other LOCKED docs.
