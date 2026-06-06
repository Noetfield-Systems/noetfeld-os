# SKILL-002 — Pre-commit audit

**When:** After `git add`, before `git commit`.

## Steps

1. `git diff --cached --name-only` — list staged files.
2. Reject if staged paths include:
   - `ops/private/`
   - `docs/internal/`
3. Run `./scripts/verify-agent-scope.sh` — must exit 0.
4. Scan staged diff for forbidden strings (script covers tracked files; also check commit message):

| Forbidden in commit msg / diff | Block |
|--------------------------------|-------|
| trustfield.ca | yes |
| TrustField UPG-003/004/011 implementation | yes |
| VENDOR_DILIGENCE_PACK (TrustField) | yes |
| "deploy TrustField" / "TrustField Vercel" | yes |

5. Confirm commit tag: `[NF-CLOUD-AGENT]` or `[NF-LOCAL-AGENT]` when agent-authored.

## On FAIL

- Do not commit.
- If boundary crossed: file incident per SKILL-004.
- Revert wrong files: `git restore --staged <path>`.

## On PASS

- Proceed with commit.
- Note in session report: `pre_commit_audit: PASS`.
