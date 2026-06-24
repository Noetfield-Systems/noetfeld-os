# Agent-auto reports (NF-GAOS)

Machine-generated snapshots — **do not edit by hand**.

| Output | Refresh |
|--------|---------|
| `LIVE-STATUS.md` | `make nf-live-orient` |
| `events/nf-session-gate-v1.json` | `make nf-session-gate` |
| `events/nf-live-routing-v1.json` | `bash scripts/nf_routing_card.sh --json` |
| `events/nf-stale-guard-v1.json` | `python3 scripts/nf_stale_guard_v1.py --json` |

Boot all: `make nf-onboard`

Law: `docs/ops/NF_GAOS_W0_LOCKED_v1.md`
