# Projects — do not mix

| Project | What it is | This repo / chat? |
|---------|------------|-------------------|
| **TrustField Technologies** | Parent company — execution, partnerships, corporate ops | **This Cursor chat** — scope work here unless the user names another product |
| **Noetfield** | Separate product — governance execution infrastructure | **No** — not in scope for this chat; own repo and deploy (`www.noetfield.com`, `platform.noetfield.com`) |
| **VIRLUX** | Separate product — Canadian B2B FX / payments | **No** — separate codebase; notes only under [`todolist/external/virlux/`](todolist/external/virlux/) |

## TrustField Technologies (this chat)

- Corporate / execution / partnership work for **TrustField Technologies** only.
- Do **not** implement Noetfield platform features, public-site GTM, Telegram, or intake APIs in this thread unless the user explicitly re-scopes to Noetfield.
- Strategic reference docs (TrustField ↔ Noetfield split) live under `docs/SOURCE_OF_TRUTH/` and `Noetfield-All-Documents/` — read-only context, not a license to ship Noetfield code here.

## Noetfield (separate — do not mix into TrustField chat)

- Different product and delivery surface from TrustField corporate work.
- If work is Noetfield-specific, use a **Noetfield-scoped** chat/repo — not this one.
- Historical tracker (Noetfield only): [`todolist/NEXT_MOVES.md`](todolist/NEXT_MOVES.md), [`todolist/noetfield-platform.md`](todolist/noetfield-platform.md)

## VIRLUX (separate)

- **Different product:** Interac, Circle, dashboard, etc.
- **Do not** add VIRLUX features, env vars, or payment logic to TrustField or Noetfield workstreams from this chat.
- Backlog notes: [`todolist/external/virlux/`](todolist/external/virlux/) — implement in the VIRLUX codebase.

**Rule of thumb:** *This chat = TrustField. Noetfield = other project. VIRLUX = other project.*
