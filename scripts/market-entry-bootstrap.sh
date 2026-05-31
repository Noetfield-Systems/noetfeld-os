#!/usr/bin/env bash
# One-shot setup for 30-day market entry (private ops + MSB pack).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"

echo "== bootstrap private ops =="
"${ROOT}/scripts/bootstrap-private-ops.sh"

echo "== seed MSB partner pack =="
"${ROOT}/scripts/seed-msb-partner-pack.sh"

PRIVATE_MSB="${ROOT}/ops/private/msb"
if [[ -f "${PRIVATE_MSB}/OUTREACH_TRACKER.md" ]]; then
  if ! grep -q "Primary ICP (30-day plan)" "${PRIVATE_MSB}/OUTREACH_TRACKER.md" 2>/dev/null; then
    echo "Note: re-copy templates to refresh tracker header if needed."
  fi
fi

echo ""
echo "Market entry ready."
echo "  Checklist: docs/MARKET_ENTRY_30_DAY.md"
echo "  Private:   ops/private/msb/ (emails, tracker, SOW templates)"
echo "  Pilot keys: docs/PRODUCTION_PILOT_KEYS.md"
echo "  Intake SLA: docs/INTAKE_OPS.md (+ INTAKE_OPS_WEBHOOK_URL in production)"
