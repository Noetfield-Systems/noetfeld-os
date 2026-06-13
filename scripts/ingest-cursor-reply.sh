#!/usr/bin/env bash
# Noetfield — validate cursor-reply YAML then ingest to Prompt OS.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPLY="${1:-${ROOT}/reports/cursor-reply-latest.txt}"
INGEST="${HOME}/Desktop/SinaPromptOS/scripts/ingest-cursor-reply.sh"
DESKTOP_REPO="${HOME}/Desktop/Noetfield"

cd "$ROOT"

if [[ ! -f "$REPLY" ]]; then
  echo "FAIL: reply file not found: $REPLY" >&2
  exit 1
fi

python3 scripts/verify_agent_reply_yaml.py "$REPLY"

if [[ ! -x "$INGEST" ]]; then
  echo "FAIL: ingest script not found at $INGEST" >&2
  exit 1
fi

# Prompt OS mark_done reads ~/Desktop/Noetfield/os/plan.json — bridge if canonical repo is elsewhere.
if [[ -f "${ROOT}/os/plan.json" && ! -f "${DESKTOP_REPO}/os/plan.json" ]]; then
  mkdir -p "${DESKTOP_REPO}"
  ln -sfn "${ROOT}/os" "${DESKTOP_REPO}/os"
fi

"$INGEST" noetfield "$REPLY"
