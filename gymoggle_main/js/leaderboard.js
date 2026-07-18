/* GymOggle — leaderboard
   Part of the GymOggle app. Loaded as a classic script; modules share globals. */

/* ---------- leaderboard ---------- */
let boardData = null, boardTab = "scores", boardEx = "squats";

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
function renderBoard(){
  $("exFilter").classList.toggle("hide", boardTab!=="scores");
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