/* GymOggle — core: config, state, audio, camera, model, the frame loop
   Part of the GymOggle app. Loaded as a classic script; modules share globals. */

/* ============================================================
   CONFIG — your Render referee URL (wss://). Override with ?server=
   ============================================================ */
const DEFAULT_SERVER = "wss://gymoggle-referee.onrender.com";
const params = new URLSearchParams(location.search);
const SERVER_URL = params.get("server") || DEFAULT_SERVER;
const HTTP_BASE = SERVER_URL.replace(/^ws/, "http");   // wss->https for REST calls
const JOIN_CODE = (params.get("join") || "").toUpperCase().slice(0,4);

const $ = id => document.getElementById(id);
const screens = { landing:$("landing"), game:$("game"), results:$("results"), board:$("board"), daily:$("daily"), ffa:$("ffa"), journey:$("journey"), jday:$("jday"), jrun:$("jrun"), jcoach:$("jcoach"), how:$("how") };
function show(name){ for(const k in screens) screens[k].classList.toggle("on", k===name); }

const video=$("video"), overlay=$("overlay"), octx=overlay.getContext("2d");
const youScoreEl=$("youScore"), oppScoreEl=$("oppScore");
const clockEl=$("clock"), statusEl=$("status"), centerEl=$("center");

const S = { me:null, myReps:0, oppReps:0, active:false, duration:60, startTs:0,
            phase:"idle", winner:null, name:"You", intent:null, code:null, exercise:"squats", oppName:"Opponent" };
let chosenExercise = "squats";   // creator's pick on the landing screen
let busy = false;                // true while a game is starting/active (blocks re-entry)

// Identity comes from Google login. auth.js sets window.PID (= var PID here, since this
// is a classic script) to the Supabase user id before the app boots. Until then we fall
// back to a local anon id so nothing throws.
var PID = (function(){
  try{
    let id = localStorage.getItem("gymoggle_pid");
    if(!id){ id = "p_"+Math.random().toString(36).slice(2,10)+Date.now().toString(36); localStorage.setItem("gymoggle_pid", id); }
    return id;
  }catch(e){ return "p_"+Math.random().toString(36).slice(2,10); }
})();
const other = p => p==="P1" ? "P2" : "P1";

/* ============================================================
   SOUND — all synthesized in-code with Web Audio (no files)
   ============================================================ */
let actx=null, master=null, muted=false;
function initAudio(){
  if(!actx){
    actx = new (window.AudioContext||window.webkitAudioContext)();
    master = actx.createGain();
    master.gain.value = muted?0:1;
    master.connect(actx.destination);
  }
  if(actx.state==="suspended") actx.resume();
  // prime text-to-speech on this user gesture (needed on mobile)
  try{ if(window.speechSynthesis) speechSynthesis.resume(); }catch(e){}
}

/* ---- text-to-speech: read cues aloud (phones can't read the on-screen text) ---- */
const sayable = t => (t||"").replace(/[^\x00-\x7F]/g,"").replace(/\s+/g," ").trim();
function speak(text, interrupt){
  try{
    if(muted || !window.speechSynthesis) return;
    const words = sayable(text);
    if(!words) return;
    if(interrupt) speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(words);
    u.lang="en-US"; u.rate=1.06; u.pitch=1.0; u.volume=1.0;
    speechSynthesis.speak(u);
  }catch(e){}
}
function beep(freq=440, dur=0.14, type="square", vol=0.25, when=0){
  if(!actx||!master) return;
  const t=actx.currentTime+when;
  const o=actx.createOscillator(), g=actx.createGain();
  o.type=type; o.frequency.value=freq;
  g.gain.setValueAtTime(0.0001,t);
  g.gain.linearRampToValueAtTime(vol,t+0.01);
  g.gain.exponentialRampToValueAtTime(0.0001,t+dur);
  o.connect(g).connect(master);
  o.start(t); o.stop(t+dur+0.02);
}
function repPop(){
  if(!actx||!master) return;
  const t=actx.currentTime;
  const o=actx.createOscillator(), g=actx.createGain();
  o.type="triangle";
  o.frequency.setValueAtTime(560,t);
  o.frequency.exponentialRampToValueAtTime(920,t+0.05);
  g.gain.setValueAtTime(0.3,t);
  g.gain.exponentialRampToValueAtTime(0.0001,t+0.12);
  o.connect(g).connect(master);
  o.start(t); o.stop(t+0.14);
}
function whistle(){ beep(1650,0.16,"square",0.25,0); beep(1650,0.13,"square",0.22,0.2); beep(1980,0.22,"square",0.24,0.4); }
/* Upbeat workout loop, synthesized (no files). Optionally set MUSIC_URL
   to an mp3 and it'll use that instead. Mute button controls both. */
const MUSIC_URL = "";   // e.g. "https://yoursite.netlify.app/beat.mp3"
let musicGain=null, beatTimer=null, beatStep=0, nextNoteTime=0, musicEl=null;
const BPM=128, STEP=30/BPM;   // seconds per 8th note

function kick(t){
  const o=actx.createOscillator(), g=actx.createGain();
  o.frequency.setValueAtTime(130,t); o.frequency.exponentialRampToValueAtTime(45,t+0.11);
  g.gain.setValueAtTime(0.9,t); g.gain.exponentialRampToValueAtTime(0.001,t+0.18);
  o.connect(g).connect(musicGain); o.start(t); o.stop(t+0.2);
}
function hat(t){
  const size=Math.floor(0.03*actx.sampleRate);
  const buf=actx.createBuffer(1,size,actx.sampleRate); const d=buf.getChannelData(0);
  for(let i=0;i<size;i++) d[i]=Math.random()*2-1;
  const n=actx.createBufferSource(); n.buffer=buf;
  const hp=actx.createBiquadFilter(); hp.type="highpass"; hp.frequency.value=7000;
  const g=actx.createGain(); g.gain.setValueAtTime(0.25,t); g.gain.exponentialRampToValueAtTime(0.001,t+0.04);
  n.connect(hp).connect(g).connect(musicGain); n.start(t); n.stop(t+0.05);
}
function bass(t,freq){
  const o=actx.createOscillator(), g=actx.createGain();
  o.type="triangle"; o.frequency.value=freq;
  g.gain.setValueAtTime(0.0001,t); g.gain.linearRampToValueAtTime(0.35,t+0.02);
  g.gain.exponentialRampToValueAtTime(0.001,t+STEP*0.9);
  o.connect(g).connect(musicGain); o.start(t); o.stop(t+STEP);
}
const BASSLINE=[55,0,55,65,55,0,73,65];   // simple riff over 8 steps (Hz), 0=rest
function playStep(step,t){
  if(step%4===0) kick(t);            // kick on the beat
  if(step%2===1) hat(t);             // hats offbeat
  const f=BASSLINE[step%8]; if(f) bass(t,f);
}
function startBeat(){
  if(!actx||!master) return;
  if(!musicGain){ musicGain=actx.createGain(); musicGain.gain.value=0.32; musicGain.connect(master); }
  if(MUSIC_URL){
    if(!musicEl){ musicEl=new Audio(MUSIC_URL); musicEl.loop=true; musicEl.crossOrigin="anonymous";
      try{ actx.createMediaElementSource(musicEl).connect(musicGain); }catch(e){} }
    musicEl.currentTime=0; musicEl.play().catch(()=>{});
    return;
  }
  if(beatTimer) return;
  beatStep=0; nextNoteTime=actx.currentTime+0.05;
  const scheduler=()=>{
    while(nextNoteTime < actx.currentTime + 0.12){
      playStep(beatStep,nextNoteTime);
      nextNoteTime+=STEP; beatStep++;
    }
    beatTimer=setTimeout(scheduler,25);
  };
  scheduler();
}
function stopBeat(){
  if(musicEl){ try{ musicEl.pause(); }catch(e){} }
  if(beatTimer){ clearTimeout(beatTimer); beatTimer=null; }
}
$("muteBtn").addEventListener("click",()=>{
  muted=!muted;
  if(master) master.gain.value=muted?0:1;
  if(muted){ try{ if(window.speechSynthesis) speechSynthesis.cancel(); }catch(e){} }
  $("muteBtn").textContent=muted?"🔇":"🔊";
});

/* ---------- model + camera ---------- */
let landmarker=null, camStarted=false;
let PoseLandmarker=null, FilesetResolver=null;
async function initModel(){
  if(!PoseLandmarker){   // dynamic import: works from a classic script
    const mp = await import("https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14");
    PoseLandmarker = mp.PoseLandmarker; FilesetResolver = mp.FilesetResolver;
  }
  const fileset = await FilesetResolver.forVisionTasks(
    "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm");
  landmarker = await PoseLandmarker.createFromOptions(fileset,{
    baseOptions:{
      modelAssetPath:"https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task",
      delegate:"GPU"
    },
    runningMode:"VIDEO", numPoses:1
  });
}
async function initCamera(){
  if(camStarted) return;
  const stream = await navigator.mediaDevices.getUserMedia({
    video:{ facingMode:"user", width:{ideal:960}, height:{ideal:720} }, audio:false });
  video.srcObject = stream;
  window.camStream = stream;          // a MediaStream can feed multiple <video>s (FFA grid)
  await video.play();
  overlay.width=video.videoWidth; overlay.height=video.videoHeight;
  camStarted=true;
}

/* ---------- detection loop ---------- */
let lastTs=-1, looping=false;
function loop(){
  if(landmarker && video.readyState>=2){
    const ts=performance.now();
    if(ts!==lastTs){
      lastTs=ts;
      const res=landmarker.detectForVideo(video,ts);
      octx.clearRect(0,0,overlay.width,overlay.height);
      if(res.landmarks && res.landmarks.length){
        const lms=res.landmarks[0];
        const {down,draw}=processPose(lms);
        drawPose(lms, draw||[], flash>0 ? "#ffffff" : (down? "#ff2e7e":"#22e0d6"));
        if(flash>0) flash--;
      }
    }
  }
  requestAnimationFrame(loop);
}
function drawPose(lms,conns,color){
  octx.save(); octx.strokeStyle=color; octx.fillStyle=color; octx.lineWidth=4;
  const pts=new Set();
  for(const [a,b] of conns){ pts.add(a); pts.add(b);
    if(vis(lms[a])>0.5 && vis(lms[b])>0.5){
      octx.beginPath();
      octx.moveTo(lms[a].x*overlay.width, lms[a].y*overlay.height);
      octx.lineTo(lms[b].x*overlay.width, lms[b].y*overlay.height); octx.stroke(); } }
  for(const i of pts){ if(vis(lms[i])>0.5){
    octx.beginPath(); octx.arc(lms[i].x*overlay.width, lms[i].y*overlay.height,6,0,7); octx.fill(); } }
  octx.restore();
}


/* ---------- misc ---------- */
function toast(msg){ const t=$("toast"); t.textContent=msg; t.classList.add("on"); setTimeout(()=>t.classList.remove("on"),4000); }

/* ---------- dismiss the intro splash after the animation ---------- */
try{
  const sp=$("splash");
  if(sp){
    setTimeout(()=>{ sp.style.opacity="0"; setTimeout(()=>{ sp.style.display="none"; }, 480); }, 2850);
  }
}catch(e){}

/* ---------- decorative sparkles on the landing (guarded, non-critical) ---------- */
try{
  const box=$("sparkles");
  if(box){
    for(let i=0;i<16;i++){
      const s=document.createElement("i");
      s.style.left=Math.random()*100+"%";
      s.style.animationDuration=(6+Math.random()*6)+"s";
      s.style.animationDelay=(-Math.random()*8)+"s";
      const sc=0.5+Math.random()*1.1; s.style.width=s.style.height=(4*sc)+"px";
      box.appendChild(s);
    }
  }
}catch(e){}

// best-effort: tell the server we're gone if the tab closes mid-game
window.addEventListener("pagehide", ()=>{ try{ if(ws && ws.readyState===1) ws.send(JSON.stringify({type:"leave"})); }catch(e){} });

/* ---------- How to Play wiring ---------- */
(function(){
  const b=$("howBtn"); if(b) b.addEventListener("click", ()=> show("how"));
  const back=$("howBack"); if(back) back.addEventListener("click", ()=> show("landing"));
  const go=$("howStart"); if(go) go.addEventListener("click", ()=> show("landing"));
})();

/* ---------- the app boots only AFTER Google login completes (auth.js calls this) ---------- */
function onAuthReady(){
  // name field defaults to the chosen username
  const nm = $("name"); if(nm && window.PNAME) nm.value = window.PNAME;
  // arrived via a share link (?join=CODE)
  if(JOIN_CODE && JOIN_CODE.length===4){
    $("joinCode").value = JOIN_CODE;
    const note=$("challengeNote"); if(note) note.style.display="block";
  }
}