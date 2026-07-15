/* GymOggle — multiplayer: SACRED. Validated with strangers in a gym. Change with care.
   Part of the GymOggle app. Loaded as a classic script; modules share globals. */

/* ---------- networking ---------- */
let ws=null;
function connect(){
  // kill any previous/orphan socket so a late-opening one can't send stray messages
  try{ if(ws){ ws.onopen=ws.onmessage=ws.onerror=ws.onclose=null; ws.close(); } }catch(e){}
  try{ ws=new WebSocket(SERVER_URL); }
  catch(e){ setStatus("Bad server address",true); return; }

  ws.onopen = ()=>{
    if(S.intent==="create") ws.send(JSON.stringify({type:"create", exercise:chosenExercise, pid:PID, name:S.name}));
    else if(S.intent==="join") ws.send(JSON.stringify({type:"join", code:S.code, pid:PID, name:S.name}));
    else if(S.intent==="quick") ws.send(JSON.stringify({type:"quick", exercise:chosenExercise, pid:PID, name:S.name}));
  };
  ws.onmessage = ev=>{
    const d=JSON.parse(ev.data), t=d.type;
    if(t==="created"){ S.me=d.you; S.code=d.code; if(d.exercise) S.exercise=d.exercise; showShareCode(d.code); }
    else if(t==="joined"){ S.me=d.you; S.code=d.code; if(d.exercise) S.exercise=d.exercise;
      centerWait("Joining "+exLabel()+" battle…","Getting you into the match"); }
    else if(t==="searching"){ if(d.exercise) S.exercise=d.exercise; showSearching(); }
    else if(t==="matched"){ S.me=d.you; if(d.exercise) S.exercise=d.exercise;
      centerWait("Opponent found!","Get ready to battle"); }
    else if(t==="lobby"){ if(d.names) S.oppName=d.names[other(S.me)]||"Opponent"; openLobby(d.duration); }
    else if(t==="chat"){ addChat(d.text, d.who===S.me, d.from); }
    else if(t==="ready_state"){ if(d.who!==S.me) lobbyOppReady(); }
    else if(t==="cancelled"){ /* handled locally on cancel tap */ }
    else if(t==="opponent_here"){ /* start follows */ }
    else if(t==="plank_go"){
      plankPhase="count";
      let n=d.count||5;
      setStatus("Both in! Hold… "+n); speak("Hold!", true);
      const iv=setInterval(()=>{ n--; if(n>0){ setStatus("Hold… "+n); beep(520,.06); }
        else { clearInterval(iv); } }, 1000);
    }
    else if(t==="plank_live"){
      plankPhase="live"; resetHold();       // clock starts NOW
      S.active=true;
      setStatus("GO! Hold it!", false); speak("Go!", true); beep(880,.15);
    }
    else if(t==="start"){ if(d.exercise) S.exercise=d.exercise; show("game"); startMatch(d.duration); }
    else if(t==="scores"){ const sc=d.scores; if(S.me && other(S.me) in sc){
        const newOpp=sc[other(S.me)];
        if(newOpp>S.oppReps){ oppRepPump(); oppRun += (newOpp - S.oppReps); }
        S.oppReps=newOpp; oppScoreEl.textContent=S.oppReps; updatePresence();
      } }
    else if(t==="end"){ const sc=d.scores; if(S.me && other(S.me) in sc) S.oppReps=sc[other(S.me)]; endMatch(d.winner); }
    else if(t==="rematch_pending"){ setAgain("pending"); }
    else if(t==="rematch_offer"){ setAgain("offer"); }
    else if(t==="opponent_left"){ opponentLeft(); }
    else if(t==="error"){
      if(d.reason==="no_room") toast("No game with that code.");
      else if(d.reason==="room_full") toast("That game is already full.");
      else toast("Couldn't join.");
      backToLanding();
    }
  };
  ws.onerror = ()=> setStatus("Can't reach referee — check the server URL",true);
  ws.onclose = ()=>{ if(S.phase==="playing") toast("Connection dropped"); };
}
let lastSent=-1;
function pushReps(){
  if(ws && ws.readyState===1 && S.active && S.myReps!==lastSent){
    lastSent=S.myReps; ws.send(JSON.stringify({type:"reps", reps:S.myReps}));
  }
}

/* ---------- center-screen states ---------- */
function setStatus(txt,warn=false){ statusEl.textContent=txt; statusEl.classList.toggle("warn",warn); }
function exLabel(){ return (EXERCISES[S.exercise]||EXERCISES.squats).label; }
const isHold = () => (EXERCISES[S.exercise]||{}).hold === true;

/* ---------- opponent presence + callouts ---------- */
const CALLOUTS = {
  ahead:  ["You pulled ahead!","You're MOGGING them!","Certified mogger 😤","They can't keep up!",
           "Eat their dust!","You're built different!","Keep cooking 🔥","Lead is yours — take it!",
           "They're gassed, push!","Dominate!"],
  behind: ["They passed you!","Don't get mogged!","You're getting cooked!","Wake up — they're ahead!",
           "They're pulling away!","Catch up, champ!","Dig deeper!","You're better than this!",
           "Turn it UP 🔥","No mercy — move!"],
  tie:    ["Neck and neck!","Too close to call!","It's a DOGFIGHT!","Dead heat!","Someone break it!","All square!"],
  streak: ["They're on a HEATER 🔥","They're cooking!","Unstoppable streak!","Beast mode engaged!","Stop the bleeding!"],
  idle:   ["Hello? Are you even there?","Did you fall asleep? 😴","Anyone home? MOVE!","Your bar's collecting dust…",
           "This isn't a rest day!","Wake up — they're repping!","Are you buffering?","Hello?? Do something!"]
};
const pick = arr => arr[Math.floor(Math.random()*arr.length)];
let prevLead=0, lastCalloutAt=0, oppRun=0, myLastRepTs=0;
const IDLE_MS=15000;   // no reps for 15s -> "you there?" nudge
const isIdle = () => S.active && (performance.now()-myLastRepTs > IDLE_MS);

function oppRepPump(){
  const a=$("oppAvatar"); if(!a) return;
  a.classList.remove("rep");
  // restart the CSS animation reliably — offsetWidth reflow is flaky on SVG, so use double rAF
  requestAnimationFrame(()=>requestAnimationFrame(()=>{ a.classList.add("rep"); }));
}
function setOppMood(m){
  const a=$("oppAvatar"); if(!a) return;
  a.classList.remove("mood-win","mood-lose","mood-neutral");
  a.classList.add("mood-"+m);
}
function flashCallout(text,tone){
  const c=$("callout"); if(!c) return;
  c.textContent=text;
  c.style.color = tone==="ahead"?"var(--you)":(tone==="behind"?"var(--opp)":(tone==="idle"?"var(--bone)":"var(--gold)"));
  c.classList.remove("show"); void c.offsetWidth; c.classList.add("show");
  speak(text, true);   // read the trash-talk aloud
}
function updatePresence(){
  const you=S.myReps, opp=S.oppReps, max=Math.max(you,opp,1);
  const yb=$("youBar"), ob=$("oppBar");
  if(yb) yb.style.width=(you/max*100)+"%";
  if(ob) ob.style.width=(opp/max*100)+"%";
  setOppMood(opp>you?"win":(opp<you?"lose":"neutral"));   // gorilla grins when winning, grits when losing
  if(!S.active) return;
  const now=performance.now(), diff=you-opp;
  const lead = diff>0?1:(diff<0?-1:0);
  // if I've gone idle, the idle nudge (fired from tick) owns my screen — no lead/trail clash
  if(isIdle()){ prevLead=lead; return; }
  const leadChanged = lead!==prevLead;
  let pool = diff>0?"ahead":(diff<0?"behind":"tie");
  if(oppRun>=3 && diff<0) pool="streak";
  const tone = diff>0?"ahead":(diff<0?"behind":"tie");
  if(leadChanged || oppRun>=3 || now-lastCalloutAt>2600){
    flashCallout(pick(CALLOUTS[pool]), tone);
    lastCalloutAt=now;
    if(pool==="streak") oppRun=0;
  }
  prevLead=lead;
}
function resetPresence(){
  prevLead=0; lastCalloutAt=0; oppRun=0; myLastRepTs=performance.now();
  const yb=$("youBar"), ob=$("oppBar"); if(yb) yb.style.width="0%"; if(ob) ob.style.width="0%";
  $("callout").classList.remove("show");
  $("oppAvatar").setAttribute("class","avatar ex-"+S.exercise);   // SVG className is read-only; use setAttribute
  const dh=$("dbgHip"); if(dh) dh.style.display = (SHOW_HIP_DEBUG && (S.exercise==="pushups"||S.exercise==="plank")) ? "block" : "none";
}
function showPresence(on){
  $("oppPanel").classList.toggle("on",on);
  $("raceWrap").classList.toggle("on",on);
}
function centerWait(title, sub){
  centerEl.innerHTML=`<div class="box"><div class="spin"></div><p>${title}</p><small>${sub||""}</small>
    <div class="load-tip" id="loadTip"></div></div>`;
  startTips();
}

/* ---------- rotating loading tips ---------- */
const TIPS = [
  "Both knees must bend for a squat to count — no half-reps!",
  "Push-ups need you horizontal — no standing and flapping. 😤",
  "Stand back so your whole body fits in the camera.",
  "Good lighting means better rep detection.",
  "Rattle your opponent with some trash talk in the lobby.",
  "Both players hit READY to skip the countdown and start early.",
  "Your rival's gorilla grins when they're winning — wipe that smile off.",
  "Go idle for 15 seconds and the game WILL call you out.",
  "Your best score per exercise lands you on the leaderboard.",
  "Pace yourself — 35 seconds is longer than it looks.",
  "Camera never leaves your device — only your rep count is sent.",
];
let tipTimer=null, tipIdx=0;
function startTips(){
  clearInterval(tipTimer);
  const el=$("loadTip"); if(!el) return;
  tipIdx=Math.floor(Math.random()*TIPS.length);
  el.textContent="💡 "+TIPS[tipIdx];
  tipTimer=setInterval(()=>{
    const e=$("loadTip"); if(!e){ clearInterval(tipTimer); tipTimer=null; return; }
    tipIdx=(tipIdx+1)%TIPS.length;
    e.style.opacity="0";
    setTimeout(()=>{ const x=$("loadTip"); if(x){ x.textContent="💡 "+TIPS[tipIdx]; x.style.opacity="1"; } },300);
  }, 3800);
}
function stopTips(){ clearInterval(tipTimer); tipTimer=null; }
function showSearching(){
  centerEl.innerHTML=`<div class="box"><div class="spin"></div>
    <p>Finding an opponent</p><small>${exLabel()} · matching you with someone…</small>
    <div class="load-tip" id="loadTip"></div>
    <button class="btn" id="cancelBtn">Cancel</button></div>`;
  setStatus("Searching…");
  startTips();
  const c=$("cancelBtn");
  if(c) c.addEventListener("click",()=>{
    try{ if(ws && ws.readyState===1) ws.send(JSON.stringify({type:"cancel"})); }catch(e){}
    backToLanding();
  });
}

/* ---------- pre-game lobby (ready-up + countdown + chat) ---------- */
let lobbyTimer=null, lobbyReady=false;
const esc = s => (s||"").replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function openLobby(duration){
  S.phase="lobby"; lobbyReady=false; stopTips();
  setStatus("Get ready");
  centerEl.innerHTML=`<div class="lobby">
    <div class="l-title">Get Ready</div>
    <div class="l-vs">You vs <b>${esc(S.oppName||"Opponent")}</b> · ${exLabel()}</div>
    <div class="l-timer" id="lTimer">0:${String(duration).padStart(2,"0")}</div>
    <div class="l-chat" id="lChat"><div class="sys">Say hi — or talk some trash 😤</div></div>
    <div class="l-inrow">
      <input id="chatInput" maxlength="200" placeholder="Talk trash…" autocomplete="off" />
      <button id="chatSend">Send</button>
    </div>
    <button class="l-ready" id="readyBtn">Ready</button>
    <div class="l-status" id="lStatus"></div>
  </div>`;
  // local countdown (server is authoritative on the actual start)
  let remaining=duration;
  clearInterval(lobbyTimer);
  lobbyTimer=setInterval(()=>{
    remaining--; const el=$("lTimer");
    if(el) el.textContent="0:"+String(Math.max(0,remaining)).padStart(2,"0");
    if(remaining<=0) clearInterval(lobbyTimer);
  },1000);
  // wire chat + ready
  const send=()=>{
    const inp=$("chatInput"); if(!inp) return;
    const txt=inp.value.trim(); if(!txt) return;
    try{ if(ws&&ws.readyState===1) ws.send(JSON.stringify({type:"chat", text:txt})); }catch(e){}
    inp.value="";
  };
  $("chatSend").addEventListener("click", send);
  $("chatInput").addEventListener("keydown", e=>{ if(e.key==="Enter") send(); });
  $("readyBtn").addEventListener("click", ()=>{
    if(lobbyReady) return;
    lobbyReady=true;
    try{ if(ws&&ws.readyState===1) ws.send(JSON.stringify({type:"ready"})); }catch(e){}
    const b=$("readyBtn"); b.disabled=true; b.textContent="You're ready ✓";
    const st=$("lStatus"); if(st) st.textContent="Waiting for opponent…";
  });
}
function addChat(text, mine, who){
  const box = (S.phase==="done") ? $("rChat") : $("lChat");
  if(!box) return;
  const div=document.createElement("div");
  div.className="msg"+(mine?"":" them");
  div.innerHTML=`<b>${esc(who||(mine?"You":"Them"))}:</b> ${esc(text)}`;
  box.appendChild(div); box.scrollTop=box.scrollHeight;
}
function lobbyOppReady(){
  const st=$("lStatus"); if(st) st.textContent="Opponent is ready! 🔥";
  const box=$("lChat");
  if(box){ const d=document.createElement("div"); d.className="sys"; d.textContent="Opponent hit ready"; box.appendChild(d); box.scrollTop=box.scrollHeight; }
}
function shareLink(code){
  return location.origin + location.pathname + "?join=" + code;
}
async function shareGame(code){
  const url = shareLink(code);
  if(navigator.share){
    try{ await navigator.share({title:"GymOggle", text:"Fight me on GymOggle 💪", url}); }
    catch(e){ /* user dismissed the share sheet — ignore */ }
  } else {
    try{ await navigator.clipboard.writeText(url); toast("Link copied — paste it to a friend"); }
    catch(e){ toast(url); }
  }
}
function showShareCode(code){
  centerEl.innerHTML=`<div class="box"><div class="codelabel">${exLabel()} · challenge a friend</div>
    <div class="codeshow">${code}</div>
    <small>Waiting for your friend to join…</small>
    <div class="sharebtns">
      <button class="btn" id="shareBtn">Share link</button>
      <button class="btn" id="copyBtn">Copy code</button>
    </div></div>`;
  setStatus("Room ready");
  const sh=$("shareBtn"); if(sh) sh.addEventListener("click",()=> shareGame(code));
  const c=$("copyBtn");  if(c)  c.addEventListener("click",()=>{ navigator.clipboard?.writeText(code); toast("Code copied"); });
}

/* ---------- PLANK CHICKEN: no timer. First to break form loses. ---------- */
let plankPhase="wait";   // "wait" (get into position) -> "count" -> "live"
function wireHoldMode(){
  resetHold();
  plankPhase="wait";
  let sentReady=false;
  onHoldTick = (secs, holding)=>{
    if(plankPhase==="wait"){
      // phase 1: tell the player to get into position; report when they're holding
      if(holding && !sentReady){
        sentReady=true;
        try{ if(ws&&ws.readyState===1) ws.send(JSON.stringify({type:"plank_ready"})); }catch(e){}
        setStatus("You're in! Waiting for opponent…");
      } else if(!holding){
        sentReady=false;
        setStatus("Get into a plank position…");
      }
      youScoreEl.textContent="0";
      return;
    }
    if(plankPhase==="count"){
      youScoreEl.classList.toggle("wobble", !holding);
      return;                            // countdown handled by plank_go handler
    }
    // phase 3: LIVE — seconds held = score
    const s=Math.floor(HOLD.secs);
    if(s!==S.myReps){ S.myReps=s; youScoreEl.textContent=s; pushReps(); updatePresence(); }
    youScoreEl.classList.toggle("wobble", !holding);
  };
  onHoldFailed = ()=>{
    if(plankPhase!=="live" || !S.active) return;   // drops before "live" don't count
    try{ if(ws&&ws.readyState===1) ws.send(JSON.stringify({type:"broke"})); }catch(e){}
    S.active=false;
    setStatus("You dropped! 💀", true); speak("You dropped!", true);
    beep(160,0.4,"sawtooth",0.3);
  };
}
function unwireHoldMode(){
  onHoldTick=()=>{}; onHoldFailed=()=>{};
  if(youScoreEl) youScoreEl.classList.remove("wobble");
}

/* ---------- match flow ---------- */
let lastSecond=-1;
function startMatch(duration){
  S.duration=duration||60; S.startTs=performance.now()/1000;
  S.myReps=0; S.oppReps=0; lastSent=-1; lastSecond=-1;
  youScoreEl.textContent="0"; oppScoreEl.textContent="0";
  S.phase="playing"; setStatus("Get ready"); setAgain("idle"); removeLeftNote(); resetPresence(); clearInterval(lobbyTimer); stopTips();
  S.mode = isHold() ? "hold" : "reps";        // plank = hold, everything else = reps
  centerEl.innerHTML='<div class="box"><div class="vsflash">VS</div></div>';
  if(S.mode==="hold"){
    wireHoldMode(); $("clock").classList.add("hidden");
    S.active=true;                       // detection runs; but drops only count once "live"
    setStatus("Get into a plank position…");
  } else {
    unwireHoldMode(); $("clock").classList.remove("hidden");
    tick();
    setTimeout(runCountdown, 700);
  }
}
function runCountdown(){
  const seq=[["3",440],["2",440],["1",440],["GO",800]];
  let i=0;
  (function step(){
    if(i>=seq.length){ centerEl.innerHTML=""; S.active=true; setStatus(exLabel()+" — go!"); startBeat();
      const eb=$("exBanner"); eb.textContent="Perform "+exLabel()+"!"; eb.classList.add("on"); showPresence(true);
      speak(exLabel()+"! Go!", true); return; }
    const [n,f]=seq[i++];
    centerEl.innerHTML=`<div class="box"><div class="bigcount">${n}</div></div>`;
    beep(f, n==="GO"?0.34:0.14, n==="GO"?"sawtooth":"square", 0.28);
    if(n!=="GO") speak(n, true);
    setTimeout(step, n==="GO"?420:600);
  })();
}
function tick(){
  if(S.phase!=="playing") return;
  const remaining=Math.max(0, S.duration-(performance.now()/1000 - S.startTs));
  const sec=Math.ceil(remaining);
  const m=Math.floor(remaining/60), s=Math.floor(remaining%60);
  clockEl.textContent=`${m}:${String(s).padStart(2,"0")}`;
  clockEl.classList.toggle("low", remaining<=10 && S.active);
  if(sec!==lastSecond){
    lastSecond=sec;
    if(S.active && sec<=5 && sec>0) beep(520,0.07,"square",0.22);   // final-5 tension ticks
  }
  // idle nudge: no reps for 10s -> "you there?" (owns the screen, throttled)
  if(isIdle() && performance.now()-lastCalloutAt>3000){
    flashCallout(pick(CALLOUTS.idle), "idle");
    lastCalloutAt=performance.now();
  }
  if(remaining<=0){ if(S.active){ whistle(); stopBeat(); $("exBanner").classList.remove("on"); } S.active=false; }
  requestAnimationFrame(tick);
}
function endMatch(winner){
  S.active=false; S.phase="done"; S.winner=winner; stopBeat(); $("exBanner").classList.remove("on"); showPresence(false);
  $("rYouName").textContent=S.name;
  const iWon=winner===S.me, tie=winner==="TIE";
  const v=$("verdict");
  v.textContent=tie?"Draw":(iWon?"You win":"You lose");
  v.className="big "+(tie?"tie":(iWon?"w":"lose"));
  speak(tie?"It's a draw!":(iWon?"You win!":"You lose!"), true);
  $("rYou").classList.toggle("win", iWon||tie);
  $("rOpp").classList.toggle("win", (!iWon&&!tie)||tie);
  $("crownYou").textContent=iWon?"👑":"";
  $("crownOpp").textContent=(!iWon&&!tie)?"👑":"";
  setAgain("idle");
  const rc=$("rChat"); if(rc) rc.innerHTML="";
  show("results");
  // juice: count the scores up, play a sting, throw confetti for a win
  countUp($("rYouScore"), S.myReps);
  countUp($("rOppScore"), S.oppReps);
  if(tie) tieSound();
  else if(iWon){ victorySound(); confettiBurst(iWon); }
  else defeatSound();
}
function countUp(el,target){
  const dur=750, t0=performance.now();
  (function step(now){
    const p=Math.min(1,(now-t0)/dur);
    el.textContent=Math.round(target*(1-Math.pow(1-p,3)));   // ease-out
    if(p<1) requestAnimationFrame(step);
  })(t0);
}
function victorySound(){
  if(!actx||!master) return;
  [523,659,784,1047].forEach((f,i)=> beep(f,0.18,"triangle",0.3,i*0.11));   // C-E-G-C rising
}
function defeatSound(){ if(actx&&master){ beep(300,0.3,"sawtooth",0.2,0); beep(200,0.4,"sawtooth",0.2,0.18); } }
function tieSound(){ if(actx&&master){ beep(440,0.2,"triangle",0.25,0); beep(440,0.2,"triangle",0.25,0.22); } }

/* lightweight confetti on the winner's side */
function confettiBurst(){
  let cv=$("confetti");
  if(!cv){ cv=document.createElement("canvas"); cv.id="confetti";
    cv.style.cssText="position:absolute;inset:0;width:100%;height:100%;z-index:8;pointer-events:none";
    $("results").appendChild(cv); }
  const ctx=cv.getContext("2d");
  cv.width=cv.clientWidth; cv.height=cv.clientHeight;
  const colors=["#ffd23f","#22e0d6","#ff2e7e","#f4f0ff"];
  const parts=Array.from({length:140},()=>({
    x:Math.random()*cv.width, y:-20-Math.random()*cv.height*0.4,
    vx:(Math.random()-0.5)*3, vy:2+Math.random()*4,
    s:4+Math.random()*6, rot:Math.random()*6, vr:(Math.random()-0.5)*0.3,
    c:colors[Math.floor(Math.random()*colors.length)]
  }));
  const t0=performance.now();
  (function frame(now){
    ctx.clearRect(0,0,cv.width,cv.height);
    for(const p of parts){
      p.x+=p.vx; p.y+=p.vy; p.vy+=0.05; p.rot+=p.vr;
      ctx.save(); ctx.translate(p.x,p.y); ctx.rotate(p.rot);
      ctx.fillStyle=p.c; ctx.fillRect(-p.s/2,-p.s/2,p.s,p.s*0.5); ctx.restore();
    }
    if(now-t0<2600 && screens.results.classList.contains("on")) requestAnimationFrame(frame);
    else ctx.clearRect(0,0,cv.width,cv.height);
  })(t0);
}
function setAgain(mode){
  const b=$("againBtn"); if(!b) return;
  b.classList.remove("accept");
  if(mode==="idle"){ b.disabled=false; b.textContent="Play again"; }
  else if(mode==="pending"){ b.disabled=true; b.textContent="Waiting for opponent…"; }
  else if(mode==="offer"){ b.disabled=false; b.classList.add("accept"); b.textContent="Rematch? Tap to accept!"; }
  else if(mode==="left"){ b.disabled=true; b.textContent="Opponent left"; }
}
function removeLeftNote(){ const n=$("leftNote"); if(n) n.remove(); }
function opponentLeft(){
  stopBeat(); $("exBanner").classList.remove("on"); showPresence(false); S.active=false;
  toast("Your rival left the game.");
  if(screens.results.classList.contains("on")){
    // stay on the results screen, but make it obvious the rematch is off
    setAgain("left");
    if(!$("leftNote")){
      const n=document.createElement("div");
      n.id="leftNote"; n.className="leftnote"; n.textContent="Opponent left — no rematch";
      $("results").appendChild(n);
    }
  } else {
    // mid-match or waiting: show a clear message + a way home (don't auto-yank)
    S.phase="idle"; S.active=false; show("game");
    clockEl.classList.remove("low");
    centerEl.innerHTML=`<div class="box"><p>Your rival left the game</p>
      <button class="btn" id="homeBtn">Back to home</button></div>`;
    setStatus("Opponent left",true);
    const h=$("homeBtn"); if(h) h.addEventListener("click", backToLanding);
  }
}
function backToLanding(){
  removeLeftNote(); busy=false; clearInterval(lobbyTimer); stopTips();
  S.phase="idle"; S.me=null; S.code=null; S.intent=null;
  try{ if(ws && ws.readyState===1) ws.send(JSON.stringify({type:"leave"})); }catch(e){}
  try{ if(ws) ws.close(); }catch(e){}
  centerEl.innerHTML=""; clockEl.textContent="1:00"; clockEl.classList.remove("low");
  resetLandingButtons();
  show("landing");
}

/* ---------- entry ---------- */
function resetLandingButtons(){
  $("findBtn").disabled=false; $("findBtn").textContent="Find opponent";
  $("createBtn").disabled=false; $("createBtn").textContent="Create game";
  $("joinBtn").disabled=false; $("joinBtn").textContent="Join";
}
async function enterGame(intent, code){
  if(busy) return;            // ignore double-taps / retries while a game is starting
  const nm = $("name").value.trim();
  if(!nm){ toast("Enter a tag first 💪"); $("name").focus(); return; }
  busy=true;
  initAudio();   // unlock audio on the user gesture
  S.name = nm.slice(0,12);
  $("youName").textContent=S.name;
  $("findBtn").disabled=true; $("createBtn").disabled=true; $("joinBtn").disabled=true;
  const active = intent==="quick" ? $("findBtn") : (intent==="create" ? $("createBtn") : $("joinBtn"));
  active.textContent="Loading…";
  try{
    if(!landmarker) await initModel();
    await initCamera();
  }catch(e){
    resetLandingButtons(); busy=false;
    toast(e.name==="NotAllowedError" ? "Camera blocked — allow access and try again." : "Couldn't start camera/model. "+e.message);
    return;
  }
  resetLandingButtons();
  S.intent=intent; S.code=code;
  show("game");
  if(!looping){ looping=true; loop(); }
  centerWait(intent==="quick"?"Finding an opponent…":(intent==="create"?"Creating game…":"Joining…"),"");
  if(SERVER_URL.includes("YOUR-APP")){ setStatus("Set your server URL",true); centerWait("Server not set","Edit SERVER_URL in the file, then reload."); return; }
  connect();
}

document.querySelectorAll(".ex").forEach(b=>{
  b.addEventListener("click",()=>{
    document.querySelectorAll(".ex").forEach(x=>x.classList.remove("on"));
    b.classList.add("on");
    chosenExercise=b.dataset.ex;
  });
});

$("findBtn").addEventListener("click", ()=> enterGame("quick", null));
$("createBtn").addEventListener("click", ()=> enterGame("create", null));
$("joinBtn").addEventListener("click", ()=>{
  const code=$("joinCode").value.trim().toUpperCase();
  if(code.length<4){ toast("Enter the 4-character code."); return; }
  enterGame("join", code);
});
$("joinCode").addEventListener("input", e=>{ e.target.value=e.target.value.toUpperCase(); });
$("againBtn").addEventListener("click", ()=>{
  // works both as "request rematch" and "accept opponent's rematch"
  if(ws && ws.readyState===1) ws.send(JSON.stringify({type:"rematch"}));
  setAgain("pending");
});
$("exitBtn").addEventListener("click", ()=> backToLanding());

/* post-match chat (results screen) — shares the same relay as the lobby chat */
(function wireResultsChat(){
  const send=()=>{
    const inp=$("rChatInput"); if(!inp) return;
    const txt=inp.value.trim(); if(!txt) return;
    try{ if(ws&&ws.readyState===1) ws.send(JSON.stringify({type:"chat", text:txt})); }catch(e){}
    inp.value="";
  };
  const s=$("rChatSend"), i=$("rChatInput");
  if(s) s.addEventListener("click", send);
  if(i) i.addEventListener("keydown", e=>{ if(e.key==="Enter") send(); });
})();