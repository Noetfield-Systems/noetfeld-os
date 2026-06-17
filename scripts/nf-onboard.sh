#!/usr/bin/env bash
# nf-onboard.sh — Noetfield NF-GAOS session boot ladder
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

ROLE="${1:-cloud}"
JSON=false
shift || true

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json) JSON=true ;;
    --role) ROLE="$2"; shift 2; continue ;;
    -h|--help)
      echo "Usage: bash scripts/nf-onboard.sh [cloud|local] [--json]"
      echo "       make nf-onboard | make nf-onboard-local"
      exit 0
      ;;
    *) echo "Unknown: $1" >&2; exit 2 ;;
  esac
  shift
done

if [[ "$ROLE" == "local" ]]; then
  export NOETFIELD_AGENT_ID="${NOETFIELD_AGENT_ID:-noetfield_local}"
  echo "=== nf-onboard LOCAL ==="
  echo "agent: $NOETFIELD_AGENT_ID"
  echo "law: docs-only — do not edit product git from All-Documents chat"
  echo "read: ROUTING_CARD.md § Local"
  python3 scripts/nf_session_gate_run_v1.py --role local --json || true
  exit 0
fi

export NOETFIELD_AGENT_ID="${NOETFIELD_AGENT_ID:-noetfield_cloud}"
FAIL=0

echo "=== nf-onboard CLOUD ==="
echo "step 1/6 session gate"
python3 scripts/nf_session_gate_run_v1.py --role cloud --json || FAIL=1

echo "step 2/6 live orient"
bash scripts/nf-live-orient-v1.sh || FAIL=1

echo "step 3/6 routing card"
bash scripts/nf_routing_card.sh --json > /dev/null

echo "step 4/6 stale guard"
python3 scripts/nf_stale_guard_v1.py --json || FAIL=1

echo "step 5/6 voyage integrity"
python3 scripts/nf_voyage_integrity_v1.py --json || FAIL=1

echo "step 6/6 panel export"
bash scripts/nf-panel-export-v1.sh || true

if [[ "$JSON" == true ]]; then
  python3 - <<PY
import json
from pathlib import Path
root = Path("$ROOT")
events = root / "reports/agent-auto/events"
def load(n):
    p = events / n
    return json.loads(p.read_text()) if p.is_file() else {}
print(json.dumps({
  "schema_version": "nf-onboard-v1",
  "ok": $FAIL == 0,
  "agent_id": "$NOETFIELD_AGENT_ID",
  "gate": load("nf-session-gate-v1.json"),
  "stale": load("nf-stale-guard-v1.json"),
  "voyage": load("nf-voyage-integrity-v1.json"),
  "routing": load("nf-live-routing-v1.json"),
  "live_status": "reports/agent-auto/LIVE-STATUS.md",
}, indent=2))
PY
fi

echo ""
echo "Read: reports/agent-auto/LIVE-STATUS.md"
echo "Pin:  ROUTING_CARD.md"
echo "Panel: http://127.0.0.1:8780/ → Noetfield tab"
echo "Next: ASK founder or proceed with explicit implement order"

exit "$FAIL"
