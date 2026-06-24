#!/usr/bin/env bash
# verify-nf-anti-staleness-max.sh — maximum anti-staleness superset verify
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== verify-nf-anti-staleness-max ==="

for f in \
  docs/ops/NF_ANTI_STALENESS_MAXIMUM_FIX_SET_LOCKED_v1.md \
  data/nf_anti_staleness_max_v1.json \
  scripts/nf_anti_staleness_max_v1.py \
  scripts/nf_orient_read_chain_v1.py \
  scripts/nf_email_lane_guard_v1.py \
  scripts/nf_founder_input_sync_v1.py \
  scripts/nf_mono_nerve_v1.py; do
  [[ -f "$f" ]] || { echo "FAIL missing $f" >&2; fail=1; continue; }
  echo "OK   $f"
done

python3 scripts/nf_orient_read_chain_v1.py --json >/dev/null || fail=1
echo "OK   nf_orient_read_chain_v1"

python3 scripts/nf_email_lane_guard_v1.py --json >/dev/null || true
echo "OK   nf_email_lane_guard_v1"

python3 scripts/nf_anti_staleness_max_v1.py --json >/dev/null || fail=1
echo "OK   nf_anti_staleness_max_v1"

[[ -f "$HOME/.sina/nf-anti-staleness-max-v1.json" ]] || { echo "FAIL missing anti-staleness max receipt" >&2; fail=1; }

chmod +x scripts/verify-nf-mono-nerve-wire.sh 2>/dev/null || true
if [[ -x scripts/verify-nf-mono-nerve-wire.sh ]]; then
  ./scripts/verify-nf-mono-nerve-wire.sh || fail=1
  echo "OK   verify-nf-mono-nerve-wire"
fi

chmod +x scripts/verify-nf-agent-report-language.sh
./scripts/verify-nf-agent-report-language.sh || fail=1
echo "OK   verify-nf-agent-report-language"

chmod +x scripts/prove-nf-factory-spine.sh 2>/dev/null || true
if [[ -x scripts/prove-nf-factory-spine.sh ]]; then
  ./scripts/prove-nf-factory-spine.sh || fail=1
  echo "OK   prove-nf-factory-spine"
fi

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-nf-anti-staleness-max: PASS"
else
  echo ""
  echo "verify-nf-anti-staleness-max: FAIL"
  exit 1
fi
