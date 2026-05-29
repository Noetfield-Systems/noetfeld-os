# Noetfield — All Documents

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
