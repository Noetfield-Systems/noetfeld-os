#!/usr/bin/env bash
# verify-nf-gaos-w1.sh — W1 full NF-GAOS verify bundle
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== verify-nf-gaos-w1 ==="

./scripts/verify-nf-gaos-w0.sh || fail=1
./scripts/verify-nf-anti-fragmentation-v1.sh || fail=1
python3 scripts/nf_voyage_integrity_v1.py --json >/dev/null || fail=1
bash scripts/nf-bavt-run.sh --fast --json >/dev/null || fail=1
./scripts/verify-agent-scope.sh || fail=1
python3 scripts/nf_governance_unify_v1.py --scan --json >/dev/null || fail=1

[[ -f docs/ops/NF_GAOS_W1_LOCKED_v1.md ]] || { echo "FAIL missing NF_GAOS_W1_LOCKED_v1.md" >&2; fail=1; }

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-nf-gaos-w1: PASS"
  exit 0
fi
echo ""
echo "verify-nf-gaos-w1: FAIL" >&2
exit 1
