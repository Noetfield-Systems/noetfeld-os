#!/usr/bin/env bash
# nf-unified-routing.sh — print NF unified routing graph + live summary
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
JSON=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json) JSON=true ;;
    -h|--help)
      echo "Usage: bash scripts/nf-unified-routing.sh [--json]"
      exit 0
      ;;
    *) echo "Unknown: $1" >&2; exit 2 ;;
  esac
  shift
done

GRAPH="$ROOT/os/NF_UNIFIED_ROUTING_GRAPH.json"
if [[ ! -f "$GRAPH" ]]; then
  echo "FAIL missing $GRAPH" >&2
  exit 1
fi

bash scripts/nf_routing_card.sh --json >"$ROOT/reports/agent-auto/events/nf-live-routing-v1.json" 2>/dev/null || true

if [[ "$JSON" == true ]]; then
  python3 - <<PY
import json
from pathlib import Path
root = Path("$ROOT")
graph = json.loads((root / "os/NF_UNIFIED_ROUTING_GRAPH.json").read_text())
live = {}
p = root / "reports/agent-auto/events/nf-live-routing-v1.json"
if p.is_file():
    live = json.loads(p.read_text())
print(json.dumps({"graph": graph, "live": live}, indent=2))
PY
else
  echo "=== NF Unified Routing Graph ==="
  python3 - <<PY
import json
from pathlib import Path
g = json.loads(Path("os/NF_UNIFIED_ROUTING_GRAPH.json").read_text())
print(g.get("one_sentence", ""))
print("")
for n in g.get("nodes", []):
    print(f"  {n['id']}: {n['label']}")
print("")
print("Boot: make nf-onboard")
print("Ladder: see routing_ladder in os/NF_UNIFIED_ROUTING_GRAPH.json")
PY
fi
