/* GymOggle — daily tasks + solo mode
   Part of the GymOggle app. Loaded as a classic script; modules share globals. */

/* ---------- DAILY TASKS ---------- */
const EX_ICON = { squats:"🏋️", pushups:"💪", situps:"🔥", jacks:"⭐", plank:"🧱" };
let DAILY = null;

async function openDaily(){
  show("daily");
  $("dList").innerHTML = `<div class="lb-empty">Loading today's tasks…</div>`;
  try{
    const r = await fetch(HTTP_BASE + "/daily?pid=" + encodeURIComponent(PID));
    DAILY = await r.json();
    renderDaily();
  }catch(e){
    $("dList").innerHTML = `<div class="lb-empty">Couldn't load tasks.<br>(Server may be waking — try again in a moment.)</div>`;
  }
}
function renderDaily(){
  if(!DAILY || !DAILY.ok){ $("dList").innerHTML = `<div class="lb-empty">Couldn't load tasks.</div>`; return; }
  const done = new Set(DAILY.done||[]);
  $("dCoins").textContent  = DAILY.coins||0;
  $("dStreak").textContent = DAILY.streak||0;
  $("dDone").textContent   = done.size+"/3";
  $("dList").innerHTML = (DAILY.tasks||[]).map(t=>{
    const isDone = done.has(t.idx);
    const label = (EXERCISES[t.exercise]||{label:t.exercise}).label;
    const isHoldTask = (EXERCISES[t.exercise]||{}).hold === true;
    const title = isHoldTask ? `${t.target}s ${label}` : `${t.target} ${label}`;
    return `<div class="d-task${isDone?" done":""}" data-idx="${t.idx}">
      <div class="d-ico">${EX_ICON[t.exercise]||"🎯"}</div>
      <div class="d-txt"><b>${title}</b>
        <small>${isDone?"Completed ✓":"Tap to start"}</small></div>
      <div class="d-coin">${isDone?"✓":"+"+t.coins+" 🪙"}</div>
    </div>`;
  }).join("") + (done.size>=3 ? `<div class="d-all">🔥 All done — streak ${DAILY.streak}!</div>` : "");
  document.querySelectorAll(".d-task").forEach(el=>{
    if(el.classList.contains("done")) return;
    el.addEventListener("click", ()=>{
      const t = DAILY.tasks.find(x=>x.idx===+el.dataset.idx);
      if(t) startSolo(t);
    });
  });
}
$("dailyBtn").addEventListener("click", openDaily);
$("dailyBack").addEventListener("click", ()=> show("landing"));

/* ---------- SOLO MODE (run one daily task, no opponent) ---------- */
const SOLO = { on:false, task:null, reps:0, milestones:new Set() };
const BOSSES = {
  squats:  ["The Leg Day Demon","Quadzilla","The Squat Goblin"],
  pushups: ["The Floor Fiend","Baron Bench","The Chest Crusher"],
  situps:  ["The Core Kraken","Ab-solute Zero","The Crunch Lord"],
  jacks:   ["Captain Cardio","The Star Beast","Jack the Ripper"],
  plank:   ["The Iron Wall","Lord Stillness","The Endurance Beast"],
};
const SOLO_CHEERS = {
  quarter: ["Warming up 🔥","It's feeling it!","Keep going!","That's the way!"],
  half:    ["HALFWAY! 😤","It's on the ropes!","Halfway there — push!","Don't slow down!"],
  three:   ["Nearly down! 🔥","Finish it!","It's almost beaten!","One more push!"],
  last:    ["LAST ONE!! 💀","Finish. It. NOW.","One more! FINISH IT!"],
};

async function startSolo(task){
  if(busy) return;
  busy = true;
  initAudio();
  try{
    if(!landmarker) await initModel();
    await initCamera();
  }catch(e){
    busy=false;
    toast(e.name==="NotAllowedError" ? "Camera blocked — allow access and try again." : "Couldn't start camera. "+e.message);
    return;
  }
  SOLO.on=true; SOLO.task=task; SOLO.reps=0; SOLO.milestones=new Set();
  S.exercise = task.exercise;
  stage="up"; jackFeetMin=null;   // fresh stance baseline each run
  SOLO.hold = (EXERCISES[task.exercise]||{}).hold === true;
  if(SOLO.hold) wireSoloHold(task);
  else { onHoldTick=()=>{}; onHoldFailed=()=>{}; }
  const label=(EXERCISES[task.exercise]||{label:task.exercise}).label;
  const bosses = BOSSES[task.exercise] || ["The Grind"];
  $("soloTitle").textContent = label;
  $("soloBossName").textContent = pick(bosses);
  $("soloTarget").textContent = task.target + (SOLO.hold ? "s" : "");
  $("soloNow").textContent = "0";
  $("soloBar").style.width = "0%";
  $("soloHp").style.width = "100%";
  $("soloHp").classList.remove("low");
  $("soloHpTxt").textContent = task.target+" / "+task.target;
  $("soloCoins").textContent = "+"+(task.coins||10);
  $("soloHud").style.display = "flex";
  $("soloQuit").style.display = "block";
  // the gorilla trains alongside you — it mirrors YOUR reps in solo
  $("oppAvatar").setAttribute("class","avatar ex-"+S.exercise);
  const on=$("oppPanel"); if(on){ on.classList.add("on"); on.querySelector(".opp-name").textContent="Training Partner"; }
  $("oppScore").textContent = "0";
  $("raceWrap").classList.remove("on");
  const ck=$("clock"); if(ck){ ck.classList.add("hidden"); }   // daily tasks have no match timer
  show("game");
  if(!looping){ looping=true; loop(); }
  $("soloQuit").style.display = "block";       // leave option, always available
  // countdown from 5 before anything counts
  SOLO.armed = false;
  soloCountdown(()=>{
    SOLO.armed = true;
    setStatus(label+" — go!");
    speak("Go!", true);
    if(SOLO.hold){ resetHold(); }
  });
}

function soloCountdown(cb){
  let el=$("soloCount");
  if(!el){ el=document.createElement("div"); el.id="soloCount"; el.className="solo-countdown"; $("game").appendChild(el); }
  el.style.display="flex";
  let n=5;
  el.textContent=n; beep(440,.1);
  const iv=setInterval(()=>{
    n--;
    if(n>0){ el.textContent=n; beep(440,.1); }
    else if(n===0){ el.textContent="GO!"; beep(880,.18); }
    else { clearInterval(iv); el.style.display="none"; cb(); }
  }, 800);
}
/* ---------- solo PLANK: hold the clock, don't break ---------- */
function wireSoloHold(task){
  resetHold();
  onHoldTick = (secs, holding)=>{
    if(!SOLO.on || !SOLO.armed) return;   // wait for GO
    const shown = Math.min(task.target, secs);
    SOLO.reps = Math.floor(secs);
    $("soloNow").textContent = shown.toFixed(1);
    const pct = Math.min(100, secs/task.target*100);
    $("soloBar").style.width = pct+"%";
    const hp = Math.max(0, 100-pct);
    $("soloHp").style.width = hp+"%";
    $("soloHp").classList.toggle("low", hp<=35);
    $("soloHpTxt").textContent = Math.max(0,(task.target-secs)).toFixed(0)+"s left";
    // milestone hype (same as reps)
    const f = secs/task.target;
    const st = f>=0.9 ? "last" : (f>=0.75 ? "three" : (f>=0.5 ? "half" : (f>=0.25 ? "quarter" : null)));
    if(st && !SOLO.milestones.has(st)){ SOLO.milestones.add(st); flashCallout(pick(SOLO_CHEERS[st]), "ahead"); }
    if(secs >= task.target){ SOLO.reps = task.target; finishSolo(); }
  };
  onHoldFailed = ()=>{
    if(!SOLO.on) return;
    setStatus("Plank broken! Try again.", true);
    speak("Plank broken!", true);
    beep(160,0.4,"sawtooth",0.3);
    endSolo(); show("daily");
  };
}
function soloRep(){
  if(!SOLO.armed) return;          // ignore reps during the 5-count
  SOLO.reps++;
  const t=SOLO.task, left=Math.max(0, t.target-SOLO.reps);
  $("soloNow").textContent = SOLO.reps;
  const pct = Math.min(100, SOLO.reps/t.target*100);
  $("soloBar").style.width = pct+"%";
  // boss HP drains
  const hp = Math.max(0, 100-pct);
  $("soloHp").style.width = hp+"%";
  $("soloHp").classList.toggle("low", hp<=35);
  $("soloHpTxt").textContent = left+" / "+t.target;
  // the gorilla keeps pace with you
  oppRepPump(); $("oppScore").textContent = SOLO.reps;
  repPop();
  // milestone hype
  const f = SOLO.reps/t.target;
  const stage_ = left===1 ? "last" : (f>=0.75 ? "three" : (f>=0.5 ? "half" : (f>=0.25 ? "quarter" : null)));
  if(stage_ && !SOLO.milestones.has(stage_)){
    SOLO.milestones.add(stage_);
    flashCallout(pick(SOLO_CHEERS[stage_]), stage_==="last" ? "behind" : "ahead");
  }
  if(SOLO.reps >= t.target) finishSolo();
}
async function finishSolo(){
  const task = SOLO.task, reps = SOLO.reps;
  endSolo();
  confettiBurst && confettiBurst();
  speak("Task complete!", true);
  toast("Task complete! 🪙");
  try{
    const r = await fetch(HTTP_BASE + "/daily/complete", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({ pid:PID, name:S.name||($("name").value.trim()||"Player"),
                             task_idx:task.idx, exercise:task.exercise, reps:reps })
    });
    const d = await r.json();
    if(d.ok){
      if(d.earned) toast("+"+d.earned+" coins!");
      if(d.all_done) speak("All daily tasks complete! Streak "+d.streak, true);
    }
  }catch(e){}
  openDaily();   // refresh the board
}
function endSolo(){
  SOLO.on=false; busy=false;
  onHoldTick=()=>{}; onHoldFailed=()=>{};
  const ck=$("clock"); if(ck){ ck.classList.remove("hidden"); }
  $("soloHud").style.display="none";
  $("soloQuit").style.display="none";
  $("oppPanel").classList.remove("on");
  const nm=$("oppPanel").querySelector(".opp-name"); if(nm) nm.textContent="Opponent";
  $("callout").classList.remove("show");
  setStatus("");
}
$("soloQuit").addEventListener("click", ()=>{ endSolo(); show("daily"); });