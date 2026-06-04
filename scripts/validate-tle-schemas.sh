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

echo "=== validate-tle-schemas ==="

for f in \
  packages/schemas/tle-v1.schema.json \
  packages/schemas/evidence.schema.json \
  packages/schemas/connector-manifest.schema.json \
  docs/spec/openapi/tle-v1.openapi.yaml; do
  if [[ "$f" == *.yaml ]]; then
    "$PY" -c "
import sys
try:
    import yaml
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', 'pyyaml'])
    import yaml
yaml.safe_load(open('${ROOT}/${f}'))
" && echo "OK  $f"
  else
    check_json "${ROOT}/${f}"
  fi
done

"$PY" -c "
import json, sys, pathlib
try:
    import yaml
    import jsonschema
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', 'pyyaml', 'jsonschema'])
    import yaml
    import jsonschema

root = pathlib.Path('${ROOT}')
schema = json.load(open(root / 'packages/schemas/tle-v1.schema.json'))
samples = [
    'docs/spec/samples/tle-go-approved.yaml',
    'docs/spec/samples/tle-conditional.yaml',
    'docs/spec/samples/tle-rejected.yaml',
]
for rel in samples:
    data = yaml.safe_load(open(root / rel))
    jsonschema.validate(data, schema)
    print(f'OK  {rel} (schema-valid)')
"

grep -q 'Trust Ledger Entry' "${ROOT}/docs/strategy/NOETFIELD_COPILOT_TLE_V12_LOCKED.md"
grep -q 'metadata_only' "${ROOT}/docs/spec/evidence-intake-contract-v1.md"
grep -q '/evidence/ingest' "${ROOT}/docs/spec/openapi/tle-v1.openapi.yaml"
echo "OK  locked docs + contract cross-checks"
echo "All TLE schema checks passed."
