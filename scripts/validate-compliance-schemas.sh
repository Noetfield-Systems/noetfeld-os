#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${ROOT}/.venv/bin/python3"
if [[ ! -x "$PY" ]]; then
  PY=python3
fi

check_json() {
  local f="$1"
  "$PY" -c "import json; json.load(open('$f'))" && echo "OK  $f"
}

echo "=== validate-compliance-schemas ==="
for f in \
  packages/schemas/policy.schema.json \
  packages/schemas/governance.schema.json \
  packages/schemas/control.schema.json \
  packages/schemas/risk.schema.json \
  packages/schemas/agent-manifest.schema.json \
  packages/schemas/rag-answer.schema.json \
  docs/spec/samples/copilot-oversharing-policy.json \
  docs/spec/samples/evidence-retention-policy.json \
  packages/policy-packs/copilot-governance-v1.json \
  packages/policy-packs/bank-pilot-v1.json \
  docs/spec/workflows/CopilotQuickScan.workflow.json \
  docs/spec/workflows/CopilotReadiness.workflow.json; do
  check_json "${ROOT}/${f}"
done

if [[ -f "${ROOT}/docs/spec/samples/governance-copilot-v1.yaml" ]]; then
  grep -q 'policy_pack: copilot-governance-v1' "${ROOT}/docs/spec/samples/governance-copilot-v1.yaml"
  echo "OK  docs/spec/samples/governance-copilot-v1.yaml"
fi

grep -q 'COP-DLP-001' "${ROOT}/docs/spec/copilot-control-catalog.md"
grep -qi 'append-only' "${ROOT}/docs/spec/copilot-control-catalog.md"
echo "OK  copilot-control-catalog.md"
echo "All compliance schema checks passed."
