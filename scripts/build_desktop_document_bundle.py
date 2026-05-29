#!/usr/bin/env python3
"""Build Noetfield-All-Documents/ — desktop-friendly mirror of uploaded SOT + registry."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_UPLOADED = ROOT / "docs/SOURCE_OF_TRUTH/uploaded"
SRC_REGISTRY = ROOT / "docs/SOURCE_OF_TRUTH/registry"
OUT = ROOT / "Noetfield-All-Documents"


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)

    shutil.copytree(SRC_UPLOADED, OUT / "uploaded")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "registry").mkdir(parents=True, exist_ok=True)

    for name in (
        "source_document_inventory.json",
        "source_of_truth_registry.json",
        "active_rule_candidates.json",
    ):
        src = SRC_REGISTRY / name
        if src.is_file():
            shutil.copy2(src, OUT / "registry" / name)

    inventory = json.loads((SRC_REGISTRY / "source_document_inventory.json").read_text(encoding="utf-8"))
    docs = inventory.get("documents", [])
    batches = inventory.get("batches", [])

    lines = [
        "# Noetfield — All Uploaded Documents (Manifest)",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        f"- **Batches:** {len(batches)}",
        f"- **Documents:** {len(docs)}",
        "",
        "## Batch folders",
        "",
    ]
    for batch in batches:
        bid = batch.get("batch_id", "?")
        folder = batch.get("source_folder", "").replace("docs/SOURCE_OF_TRUTH/uploaded/", "")
        lines.append(f"- `{bid}` → `uploaded/{folder or bid}/`")

    lines.extend(["", "## Documents by batch", ""])
    by_batch: dict[str, list[dict]] = {}
    for doc in docs:
        by_batch.setdefault(doc.get("upload_batch", "unknown"), []).append(doc)

    for batch_id in sorted(by_batch.keys()):
        lines.append(f"### {batch_id}")
        lines.append("")
        for doc in sorted(by_batch[batch_id], key=lambda d: d.get("document_key", "")):
            rel = doc.get("source_path", "").replace("docs/SOURCE_OF_TRUTH/uploaded/", "uploaded/")
            lines.append(f"- [{doc.get('title', doc.get('document_key'))}]({rel})")
        lines.append("")

    (OUT / "MANIFEST.md").write_text("\n".join(lines), encoding="utf-8")

    readme = """# Noetfield — All Documents

This folder is a **complete mirror** of everything ingested from your uploads into the
Source of Truth registry. It is kept in sync with:

- `docs/SOURCE_OF_TRUTH/uploaded/` (all batch markdown files)
- `docs/SOURCE_OF_TRUTH/registry/` (inventory + active SOT + rules)

## On GitHub (cloud)

This folder is committed on branch `cursor/platform-blueprint-37f0` in the Noetfield repo.
Pull or browse: `Noetfield-All-Documents/` at the repository root.

## On your Desktop (local)

After cloning the repo on your Mac or PC, run from the repo root:

```bash
./scripts/sync_to_desktop.sh
```

That copies this folder to:

- **macOS / Linux:** `~/Desktop/Noetfield-All-Documents`
- **Windows (Git Bash):** `$USERPROFILE/Desktop/Noetfield-All-Documents`

Or copy manually:

```bash
cp -R Noetfield-All-Documents ~/Desktop/
```

## Refresh after new uploads

From the repo root:

```bash
python3 scripts/build_desktop_document_bundle.py
```

Then commit and push `Noetfield-All-Documents/` if you want GitHub updated too.

## Contents

| Path | Description |
|------|-------------|
| `uploaded/2026-05-batch-001` … `019` | Normalized markdown per upload batch |
| `registry/*.json` | Master inventory and active SOT decisions |
| `MANIFEST.md` | Auto-generated index of all documents |
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")

    md_count = len(list((OUT / "uploaded").rglob("*.md")))
    print(f"Wrote {OUT}")
    print(f"  markdown files: {md_count}")
    print(f"  registry files: {len(list((OUT / 'registry').glob('*.json')))}")


if __name__ == "__main__":
    main()
