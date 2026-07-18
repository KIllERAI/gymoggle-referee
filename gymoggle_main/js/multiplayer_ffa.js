/* GymOggle — N-PLAYER FREE-FOR-ALL (2-8)
   A SEPARATE mode. Uses its own WebSocket (mws) and its own screen, so the
   validated 1v1 code in multiplayer.js is never touched.
   Reps mode: most reps in 35s wins.   Plank: last one holding wins. */

const FFA = {
  on:false, mws:null, code:null, size:4, exercise:"squats",
  host:false, players:[], me:null, myReps:0, mode:"reps",
  started:false, plankPhase:"wait", startTs:0, sentReady:false, clockIv:null
};
const FFA_WS = (typeof SERVER_URL!=="undefined" ? SERVER_URL : "wss://gymoggle-referee.onrender.com/");

function ffaConnect(onOpen){
  try{ if(FFA.mws) FFA.mws.close(); }catch(e){}
  const w = new WebSocket(FFA_WS);
  FFA.mws = w;
  w.onopen = ()=> onOpen && onOpen();
  w.onmessage = ev => ffaMsg(JSON.parse(ev.data));
  w.onerror = ()=> toast("Connection error — the server may be waking (40s). Try again.");
}
function ffaSend(o){ try{ if(FFA.mws && FFA.mws.readyState===1) FFA.mws.send(JSON.stringify(o)); }catch(e){} }

/* ---------- entry: create / join ---------- */
function ffaCreate(size, exercise, duration){
  FFA.size=size; FFA.exercise=exercise; FFA.host=true; FFA.duration=duration||30;
  ffaConnect(()=> ffaSend({type:"m_create", size, exercise, duration:FFA.duration, pid:PID, name:playerName(), token:window.PTOKEN}));
  show("ffa"); ffaLobbyWaiting("Creating room…");
}
function ffaJoin(code){
  FFA.host=false;
  ffaConnect(()=> ffaSend({type:"m_join", code:code.toUpperCase(), pid:PID, name:playerName(), token:window.PTOKEN}));
  show("ffa"); ffaLobbyWaiting("Joining "+code.toUpperCase()+"…");
}
function playerName(){ return (S.name || ($("name")&&$("name").value.trim()) || "Player"); }

/* ---------- message handling ---------- */
function ffaMsg(d){
  const t=d.type;
  if(t==="m_created"){ FFA.code=d.code; FFA.size=d.size; }
  else if(t==="m_joined"){ FFA.code=d.code; }
  else if(t==="m_error"){ toast(d.msg); ffaExit(); }
  else if(t==="m_roster"){
    FFA.players=d.players; FFA.size=d.size; FFA.exercise=d.exercise; FFA.host=(d.host===PID);
    FFA.me=FFA.players.find(p=>p.pid===PID)||null;
    ffaRenderLobby();
  }
  else if(t==="m_start"){ ffaBeginMatch(d); }
  else if(t==="m_countdown"){ ffaCountdown(d.count||3); }
  else if(t==="m_go"){ ffaGo(); }
  else if(t==="m_score"){ const p=FFA.players.find(x=>x.pid===d.pid); if(p){ p.reps=d.reps; ffaUpdateCell(p); } }
  else if(t==="m_dropped"){ const p=FFA.players.find(x=>x.pid===d.pid); if(p){ p.out=true; ffaUpdateCell(p);
      if(d.pid===PID){ setFfaStatus("You dropped! 💀"); } } }
  else if(t==="m_ready"){ const p=FFA.players.find(x=>x.pid===d.pid); if(p){ p.ready=true; ffaUpdateCell(p); } }
  else if(t==="m_over"){ ffaResults(d); }
  else if(t==="m_chat"){ ffaAddChat(d); }
}

/* ---------- lobby ---------- */
function ffaLobbyWaiting(msg){
  $("ffaGrid").innerHTML = `<div class="ffa-wait"><div class="spin"></div><p>${msg}</p>
    <small>Server may take ~40s to wake on first connect</small></div>`;
  $("ffaBar").style.display="none";
}
function ffaRenderLobby(){
  FFA.on=true;
  ffaShowChat(true);
  $("ffaBar").style.display="flex";
  $("ffaTitle").textContent = "Room "+(FFA.code||"");
  $("ffaSub").textContent = `${(EXERCISES[FFA.exercise]||{label:FFA.exercise}).label} · ${FFA.players.length}/${FFA.size} players`;
  const g=$("ffaGrid"); g.className="ffa-grid n"+FFA.size;
  g.innerHTML = FFA.players.map(p=>ffaCell(p,true)).join("")
    + Array.from({length:Math.max(0,FFA.size-FFA.players.length)},
        ()=>`<div class="ffa-cell empty"><span>Waiting…</span></div>`).join("");
  // host controls
  const ctrl=$("ffaCtrl");
  if(FFA.host){
    ctrl.innerHTML = FFA.players.length>=2
      ? `<button class="btn primary" id="ffaStart">Start match (${FFA.players.length})</button>`
      : `<p class="ffa-hint">Share code <b>${FFA.code}</b> — need 2+ players</p>`;
    const b=$("ffaStart"); if(b) b.addEventListener("click", ()=> ffaSend({type:"m_begin"}));
  } else {
    ctrl.innerHTML = `<p class="ffa-hint">Waiting for host to start… (code <b>${FFA.code}</b>)</p>`;
  }
  const share=$("ffaShare"); if(share) share.textContent = FFA.code||"";
}

/* a player cell: your own shows the camera; others show a colored gorilla */
function ffaCell(p, lobby){
  const me = p.pid===PID;
  const inner = me
    ? `<div class="ffa-cam" id="ffaCam"></div>`
    : gorillaSVG(p.color);
  return `<div class="ffa-cell${me?' me':''}${p.out?' out':''}" data-pid="${p.pid}" style="--pc:${p.color}">
      ${inner}
      <div class="ffa-name">${me?"YOU":esc(p.name)}</div>
      <div class="ffa-val" id="val-${p.pid}">${lobby?'':'0'}</div>
      ${p.out?'<div class="ffa-x">OUT</div>':''}
    </div>`;
}
function gorillaSVG(color){
  return `<svg class="ffa-gorilla" viewBox="0 0 100 100" style="--gc:${color}">
    <ellipse class="gb" cx="50" cy="62" rx="26" ry="26"/>
    <rect class="gb" x="14" y="44" width="13" height="40" rx="6.5"/>
    <rect class="gb" x="73" y="44" width="13" height="40" rx="6.5"/>
    <circle class="gb" cx="30" cy="28" r="6"/><circle class="gb" cx="70" cy="28" r="6"/>
    <ellipse class="gb" cx="50" cy="30" rx="19" ry="18"/>
    <ellipse class="gf" cx="50" cy="34" rx="13" ry="13"/>
    <circle class="ge" cx="43" cy="30" r="3.2"/><circle class="ge" cx="57" cy="30" r="3.2"/>
    <circle class="gp" cx="43.4" cy="30.4" r="1.6"/><circle class="gp" cx="57.4" cy="30.4" r="1.6"/>
  </svg>`;
}

/* ---------- match ---------- */
async function ffaBeginMatch(d){
  FFA.mode=d.mode; FFA.exercise=d.exercise||FFA.exercise; FFA.started=true; FFA.myReps=0;
  const rw=$("ffaResults"); if(rw) rw.style.display="none";   // clear any results overlay (rematch)
  ffaShowChat(false);
  S.exercise=FFA.exercise; stage="up"; jackFeetMin=null;
  // start the camera + detection
  try{ if(!landmarker) await initModel(); await initCamera(); }
  catch(e){ toast("Camera error"); return; }
  if(!looping){ looping=true; loop(); }
  // build the play grid
  $("ffaBar").style.display="flex";
  $("ffaTitle").textContent = (EXERCISES[FFA.exercise]||{label:FFA.exercise}).label;
  $("ffaCtrl").innerHTML="";
  const g=$("ffaGrid"); g.className="ffa-grid n"+FFA.size;
  g.innerHTML = FFA.players.map(p=>ffaCell(p,false)).join("");
  // mount the live camera into your cell
  const cam=$("ffaCam");
  if(cam){ const v=document.createElement("video"); v.autoplay=true; v.muted=true; v.playsInline=true;
    v.srcObject=window.camStream; cam.appendChild(v); }
  // route reps / holds to FFA
  if(FFA.mode==="hold"){ ffaWireHold(); }
  else { onRep = ffaRep; onHoldTick=()=>{}; onHoldFailed=()=>{}; }
  ffaShowChat(false);
  setFfaStatus(FFA.mode==="hold" ? "Get into a plank…" : "Get ready…");
}
function ffaCountdown(n){
  let el=$("ffaCount");
  if(!el){ el=document.createElement("div"); el.id="ffaCount"; el.className="ffa-countdown"; $("ffa").appendChild(el); }
  el.style.display="flex";
  let c=n;
  el.textContent=c; beep(440,.12);
  const iv=setInterval(()=>{
    c--;
    if(c>0){ el.textContent=c; beep(440,.12); }
    else if(c===0){ el.textContent="GO!"; beep(880,.2); }
    else { clearInterval(iv); el.style.display="none"; }
  }, 800);
}
function ffaGo(){
  if(FFA.mode==="hold"){ FFA.plankPhase="live"; resetHold(); FFA.startTs=performance.now();
    setFfaStatus("GO! Hold it!"); speak("Go!",true); beep(880,.15);
    if(FFA.clockIv) clearInterval(FFA.clockIv);
    FFA.clockIv=setInterval(ffaTickClock, 250);
  } else {
    FFA.startTs=performance.now(); setFfaStatus("GO!"); speak("Go!",true); beep(880,.15);
    if(FFA.clockIv) clearInterval(FFA.clockIv);
    FFA.clockIv=setInterval(ffaTickClock, 250);
  }
}
function ffaTickClock(){
  const dur = (FFA.mode==="hold") ? 999 : 35;
  const el=(performance.now()-FFA.startTs)/1000;
  const left=Math.max(0, dur-el);
  $("ffaClock").textContent = (FFA.mode==="hold")
    ? el.toFixed(0)+"s"
    : Math.ceil(left)+"s";
}
function ffaRep(){
  FFA.myReps++;
  const me=FFA.players.find(p=>p.pid===PID); if(me){ me.reps=FFA.myReps; ffaUpdateCell(me); }
  ffaSend({type:"m_rep", reps:FFA.myReps});
  repPop();
}
function ffaWireHold(){
  resetHold(); FFA.plankPhase="wait"; FFA.sentReady=false;
  onHoldTick=(secs,holding)=>{
    if(FFA.plankPhase==="wait"){
      if(holding && !FFA.sentReady){ FFA.sentReady=true; ffaSend({type:"m_ready"}); setFfaStatus("You're in! Waiting…"); }
      else if(!holding){ FFA.sentReady=false; setFfaStatus("Get into a plank…"); }
    }
  };
  onHoldFailed=()=>{
    if(FFA.plankPhase!=="live") return;
    ffaSend({type:"m_out"});
    const me=FFA.players.find(p=>p.pid===PID); if(me){ me.out=true; ffaUpdateCell(me); }
    setFfaStatus("You dropped! 💀"); speak("You dropped!",true); beep(160,.4,"sawtooth",.3);
  };
}
function ffaUpdateCell(p){
  const cell=document.querySelector(`.ffa-cell[data-pid="${p.pid}"]`);
  if(!cell) return;
  const val=cell.querySelector(".ffa-val");
  if(val) val.textContent = (FFA.mode==="hold") ? (p.out?"OUT":"holding") : p.reps;
  cell.classList.toggle("out", !!p.out);
  if(p.pid!==PID){                   // make the gorilla react
    const gor=cell.querySelector(".ffa-gorilla");
    if(gor){ gor.classList.remove("nod"); void gor.offsetWidth; gor.classList.add("nod"); }
  }
}
function setFfaStatus(msg){ const s=$("ffaStatus"); if(s) s.textContent=msg; }

/* ---------- results ---------- */
function ffaResults(d){
  FFA.started=false; if(FFA.clockIv) clearInterval(FFA.clockIv);
  onRep=null; onHoldTick=()=>{}; onHoldFailed=()=>{};
  const win=d.standings.find(p=>p.pid===d.winner);
  const iWon = d.winner===PID;
  $("ffaGrid").innerHTML="";
  $("ffaCtrl").innerHTML="";
  $("ffaBar").style.display="none";
  const wrap=$("ffaResults"); wrap.style.display="flex";
  wrap.innerHTML=`
    <div class="ffa-trophy" id="ffaTrophy"></div>
    <div class="ffa-winner">${iWon?"🏆 YOU WIN!":(win?esc(win.name)+" wins!":"Match over")}</div>
    <div class="ffa-standings">${d.standings.map((p,i)=>`
      <div class="ffa-rank${p.pid===PID?' me':''}"><b>${i+1}</b>
        <span class="dot" style="background:${p.color}"></span>
        <span class="nm">${esc(p.name)}</span>
        <span class="sc">${FFA.mode==="hold"?(p.out?"out":"held"):p.reps+" reps"}</span></div>`).join("")}</div>
    <div class="ffa-rbtns">
      ${FFA.host
        ? `<button class="btn primary" id="ffaAgain">Play again</button>`
        : `<div class="ffa-waithost">Waiting for host to start a rematch…</div>`}
      <button class="btn ghost" id="ffaExit">Exit</button>
    </div>`;
  playTrophy();
  ffaShowChat(true);
  if(iWon) confettiBurst && confettiBurst();
  const again=$("ffaAgain");
  if(again) again.addEventListener("click", ()=>{
    // host restarts the whole room -> everyone goes back to the match
    wrap.style.display="none";
    ffaShowChat(true);
    ffaRenderLobby();
    ffaSend({type:"m_begin"});      // server re-runs mstart -> m_start broadcasts to all
  });
  $("ffaExit").addEventListener("click", ffaExit);
}
function playTrophy(){
  const el=$("ffaTrophy"); if(!el || !window.lottie) return;
  fetch("assets/trophy.json").then(r=>r.json()).then(data=>{
    window.lottie.loadAnimation({container:el, renderer:"svg", loop:false, autoplay:true, animationData:data});
  }).catch(()=>{ el.textContent="🏆"; el.style.fontSize="80px"; });
}

/* ---------- exit ---------- */
function ffaExit(){
  ffaSend({type:"m_leave"});
  try{ if(FFA.mws) FFA.mws.close(); }catch(e){}
  FFA.on=false; FFA.started=false; onRep=null; onHoldTick=()=>{}; onHoldFailed=()=>{};
  if(FFA.clockIv) clearInterval(FFA.clockIv);
  const r=$("ffaResults"); if(r) r.style.display="none";
  ffaShowChat(false);
  const cb=$("ffaChat"); if(cb) cb.innerHTML="";
  show("landing");
}

/* ---------- chat ---------- */
function ffaAddChat(d){
  const box=$("ffaChat"); if(!box) return;
  const div=document.createElement("div"); div.className="msg";
  const mine = d.pid===PID;
  div.innerHTML=`<b style="color:${d.color||'var(--you)'}">${esc(d.from)}${mine?" (you)":""}:</b> ${esc(d.text)}`;
  box.appendChild(div); box.scrollTop=box.scrollHeight;
}
function ffaShowChat(on){
  const p=$("ffaChatPanel"); if(p) p.style.display = on ? "flex" : "none";
}
function ffaSendChat(){
  const i=$("ffaChatInput"); if(!i) return;
  const txt=(i.value||"").trim(); if(!txt) return;
  ffaSend({type:"m_chat", text:txt}); i.value="";
}
(function(){
  const send=$("ffaChatSend"), inp=$("ffaChatInput");
  if(send) send.addEventListener("click", ffaSendChat);
  if(inp) inp.addEventListener("keydown", e=>{ if(e.key==="Enter") ffaSendChat(); });
})();

/* ---------- landing entry: pick size + exercise, then create ---------- */
function ffaOpenCreate(){
  const c=$("center"); // reuse nothing; build an inline chooser on the FFA screen
  show("ffa");
  $("ffaBar").style.display="none"; $("ffaResults").style.display="none";
  $("ffaCtrl").innerHTML=""; $("ffaStatus").textContent="";
  const exs=[["squats","🏋️ Squats"],["pushups","💪 Push-ups"],["jacks","⭐ Jacks"],["plank","🧱 Plank"]];
  $("ffaGrid").className="ffa-setup";
  $("ffaGrid").innerHTML=`
    <div class="ffa-setup-card">
      <h3>Group Battle</h3>
      <label>Players</label>
      <div class="seg" id="ffaSizeSeg">
        ${[2,3,4,5,6,7,8].map(n=>`<button data-n="${n}"${n===4?' class="on"':''}>${n}</button>`).join("")}
      </div>
      <label>Exercise</label>
      <div class="seg wrap" id="ffaExSeg">
        ${exs.map(([k,l],i)=>`<button data-ex="${k}"${i===0?' class="on"':''}>${l}</button>`).join("")}
      </div>
      <label id="ffaTimerLbl">Timer</label>
      <div class="seg wrap" id="ffaTimeSeg">
        ${[[30,"30s"],[60,"1m"],[120,"2m"],[180,"3m"],[300,"5m"]].map(([s,l],i)=>`<button data-s="${s}"${i===0?' class="on"':''}>${l}</button>`).join("")}
      </div>
      <button class="btn primary wide" id="ffaMake">Create room</button>
      <div class="or"><i></i>or join<i></i></div>
      <div class="joinrow">
        <input id="ffaJoinCode" maxlength="4" placeholder="CODE" autocomplete="off"/>
        <button class="btn ghost" id="ffaJoinBtn">Join</button>
      </div>
    </div>`;
  let size=4, ex="squats", dur=30;
  $("ffaSizeSeg").addEventListener("click", e=>{ const b=e.target.closest("button"); if(!b)return;
    [...e.currentTarget.children].forEach(x=>x.classList.remove("on")); b.classList.add("on"); size=+b.dataset.n; });
  $("ffaExSeg").addEventListener("click", e=>{ const b=e.target.closest("button"); if(!b)return;
    [...e.currentTarget.children].forEach(x=>x.classList.remove("on")); b.classList.add("on"); ex=b.dataset.ex;
    // plank = no timer-to-win, it's last-one-standing; grey the timer out
    const isPlank = ex==="plank";
    $("ffaTimeSeg").style.opacity = isPlank ? ".4" : "1";
    $("ffaTimeSeg").style.pointerEvents = isPlank ? "none" : "auto";
    $("ffaTimerLbl").textContent = isPlank ? "Timer (plank = last one holding wins)" : "Timer";
  });
  $("ffaTimeSeg").addEventListener("click", e=>{ const b=e.target.closest("button"); if(!b)return;
    [...e.currentTarget.children].forEach(x=>x.classList.remove("on")); b.classList.add("on"); dur=+b.dataset.s; });
  $("ffaMake").addEventListener("click", ()=> ffaCreate(size, ex, dur));
  const jb=$("ffaJoinBtn"), jc=$("ffaJoinCode");
  if(jb) jb.addEventListener("click", ()=>{ const code=(jc.value||"").trim(); if(code.length>=3) ffaJoin(code); });
  if(jc) jc.addEventListener("keydown", e=>{ if(e.key==="Enter"){ const code=(jc.value||"").trim(); if(code.length>=3) ffaJoin(code); } });
}

/* wire landing buttons — Create game + Join now use the unified Group Battle system */
(function(){
  const create=$("createBtn"); if(create) create.addEventListener("click", ffaOpenCreate);
  const jc=$("joinCode"), jb=$("joinBtn");
  if(jb) jb.addEventListener("click", ()=>{ const code=(jc.value||"").trim(); if(code.length>=3) ffaJoin(code); });
  if(jc) jc.addEventListener("keydown", e=>{ if(e.key==="Enter"){ const code=(jc.value||"").trim(); if(code.length>=3) ffaJoin(code); } });
  const leave=$("ffaLeave"); if(leave) leave.addEventListener("click", ffaExit);
})();