/* GymOggle — 30-DAY JOURNEY
   A Duolingo-style path of 30 days. One weekly template, volume rising each week.
   Reuses existing detection via the onRep / onHoldTick hooks — does NOT touch multiplayer.js.
   Progress saved locally for now (moves to the account when login lands). */

const JOURNEY_KEY = "gymoggle_journey_v1";
const J_LOTTIE = {};                 // cache of loaded animation JSON

/* ---- the weekly template (Mon..Sun). Volume scales per week. ---- */
// type: "count" (camera reps) | "hold" (plank seconds) | "coach" (animation+timer) | "battle" | "rest"
const WEEK = [
  { focus:"Lower Body", icon:"🦵", items:[
      {ex:"squats", type:"count", base:12, add:4},
      {ex:"lunges", type:"coach", anim:"lunges", sets:"3 × 10 each leg", secs:40},
      {ex:"glute-bridges", type:"coach", anim:"glute-bridges", sets:"3 × 15", secs:40},
  ]},
  { focus:"Upper Body", icon:"💪", items:[
      {ex:"pushups", type:"count", base:8, add:2},
      {ex:"tricep-dips", type:"coach", anim:"tricep-dips", sets:"3 × 10", secs:40},
      {ex:"plank", type:"hold", base:20, add:10},
  ]},
  { focus:"Cardio", icon:"🔥", items:[
      {ex:"jacks", type:"count", base:20, add:6},
      {ex:"high-knees", type:"coach", anim:"high-knees", sets:"40 seconds", secs:40},
      {ex:"mountain-climbers", type:"coach", anim:"generic", sets:"3 × 20", secs:40},
  ]},
  { focus:"Rest", icon:"😌", rest:true, items:[
      {ex:"rest", type:"rest", anim:"rest", secs:60},
  ]},
  { focus:"Core", icon:"🎯", items:[
      {ex:"plank", type:"hold", base:20, add:10},
      {ex:"russian-twists", type:"coach", anim:"russian-twists", sets:"3 × 20", secs:40},
      {ex:"dead-bug", type:"coach", anim:"generic", sets:"3 × 12", secs:40},
  ]},
  { focus:"Battle Day", icon:"⚔️", items:[
      {ex:"battle", type:"battle"},
  ]},
  { focus:"Rest", icon:"😌", rest:true, items:[
      {ex:"wall-sit", type:"coach", anim:"wall-sit", sets:"3 × 30 seconds", secs:40},
  ]},
];
const EX_NAME = {
  squats:"Squats", pushups:"Push-ups", jacks:"Jumping Jacks", plank:"Plank",
  lunges:"Lunges", "glute-bridges":"Glute Bridges", "tricep-dips":"Tricep Dips",
  "high-knees":"High Knees", "mountain-climbers":"Mountain Climbers",
  "russian-twists":"Russian Twists", "dead-bug":"Dead Bug", "wall-sit":"Wall Sit",
  rest:"Recovery & Breathing", battle:"Live Battle",
};
const TOTAL_DAYS = 30;

/* ---- progress ---- */
function jLoad(){
  try{ return JSON.parse(localStorage.getItem(JOURNEY_KEY)) || {done:{}, current:1}; }
  catch(e){ return {done:{}, current:1}; }
}
function jSave(p){ try{ localStorage.setItem(JOURNEY_KEY, JSON.stringify(p)); }catch(e){} }
let JP = jLoad();

/* the plan for a given day number (1..30). week index cycles; volume rises each week. */
function dayPlan(day){
  const wi = (day-1) % 7;                    // day of week
  const week = Math.floor((day-1) / 7);      // 0-based week -> volume tier
  const t = WEEK[wi];
  const items = t.items.map(it=>{
    const o = {...it, name:EX_NAME[it.ex]||it.ex};
    if(it.type==="count") o.target = it.base + it.add*week;
    if(it.type==="hold")  o.target = it.base + it.add*week;
    return o;
  });
  return { day, focus:t.focus, icon:t.icon, rest:!!t.rest, items };
}

/* ---- the map screen ---- */
function openJourney(){
  JP = jLoad();
  show("journey");
  renderMap();
}
function renderMap(){
  const done = Object.keys(JP.done).length;
  $("jProgFill").style.width = (done/TOTAL_DAYS*100)+"%";
  $("jProgTxt").textContent = `Day ${Math.min(JP.current,TOTAL_DAYS)} of ${TOTAL_DAYS}`;
  const path = $("jPath");
  let html = "";
  for(let day=1; day<=TOTAL_DAYS; day++){
    const p = dayPlan(day);
    const state = JP.done[day] ? "done" : (day===JP.current ? "today" : (day<JP.current ? "done" : "locked"));
    const side = day%2 ? "left" : "right";
    html += `<button class="j-node ${state} ${side}" data-day="${day}" ${state==="locked"?"disabled":""}>
      <span class="j-ico">${JP.done[day]?"✓":p.icon}</span>
      <span class="j-day">Day ${day}</span>
      <span class="j-focus">${p.focus}</span>
    </button>`;
  }
  path.innerHTML = html;
  path.querySelectorAll(".j-node:not(.locked)").forEach(n=>
    n.addEventListener("click", ()=> openDay(+n.dataset.day)));
  // scroll today into view
  const t = path.querySelector(".j-node.today"); if(t) t.scrollIntoView({block:"center"});
}

/* ---- day screen: the checklist ---- */
let curDay = null, dayItemState = [];
function openDay(day){
  curDay = day;
  const p = dayPlan(day);
  dayItemState = p.items.map(()=>false);
  show("jday");
  $("jdayTitle").textContent = `Day ${day} · ${p.focus}`;
  $("jdayIcon").textContent = p.icon;
  renderDayList();
}
function renderDayList(){
  const p = dayPlan(curDay);
  $("jdayList").innerHTML = p.items.map((it,i)=>{
    const label = it.type==="count" ? `${it.target} ${it.name}`
                : it.type==="hold"  ? `${it.target}s ${it.name}`
                : it.type==="battle"? `Win a live battle`
                : it.type==="rest"  ? it.name
                : `${it.name} · ${it.sets}`;
    const tag = it.type==="count"||it.type==="hold" ? "🎥"
              : it.type==="battle" ? "⚔️" : it.type==="rest" ? "😌" : "⏱️";
    return `<button class="jd-item ${dayItemState[i]?"done":""}" data-i="${i}">
      <span class="jd-tag">${tag}</span>
      <span class="jd-label">${label}</span>
      <span class="jd-check">${dayItemState[i]?"✓":"›"}</span>
    </button>`;
  }).join("");
  $("jdayList").querySelectorAll(".jd-item").forEach(b=>
    b.addEventListener("click", ()=> startItem(+b.dataset.i)));
  const allDone = dayItemState.every(Boolean);
  $("jdayFinish").style.display = allDone ? "block" : "none";
}

/* ---- run one item ---- */
function itemComplete(i){
  dayItemState[i] = true;
  beep(880,.08); 
  show("jday"); renderDayList();
}

function startItem(i){
  if(dayItemState[i]) return;               // already done
  const it = dayPlan(curDay).items[i];
  if(it.type==="count")      jCount(it, i);
  else if(it.type==="hold")  jHold(it, i);
  else if(it.type==="coach") jCoach(it, i);
  else if(it.type==="rest")  jCoach(it, i);
  else if(it.type==="battle")jBattle(it, i);
}

/* COUNTED — a clean rep counter (no boss/coins UI). Uses the onRep hook. */
async function jCount(it, i){
  show("jrun");
  S.exercise = it.ex; stage="up"; jackFeetMin=null;
  let n = 0;
  $("jrunName").textContent = it.name;
  $("jrunNow").textContent = "0";
  $("jrunTarget").textContent = it.target;
  $("jrunBar").style.width = "0%";
  $("jrunHint").textContent = "Get in frame — go!";
  try{ if(!landmarker) await initModel(); await initCamera(); }
  catch(e){ toast("Camera error — allow access"); show("jday"); return; }
  mountJrunCam();
  if(!looping){ looping=true; loop(); }
  onRep = ()=>{
    n++; $("jrunNow").textContent = n;
    $("jrunBar").style.width = Math.min(100, n/it.target*100)+"%";
    repPop(); beep(660,.05);
    if(n>=it.target){ onRep=null; jRunDone(i); }
  };
  $("jrunQuit").onclick = ()=>{ onRep=null; show("jday"); };
}

/* HOLD (plank) — uses onHoldTick/onHoldFailed */
async function jHold(it, i){
  show("jrun");
  S.exercise = "plank"; 
  $("jrunName").textContent = it.name;
  $("jrunNow").textContent = "0.0";
  $("jrunTarget").textContent = it.target+"s";
  $("jrunBar").style.width = "0%";
  $("jrunHint").textContent = "Hold the plank!";
  try{ if(!landmarker) await initModel(); await initCamera(); }
  catch(e){ toast("Camera error"); show("jday"); return; }
  mountJrunCam();
  if(!looping){ looping=true; loop(); }
  resetHold();
  onHoldTick = (secs, holding)=>{
    $("jrunNow").textContent = Math.min(it.target, secs).toFixed(1);
    $("jrunBar").style.width = Math.min(100, secs/it.target*100)+"%";
    $("jrunHint").textContent = holding ? "Hold it!" : "Get into a plank…";
    if(secs >= it.target){ onHoldTick=()=>{}; onHoldFailed=()=>{}; jRunDone(i); }
  };
  onHoldFailed = ()=>{ $("jrunHint").textContent = "Broke! Get back into position…"; };
  $("jrunQuit").onclick = ()=>{ onHoldTick=()=>{}; onHoldFailed=()=>{}; show("jday"); };
}
function mountJrunCam(){
  const box=$("jrunCam"); if(!box) return; box.innerHTML="";
  const v=document.createElement("video"); v.autoplay=true; v.muted=true; v.playsInline=true;
  v.srcObject = window.camStream; box.appendChild(v);
}
function jRunDone(i){
  confettiBurst && confettiBurst(); speak("Nice!", true); beep(990,.12);
  show("jday"); itemComplete(i);
}

/* COACH / REST — animation + timer + Done */
function jCoach(it, i){
  show("jcoach");
  $("jcoachName").textContent = it.name;
  $("jcoachSets").textContent = it.sets || "";
  const box=$("jcoachAnim"); box.innerHTML="";
  loadLottie(box, it.anim||"generic");
  let left = it.secs || 40;
  $("jcoachTimer").textContent = left+"s";
  const done=$("jcoachDone");
  done.disabled=true; done.textContent="Wait…";
  clearInterval(window._jcIv);
  window._jcIv = setInterval(()=>{
    left--; $("jcoachTimer").textContent = Math.max(0,left)+"s";
    if(left<=0){ clearInterval(window._jcIv); done.disabled=false; done.textContent="Done ✓"; beep(880,.1); }
  }, 1000);
  done.onclick = ()=>{ if(done.disabled) return; clearInterval(window._jcIv); show("jday"); itemComplete(i); };
  $("jcoachQuit").onclick = ()=>{ clearInterval(window._jcIv); show("jday"); };
}

/* BATTLE — hand off to existing 1v1 (untouched). Completing the day is on return. */
function jBattle(it, i){
  // mark battle "attempted" — completing an actual match is bonus; we don't block the map on matchmaking
  toast("Loading live battle…");
  dayItemState[i] = true;   // starting the battle counts for map progress (forgiving)
  renderDayList();
  if(typeof enterGame==="function"){ enterGame("quick", null); }
  else { show("landing"); }
}

/* ---- finish the day ---- */
async function finishDay(){
  if(!dayItemState.every(Boolean)) return;
  JP.done[curDay] = true;
  if(curDay===JP.current && JP.current<TOTAL_DAYS) JP.current++;
  jSave(JP);
  confettiBurst && confettiBurst(); speak("Day complete!", true);
  // award coins into the existing economy
  try{
    await fetch(HTTP_BASE + "/journey/complete", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({ pid:PID, name:S.name||"Player", day:curDay })
    });
  }catch(e){}
  toast("Day "+curDay+" complete! +20 🪙");
  show("journey"); renderMap();
}

/* ---- lottie loader (cached) ---- */
function loadLottie(container, key){
  if(!window.lottie){ container.textContent="🏋️"; container.style.fontSize="72px"; return; }
  const draw = data => window.lottie.loadAnimation({container, renderer:"svg", loop:true, autoplay:true, animationData:data});
  if(J_LOTTIE[key]){ draw(J_LOTTIE[key]); return; }
  fetch("assets/ex/"+key+".json").then(r=>r.json()).then(data=>{ J_LOTTIE[key]=data; draw(data); })
    .catch(()=>{ container.textContent="🏋️"; container.style.fontSize="72px"; });
}

/* ---- wire entry ---- */
(function(){
  const b=$("journeyBtn"); if(b) b.addEventListener("click", openJourney);
  const back=$("jBack"); if(back) back.addEventListener("click", ()=> show("landing"));
  const dback=$("jdayBack"); if(dback) dback.addEventListener("click", ()=>{ show("journey"); renderMap(); });
  const fin=$("jdayFinish"); if(fin) fin.addEventListener("click", finishDay);
})();