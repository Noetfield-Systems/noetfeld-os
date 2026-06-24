#!/usr/bin/env bash
# verify-nf-gaos-w2.sh — W2 production ship lane (light default · heavy optional)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== verify-nf-gaos-w2 ==="

for f in \
  docs/ops/NF_GAOS_W2_LOCKED_v1.md \
  docs/ops/NF_GAOS_W2_UPGRADE_10_STEP_LOCKED_v1.md \
  docs/ops/NF_VERIFY_TIERS_LOCKED_v1.md; do
  [[ -f "$f" ]] || { echo "FAIL missing $f" >&2; fail=1; continue; }
  echo "OK   $f"
done

./scripts/verify-nf-gaos-w1.sh || fail=1

if grep -q 'verify-all-tiers' Makefile && grep -q 'verify-nf-gaos-w2' Makefile; then
  echo "OK   Makefile tier + W2 targets"
else
  echo "FAIL Makefile missing verify-all-tiers or verify-nf-gaos-w2" >&2
  fail=1
fi

if [[ -f docs/schemas/agent-manifest.schema.json ]] && grep -qF 'agent-manifest.schema.json' start/index.html 2>/dev/null; then
  echo "OK   ship-058 agent manifest on /start/"
else
  echo "FAIL ship-058 missing agent-manifest wire on /start/" >&2
  fail=1
fi

if [[ "${NF_W2_VERIFY_FULL:-}" == "1" ]]; then
  echo "== NF_W2_VERIFY_FULL: running verify-all-tiers + verify-final-lock =="
  make verify-all-tiers || fail=1
  make verify-final-lock || fail=1
  make verify-nf-gaos-w3 || fail=1
else
  echo "SKIP heavy tier bundle (set NF_W2_VERIFY_FULL=1 for full W2)"
fi

if [[ -n "${PLATFORM_HEALTH_BASE:-}" ]]; then
  echo "== platform smoke: ${PLATFORM_HEALTH_BASE} =="
  PLATFORM_HEALTH_BASE="${PLATFORM_HEALTH_BASE}" ./scripts/deploy_platform_smoke.sh || fail=1
else
  echo "SKIP platform smoke (PLATFORM_HEALTH_BASE unset — Steps 3–4 pending)"
fi

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-nf-gaos-w2: PASS"
  exit 0
fi
echo ""
echo "verify-nf-gaos-w2: FAIL" >&2
exit 1
