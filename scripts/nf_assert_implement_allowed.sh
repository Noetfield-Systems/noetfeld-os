#!/usr/bin/env bash
# Fail-closed before first implement edit — mono nerve + cascade + founder implement.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

REQUIRE="${NF_FOUNDER_IMPLEMENT:-}"
if [[ "$REQUIRE" != "1" && "$REQUIRE" != "true" && "$REQUIRE" != "yes" ]]; then
  echo "EXECUTION DENIED: set NF_FOUNDER_IMPLEMENT=1 for implement" >&2
  exit 1
fi

python3 scripts/nf_mono_nerve_v1.py --json >/dev/null || {
  echo "EXECUTION DENIED: nf-mono-nerve FAIL — run make nf-onboard" >&2
  exit 1
}

python3 scripts/nf_founder_input_sync_v1.py --json >/dev/null || {
  echo "EXECUTION DENIED: founder-input disk sync FAIL" >&2
  exit 1
}

python3 scripts/nf_orient_read_chain_v1.py --json >/dev/null || {
  echo "EXECUTION DENIED: orient read chain incomplete" >&2
  exit 1
}

python3 scripts/nf_email_lane_guard_v1.py --json >/dev/null || true
if [[ -n "${NF_EMAIL_LANE_EDIT:-}" ]]; then
  NF_EMAIL_LANE_EDIT=1 python3 scripts/nf_email_lane_guard_v1.py --json >/dev/null || {
    echo "EXECUTION DENIED: email lane edit blocked while defer ON" >&2
    exit 1
  }
fi

python3 scripts/nf_stale_guard_v1.py --json >/dev/null || {
  echo "EXECUTION DENIED: context stale — run make nf-onboard" >&2
  exit 1
}

python3 scripts/nf_receipt_cascade_v1.py --json >/dev/null || {
  echo "EXECUTION DENIED: receipt cascade FAIL — run make nf-onboard" >&2
  exit 1
}

export NF_FOUNDER_IMPLEMENT=1
python3 scripts/nf_gatekeeper_v1.py --json --require-implement >/dev/null || {
  echo "EXECUTION DENIED: gatekeeper FAIL — read reports/agent-auto/events/nf-gatekeeper-v1.json" >&2
  exit 1
}

echo "OK: safe to implement"
