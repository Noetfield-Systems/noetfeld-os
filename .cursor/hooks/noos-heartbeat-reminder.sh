#!/usr/bin/env bash
# Fail-open heartbeat reminder after file edits when claim is aging (warn only).
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
STATE="${ROOT}/.noos-runtime/integrator/noos-integrator-state-v1.json"

input="$(cat)"

python3 - <<'PY' "$STATE" "$input"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

state_path = sys.argv[1]
raw = sys.argv[2] if len(sys.argv) > 2 else ""

def parse_iso(ts):
    if not ts:
        return None
    text = str(ts).strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text).astimezone(timezone.utc)
    except ValueError:
        return None

if not Path(state_path).is_file():
    raise SystemExit(0)

try:
    state = json.loads(Path(state_path).read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError):
    raise SystemExit(0)

now = datetime.now(timezone.utc)
warn_mins = 20

for task in state.get("tasks") or []:
    if not isinstance(task, dict):
        continue
    if str(task.get("status") or "") not in ("claimed", "in_progress", "blocked"):
        continue
    hb = parse_iso(task.get("heartbeat_at") or task.get("claimed_at"))
    if not hb:
        continue
    age_m = (now - hb).total_seconds() / 60.0
    if age_m >= warn_mins:
        tid = task.get("task_id") or "UNKNOWN"
        print(
            f"[noos-heartbeat-reminder] WARN: claim '{tid}' heartbeat age {int(age_m)}m. "
            f"Run: make local-heartbeat TASK={tid}",
            file=sys.stderr,
        )
PY

exit 0
