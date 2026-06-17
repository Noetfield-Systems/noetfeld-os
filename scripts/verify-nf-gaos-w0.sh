#!/usr/bin/env bash
# verify-nf-gaos-w0.sh — smoke W0 NF-GAOS spine
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== verify-nf-gaos-w0 ==="

for f in \
  entry/START_HERE_LOCKED_v1.md \
  ROUTING_CARD.md \
  docs/ops/NF_GAOS_W0_LOCKED_v1.md \
  os/NF_UNIFIED_ROUTING_GRAPH.json \
  scripts/nf_session_gate_run_v1.py \
  scripts/nf-live-orient-v1.sh \
  scripts/nf_routing_card.sh \
  scripts/nf_routing_card_v1.py \
  scripts/nf-onboard.sh \
  scripts/nf-unified-routing.sh \
  scripts/nf_stale_guard_v1.py; do
  if [[ -f "$f" ]]; then
    echo "OK   $f"
  else
    echo "FAIL missing $f" >&2
    fail=1
  fi
done

python3 scripts/nf_session_gate_run_v1.py --json >/dev/null || fail=1
echo "OK   session gate"

bash scripts/nf-live-orient-v1.sh >/dev/null || fail=1
echo "OK   live orient"

[[ -f reports/agent-auto/LIVE-STATUS.md ]] || fail=1
echo "OK   LIVE-STATUS.md"

bash scripts/nf-unified-routing.sh --json >/dev/null || fail=1
echo "OK   unified routing json"

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-nf-gaos-w0: PASS"
  exit 0
fi
echo ""
echo "verify-nf-gaos-w0: FAIL" >&2
exit 1
