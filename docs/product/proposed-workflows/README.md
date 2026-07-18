# Proposed workflows (founder-gated registration required)

These workflows are delivered ready-to-activate but are NOT live governed
workflows. Adding a workflow under `.github/workflows/` requires registering it
in `data/noos-parallel-agent-registry-v1.json`, which is an **L5-frozen registry
(founder gate)**. The machine does not edit it.

## supabase-migrate-v1.yml

Narrow, additive-only Supabase migration gated on the protected `production`
environment. Exact founder activation:

1. Move to `.github/workflows/supabase-migrate-v1.yml`.
2. Register it in `data/noos-parallel-agent-registry-v1.json` (founder gate).
3. Merge to the default branch (founder gate).
4. `gh workflow run supabase-migrate-v1.yml -f migration=0021_software_repair_runway.sql`
5. Approve the pending `production` environment gate.

Until then, the schema (migration `0021_software_repair_runway.sql`) is
`PROTECTED_ENVIRONMENT_APPROVAL_REQUIRED`.
