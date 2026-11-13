#!/usr/bin/env python3
"""Playwright browser acceptance of the *live UI* with clearly mocked protected API data.
No Founder token, no production mutations. Screenshots are visual QA fixtures, NOT real customer evidence.
"""
import json
import os
from pathlib import Path
from urllib.parse import urlparse
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright

BASE=os.getenv("BUSINESS_OS_URL","https://business-os-core-production.up.railway.app").rstrip("/")
PREVIEW=os.getenv("CONTROL_UI_PREVIEW")=="1"
SERVER=None
if PREVIEW:
    static_dir=Path(__file__).parent/"static"
    class PreviewHandler(BaseHTTPRequestHandler):
        def log_message(self,*_args):pass
        def do_GET(self):
            path=urlparse(self.path).path
            routes={"/control":("control.html","text/html; charset=utf-8"),
                    "/control/premium.css":("control-premium.css","text/css; charset=utf-8"),
                    "/control/premium.js":("control-premium.js","text/javascript; charset=utf-8")}
            if path in routes:
                filename,content_type=routes[path]
                body=(static_dir/filename).read_bytes()
                self.send_response(200);self.send_header("Content-Type",content_type)
                self.send_header("Content-Length",str(len(body)));self.end_headers()
                self.wfile.write(body)
                return
            if path in {"/health","/ready","/health/deep"}:
                body=json.dumps({"ok":True,"ready":True,"worker":"running","storage":"ready"}).encode()
                self.send_response(200);self.send_header("Content-Type","application/json")
                self.end_headers();self.wfile.write(body)
                return
            self.send_error(404)
    SERVER=ThreadingHTTPServer(("127.0.0.1",0),PreviewHandler)
    Thread(target=SERVER.serve_forever,daemon=True).start()
    BASE="http://127.0.0.1:"+str(SERVER.server_port)
OUT=Path("qa-artifacts")
OUT.mkdir(exist_ok=True)
fixture={
    "overview":{
        "counts":{"contacts":1,"opportunities":0,"qualified":0,"won":0,"queued_events":0,
                  "pending_tasks":1055,"feedback":0,"platform_intake_signals":1,
                  "platform_intake_pending":0,"platform_intake_tasks_created":1},
        "weighted_pipeline_cad":1250,"pipeline_note":"Estimated value only",
        "llm_configured":True,"worker_interval_seconds":5,
        "brands":[]
    },
    "org":{
        "organization":{"company_role_count":8,"runtime_executor_count":11,"founder":{"role_id":"H-001"}},
        "seats":[
            {"role_id":"N-01","title":"Chief of Staff & Operations Officer","runtime_role_names":["Chief of Staff"],
             "activation_status":"mapped_existing","activation_meaning":"Role is configured. Live execution status comes from task runs.","manager_name":"Founder","layer":1,"max_authority":"A3"},
            {"role_id":"N-02","title":"Opportunity Intelligence Officer","runtime_role_names":["Market Intelligence"],
             "activation_status":"partial_existing","activation_meaning":"Some capabilities are configured.","manager_name":"Chief of Staff","layer":2,"max_authority":"A2"},
            {"role_id":"N-03","title":"Product & Engineering Delivery Officer","runtime_role_names":["Engineering"],
             "activation_status":"mapped_existing","activation_meaning":"Engineering tasks are configured.","manager_name":"Chief of Staff","layer":2,"max_authority":"A3"}
        ]
    },
    "opportunities":{"opportunities":[
        {"id":"opp-fixture","name":"Example Contact","email":"fixture@example.invalid","company":"Example Company",
         "brand":"noetfield","audience":"founder","intent":"partner","score":73,"estimated_value":1250,"stage":"new","role":"founder"}
    ]},
    "tasks":{"tasks":[
        {"id":"task-fixture","company_role_id":"N-02","company_role_title":"Opportunity Intelligence Officer",
         "role":"partnerships","brand":"noetfield","title":"Assess potential GTM partner",
         "objective":"Assess mutual distribution value using verifiable information.",
         "status":"drafted","result":None,"next_action":"Review evidence and prepare founder decision",
         "pending_dependencies":0,"dependency_count":0}
    ]},
    "events":{"events":[
        {"id":"event-fixture","event_type":"platform.intake.signal.received","status":"processed",
         "brand":"noetfield","created_at":"2026-11-12T20:30:00+00:00"}
    ]},
    "runs":{"runs":[
        {"id":"run-fixture","role":"market_intelligence","provider":"fixture-provider","status":"completed",
         "input_tokens":150,"output_tokens":320,"started_at":"2026-11-12T20:32:00+00:00"}
    ]},
    "roi":{"brands":[],"events_last_7d":107,"actual_revenue":"Not connected",
           "cost_tracking":"Token usage tracked. Infrastructure costs not connected."},
    "connect-opportunities":{"items":[]},
    "operations-relay":{
        "schema":"noetfield.company-os.operations-relay.v1",
        "source":"Fixture Company OS stored data, not production",
        "last_supervisor_tick":"2026-11-12T22:00:00+00:00",
        "counts":{"queued":2,"running":1,"blocked":1,"failed":0,"drafted":48,
                  "approved":0,"tasks_needing_execution":3,"needs_attention":1},
        "handoffs":[{"task_id":"task-agent-fixture","title":"Investigate retry",
             "from":"market_intelligence","to":"engineering_operator",
             "owner_role":"engineering_operator","provider":"deterministic-evidence",
             "actual_model_call_observed":False,"input_tokens":0,
             "status":"drafted","created_at":"2026-11-12T22:00:00+00:00"}],
        "actions":[{"action":"BLOCKER_OWNER_ASSIGNED","owner":"Engineering Delivery",
           "result":"DIAGNOSIS_QUEUED_NOT_REPAIRED","at":"2026-11-12T22:00:00+00:00"}],
        "blockers":[{"reason_code":"project_not_allowed","state":"FOUNDER_HANDOFF_REJECTED",
            "owner":"Company OS / owning Company OS tenant",
            "next_action":"Fix canonical project routing"}],
        "end_to_end_motor_execution_proven":False
    },
    "runtime-mesh":{
        "schema":"noetfield.company-os.runtime-mesh-observation.v1",
        "nodes":[
            {"id":"sina_founder","label":"Sina Founder OS","url":"https://sina-founder-os-staging-staging.up.railway.app/","state":"SERVICE_HEALTH_REPORTED"},
            {"id":"business_os","label":"Company OS / NOOS","url":"https://business-os-core-production.up.railway.app/control","state":"LOCAL_CONTROL_SURFACE"},
            {"id":"runway_motor","label":"Runway Motor","url":"https://github.com/Noetfield-Systems/NOETFIELD-RUNWAY","state":"EXECUTION_NOT_OBSERVED"},
            {"id":"independent_verifier","label":"Independent Verifier","url":"https://github.com/Noetfield-Systems/Verification_Layer","state":"RECEIPT_NOT_OBSERVED"}
        ],
        "founder_handoff":{"state":"LIVE","work_packets_claimed":3,"pending_ack":1,"verified_outcomes":0,"external_effects":0},
        "summary":{"verified_edges":0,"runway_e2e_commissioned":False}
    },
    "commercial-team":{"state":"INTERNAL_ONLY","roles":[]},
}
CASE_FIXTURE={
        "intake_id":"INT-ABCDEF246801","request_id":"RID-CNX-FIXTURE",
        "source_created_at":"2026-11-12T20:30:00Z","category":"partnership",
        "initiative":"noetfield","source_channel":"linkedin","case_stage":"QUALIFYING",
        "review_state":"tasks_created","review_owner_role":"partnerships",
        "next_action":"Verify actual partner reach","due_at":"2026-11-15T10:00:00Z",
        "evidence_ref":None,"notes":"","case_version":1,"specialist_roles":["partnerships"],
        "advisory_tasks":[],"actual_owner_assigned":False,"confirmed_meeting":False,"verified_conversion":None
    }
mock_calls=[]
def make_handler(route):
    req=route.request
    u=urlparse(req.url)
    resource=u.path.rsplit("/",1)[-1]
    if req.method=="POST" and u.path=="/api/control/tasks":
        mock_calls.append("POST /api/control/tasks")
        return route.fulfill(status=200,content_type="application/json",
                             body=json.dumps({"created":True,"task_id":"task-fixture-new"}))
    if req.method=="PATCH" and u.path.startswith("/api/control/connect-cases/"):
        mock_calls.append("PATCH Connect case")
        return route.fulfill(status=200,content_type="application/json",
                             body=json.dumps({"updated":True,"case":{"version":2}}))
    if req.method=="POST" and "/approve" in u.path:
        return route.fulfill(status=200,content_type="application/json",body='{"approved":true}')
    if req.method=="POST" and "/commission" in u.path:
        return route.fulfill(status=200,content_type="application/json",
                             body='{"already_commissioned":false,"external_actions":0}')
    if resource=="overview" and "BAD_ACCESS_KEY" in req.headers.get("authorization",""):
        return route.fulfill(status=401,content_type="application/json",body='{"detail":"Founder authentication required."}')
    if resource=="dashboard":
        from datetime import datetime,timedelta,timezone
        from urllib.parse import parse_qs
        params=parse_qs(u.query)
        days=int(params.get("days",["7"])[0])
        brand=params.get("brand",[""])[0]
        today=datetime.now(timezone.utc).date()
        labels=[(today-timedelta(days=x)).isoformat() for x in range(days-1,-1,-1)]
        last=[2,7,13,20,12,22,31]
        counts=([0]*(days-7))+last
        value={"source":"Company OS durable tables","brand":brand or "all","days":days,
               "as_of":datetime.now(timezone.utc).isoformat(),
               "counts":{"contacts":0,"opportunities":0,"active_opportunities":0,
                         "pending_tasks":103 if brand else 1055,"activity_events":sum(counts)},
               "activity_daily":[{"date":day,"count":n} for day,n in zip(labels,counts)],
               "collected_revenue":{"state":"not_connected","amount":None},
               "scope":"Fixture records filtered by venture"}
        mock_calls.append("GET dashboard "+(brand or "all")+" "+str(days))
        return route.fulfill(status=200,content_type="application/json",body=json.dumps(value))
    if resource=="task-inbox":
        from urllib.parse import parse_qs
        params=parse_qs(u.query)
        offset=int(params.get("offset",["0"])[0])
        limit=int(params.get("limit",["40"])[0])
        status=params.get("status",[""])[0]
        brand=params.get("brand",[""])[0]
        q=params.get("q",[""])[0].lower()
        items=[{
            "id":f"task-fixture-{i:03d}","title":f"Review opportunity {i:03d}",
            "objective":"Review real scope and evidence",
            "status":"drafted" if i%2==0 else "queued",
            "role":"partnerships","company_role_title":"Partnerships","brand":"noetfield",
            "next_action":"Recommend next step","result":None,"pending_dependencies":0,
        } for i in range(85)]
        if status:items=[x for x in items if x["status"]==status]
        if brand:items=[x for x in items if x["brand"]==brand]
        if q:items=[x for x in items if q in x["title"].lower() or q in x["id"].lower()]
        result={"schema":"noetfield.business-os.task-inbox.v1",
                "tasks":items[offset:offset+limit],"total":len(items),"offset":offset,
                "limit":limit,"has_more":offset+limit<len(items),"status_counts":{"drafted":43,"queued":42}}
        mock_calls.append("GET task-inbox "+str(offset))
        return route.fulfill(status=200,content_type="application/json",body=json.dumps(result))
    if resource in fixture:
        mock_calls.append(req.method+" "+resource)
        return route.fulfill(status=200,content_type="application/json",body=json.dumps(fixture[resource]))
    raise RuntimeError("Unexpected API route: "+req.method+" "+u.path)

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=["--disable-dev-shm-usage"])
    page=browser.new_page(viewport={"width":1536,"height":1024},device_scale_factor=1)
    errors=[]
    page.on("pageerror",lambda err:errors.append(str(err)))
    page.add_init_script("""(function(){
      window.__storedCredential = null;
      window.__credentialStores = 0;
      Object.defineProperty(window, 'PasswordCredential', {
        configurable:true,
        value:class PasswordCredential {
          constructor(options){ this.id=options.id;this.name=options.name;this.password=options.password; }
        }
      });
      Object.defineProperty(navigator, 'credentials', {
        configurable:true,
        value:{store:async function(credential){
          window.__storedCredential={id:credential.id,password:credential.password};
          window.__credentialStores++;
        }}
      });
    })();""")
    page.route("**/api/control/**",make_handler)
    page.goto(BASE+"/control",wait_until="load",timeout=40000)
    assert page.locator("#auth-form").is_visible(), "Founder login must be a real form"
    assert page.locator("#token").get_attribute("autocomplete")=="current-password"
    assert page.locator("#founder-login-id").get_attribute("autocomplete")=="username"
    assert page.locator("#token").get_attribute("name")=="password"
    page.screenshot(path=str(OUT/"founder-login-fixture.png"),full_page=True)
    page.locator("#token").fill("FIXTURE_TOKEN_NOT_A_REAL_SECRET")
    page.locator("#save-password").check()
    page.locator("#auth-form").evaluate("(form) => form.requestSubmit()")
    page.locator("#metrics .metric").first.wait_for(timeout=30000)
    page.wait_for_function("window.__credentialStores===1")
    assert page.evaluate("window.__storedCredential.id")=="founder", "Password manager identity is wrong"
    assert page.evaluate("window.__storedCredential.password")=="FIXTURE_TOKEN_NOT_A_REAL_SECRET"
    assert page.locator("#token").input_value()=="", "Access key should be cleared from the field"
    assert page.evaluate("localStorage.getItem('noos-founder-token')") is None, "Access key must not be persisted in localStorage"
    page.wait_for_function("document.querySelector('#activity-bars .activity-bar')?.getAttribute('title')",timeout=20000)
    assert "0" in page.locator("#metrics .metric").first.inner_text(), "Active opportunity count should be source-backed"
    assert "1,055" in page.locator("#metrics").inner_text(), "Overview did not display actual-bound fixture field"
    assert "Not connected" in page.locator("#metrics").inner_text(), "Revenue must never show fabricated zero"
    assert page.locator(".sidebar").is_visible()
    page.screenshot(path=str(OUT/"founder-desktop-fixture.png"),full_page=False)
    views=["actions","connect","opportunities","relationships","team","workflows","activity","revenue","health","settings"]
    for view in views:
        if view=="connect":
            page.locator('.side-link[data-go="opportunities"]').click()
            page.locator('.view[data-view="opportunities"] button[data-go="connect"]').first.click()
        elif view=="workflows":
            page.locator('.side-link[data-go="team"]').click()
            page.locator('.view[data-view="team"] button[data-go="workflows"]').first.click()
        elif view=="health":
            page.locator('.sidebar-secondary .side-link[data-go="settings"]').click()
            page.locator('.view[data-view="settings"] button[data-go="health"]').first.click()
        elif view=="settings":
            page.locator('.sidebar-secondary .side-link[data-go="settings"]').click()
        else:
            page.locator('.side-link[data-go="'+view+'"]').click()
        assert page.locator('.view[data-view="'+view+'"]').is_visible(), "Navigation failed: "+view
    page.locator('.side-link[data-go="actions"]').click()
    page.wait_for_function("document.querySelector('#task-list-scope').textContent.includes('of 85')")
    assert page.locator("#tasks tr[data-task-row]").count()==40, "Task inbox did not paginate at 40"
    page.locator("#task-next").click()
    page.wait_for_function("document.querySelector('#task-list-scope').textContent.includes('41–80 of 85')")
    assert page.locator("#tasks tr[data-task-row]").count()==40, "Second task page did not load"
    page.locator("#task-search").fill("opportunity 013")
    page.locator("#task-inbox-controls button[type=submit]").click()
    page.wait_for_function("document.querySelector('#task-list-scope').textContent.includes('of 1')")
    assert page.locator("#tasks tr[data-task-row]").count()==1, "Task search did not filter actual source"
    page.locator("#dashboard-venture").select_option("noetfield")
    page.wait_for_function("document.querySelector('#metrics')?.textContent?.includes('103')")
    assert "GET dashboard noetfield 7" in mock_calls
    page.locator("#dashboard-period").select_option("30")
    page.wait_for_function("document.querySelector('#activity-unit')?.textContent?.includes('last 30 days')")
    page.locator("#dashboard-venture").select_option("")
    page.locator("#dashboard-period").select_option("7")
    page.locator('.side-link[data-go="team"]').click()
    page.locator('.view[data-view="team"] button[data-go="workflows"]').first.click()
    form=page.locator("#new-work-form")
    form.locator('select[name="role"]').select_option("partnerships")
    form.locator('input[name="title"]').fill("Assess a qualified partner")
    form.locator('textarea[name="objective"]').fill("Produce an evidence-ranked partnership recommendation and specific next action.")
    form.locator('button[type="submit"]').click()
    page.wait_for_timeout(900)
    assert "POST /api/control/tasks" in mock_calls, "New work button did not call backend"
    assert page.locator('.view[data-view="actions"]').is_visible(), "New task did not navigate back to Action Center"
    fixture["connect-opportunities"]["items"]=[CASE_FIXTURE]
    page.locator('.side-link[data-go="opportunities"]').click()
    page.locator('[data-go="connect"]').filter(has_text="Open partnership").first.click()
    page.locator("#refresh-connect").click()
    page.locator("#connectrows [data-edit-connect]").first.click()
    assert page.locator("#connect-case-editor").is_visible(), "Connect editor missing"
    page.locator("#connect-next").fill("Verify partner's actual sales reach")
    page.locator("#connect-save").click()
    page.wait_for_timeout(400)
    assert "PATCH Connect case" in mock_calls, "Connect case edit did not call backend"
    page.locator(".side-link[data-go='overview']").click()
    page.set_viewport_size({"width":390,"height":844})
    page.wait_for_timeout(300)
    assert page.locator("#menu-open").is_visible(), "Mobile menu control unavailable"
    page.locator("#menu-open").click()
    assert page.locator(".sidebar").is_visible(), "Mobile drawer did not open"
    page.locator('.side-link[data-go="opportunities"]').click()
    page.locator('.view[data-view="opportunities"] button[data-go="connect"]').first.click()
    assert page.locator('.view[data-view="connect"]').is_visible(), "Mobile navigation did not switch views"
    page.locator("#menu-open").click()
    page.locator(".side-link[data-go='overview']").click()
    page.wait_for_timeout(380)
    assert not page.evaluate("document.body.classList.contains('nav-open')"), "Mobile drawer failed to close after navigation"
    page.screenshot(path=str(OUT/"founder-mobile-fixture.png"),full_page=True)
    width=page.evaluate("document.documentElement.scrollWidth")
    assert width <= 390+3, "Unexpected horizontal page overflow at mobile width: "+str(width)
    assert not errors, "Browser runtime errors: "+"; ".join(errors[:4])
    page.locator("#menu-open").click()
    page.locator('.sidebar-secondary .side-link[data-go="settings"]').click()
    page.locator("#logout").click()
    assert page.locator("#auth-form").is_visible(), "Lock must return user to sign-in"
    assert page.evaluate("sessionStorage.getItem('noos-founder-token')") is None, "Lock must clear session token"
    page.locator("#token").fill("BAD_ACCESS_KEY")
    page.locator("#auth-form").evaluate("(form) => form.requestSubmit()")
    page.wait_for_function("document.querySelector('#auth-feedback')?.textContent?.includes('Access was not verified')",timeout=10000)
    assert page.evaluate("window.__credentialStores") == 1, "Invalid password must not be saved"
    assert page.locator("#auth-form").is_visible(), "Failed authentication must not unlock workspace"
    assert not errors, "Browser runtime errors after failed authentication: "+"; ".join(errors[:4])
    browser.close()
if SERVER is not None:SERVER.shutdown()
print(json.dumps({"status":"PASS","ui":"branch-preview" if PREVIEW else "production-hosted","protected_api_data":"mocked fixtures",
                  "views_tested":11,"mobile_width":390,"auth_and_password_store":"mocked browser API verified","actual_external_mutations":0,
                  "mocked_api_calls":len(mock_calls),
                  "screenshots":[str(x) for x in OUT.glob("*.png")]}))
