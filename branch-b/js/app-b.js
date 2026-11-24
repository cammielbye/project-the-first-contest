// The Branch B table (Nov 23): the main table's look with the Branch B rules enforced by js/rules-b.js.
// Three ways to play, like the main table: against the computer (js/ai-b.js), two players on one screen, and a
// friend online (js/net.js, PeerJS; the host's browser runs the contest and the guest sends its actions).
import * as R from "./rules-b.js";
import { planFor, act } from "./ai-b.js";
import { token, frontHtml, backHtml, esc } from "./cards-b.js";
import { createNet, peerOptionsFromUrl } from "./net.js";

const $ = (id) => document.getElementById(id);
const store = {
  get(k, d) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} },
};
const params = new URLSearchParams(location.search);
const NAMES = { computer: ["You", "Computer"], local: ["Player 1", "Player 2"], friend: ["Player 1", "Player 2"] };
const TOK = 96, POCKET = 73;

let mode = params.get("join") ? "friend" : store.get("bb:mode", "computer");
let S = null, undo = [];
const ui = { binderSel: null, cardSel: null, opening: 0, busy: false, rules: false, dismissed: false };
let stage = store.get("bb:stage", "mid"); // which binders a new contest deals (the simulation stages)
const F = { net: null, role: null, room: null, status: "", linked: false };

// ---------------------------------------------------------------- who is who
const me = () => (mode === "friend" ? (F.role === "guest" ? 1 : 0) : 0);
const bottom = () => (mode === "local" ? 0 : me());
const actor = () => (S ? (S.pending ? S.pending.P : R.active(S)) : null); // the seat that acts next
const mine = (P) => P !== null && (mode === "local" ? true : P === me()); // can this screen act for seat P?
const viewer = () => (mode === "local" ? (actor() ?? 0) : me()); // whose binder and hidden choices this screen shows
const label = (P) => (mode === "friend" ? `${S.names[P]}${P === me() ? " (you)" : ""}` : S.names[P]);

// ---------------------------------------------------------------- the contest
const saveKey = () => `bb:state:${mode}`;
function save() { if (S && !(mode === "friend" && F.role === "guest")) store.set(saveKey(), S); }
function load() { const s = store.get(saveKey(), null); return s && s.v === 1 && s.P ? s : null; }
function newContest() {
  S = R.newGame(Math.random() < 0.5 ? 0 : 1, NAMES[mode], stage);
  undo = []; Object.assign(ui, { binderSel: null, cardSel: null, opening: 0, dismissed: false });
  save(); broadcast(); render(); kickComputer();
}
function apply(P, a) {
  if (a.k === "clear") { R.clearStage(S, P); return true; }
  return act(S, P, a);
}
function doAct(a) {
  if (!S || ui.busy) return;
  if (mode === "friend" && F.role === "guest") { F.net?.send({ type: "act", a }); ui.binderSel = null; ui.cardSel = null; render(); return; }
  const P = actor();
  if (!mine(P)) return;
  const before = JSON.stringify(S);
  if (!apply(P, a)) return;
  if (mode !== "friend") { undo.push(before); if (undo.length > 80) undo.shift(); }
  ui.binderSel = null; ui.cardSel = null;
  save(); broadcast(); render(); kickComputer();
}

// ---------------------------------------------------------------- the computer
function kickComputer(tries = 0) {
  if (mode !== "computer" || !S || S.phase === "over" || ui.busy || actor() !== 1 || tries > 3) return;
  ui.busy = true; render();
  setTimeout(() => {
    const game = S, plan = planFor(S, 1);
    if (!plan.length) { ui.busy = false; render(); return; }
    const run = (i) => {
      if (S !== game) { ui.busy = false; return; }
      const a = plan[i];
      const stop = !a || !act(S, 1, a) || S.phase === "over" || (S.pending && S.pending.P !== 1) || (!S.pending && R.active(S) !== 1);
      save(); render();
      if (stop) { ui.busy = false; render(); if (actor() === 1 && S.phase !== "over") kickComputer(tries + 1); return; }
      setTimeout(() => run(i + 1), 650);
    };
    run(0);
  }, 450);
}

// ---------------------------------------------------------------- friend online
function broadcast() { if (mode === "friend" && F.role === "host" && F.net) F.net.send({ type: "state", s: S }); }
function startFriend(role, room) {
  if (!window.RTCPeerConnection || !window.Peer) { F.status = "This copy of the table can't open a connection. Use the GitHub Pages copy for Friend mode."; render(); return; }
  F.role = role; F.room = room.toUpperCase(); F.linked = false;
  if (role === "host") { S = load(); if (!S) { S = R.newGame(Math.random() < 0.5 ? 0 : 1, NAMES.friend, stage); save(); } }
  else S = null;
  F.net = createNet({
    mode: role, room: F.room, peerOptions: peerOptionsFromUrl(params),
    onStatus: (st) => {
      F.status = { waiting: "Waiting for your friend to join.", linked: "Connected.", unlinked: "Your friend disconnected.", connecting: "Connecting…", "host-missing": "No table with that code yet. Retrying…", "busy-id": "That code is still in use. Retrying…", "broker-lost": "Lost the connection broker. Reconnecting…" }[st.kind] || st.message || st.kind;
      F.linked = st.kind === "linked" ? true : st.kind === "unlinked" ? false : F.linked;
      render();
    },
    onMessage: (m) => {
      if (m.type === "_linked") { if (F.role === "host") broadcast(); return; }
      if (F.role === "guest" && m.type === "state") { S = m.s; render(); return; }
      if (F.role === "guest" && m.type === "busy") { F.status = "That table already has two players."; render(); return; }
      if (F.role === "host" && m.type === "act" && S) {
        if (m.a.k === "new") return newContest();
        if (actor() !== 1) return;
        const before = JSON.stringify(S);
        if (apply(1, m.a)) { save(); broadcast(); render(); } else S = JSON.parse(before);
      }
    },
  });
  render();
}
const code = () => Array.from({ length: 5 }, () => "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"[Math.floor(Math.random() * 32)]).join("");

// ---------------------------------------------------------------- what can be clicked
function targets() {
  const t = { cards: new Set(), worlds: new Set(), ghost: new Set(), stop: false, cancel: false, prompt: "" };
  if (!S || S.phase === "over") return t;
  if (S.pending && mine(S.pending.P) && !ui.busy) {
    const st = R.choices(S);
    if (st) for (const o of st.opts) { if (o.t === "card") t.cards.add(o.id); else if (o.t === "world") t.worlds.add(`${o.side}:${o.w}`); else if (o.t === "new") t.ghost.add(o.side); }
    t.stop = !!st?.canStop; t.cancel = !S.pending.picks.length && !S.pending.locked; t.prompt = st?.prompt || "";
    return t;
  }
  if (ui.binderSel !== null) {
    const P = actor();
    for (const m of R.legalPlays(S, P)) if (m.ci === ui.binderSel) { if (m.w === "new") t.ghost.add(P); else t.worlds.add(`${m.side}:${m.w}`); }
  }
  return t;
}
function playable(P) { return mine(P) && !ui.busy && R.legalPlays(S, P).length > 0; }

// ---------------------------------------------------------------- drawing
function render() {
  document.querySelectorAll("#modes button").forEach((b) => b.classList.toggle("on", b.dataset.mode === mode));
  $("undoBtn").disabled = mode === "friend" || !undo.length || ui.busy;
  document.querySelectorAll("#stages button").forEach((b) => b.classList.toggle("on", b.dataset.stage === stage));
  $("stages").title = S && S.stage && S.stage !== stage ? `This contest uses ${S.stage}-game binders; the next one uses ${stage}-game binders.` : "";
  if (mode === "friend" && !F.role) { $("areaTop").innerHTML = ""; $("areaBottom").innerHTML = ""; $("plaque").innerHTML = ""; $("binderPanel").innerHTML = ""; $("status").innerHTML = ""; return renderOverlay(); }
  if (!S) { $("status").textContent = F.status; renderOverlay(); return; }
  const T = targets();
  const st = S.phase === "over" ? "Contest over" : R.shared(S) ? "Turn 10, <b>shared</b>" : `Turn <b>${R.turnNo(S)}</b> of 9`;
  $("status").innerHTML = `${st}${mode === "friend" ? ` · room <b>${esc(F.room)}</b>, ${esc(F.status)}` : ""}`;
  const top = 1 - bottom();
  $("areaTop").innerHTML = side(top, T);
  $("areaBottom").innerHTML = side(bottom(), T);
  $("plaque").innerHTML = plaque(T, top);
  renderBinder();
  renderOverlay();
  const rows = [...document.querySelectorAll("#table .row")].map((r) => r.getBoundingClientRect().width);
  $("table").style.setProperty("--runw", `${Math.max(560, ...rows) + 110}px`);
}
function side(P, T) {
  const W = S.P[P].worlds, pc = P === 0 ? "var(--p1)" : "var(--p2)";
  const staged = S.phase === "lock" && P === viewer() ? S.stage[P].force : null;
  const worlds = W.map((w, wi) => {
    const pts = R.worldPts(S, w), tgt = T.worlds.has(`${P}:${wi}`);
    const cards = w.map((id) => {
      const i = S.inst[id], cls = [i.o !== P ? `away own${i.o}` : "", T.cards.has(id) ? "opt" : "", ui.cardSel === id ? "sel" : "", !i.f && i.h === S.half && S.phase === "turn" ? "fresh" : "", id === staged ? "locked" : ""].join(" ");
      return token(i.c, i.f, TOK, cls).replace('class="tok', `data-id="${id}" data-ci="${i.c}" data-back="${i.f ? 1 : 0}" tabindex="0" role="button" aria-label="${esc(i.f ? R.CARDS[i.c].b : R.CARDS[i.c].n)}" class="tok`);
    }).join("");
    const slots = Array.from({ length: 4 - w.length }, () => '<span class="slot"></span>').join("");
    return `<div class="world${pts >= 3 ? " perfect" : ""}${tgt ? " tgt" : ""}" style="--pc:${pc}" ${tgt ? `data-act="world" data-side="${P}" data-w="${wi}" tabindex="0" role="button"` : ""}><span class="lab">World ${wi + 1} · ${pts} point${pts === 1 ? "" : "s"}</span>${cards}${slots}</div>`;
  }).join("");
  const ghost = T.ghost.has(P) ? `<div class="world ghost" style="--pc:${pc}" data-act="world" data-side="${P}" data-w="new" tabindex="0" role="button">New world</div>` : "";
  const empty = !W.length && !ghost ? `<span class="empty-note">${label(P) === "You" ? "You have" : `${esc(label(P))} has`} no worlds yet.</span>` : "";
  return `<div class="row">${worlds}${ghost}${empty}</div>`;
}
function plaque(T, top) {
  const P = actor(), who = (X) => {
    const n = R.total(S, X);
    return `<div class="who ${X === top ? "" : "r"} ${X === 0 ? "p1" : "p2"} ${P === X ? "on" : ""}"><span class="nm">${esc(label(X))}</span><span class="pts"><b>${n}</b> world point${n === 1 ? "" : "s"} · ${S.P[X].binder.length} in binder${S.phase === "lock" && S.locked[X] ? " · locked in" : ""}</span></div>`;
  };
  return `${who(top)}<div class="mid">${middle(T, P)}</div>${who(1 - top)}`;
}
function middle(T, P) {
  const btn = (act, text, cls = "", dis = false) => `<button data-act="${act}" class="${cls}" ${dis ? "disabled" : ""}>${text}</button>`;
  if (S.phase === "over") {
    const w = S.winner;
    return `<div class="say"><b>${w.P === null ? "A draw." : `${esc(label(w.P))} win${label(w.P) === "You" ? "" : "s"}${w.why === "perfect" ? " with a perfect world" : " on world points"}.`}</b></div><div class="sub">${esc(S.names[0])} ${R.total(S, 0)} · ${esc(S.names[1])} ${R.total(S, 1)}</div><div class="btns">${btn("new", "New contest", "go")}</div>`;
  }
  if (S.pending) {
    if (!mine(S.pending.P) || ui.busy) return `<div class="say">${esc(label(S.pending.P))} ${mode === "computer" ? "is choosing" : "chooses"} for ${esc(R.card(S, S.pending.id).b)}…</div>`;
    return `<div class="say">${esc(R.card(S, S.pending.id).b)}: ${esc(T.prompt)}</div><div class="btns">${T.stop ? btn("stop", "Stop here") : ""}${T.cancel ? btn("cancel", "Cancel") : ""}</div>`;
  }
  if (ui.busy) return `<div class="say">The computer is thinking…</div>`;
  if (!mine(P)) return `<div class="say">Waiting for ${esc(label(P))}${S.phase === "lock" ? " to lock in" : ""}…</div>`;
  if (ui.binderSel !== null) return `<div class="say">Choose a world for <b>${esc(R.CARDS[ui.binderSel].n)}</b>${R.CARDS[ui.binderSel].away ? ", yours or your opponent's" : ""}.</div><div class="btns">${btn("unsel", "Cancel")}</div>`;
  const lock = S.phase === "lock";
  let sel = "";
  if (ui.cardSel && S.inst[ui.cardSel]) {
    const id = ui.cardSel, i = S.inst[id], c = R.CARDS[i.c], can = R.canUseForce(S, P, id);
    const why = i.f ? "already used" : i.h === S.half && !lock ? "played this turn" : S.forced >= 1 && !lock ? "you've used a force this turn" : lock && S.stage[P].force ? "a force is already locked in" : "";
    sel = `<div class="sub"><b>${esc(c.n)}</b> → ${esc(c.b)}: ${esc(c.t || "its pips count as any element")}</div><div class="btns">${btn("force", lock ? `Lock in ${esc(c.b)}` : `Use ${esc(c.b)}`, "go", !can)}${btn("unsel", "Close")}</div>${can ? "" : `<div class="sub">Can't use it: ${why}.</div>`}`;
  }
  if (lock) {
    const st = S.stage[P];
    return `<div class="say">${esc(label(P))}: lock in a landscape and a force, hidden until the reveal.</div><div class="sub">${st.play ? `Landscape: <b>${esc(R.CARDS[st.play.ci].n)}</b>` : "No landscape yet"} · ${st.force ? `Force: <b>${esc(R.card(S, st.force).b)}</b>` : "no force yet"}</div>${sel}<div class="btns">${st.play || st.force ? btn("clear", "Clear") : ""}${btn("lock", `Lock in${mode === "local" ? ` ${esc(label(P))}` : ""}`, "go")}</div>`;
  }
  const cap = 1 + S.extra;
  return `<div class="say">${esc(label(P))}${label(P) === "You" ? "r" : "'s"} turn. Play a landscape from the binder, or pick a card in play to use its force.</div><div class="sub">Landscapes ${S.played}/${cap} · forces ${S.forced}/1</div>${sel}<div class="btns">${btn("end", R.turnNo(S) === 9 && R.active(S) !== S.first ? "End turn 9 · to the shared 10th" : "End turn", "go")}</div>`;
}
function renderBinder() {
  const V = viewer(), canPlay = playable(V) && !S.pending;
  const have = new Set(S.P[V].binder), staged = S.phase === "lock" ? S.stage[V].play?.ci : undefined;
  const pocket = (ci) => {
    if (!have.has(ci) || ci === staged) return '<div class="pocket"></div>';
    const cls = `${canPlay ? "" : "dim"} ${ui.binderSel === ci ? "sel" : ""}`;
    return `<div class="pocket">${token(ci, false, POCKET, cls).replace('class="tok', `data-act="bcard" data-ci="${ci}" data-back="0" tabindex="0" role="button" aria-label="${esc(R.CARDS[ci].n)}" class="tok`)}</div>`;
  };
  // the binder holds the cards this player brought, four to a page, two pages open at a time
  const deck = S.P[V].deck || R.CARDS.map((c) => c.i), openings = Math.max(1, Math.ceil(deck.length / 8));
  ui.opening = Math.min(ui.opening, openings - 1);
  const base = ui.opening * 8, page = 2 * ui.opening + 1;
  const leaf = (k, side) => `<div class="leaf ${side}"><div class="phead"><span>${side === "left" ? `Page ${page}` : ""}</span><span>${side === "right" ? `Page ${page + 1}` : ""}</span></div><div class="pockets">${[0, 1, 2, 3].map((j) => (deck[base + k + j] === undefined ? '<div class="pocket"></div>' : pocket(deck[base + k + j]))).join("")}</div></div>`;
  const title = mode === "local" ? `${label(V)}'s binder` : "Your binder";
  $("binderPanel").innerHTML = `<h2 class="btitle">${esc(title)}</h2><p class="bhint">${canPlay ? "Click a landscape, then a world on the table. Hover any card to read both sides." : "Hover any card to read both sides."}</p>
    <div class="cover">${leaf(0, "left")}<div class="spine"><span class="hb t"></span><span class="hb b"></span></div>${leaf(4, "right")}</div>
    <div class="pagetabs">${Array.from({ length: openings }, (_, k) => `<button data-act="pages" data-k="${k}" class="${ui.opening === k ? "on" : ""}">Pages ${2 * k + 1}–${2 * k + 2}</button>`).join("")}</div>
    <div class="logbox"><h2>Log</h2><ul>${S.log.slice(-60).reverse().map((l) => `<li class="${l.P === 0 ? "p0" : l.P === 1 ? "p1" : ""}">${esc(l.text)}</li>`).join("")}</ul></div>`;
}
function renderOverlay() {
  const o = $("overlay");
  if (ui.rules) {
    o.hidden = false;
    o.innerHTML = `<div class="dialog"><h2>Rules for this test</h2><ul>
      <li>Binders follow the stage chosen at the top: early, every card with 1 or 2 pips (16); mid, those plus one random 3-pip card each (17); late, all 24. Best of one; a coin toss picks who goes first.</li>
      <li>Whole turns back and forth, 9 each. Turn 10 is shared: both players lock in a landscape and a force, then reveal together; forces resolve in turn order.</li>
      <li>Each turn: play up to one landscape and use up to one force. Using a force flips the card: its front pips stop counting and its back pips count.</li>
      <li>A landscape can't use its force the turn it's played. A card flipped by another card's force doesn't use its own force, unless the text says "Its force happens."</li>
      <li>Worlds hold up to 2×2. A world point is one of each element or four of one, each pip counted once.</li>
      <li>A world worth 3 world points is a perfect world and wins at once. Otherwise the most world points after turn 10 wins.</li>
    </ul><div class="btns"><button data-act="rules" class="go">Close</button></div></div>`;
    return;
  }
  if (mode === "friend" && !F.role) {
    o.hidden = false;
    o.innerHTML = `<div class="dialog"><h2>Play a friend online</h2><p>One of you hosts and sends the other a code. The host's browser runs the contest.</p>
      <div class="btns"><button data-act="host" class="go">Host a table</button></div>
      <p>Or join with a code:</p><div class="btns"><input id="joinCode" maxlength="5" placeholder="CODE" aria-label="Table code"><button data-act="join">Join</button></div>
      ${F.status ? `<p class="sub">${esc(F.status)}</p>` : ""}<div class="btns"><button data-act="mode" data-mode="computer">Back to the computer</button></div></div>`;
    return;
  }
  if (mode === "friend" && F.role === "host" && !F.linked) {
    o.hidden = false;
    const link = `${location.origin}${location.pathname}?join=${F.room}`;
    o.innerHTML = `<div class="dialog"><h2>Table ${esc(F.room)}</h2><p>Send your friend this code, or this link:</p><p><code>${esc(link)}</code></p><p class="sub">${esc(F.status)}</p><div class="btns"><button data-act="copy">Copy link</button><button data-act="mode" data-mode="computer">Cancel</button></div></div>`;
    return;
  }
  if (mode === "friend" && F.role === "guest" && !S) {
    o.hidden = false;
    o.innerHTML = `<div class="dialog"><h2>Joining ${esc(F.room)}</h2><p>${esc(F.status || "Connecting…")}</p><div class="btns"><button data-act="mode" data-mode="computer">Cancel</button></div></div>`;
    return;
  }
  o.hidden = true; o.innerHTML = "";
}

// ---------------------------------------------------------------- input
document.addEventListener("click", (e) => {
  const t = e.target.closest("[data-act], .tok[data-id]");
  if (!t) return;
  const a = t.dataset.act;
  if (!a && t.dataset.id) {
    // a card inside a world you're choosing counts as choosing that world
    const wEl = t.closest('.world[data-act="world"]');
    if (wEl && S && (ui.binderSel !== null || (S.pending && !targets().cards.has(t.dataset.id)))) return wEl.click();
    return clickCard(t.dataset.id);
  }
  if (a === "mode") { switchMode(t.dataset.mode); return; }
  if (a === "rules") { ui.rules = !ui.rules; return render(); }
  if (a === "host") return startFriend("host", code());
  if (a === "join") { const c = ($("joinCode")?.value || "").trim(); if (c.length >= 4) startFriend("guest", c); return; }
  if (a === "copy") { navigator.clipboard?.writeText(`${location.origin}${location.pathname}?join=${F.room}`).catch(() => {}); return; }
  if (a === "pages") { ui.opening = +t.dataset.k; return render(); }
  if (a === "stage") { stage = t.dataset.stage; store.set("bb:stage", stage); render(); return; }
  if (!S) return;
  if (a === "new") { if (mode === "friend" && F.role === "guest") F.net?.send({ type: "act", a: { k: "new" } }); else newContest(); return; }
  if (a === "undo") { if (undo.length && !ui.busy) { S = JSON.parse(undo.pop()); ui.binderSel = null; ui.cardSel = null; save(); render(); } return; }
  if (a === "unsel") { ui.binderSel = null; ui.cardSel = null; return render(); }
  if (a === "bcard") { if (t.classList.contains("dim")) return; ui.cardSel = null; ui.binderSel = ui.binderSel === +t.dataset.ci ? null : +t.dataset.ci; return render(); }
  if (a === "world") {
    const side = +t.dataset.side, w = t.dataset.w === "new" ? "new" : +t.dataset.w;
    if (S.pending) return doAct({ k: "pick", opt: w === "new" ? { t: "new", side } : { t: "world", side, w } });
    if (ui.binderSel !== null) return doAct({ k: "play", ci: ui.binderSel, w, side });
    return;
  }
  if (a === "stop") return doAct({ k: "pick", opt: { t: "stop" } });
  if (a === "cancel") return doAct({ k: "cancel" });
  if (a === "force" && ui.cardSel) return doAct({ k: "force", id: ui.cardSel });
  if (a === "end") return doAct({ k: "end" });
  if (a === "lock") return doAct({ k: "lock" });
  if (a === "clear") return doAct({ k: "clear" });
});
function clickCard(id) {
  if (!S || ui.busy) return;
  if (S.pending) { if (mine(S.pending.P) && targets().cards.has(id)) doAct({ k: "pick", opt: { t: "card", id } }); return; }
  const P = actor(), f = R.findCard(S, id);
  if (!mine(P) || !f || S.inst[id].o !== P) { ui.cardSel = null; return render(); }
  ui.binderSel = null; ui.cardSel = ui.cardSel === id ? null : id; render();
}
document.addEventListener("keydown", (e) => {
  if ((e.key === "Enter" || e.key === " ") && e.target.matches("[role=button]")) { e.preventDefault(); e.target.click(); }
  if (e.key === "Escape") { ui.binderSel = null; ui.cardSel = null; ui.rules = false; render(); }
});
function switchMode(m) {
  if (F.net) { location.href = location.pathname + (m === "friend" ? "" : ""); store.set("bb:mode", m); return; }
  mode = m; store.set("bb:mode", m); ui.busy = false;
  if (m === "friend") { S = null; F.role = null; F.status = ""; return render(); }
  S = load(); undo = [];
  if (!S) newContest(); else { render(); kickComputer(); }
}

// hovering a card shows both of its faces, large
const pv = $("preview");
document.addEventListener("mouseover", (e) => {
  const t = e.target.closest(".tok[data-ci]");
  if (!t) { pv.hidden = true; return; }
  const c = R.CARDS[+t.dataset.ci], back = t.dataset.back === "1", s = 0.56;
  const face = (html, on) => `<div class="tok${on ? " sel" : ""}" style="--s:${s}"><div class="face">${html}</div></div>`;
  pv.innerHTML = face(frontHtml(c), !back) + face(backHtml(c), back);
  pv.hidden = false;
  const r = t.getBoundingClientRect(), w = 2 * 320 * s + 30, h = 448 * s + 20;
  const x = r.right + 12 + w < innerWidth ? r.right + 12 : Math.max(8, r.left - 12 - w);
  pv.style.left = `${x}px`; pv.style.top = `${Math.min(innerHeight - h - 8, Math.max(8, r.top - 40))}px`;
});

// ---------------------------------------------------------------- start
if (mode === "friend") {
  const j = params.get("join");
  if (j) startFriend("guest", j); else render();
} else {
  S = load();
  if (!S) newContest(); else { render(); kickComputer(); }
}
