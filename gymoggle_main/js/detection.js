/* GymOggle — detection: the 4 exercises + rep state machine
   Part of the GymOggle app. Loaded as a classic script; modules share globals. */

/* ---------- rep detection (ported from Python) ---------- */
function angle(a,b,c){
  const rad = Math.atan2(c.y-b.y, c.x-b.x) - Math.atan2(a.y-b.y, a.x-b.x);
  let deg = Math.abs(rad*180/Math.PI);
  if(deg>180) deg = 360-deg;
  return deg;
}
let stage="up", flash=0;
let jackFeetMin=null;   // learned closed-feet stance for jumping jacks (resets each run)
const vis = lm => (lm.visibility==null ? 1 : lm.visibility);

/* ============================================================
   >>> PUSH-UP ANTI-CHEAT: HIP ANGLE THRESHOLD <<<  (TUNE ME)
   Real push-up  = body flat/straight -> hip angle (shoulder-hip-knee) ~180.
   Knee push-up  = hips pike up        -> hip angle noticeably lower.
   A rep only counts if the hip stays STRAIGHTER than this many degrees.
   Raise it = stricter (harder to fake). Lower it = more lenient.
   ============================================================ */
let PUSHUP_HIP_MIN = 155;   // <<< CHANGE THIS NUMBER to tune the knee-push-up gate
let PUSHUP_UP_ELBOW = 150;  // <<< arms straighter than this = "up" (top of push-up)
let PUSHUP_DOWN_ELBOW = 100;
let PLANK_HIP_MIN = 150;    // <<< hip must stay straighter than this. Sag/pike = broken plank.
const PLANK_GRACE = 1.2;    // <<< seconds of broken form before the plank counts as FAILED// <<< arms bent tighter than this = "down" (bottom of push-up)
const SHOW_HIP_DEBUG = true; // <<< shows the live hip angle on screen during push-ups; set false when done tuning

/* ---- Per-exercise detection. Each measure() returns:
   {ok:false}                       -> body not framed well enough
   {ok:true, down:bool, up:bool, draw:[[a,b],...]}   -> current pose state
   "down"=the flexed/bottom position, "up"=the extended/top position.
   Tune the angle thresholds below per exercise if counts feel off. ---- */
const EXERCISES = {
  squats: {
    label:"Squats", warn:"Step back — legs not in frame",
    measure(lms){
      const need=[23,25,27,24,26,28];
      if(Math.min(...need.map(i=>vis(lms[i]))) < 0.6) return {ok:false};
      const la=angle(lms[23],lms[25],lms[27]);   // left  hip-knee-ankle
      const ra=angle(lms[24],lms[26],lms[28]);   // right hip-knee-ankle
      return {ok:true, down:Math.max(la,ra)<100, up:Math.min(la,ra)>160,
              draw:[[23,25],[25,27],[24,26],[26,28],[23,24]]};
    }
  },
  pushups: {
    label:"Push-ups", warn:"Side-on — hands to feet in frame",
    // A real push-up = the whole body drops toward the floor and rises back up.
    // We measure how high the shoulder sits ABOVE the planted hands (wrist),
    // scaled by torso length so it's the same near/far from camera.
    // Lying flat and bending your arms keeps the shoulder on the floor -> no rise -> no rep.
    measure(lms){
      const sides=[[11,23,25,13,15],[12,24,26,14,16]]; // shoulder,hip,knee,elbow,wrist
      let best=null,bv=-1;
      for(const a of sides){
        const v=Math.min(vis(lms[a[0]]),vis(lms[a[1]]),vis(lms[a[3]]),vis(lms[a[4]]));
        if(v>bv){bv=v;best=a;}
      }
      if(bv<0.5) return {ok:false};
      const [sh,hip,kn,el,wr]=best;
      const S_=lms[sh], H=lms[hip];
      // GATE 1 — ORIENTATION: body must be roughly HORIZONTAL (a plank). Standing is vertical -> blocked.
      if(Math.abs(H.x - S_.x) < Math.abs(H.y - S_.y)) return {ok:false, warnMsg:"Get horizontal — this is a plank position"};

      // GATE 2 — HIP ANGLE ANTI-CHEAT (shoulder-hip-knee): straight(~180)=real, piked=knee push-up -> blocked.
      const hipAngle = angle(S_, H, lms[kn]);
      window.__hipAngle = hipAngle;
      if(hipAngle < PUSHUP_HIP_MIN) return {ok:false, hip:hipAngle, warnMsg:"Straighten your body — no knee push-ups!"};

      // UP/DOWN — ELBOW ANGLE (shoulder-elbow-wrist): extended=up, bent=down. Reliable now that the
      // two gates above block standing/knee cheats.
      const elbow = angle(lms[sh], lms[el], lms[wr]);
      window.__elbowAngle = elbow;
      return {ok:true, hip:hipAngle, elbow:elbow,
              up: elbow > PUSHUP_UP_ELBOW, down: elbow < PUSHUP_DOWN_ELBOW,
              draw:[[sh,el],[el,wr],[sh,hip],[hip,kn]]};
    }
  },
  situps: {
    label:"Sit-ups", warn:"Side-on, lying down — full body in frame",
    // Torso angle shoulder-hip-knee. Widened range so only a FULL lie-down-to-sit-up
    // swing counts (small wiggles no longer register). Arms are never used.
    measure(lms){
      const sides=[[11,23,25],[12,24,26]];
      let best=null,bv=-1;
      for(const a of sides){ const v=Math.min(vis(lms[a[0]]),vis(lms[a[1]]),vis(lms[a[2]])); if(v>bv){bv=v;best=a;} }
      if(bv<0.5) return {ok:false};
      const [s,h,k]=best;
      const S_=lms[s], H=lms[h];
      const ang=angle(lms[s],lms[h],lms[k]);
      // The "down" (lying flat) state only counts if the body is actually HORIZONTAL.
      // Standing straight has the same shoulder-hip-knee angle as lying, so without
      // this gate you could stand and bend to fake sit-ups. Vertical body -> no "down".
      const lyingFlat = Math.abs(H.x - S_.x) > Math.abs(H.y - S_.y);
      return {ok:true, down:(ang>140 && lyingFlat), up:ang<75, draw:[[s,h],[h,k]]};
    }
  },
  plank: {
    label:"Plank", warn:"Get into a plank — side-on to the camera",
    hold:true,                     // <-- this exercise is a HOLD, not reps
    // Reuses the two push-up gates: body must be HORIZONTAL and the hip must stay
    // STRAIGHT. Sagging or piking the hips = broken form. Same anti-cheat, no timer.
    measure(lms){
      const sides=[[11,23,25],[12,24,26]];   // shoulder, hip, knee
      let best=null, bv=-1;
      for(const a of sides){
        const v=Math.min(vis(lms[a[0]]),vis(lms[a[1]]),vis(lms[a[2]]));
        if(v>bv){bv=v;best=a;}
      }
      if(bv<0.5) return {ok:false, warnMsg:"Step back — whole body side-on to the camera"};
      const [sh,hip,kn]=best;
      const S_=lms[sh], H=lms[hip];
      // GATE 1 — horizontal (a plank is a horizontal body). Standing = blocked.
      if(Math.abs(H.x - S_.x) < Math.abs(H.y - S_.y))
        return {ok:true, holding:false, warnMsg:"Get horizontal — plank position"};
      // GATE 2 — straight hip. Sag or pike breaks the plank.
      const hipAngle = angle(S_, H, lms[kn]);
      const straight = hipAngle > PLANK_HIP_MIN;
      return {ok:true, holding:straight, hip:hipAngle,
              warnMsg: straight ? "" : (hipAngle < PLANK_HIP_MIN-25 ? "Hips are sagging!" : "Keep your body straight!"),
              draw:[[sh,hip],[hip,kn]]};
    }
  },
  jacks: {
    label:"Jumping Jacks", warn:"Step back — whole body in frame",
    // OPEN = hands above head AND feet apart.  CLOSED = hands down AND feet together.
    measure(lms){
      const need=[11,12,15,16,27,28];
      for(const i of need){ if(vis(lms[i])<0.5) return {ok:false}; }
      const shY=(lms[11].y+lms[12].y)/2;
      const shW=Math.abs(lms[11].x-lms[12].x)||0.001;
      const wrY=(lms[15].y+lms[16].y)/2;                 // y grows downward
      const spread=Math.abs(lms[27].x-lms[28].x)/shW;    // ankle spread in shoulder-widths
      const handsUp   = wrY < shY;
      const handsDown = wrY > shY + 0.10;
      const feetApart = spread > 1.30;
      const feetTogether = spread < 0.95;
      // one full cycle (open -> closed) = 1 rep
      return {ok:true, down:(handsUp && feetApart), up:(handsDown && feetTogether),
              draw:[[11,13],[13,15],[12,14],[14,16],[23,25],[25,27],[24,26],[26,28]]};
    }
  }
};

/* ---------- HOLD exercises (plank): time held, not reps ---------- */
const HOLD = { secs:0, holding:false, brokeAt:0, failed:false, lastTs:0 };
function resetHold(){ HOLD.secs=0; HOLD.holding=false; HOLD.brokeAt=0; HOLD.failed=false; HOLD.lastTs=performance.now(); }

function processHold(cfg, lms){
  const m = cfg.measure(lms);
  const now = performance.now();
  const dt = Math.min(0.25, (now - (HOLD.lastTs||now))/1000);
  HOLD.lastTs = now;

  const good = m.ok && m.holding;
  if(good){
    HOLD.secs += dt;                 // clock only runs while the form is good
    HOLD.holding = true;
    HOLD.brokeAt = 0;
    if(S.active || SOLO.on) setStatus("HOLD! " + HOLD.secs.toFixed(1) + "s");
  } else {
    HOLD.holding = false;
    if(!HOLD.brokeAt) HOLD.brokeAt = now;
    const brokenFor = (now - HOLD.brokeAt)/1000;
    if(S.active || SOLO.on)
      setStatus((m.warnMsg||cfg.warn) + "  —  " + Math.max(0,(PLANK_GRACE-brokenFor)).toFixed(1) + "s", true);
    // a grace window, so a wobble doesn't instantly end it
    if(brokenFor > PLANK_GRACE && !HOLD.failed){
      HOLD.failed = true;
      onHoldFailed();                // wired by multiplayer.js / daily.js
    }
  }
  onHoldTick(HOLD.secs, HOLD.holding);   // wired by multiplayer.js / daily.js
  return {down:false, draw:m.draw||null};
}
/* these get overridden by whichever mode is running */
let onHoldFailed = ()=>{};
let onHoldTick   = ()=>{};

function processPose(lms){
  const cfg = EXERCISES[S.exercise] || EXERCISES.squats;
  if(cfg.hold) return processHold(cfg, lms);
  const m = cfg.measure(lms);
  // live hip-angle readout (push-ups only) so you can tune PUSHUP_HIP_MIN by eye
  if(SHOW_HIP_DEBUG && S.exercise==="pushups"){
    const d=$("dbgHip");
    if(d){ const h=(m.hip!=null?Math.round(m.hip):"—"), e=(m.elbow!=null?Math.round(m.elbow):"—");
      d.textContent = "hip "+h+"°  ·  elbow "+e+"°   (hip>"+PUSHUP_HIP_MIN+"  up>"+PUSHUP_UP_ELBOW+"  down<"+PUSHUP_DOWN_ELBOW+")"; }
  }
  if(!m.ok){ if(S.active) setStatus(m.warnMsg||cfg.warn,true); return {down:false, draw:null}; }
  if(m.down){ stage="down"; }
  if(m.up && stage==="down"){
    stage="up"; flash=8;
    if(SOLO.on){ soloRep(); }
    else if(S.active){
      S.myReps++; youScoreEl.textContent=S.myReps; pushReps();
      repPop(); oppRun=0; myLastRepTs=performance.now(); updatePresence();
      youScoreEl.style.transform="scale(1.25)";
      setTimeout(()=>youScoreEl.style.transform="scale(1)",90);
    }
  }
  return {down:m.down, draw:m.draw};
}