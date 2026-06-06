#!/usr/bin/env bash
# Prefer repo .venv so make dev-local works without manual activate.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -x "${ROOT}/.venv/bin/python3" ]]; then
  exec "${ROOT}/.venv/bin/python3" "$@"
fi
exec python3 "$@"
