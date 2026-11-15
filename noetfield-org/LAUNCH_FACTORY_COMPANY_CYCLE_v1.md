# NOOS Company Cycle — Launch Factory integration contract v1 (2026-11-15)

**Status: source code/contract, NOT a deployed 24/7 pipeline.** Keep the Company OS existing workforce, Governor, tool-routing and worker leases. No fresh scheduler, database or authorization server.

## Parent/child separation
- Portfolio priority, idea and launch program: `Noetfield-Systems/sina_founder_os/integrations/launch-factory`.
- NOOS can execute **only** `company_project` whose `company_id` matches `noetfield-systems-inc`.
- ARQANT, Cairn, BuildRelay and other independent ventures use their own Company OS/AgentOS and must not be executed through the Noetfield corporate wallet, customer data, agent credentials or treasury. NOOS may provide reusable code/engineering services via a separately authorized engagement, never implicit takeover.
- Fieldwork remains single CRM and network evidence source; segment project routes independently.

## Operational cycle
Portfolio experiment → source prototype recovered → owned project runtime → real usable core loop → existing Railway/Cloudflare route → channel-specific community activation → attributed relationship intelligence from Fieldwork → consented external publishing → genuine user activation → actual cash/payment/onchain evidence → iterate/scale/park.

### Existing workforce mapping
| Launch role | NOOS seat |
| --- | --- |
| Product/Engineering/Onchain technical prep | N-03 |
| Community onboarding and retention | N-07 |
| Fieldwork/source relationships/Revenue | N-05 |
| Distribution, content and channel campaigns | N-06 |
| Independent proof/QA | N-04 |
| Intelligence/experiment selection | N-02 |
| Cross-role coordination | N-01 |
| Spend/finance reconciliation | N-08 |

`scripts/launch_factory_company_cycle_v1.py` accepts a Sina Launch Factory candidate plan and strictly compiles existing-seat assignments with immutable source digest, canonical company/project IDs and no automatic external side effects. It does **not** create a second live queue. Next integration step is the current role/mission intake with Governor decision and actual rights, not a fresh adapter daemon.

## Production receipt
Per project: source SHA, build CI, actual deployment SHA + URL + viewport journey, first-party activation events, retained cohort, verified referrals, public post URLs, payment provider settlement receipt or signed onchain transaction if relevant. Distinguish available source code from actual deployed code and real revenue.

## Activation
`python3 -m unittest tests/test_launch_factory_company_cycle_v1.py`.
Use `python3 scripts/launch_factory_company_cycle_v1.py <candidate-plan.json>` to print mapped candidates. No environment changes or production writes are performed by this script.

Company OS must continuously handle safe product and distribution tasks within its existing permitted loop; token signing, fund transfers and legal binding effects require actual scoped owner authority only for those individual actions. No blanket pause of other roles.
