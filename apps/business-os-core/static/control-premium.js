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
const pictograms={"target":"<circle cx=\"12\" cy=\"12\" r=\"9\"/><circle cx=\"12\" cy=\"12\" r=\"5\"/><circle cx=\"12\" cy=\"12\" r=\"1\"/>","check":"<rect x=\"4\" y=\"3\" width=\"16\" height=\"18\" rx=\"3\"/><path d=\"m8 12 3 3 5-6\"/>","activity":"<path d=\"M2 12h5l3-8 4 16 3-8h5\"/>","revenue":"<ellipse cx=\"12\" cy=\"5\" rx=\"8\" ry=\"3\"/><path d=\"M4 5v13c0 4 16 4 16 0V5M4 12c0 4 16 4 16 0\"/>","inbox":"<path d=\"M4 4h16l2 12v4H2v-4L4 4Z\"/><path d=\"M2 15h6l2 3h4l2-3h6\"/>","person":"<circle cx=\"12\" cy=\"8\" r=\"4\"/><path d=\"M5 21v-2a7 7 0 0 1 14 0v2\"/>","code":"<path d=\"m8 8-4 4 4 4m8-8 4 4-4 4m-6 3 4-12\"/>","link":"<path d=\"m10 13 4-4M8 16H6a4 4 0 0 1 0-8h4m4 0h4a4 4 0 0 1 0 8h-4\"/>","arrow":"<path d=\"M4 12h16m-6-6 6 6-6 6\"/>","grid":"<path d=\"M4 3h7v8H4zM13 3h7v8h-7zM4 13h7v8H4zM13 13h7v8h-7z\"/>"};
const pictogram=name=>'<svg class="ui-icon" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'+(pictograms[name]||pictograms.grid)+'</svg>';
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
function metric(label,value,note,icon,view,kind,linkText){
  const word=String(value).length>8;
  return '<article class="metric '+(kind||"")+'"><div class="metric-ico">'+pictogram(icon)+'</div>'+
    '<span>'+esc(label)+'</span><strong class="'+(word?'is-word':'')+'">'+esc(value)+'</strong>'+
    (note?'<small>'+esc(note)+'</small>':'')+
    '<div><a href="#'+view+'" data-go="'+view+'">'+esc(linkText||"View details")+' →</a></div></article>';
}
let last=null,connectRecords=[],currentView="";
let dashboardSnapshot=null,dashboardReq=0;
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
  if(name==="health"){loadHealth();if(!document.body.classList.contains("locked"))void loadRuntimeMesh();}
  if(name==="actions"&&!document.body.classList.contains("locked"))loadTaskInbox();
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
  if(isConnected){showView((location.hash||"#overview").slice(1),{noHash:true,noScroll:true});if(last&&typeof api==="function")void loadDashboard();}
}
function formatTask(x){
  return "<div class='action-item'><span class='action-mark' aria-hidden='true'>☷</span><div><b>"+esc(x.title||"Review work")+"</b><p>"+esc(role[x.role]||x.company_role_title||"Company operations")+" · "+esc(humanStatus(x.status))+" · "+esc(x.brand||"Portfolio")+"</p></div><button class='btn alt' type='button' data-task-focus='"+esc(x.id)+"'>Review →</button></div>";
}

const taskInboxState={offset:0,limit:40,loaded:false,requestId:0};
function taskRow(x){
  let details={};try{details=JSON.parse(x.result||"{}")}catch{}
  const recommendation=details.recommendation||{};
  return '<tr data-task-row="'+esc(x.id)+'"><td><b>'+esc(x.title||"Untitled work")+'</b>'+
    '<span class="muted">'+esc(x.brand||"Portfolio")+' · '+esc(x.id)+'</span>'+
    '<details class="task-detail"><summary>Context</summary><p>'+esc(x.objective||"No further context recorded")+'</p></details></td>'+
    '<td>'+esc(role[x.role]||x.role)+'<span class="muted">'+esc(x.company_role_title||"")+'</span></td>'+
    '<td>'+labelTag(x.status)+'<span class="muted">'+safeNumber(x.pending_dependencies||0)+' waiting dependencies</span></td>'+
    '<td>'+esc(recommendation.next_best_action||x.next_action||"No next step recorded")+'</td>'+
    '<td>'+(x.status==="drafted"?'<button class="btn alt" data-approve="'+esc(x.id)+'">Record approval</button>':'<span class="muted">No action available</span>')+'</td></tr>';
}
async function loadTaskInbox(reset=false){
  if(reset)taskInboxState.offset=0;
  if(document.body.classList.contains("locked"))return;
  const id=++taskInboxState.requestId;
  const params=new URLSearchParams({limit:String(taskInboxState.limit),offset:String(taskInboxState.offset)});
  const status=$("action-filter").value,brand=$("task-brand").value,q=$("task-search").value.trim();
  if(status)params.set("status",status);
  if(brand)params.set("brand",brand);
  if(q)params.set("q",q);
  $("task-list-scope").textContent="Loading tasks from the full Company OS queue…";
  $("task-prev").disabled=true;$("task-next").disabled=true;
  try{
    const d=await api("/api/control/task-inbox?"+params.toString());
    if(id!==taskInboxState.requestId)return;
    if(d.schema!=="noetfield.business-os.task-inbox.v1"||!Array.isArray(d.tasks))throw Error("Unsupported task inbox response");
    taskInboxState.loaded=true;
    const start=d.total?d.offset+1:0,end=d.offset+d.tasks.length;
    $("tasks").innerHTML=d.tasks.length?d.tasks.map(taskRow).join(""):'<tr><td colspan="5"><div class="empty"><h3>No matching work</h3><p>Adjust your filters or try another search.</p></div></td></tr>';
    $("task-list-scope").textContent="Showing "+start+"–"+end+" of "+safeNumber(d.total)+" matching tasks from Company OS.";
    $("task-prev").disabled=taskInboxState.offset===0;
    $("task-next").disabled=!d.has_more;
  }catch(err){
    if(id!==taskInboxState.requestId)return;
    $("tasks").innerHTML='<tr><td colspan="5"><div class="empty"><h3>Could not load your work</h3><p>Task data has not been changed.</p><button class="btn alt" type="button" data-retry-inbox>Try again</button></div></td></tr>';
    $("task-list-scope").textContent="Work inbox unavailable: "+err.message;
  }
}

function referenceActionRow(icon,title,badge,desc,destination,cta,tone){
  return '<div class="reference-action-row"><span class="ref-action-icon">'+pictogram(icon)+'</span>'+
    '<div class="ref-action-copy"><strong>'+esc(title)+'</strong><span class="tag '+(tone||'neutral')+'">'+esc(badge)+'</span>'+
    '<p>'+esc(desc)+'</p></div><button class="ref-link" type="button" data-go="'+destination+'">'+esc(cta)+' '+pictogram('arrow')+'</button></div>';
}
function renderActionCenter(t,overview){
  const count=overview?.counts?.pending_tasks;
  $('action-count').textContent=count===undefined?'—':safeNumber(count);
  $('action-count-hint').textContent=count===undefined?'Unable to read pending work':'Company OS durable task queue';
  $('nav-action-count').textContent=count===undefined?'—':count>999?(count/1000).toFixed(1)+'K':String(count);
  const label=count===undefined?'Unavailable':safeNumber(count)+' pending';
  const sourceLoaded=$('connect-count').textContent!=='—';
  const connectCount=sourceLoaded?Number($('connect-count').textContent.replace(/,/g,'')):null;
  const fresh=connectCount===null?'Checking…':safeNumber(connectCount)+' recent';
  $('action-preview').innerHTML=
    referenceActionRow('check','Task backlog',label,'Review and prioritize the existing queue.','actions','Open queue','warn')+
    referenceActionRow('target','Incoming opportunities',fresh,'Review submitted proposals and partnership requests.','connect','Open Connect','neutral')+
    referenceActionRow('revenue','Revenue visibility','Not connected','Link verified financial data to track collected cash.','revenue','View revenue','neutral');
  if(!taskInboxState.loaded)$('task-list-scope').textContent='Open Action Center to load the complete Company OS work queue.';
}
function renderTeam(org){
  const seats=org?.seats||[];
  const pick=(id)=>seats.find(x=>x.role_id===id);
  const selected=[pick('N-01'),pick('N-02'),pick('N-03')].filter(Boolean);
  if(!selected.length)selected.push(...seats.slice(0,3));
  const compactLabel=(x)=>{
    if(x.role_id==='N-01')return 'Chief of Staff';
    if(x.role_id==='N-02')return 'Opportunity Intelligence';
    if(x.role_id==='N-03')return 'Engineering Delivery';
    return String(x.title||'Company specialist').replace(/Officer|& Operations/gi,'').trim();
  };
  $('team-summary').innerHTML=selected.length?selected.map(x=>{
    const isPartial=String(x.activation_status||'').includes('partial');
    const status=isPartial?'Partial':String(x.activation_status||'').includes('mapped')?'Configured':'Not verified';
    const glyph=x.role_id==='N-03'?'code':x.role_id==='N-02'?'target':'person';
    return '<div class="team-compact-row"><span class="ref-action-icon">'+pictogram(glyph)+'</span>'+
      '<strong>'+esc(compactLabel(x))+'</strong><span class="tag '+(isPartial?'warn':'')+'">'+esc(status)+'</span></div>';
  }).join(''):'<div class="empty"><h3>Team registry unavailable</h3><p>Connect the Company OS roster to see configured roles.</p></div>';
  $('agents').innerHTML=seats.length?'<div class="stack-list">'+seats.map(x=>{
    const activation=String(x.activation_status||'').toLowerCase();
    const readable=activation.includes('mapped')?'Configured':activation.includes('partial')?'Partially available':humanStatus(x.activation_status);
    return '<details class="agent-item"><summary><span><b>'+esc(x.title||x.role_id)+'</b>'+
      '<span class="muted">'+esc((x.runtime_role_names||[]).join(' · ')||'No runtime specialist mapped')+'</span></span>'+
      '<span class="tag '+(activation.includes('partial')?'warn':'neutral')+'">'+esc(readable)+'</span></summary>'+
      '<div class="agent-item__body"><p class="helper">'+esc(x.activation_meaning||'Registry entry only. Live execution must be checked separately.')+'</p>'+
      '<p class="muted">Reporting to: '+esc(x.manager_name||'Founder')+'</p>'+
      '<details><summary class="muted">Technical details</summary><p class="helper">Seat '+esc(x.role_id)+' · Layer '+esc(x.layer)+' · Authority '+esc(x.max_authority||'not specified')+'</p></details></div></details>';
  }).join('')+'</div>':'<div class="empty">Team data is not loaded.</div>';
  const a=org?.organization?.company_role_count,b=org?.organization?.runtime_executor_count;
  $('team-total').textContent=safeNumber(a);
  $('capability-total').textContent=safeNumber(b);
  $('capacity-inline').textContent=a===undefined||b===undefined?'Not available':safeNumber(a)+' company roles · '+safeNumber(b)+' capabilities';
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
  connectRecords=unavailable?[]:items;
  const venture=$('dashboard-venture').value;
  const matching=connectRecords.filter(x=>!venture||x.initiative===venture);
  const active=matching.filter(x=>!['ARCHIVED','DECLINED','CLOSED_LOST'].includes(x.case_stage));
  if(unavailable){
    $('connect-summary').innerHTML='<div class="ref-empty"><span class="ref-connection-error">Incoming opportunities could not be loaded.</span>'+
      '<p>Your source records have not been deleted. Check the Connect inbox for details.</p>'+
      '<button class="ref-link" data-go="connect" type="button">Open Connect '+pictogram('arrow')+'</button></div>';
    $('connect-count').textContent='—';$('connect-open').textContent='—';$('connect-scope').textContent='Connect feed unavailable';
  }else{
    $('connect-count').textContent=safeNumber(matching.length);
    $('connect-open').textContent=safeNumber(active.length);
    $('connect-scope').textContent=matching.length+' recent linked requests in the source feed (maximum 100).';
    const records=active.slice(0,3);
    $('connect-summary').innerHTML=records.length?'<div class="ref-connect-list">'+records.map(x=>
      '<div class="reference-action-row"><span class="ref-action-icon">'+pictogram('target')+'</span>'+
      '<div class="ref-action-copy"><strong>'+esc(category[x.category]||x.category)+'</strong>'+
      '<span class="tag neutral">'+esc(humanStatus(x.case_stage))+'</span>'+
      '<p>'+esc(x.initiative)+' · '+esc(x.source_channel)+'</p></div>'+
      '<button type="button" class="ref-link" data-go="connect">Review '+pictogram('arrow')+'</button></div>'
    ).join('')+'</div>':
    '<div class="ref-empty"><span class="ref-empty-icon">'+pictogram('inbox')+'</span>'+
      '<h3>No relationship opportunities yet</h3>'+
      '<p>Share the Connect link to invite proposals, partnerships, investment, talent, or other collaboration opportunities.</p>'+
      '<div class="ref-empty-actions"><button id="copy-connect" class="btn" type="button">'+pictogram('link')+' Copy public link</button>'+
      '<a class="ref-link" href="https://www.noetfield.com/connect/" target="_blank" rel="noopener noreferrer">Open intake '+pictogram('arrow')+'</a></div></div>';
  }
  if(last){
    const counts=dashboardSnapshot?.counts||last.o?.counts||{};
    renderActionCenter(last.t,{counts:{...last.o?.counts,...counts}});
  }
}


function renderActivityTrend(d){
  if(!d||!Array.isArray(d.activity_daily)){
    $('activity-bars').innerHTML='<span class="activity-loading">Activity source unavailable</span>';
    $('activity-bars').setAttribute('aria-label','Activity source unavailable');
    return;
  }
  const daily=d.days===30?d.activity_daily.slice(-15):d.activity_daily;
  const max=Math.max(0,...daily.map(x=>Number(x.count)||0));
  if(!max){
    $('activity-bars').innerHTML='<span class="activity-loading">No events recorded</span>';
    $('activity-bars').setAttribute('aria-label','No events recorded in the selected period');
  }else{
    $('activity-bars').innerHTML=daily.map(x=>{
      const height=(Math.max(0,Number(x.count)||0)/max*65);
      return '<span class="activity-bar" title="'+esc(x.date)+': '+safeNumber(x.count)+' recorded events" style="height:'+height.toFixed(1)+'px"></span>';
    }).join('');
    $('activity-bars').setAttribute('aria-label',daily.map(x=>x.date+': '+x.count+' events').join(', '));
  }
  $('activity-week').textContent=safeNumber(d.counts?.activity_events);
  $('activity-unit').textContent='events / last '+d.days+' days';
}
function renderSummaryMetrics(d){
  const fallback=last?.o?.counts||{};
  const counts=d?.counts||fallback;
  const activity=d?.counts?.activity_events;
  const days=d?.days||Number($('dashboard-period').value)||7;
  const pending=counts.pending_tasks;
  const opportunities=counts.active_opportunities??counts.opportunities;
  $('metrics').innerHTML=[
    metric('Active opportunities',safeNumber(opportunities),'','target','opportunities','','View opportunities'),
    metric('Pending tasks',safeNumber(pending),'','check','actions','attention','Review workload'),
    metric('Activity · last '+days+' days',safeNumber(activity??null),'','activity','activity','','View activity'),
    metric('Collected revenue','Not connected','Financial source not linked','revenue','revenue','','View revenue')
  ].join('');
}
async function loadDashboard(){
  if(document.body.classList.contains('locked'))return;
  const id=++dashboardReq,brand=$('dashboard-venture').value,days=$('dashboard-period').value;
  const params=new URLSearchParams({days});
  if(brand)params.set('brand',brand);
  try{
    const d=await api('/api/control/dashboard?'+params);
    if(id!==dashboardReq)return;
    if(d.source!=='Company OS durable tables'||!d.counts)throw Error('Unsupported summary data');
    dashboardSnapshot=d;
    renderSummaryMetrics(d);
    renderActivityTrend(d);
    $('last-updated').textContent='Updated '+new Date(d.as_of).toLocaleString('en-CA');
    $('data-note').textContent=d.scope||'Live Company OS data; unverified activity is not collected revenue.';
    if(last)renderActionCenter(last.t,{counts:{...last.o?.counts,...d.counts}});
    if(connectRecords)paintConnect(connectRecords);
  }catch(err){
    if(id!==dashboardReq)return;
    dashboardSnapshot=null;
    $('activity-bars').innerHTML='<span class="activity-loading">Trend unavailable</span>';
    $('activity-week').textContent='—';
    $('metrics').innerHTML='<div class="empty">Dashboard totals are temporarily unavailable. Existing records remain accessible in their individual sections.</div>';
    $('data-note').textContent='Dashboard summary unavailable: '+err.message;
  }
}
function render(data){
  last=data;
  const {o,org,op,t,e,r,roi}=data;
  const counts=o?.counts||{};
  const asStat=(key)=>counts[key]===undefined?"—":safeNumber(counts[key]);
  const detail=[
    ["Contacts",asStat("contacts"),"Business OS contact records"],
    ["Qualified",asStat("qualified"),"Score of 65 or higher; not a sale"],
    ["Reported wins",asStat("won"),"Recorded won stage, not verified cash"],
    ["Queued events",asStat("queued_events"),"System events awaiting processing"],
    ["Imported requests",asStat("platform_intake_signals"),"Linked intake source records"],
    ["Requests to process",asStat("platform_intake_pending"),"Received, not yet routed"],
    ["Routed requests",asStat("platform_intake_tasks_created"),"Internal review tasks created"],
    ["Weighted pipeline",o?.weighted_pipeline_cad===undefined?"—":Number(o.weighted_pipeline_cad).toLocaleString("en-CA",{style:"currency",currency:"CAD",maximumFractionDigits:0}),"Estimate only — not revenue"]
  ];
  $("pulse-metrics").innerHTML=detail.map(([label,value,description])=>
    '<div class="compact-metric"><span>'+esc(label)+'</span><strong>'+esc(value)+'</strong><small>'+esc(description)+'</small></div>'
  ).join("");
  renderSummaryMetrics(null);
  $('worker-cycle-value').textContent=o?.worker_interval_seconds?('Every '+o.worker_interval_seconds+' seconds'):'Unknown';
  $('llm-config-value').textContent=o?.llm_configured===true?'✓ Configured':o?.llm_configured===false?'Needs setup':'Not verified';
  $('llm-config-value').className='tag '+(o?.llm_configured===true?'good':'warn');
  if(!dashboardSnapshot)renderActivityTrend(null);
  // The dashboard endpoint supplies brand-scoped counts and real daily activity history.
  // Summary request begins after authenticated workspace unlocks.
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
async function loadRuntimeMesh(){
  const output=$("runtime-mesh");
  if(document.body.classList.contains("locked")){output.textContent="Founder access required.";return;}
  output.textContent="Checking existing execution services…";
  try{
    const data=await api("/api/control/runtime-mesh");
    if(data.schema!=="noetfield.company-os.runtime-mesh-observation.v1"||!Array.isArray(data.nodes))throw Error("Invalid source response");
    const handoff=data.founder_handoff||{};
    const header='<div class="status-line"><span><b>Founder → Company handoff</b><br><span class="muted">Received WorkPackets: '+safeNumber(handoff.work_packets_claimed)+' · Pending ACK: '+safeNumber(handoff.pending_ack)+' · Independently verified outcomes: '+safeNumber(handoff.verified_outcomes)+'</span></span>'+labelTag(handoff.state||"NOT_OBSERVED")+'</div>';
    const rows=data.nodes.map(node=>{
      const status=node.state||"NOT_OBSERVED";
      const good=["SERVICE_HEALTH_REPORTED","GOAL_KERNEL_HEALTH_REPORTED","HTTP_REACHABLE_ONLY","LOCAL_CONTROL_SURFACE"].includes(status);
      const href=typeof node.url==="string"&&node.url.startsWith("https://")?node.url:null;
      const label=href?'<a href="'+esc(href)+'" target="_blank" rel="noopener noreferrer">'+esc(node.label)+'</a>':esc(node.label);
      return '<div class="status-line"><span><b>'+label+'</b><br><span class="muted">'+esc(humanStatus(status))+'</span></span><span class="tag '+(good?"":"warn")+'">'+(good?"Endpoint only":"Unproven")+'</span></div>';
    }).join("");
    output.innerHTML=header+rows+'<p class="helper">Source health and a WorkPacket ACK do not prove authorized Motor execution, a deployed change, independent verification or collected revenue. Runway remains the canonical execution engine.</p>';
  }catch(e){output.textContent="Cannot read execution chain: "+e.message;}
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
  $('dashboard-venture').addEventListener('change',()=>{
    if(document.body.classList.contains('locked'))return;
    $('task-brand').value=$('dashboard-venture').value;
    void loadDashboard();
  });
  $('dashboard-period').addEventListener('change',()=>void loadDashboard());
  $("action-filter").addEventListener("change",()=>loadTaskInbox(true));
  $("task-brand").addEventListener("change",()=>loadTaskInbox(true));
  $("task-inbox-controls").addEventListener("submit",e=>{e.preventDefault();loadTaskInbox(true)});
  $("task-next").addEventListener("click",()=>{taskInboxState.offset+=taskInboxState.limit;loadTaskInbox()});
  $("task-prev").addEventListener("click",()=>{taskInboxState.offset=Math.max(0,taskInboxState.offset-taskInboxState.limit);loadTaskInbox()});
  document.body.addEventListener("click",e=>{
    if(e.target.closest("[data-retry-inbox]"))loadTaskInbox();
    const focus=e.target.closest("[data-task-focus]");
    if(focus){$("task-search").value=focus.dataset.taskFocus;showView("actions");loadTaskInbox(true);}
  });
  window.addEventListener("hashchange",()=>showView(location.hash.slice(1),{noHash:true}));

  // Native form submit handles Enter and password-manager heuristics.
  setAuth(false,"Founder access required");
  showView(location.hash.slice(1)||"overview",{noHash:true,noScroll:true});
}
window.noosPremium={render,paintConnect,setAuth,loadHealth,showView,loadTaskInbox};
init();
})();