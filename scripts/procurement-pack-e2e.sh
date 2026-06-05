#!/usr/bin/env bash
# Procurement pack zip E2E — draft → approve → GET export?format=zip → assert contents
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"

BASE="http://127.0.0.1:${NF_DEV_PUBLIC_PORT}"
TENANT="X-Tenant-ID: procurement-e2e"
HDR=(-H "Content-Type: application/json" -H "${TENANT}" -H "X-Role: approver")

code="$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 3 "${BASE}/health" 2>/dev/null || echo "000")"
if [[ "$code" != "200" ]]; then
  echo "FAIL: dev stack not up. Run: make dev-local" >&2
  exit 1
fi

echo "=== procurement-pack-e2e ==="

DRAFT="$(curl -sS -X POST "${BASE}/tle/draft" "${HDR[@]}" \
  -d '{"evidence_ids":["EV-PURVIEW-001","EV-ENTRA-001","EV-AUDIT-001"]}')"
TLE_ID="$(echo "$DRAFT" | python3 -c "import sys,json; print(json.load(sys.stdin)['tle_id'])")"
echo "OK   draft ${TLE_ID}"

for approver in cio-001 legal-001 sec-001; do
  curl -sS -X POST "${BASE}/tle/${TLE_ID}/approve" "${HDR[@]}" \
    -d "{\"approver_id\":\"${approver}\",\"decision\":\"Approved\"}" >/dev/null
done
echo "OK   approved"

ZIP_PATH="$(mktemp -t nf-procurement-pack.XXXXXX.zip)"
trap 'rm -f "$ZIP_PATH"' EXIT
http_code="$(curl -sS -o "$ZIP_PATH" -w "%{http_code}" \
  -H "${TENANT}" "${BASE}/tle/${TLE_ID}/export?format=zip")"
if [[ "$http_code" != "200" ]]; then
  echo "FAIL: zip export HTTP ${http_code}" >&2
  exit 1
fi

python3 - "$ZIP_PATH" <<'PY'
import sys, zipfile
path = sys.argv[1]
with zipfile.ZipFile(path) as zf:
    names = set(zf.namelist())
    for required in ("board_pack.json", "board_pack.pdf", "README-procurement.txt"):
        if required not in names:
            raise SystemExit(f"missing {required} in zip")
    if not zf.read("board_pack.pdf").startswith(b"%PDF"):
        raise SystemExit("board_pack.pdf is not a PDF")
    if not zf.read("board_pack.json").strip().startswith(b"{"):
        raise SystemExit("board_pack.json invalid")
print("OK   zip contains PDF + JSON + README")
PY

echo "=== procurement-pack-e2e PASS ==="
