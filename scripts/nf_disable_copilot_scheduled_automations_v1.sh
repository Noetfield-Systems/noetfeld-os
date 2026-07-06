#!/usr/bin/env bash
# Record policy: all Copilot scheduled automations disabled — Kaizen + daily heartbeat own the lane.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="${ROOT}/governance/COPILOT_SCHEDULED_AUTOMATIONS_LOCKED.json"
RECEIPT="${HOME}/.sina/nf-copilot-scheduled-automations-disabled-v1.json"
TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

python3 - <<'PY' "$MANIFEST" "$RECEIPT" "$TS"
import json, sys
from pathlib import Path
manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
receipt = {
    "schema": "nf-copilot-scheduled-automations-disabled-v1",
    "at": sys.argv[3],
    "policy": manifest.get("policy"),
    "automations": manifest.get("automations", []),
    "replacement_surfaces": manifest.get("replacement_surfaces", []),
    "ok": True,
}
path = Path(sys.argv[2]).expanduser()
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
print(json.dumps(receipt, indent=2))
PY

echo "[nf-disable-copilot-scheduled] receipt → ${RECEIPT}"
echo "[nf-disable-copilot-scheduled] In Cursor: Automations → disable all scheduled Copilot agents for Noetfield."
