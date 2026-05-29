#!/usr/bin/env bash
# Copy Noetfield-All-Documents to the user's Desktop (run on your Mac/PC after git clone).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${REPO_ROOT}/Noetfield-All-Documents"

if [[ ! -d "$SRC" ]]; then
  echo "Bundle missing. Building from Source of Truth..."
  python3 "${REPO_ROOT}/scripts/build_desktop_document_bundle.py"
fi

if [[ "$(uname -s)" == "MINGW"* ]] || [[ "$(uname -s)" == "MSYS"* ]] || [[ -n "${WINDIR:-}" ]]; then
  DEST="${USERPROFILE}/Desktop/Noetfield-All-Documents"
else
  DEST="${HOME}/Desktop/Noetfield-All-Documents"
fi

mkdir -p "$(dirname "$DEST")"
rm -rf "$DEST"
cp -R "$SRC" "$DEST"

echo "Copied to: $DEST"
echo "Open that folder on your Desktop to browse all uploaded documents."
