#!/usr/bin/env bash
# nf_routing_card.sh — live queue head + scope summary for Noetfield agents
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
JSON=false

usage() {
  cat <<'EOF'
Usage: bash scripts/nf_routing_card.sh [OPTIONS]

  --json        Machine-readable routing card
  -h|--help     Help

Pin: ROUTING_CARD.md · Graph: os/NF_UNIFIED_ROUTING_GRAPH.json
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json) JSON=true ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown: $1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

EVENTS="$ROOT/reports/agent-auto/events"
mkdir -p "$EVENTS"

python3 scripts/nf_routing_card_v1.py --root "$ROOT" --events "$EVENTS" ${JSON:+--json}
