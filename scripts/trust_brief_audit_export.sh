#!/usr/bin/env bash
# Fetch governance audit-export for a RID (Trust Brief / Shadow deliverable).
set -euo pipefail
PLATFORM="${PLATFORM:-https://platform.noetfield.com}"
RID=""
OUT_DIR="."

usage() {
  echo "Usage: $0 --request-id RID-... [--out dir] [--platform URL]" >&2
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --request-id) RID="${2:-}"; shift 2 ;;
    --out) OUT_DIR="${2:-.}"; shift 2 ;;
    --platform) PLATFORM="${2:-}"; shift 2 ;;
    -h|--help) usage ;;
    *) echo "Unknown arg: $1" >&2; usage ;;
  esac
done

[[ -n "$RID" ]] || usage
mkdir -p "$OUT_DIR"

AUTH=()
if [[ -n "${PILOT_KEY:-}" ]]; then
  AUTH=(-H "Authorization: Bearer $PILOT_KEY")
elif [[ -n "${GOVERNANCE_PILOT_API_KEYS:-}" ]]; then
  first="${GOVERNANCE_PILOT_API_KEYS%%,*}"
  secret="${first#*:}"
  secret="${secret//[[:space:]]/}"
  [[ -n "$secret" ]] && AUTH=(-H "Authorization: Bearer $secret")
fi

safe_name="${RID//\//_}"
out_file="$OUT_DIR/audit-export-${safe_name}.json"

curl -fsSL "${AUTH[@]}" \
  "$PLATFORM/api/v1/governance/audit-export?request_id=$(python3 -c "import urllib.parse; print(urllib.parse.quote('''$RID'''))")" \
  -o "$out_file"

echo "Wrote $out_file"
python3 -m json.tool "$out_file" | head -40
