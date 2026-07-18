/* GymOggle — AUTH (Google login via Supabase)
   Establishes the user's identity BEFORE the app runs. On success it sets:
     window.PID    = the Supabase user id (stable across devices)
     window.PNAME  = chosen username
     window.PCOLOR = chosen avatar colour
     window.PTOKEN = the JWT (sent to the server so it can VERIFY the user)
   The rest of the app keeps using PID / S.name exactly as before. */

const SUPA_URL  = "https://klufzqcavryvmfbjblug.supabase.co";
const SUPA_ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtsdWZ6cWNhdnJ5dm1mYmpibHVnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM1ODM4MTksImV4cCI6MjA5OTE1OTgxOX0.hdP4W1DWX7AzBe3kP4BeFFGeq43Hy2QQaHZjYE-CF3g";     // <-- anon PUBLIC key (safe in browser). Replaced at deploy.
const AVATAR_COLORS = ["#22e0d6","#ff2e7e","#ffd23f","#7cf16a","#a78bfa","#ff9f43","#4dd0e1","#f06292"];

let sb = null;                        // supabase client
let AUTH_USER = null;                 // { id, email }

/* load the supabase-js library, then boot */
function authBoot(){
  const s = document.createElement("script");
  s.src = "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2";
  s.onload = authInit;
  s.onerror = ()=> authFatal("Couldn't load login library. Check your connection.");
  document.head.appendChild(s);
}

async function authInit(){
  try{
    sb = supabase.createClient(SUPA_URL, SUPA_ANON, {
      auth:{ persistSession:true, autoRefreshToken:true, detectSessionInUrl:true }
    });
  }catch(e){ return authFatal("Login init failed."); }

  // returning from a Google redirect? this picks up the session.
  const { data:{ session } } = await sb.auth.getSession();
  if(session){ await onSignedIn(session); }
  else { showAuthScreen(); }

  sb.auth.onAuthStateChange((_e, sess)=>{ if(sess && !AUTH_USER) onSignedIn(sess); });
}

async function onSignedIn(session){
  AUTH_USER = { id: session.user.id, email: session.user.email };
  window.PTOKEN = session.access_token;         // JWT for the server to verify
  // fetch (or create) this user's GymOggle profile
  let prof = null;
  try{
    const r = await fetch(HTTP_BASE + "/me", {
      method:"POST", headers:{ "Content-Type":"application/json" },
      body: JSON.stringify({ token: window.PTOKEN })
    });
    prof = await r.json();
  }catch(e){}

  if(prof && prof.ok && prof.profile && prof.profile.name){
    applyProfile(prof.profile);
    maybePrimer();               // existing player -> primer if not seen, else straight in
  }else{
    showSetupScreen();           // new player -> setup, then primer
  }
}

function applyProfile(p){
  window.PID = AUTH_USER.id;
  window.PNAME = p.name;
  window.PCOLOR = p.color || AVATAR_COLORS[0];
  if(typeof S!=="undefined"){ S.name = p.name; }
}

/* ---------- screens ---------- */
function showAuthScreen(){
  const el = $("authScreen"); if(!el) return;
  el.style.display = "flex";
  el.innerHTML = `
    <div class="auth-card">
      <div class="auth-logo">GYMOGGLE</div>
      <p class="auth-tag">Battle a friend · Most reps wins</p>
      <button class="auth-google" id="authGoogleBtn">
        <svg viewBox="0 0 24 24" width="20" height="20"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84A11 11 0 0 0 12 23z"/><path fill="#FBBC05" d="M5.84 14.1a6.6 6.6 0 0 1 0-4.2V7.06H2.18a11 11 0 0 0 0 9.88l3.66-2.84z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84C6.71 7.31 9.14 5.38 12 5.38z"/></svg>
      Sign in with Google</button>
      <p class="auth-fine">Camera stays on your device. We store only your username, score, and email.</p>
    </div>`;
  $("authGoogleBtn").addEventListener("click", async ()=>{
    $("authGoogleBtn").disabled = true; $("authGoogleBtn").textContent = "Opening Google…";
    const { error } = await sb.auth.signInWithOAuth({
      provider:"google",
      options:{ redirectTo: location.origin + location.pathname }
    });
    if(error) authFatal("Sign-in failed: " + error.message);
  });
}

function showSetupScreen(){
  const el = $("authScreen"); if(!el) return;
  el.style.display = "flex";
  let color = AVATAR_COLORS[0];
  el.innerHTML = `
    <div class="auth-card">
      <div class="auth-logo small">Welcome!</div>
      <p class="auth-tag">Pick a name and a colour</p>
      <input id="setupName" class="auth-input" maxlength="16" placeholder="Username" autocomplete="off"/>
      <div class="auth-colors" id="setupColors">
        ${AVATAR_COLORS.map((c,i)=>`<button class="auth-swatch${i===0?' on':''}" data-c="${c}" style="background:${c}"></button>`).join("")}
      </div>
      <button class="btn primary wide" id="setupGo">Start</button>
      <p class="auth-err" id="setupErr"></p>
    </div>`;
  $("setupColors").addEventListener("click", e=>{
    const b=e.target.closest(".auth-swatch"); if(!b) return;
    [...e.currentTarget.children].forEach(x=>x.classList.remove("on"));
    b.classList.add("on"); color=b.dataset.c;
  });
  $("setupGo").addEventListener("click", async ()=>{
    const name = ($("setupName").value||"").trim();
    if(name.length < 2){ $("setupErr").textContent="Pick a name (2+ characters)"; return; }
    $("setupGo").disabled=true; $("setupGo").textContent="Creating…";
    try{
      const r = await fetch(HTTP_BASE + "/me/create", {
        method:"POST", headers:{ "Content-Type":"application/json" },
        body: JSON.stringify({ token: window.PTOKEN, name, color })
      });
      const res = await r.json();
      if(res.ok){ applyProfile(res.profile); maybePrimer(); }
      else { $("setupErr").textContent = res.error==="name_taken" ? "That name's taken — try another." : "Something went wrong."; $("setupGo").disabled=false; $("setupGo").textContent="Start"; }
    }catch(e){ $("setupErr").textContent="Network error — try again."; $("setupGo").disabled=false; $("setupGo").textContent="Start"; }
  });
}

function maybePrimer(){
  let seen=false;
  try{ seen = localStorage.getItem("gymoggle_primer")==="1"; }catch(e){}
  if(seen){ startApp(); return; }
  showPrimer();
}
function showPrimer(){
  const el=$("authScreen"); if(!el){ startApp(); return; }
  el.style.display="flex";
  el.innerHTML=`
    <div class="auth-card">
      <div class="auth-logo small">📸 Camera time</div>
      <p class="auth-tag">GymOggle counts your reps with your camera</p>
      <div class="primer-points">
        <div><span>🔒</span> Your camera <b>never leaves your device</b> — we only send your rep count.</div>
        <div><span>🧍</span> Stand back so your <b>whole body</b> fits in frame.</div>
        <div><span>💡</span> Good lighting = better counting.</div>
      </div>
      <button class="btn primary wide" id="primerAllow">Allow camera & play</button>
      <button class="btn ghost wide" id="primerLater">Maybe later</button>
      <p class="auth-err" id="primerErr"></p>
    </div>`;
  $("primerAllow").addEventListener("click", async ()=>{
    $("primerAllow").disabled=true; $("primerAllow").textContent="Requesting…";
    try{
      const stream = await navigator.mediaDevices.getUserMedia({ video:{ facingMode:"user" }, audio:false });
      stream.getTracks().forEach(t=>t.stop());   // just priming the permission; real start happens in-game
      try{ localStorage.setItem("gymoggle_primer","1"); }catch(e){}
      startApp();
    }catch(e){
      $("primerErr").textContent = "Camera blocked. You can enable it in your browser's site settings, then reload.";
      $("primerAllow").disabled=false; $("primerAllow").textContent="Allow camera & play";
    }
  });
  $("primerLater").addEventListener("click", ()=>{
    try{ localStorage.setItem("gymoggle_primer","1"); }catch(e){}
    startApp();   // they can still grant it when a match starts
  });
}

function startApp(){
  const el = $("authScreen"); if(el) el.style.display="none";
  document.body.classList.add("authed");
  if(typeof onAuthReady==="function") onAuthReady();   // let the app finish booting
}

function authFatal(msg){
  const el = $("authScreen"); if(!el){ alert(msg); return; }
  el.style.display="flex";
  el.innerHTML = `<div class="auth-card"><div class="auth-logo small">Hmm.</div>
    <p class="auth-tag">${msg}</p>
    <button class="btn primary wide" onclick="location.reload()">Retry</button></div>`;
}

async function authSignOut(){
  try{ await sb.auth.signOut(); }catch(e){}
  location.reload();
}

authBoot();