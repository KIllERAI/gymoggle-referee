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
let PUSHUP_FRONT_UP   = 1.05;  // <<< FRONT view: shoulders this far above hands (in shoulder-widths) = UP
let PUSHUP_FRONT_DOWN = 0.60;  // <<< FRONT view: this close to the hands = DOWN (chest lowered)
let PLANK_HIP_MIN = 150;
let plankBaseY = null;   // learned resting chest height for the current hold
let PLANK_LEVEL_MAX = 0.60;   // <<< body counts as "in a plank" when shoulder~hip height gap < this
let PLANK_DROP_MAX  = 0.35;   // <<< chest sinks more than this (shoulder-widths) below its high point = COLLAPSED    // <<< hip must stay straighter than this. Sag/pike = broken plank.
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
    label:"Push-ups", warn:"Hands on the floor — whole body in frame",
    // Works from EITHER angle. We auto-detect which one you're using.
    //
    //  FRONT VIEW (camera in front of you, like PushSlayer):
    //     As you lower, your shoulders drop toward your hands AND move closer to
    //     the camera. So the shoulder->hand gap shrinks while shoulder width grows.
    //     Measuring that gap IN SHOULDER-WIDTHS gives a scale-free "depth" signal
    //     that needs no side view. (This is the trapezoid trick.)
    //
    //  SIDE VIEW (camera side-on):
    //     Elbow angle for up/down + the HIP-ANGLE anti-cheat that blocks knee
    //     push-ups. Only the side view can see a piked hip, so only it can catch
    //     that cheat.
    measure(lms){
      const LS=lms[11], RS=lms[12], LW=lms[15], RW=lms[16], LH=lms[23], RH=lms[24];
      if(Math.min(vis(LS),vis(RS),vis(LW),vis(RW)) < 0.5)
        return {ok:false, warnMsg:"Step back — shoulders and hands must be visible"};

      const shMidX=(LS.x+RS.x)/2, shMidY=(LS.y+RS.y)/2;
      const hipMidX=(LH.x+RH.x)/2, hipMidY=(LH.y+RH.y)/2;
      const shW = Math.hypot(LS.x-RS.x, LS.y-RS.y) || 0.001;

      // Which way is the camera? Side-on = the body runs ACROSS the image.
      const bodyDx=Math.abs(hipMidX-shMidX), bodyDy=Math.abs(hipMidY-shMidY);
      const sideView = bodyDx > bodyDy;

      /* ---------------- FRONT VIEW ---------------- */
      if(!sideView){
        const wrMidY=(LW.y+RW.y)/2;
        // shoulders sit ABOVE the hands; measure that gap in shoulder-widths.
        // top of the rep -> big.   bottom -> small.
        const depth = (wrMidY - shMidY) / shW;
        window.__pushDepth = depth;
        // must actually be in a push-up shape: hands below the shoulders
        if(wrMidY < shMidY)
          return {ok:false, warnMsg:"Get into a push-up — hands on the floor"};
        return {ok:true, depth, front:true,
                up:   depth > PUSHUP_FRONT_UP,
                down: depth < PUSHUP_FRONT_DOWN,
                draw:[[11,12],[12,16],[16,15],[15,11],[11,13],[13,15],[12,14],[14,16]]};
      }

      /* ---------------- SIDE VIEW (keeps the knee-cheat gate) ---------------- */
      const sides=[[11,23,25,13,15],[12,24,26,14,16]];
      let best=null,bv=-1;
      for(const a of sides){
        const v=Math.min(vis(lms[a[0]]),vis(lms[a[1]]),vis(lms[a[3]]),vis(lms[a[4]]));
        if(v>bv){bv=v;best=a;}
      }
      if(bv<0.5) return {ok:false};
      const [sh,hip,kn,el,wr]=best;
      const hipAngle = angle(lms[sh], lms[hip], lms[kn]);
      window.__hipAngle = hipAngle;
      if(hipAngle < PUSHUP_HIP_MIN)
        return {ok:false, hip:hipAngle, warnMsg:"Straighten your body — no knee push-ups!"};
      const elbow = angle(lms[sh], lms[el], lms[wr]);
      return {ok:true, hip:hipAngle, elbow, front:false,
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
    label:"Plank", warn:"Get into a plank position",
    hold:true,
    // The real question for a plank hold is simple: has your CHEST/TORSO dropped to
    // the floor (collapsed), or are you still up holding it? We track the torso's
    // resting height when you first get into position, and you "break" when it sinks.
    // Works front OR side (auto): from the front we also require the body to be
    // level (shoulders ~ hips) so standing doesn't count as a plank.
    measure(lms){
      const LS=lms[11], RS=lms[12], LH=lms[23], RH=lms[24], LK=lms[25], RK=lms[26];
      if(Math.min(vis(LS),vis(RS),vis(LH),vis(RH)) < 0.5)
        return {ok:false, holding:false, warnMsg:"Step back — whole body in frame"};

      const shMidX=(LS.x+RS.x)/2, shMidY=(LS.y+RS.y)/2;
      const hipMidX=(LH.x+RH.x)/2, hipMidY=(LH.y+RH.y)/2;
      const shW=Math.hypot(LS.x-RS.x, LS.y-RS.y)||0.001;
      const torsoMidY=(shMidY+hipMidY)/2;                 // chest/belly height
      const bodyDx=Math.abs(hipMidX-shMidX), bodyDy=Math.abs(hipMidY-shMidY);
      const sideView = bodyDx > bodyDy;

      // "in position" = body roughly LEVEL (a plank is horizontal-ish).
      // measured in shoulder-widths so it's scale/ distance-proof.
      const level = Math.abs(hipMidY-shMidY)/shW;
      const inPlank = sideView ? true : (level < PLANK_LEVEL_MAX);

      // torso baseline: the HIGHEST (smallest y) torso we've seen while holding.
      // if the chest sinks well below that baseline -> collapsed -> broken.
      if(inPlank){
        if(plankBaseY===null || torsoMidY < plankBaseY) plankBaseY = torsoMidY;
      }
      const sank = plankBaseY!==null ? (torsoMidY - plankBaseY)/shW : 0;  // how far chest dropped
      window.__plankSank = sank; window.__plankLevel = level;

      const collapsed = sank > PLANK_DROP_MAX;             // chest hit the deck
      const holding = inPlank && !collapsed;
      return {ok:true, holding, front:!sideView, sank, level,
              warnMsg: !inPlank ? "Get down into a plank"
                     : collapsed ? "You dropped!" : "",
              draw: sideView ? [[11,23],[23,25]] : [[11,12],[23,24],[11,23],[12,24]]};
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
function resetHold(){ HOLD.secs=0; HOLD.holding=false; HOLD.brokeAt=0; HOLD.failed=false; HOLD.lastTs=performance.now(); plankBaseY=null; }

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
  if(SHOW_HIP_DEBUG && S.exercise==="plank"){
    const d=$("dbgHip");
    if(d && d.style) d.style.display="block";
    if(d){ if(m.front){ d.textContent="FRONT · level "+(m.level!=null?m.level.toFixed(2):"—")+"  (flat < "+PLANK_FRONT_LEVEL+")"+(m.holding?"  HOLDING":""); }
           else { d.textContent="SIDE · hip "+(m.hip!=null?Math.round(m.hip):"—")+"°  (>"+PLANK_HIP_MIN+")"+(m.holding?"  HOLDING":""); } }
  }
  if(SHOW_HIP_DEBUG && S.exercise==="pushups"){
    const d=$("dbgHip");
    if(d){
      if(m.front){
        d.textContent = "FRONT · depth "+(m.depth!=null?m.depth.toFixed(2):"—")
                      + "   (up>"+PUSHUP_FRONT_UP+"  down<"+PUSHUP_FRONT_DOWN+")";
      } else {
        const h=(m.hip!=null?Math.round(m.hip):"—"), e=(m.elbow!=null?Math.round(m.elbow):"—");
        d.textContent = "SIDE · hip "+h+"°  elbow "+e+"°   (hip>"+PUSHUP_HIP_MIN+"  up>"+PUSHUP_UP_ELBOW+"  down<"+PUSHUP_DOWN_ELBOW+")";
      }
    }
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