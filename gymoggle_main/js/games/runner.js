/* GymOggle — 🦍 endless runner — PARKED. Not loaded by index.html.
   To revive: add <script src="js/games/runner.js"></script> and restore the
   two hooks (runPose in processPose, runStep in loop).
   Part of the GymOggle app. Loaded as a classic script; modules share globals. */

/* ==========================================================================
   🦍 ESCAPE THE JUNGLE — endless runner
   Controls (4 mechanics, nothing else):
     JUMP  = both feet off the ground      DUCK  = bend your upper body
     RAISE LEFT hand = move left lane      RAISE RIGHT hand = move right lane
   The runner always runs. The obstacles ARE the workout.
   ========================================================================== */
/* --- Kenney medieval tiles (CC0), embedded --- */
const RUN_ART_SRC = {"crate": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEYAAABGCAYAAABxLuKEAAACt0lEQVR42u3bT2sTQRQA8Le7L8VUbaG1IhRtaoy2PXrw0qIeWr+B38sP46mCUCiCHnLxIoUiKSi0NLEmMVn3z4yHMIdkszHZndl5C+9BIJDNZPaXmcx7O1mn+e6tBI5EuEwwPfCq67MCjxiGYRiGYRiGYRiGYRiGYRiO8XCuW8dj1fX30w/QPv+Wu+G7typQXfJg7fkruLP1NFMbg+H0Os7/cQ79r59gGMTQ88PcfV2v78D2wdF4ETl5kDogL47qcKd5AgCQGccGylQYyjhFoaTCUMT5e3mhFeXek12o7R+mvo6z3kwFJ+p2tKJsNPag/vINRFGcDYYCTtTtwO8vxzAY+FpR/hc4T2O2cKLeLysoc8PYwAlu2tZQFoIpEie4acPl6XsY/BlaQVkYpgicfusMOs0T7T+0iwZm+TBTOOq5ziU5DUUIoR/GJI7O5K22fzhzSTZWRG4fHMF6fSf3SfT8EIbB6ATCWBjNaI1OJZMjZ6VaGaX/YbZverXWyI2iBYYSzmqtAZsvXmspVrXAUMDRiaIVxiaObhTtMDZwJlHQ82jCFImjY/UpFKYIHJMoRmFM4tx+1DCKkjvBmyeW729CLPInbSoJXKlWYOPhlulumx0x/dYZ/Pz8EaJYAoAAz3W1jBzdF9gLhVFV8vISgh/EpcNBkyiqIKygC2EkSoWDplFUlA0HEZMJkZQSpJQghNSCQh3HdR1wnNFj5ohRBwkRa0OhjONO6QOanD5lwtEOk/UaLXUctIFSBhy0hTKJs/Z4F9BzyOyVo00UFQ+e7Y3VPhRw0DbKZJVM5Y8ESAmFEg5SQ6GCgxRRKOCkwqgtTFsoReIIIRLZL87awrSNUhSOEDJR/iB1FFvTCsuAYgMHy4JSNI7D912nXIpggpTlmu+75hHDMAzDMAzDMAzDMAzDMAzDkYh/a4U4pUTt8koAAAAASUVORK5CYII=", "crate2": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEYAAABGCAYAAABxLuKEAAACO0lEQVR42u3bP0/CQBgG8KdHaVyMg+jigkES8AO4aNRB+QZ+Lz+PizpojEYSdTD4HxMXFQdBRKR3DkoioRSUO3rXe5+EiRTKj7d3915Tp7i5IUDpCiOC4LiPrw1SoIohGIIhGIIhGIIhGIIhGIKhdMZ5Lm/17K6bzU+0fL+7wUok4HlJ5SdXfw/u4yrXJdwfbEv7nunsPLIrhc7fGHaA5yXhIanVPzkKlL4wuqXxcA1xeYjU+Biqjc+hP28yk8Ps0nrwtoNJKLWzfbw3fSkoqbk80otrPd83AqZ+dYL61ak0lKnsPDLLBbRavrkw1bM9fDzcSEcxerqOCkVrmMrxTmQo2sJUjnfwdn8ZGYqWMDqgaAcjGyU1l++JwjkPPVabWalWvpCKMpnJIb24Fjola18xtfIFXoq7UlF6rWgHjfKKYcyB43y/2hFCQAgBzoV0lIl0dmiUkVQMY6wDBQAcxwFjTAnKzMKq2fsx1buStiiRwVTvSng62tYWJRIY1ShuIiHlPF2TUWTMPpFVTHshZRLKSCqGc4HX23Pt1imRV4yOi7fIYUxFUQpjMooyGNNRlMDEAQUAXNftXhD9bvKsGGgDGt3Aimk3edYMtAGNLqPLR9EYE0eUoWHiijIUTJxR/g0Td5R/wdiA8mcYW1D+BGMTysAwtqGEwrR33mxACbpd64bdwrSlUjgX4NwfrGJsvHz6wtiOEghDKD87DPTctaLuOq6h566pYgiGYAiGYAiGYAiGYAiGYCjd+QLb0TItr4y9RQAAAABJRU5ErkJggg==", "gate": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEYAAABGCAYAAABxLuKEAAAA4klEQVR42u3aMQrCQBAF0InaiwgRJaew0ZsJVlaCZ7H1GFYWKTxCwDNotwSjmFgZeR8Whiz5DK9Jk2y5Wt+jlu3hkOZpnqf5VlUREbHfbKJN+t4zCHkZMGDAgAEDBgwYMGDAgBEwYMCAAQMGDBgwYMAIGDBgwIABAwYMGDBgBExXmMv5nOZbVaXzfPcpfe8ZzotiV39wLcsYTyYxWywaxafjsfUife9pwLwq6brEP/SM3pXUX/hmib73ZM8/QIuvEhgwYMCAAQMGDBgwAgYMGDBgwIABAwYMGDACBgwYMGB+Iw9d5J3NC08XhwAAAABJRU5ErkJggg==", "gate2": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEYAAABGCAYAAABxLuKEAAAEyklEQVR42u2bTWsbRxjH/5bXkt8oxi7OpaWBtFAfGkoo5JBTb80x0HO+Tj5BrzkX3EMOgfYU3EMCwS4xITrEASvFUSyktbQezc7uzs6OepC0Xds7I68s2fuiPyxIKzGyfn7e5nlGc3/s/N3DBMRsW/v68soKrltCCARCAAA81w3vRx+r7hnIuKSU8DmHEAIOYwiEgM/5ldfNJBjPdc9cKgVBACll33p8/39LijyOWtdUwBiGcWHx6GtXdQmHMbiMXQAhpewDCAL4nIfPU2Mx5UoF5Uploi5iUwpG6QXX8H0fYngp/hm5cyWHMdiUwmXsjEv4nIex5DqUCjBCCFBCYFOK3iAmSCnBPQ/c8ybiGiqtrK4CAP49PEwPGCEEiGWBURre45yDuy78mAB5Wfmc49SyAAAnrRYA4JdHjwAA8/Pz+Or27fC9J80mAOD3p09vHsx5IEEQwHNdcM9Dr9cbC8JJqwXS6eDUsuBE3HCoXx8/Tq8rxQFxHQfc8xKts7a+jnKlgsXlZfz25El2Y4yUEpQQdAlBb5BOkwJZXFrCt1tbWFtfh7GwELpAZoOv57pomyYCIRIDMZtN/HDvHr5YW0O5UsHG5ua1WfdUwRDLArEsSCnDKnVUDDGbTTTqdTTqdTiM4eeHD28kMRjTiiUd04Q3yC6M0rA01wGpHRyg8flzKuqpiYPhnKPVaKAnZb+Md5yRWeV9tYrahw+pKjQnCsamFFa7DTGwklFV6nG9juqbN7HpNTdgbErRMc2witXFkoVyGa9evEiN28SpNEkonuuOhLKxuYnvtrZSDWUiFhOFouviGYaB7+/exdzcXCZ6PqXrgLK4tIQf79/Hl7duZaYZNrbFeK57aSg/PXgAY2EBWdJYYKSUMJvNkVBWVlfxzZ07mYMyFhgpJVqNBrjnaaGsbWzg68j2PmtKHGOsdhue68LudpXvOarVMg0lMRiHMVBCtCn5qFbD/u4usq5SEhdqm2Z/dqNoNZ52OrmAkgjM0IVULQOfc7za2UFedCkww4o22ps9r92XL2MHWbkGY7XbcBhTxpX31WrYdC4MGJtSMNtWutBpp4ODahV500gwxLLgaOqVvATbRGC6g7iiykKHBwcgg/lNocBQQpQduGHnLa8q6WKL3e0qe7Xv9vdzlYUuDYYSojx7wmwbnz5+RJ4VC4ZzDkqI0lry7EJaMDpr8TnPvbXEghmOU5WZKGVjjmsD4zCmHWcc1WrFBBN3tGuo48HYtAgyhieKgP6xDGJZyj3Rp4JYywWLoYQorYXZdupnQVMDY1OqPOLVqNdRJJXO75RVmvZBndSCcR1HG1iTutHbvb0zUIfX+dfSuk4pGkNUe5/jMdzo+fZ27Ae+3dvD8+3t1K9TigZe1RZgXDc6/8ck/TI3uU44cKOaOdFV2pbRDx7ny9zUOnN/7v3TC4IA+69fx2Ykn3P89ewZiqYS0J8CKGdFOe3QXQqMriGVt+5/IjC6A4REU9vkGoxNqTbwFtqVdIVdUXbTF8BIKSEVgdcs2DbgDBjdr8b8HE8BRoIJNIeUSUHjCwCUHE1GmsTvlzMLRndYudAWozvzUmRpZ9enRbYY3fxZFDkrFTnAjizwZhkpro6ZtRuSp+tZVpppBmYGZgZmOvoPMtvtfj4R/GwAAAAASUVORK5CYII=", "torch": "data:image/png;base64,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", "flag": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEYAAABGCAYAAABxLuKEAAADOUlEQVR42u3azWoTURQH8P+5Mxkb8SNvYN7AWtzrxg9oi0EbfAR3WtyKqIgLkX6oKLiye0WmWoOC4LjXOH2D+AZjwcaZ6dy/i6a1apukaao1cw6ECeEyhF/OuXPuvRG0ov6geoIWkwKWAICQSAxmRy4/+4AchgDA5/sT50jxNx0grBy78nw+dzAfn1QPmyYbyQpLy8kKyDUQYL/nwnMlskUpH7/07GueYIw0eTNObSlaTpCsWKTZ6itZsYiWE8SpLUmTN/OWMYZkZamZbjlgqZmCZCV3MN/irMw2AwjgW5yVcwcTp7bjoDi1uPGx+v56/eLR3MBYsuMgSwIiJw0Z3vhUfXqtfv7IwD+VJhfG2sqkcQYAGDpYQPGQB6dgADAC4FvB3O2RwexzuoYp7HNWr0UHQwcKMK5pTUIMCJmLQf/u8cF5pG8bZq0tLAw58Iou3I2fkwFFAgqD/z2TeoPZEI5n4BVdFIYciJGNz7MIREiRAGREg9Aia9wZefElFzC/I7meA9czv2bSlr0AQwARREIC0ba/PDEMsATBMCClfsK4/bxZllhkiUXcKjensAolAhhXYFwDZ21uWl13DLfenZSeV3qyKxnj7lou8ieUtUS2Sb/keAbGyPq1bV/hmD9/iNSCbN27Q9fhFMxvpd4B5mxdurJ7M8K+22WJRQYg/Z61TwwBXM/5q3OMgYbCKIzCKIzCKIzCKIzCKIzCaChMt6vrTqvm9Y0qOJoxeQ8CkasKCCloCBgKGdw7/eoDsJs7eHs3AoDBRoRN55gcpEQIEd9mDGbOvOz6SMcd0PLwRegbYTA1WuvpuGaAYNgQyqwx1p8aq+347Oqfbob3q0yMhT89/nqxr33M/zhnCGXOGOv3WiYDAUMiFKAhoO/ti/27p979lT8O7EWYiKAPMhRx/McTtX9y1t01jIitEGYYZAVYP1rtR0oEEAlJ2xBx/EcXanvi0L9rmJnR2jyAeQC3rr4aO0pjy6RUACl3RAUjgmELIqIxoQsbPTz/dnGvlnBPpTQ9vrAIYLEFpYtIXV1rKIzCKIzCKIzCKIzCKIzCKIzCaCiMwiiMwiiMwiiMwiiMwiiMhsIozE7iB4o8YbrZzWxFAAAAAElFTkSuQmCC", "ground": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEYAAABGCAYAAABxLuKEAAABtUlEQVR42u2bQU7DMBBFx1PHAracALHhEGxZcilOxckAlWTMggWITBo32I3H/iN1FaVSX//8/HFs9/ryHCmxbu8f6O7xSb329v5x8t6b6yuyVJwDSovFgLIRTCoUfzhsulZr+VxKCWGgQEP7iumxfVbB9A5FBQMoisf8hXI8fpLESCLyQ5KZ2DkKYegDjKaUcZpmN4gICVFTRrsIptb20RSr+kEBFfuaPUVTrFYlVMww2n/OSgCTEOUtRvysI0FrMR+tVFox5v91duTc9+d3xRgpxkgisU/FMPMMChGRc46YGa0Ej+kFzDmxIHeEqNp894wLaKUewZyaytcmdrM5JmURTSSSyLTp+82CKb2IVhyMlj5TkmfzHqOlz5TkCfMFGIDZNRXnSsBmn0qlU3FxxSwFqbWAtbsiy4PZHrLgMQADMAADMJ2V934eiCwMeaUHXVUxFoa80oMuWgkeAzAAAzAAAzAAAzC9gKl9hS1nab/Vj+PUvTq0VUa0EjwGYAAGYACmnrr4K1or+2X48mBs7JdBKwEMwABMU2Cs7JfJ9rheOiOdc1OySTBLZ6StnuyHxwDMefUFIkmqZE404SAAAAAASUVORK5CYII=", "wall": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEYAAABGCAYAAABxLuKEAAABa0lEQVR42u3bS07DMBCA4cF2bEQllj0N1+AeHIUF50KcgyVSEHFslw0CtXGsoibN65+tEyn5OjMeR+rN6/PjQYhOKAjyYd4/vlAgY4ABBhhggAEGGGCAAYY4OSs1bexdrB+eJITQvckYsc6N/nCfdf2v6+92u+FgSovWuasAUEpLKiVX6d7FduEvZ60VpbVoffyOMUZJMYr3fpsZU1nbQRER0VpLZS2lRI/ZCowxZpRrL96uJ2+eE44LlNIWYdrCdlxam30plcI3jaSUJKX09ysrJUqp3/Lz3hdnlVVmTAjhCEVEJKWUPdvNsvnmps9zJs/V95jc9HnO5EnzBQaYSafioSbgxW7XY0/Fo2dM3yDVznhHukrGXDJk0WOAAQYYYDYWBoL8QReYn4MupUSPAQYYYIABBhhggFl/5L4mciSQ/FdGMoZSAmaQMPv7297F/dsLGUOcZAz/uyZjgAEGGGCAAQYYYIABhujEN6/lXrcn0ysXAAAAAElFTkSuQmCC", "brick": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEYAAABGCAYAAABxLuKEAAABb0lEQVR42u3bUU7DMAyAYZNkqUR3Cg7CLbgJB+GBcyHOwSNqEU3TwBtoJK020WxL8/ux7aT1m+3alXbz8vTwJUQUCoJ0mLf3TxTIGGCAAQYYYIABBhhggCH+7Erd/ePsSTcM4r2PP2SM2KbJ/uU++v6k62/bdj2YpZO2ac4CQCmVVEpbvjlrrSitRWt9cHyaJgnTJM65OjNmZ22EIiKitZadtZQSPaYWGGNMlmuLb76XHBcopRphxoXH8dK5oucYNwwSQpAQwu+vrJQopX7Kzzm3OKtsMmO89wcoIiIhhORud5XNNzV9HjN5br7HpKbPYyZPmi8wwFx0Kl5rAi72cZ17Ks6eMXOD1HjFT6SzZMx/hix6DDDAAANMZWHa/T46WMKSl3vRTWZMCUte7kWXUqLHAAMMMMAAAwwwtcCMlawDc/dq+q6rPjtSbxkpJXoMMKuEuXt9RoGMOSFj+N81GQMMMMAAAwwwwAADDDBEFN99Emx66QNIrQAAAABJRU5ErkJggg=="};
const ART = {};
let artReady = false;
function loadArt(){
  const keys=Object.keys(RUN_ART_SRC); let n=0;
  for(const k of keys){
    const im=new Image();
    im.onload=()=>{ if(++n===keys.length) artReady=true; };
    im.onerror=()=>{ if(++n===keys.length) artReady=true; };
    im.src=RUN_ART_SRC[k]; ART[k]=im;
  }
}
loadArt();

const RUN = {
  on:false, state:"idle",           // "calib" | "play" | "over"
  cv:null, cx:null, W:0, H:0, dpr:1,
  lane:1, laneF:1,                  // laneF = smoothed lane for animation
  py:0, vy:0, air:false, duckT:0,
  obs:[], coins:[], pops:[],
  dist:0, speed:14, coinN:0, lives:3,
  rage:0, shake:0, t:0, last:0, spawnZ:0, coinZ:0,
  calib:null, armed:{L:true,R:true}, fire:{J:0,D:0,L:0,R:0}, lock:0,
  cal:null, best:0
};
const RUN_KEY="gymoggle_runcalib", RUN_BEST="gymoggle_runbest";
const R_RAISE_ON=0.12, R_RAISE_OFF=0.02, R_COOL=0.35, R_LOCK=0.60;
const LANE_W=1.55, FOV=260, FAR=900;

/* ---------- pose measurement (mirrors the tuned lab) ---------- */
function runMeasure(l){
  const shY=(l[11].y+l[12].y)/2, hipY=(l[23].y+l[24].y)/2, ankY=(l[27].y+l[28].y)/2;
  return { shY, torso:Math.abs(hipY-shY)||1e-3, leg:Math.abs(ankY-hipY)||1e-3,
           ankL:l[27].y, ankR:l[28].y, wrLx:l[15].x, wrRx:l[16].x };
}

/* ---------- 3-step calibration: learns YOUR jump/duck + which hand is which ---------- */
const RUN_STEPS=[
  {t:"Stand still", s:"Whole body in frame. Arms relaxed.", d:3},
  {t:"Jump!", s:"Hop a few times — both feet off the ground.", d:5},
  {t:"Duck!", s:"Bend your upper body down, a few times.", d:5},
];
function runCalibStart(){
  RUN.state="calib";
  RUN.cal={step:0, t0:performance.now()/1000, buf:[], peak:{foot:0,duck:0}, rest:null, L:15, R:16};
  runCalibUI();
}
function runCalibUI(){
  const c=RUN.cal, st=RUN_STEPS[c.step];
  const left=Math.max(0, st.d-(performance.now()/1000-c.t0));
  centerEl.innerHTML=`<div class="run-calib">
    <h3>${c.step+1}/3 · ${st.t}</h3><p>${st.s}</p>
    <div class="cbar"><i style="width:${(1-left/st.d)*100}%"></i></div>
    <small>${left.toFixed(1)}s — this teaches the game YOUR body</small></div>`;
}
function runCalibFeed(l){
  const c=RUN.cal, q=runMeasure(l), now=performance.now()/1000;
  const st=RUN_STEPS[c.step], el=now-c.t0;
  if(c.step===0){
    c.buf.push([q.torso,q.leg,q.ankL,q.ankR,q.wrLx,q.wrRx]);
    if(el>=st.d && c.buf.length>10){
      const med=i=>{const a=c.buf.map(b=>b[i]).sort((x,y)=>x-y);return a[a.length>>1];};
      c.rest={torso:med(0), leg:med(1), ankL:med(2), ankR:med(3)};
      // the frame is mirrored, so MediaPipe's left/right labels are unreliable.
      // just take whichever wrist actually sits further LEFT on screen.
      c.L = med(4)<med(5) ? 15 : 16;  c.R = c.L===15 ? 16 : 15;
      c.step=1; c.t0=now; c.buf=[];
    }
  } else if(c.step===1){
    const fL=(c.rest.ankL-q.ankL)/c.rest.leg, fR=(c.rest.ankR-q.ankR)/c.rest.leg;
    c.peak.foot=Math.max(c.peak.foot, Math.min(fL,fR));   // BOTH feet -> the lower one
    if(el>=st.d){ c.step=2; c.t0=now; }
  } else {
    c.peak.duck=Math.max(c.peak.duck, (c.rest.torso-q.torso)/c.rest.torso);
    if(el>=st.d){
      RUN.calib={ rest:c.rest, L:c.L, R:c.R,
        thr:{ foot:Math.max(0.05, c.peak.foot*0.55), duck:Math.max(0.06, c.peak.duck*0.55) } };
      try{ localStorage.setItem(RUN_KEY, JSON.stringify(RUN.calib)); }catch(e){}
      runStart();
      return;
    }
  }
  runCalibUI();
}

/* ---------- the controller: 4 inputs, that's all ---------- */
function runPose(l){
  if(RUN.state==="calib"){ runCalibFeed(l); return; }
  if(RUN.state!=="play" || !RUN.calib) return;
  const q=runMeasure(l), R=RUN.calib.rest, T=RUN.calib.thr, now=performance.now()/1000;
  const ok=(k,cool)=>{ if(now-RUN.fire[k]<cool) return false; RUN.fire[k]=now; return true; };

  // JUMP — both feet up. Jogging always keeps one foot down, so this can't false-fire.
  const fL=(R.ankL-q.ankL)/R.leg, fR=(R.ankR-q.ankR)/R.leg;
  const both = fL>T.foot && fR>T.foot;
  if(both && !RUN.air && ok("J",R_COOL)){ RUN.vy=-16.5; RUN.air=true; RUN.lock=now+R_LOCK; beep(720,0.06,"square",0.22); }

  // DUCK
  const squash=(R.torso-q.torso)/R.torso;
  const duckNow = squash>T.duck;
  if(duckNow && ok("D",R_COOL)){ RUN.duckT=0.55; RUN.lock=now+R_LOCK; beep(300,0.07,"sine",0.22); }

  // STEER — raise a hand above the shoulder. Jogging keeps hands BELOW the shoulders,
  // so arm swing can never steer you by accident. Jump/duck lock it out (arms fly up).
  const blocked = both || duckNow || RUN.air || now<RUN.lock;
  const rL=(q.shY - l[RUN.calib.L].y)/R.torso;
  const rR=(q.shY - l[RUN.calib.R].y)/R.torso;
  if(blocked){ RUN.armed.L=RUN.armed.R=false; }
  else{
    const onL=rL>R_RAISE_ON, onR=rR>R_RAISE_ON;
    if(onL && !onR && RUN.armed.L && ok("L",R_COOL)){ RUN.lane=Math.max(0,RUN.lane-1); RUN.armed.L=false; beep(520,0.05,"triangle",0.20); }
    if(onR && !onL && RUN.armed.R && ok("R",R_COOL)){ RUN.lane=Math.min(2,RUN.lane+1); RUN.armed.R=false; beep(520,0.05,"triangle",0.20); }
    if(rL<R_RAISE_OFF) RUN.armed.L=true;      // hand back down -> can steer again
    if(rR<R_RAISE_OFF) RUN.armed.R=true;
  }
}

/* ---------- game ---------- */
function runStart(){
  RUN.state="play";
  Object.assign(RUN,{lane:1,laneF:1,py:0,vy:0,air:false,duckT:0,obs:[],coins:[],pops:[],
                     dist:0,speed:14,coinN:0,lives:3,rage:0,shake:0,t:0,spawnZ:FAR,coinZ:FAR+180,
                     armed:{L:true,R:true},fire:{J:0,D:0,L:0,R:0},lock:0});
  RUN.best = +(localStorage.getItem(RUN_BEST)||0);
  centerEl.innerHTML="";
  $("stage").classList.add("runner");
  runResize();
  speak("Run!", true);
}
function runResize(){
  const cv=RUN.cv; if(!cv) return;
  const r=cv.getBoundingClientRect(); RUN.dpr=Math.min(2,window.devicePixelRatio||1);
  cv.width=r.width*RUN.dpr; cv.height=r.height*RUN.dpr;
  RUN.W=r.width; RUN.H=r.height;
  RUN.cx.setTransform(RUN.dpr,0,0,RUN.dpr,0,0);
}
// perspective: z ahead -> screen scale/pos
function proj(z){
  const s=FOV/(z+FOV);
  return {s, y: RUN.H*0.46 + (RUN.H*0.52)*s};
}
function laneX(lane, s){ return RUN.W/2 + (lane-1)*(RUN.W*0.22*LANE_W)*s; }

function runStep(dt){
  if(RUN.state!=="play") return;
  RUN.t+=dt;
  RUN.speed = 14 + Math.min(16, RUN.dist/260);      // gently ramps — never player-controlled
  RUN.dist += RUN.speed*dt*3.1;
  RUN.laneF += (RUN.lane-RUN.laneF)*Math.min(1, dt*11);
  if(RUN.shake>0) RUN.shake=Math.max(0,RUN.shake-dt*3);

  // jump arc
  if(RUN.air){ RUN.vy += 52*dt*2.4; RUN.py += RUN.vy*dt*2.4;
    if(RUN.py>=0){ RUN.py=0; RUN.vy=0; RUN.air=false; } }
  if(RUN.duckT>0) RUN.duckT-=dt;

  // spawn obstacles + coins
  const step = RUN.speed*dt*3.1;
  RUN.spawnZ -= step; RUN.coinZ -= step;
  for(const o of RUN.obs) o.z -= step;
  for(const c of RUN.coins) c.z -= step;

  if(RUN.spawnZ<=0){
    const kind = Math.random()<0.5 ? "log" : "vine";   // log=JUMP, vine=DUCK
    const lanes=[0,1,2];
    // sometimes block two lanes to force a real decision
    const blockN = RUN.dist>420 && Math.random()<0.35 ? 2 : 1;
    for(let i=0;i<blockN;i++){
      const L=lanes.splice(Math.floor(Math.random()*lanes.length),1)[0];
      RUN.obs.push({z:FAR, lane:L, kind, hit:false});
    }
    RUN.spawnZ = 210 + Math.random()*130 - Math.min(70, RUN.dist/40);
  }
  if(RUN.coinZ<=0){
    const L=Math.floor(Math.random()*3);
    for(let i=0;i<4;i++) RUN.coins.push({z:FAR+i*46, lane:L, got:false});
    RUN.coinZ = 340 + Math.random()*260;
  }

  // collisions (player sits at z≈0)
  for(const o of RUN.obs){
    if(o.hit || o.z>26 || o.z<-30) continue;
    if(Math.abs(o.lane-RUN.laneF)>0.55) continue;
    const cleared = o.kind==="log" ? (RUN.py < -16) : (RUN.duckT>0);
    o.hit=true;
    if(!cleared){
      RUN.lives--; RUN.rage=Math.min(1,(3-RUN.lives)/3); RUN.shake=1;
      beep(110,0.20,"sawtooth",0.30); speak(RUN.lives>0?"Ouch!":"", false);
      if(RUN.lives<=0) runOver();
    }
  }
  for(const c of RUN.coins){
    if(c.got || c.z>24 || c.z<-24) continue;
    if(Math.abs(c.lane-RUN.laneF)<0.6){ c.got=true; RUN.coinN++;
      RUN.pops.push({x:laneX(c.lane,proj(0).s), y:proj(0).y-60, t:0}); beep(880,0.05,"square",0.18); }
  }
  RUN.obs   = RUN.obs.filter(o=>o.z>-40);
  RUN.coins = RUN.coins.filter(c=>c.z>-40 && !c.got);
  RUN.pops  = RUN.pops.filter(p=>(p.t+=dt)<0.6);

  // the gorilla creeps closer over time; a clean run pushes it back
  RUN.rage = Math.max(0, Math.min(1, RUN.rage - dt*0.02));

  $("runDist").textContent = Math.floor(RUN.dist);
  $("runCoins").textContent = RUN.coinN;
  $("runHits").textContent = RUN.lives+" lives";
  $("runRage").style.width = ((3-RUN.lives)/3*100)+"%";
  runDraw();
}

function runDraw(){
  const c=RUN.cx, W=RUN.W, H=RUN.H; if(!c) return;
  c.save();
  if(RUN.shake>0){ const s=RUN.shake*7; c.translate((Math.random()-.5)*s,(Math.random()-.5)*s); }
  const HZ = H*0.46;                                  // horizon

  // ---------- torch-lit castle sky ----------
  const sky=c.createLinearGradient(0,0,0,HZ);
  sky.addColorStop(0,"#120d1c"); sky.addColorStop(1,"#2c2036");
  c.fillStyle=sky; c.fillRect(0,0,W,HZ);

  // ---------- castle walls receding on both sides ----------
  if(artReady && ART.wall.complete){
    const rows=16;
    for(let i=rows;i>=1;i--){
      const z=i*(FAR/rows), p=proj(z), pn=proj(z-FAR/rows);
      const w0=RUN.W*0.34*p.s, w1=RUN.W*0.34*pn.s;   // wall inner edge
      const x0=W/2-w0*2.1, x1=W/2-w1*2.1;
      const h0=200*p.s, h1=200*pn.s;
      c.globalAlpha=0.35+0.55*(1-p.s);
      // left wall slab
      c.fillStyle="#3a3550";
      c.beginPath(); c.moveTo(x0,p.y); c.lineTo(x1,pn.y); c.lineTo(x1,pn.y-h1); c.lineTo(x0,p.y-h0); c.closePath(); c.fill();
      // right wall slab (mirror)
      c.beginPath(); c.moveTo(W-x0,p.y); c.lineTo(W-x1,pn.y); c.lineTo(W-x1,pn.y-h1); c.lineTo(W-x0,p.y-h0); c.closePath(); c.fill();
    }
    c.globalAlpha=1;
    // torches along the walls (scroll toward you)
    for(let i=0;i<7;i++){
      const z=((i*150 - RUN.dist*3.1)%1050+1050)%1050;
      if(z>FAR||z<10) continue;
      const p=proj(z), sz=70*p.s*1.5;
      const off=RUN.W*0.34*p.s*2.1;
      const flick=1+Math.sin(RUN.t*13+i)*0.08;
      c.globalAlpha=Math.min(1,p.s*3.2);
      c.drawImage(ART.torch, W/2-off-sz*0.5, p.y-150*p.s, sz*flick, sz*flick);
      c.drawImage(ART.torch, W/2+off-sz*0.5, p.y-150*p.s, sz*flick, sz*flick);
      // torch glow
      const gl=c.createRadialGradient(W/2-off,p.y-130*p.s,0,W/2-off,p.y-130*p.s,90*p.s);
      gl.addColorStop(0,"rgba(255,170,60,.30)"); gl.addColorStop(1,"rgba(255,170,60,0)");
      c.fillStyle=gl; c.fillRect(W/2-off-90*p.s,p.y-220*p.s,180*p.s,180*p.s);
      const gr=c.createRadialGradient(W/2+off,p.y-130*p.s,0,W/2+off,p.y-130*p.s,90*p.s);
      gr.addColorStop(0,"rgba(255,170,60,.30)"); gr.addColorStop(1,"rgba(255,170,60,0)");
      c.fillStyle=gr; c.fillRect(W/2+off-90*p.s,p.y-220*p.s,180*p.s,180*p.s);
    }
    c.globalAlpha=1;
  }

  // ---------- stone floor, tiled in perspective ----------
  c.fillStyle="#1a1622"; c.fillRect(0,HZ,W,H-HZ);
  if(artReady && ART.ground.complete){
    const rows=22;
    for(let i=rows;i>=1;i--){
      const z=i*(FAR/rows), p=proj(z), pn=proj(Math.max(0,z-FAR/rows));
      const bandH=Math.max(1, pn.y-p.y);
      const w=RUN.W*0.30*p.s*3.4;
      c.globalAlpha=Math.min(1, 0.25+p.s*2.6);
      // scroll the texture toward the player
      const shift=((RUN.dist*3.1)%70)*p.s;
      c.drawImage(ART.ground, W/2-w/2, p.y-shift*0.2, w, bandH+2);
      c.globalAlpha=1;
    }
  }
  // lane grooves
  c.strokeStyle="rgba(0,0,0,.35)"; c.lineWidth=2;
  for(const L of [0.5,1.5]){
    c.beginPath();
    for(let z=0;z<=FAR;z+=30){ const p=proj(z), x=laneX(L,p.s); z===0?c.moveTo(x,p.y):c.lineTo(x,p.y); }
    c.stroke();
  }

  // ---------- the beast, closing in behind you ----------
  const gp=proj(130 - RUN.rage*105), gs=gp.s*(1.5+RUN.rage*1.6);
  c.globalAlpha=0.4+RUN.rage*0.6;
  drawBeast(c, W/2 + (RUN.laneF-1)*14, gp.y, gs*130, RUN.t, RUN.rage);
  c.globalAlpha=1;

  // ---------- obstacles + coins, far to near ----------
  const items=[...RUN.obs.map(o=>({...o,type:"o"})), ...RUN.coins.map(o=>({...o,type:"c"}))]
              .sort((a,b)=>b.z-a.z);
  for(const it of items){
    if(it.z<-30||it.z>FAR) continue;
    const p=proj(it.z), x=laneX(it.lane,p.s);
    const shade=Math.min(1, 0.30+p.s*2.4);
    c.globalAlpha=shade;
    if(it.type==="o"){
      const w=RUN.W*0.19*p.s;
      if(it.kind==="log"){                                // CRATE -> JUMP over it
        const img = (it.lane%2 ? ART.crate : ART.crate2);
        if(artReady && img.complete) c.drawImage(img, x-w/2, p.y-w, w, w);
        else { c.fillStyle="#8a6238"; c.fillRect(x-w/2,p.y-w,w,w); }
      } else {                                            // PORTCULLIS -> DUCK under it
        const img = ART.gate;
        const gw=w*1.25, gh=w*1.05;
        if(artReady && img.complete) c.drawImage(img, x-gw/2, p.y-165*p.s, gw, gh);
        else { c.fillStyle="#77839a"; c.fillRect(x-gw/2,p.y-165*p.s,gw,gh); }
        // spikes on the bottom edge so it reads as "duck!"
        c.fillStyle="#9aa7bd";
        for(let i=0;i<5;i++){
          const sx=x-gw/2+gw*(i+.5)/5, sy=p.y-165*p.s+gh;
          c.beginPath(); c.moveTo(sx-4*p.s,sy); c.lineTo(sx+4*p.s,sy); c.lineTo(sx,sy+11*p.s); c.closePath(); c.fill();
        }
      }
    } else {                                              // COIN
      const r=12*p.s, cy=p.y-48*p.s - Math.sin(RUN.t*6+it.z*0.05)*5*p.s;
      const spin=Math.abs(Math.cos(RUN.t*5+it.z*0.04));
      c.fillStyle="#ffd23f"; c.strokeStyle="#a9761b"; c.lineWidth=2.4*p.s;
      c.beginPath(); c.ellipse(x,cy, r*(0.35+0.65*spin), r, 0,0,7); c.fill(); c.stroke();
      c.fillStyle="rgba(255,255,255,.65)";
      c.beginPath(); c.ellipse(x-r*0.25*spin, cy-r*0.3, r*0.16*spin+0.6, r*0.30, 0,0,7); c.fill();
    }
    c.globalAlpha=1;
  }

  // ---------- the knight (back view) ----------
  const p0=proj(0), px=laneX(RUN.laneF,p0.s), py=p0.y + RUN.py*p0.s*3.2;
  drawKnight(c, px, py, 112*p0.s, RUN.t, RUN.duckT>0, RUN.air);

  // coin pops
  for(const pop of RUN.pops){
    c.globalAlpha=1-pop.t/0.6; c.fillStyle="#ffd23f";
    c.font="bold 20px 'JetBrains Mono'"; c.textAlign="center";
    c.fillText("+1", pop.x, pop.y - pop.t*46);
  }
  c.globalAlpha=1;
  // dungeon vignette
  const v=c.createRadialGradient(W/2,H*0.6,H*0.22,W/2,H*0.6,H*0.85);
  v.addColorStop(0,"rgba(0,0,0,0)"); v.addColorStop(1,"rgba(0,0,0,.68)");
  c.fillStyle=v; c.fillRect(0,0,W,H);
  c.restore();
}

/* Back-view knight — you see their back as they flee down the corridor.
   Free sprite packs are all side-view, which reads wrong from behind, so this
   is drawn to the camera angle the game actually uses. */
function drawKnight(c,x,y,h,t,duck,air){
  const s=h/112, bob=air?0:Math.sin(t*15)*2.2*s;
  const torsoH=(duck?36:58)*s;
  c.save(); c.translate(x,y+bob);
  // shadow
  c.fillStyle="rgba(0,0,0,.45)";
  c.beginPath(); c.ellipse(0,2*s,20*s,5.5*s,0,0,7); c.fill();
  const sw=air?0.65:Math.sin(t*15);
  // legs
  if(!duck){
    c.strokeStyle="#4a4258"; c.lineWidth=7*s; c.lineCap="round";
    c.beginPath(); c.moveTo(-5*s,-4*s); c.lineTo(-5*s+sw*10*s, 15*s); c.stroke();
    c.beginPath(); c.moveTo( 5*s,-4*s); c.lineTo( 5*s-sw*10*s, 15*s); c.stroke();
  }
  // cape (flaps as you run)
  c.fillStyle="#b8203f";
  c.beginPath();
  c.moveTo(-12*s,-torsoH+6*s);
  c.quadraticCurveTo(-16*s+sw*4*s, -torsoH*0.35, -9*s+sw*5*s, 4*s);
  c.lineTo(9*s+sw*5*s, 4*s);
  c.quadraticCurveTo(16*s+sw*4*s, -torsoH*0.35, 12*s,-torsoH+6*s);
  c.closePath(); c.fill();
  // armour torso
  c.fillStyle="#8f96a8";
  c.beginPath(); c.roundRect(-11*s,-torsoH, 22*s, torsoH, 6*s); c.fill();
  c.fillStyle="#6f7686";
  c.fillRect(-11*s,-torsoH*0.55, 22*s, 3*s);
  // arms pumping
  c.strokeStyle="#8f96a8"; c.lineWidth=6*s; c.lineCap="round";
  c.beginPath(); c.moveTo(-10*s,-torsoH+13*s); c.lineTo(-15*s-sw*7*s,-torsoH+30*s); c.stroke();
  c.beginPath(); c.moveTo( 10*s,-torsoH+13*s); c.lineTo( 15*s+sw*7*s,-torsoH+30*s); c.stroke();
  // helm (back of head)
  c.fillStyle="#a7aebd";
  c.beginPath(); c.arc(0,-torsoH-11*s, 12*s, 0, 7); c.fill();
  c.fillStyle="#8f96a8";
  c.fillRect(-12*s,-torsoH-12*s, 24*s, 4*s);
  // plume
  c.fillStyle="#ffd23f";
  c.beginPath(); c.ellipse(0,-torsoH-23*s, 4*s, 8*s, 0,0,7); c.fill();
  c.restore();
}

/* The thing chasing you. */
function drawBeast(c,x,y,h,t,rage){
  const s=h/130, sway=Math.sin(t*8)*4*s, lunge=Math.abs(Math.sin(t*8))*3*s;
  c.save(); c.translate(x+sway,y+lunge);
  // hulking body
  c.fillStyle="#1c1526";
  c.beginPath(); c.ellipse(0,-44*s,34*s,36*s,0,0,7); c.fill();
  c.beginPath(); c.ellipse(-38*s,-42*s,11*s,29*s,0,0,7); c.fill();
  c.beginPath(); c.ellipse( 38*s,-42*s,11*s,29*s,0,0,7); c.fill();
  c.beginPath(); c.ellipse(0,-92*s,25*s,22*s,0,0,7); c.fill();
  // horns
  c.fillStyle="#2a2036";
  c.beginPath(); c.moveTo(-20*s,-104*s); c.lineTo(-30*s,-124*s); c.lineTo(-12*s,-110*s); c.closePath(); c.fill();
  c.beginPath(); c.moveTo( 20*s,-104*s); c.lineTo( 30*s,-124*s); c.lineTo( 12*s,-110*s); c.closePath(); c.fill();
  // burning eyes — brighter the angrier it is
  const glow=0.55+rage*0.45;
  c.fillStyle=`rgba(255,${90-rage*60},${40},${glow})`;
  c.beginPath(); c.ellipse(-8*s,-95*s,5*s,4*s,0,0,7); c.fill();
  c.beginPath(); c.ellipse( 8*s,-95*s,5*s,4*s,0,0,7); c.fill();
  const eg=c.createRadialGradient(0,-95*s,0,0,-95*s,34*s);
  eg.addColorStop(0,`rgba(255,60,30,${0.30*glow})`); eg.addColorStop(1,"rgba(255,60,30,0)");
  c.fillStyle=eg; c.fillRect(-40*s,-130*s,80*s,70*s);
  // teeth
  c.fillStyle="#e8e2d8";
  for(let i=0;i<5;i++){
    const tx=-14*s+i*7*s;
    c.beginPath(); c.moveTo(tx,-80*s); c.lineTo(tx+5*s,-80*s); c.lineTo(tx+2.5*s,-71*s); c.closePath(); c.fill();
  }
  c.restore();
}

function runOver(){
  RUN.state="over";
  const d=Math.floor(RUN.dist);
  if(d>RUN.best){ RUN.best=d; try{ localStorage.setItem(RUN_BEST,d); }catch(e){} }
  whistle(); speak("Caught! The gorilla got you.", true);
  centerEl.innerHTML=`<div class="run-calib">
    <h3>🦍 Caught!</h3>
    <p><b>${d} m</b> · 🪙 ${RUN.coinN} coins<br><small>Best: ${RUN.best} m</small></p>
    <button class="btn primary" id="runAgain">Run again</button>
    <button class="btn ghost" id="runExit" style="margin-top:8px">Exit</button></div>`;
  $("runAgain").addEventListener("click", runStart);
  $("runExit").addEventListener("click", runQuit);
}
function runQuit(){
  RUN.on=false; RUN.state="idle"; busy=false;
  $("stage").classList.remove("runner");
  centerEl.innerHTML="";
  show("landing");
}
async function startRunner(){
  if(busy) return; busy=true; initAudio();
  try{
    if(!landmarker) await initModel();
    await initCamera();
  }catch(e){ busy=false;
    toast(e.name==="NotAllowedError"?"Camera blocked — allow access and try again.":"Couldn't start camera.");
    return; }
  RUN.on=true;
  RUN.cv=$("runCanvas"); RUN.cx=RUN.cv.getContext("2d");
  showPresence(false);
  show("game");
  if(!looping){ looping=true; loop(); }
  setStatus("");
  let saved=null;
  try{ saved=JSON.parse(localStorage.getItem(RUN_KEY)||"null"); }catch(e){}
  if(saved && saved.rest && saved.thr){ RUN.calib=saved; runStart(); }
  else { $("stage").classList.remove("runner"); runCalibStart(); }
  RUN.last=performance.now();
}
$("runBtn").addEventListener("click", startRunner);
$("runQuit").addEventListener("click", runQuit);
window.addEventListener("resize", ()=>{ if(RUN.on) runResize(); });

document.querySelectorAll(".btab").forEach(b=> b.addEventListener("click",()=>{
  document.querySelectorAll(".btab").forEach(x=>x.classList.remove("on")); b.classList.add("on");
  boardTab=b.dataset.tab; renderBoard();
}));
document.querySelectorAll(".bex").forEach(b=> b.addEventListener("click",()=>{
  document.querySelectorAll(".bex").forEach(x=>x.classList.remove("on")); b.classList.add("on");
  boardEx=b.dataset.bex; renderBoard();
}));