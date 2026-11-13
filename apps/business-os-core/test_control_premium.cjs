/* Premium Founder Control Plane contracts and safe fixture-based UI rendering. */
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const assert=require("node:assert/strict");
const root=__dirname;
const html=fs.readFileSync(path.join(root,"static/control.html"),"utf8");
const css=fs.readFileSync(path.join(root,"static/control-premium.css"),"utf8");
const ui=fs.readFileSync(path.join(root,"static/control-premium.js"),"utf8");
const inline=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
assert.equal(inline.length,1,"Expected one existing application controller");
new vm.Script(inline[0],{filename:"control-inline.js"});
new vm.Script(ui,{filename:"control-premium.js"});
assert.match(html,/\/control\/premium\.css\?v=6/);
assert.match(html,/\/control\/premium\.js\?v=10/);
assert.match(html,/type="password" id="token"/);
assert.match(html,/<form id="auth-form" method="post" action="\/control" autocomplete="on">/);
assert.match(html,/name="username" autocomplete="username"/);
assert.match(html,/name="password" autocomplete="current-password"/);
assert.match(html,/id="save-password" type="checkbox"/);
assert.match(inline[0],/PasswordCredential/);
assert.match(inline[0],/navigator\.credentials\.store/);
assert.match(inline[0],/sessionStorage\.setItem\('noos-founder-token',token\)/);
assert.doesNotMatch(inline[0],/localStorage\.setItem/);
assert.doesNotMatch(html,/id="token"[^>]*autocomplete="off"/);
assert.match(html,/<meta name="robots" content="noindex,nofollow"/);
assert.ok(!html.includes('value="FAKE_REVENUE"'));
const expectedViews=["overview","actions","connect","opportunities","relationships","team","workflows","activity","revenue","health","settings"];
for(const v of expectedViews){
  assert.ok(html.includes('data-view="'+v+'"'),"missing view: "+v);
  assert.ok(html.includes('data-go="'+v+'"'),"missing navigation: "+v);
}
const ids=[...html.matchAll(/id="([^"]+)"/g)].map(m=>m[1]);
const unique=new Set(ids);
assert.equal(unique.size,ids.length,"Duplicate HTML IDs: "+ids.filter((id,i)=>ids.indexOf(id)!==i));
const required=[...ui.matchAll(/\$\("([^"]+)"\)/g),...inline[0].matchAll(/\$\('([^']+)'\)/g)].map(m=>m[1]);
for(const id of required){if(id!=="copy-connect")assert.ok(unique.has(id),"Controller references unknown element "+id);}
assert.match(css,/@media\(max-width:780px\)/);
assert.match(css,/@media\(max-width:520px\)/);
assert.match(css,/prefers-reduced-motion/);
assert.match(inline[0],/\/api\/control\/connect-cases\//);
assert.match(inline[0],/\/api\/control\/tasks\/'\+id\+'\/approve/);
assert.match(inline[0],/\/api\/control\/commercial-team\/commission/);
assert.match(ui,/\/api\/control\/tasks/);
assert.match(ui,/\/api\/control\/runtime-mesh/);
assert.match(html,/id="runtime-mesh"/);
assert.match(ui,/function loadRuntimeMesh/);
assert.match(html,/id="operations-relay-preview"/);
assert.match(html,/id="operations-relay-detail"/);
assert.match(ui,/function loadOperationsRelay/);
assert.match(ui,/\/api\/control\/operations-relay/);
assert.match(ui,/actual_model_call_observed/);
assert.match(ui,/Inspect assigned prompt & recorded response/);
assert.match(ui,/response_kind/);
assert.match(ui,/counts\.actionable_tasks/);
assert.match(ui,/runway_e2e_commissioned|Runway remains the canonical execution engine/);
class FakeClassList{
  constructor(){this.items=new Set()}
  toggle(name,force){const on=force===undefined?!this.items.has(name):Boolean(force);if(on)this.items.add(name);else this.items.delete(name);return on}
  add(n){this.items.add(n)}
  remove(n){this.items.delete(n)}
  contains(n){return this.items.has(n)}
}
class FakeElement{
  constructor(id){this.id=id;this.textContent="";this.innerHTML="";this.hidden=false;this.value="";this.dataset={};this.classList=new FakeClassList()}
  addEventListener(){}
  setAttribute(){}
  removeAttribute(){}
  scrollIntoView(){}
}
const elements=new Map(ids.map(id=>[id,new FakeElement(id)]));
const body=new FakeElement("body");
const document={body,getElementById:id=>elements.get(id)||null,querySelectorAll:()=>[],addEventListener(){}};
const window={addEventListener(){},scrollTo(){},navigator:{}};
const location={hash:""};
const history={replaceState(){}};
const context=vm.createContext({document,window,location,history,navigator:{},console,Date,Number,Map,Set,Boolean,String,Array,Promise,URLSearchParams});
vm.runInContext(ui,context,{timeout:1000});
assert.ok(window.noosPremium?.render,"Premium workspace did not register");
const fixture={
 o:{counts:{opportunities:2,pending_tasks:1055},llm_configured:true,model_connection:{state:"AUTH_REJECTED",last_error_code:"HTTP_401",observed_at:"2026-11-13T06:15:00Z"}},
 org:{organization:{company_role_count:8,runtime_executor_count:11},seats:[{title:"Chief of Staff",role_id:"N-01",activation_status:"mapped_existing",runtime_role_names:["Operations"],manager_name:"Founder"}]},
 op:{opportunities:[{id:"opp-test",name:"Example Founder",company:"Example Org",email:"someone@example.invalid",stage:"new",brand:"noetfield"}]},
 t:{tasks:[{id:"task-test",title:"Review potential partner",status:"drafted",role:"partnerships",company_role_title:"Partnerships",brand:"noetfield",next_action:"Verify audience",result:null}]},
 e:{events:[{event_type:"intake.received",status:"processed",brand:"noetfield",created_at:"2026-11-12T20:30:00Z"}]},
 r:{runs:[]},
 roi:{brands:[],events_last_7d:107,actual_revenue:"Not connected"}
};
window.noosPremium.render(fixture);
assert.match(elements.get("metrics").innerHTML,/1,055/);
assert.match(elements.get("llm-config-value").textContent,/Auth rejected.*HTTP_401/);
assert.ok(elements.get("llm-config-value").className.includes("bad"));
assert.match(html,/Model connection/);
assert.match(elements.get("metrics").innerHTML,/Not connected/);
assert.match(elements.get("action-preview").innerHTML,/Work requiring action/);
assert.match(elements.get("action-preview").innerHTML,/Incoming opportunities/);
assert.match(elements.get("action-preview").innerHTML,/Revenue visibility/);
assert.match(html,/id="dashboard-venture"/);
assert.match(html,/id="dashboard-period"/);
assert.match(html,/id="activity-bars"/);
assert.match(html,/id="worker-cycle-value"/);
assert.match(elements.get("team-summary").innerHTML,/Chief of Staff/);
assert.match(elements.get("revenue-state").innerHTML,/Collected revenue not connected/);
assert.match(elements.get("relationship-list").innerHTML,/Example Founder/);
window.noosPremium.paintConnect([{intake_id:"INT-ABCDEF246801",category:"events",initiative:"noetfield",source_channel:"linkedin",case_stage:"NEW"}]);
assert.equal(elements.get("connect-count").textContent,"1");
assert.match(elements.get("connect-summary").innerHTML,/Events &amp; awards|Events & awards/);
window.noosPremium.paintConnect(null);
assert.equal(elements.get("connect-count").textContent,"—");
window.noosPremium.setAuth(true);
assert.equal(elements.get("auth-gate").classList.contains("hide"),true);
window.noosPremium.setAuth(false);
assert.equal(elements.get("app").classList.contains("hide"),true);
console.log("PASS premium UI: assets, 11 views, API controls, semantic metrics, accessible states, auth, source-data rendering");
