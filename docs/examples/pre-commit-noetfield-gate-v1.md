# Pre-commit hook example — `noetfield gate` (UPG-0169)

Optional local gate before commit. Install is **not** mandatory for NOOS contributors.

## Using pre-commit framework

Save as `.pre-commit-config.yaml` in your repo root (copy this snippet):

```yaml
repos:
  - repo: local
    hooks:
      - id: noetfield-gate
        name: noetfield gate
        entry: noetfield gate
        language: system
        pass_filenames: false
        stages: [commit]
```

Install once:

```bash
pip install pre-commit noetfield-gate
pre-commit install
```

## Plain git hook (no pre-commit package)

`.git/hooks/pre-commit`:

```bash
#!/usr/bin/env bash
set -euo pipefail
noetfield gate
```

```bash
chmod +x .git/hooks/pre-commit
```

Gate writes `~/.noetfield/gate-report-v1.json` on every run. See https://www.noetfield.com/gel/ for policy details.
