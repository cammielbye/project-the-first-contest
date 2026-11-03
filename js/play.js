// Play a contest against the computer, on the third-pass rules engine (js/game/rules.js).
import * as R from "./game/rules.js";
import { makeAI } from "./game/ai.js";
import { renderFace, setFaceArt } from "./cards.js";

const ME = 0, AI = 1;
const $ = (id) => document.getElementById(id);
const esc = (t) => String(t ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const el = (tag, cls, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html !== undefined) e.innerHTML = html; return e; };

let cardsJson, binders, byId;
let s = null;                 // the contest
let sel = null;               // { id, face, moves, picks, options }
let busy = false;             // the computer is thinking
let lastTs = 0;               // newest instance after the computer's last play, for the highlight
let choice = { mine: 0, theirs: 1 };
const ai = makeAI({});

// ------------------------------------------------------------------ boot
async function boot() {
  const get = (u) => fetch(u, { cache: "no-cache" }).then((r) => r.json());
  const [cj, bj, fj] = await Promise.all([get("data/cards.json"), get("data/binders.json"), get("data/card-faces.json").catch(() => null)]);
  cardsJson = cj; binders = bj.binders;
  byId = new Map(cj.cards.map((c) => [c.id, c]));
  R.loadCards(cj);
  setFaceArt(fj?.faces);
  $("btnNew").onclick = () => showStart();
  $("btnRules").onclick = () => showRules();
  $("btnVoids").onclick = () => showVoids();
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && sel) { sel = null; render(); }
    if (!s || !$("overlay").hidden) return;
    if (e.key === "ArrowRight") flipTo(page + 1);
    if (e.key === "ArrowLeft") flipTo(page - 1);
  });
  let rt = null;
  window.addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(() => s && binder(), 120); });
  showStart();
}

// ------------------------------------------------------------------ symbols
const SYM = {
  1: { color: "#D0663F", d: "M12 3.5 L20.5 19 H3.5 Z" },
  2: { color: "#7FA7B5", d: "M3.5 5 H20.5 L12 20.5 Z" },
  4: { color: "#D5D8CC", d: "M12 3.5 L20.5 19 H3.5 Z M3 12.5 H21" },
  8: { color: "#A88F6B", d: "M3.5 5 H20.5 L12 20.5 Z M3 11.5 H21" },
};
function chip(mask, size = 15) {
  const bits = [1, 2, 4, 8].filter((b) => mask & b);
  if (mask === 15) return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="#C2C5B8" stroke-width="2"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="2"/></svg>`;
  return bits.map((b) => `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${SYM[b].color}" stroke-width="2.2" stroke-linejoin="round"><path d="${SYM[b].d}"/></svg>`).join(bits.length > 1 ? "<span style='color:#888;font-size:10px'>/</span>" : "");
}
const elCounts = (ids) => {
  const t = [0, 0, 0, 0];
  for (const id of ids) { const d = R.C[id]; if (!d || !d.aff) continue; for (const m of d.aff) [1, 2, 4, 8].forEach((b, k) => { if (m & b && m !== 15) t[k] += POP1(m) > 1 ? 0.5 : 1; }); }
  return t;
};
const POP1 = (m) => [1, 2, 4, 8].filter((b) => m & b).length;

// ------------------------------------------------------------------ cards
function face(id, faceName, extra = {}) {
  const c = byId.get(id);
  const f = c.meta ? "meta" : faceName === "force" ? "force" : "permanence";
  const node = renderFace(c, f, { size: extra.size || "token" });
  node.dataset.card = id;
  node.dataset.face = f;
  node.addEventListener("mouseenter", () => preview(id, f));
  return node;
}
let hover = null; // { id, face } the card being looked at closely, on the binder's inside page
function preview(id, f) {
  if (sel && !sel.face) return; // the chosen card stays on the page until a face is picked
  hover = { id, face: f };
  insidePage();
}

// ------------------------------------------------------------------ start, rules, voids
function binderCard(k, on, which) {
  const b = binders[k];
  const t = elCounts(b.cards);
  const d = el("div", "binderpick" + (on ? " on" : ""));
  d.innerHTML = `<b>${esc(b.name.replace(/^Binder \w, /, ""))}</b><small>${esc(b.note || "")}</small><div class="els">fire ${t[0]} · water ${t[1]} · air ${t[2]} · earth ${t[3]}</div>`;
  d.onclick = () => { choice[which] = k; showStart(); };
  return d;
}
function showStart() {
  const o = $("overlay"); o.hidden = false; o.innerHTML = "";
  const dlg = el("div", "dialog");
  dlg.innerHTML = `<h2>Play a contest against the computer</h2><p>Third-pass cards, best of three rounds, 10 cards a round. Make a world worth 3 world points and you win the contest on the spot (the Nov 2 test rule). Pick your binder and the computer's.</p>`;
  dlg.append(el("h3", "", "Your binder"));
  const r1 = el("div", "row"); binders.forEach((_, k) => r1.append(binderCard(k, choice.mine === k, "mine"))); dlg.append(r1);
  dlg.append(el("h3", "", "The computer's binder"));
  const r2 = el("div", "row"); binders.forEach((_, k) => r2.append(binderCard(k, choice.theirs === k, "theirs"))); dlg.append(r2);
  const act = el("div", "actions");
  const go = el("button", "primary", "Start the contest"); go.onclick = () => startContest();
  const rules = el("button", "", "How to play"); rules.onclick = () => showRules(true);
  act.append(rules, go); dlg.append(act);
  o.append(dlg);
}
function showRules(back) {
  const o = $("overlay"); o.hidden = false; o.innerHTML = "";
  const dlg = el("div", "dialog");
  dlg.innerHTML = `<h2>How to play</h2>
  <ul>
    <li>Take turns playing one card from your binder, either face. A <b>permanence</b> goes into one of your worlds (or starts a new one). A <b>force</b> happens once, or lasts the round. Meta cards have one face.</li>
    <li>A world holds up to four permanences in a 2×2. A card joins next to one already there (sides, not corners).</li>
    <li>Each world scores a <b>world point</b> for every complete set of fire, water, air and earth in it. An either-or capsule counts as one of its two elements; a wildcard as any.</li>
    <li>Most world points wins the round. A tie goes to whoever has the most of any one element across all their permanences. A drawn round counts for both players.</li>
    <li><b>Pass</b> when you're done: you're out for the rest of the round. The round ends when both players have passed. You can play 10 cards a round.</li>
    <li>At round end, cards go to their owner's void, except those that return to the binder. Win two rounds to win the contest.</li>
    <li><b>Test rule (Nov 2):</b> a world worth 3 world points wins the contest at once.</li>
  </ul>
  <h3>Playing a card</h3>
  <ul>
    <li>Your binder is on the right. Turn its leaves with ‹ ›, the tabs on its edge, or the arrow keys. Cards you've played leave an empty sleeve that says where they went.</li>
    <li>Click a card in your binder. If both faces can be played, choose one on the binder's inside page. Then click the highlighted spots, cards or worlds, or use the buttons under the table. <b>Esc</b> or <b>Cancel</b> backs out.</li>
    <li>Hover any card to see both faces on the binder's inside page. The symbols under a card on the table are its affinities <i>right now</i>, after every effect; an outline means they've changed.</li>
  </ul>
  <h3>How the computer reads open rules</h3>
  <ul>
    <li>"With one affinity" means one ring printed on the card (an either-or capsule counts as one).</li>
    <li>"Return" isn't "remove", so "can't be removed" doesn't stop it.</li>
    <li>Moving goes to another existing world of the card's owner; "becomes its own world" starts a new one. Splits cut a world down the middle.</li>
    <li>Hurricane scatters every world of the chosen player into worlds of one. Echo's card doesn't count toward the 10.</li>
    <li>Ice Sheet blanks every fire permanence, both players'. A force has its card's elements; a wildcard gives none.</li>
  </ul>`;
  const act = el("div", "actions"); const ok = el("button", "primary", back ? "Back" : "Close");
  ok.onclick = () => (back ? showStart() : ((o.hidden = true), render()));
  act.append(ok); dlg.append(act); o.append(dlg);
}
function showVoids() {
  if (!s) return;
  const o = $("overlay"); o.hidden = false; o.innerHTML = "";
  const dlg = el("div", "dialog");
  dlg.innerHTML = `<h2>Voids</h2>`;
  for (const P of [ME, AI]) {
    dlg.append(el("h3", "", `${P === ME ? "Your" : "The computer's"} void (${s.p[P].void.length})`));
    const g = el("div", "voidgrid");
    for (const id of s.p[P].void) g.append(face(id, "permanence"));
    dlg.append(g);
  }
  const act = el("div", "actions"); const ok = el("button", "primary", "Close"); ok.onclick = () => { o.hidden = true; };
  act.append(ok); dlg.append(act); o.append(dlg);
}

// ------------------------------------------------------------------ contest flow
function startContest() {
  $("overlay").hidden = true;
  const bm = binders[choice.mine], bt = binders[choice.theirs];
  s = R.newContest(bm.cards, bt.cards, Math.random() < 0.5 ? ME : AI, ["You", "Computer"]);
  s.binderNames = [bm.name.replace(/^Binder \w, /, ""), bt.name.replace(/^Binder \w, /, "")];
  s.order = [bm.cards.slice(), bt.cards.slice()]; // pockets keep their cards' places all contest
  page = 0; hover = null;
  sel = null; lastTs = 0;
  s.log.push({ r: 1, P: null, text: `Round 1. ${s.opener === ME ? "You open." : "The computer opens."}` });
  R.advance(s);
  render(); step();
}
function step() {
  if (!s) return;
  if (s.phase === "roundOver") return showRoundOver();
  if (s.phase === "contestOver") return showContestOver();
  if (s.turn === AI && !busy) {
    busy = true; render();
    setTimeout(() => {
      const before = s.ts;
      const m = ai.choose(s, AI);
      if (m) R.play(s, AI, m); else R.pass(s, AI);
      lastTs = before;
      busy = false; render(); step();
    }, 650);
  }
}
function showRoundOver() {
  const rec = s.rounds[s.rounds.length - 1];
  const o = $("overlay"); o.hidden = false; o.innerHTML = "";
  const dlg = el("div", "dialog");
  const head = rec.winner === null ? "Round " + rec.r + " is a draw" : rec.winner === ME ? `You win round ${rec.r}` : `The computer wins round ${rec.r}`;
  dlg.innerHTML = `<h2>${head}</h2><p>Decided by ${esc(rec.why)}. Rounds won: you ${s.p[ME].wins}, the computer ${s.p[AI].wins}.</p>
  <table><tr><th></th><th>World points</th><th>Tie-break</th><th>Worlds</th></tr>
  ${[ME, AI].map((P) => `<tr><td>${P === ME ? "You" : "Computer"}</td><td>${rec.score[P].pts}</td><td>${rec.score[P].tie}</td><td>${rec.score[P].worlds.map((w) => `${w.cards} card${w.cards > 1 ? "s" : ""}: ${w.k}`).join(" · ") || "none"}</td></tr>`).join("")}</table>`;
  const act = el("div", "actions"); const ok = el("button", "primary", "Next round");
  ok.onclick = () => { o.hidden = true; R.nextRound(s); s.log.push({ r: s.r, P: null, text: `Round ${s.r}. ${s.opener === ME ? "You open." : "The computer opens."}` }); R.advance(s); render(); step(); };
  act.append(ok); dlg.append(act); o.append(dlg);
}
function showContestOver() {
  render();
  const o = $("overlay"); o.hidden = false; o.innerHTML = "";
  const dlg = el("div", "dialog");
  const head = s.winner === null ? "The contest is a draw" : s.winner === ME ? "You win the contest" : "The computer wins the contest";
  const why = s.why === "3-point world" ? "with a world worth 3 world points" : s.why === "Cradle" ? "with Cradle (3 of each affinity)" : `on rounds, ${s.p[ME].wins}–${s.p[AI].wins}`;
  dlg.innerHTML = `<h2>${head}</h2><p>Won ${why}.</p>
  <table><tr><th>Round</th><th>Winner</th><th>How</th><th>You</th><th>Computer</th></tr>
  ${s.rounds.map((r) => `<tr><td>${r.r}</td><td>${r.winner === null ? "draw" : r.winner === ME ? "you" : "computer"}</td><td>${esc(r.why)}</td><td>${r.score[0].pts} point${r.score[0].pts === 1 ? "" : "s"}, tie ${r.score[0].tie}</td><td>${r.score[1].pts} point${r.score[1].pts === 1 ? "" : "s"}, tie ${r.score[1].tie}</td></tr>`).join("")}</table>`;
  const act = el("div", "actions");
  const look = el("button", "", "Look at the table"); look.onclick = () => { o.hidden = true; };
  const again = el("button", "", "Rematch"); again.onclick = () => startContest();
  const next = el("button", "primary", "New contest"); next.onclick = () => showStart();
  act.append(look, again, next); dlg.append(act); o.append(dlg);
}

// ------------------------------------------------------------------ choosing a play
const keyOf = (pk) => JSON.stringify(pk);
const matches = (m, picks) => picks.every((pk, k) => m.picks[k] && keyOf(m.picks[k]) === keyOf(pk));
function myMoves() { return s && s.phase === "turn" && s.turn === ME && !busy ? R.legalMoves(s, ME) : []; }
function clickCard(id) {
  const ms = myMoves().filter((m) => m.id === id);
  if (!ms.length) { flash(s.turn !== ME ? "It's the computer's turn." : `${R.C[id].name} has no legal play right now.`); return; }
  const faces = [...new Set(ms.map((m) => m.face))];
  sel = { id, face: null, moves: ms, picks: [], options: null };
  if (faces.length === 1) chooseFace(faces[0]); else render();
}
function chooseFace(f) { sel.face = f; sel.moves = sel.moves.filter((m) => m.face === f); next(); }
function next() {
  const rem = sel.moves.filter((m) => matches(m, sel.picks));
  if (!rem.length) { sel = null; render(); return; }
  const k = sel.picks.length;
  const done = rem.find((m) => m.picks.length === k);
  if (done && rem.every((m) => m.picks.length === k)) return commit(done);
  const seen = new Map();
  for (const m of rem) if (m.picks[k]) seen.set(keyOf(m.picks[k]), m.picks[k]);
  sel.options = [...seen.values()];
  if (sel.options.length === 1 && sel.options[0].k === "face") { sel.picks.push(sel.options[0]); return next(); }
  render();
}
function pick(pk) { if (!sel || !sel.options) return; sel.picks.push(pk); next(); }
function commit(m) {
  sel = null;
  R.play(s, ME, m);
  lastTs = 0;
  render(); step();
}
let flashTimer = null;
function flash(t) { const p = $("prompt"); p.dataset.flash = t; render(); clearTimeout(flashTimer); flashTimer = setTimeout(() => { delete p.dataset.flash; render(); }, 2200); }

const PICK_WORDS = { cell: "Choose where it goes", perm: "Choose a permanence", world: "Choose a world", player: "Choose a player", force: "Choose a force in play", void: "Choose a card from your void", obinder: "Choose a card from the computer's binder", face: "Choose which face to play" };
function pickHint() {
  const d = R.C[sel.id];
  const k = sel.picks.length;
  const kind = sel.options[0].k;
  let what = PICK_WORDS[kind];
  const sub = sel.picks[0] && sel.picks[0].k === "void" ? R.C[sel.picks[0].card] : null;
  const name = sel.face === "force" ? d.fname : d.name;
  const text = sel.face === "force" ? d.ftext : sel.face === "meta" ? d.text : d.ptext;
  if (sel.face === "perm" && k > 0) what = d.name === "Snowfield" ? "Choose one of your permanences to return" : d.name === "Bluff" ? (kind === "perm" ? "Choose one of your permanences to move" : "Choose where it moves") : d.name === "Hanging Valley" ? "Choose two of your permanences to swap" : what;
  return `<span class="msg"><b>${esc(name)}</b>${text ? ` <em>${esc(text)}</em>` : ""}${sub ? ` → ${esc(sub.name)}` : ""} · ${what}.</span>`;
}

// ------------------------------------------------------------------ rendering
// after a round ends the table is cleared; show it as it stood until the next round starts
function shown() {
  if (s.phase !== "turn" && s.ended) return Object.assign({}, s, { inst: s.ended.inst, worlds: s.ended.worlds, _v: null, calm: false });
  return s;
}
let T = null; // the table being drawn
function render() {
  if (!s) return;
  T = shown();
  const sc = R.score(T);
  const v = R.view(T);
  // status
  const turn = s.phase !== "turn" ? "" : s.turn === ME ? (s.extras.length ? "<b>Your turn</b> · you may play another card" : "<b>Your turn</b>") : busy ? "The computer is thinking…" : "The computer's turn";
  $("status").innerHTML = `Round <b>${s.r}</b> of 3 · rounds won: you <b>${s.p[ME].wins}</b> – <b>${s.p[AI].wins}</b> computer · ${turn}`;
  bar($("oppBar"), AI, sc); bar($("myBar"), ME, sc);
  worlds($("oppWorlds"), AI, v, sc); worlds($("myWorlds"), ME, v, sc);
  inplay(sc);
  binder(); prompt(); log();
  highlight();
}
function bar(box, P, sc) {
  const pl = s.p[P];
  box.className = "pbar " + (P === ME ? "me" : "opp");
  const turn = s.phase === "turn" && s.turn === P;
  box.innerHTML = `<span class="who">${P === ME ? "You" : "Computer"}</span>
    <span class="pill">${esc(s.binderNames[P])}</span>
    <span class="pill big">${sc[P].pts} world point${sc[P].pts === 1 ? "" : "s"}</span>
    <span class="pill">tie-break ${sc[P].tie}</span>
    <span class="pill">played ${pl.played}/${s.cap}</span>
    <span class="pill">binder ${pl.binder.length}</span>
    <span class="pill">void ${pl.void.length}</span>
    ${pl.passed ? `<span class="pill passed">passed</span>` : turn ? `<span class="pill turn">${P === ME ? "your turn" : "thinking"}</span>` : ""}
    ${pl.skip ? `<span class="pill passed">skips next turn</span>` : ""}`;
}
function forcesOn(iid) { return R.forces(T).filter((f) => f.t === iid || f.t2 === iid); }
function forcesOnWorld(wid) { return R.forces(T).filter((f) => f.w === wid || f.w2 === wid); }
function worlds(box, P, v, sc) {
  box.innerHTML = "";
  const cellPicks = sel && sel.options ? sel.options.filter((o) => o.k === "cell") : [];
  for (const w of R.worldsOf(T, P)) {
    const ws = sc[P].worlds.find((x) => x.id === w.id) || { k: 0, cov: 0 };
    const wb = el("div", "world " + (P === ME ? "me" : "opp"));
    wb.dataset.wid = w.id;
    wb.append(el("div", "wlabel", `<span>WORLD ${w.n}</span><span class="pts${ws.k >= 2 ? " hot" : ""}">${ws.k} pt${ws.k === 1 ? "" : "s"}</span>`));
    const full = cellPicks.some((o) => o.w === w.id);
    const occ = [0, 1, 2, 3].filter((c) => w.cells[c] !== null);
    const rows = full ? [0, 1] : [...new Set(occ.map((c) => c >> 1))].sort();
    const cols = full ? [0, 1] : [...new Set(occ.map((c) => c & 1))].sort();
    const g = el("div", "grid"); g.style.gridTemplateColumns = `repeat(${cols.length}, auto)`;
    for (const r of rows) for (const c of cols) {
      const cell = r * 2 + c;
      const iid = w.cells[cell];
      if (iid === null) {
        const sl = el("div", "slot empty" + (full ? " open" : "")); sl.dataset.w = w.id; sl.dataset.cell = cell; g.append(sl); continue;
      }
      const i = T.inst[iid];
      const wrap = el("div", "cardwrap slot"); wrap.dataset.iid = iid;
      const node = face(i.card, "permanence"); node.classList.add("own-" + i.owner);
      if (v.blank[iid]) node.classList.add("blank");
      if (lastTs && i.ts >= lastTs) node.classList.add("lastplay");
      wrap.append(node);
      const on = forcesOn(iid);
      if (on.length) { const b = el("div", "badges"); for (const f of on) b.append(el("span", "tag force", esc(R.C[f.card].fname))); wrap.append(b); }
      const now = v.tok[iid] || [], printed = R.C[i.card].aff;
      const changed = now.length !== printed.length || now.some((t, k) => t !== printed[k]);
      wrap.append(el("div", "chips" + (changed ? " changed" : ""), now.length ? now.map((t) => chip(t)).join("") : `<span class="none">no affinities</span>`));
      g.append(wrap);
    }
    wb.append(g);
    const fw = forcesOnWorld(w.id);
    if (fw.length) { const t = el("div", "wtags"); for (const f of fw) t.append(el("span", "tag force", esc(R.C[f.card].fname))); wb.append(t); }
    box.append(wb);
  }
  if (P === ME && cellPicks.some((o) => o.w === "new")) { const nw = el("div", "newworld", "New world"); nw.dataset.w = "new"; nw.dataset.cell = 0; box.append(nw); }
  if (!box.children.length) box.append(el("div", "", `<span style="color:var(--muted);font-size:12px">${P === ME ? "Your worlds appear here." : "The computer's worlds appear here."}</span>`));
}
function inplay(sc) {
  const box = $("inplay"); box.innerHTML = "";
  box.append(el("span", "lbl", "In play this round"));
  const fs = R.forces(T);
  if (!fs.length && !s.calm) box.append(el("span", "tag", "no lasting forces"));
  if (s.calm) box.append(el("span", "tag warn", "Calm: no forces this round"));
  for (const f of fs) {
    const d = R.C[f.card];
    const wrap = el("div", "f"); wrap.dataset.fid = f.id;
    const node = face(f.card, "force"); node.classList.add("own-" + f.owner);
    if (lastTs && f.ts >= lastTs) node.classList.add("lastplay");
    wrap.append(node);
    let where = "everywhere";
    if (f.t) where = "on " + (T.inst[f.t] ? R.C[T.inst[f.t].card].name : "?") + (f.t2 && T.inst[f.t2] ? " and " + R.C[T.inst[f.t2].card].name : "");
    else if (f.w) where = "on " + R.worldLabel(T, f.w, ME) + (f.w2 ? " and " + R.worldLabel(T, f.w2, ME) : "");
    else if (/^Your /.test(d.ftext)) where = f.owner === ME ? "your worlds" : "the computer's worlds";
    if (d.fname === "Whiteout") where = `until ${f.owner === ME ? "your" : "the computer's"} next turn`;
    wrap.append(el("div", "cap", esc(d.fname) + " · " + esc(where)));
    box.append(wrap);
  }
  const g = el("div", "score");
  g.innerHTML = `<span class="h"></span><span class="h">WORLD POINTS</span><span class="h">TIE-BREAK</span>
    <span>You</span><span>${sc[ME].pts}</span><span>${sc[ME].tie}</span>
    <span>Computer</span><span>${sc[AI].pts}</span><span>${sc[AI].tie}</span>`;
  box.append(g);
}
// ------------------------------------------------------------------ the binder
const PER = 9; // a nine-pocket page
let page = 0;
let flipping = false;
const pageCount = () => Math.max(1, Math.ceil(s.order[ME].length / PER));
function whereIs(id) {
  if (s.p[ME].binder.includes(id)) return "binder";
  if (Object.values(s.inst).some((i) => i.card === id && i.owner === ME)) return "table";
  if (s.p[ME].void.includes(id)) return "void";
  return "gone";
}
// fit the open binder to the right half: pocket scale and preview scale
function fit() {
  const r = $("right").getBoundingClientRect();
  const W = r.width - 36 - 30, H = r.height - 28;
  const sc = Math.max(0.2, Math.min((W - 190) / 1536, (H - 226) / 1344, 0.5));
  const pageW = 3 * (320 * sc + 8) + 20 + 36;
  const insideW = Math.round(pageW * 0.6);
  const contentH = 104 + 1344 * sc;
  const pv = Math.max(0.2, Math.min((insideW - 36) / 320, (contentH - 210) / 2 / 448));
  const b = $("binder");
  b.style.setProperty("--s", sc.toFixed(3));
  b.style.setProperty("--pv", pv.toFixed(3));
  return { insideW, pageH: contentH + 36 };
}
const FLOURISH = `<svg class="flourish" viewBox="0 0 200 10" preserveAspectRatio="none" aria-hidden="true"><path d="M2 6 C40 1 70 9 100 5 S160 1 198 6" stroke="#8a6a40" stroke-width="1.2" fill="none"/><circle cx="100" cy="5" r="1.6" fill="#8a6a40"/></svg>`;
function spineSvg(h) {
  let d = "", holes = "";
  const n = Math.max(6, Math.round(h / 70));
  for (let k = 0; k <= n; k++) {
    const y = 20 + ((h - 40) * k) / n;
    holes += `<circle cx="15" cy="${y.toFixed(1)}" r="2.6" fill="#140a04"/>`;
    if (k < n) { const y2 = 20 + ((h - 40) * (k + 1)) / n; d += `M15 ${y.toFixed(1)} C4 ${((y + y2) / 2).toFixed(1)} 26 ${((y + y2) / 2).toFixed(1)} 15 ${y2.toFixed(1)} `; }
  }
  return `<svg viewBox="0 0 30 ${h}" preserveAspectRatio="none" aria-hidden="true">${holes}<path d="${d}" stroke="#1a0e06" stroke-width="3.2" fill="none" transform="translate(0.8 1)"/><path d="${d}" stroke="#b58a52" stroke-width="2.2" fill="none" stroke-linecap="round"/></svg>`;
}
function pagesLeaf(pg, playable) {
  const leaf = el("div", "leaf pages");
  const slots = s.order[ME].slice(pg * PER, pg * PER + PER);
  leaf.append(el("div", "phead", `<span>${esc(s.binderNames[ME])}</span><span>leaf ${pg + 1}</span>`));
  const grid = el("div", "pockets");
  for (let k = 0; k < PER; k++) {
    const id = slots[k];
    const pocket = el("div", "pocket");
    if (!id) { pocket.classList.add("blank"); grid.append(pocket); continue; }
    const at = whereIs(id);
    if (at === "binder") {
      const node = face(id, "permanence");
      if (!playable.has(id)) node.classList.add("unplayable");
      if (sel && sel.id === id) pocket.classList.add("sel");
      node.onclick = () => clickCard(id);
      pocket.append(node);
    } else {
      const d = R.C[id];
      pocket.append(el("div", "gone", `<span><b>${esc(d.name)}</b>${at === "table" ? "on the table" : at === "void" ? "in the void" : "taken"}</span>`));
      pocket.onmouseenter = () => preview(id, "permanence");
    }
    grid.append(pocket);
  }
  leaf.append(grid);
  leaf.append(el("div", "pfoot", String(pg + 1)));
  return leaf;
}
function insidePage(leaf) {
  leaf = leaf || document.querySelector("#binder .leaf.inside");
  if (!leaf || !s) return;
  leaf.innerHTML = "";
  leaf.append(el("div", "owner", "This binder belongs to you"));
  leaf.append(el("div", "bname", esc(s.binderNames[ME])));
  leaf.insertAdjacentHTML("beforeend", FLOURISH);
  const pv = el("div", "pv");
  const show = sel ? { id: sel.id, face: sel.face === "force" ? "force" : "permanence" } : hover;
  if (show && byId.get(show.id)) {
    const c = byId.get(show.id);
    const faces = c.meta ? ["meta"] : show.face === "force" ? ["force", "permanence"] : ["permanence", "force"];
    const choosing = sel && !sel.face && sel.id === show.id;
    const legal = choosing ? new Set(sel.moves.map((m) => m.face)) : new Set();
    for (const f of faces) {
      const row = el("div", "pvrow");
      row.append(renderFace(c, f, { size: "token" }));
      if (choosing) {
        const fk = f === "permanence" ? "perm" : f;
        const b = el("button", "", f === "meta" ? "Play it" : f === "permanence" ? "Play the permanence" : "Play the force");
        b.disabled = !legal.has(fk);
        b.onclick = () => chooseFace(fk);
        row.append(b);
      }
      pv.append(row);
    }
  } else pv.append(el("div", "hint", "Hover a card to look at it closely.<br>Click one to play it."));
  leaf.append(pv);
  const counts = { binder: 0, table: 0, void: 0 };
  for (const id of s.order[ME]) { const w = whereIs(id); if (counts[w] !== undefined) counts[w]++; }
  leaf.append(el("div", "notes", `<b>${counts.binder}</b> in the binder · <b>${counts.table}</b> on the table · <b>${counts.void}</b> in the void<br>Played this round: <b>${s.p[ME].played}</b> of ${s.cap}`));
}
let binderDue = false; // a redraw asked for while a leaf was turning
function binder() {
  if (flipping) { binderDue = true; return; }
  binderDue = false;
  const box = $("binder"); box.innerHTML = "";
  const { insideW, pageH } = fit();
  page = Math.min(page, pageCount() - 1);
  const playable = new Set(myMoves().map((m) => m.id));
  const cover = el("div", "cover");
  const inside = el("div", "leaf inside"); inside.style.width = insideW + "px";
  insidePage(inside);
  const spine = el("div", "spine", spineSvg(Math.round(pageH)));
  const pages = pagesLeaf(page, playable);
  const tabs = el("div", "ptabs");
  for (let k = 0; k < pageCount(); k++) {
    const t = el("button", k === page ? "on" : "", String(k + 1));
    t.title = `Leaf ${k + 1}`;
    t.onclick = () => flipTo(k);
    tabs.append(t);
  }
  cover.append(inside, spine, pages, tabs);
  box.append(cover);
  const nav = el("div", "bnav");
  const prev = el("button", "", "‹"); prev.title = "Previous leaf (←)"; prev.disabled = page === 0; prev.onclick = () => flipTo(page - 1);
  const next = el("button", "", "›"); next.title = "Next leaf (→)"; next.disabled = page >= pageCount() - 1; next.onclick = () => flipTo(page + 1);
  nav.append(prev, el("span", "", `Leaf ${page + 1} of ${pageCount()}`), next, el("span", "keys", "← → to turn"));
  box.append(nav);
}
// turn the leaf: the page lifts from the right and swings over the spine (or back)
function flipTo(k) {
  if (flipping || k < 0 || k >= pageCount() || k === page) return;
  const cover = document.querySelector("#binder .cover"), cur = cover && cover.querySelector(".leaf.pages");
  if (!cur) { page = k; binder(); return; }
  const fwd = k > page;
  const playable = new Set(myMoves().map((m) => m.id));
  const front = fwd ? cur.cloneNode(true) : pagesLeaf(k, playable);
  const rect = { left: cur.offsetLeft, top: cur.offsetTop, width: cur.offsetWidth, height: cur.offsetHeight };
  const make = () => {
    const sheet = el("div", "sheet");
    Object.assign(sheet.style, { left: rect.left + "px", top: rect.top + "px", width: rect.width + "px", height: rect.height + "px" });
    const f = el("div", "side front"); front.style.height = "100%"; f.append(front);
    const b = el("div", "side back"); b.append(el("div", "leaf inside blankback"));
    sheet.append(f, b);
    return sheet;
  };
  if (fwd) {
    page = k; binder();
    flipping = true;
    const sheet = make();
    document.querySelector("#binder .cover").append(sheet);
    requestAnimationFrame(() => requestAnimationFrame(() => { sheet.style.transform = "rotateY(-180deg)"; }));
    setTimeout(() => { sheet.remove(); flipping = false; if (binderDue) binder(); }, 620);
  } else {
    flipping = true;
    const sheet = make();
    sheet.style.transition = "none"; sheet.style.transform = "rotateY(-180deg)";
    cover.append(sheet);
    requestAnimationFrame(() => requestAnimationFrame(() => { sheet.style.transition = ""; sheet.style.transform = "rotateY(0deg)"; }));
    setTimeout(() => { page = k; flipping = false; binder(); }, 620);
  }
}

function prompt() {
  const box = $("prompt"); box.innerHTML = "";
  if (box.dataset.flash) box.append(el("span", "msg", esc(box.dataset.flash)));
  const mine = s.phase === "turn" && s.turn === ME && !busy;
  if (sel && !sel.face) {
    const d = R.C[sel.id];
    box.append(el("span", "msg", `<b>${esc(d.name)}</b> · Play it as`));
    const o = el("div", "opts");
    for (const f of [...new Set(sel.moves.map((m) => m.face))]) {
      const b = el("button", "primary", f === "perm" ? `the permanence, ${esc(d.name)}` : `the force, ${esc(d.fname)}`);
      b.onclick = () => chooseFace(f);
      b.onmouseenter = () => preview(sel.id, f === "perm" ? "permanence" : "force");
      o.append(b);
    }
    box.append(o);
  } else if (sel && sel.options) {
    box.insertAdjacentHTML("beforeend", pickHint());
    const o = el("div", "opts");
    const list = sel.options.filter((pk) => ["player", "void", "obinder", "face", "force"].includes(pk.k) || sel.options.length <= 12 || pk.w === "new");
    for (const pk of list) {
      const b = el("button", "", esc(R.describePick(s, pk, ME)).replace(/^./, (c) => c.toUpperCase()));
      b.onclick = () => pick(pk);
      if (pk.card) b.onmouseenter = () => preview(pk.card, "permanence");
      o.append(b);
    }
    box.append(o);
  } else if (mine) {
    box.append(el("span", "msg", s.extras.length ? `You may play another card${s.extras.includes("any") ? "" : " (a fire card)"}.` : "Your turn: click a card in your binder, on the right, to play it."));
  } else if (s.phase === "turn") box.append(el("span", "msg", "The computer is playing…"));
  box.append(el("span", "spacer"));
  if (sel) { const c = el("button", "", "Cancel"); c.onclick = () => { sel = null; render(); }; box.append(c); }
  if (mine && !sel) {
    const p = el("button", s.extras.length ? "" : "warn", s.extras.length ? "End turn" : "Pass for the round");
    p.onclick = () => { R.pass(s, ME); render(); step(); };
    box.append(p);
  }
}
function log() {
  const box = $("log"); const atEnd = box.scrollTop + box.clientHeight >= box.scrollHeight - 30;
  box.innerHTML = "";
  for (const l of s.log) {
    const li = el("li", l.P === null || l.P === undefined || /^Round \d/.test(l.text) ? "sys" : "p" + l.P, esc(l.text.replace(/^You played/, "You played").replace(/Computer's world/g, "the computer's world")));
    box.append(li);
  }
  if (atEnd) box.scrollTop = box.scrollHeight;
}
function highlight() {
  if (!sel || !sel.options) return;
  for (const pk of sel.options) {
    let nodes = [];
    if (pk.k === "perm") nodes = [...document.querySelectorAll(`#board [data-iid="${pk.id}"]`)];
    else if (pk.k === "world") nodes = [...document.querySelectorAll(`#board .world[data-wid="${pk.id}"]`)];
    else if (pk.k === "cell") nodes = [...document.querySelectorAll(pk.w === "new" ? `#board .newworld` : `#board .slot[data-w="${pk.w}"][data-cell="${pk.cell}"]`)];
    else if (pk.k === "force") nodes = [...document.querySelectorAll(`#inplay [data-fid="${pk.id}"]`)];
    for (const n of nodes) {
      n.classList.add("pickable");
      n.onclick = (e) => { e.stopPropagation(); pick(pk); };
    }
  }
}

boot();
