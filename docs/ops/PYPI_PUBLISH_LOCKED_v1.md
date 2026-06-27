# PYPI PUBLISH — noetfield-gate — LOCKED v1

**Status:** READY (awaiting PyPI credentials / trusted publisher)  
**Package:** `noetfield-gate` v0.1.0  
**Date:** 2026-06-26

---

## One-time PyPI setup (pick one)

### A — Trusted publishing (recommended)

1. Create/login at https://pypi.org
2. Register project name `noetfield-gate` (first upload claims it)
3. **Account → Publishing → Add trusted publisher**
   - Owner: `kazemnezhadsina144-dot`
   - Repository: `noetfeld-os`
   - Workflow: `publish-pypi.yml`
   - Environment: `pypi` (prod) / `testpypi` (TestPyPI)
4. GitHub repo → Settings → Environments → create `pypi` and `testpypi`
5. Run: **Actions → Publish PyPI → Run workflow** (target: `test` then `prod`)

Or tag release `v0.1.0` → auto-publish to production.

### B — API token (local script)

1. https://pypi.org/manage/account/token/ → scope: entire account or project
2. Add to `~/.sina/secrets.env`:
   ```
   PYPI_API_TOKEN=pypi-AgEI...
   PYPI_TEST_API_TOKEN=pypi-AgEN...   # optional TestPyPI dry run
   ```
3. Run:
   ```bash
   cd ~/Projects/noetfeld-os
   bash scripts/publish-gate-pypi.sh test   # UPG-0161
   bash scripts/publish-gate-pypi.sh prod    # UPG-0162
   ```

---

## Local validate (no upload)

```bash
cd ~/Projects/noetfeld-os
pip install build twine
python -m pytest -q tests/test_noetfield_gate.py
python -m build
python -m twine check dist/*
```

## Post-publish verify

```bash
pip install noetfield-gate
noetfield gate
curl -sS https://pypi.org/pypi/noetfield-gate/json | python3 -m json.tool | head
```

**Locked by:** noetfeld-os-cursor-chat
