#!/usr/bin/env bash
# nf-bavt-run.sh — BAVT gate summary for Noetfield
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
FAST=false
JSON=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fast) FAST=true ;;
    --json) JSON=true ;;
    -h|--help) echo "Usage: bash scripts/nf-bavt-run.sh [--fast] [--json]"; exit 0 ;;
    *) echo "Unknown: $1" >&2; exit 2 ;;
  esac
  shift
done

FAIL=0
RESULTS=()

run_gate() {
  local id="$1"
  shift
  if "$@" >/dev/null 2>&1; then
    RESULTS+=("$id:PASS")
  else
    RESULTS+=("$id:FAIL")
    FAIL=1
  fi
}

run_gate session_gate python3 scripts/nf_session_gate_run_v1.py --json
run_gate voyage_integrity python3 scripts/nf_voyage_integrity_v1.py --json
run_gate voyage_live_wire bash scripts/verify-nf-voyage-ai-live-wire-v1.sh
run_gate semantic_drift python3 scripts/nf_semantic_drift_v1.py --json
run_gate stale_guard python3 scripts/nf_stale_guard_v1.py --json

if [[ "$FAST" != true ]]; then
  run_gate agent_scope ./scripts/verify-agent-scope.sh
fi

AT="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
python3 - "$ROOT" "$AT" "$FAIL" "${RESULTS[@]}" <<'PY'
import json, sys
from pathlib import Path
root, at, fail = sys.argv[1], sys.argv[2], int(sys.argv[3])
results = sys.argv[4:]
gates = []
for r in results:
    k, v = r.split(":", 1)
    gates.append({"id": k, "ok": v == "PASS"})
payload = {
    "schema_version": "nf-bavt-run-v1",
    "generated_at": at,
    "ok": fail == 0,
    "gates": gates,
    "strategy": "os/NF_BAVT_STRATEGY.json",
}
events = Path(root) / "reports/agent-auto/events"
events.mkdir(parents=True, exist_ok=True)
(events / "nf-bavt-run-v1.json").write_text(json.dumps(payload, indent=2) + "\n")
print(json.dumps(payload, indent=2))
PY

exit "$FAIL"
