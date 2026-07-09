# Noetfield L8 semantic drift — apply patch (Mac)

**Do not use** `noetfield-voyage-drift-patches/` (superseded; conflicts with Noetfield main).

## Prerequisites

- Noetfield clone: `~/Desktop/Noetfield-Systems/Noetfield`
- noetfeld-os clone: `~/Desktop/Noetfield-Systems/noetfeld-OS` (this patch lives here)
- `VOYAGE_API_KEY` in Mac vault (for verify steps)

## Apply (zsh-safe — no globs)

```bash
cd ~/Desktop/Noetfield-Systems/noetfeld-OS && git pull origin main

cd ~/Desktop/Noetfield-Systems/Noetfield
git fetch origin && git checkout main && git pull origin main
git checkout -B cursor/nf-semantic-drift-closeout-72f6 origin/main

git am ~/Desktop/Noetfield-Systems/noetfeld-OS/receipts/proof/noetfield-semantic-drift-closeout/0001-feat-L8-semantic-drift-anchors-hybrid-chatbot-retrie.patch

git push -u origin cursor/nf-semantic-drift-closeout-72f6
```

Open PR on `Noetfield-Systems/Noetfield`: base `main`, head `cursor/nf-semantic-drift-closeout-72f6`.

## Verify (after patch)

```bash
make nf-voyage-ai-wire    # NOT nf-voyage-live-wire
make nf-semantic-drift
make nf-voyage-integrity
```

## GHA alternative (no Mac push)

In **noetfeld-os** → Actions → **Noetfield open PR from patch** → Run workflow.

Requires org secret `NOETFIELD_GITHUB_TOKEN` with push to `Noetfield-Systems/Noetfield`.
