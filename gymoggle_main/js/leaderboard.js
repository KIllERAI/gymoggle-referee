/* GymOggle — leaderboard
   Part of the GymOggle app. Loaded as a classic script; modules share globals. */

/* ---------- leaderboard ---------- */
let boardData = null, boardTab = "scores", boardEx = "squats", myStats = null;

async function openBoard(){
  show("board");
  $("boardList").innerHTML = `<div class="lb-empty">Loading…</div>`;
  try{
    const res = await fetch(HTTP_BASE + "/leaderboard");
    boardData = await res.json();
    if(!boardData.ok) throw new Error(boardData.error||"failed");
    renderBoard();
  }catch(e){
    $("boardList").innerHTML = `<div class="lb-empty">Couldn't load the leaderboard.<br>(The server may be waking up — try again in a moment.)</div>`;
  }
}

async function fetchMyStats(){
  try{
    const r = await fetch(HTTP_BASE + "/me/stats", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({ token: window.PTOKEN })
    });
    const j = await r.json();
    myStats = j.ok ? j.stats : null;
  }catch(e){ myStats = null; }
}

async function renderBoard(){
  const isMe = boardTab==="me";
  $("exFilter").classList.toggle("hide", boardTab!=="scores");

  if(isMe){
    $("boardList").innerHTML = `<div class="lb-empty">Loading your stats…</div>`;
    await fetchMyStats();
    if(!myStats){ $("boardList").innerHTML = `<div class="lb-empty">Play a match to start building your stats!</div>`; return; }
    const s = myStats, played = s.total_matches||0;
    const winRate = played ? Math.round(s.wins/played*100) : 0;
    $("boardList").innerHTML = `
      <div class="stats-hero">
        <div class="stats-name">${(s.name||"You").replace(/[<>&]/g,"")}</div>
        <div class="stats-coins">🪙 ${s.coins||0}</div>
      </div>
      <div class="stats-grid">
        <div class="stat-box"><b>${s.wins||0}</b><span>Wins</span></div>
        <div class="stat-box"><b>${s.losses||0}</b><span>Losses</span></div>
        <div class="stat-box"><b>${played}</b><span>Matches</span></div>
        <div class="stat-box"><b>${winRate}%</b><span>Win rate</span></div>
        <div class="stat-box"><b>${s.current_streak||0}</b><span>Streak</span></div>
        <div class="stat-box"><b>${s.best_streak||0}</b><span>Best streak</span></div>
      </div>
      <div class="stats-sub">Lifetime reps</div>
      <div class="stats-grid">
        <div class="stat-box"><b>${s.total?.squats||0}</b><span>🦵 Squats</span></div>
        <div class="stat-box"><b>${s.total?.pushups||0}</b><span>💪 Push-ups</span></div>
        <div class="stat-box"><b>${s.total?.jacks||0}</b><span>⭐ Jacks</span></div>
        <div class="stat-box"><b>${s.total?.plank||0}s</b><span>🧱 Plank</span></div>
      </div>
      <div class="stats-sub">Personal bests</div>
      <div class="stats-grid">
        <div class="stat-box"><b>${s.best?.squats||0}</b><span>🦵 Squats</span></div>
        <div class="stat-box"><b>${s.best?.pushups||0}</b><span>💪 Push-ups</span></div>
        <div class="stat-box"><b>${s.best?.jacks||0}</b><span>⭐ Jacks</span></div>
        <div class="stat-box"><b>${s.best?.plank||0}s</b><span>🧱 Plank</span></div>
      </div>`;
    return;
  }

  const rows = boardTab==="scores"
    ? (boardData.scores?.[boardEx] || [])
    : (boardData.wins || []);
  if(!rows.length){ $("boardList").innerHTML = `<div class="lb-empty">No scores yet — be the first!</div>`; return; }
  $("boardList").innerHTML = rows.map((r,i)=>{
    const rank=i+1, cls = rank<=3 ? " rank"+rank : "";
    const name = (r.name||"Player").replace(/[<>&]/g,"");
    return `<div class="lb-row${cls}"><span class="lb-rank">${rank}</span>`+
           `<span class="lb-name">${name}</span><span class="lb-val">${r.value}</span></div>`;
  }).join("");
}
$("boardBtn").addEventListener("click", openBoard);
$("boardBack").addEventListener("click", ()=> show("landing"));

/* tab switch: Top Scores / Most Wins */
document.querySelectorAll(".board-tabs .btab").forEach(b=>{
  b.addEventListener("click", ()=>{
    document.querySelectorAll(".board-tabs .btab").forEach(x=>x.classList.remove("on"));
    b.classList.add("on");
    boardTab = b.dataset.tab;
    if(boardData) renderBoard(); else openBoard();
  });
});
/* exercise filter: Squats / Push-ups / Jacks / Plank */
document.querySelectorAll("#exFilter .bex").forEach(b=>{
  b.addEventListener("click", ()=>{
    document.querySelectorAll("#exFilter .bex").forEach(x=>x.classList.remove("on"));
    b.classList.add("on");
    boardEx = b.dataset.bex;
    if(boardData) renderBoard(); else openBoard();
  });
});