#!/usr/bin/env bash
# TLE v1 smoke: schema file present + example YAML parses (no API required).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCHEMA="$ROOT/docs/spec/schemas/tle-v1.schema.yaml"
EXAMPLES="$ROOT/docs/spec/examples"
fail() { echo "tle-smoke: $*" >&2; exit 1; }

[[ -f "$SCHEMA" ]] || fail "missing $SCHEMA"
shopt -s nullglob
yaml_files=("$EXAMPLES"/tle-v1-*.yaml)
[[ ${#yaml_files[@]} -gt 0 ]] || fail "no tle-v1-*.yaml under $EXAMPLES"

if command -v python3 >/dev/null 2>&1; then
  python3 - "$SCHEMA" "${yaml_files[@]}" <<'PY'
import sys
from pathlib import Path
try:
    import yaml
except ImportError:
    print("tle-smoke: PyYAML not installed — checking files exist only")
    for p in sys.argv[2:]:
        Path(p).read_text(encoding="utf-8")
    sys.exit(0)
schema_path = Path(sys.argv[1])
schema_path.read_text(encoding="utf-8")
for p in sys.argv[2:]:
    data = yaml.safe_load(Path(p).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"not a mapping: {p}")
    for key in ("tle_id", "status"):
        if key not in data:
            raise SystemExit(f"missing {key} in {p}")
print(f"tle-smoke: OK ({len(sys.argv) - 2} example(s))")
PY
else
  for f in "${yaml_files[@]}"; do [[ -s "$f" ]] || fail "empty $f"; done
  echo "tle-smoke: OK (${#yaml_files[@]} example(s), python3 unavailable — size check only)"
fi
