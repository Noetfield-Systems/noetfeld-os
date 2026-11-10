# Product-native Company OS — Founder Cognitive Proxy continuation

**No second Company OS service, no duplicated scheduler and no new agent registry.**

Sina is one Founder/portfolio head. Every product Company OS has its own director, specialist remits, operating objective, source project and scoped activity history. This connector asks the authenticated Sina Goalkeeper for bounded decisions and then runs local work through the existing Company OS \`product_observations -> events -> tasks -> worker -> runs\` path.

## Integrations

- Sina source URL is fixed in \`sina_work_bridge.SOURCE_URL\`. Authentication uses the existing \`SINA_ORG_BRIDGE_TOKEN\`. A redirect, arbitrary destination, spoofed origin or unscoped tenant is rejected.
- \`POST /api/control/venture-company-os/decisions\`: existing authenticated Company OS Founder API, body has the Sina typed \`project_id\`, \`company_id\`, \`agent_role\`, \`intent\`, \`proposed_action\`, \`question\`, \`options\`, \`evidence_refs\`, optional \`request_id\`. This is **not** permission to execute Mainnet, payments, trades or live outreach.
- \`GET /api/control/venture-company-os/decisions?company_id=...&project_id=...\`: recent local decision refs and the existing event/task links; no raw prompt text or secrets.
- Company OS specialist \`process_task\` calls \`consult_existing_task\` for scoped normal tasks and retains the trusted decision as context. It never needs a Sina-created engineering task to continue a locally discovered product problem.

## Runtime state transition

\`\`\`
LOCAL_QUESTION
  -> PINNED_AUTHENTICATED_FOUNDER_DECISION
     -> PROJECT_SCOPE_AND_PERMIT_FLAGS_VERIFIED
        -> PROCEED_IN_LOCAL_COMPANY_OS / CHECK_EVIDENCE_AND_CONTINUE
          -> ATOMIC_EXISTING_PRODUCT_OBSERVATION_AND_EVENT
          -> EXISTING_COMPANY_OS_TASKS_AND_SPECIALISTS
          -> DRAFT/ARTIFACT -> EXISTING_VERIFIER
        -> FOUNDER_RATIFICATION / GOVERNOR_REQUIRED / PAUSED
          -> AUDIT_DECISION_ONLY; NO EXECUTION EVENT
     -> FAILED/UNAVAILABLE
        -> RECOVERABLE_DEGRADED; NEVER CLAIM FOUNDER APPROVAL
\`\`\`

The decision ledger stores only a deterministic reference, hashed stable authority fields, task/event links and disposition. Replays of the same \`decision_ref\` are no-ops; a changed authority envelope under the same reference is rejected. Source-reported agent feedback on Sina cannot create an independent proof receipt.

## Project scope and ownership

Company ID and project ID are always separate. A venture's Company OS local operating unit is not a claim of incorporation or financial-asset ownership. RHEVO's technical Company OS does not own the customer's token treasury. The Company OS project alias can map to a canonical Founder project only through existing founder mandate records. A Company OS cannot assume a project exists by using a prompt.

## Test/production truth

Current PR unit and integration tests exercise real local SQLite events and canonical task creation against **mocked authenticated Sina HTTPS responses**. They do not constitute proof that unrelated ChatGPT sessions installed the OpenAPI Action, that the real external Agent Fabric wrote a code commit, or that a deployed product acquired users/revenue. Check actual Railway service release SHA and first independently observed event before asserting the remote E2E pipeline is live.

## Operator acceptance sequence

1. Deploy Founder OS policy memory/API release first, healthy.
2. Deploy the existing Company OS Railway runtime with \`venture_decision_bridge.py\` included in its Docker COPY/import checks.
3. Submit a test internal question for one commissioned product using the existing authorized Company OS API.
4. Confirm authenticated Sina \`decision_ref\`, Company local decision record, exactly one project-scoped observation/event and subsequent local tasks.
5. Submit identical question again; confirm idempotent replay and no second event.
6. Submit a reserved external action question; confirm **no** local execution event.
7. Observe model route and independent receipt separately. \`specialist_degraded\` with zero model tokens is not a working coding agent, however healthy the decision bridge may be.

If the user-facing agent lacks Sina tool connection, report \`GATEWAY_NOT_CONNECTED\`; use existing policies and read-only research, not a fabricated successful API response.
