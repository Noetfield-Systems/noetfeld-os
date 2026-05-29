# Noetfield v3 MVP — Final Production Spec

Document key: `noetfield-v3-mvp-production-spec-final`

**Active v3 product SOT.** Linear pipeline: Intent → Orchestrator → rule router → sequential execution
→ single governance PASS/FAIL → append-only ledger. Explicitly excludes DAG compiler, scoring router,
microservices for MVP ship. Buildable in 48h; FastAPI single service.
