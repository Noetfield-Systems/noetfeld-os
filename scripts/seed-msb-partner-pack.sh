#!/usr/bin/env bash
# Copy committed MSB commercial templates into gitignored ops/private/msb/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${ROOT}/ops/templates/msb"
DEST="${ROOT}/ops/private/msb"
mkdir -p "${DEST}"

if [[ ! -d "${SRC}" ]]; then
  echo "Missing ${SRC}"
  exit 1
fi

cp -f "${SRC}"/*.md "${DEST}/"
echo "Seeded MSB partner pack → ${DEST}/"
echo "Files:"
ls -1 "${DEST}"
