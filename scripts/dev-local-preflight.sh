#!/usr/bin/env bash
# Ensure .venv exists before dev-local (fixes asyncpg / connection refused after failed start).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
chmod +x "${ROOT}/scripts/dev-python.sh" 2>/dev/null || true

need_bootstrap() {
  [[ ! -x "${ROOT}/.venv/bin/python3" ]] && return 0
  ! "${ROOT}/scripts/dev-python.sh" -c "import asyncpg" 2>/dev/null && return 0
  return 1
}

if need_bootstrap; then
  echo "=== Preflight: installing Python/npm deps (make bootstrap) ==="
  make bootstrap
fi

if ! "${ROOT}/scripts/dev-python.sh" -c "import asyncpg" 2>/dev/null; then
  echo "FAIL: .venv still missing asyncpg after bootstrap" >&2
  exit 1
fi
echo "OK  preflight (.venv ready)"
