#!/usr/bin/env bash
# Package gitignored ops/private for manual cloud handoff (tarball — do not commit).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAMP="$(date +%Y%m%d)"
OUT="${HOME}/Desktop/noetfield-ops-private-handoff-${STAMP}.tar.gz"

cd "${ROOT}"
if [[ ! -d ops/private ]]; then
  echo "FAIL: ops/private not found under ${ROOT}" >&2
  exit 1
fi

tar -czf "${OUT}" ops/private
echo "OK  created: ${OUT}"
echo "    size: $(du -h "${OUT}" | awk '{print $1}')"
echo ""
echo "Cloud handoff options:"
echo "  1) Cloud agent on THIS Mac with root ~/Desktop/Noetfield — no upload; ops/private already on disk."
echo "  2) Remote cloud VM — attach this tarball to cloud agent chat, or extract in cloud workspace if you have SSH."
echo "  3) Paste the handoff block from docs/ops/NOETFIELD_AGENT_TEAM_SYNC_LOCKED_v1.md (committed bridge)."
