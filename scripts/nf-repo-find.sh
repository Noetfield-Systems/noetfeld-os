#!/usr/bin/env bash
# nf-repo-find.sh — delegate to Mono repo capability map (read-only)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MONO="${ROOT}/../SinaaiMonoRepo"
if [[ ! -d "$MONO/scripts" ]]; then
  MONO="${ROOT}/../../SinaaiMonoRepo"
fi
if [[ -f "$MONO/scripts/repo-find.sh" ]]; then
  exec bash "$MONO/scripts/repo-find.sh" --repo noetfield "$@"
fi
echo "FAIL nf-repo-find: Mono repo-find.sh not found at $MONO" >&2
echo "fallback pins:" >&2
echo "  onboard: make nf-onboard" >&2
echo "  verify:  make verify-all-static && make verify-gtm" >&2
echo "  graph:   make nf-unified-routing" >&2
exit 1
