#!/usr/bin/env bash
# nf-panel-export-v1.sh — refresh events JSON for Routing Panel :8780
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p reports/agent-auto/events

python3 scripts/nf_session_gate_run_v1.py --json >/dev/null 2>&1 || true
bash scripts/nf-live-orient-v1.sh >/dev/null 2>&1 || true
python3 scripts/nf_voyage_integrity_v1.py --json >/dev/null 2>&1 || true
python3 scripts/nf_stale_guard_v1.py --json >/dev/null 2>&1 || true
bash scripts/nf_routing_card.sh --json >/dev/null 2>&1 || true

echo "nf-panel-export: events refreshed under reports/agent-auto/events/"
