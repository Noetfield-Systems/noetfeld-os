#!/usr/bin/env bash
# deploy_noos_deadman_cf_v1.sh — Phase B deadman CF worker (*/30 cron)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORKER_DIR="$ROOT/cloud/workers/noos-deadman-v1"
CONFIG_SRC="$ROOT/data/noos-deadman-config-v1.json"
INTERVALS_DST="$WORKER_DIR/src/loop-intervals.json"

python3 - <<'PY' "$ROOT" "$CONFIG_SRC" "$INTERVALS_DST"
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
config_src = Path(sys.argv[2])
intervals_dst = Path(sys.argv[3])
loops = json.loads((root / "data/noos-24-7-loops-v1.json").read_text())
dispatch = json.loads((root / "data/noos-cf-dispatch-table-v1.json").read_text())
rows = {}
for loop in loops.get("loops") or []:
    lid = str(loop["id"])
    rows[lid] = {
        "loop_id": lid,
        "event_type": loop.get("event_type"),
        "interval_minutes": int(loop.get("interval_minutes") or 5),
    }
for target in dispatch.get("targets") or []:
    if target.get("handler") == "factory":
        rows["factory_autorun"] = {
            "loop_id": "factory_autorun",
            "event_type": target.get("event_type"),
            "interval_minutes": int(target.get("interval_minutes") or 10),
        }
intervals_dst.write_text(json.dumps(rows, indent=2) + "\n")
(config_src.read_text())
PY

cp "$CONFIG_SRC" "$WORKER_DIR/src/deadman-config.json"

cd "$WORKER_DIR"

echo "== Deadman Telegram lane verify (blocks @Gateway_A and generic TELEGRAM_* env) =="
if [[ -n "${DEADMAN_TELEGRAM_BOT_TOKEN:-}" ]]; then
  python3 "$ROOT/scripts/verify_noos_deadman_telegram_lane_v1.py" --fail-on-forbidden || {
    echo "FAIL: Telegram lane blocked. Use a dedicated deadman bot — NEVER @Gateway_A or NF Probe Bot." >&2
    exit 1
  }
else
  echo "WARN: DEADMAN_TELEGRAM_BOT_TOKEN not in shell — skipping local lane verify (send_alerts=false in config until founder enables)"
fi

for key in NOETFIELD_SUPABASE_URL SUPABASE_URL NOETFIELD_SUPABASE_SERVICE_ROLE_KEY SUPABASE_SERVICE_ROLE_KEY \
  LOOP_RUNNER_URL LOOP_RUNNER_SECRET; do
  val="${!key:-}"
  if [[ -n "$val" ]]; then
    printf '%s' "$val" | wrangler secret put "$key" || {
      echo "FAIL: wrangler secret put $key" >&2
      exit 1
    }
  fi
done

if [[ "${ALLOW_DEADMAN_TELEGRAM_SECRET_UPLOAD:-}" == "1" ]]; then
  echo "== Uploading DEADMAN_TELEGRAM_* (opt-in only) =="
  for key in DEADMAN_TELEGRAM_BOT_TOKEN DEADMAN_TELEGRAM_CHAT_ID; do
    val="${!key:-}"
    if [[ -n "$val" ]]; then
      python3 "$ROOT/scripts/verify_noos_deadman_telegram_lane_v1.py" --fail-on-forbidden
      printf '%s' "$val" | wrangler secret put "$key" || exit 1
    fi
  done
else
  echo "SKIP: DEADMAN_TELEGRAM_* secret upload (default off — prevents wrong-bot spam)"
fi

wrangler deploy

echo "OK deployed noos-deadman-v1"
echo "Health: curl -fsS https://noos-deadman-v1.sina-kazemnezhad-ca.workers.dev/health"
echo "Probe:  curl -X POST 'https://noos-deadman-v1.sina-kazemnezhad-ca.workers.dev/check?telegram=0'"
