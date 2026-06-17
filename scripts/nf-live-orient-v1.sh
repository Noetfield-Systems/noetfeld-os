#!/usr/bin/env bash
# nf-live-orient-v1.sh — single live snapshot for Noetfield agents (anti-staleness)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
JSON=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json) JSON=true ;;
    -h|--help)
      echo "Usage: bash scripts/nf-live-orient-v1.sh [--json]"
      exit 0
      ;;
    *) echo "Unknown: $1" >&2; exit 2 ;;
  esac
  shift
done

EVENTS="$ROOT/reports/agent-auto/events"
OUT="$ROOT/reports/agent-auto/LIVE-STATUS.md"
mkdir -p "$EVENTS"

bash scripts/nf_routing_card.sh --json >"$EVENTS/nf-live-routing-v1.json" 2>/dev/null || true
python3 scripts/nf_stale_guard_v1.py --json >"$EVENTS/nf-stale-guard-v1.json" 2>/dev/null || true
python3 scripts/nf_session_gate_run_v1.py --json >"$EVENTS/nf-session-gate-v1.json" 2>/dev/null || true

AT="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

python3 - "$ROOT" "$OUT" "$AT" <<'PY'
import json, sys
from pathlib import Path

root, out_path, at = sys.argv[1:4]
events = Path(root) / "reports/agent-auto/events"

def load(name):
    p = events / name
    if not p.is_file():
        return {}
    try:
        return json.loads(p.read_text())
    except Exception:
        return {}

routing = load("nf-live-routing-v1.json")
stale = load("nf-stale-guard-v1.json")
gate = load("nf-session-gate-v1.json")

pending = routing.get("pending_task") or {}
git_info = routing.get("git") or {}

lines = [
    "---",
    "agent_tag: nf-local-repo-agent",
    f"generated_at: {at}",
    "author: nf-live-orient-v1.sh",
    "type: live-snapshot",
    "do_not_edit_by_hand: refresh via make nf-live-orient",
    "---",
    "",
    "# LIVE STATUS — Noetfield (machine snapshot)",
    "",
    f"**Generated:** {at} UTC · **Law:** `docs/ops/NF_GAOS_W0_LOCKED_v1.md`",
    "",
    "> Static prose in SHIP_NOW is hints only. Re-run `make nf-live-orient` when orientation matters.",
    "",
    "## Queue head (live)",
    "",
    f"| Field | Value |",
    f"|-------|-------|",
    f"| Pending id | `{pending.get('id') or 'none'}` |",
    f"| Title | {pending.get('title') or '—'} |",
    f"| Git | `{git_info.get('branch') or '?'}` @ `{git_info.get('sha') or '?'}` |",
    "",
    "## Gates",
    "",
    f"| Gate | Value |",
    f"|------|-------|",
    f"| Session gate | {'PASS' if gate.get('ok') else 'FAIL'} |",
    f"| Context stale | {stale.get('context_stale', '?')} |",
    f"| SourceA mirror | {routing.get('sourcea_mirror', False)} |",
    "",
    "## Boot",
    "",
    "```bash",
    "make nf-onboard",
    "```",
    "",
    "## Pins",
    "",
    "- `entry/START_HERE_LOCKED_v1.md`",
    "- `ROUTING_CARD.md`",
    "- `os/NF_UNIFIED_ROUTING_GRAPH.json`",
    "",
]

if stale.get("issues"):
    lines.extend(["## Stale issues", ""])
    for issue in stale["issues"]:
        lines.append(f"- {issue}")
    lines.append("")

Path(out_path).write_text("\n".join(lines), encoding="utf-8")
print(out_path)
PY

if [[ "$JSON" == true ]]; then
  python3 - <<PY
import json
from pathlib import Path
root = Path("$ROOT")
payload = {
  "generated_at": "$AT",
  "live_status": str(root / "reports/agent-auto/LIVE-STATUS.md"),
  "events_dir": str(root / "reports/agent-auto/events"),
}
print(json.dumps(payload, indent=2))
PY
else
  echo "Wrote $OUT"
fi
