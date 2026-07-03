#!/usr/bin/env bash
# Fail-open L-P5 reminder before file edits (warn only, never block).
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
STATE="${ROOT}/.noos-runtime/integrator/noos-integrator-state-v1.json"

input="$(cat)"
file_path=""

if command -v python3 >/dev/null 2>&1; then
  file_path="$(python3 - <<'PY' "$input"
import json, sys
raw = sys.argv[1] if len(sys.argv) > 1 else ""
try:
    data = json.loads(raw) if raw.strip() else {}
except json.JSONDecodeError:
    data = {}
for key in ("file_path", "path", "file", "target_path", "relative_path"):
    val = data.get(key)
    if isinstance(val, str) and val.strip():
        print(val.strip())
        break
PY
)"
fi

if [ -z "$file_path" ] || [ ! -f "$STATE" ]; then
  exit 0
fi

python3 - <<'PY' "$STATE" "$file_path"
import json, sys
from pathlib import Path

state_path, target = sys.argv[1], sys.argv[2]
target = target.lstrip("./")
try:
    state = json.loads(Path(state_path).read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError):
    raise SystemExit(0)

def overlaps(scope: str, path: str) -> bool:
    scope = scope.strip().lstrip("./")
    path = path.strip().lstrip("./")
    if not scope or not path:
        return False
    if scope == path:
        return True
    if path.startswith(scope.rstrip("/") + "/"):
        return True
    if scope.startswith(path.rstrip("/") + "/"):
        return True
    return False

active = []
for task in state.get("tasks") or []:
    if not isinstance(task, dict):
        continue
    if str(task.get("status") or "") not in ("claimed", "in_progress", "blocked"):
        continue
    scopes = task.get("scope_files") if isinstance(task.get("scope_files"), list) else []
    if any(overlaps(str(s), target) for s in scopes):
        active.append(str(task.get("task_id") or task.get("agent_id") or "claim"))

if not active:
    print(
        f"[noos-claim-reminder] WARN: no integrator claim covers '{target}'. "
        "Run: bash scripts/noos_local_claim_lane_v1.sh NOOS-LANE-<id> <paths...>",
        file=sys.stderr,
    )
PY

exit 0
