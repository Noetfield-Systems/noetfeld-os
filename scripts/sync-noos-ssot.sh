#!/usr/bin/env bash
# Sync locked Noetfield SSOT from canonical All-Documents into noetfeld-os vault.
set -euo pipefail

CANON="/Users/sinakazemnezhad/Desktop/Noetfield/Noetfield-All-Documents"
VAULT="/Users/sinakazemnezhad/Desktop/Noetfield-Systems/noetfeld-OS/docs/_NOOS_AGENT"
ROOT="/Users/sinakazemnezhad/Desktop/Noetfield-Systems/noetfeld-OS"

for f in NOETFIELD_OS_SSOT_v1_LOCKED.md NOETFIELD_UNIFIED_MASTER_v1_LOCKED.md; do
  cp "$CANON/$f" "$VAULT/$f"
  echo "OK: synced $f"
done

# Fix Part 8 sync command in vault master (canonical path is All-Documents, not SourceA).
python3 - <<'PY'
from pathlib import Path
path = Path("/Users/sinakazemnezhad/Desktop/Noetfield-Systems/noetfeld-OS/docs/_NOOS_AGENT/NOETFIELD_UNIFIED_MASTER_v1_LOCKED.md")
text = path.read_text(encoding="utf-8")
old = """**Sync command (run after any update to SourceA Noetfield docs):**
```bash
cp ~/Desktop/SourceA/NOETFIELD_UNIFIED_MASTER_v1_LOCKED.md \\
   ~/Desktop/Noetfield-Systems/noetfeld-OS/docs/_NOOS_AGENT/NOETFIELD_UNIFIED_MASTER_v1_LOCKED.md

cp ~/Desktop/SourceA/NOETFIELD_OS_SSOT_v1_LOCKED.md \\
   ~/Desktop/Noetfield-Systems/noetfeld-OS/docs/_NOOS_AGENT/NOETFIELD_OS_SSOT_v1_LOCKED.md
```"""
new = """**Sync command (canonical: Noetfield-All-Documents):**
```bash
bash ~/Desktop/Noetfield-Systems/noetfeld-OS/scripts/sync-noos-ssot.sh
```"""
if old in text:
    path.write_text(text.replace(old, new), encoding="utf-8")
PY

bash "$ROOT/scripts/check_noos_agent_docs.sh"
