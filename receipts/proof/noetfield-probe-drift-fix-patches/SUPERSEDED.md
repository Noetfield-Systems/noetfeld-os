# Superseded — do not apply

Probe drift loop fix is already on Noetfield `main` (`ae9bb11` — `scripts/sync-probe-expected-sha.sh`).

This patch conflicts on apply.

**Use instead:**

- Pull Noetfield `main`
- `bash scripts/sync-probe-expected-sha.sh "$(curl -sS https://platform.noetfield.com/api/public/chat/health | python3 -c "import json,sys; print(json.load(sys.stdin)['git_sha'])")"`

See `receipts/proof/noos-nf-probe-drift-fix-handoff-v1.json`.
