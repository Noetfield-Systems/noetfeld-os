<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260627-016
doc_type: STUDIO_SUPABASE_BOUNDARY
workspace_root: /Users/sinakazemnezhad/Projects/noetfeld-os
classification: INTERNAL — Studio lane boundary handoff
-->

# Studio Supabase Boundary

## Locked Rule

Noetfield Studio-owned operational data must use only the Noetfield Supabase project.

| Field | Value |
|---|---|
| Studio repo | `~/Desktop/Noetfield/noetfield-studio-ide/` |
| Supabase project | `noetfield` |
| Supabase ref | `tkgpapowwplupyekpivy` |
| Supabase URL | `https://tkgpapowwplupyekpivy.supabase.co` |
| Studio boundary module | `src/lib/noetfield-supabase-boundary.ts` |
| Studio SQL policy | `supabase/noetfield-studio-boundary.sql` |

## Authority Split

- SourceA registry remains authority for ecosystem ownership.
- SourceA/Forge operational tables remain outside Studio runtime data paths.
- Studio must not use `portfolio-spine` tables for Noetfield-owned data.
- Cross-project integration is async only: signed webhook, signed event row, or status token.

## Implementation Handoff

If a future Noetfield OS agent touches Studio data:

1. Work in `~/Desktop/Noetfield/noetfield-studio-ide/`, not this GEL runtime repo.
2. Use the Studio boundary module before any Supabase client creation.
3. Keep Noetfield Studio tables in the `noetfield` schema with tenant/org RLS.
4. Run `npm run boundary:check` and `npm test` in the Studio repo.
