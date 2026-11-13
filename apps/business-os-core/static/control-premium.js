/* Noetfield Company OS premium presentation layer. No simulated data or external effects. */
(function(){
"use strict";
const $=id=>document.getElementById(id);
const esc=x=>String(x??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const safeNumber=x=>(x===null||x===undefined||x===""||!Number.isFinite(Number(x))?"—":Number(x).toLocaleString("en-CA"));
const date=x=>{if(!x)return "Not scheduled";const d=new Date(x);return Number.isNaN(d.getTime())?String(x):d.toLocaleString("en-CA",{dateStyle:"medium",timeStyle:"short"});};
const category={
  partnership:"Strategic partnership",growth:"Sales & distribution",capital:"Investment & capital",people:"Talent & advisors",events:"Events & awards",business:"Customer or pilot",other:"Other opportunity"
};
const role={
  chief_of_staff:"Operations lead",audience_router:"Opportunity routing",sales_qualification:"Revenue team",customer_success:"Customer success",
  marketing_editorial:"Marketing & content",market_intelligence:"Market research",product_strategy:"Product strategy",
  roi_analyst:"Business results",engineering_operator:"Product & engineering",risk_governance:"Quality & permissions",partnerships:"Partnerships"
};
const statuses={
  mapped_existing:"Configured",partial_existing:"Partially available",
  drafted:"Prepared for review",queued:"Waiting to run",processing:"In progress",running:"In progress",
  approved:"Reviewed",completed:"Completed",failed:"Needs attention",blocked:"Waiting on dependency",dead_letter:"Needs investigation",
  NEW:"New",QUALIFYING:"Under review",QUALIFIED:"Qualified",ENGAGED:"In conversation",
  WAITING_FOUNDER:"Needs founder decision",WAITING_EXTERNAL:"Waiting on reply",
  DECLINED:"Declined",CLOSED_WON:"Reported won",CLOSED_LOST:"Closed",ARCHIVED:"Archived"
};
function humanStatus(s){const v=String(s||"unknown");return statuses[v]||v.replaceAll("_"," ").toLowerCase().replace(/^./,x=>x.toUpperCase());}
function labelTag(s){const v=String(s||"");const cls=/fail|dead|unavail|blocked/.test(v)?"bad":/partial|wait|queue|draft|running|processing/.test(v)?"warn":/approved|completed|mapped|qualif|engaged/.test(v)?"":"neutral";return '<span class="tag '+cls+'">'+esc(humanStatus(v))+'</span>';}
function metric(label,value,note,icon,view,kind){
  return '<article class="metric '+(kind||"")+'"><div class="metric-ico" aria-hidden="true">'+icon+'</div><span>'+esc(label)+'</span><strong>'+esc(value)+'</strong><small>'+esc(note)+'</small><div><a href="#'+view+'" data-go="'+view+'">View details →</a></div></article>';
}
let last=null,connectRecords=[],currentView="";
const pages={
 overview:["Company overview","What needs attention, what's moving, and what's producing results."],
 actions:["Action center","Review decisions and work that needs a clear next step."],
 opportunities:["Opportunities","Potential customers and deals recorded in the business pipeline."],
 connect:["Connect · incoming proposals","Partnerships, introductions, events, talent and other new opportunities."],
 relationships:["Relationships","People and organizations connected to recorded business opportunities."],
 team:["Team & specialists","Who does what, and which capabilities are configured."],
 workflows:["Work & workflows","Source-backed work assignments and recent model runs."],
 activity:["Activity & runs","What the company has actually recorded and executed."],
 revenue:["Revenue & results","Separate potential business value from verified money received."],
 health:["System health","Check the reliability of the components that keep work moving."],
 settings:["Workspace settings","Access, links and operational information."]
};
function showView(name,opts={}){
  if(!pages[name])name="overview";
  currentView=name;
  document.querySelectorAll(".view").forEach(el=>el.hidden=el.dataset.view!==name);
  document.querySelectorAll(".side-link[data-go]").forEach(el=>{
    const active=el.dataset.go===name;
    el.classList.toggle("active",active);
    active?el.setAttribute("aria-current","page"):el.removeAttribute("aria-current");
  });
  $("page-title").textContent=pages[name][0];
  $("page-description").textContent=pages[name][1];
  $("crumb-current").textContent=pages[name][0];
  document.body.classList.remove("nav-open");
  $("menu-open").setAttribute("aria-expanded","false");
  $("sidebar").setAttribute("aria-hidden", "false");
  if(!opts.noHash && location.hash!=="#"+name)history.replaceState(null,"","#"+name);
  if(!opts.noScroll)window.scrollTo({top:0,behavior:"instant"});
  if(name==="health")loadHealth();
}
function setAuth(isConnected,message){
  document.body.classList.toggle("locked",!isConnected);
  if(isConnected)document.body.classList.remove("nav-open");
  $("auth-gate").classList.toggle("hide",isConnected);
  $("app").classList.toggle("hide",!isConnected);
  $("sidebar").classList.toggle("hide",!isConnected);
  $("top-search").classList.toggle("hide",!isConnected);
  $("logout").classList.toggle("hide",!isConnected);
  $("refresh").classList.toggle("hide",!isConnected);
  $("auth-state").textContent="";
  $("auth-state").setAttribute("aria-hidden","true");
  $("auth-state").classList.toggle("good",isConnected);
  $("status").textContent=isConnected?"Connected":(message||"Founder access required");
  $("status").title=message||"Company OS session status";
  $("status").setAttribute("role","status");
  if(isConnected)showView((location.hash||"#overview").slice(1),{noHash:true,noScroll:true});
}
function formatTask(x){
  return "<div class='action-item'><span class='action-mark' aria-hidden='true'>☷</span><div><b>"+esc(x.title||"Review work")+"</b><p>"+esc(role[x.role]||x.company_role_title||"Company operations")+" · "+esc(humanStatus(x.status))+" · "+esc(x.brand||"Portfolio")+"</p></div><button class='btn alt' type='button' data-go='actions'>Review →</button></div>";
}
function renderActionCenter(t,overview){
  const all=(t?.tasks||[]), items=all.filter(x=>["drafted","queued","running","blocked","failed"].includes(x.status));
  const priority={failed:0,blocked:1,drafted:2,running:3,queued:4};
  items.sort((a,b)=>(priority[a.status]??9)-(priority[b.status]??9));
  const sample=items.slice(0,4);
  $("action-preview").innerHTML=sample.length?sample.map(formatTask).join(""):'<div class="empty"><div class="empty-icon">✓</div><h3>No recent work requiring review</h3><p>The latest task records contain no open items. This is not a guarantee that the full queue is empty.</p><button class="btn alt" data-go="actions">View work queue</button></div>';
  const count=overview?.counts?.pending_tasks;
  $("action-count").textContent=count===undefined?"—":safeNumber(count);
  $("action-count-hint").textContent=count===undefined?"Source unavailable":"Open company tasks across the existing queue";
  $("nav-action-count").textContent=count===undefined?"—":count>999?"999+":String(count);
  const filter=$("action-filter")?.value||"";
  const shown=all.filter(x=>!filter||x.status===filter);
  $("tasks").innerHTML=shown.map(x=>{
    let r={};try{r=JSON.parse(x.result||"{}")}catch{}
    const rec=r.recommendation||{};
    return '<tr><td><b>'+esc(x.title)+'</b><span class="muted">'+esc(x.brand||"Portfolio")+' · '+esc(x.id)+'</span></td>'+
      '<td>'+esc(role[x.role]||x.role)+'<span class="muted">'+esc(x.company_role_title||"")+'</span></td>'+
      '<td>'+labelTag(x.status)+'<span class="muted">'+safeNumber(x.pending_dependencies||0)+' waiting dependencies</span></td>'+
      '<td>'+esc(rec.next_best_action||x.next_action||"No action recorded")+'</td>'+
      '<td>'+(x.status==="drafted"?'<button class="btn alt" data-approve="'+esc(x.id)+'">Record approval</button>':'<span class="muted">—</span>')+'</td></tr>';
  }).join("")||'<tr><td colspan="5"><div class="empty">No task records match this filter.</div></td></tr>';
  $("task-list-scope").textContent="Displaying "+shown.length+" recent records from the task API (up to 150), not the entire queue.";
}
function renderTeam(org){
  const seats=org?.seats||[];
  $("team-summary").innerHTML=seats.length?seats.slice(0,4).map(x=>'<div class="status-line"><span><b>'+esc(x.title||x.role_id)+'</b><br><span class="muted">'+esc((x.runtime_role_names||[]).join(", ")||"No connected specialists listed")+'</span></span>'+labelTag(x.activation_status)+'</div>').join(""):'<div class="empty">Team registry is currently unavailable.</div>';
  $("agents").innerHTML=seats.length?'<div class="stack-list">'+seats.map(x=>{
    const activation=String(x.activation_status||"").toLowerCase();
    const readable=activation.includes("mapped")?"Configured":activation.includes("partial")?"Partially available":humanStatus(x.activation_status);
    const cls=activation.includes("partial")?"warn":"neutral";
    return '<details class="agent-item"><summary><span><b>'+esc(x.title||x.role_id)+'</b><span class="muted">'+esc((x.runtime_role_names||[]).join(" · ")||"No runtime specialist mapped")+'</span></span><span class="tag '+cls+'">'+esc(readable)+'</span></summary>'+
      '<div class="agent-item__body"><p class="helper">'+esc(x.activation_meaning||"Registry entry only. Live execution must be checked separately.")+'</p>'+
      '<p class="muted">Reporting to: '+esc(x.manager_name||"Founder")+'</p>'+
      '<details><summary class="muted">Technical details</summary><p class="helper">Seat '+esc(x.role_id)+' · Layer '+esc(x.layer)+' · Authority '+esc(x.max_authority||"not specified")+'</p></details></div></details>';
  }).join("")+'</div>':'<div class="empty">Team data has not been loaded.</div>';
  $("team-total").textContent=org?.organization?safeNumber(org.organization.company_role_count):"—";
  $("capability-total").textContent=org?.organization?safeNumber(org.organization.runtime_executor_count):"—";
}
function renderBusiness(roi){
  const available=Boolean(roi&&!roi.__source_unavailable);
  $("revenue-state").innerHTML='<div class="empty"><div class="empty-icon">◈</div><h3>Collected revenue not connected</h3><p>Financial records have not been linked to this workspace. Estimated pipeline and recorded wins are not cash received.</p><span class="muted">Connect an authorized financial source to display verified receipts.</span></div>';
  $("roi").innerHTML=available?'<div class="stack-list">'+(roi.brands||[]).map(x=>
    '<div class="status-line"><span><b>'+esc(x.brand)+'</b><br><span class="muted">'+safeNumber(x.leads)+' recorded leads · '+safeNumber(x.qualified)+' fit-qualified</span></span>'+
      '<span><b>'+Number(x.weighted_pipeline||0).toLocaleString("en-CA",{style:"currency",currency:"CAD",maximumFractionDigits:0})+'</b><br><span class="muted">Estimate, not revenue</span></span></div>'
  ).join("")+'<p class="helper">'+esc(roi.actual_revenue||"Revenue source not connected")+'</p></div>':
  '<div class="empty">Business results are temporarily unavailable.</div>';
  $("activity-week").textContent=available?safeNumber(roi.events_last_7d):"—";
}
function renderActivity(events,runs){
  $("events").innerHTML=events?.events?.length?events.events.slice(0,35).map(x=>
    '<div class="timeline-row"><b>'+esc(x.event_type.replaceAll("."," · ").replaceAll("_"," "))+'</b> '+labelTag(x.status)+
    '<p>'+esc(x.brand)+' · '+esc(date(x.created_at))+(x.error?' · Issue: '+esc(x.error):'')+'</p></div>'
  ).join(""):'<div class="empty">No source-backed activity is available.</div>';
  $("runs").innerHTML=runs?.runs?.length?runs.runs.slice(0,40).map(x=>
    '<div class="timeline-row"><b>'+esc(role[x.role]||x.role||"Model task")+'</b> '+labelTag(x.status)+
    '<p>'+esc(date(x.started_at))+' · '+esc(x.provider||"Not recorded")+' · '+safeNumber(x.input_tokens)+' input tokens</p></div>'
  ).join(""):'<div class="empty">No model execution runs are recorded.</div>';
  $("workflows-snapshot").innerHTML=runs?.runs?.length?runs.runs.slice(0,20).map(x=>
    '<div class="status-line"><span><b>'+esc(role[x.role]||x.role||"Work run")+'</b><br><span class="muted">'+esc(date(x.started_at))+'</span></span>'+labelTag(x.status)+'</div>'
  ).join(""):'<div class="empty">No recent model runs in this source. Workflow definitions from other systems are not connected here.</div>';
}
function renderPeople(op){
  const opportunities=op?.opportunities||[];
  const map=new Map();
  opportunities.forEach(x=>{
    const key=String(x.email||x.company||x.name||"").trim().toLowerCase();
    if(!key)return;
    if(!map.has(key))map.set(key,{name:x.name||"Unnamed contact",company:x.company||"",email:x.email||"",items:[],brand:x.brand});
    map.get(key).items.push(x);
  });
  const people=[...map.values()];
  $("relationship-list").innerHTML=people.length?'<div class="scroll"><table><thead><tr><th>Person or organization</th><th>Recorded role / context</th><th>Related opportunities</th></tr></thead><tbody>'+
    people.map(x=>'<tr><td><b>'+esc(x.name||x.company)+'</b><span class="muted">'+esc(x.company)+'</span></td><td>'+esc(x.items[0]?.role||x.items[0]?.audience||"Not specified")+'<span class="muted">Source: Business OS opportunity records</span></td><td>'+safeNumber(x.items.length)+' <button class="btn alt" data-go="opportunities">View opportunities</button></td></tr>').join("")+'</tbody></table></div>':
    '<div class="empty"><div class="empty-icon">♧</div><h3>No linked contacts in this source</h3><p>People attached to Business OS opportunities will appear here. A full portfolio relationship graph is not connected to this screen yet.</p><a class="btn" href="https://www.noetfield.com/connect/" target="_blank" rel="noopener noreferrer">Share Connect link ↗</a></div>';
  $("relationship-count").textContent=op?safeNumber(people.length):"—";
}
function paintConnect(items){
  const unavailable=!Array.isArray(items);
  connectRecords=Array.isArray(items)?items:[];
  if(unavailable){$("connect-summary").innerHTML='<div class="empty"><h3>Incoming requests unavailable</h3><p>We could not read the Connect feed. Your saved submissions remain in the source system.</p><button class="btn alt" data-go="connect">Review connection</button></div>';$("connect-count").textContent="—";$("connect-open").textContent="—";$("connect-scope").textContent="Feed temporarily unavailable";return;}
  const n=connectRecords.length, open=connectRecords.filter(x=>!["ARCHIVED","DECLINED","CLOSED_LOST"].includes(x.case_stage)).length;
  const newest=connectRecords.slice(0,4);
  $("connect-summary").innerHTML=n?newest.map(x=>
    '<div class="action-item"><span class="action-mark">↗</span><div><b>'+esc(category[x.category]||x.category)+'</b><p>'+esc(x.initiative)+' · '+esc(humanStatus(x.case_stage))+' · '+esc(x.source_channel)+'</p></div><button class="btn alt" data-go="connect">Review</button></div>'
  ).join(""):'<div class="empty"><div class="empty-icon">◇</div><h3>No relationship requests in this feed</h3><p>Share one link for partnerships, advisors, customers, investors and events.</p><button id="copy-connect" class="btn">Copy Connect link</button></div>';
  $("connect-count").textContent=safeNumber(n);
  $("connect-open").textContent=safeNumber(open);
  $("connect-scope").textContent=n+" recent, source-backed Connect cases in the authorized Business OS feed (maximum 100).";
  $("nav-connect-count").textContent=n>99?"99+":String(n);
}
function render(data){
  last=data;
  const {o,org,op,t,e,r,roi}=data;
  const counts=o?.counts||{};
  $("metrics").innerHTML=[
    metric("Recorded opportunities",counts.opportunities===undefined?"—":safeNumber(counts.opportunities),"Business OS records · includes all stages","◎","opportunities"),
    metric("Open work",counts.pending_tasks===undefined?"—":safeNumber(counts.pending_tasks),"Queued, running or awaiting review","▣","actions","attention"),
    metric("Activity · last 7 days",roi&&!roi.__source_unavailable?safeNumber(roi.events_last_7d):"—","Recorded events, not revenue","⌁","activity"),
    metric("Collected revenue","Not connected","No verified payment source","◈","revenue")
  ].join("");
  $("last-updated").textContent="Updated "+new Date().toLocaleTimeString("en-CA",{hour:"numeric",minute:"2-digit"});
  $("data-note").textContent="Company-wide totals from connected services. Counts and activity are not verified commercial outcomes.";
  renderActionCenter(t,o);
  renderTeam(org);
  renderActivity(e,r);
  renderBusiness(roi);
  renderPeople(op);
  if(op&&Array.isArray(op.opportunities)){
    $("pipeline-records").textContent=safeNumber(op.opportunities.length);
  }else $("pipeline-records").textContent="—";
  if(!connectRecords.length && $("connect-count").textContent==="—"){$("connect-summary").innerHTML='<div class="empty"><p>Loading incoming requests…</p></div>';}
}
async function loadHealth(){
  $("system-health").textContent="Checking service readiness…";
  const checks=[
    {label:"Company API & database",path:"/health"},
    {label:"Work processing",path:"/ready"},
    {label:"Detailed service health",path:"/health/deep"}
  ];
  const done=await Promise.allSettled(checks.map(x=>fetch(x.path,{cache:"no-store"}).then(async r=>({status:r.status,body:await r.json()}))));
  $("system-health").innerHTML=checks.map((x,i)=>{
    const settled=done[i];
    const healthy=settled.status==="fulfilled"&&settled.value.status===200&&(settled.value.body.ok===true||settled.value.body.ready===true);
    const state=settled.status==="rejected"?"Unavailable":healthy?"Responding":"Needs attention";
    const detail=settled.status==="fulfilled"?(settled.value.body.worker_interval_seconds?"Worker interval: "+settled.value.body.worker_interval_seconds+" seconds":"Service returned HTTP "+settled.value.status):"Could not reach service";
    return '<div class="status-line"><span><b>'+esc(x.label)+'</b><br><span class="muted">'+esc(detail)+'</span></span><span class="tag '+(healthy?"":"bad")+'">'+esc(state)+'</span></div>';
  }).join("")+'<p class="helper">A successful health response does not independently verify the accuracy of every downstream integration.</p>';
}
function setSearchResults(q){
  const target=$("search-results"),v=q.toLowerCase().trim();
  if(!v){target.hidden=true;target.innerHTML="";return}
  if(!last){target.hidden=false;target.innerHTML='<div class="note">Connect to search your available records.</div>';return}
  let matches=[];
  (last.op?.opportunities||[]).forEach(x=>{const name=x.company||x.name||"Opportunity";if([name,x.name,x.intent,x.brand].join(" ").toLowerCase().includes(v))matches.push({title:name,info:"Business opportunity · "+x.brand,view:"opportunities"})});
  (last.t?.tasks||[]).forEach(x=>{if([x.title,x.role,x.brand].join(" ").toLowerCase().includes(v))matches.push({title:x.title,info:"Work item · "+humanStatus(x.status),view:"actions"})});
  (last.org?.seats||[]).forEach(x=>{if([x.title,x.role_id].join(" ").toLowerCase().includes(v))matches.push({title:x.title,info:"Company role",view:"team"})});
  connectRecords.forEach(x=>{if([x.intake_id,x.category,x.initiative].join(" ").toLowerCase().includes(v))matches.push({title:category[x.category]||x.category,info:"Connect request · "+x.intake_id,view:"connect"})});
  target.hidden=false;
  target.innerHTML=matches.length?matches.slice(0,9).map(x=>'<button type="button" data-go="'+esc(x.view)+'"><b>'+esc(x.title)+'</b><span class="muted">'+esc(x.info)+'</span></button>').join(""):'<div class="note">No matches in currently loaded records. This search does not cover private systems that are not connected.</div>';
}
function copyConnect(){
  const link="https://www.noetfield.com/connect/";
  if(!navigator.clipboard?.writeText){const b=$("copy-connect");if(b)b.textContent=link;return}
  navigator.clipboard.writeText(link).then(()=>{
    const c=$("copy-connect");if(c){c.textContent="Link copied";c.setAttribute("aria-live","polite");}
    const d=$("copy-link-main");if(d)d.textContent="Copied ✓";
  }).catch(()=>{const d=$("copy-link-main");if(d)d.textContent=link});
}
function init(){
  document.querySelectorAll("[data-go]").forEach(button=>{
    if(button.closest("#metrics"))return; // dynamically created elements handled by delegate
    if(button.classList.contains("side-link"))button.addEventListener("click",()=>showView(button.dataset.go));
  });
  document.body.addEventListener("click",e=>{
    const b=e.target.closest("[data-go]");
    if(b && !b.classList.contains("side-link")){e.preventDefault();showView(b.dataset.go);}
    if(e.target.closest("#copy-connect")||e.target.closest("#copy-link-main"))copyConnect();
  });
  $("menu-open").addEventListener("click",()=>{document.body.classList.add("nav-open");$("menu-open").setAttribute("aria-expanded","true")});
  $("menu-close").addEventListener("click",()=>{document.body.classList.remove("nav-open");$("menu-open").setAttribute("aria-expanded","false")});
  $("search-input").addEventListener("input",e=>setSearchResults(e.target.value));
  $("search-input").addEventListener("keydown",e=>{if(e.key==="Escape"){e.target.value="";setSearchResults("");}});
  document.addEventListener("keydown",e=>{
    if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==="k"){e.preventDefault();$("search-input").focus();}
    if(e.key==="Escape"){document.body.classList.remove("nav-open");$("search-results").hidden=true;}
  });
  $("new-work-form").addEventListener("submit",async event=>{
    event.preventDefault();
    const form=event.currentTarget,fields=new FormData(form);
    const body={role:String(fields.get("role")||""),brand:String(fields.get("brand")||"noetfield"),title:String(fields.get("title")||"").trim(),objective:String(fields.get("objective")||"").trim()};
    const button=$("create-work-button"),feedback=$("create-work-feedback");
    if(!form.reportValidity())return;
    button.disabled=true;feedback.textContent="Creating real work in Company OS…";
    try{
      const response=await api("/api/control/tasks",{method:"POST",body:JSON.stringify(body)});
      if(!response.created||!response.task_id)throw Error("No task receipt was returned");
      feedback.textContent="Task created: "+response.task_id+". No external action has been sent.";
      form.reset();
      await refresh();
      showView("actions");
    }catch(e){feedback.textContent="Could not create task: "+e.message;}
    finally{button.disabled=false;}
  });
  $("action-filter").addEventListener("change",()=>last&&renderActionCenter(last.t,last.o));
  window.addEventListener("hashchange",()=>showView(location.hash.slice(1),{noHash:true}));

  // Native form submit handles Enter and password-manager heuristics.
  setAuth(false,"Founder access required");
  showView(location.hash.slice(1)||"overview",{noHash:true,noScroll:true});
}
window.noosPremium={render,paintConnect,setAuth,loadHealth,showView};
init();
})();