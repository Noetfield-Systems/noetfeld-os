#!/usr/bin/env bash
# Automated E2E without Docker: SQLite API + httpx smoke.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$ROOT/backend"
E2E="$ROOT/e2e"
DB_FILE="$BACKEND/.e2e_governance.db"
export DATABASE_URL="sqlite:///${DB_FILE}"
export API_URL="http://127.0.0.1:8000"
export WEB_URL="${WEB_URL:-}"

rm -f "$DB_FILE"

cd "$BACKEND"
python3 -m pip install -q -r requirements.txt
python3 -m pip install -q -r "$E2E/requirements.txt"

python3 -m uvicorn main:app --host 127.0.0.1 --port 8000 &
API_PID=$!
trap 'kill $API_PID 2>/dev/null; rm -f "$DB_FILE"' EXIT

sleep 2
export API_URL
if [[ -n "$WEB_URL" ]]; then
  export WEB_URL
  python3 "$E2E/smoke.py"
else
  python3 - <<'PY'
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "e2e"))
os.environ.setdefault("API_URL", "http://127.0.0.1:8000")
# API-only smoke when web not running
import httpx
import time

api = os.environ["API_URL"].rstrip("/")
deadline = time.time() + 60
while time.time() < deadline:
    try:
        if httpx.get(f"{api}/health", timeout=3).status_code == 200:
            break
    except Exception:
        time.sleep(1)
else:
    raise SystemExit("API health timeout")

r = httpx.post(
    f"{api}/evaluate",
    json={
        "actor": "e2e:local",
        "action": "read_audit",
        "context": "local automated smoke without docker",
    },
    timeout=30,
)
r.raise_for_status()
rid = r.json()["rid"]
httpx.get(f"{api}/audit/{rid}", timeout=15).raise_for_status()
print("API-only E2E passed.", rid)
PY
fi

echo "e2e-local: OK"
