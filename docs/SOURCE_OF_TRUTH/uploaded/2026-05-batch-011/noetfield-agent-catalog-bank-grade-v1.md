# Noetfield Agent Catalog — Bank-Grade

Document key: `noetfield-agent-catalog-bank-grade-v1`

Microservice agents with scoped permissions, auditable outputs, policy guards. Humans are the only
production-change authority.

## Agent roster

| Agent | Role | Can execute production? |
| Ingest | Normalize sources → events | No |
| Lineage | Provenance graph | Registry write only |
| Snapshot | Signed evidence snapshots | HSM sign, WORM store |
| Drift | Trajectory, slope, AUC | Alerts only |
| Risk | Risk(t), priority | Propose only |
| Decision | Ranked recommendations | Propose + Evidence Pack |
| Remediation | Playbooks (non-exec) | Flagged scripts only |
| Audit | Evidence Pack assembly | HSM sign, read-only publish |
| Orchestrator | Schedule, throttle, policy | Control plane only |
| Monitor | Health, adaptive thresholds | Propose tuning |
| Gatekeeper assistant | Triage payloads for UI | Cannot sign |
| Executor | Safe-zone automation | **Disabled by default**; multi-sig |

Every agent action emits `agent_event` with manifest_sha256 into the event store.
