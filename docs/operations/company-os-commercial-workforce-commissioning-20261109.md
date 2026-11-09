# Company OS commercial workforce commissioning — 2026-11-09

## Scope
Reuse existing Business OS Core roles and runtime for Noetfield, TrustField and SignalForge. This is an **internal onboarding workflow**, not an autonomous outbound SDR, an AI-operated helpdesk or a public posting bot.

## Live-source baseline
Repository: Noetfield-Systems/noetfeld-os, base branch \`platform/business-os-core-v1\`.
Runtime: the existing \`business-os-core\` Railway service with SQLite persistence and a 5-second queue loop.
The Company OS already has event/lead intake, specialist internal drafting, dependency-gated Founder decision brief, approval endpoint, and a read-only Sina revenue queue. A token-protected Founder Control Plane exists.

## Role reuse and powers
| Workforce seat | Runtime role | Allowed | Not commissioned |
|---|---|---|---|
| N-05 Revenue | sales_qualification | Qualify consented opportunities, prepare tailored outreach and scope drafts | External send, deal negotiation, pricing commitment |
| N-07 Customer Success | customer_success | Support triage, knowledge-grounded reply draft, escalation proposal | Customer reply, account write, refund/security incident handling |
| N-06 Marketing | marketing_editorial | Campaign brief, evidence-backed webpage and post draft | Public publishing, DM, claims of external performance |

All three use the existing Business OS Core queued task executor; \`draft\` is a runtime tier, not proof of LLM tool execution. In the absence of configured AI opt-in and model credentials the processor returns deterministic draft results.

## Product separation
- Noetfield: founder-operated alpha, one governed workflow, first-party evidence.
- TrustField: FINTRAC / Canadian regulatory operations, named accountable officers, no custody/settlement or self-filing.
- SignalForge: explainable research signals and backtest analysis, no broker execution or performance promises.
These are **brand lanes**, not additional corporate legal entities.

## Commission
After PR CI and deployment to an authorized environment:
1. Open \`https://business-os-core-production.up.railway.app/control\` using the already-configured Founder token (no token in query strings).
2. Under **Commercial workforce / Company OS**, select Noetfield, TrustField or SignalForge.
3. Click **Commission internal roles** and confirm. This POSTs to \`/api/control/commercial-team/commission\`.
4. Inspect \`/api/control/commercial-team?brand=<brand>\` and underlying /tasks, /events and /runs for the task IDs and states.
5. Refresh the dashboard. A second commission request must return \`already_commissioned=true\`, with the same task IDs.
6. Check the read-only Sina revenue-queue projection \`commercial_workforce\`. This adds no buyer data and does not prove an active SinaOS consumer.

### API sample (internal, do not paste token into a URL)
\`\`\`shell
curl -X POST "$BUSINESS_OS_CORE_URL/api/control/commercial-team/commission" \
  -H "Authorization: Bearer $FOUNDER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"brand":"noetfield"}'
\`\`\`

An accepted request should return three internal task IDs, \`external_actions:0\` and \`autonomy:"internal_draft_only"\`. These are real DB records, not fabricated staff or revenue.

## Real channel integration (NOT implemented in this PR)
- Inbound consent: customer form / product contact record must route to one approved queue with original source, tenant and retention policy. No AI response without appropriate opt-in.
- CRM: map \`lead -> qualification -> next action -> Founder approval -> actual sent message receipt -> buyer response -> opportunity\`. Existing Noetfield public intake sync must be tested against real hosting credentials.
- Support: connect approved inbox/helpdesk + signed FAQ KB, identity check, escalation routing, sent/replied receipt, SLA reporting.
- Marketing: connect approved channel publisher and analytics after claim check; human public-release gate, canonical post record.
- Sina: verify consumer actually reads the PII-free company queue and ratifies strategic priorities; extra payload field alone is not E2E orchestration.
- Paperclip: verify Governor-approved WorkPacket execution, runtime adapter, objective completion, independent QA and receipt. Paperclip account deployment is not this proof.

## Release verification
- GitHub tests \`python -m unittest discover -s apps/business-os-core -p "test_*.py"\` PASS on the PR tip.
- Confirm target branch's Docker source includes \`commercial_team.py\`, \`app.py\`, \`core.py\`, seat registry and control HTML.
- After deployment: /health database ready; authentication rejects missing/bad tokens; commission idempotent per brand; three internal tasks per brand; deterministic or opt-in LLM drafts; no external sends; record task IDs and SHA.
- Do not claim a new real customer until an independently identifiable consenting customer contacts or signs.
- Do not claim additional operating cost is zero: use actual Railway, inference, email and storage invoices.

## Founder exception budget
The user should ratify only high-value exceptions: messaging outside the organization, pricing/contract, publication, security and regulated decisions. Routine internal research, draft creation, status tracking and reversible analysis may operate inside their approved scope.
