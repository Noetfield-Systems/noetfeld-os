# Noetfield repo instructions

- Operate in this repository only (`Noetfield-Systems/Noetfield`).
- Follow `repo-policy.json` and run `python3 scripts/check_repo_policy.py` after policy/config changes.
- Keep cross-repo coordination contract-based only (contracts, exports, manifests, APIs, receipts).
- Do not add active implementation work for TrustField, VIRLUX, noetfeld-os runtime, or studio-ide in this repo.
- Prefer safe, repo-local updates; preserve historical evidence documents unless a task explicitly asks to rewrite history.

## Forbidden active-config markers

The following legacy slug must not appear in active configuration:

- `kazemnezhadsina144-dot`
