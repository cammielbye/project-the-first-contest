// Playing the computer, on the table page. The third-pass rules engine (js/game/rules.js)
// applies every card and the computer (js/game/ai.js) plays the other seat. The binder, the
// felt, the scoreboard, the log and the voids are the table's own; this file only feeds them
// the engine's contest instead of the hand-moved table. A table with a friend in a room stays
// rules-by-hand.
import * as R from "./game/rules.js";
import { makeAI } from "./game/ai.js";

const ME = 0, AI = 1;
const SEAT = ["p1", "p2"]; // you sit where player 1 sits at the friend table
const SAVE = "tfc:cpu:contest";
const SAVE_V = 1;

// The four element symbols, bare (no ring), for a card whose affinities have changed.
// Engine bits: fire 1, water 2, air 4, earth 8; 15 is a wildcard.
const SYM = {
  1: { color: "#D0663F", d: "M12 3.5 L20.5 19 H3.5 Z" },
  2: { color: "#7FA7B5", d: "M3.5 5 H20.5 L12 20.5 Z" },
  4: { color: "#D5D8CC", d: "M12 3.5 L20.5 19 H3.5 Z M3 12.5 H21" },
  8: { color: "#A88F6B", d: "M3.5 5 H20.5 L12 20.5 Z M3 11.5 H21" },
};
function chipSvg(mask) {
  if (mask === 15) return `<svg viewBox="0 0 24 24" fill="none" stroke="#C2C5B8" stroke-width="2"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="2"/></svg>`;
  return [1, 2, 4, 8]
    .filter((b) => mask & b)
    .map((b) => `<svg viewBox="0 0 24 24" fill="none" stroke="${SYM[b].color}" stroke-width="2.2" stroke-linejoin="round"><path d="${SYM[b].d}"/></svg>`)
    .join('<span class="or">/</span>');
}
const elementLine = (ids) => {
  const t = [0, 0, 0, 0];
  for (const id of ids) {
    const d = R.C[id];
    if (!d || !d.aff) continue;
    for (const m of d.aff) {
      const bits = [1, 2, 4, 8].filter((b) => m & b);
      if (m !== 15) bits.forEach((b) => (t[[1, 2, 4, 8].indexOf(b)] += bits.length > 1 ? 0.5 : 1));
    }
  }
  return `fire ${t[0]} · water ${t[1]} · air ${t[2]} · earth ${t[3]}`;
};
const short = (name) => name.replace(/^Binder \w, /, "");
const upper = (t) => String(t).replace(/^./, (c) => c.toUpperCase());

export function createComputer(ctx) {
  const { h, renderFace, buildAlbum, goneSleeve, store, $, ui, cardsById, cardOrder, binders } = ctx;
  R.loadCards(ctx.cardsJson);
  const ai = makeAI({});

  let s = load(); // the contest, or null before one starts
  const saved = store.get("tfc:cpu:choice", null);
  const choice = {
    mine: saved && saved.mine < binders.length ? saved.mine : 0,
    theirs: saved && saved.theirs < binders.length ? saved.theirs : Math.min(1, binders.length - 1),
  };
  let sel = null; // the card being played: { id, face, moves, picks, options, note }
  let busy = false; // the computer is thinking
  let lastTs = 0; // cards from the computer's last play glow
  let flashMsg = "", flashTimer = null;
  let dismissed = null; // the round or contest summary you closed to look at the table
  let T = null; // the table being drawn
  const faceOf = new Map(); // a binder card flipped on its own with ↻

  // ---------------------------------------------------------------- keeping the contest
  function load() {
    const d = store.get(SAVE, null);
    if (!d || d.v !== SAVE_V || d.synced !== ctx.cardsJson.syncedAt || !d.s || !Array.isArray(d.s.p)) return null;
    const ok = (id) => !!R.C[id];
    if (!d.s.p.every((p) => p.binder.every(ok) && p.void.every(ok))) return null;
    return d.s;
  }
  function save() {
    if (!s) return store.set(SAVE, null);
    const cache = s._v;
    s._v = null;
    store.set(SAVE, { v: SAVE_V, synced: ctx.cardsJson.syncedAt, s });
    s._v = cache;
  }

  // ---------------------------------------------------------------- the contest
  const byPool = (a, b) => (cardOrder.get(a) ?? 1e6) - (cardOrder.get(b) ?? 1e6);
  const pockets = (b) => [...new Set(b.cards)].filter((id) => cardsById.has(id)).sort(byPool);
  function start() {
    const bm = binders[choice.mine], bt = binders[choice.theirs];
    s = R.newContest(bm.cards, bt.cards, Math.random() < 0.5 ? ME : AI, ["You", "Computer"]);
    s.binderNames = [short(bm.name), short(bt.name)];
    s.order = [pockets(bm), pockets(bt)];
    s.log.push({ r: 1, P: null, text: `Round 1. ${s.opener === ME ? "You open." : "The computer opens."}` });
    R.advance(s);
    sel = null; lastTs = 0; dismissed = null; busy = false;
    faceOf.clear();
    ui.binderPage = 0;
    ui.voidOpen = null;
    closeDialog();
    save();
    ctx.render();
    step();
  }
  function newContest() {
    s = null; sel = null; busy = false; dismissed = null;
    closeDialog();
    save();
    ctx.render();
  }
  function step() {
    if (!s) return;
    if (s.phase === "roundOver") return showRoundOver();
    if (s.phase === "contestOver") return showContestOver();
    if (s.turn === AI && !busy) {
      busy = true;
      ctx.render();
      const game = s;
      setTimeout(() => {
        busy = false;
        if (s !== game || s.phase !== "turn" || s.turn !== AI) return; // a new contest started meanwhile
        const before = s.ts;
        const m = ai.choose(s, AI);
        if (m) R.play(s, AI, m);
        else R.pass(s, AI);
        lastTs = before;
        save();
        ctx.render();
        step();
      }, 650);
    }
  }
  function resume() {
    if (!s) return;
    if (s.phase === "turn") step();
    else if (s.phase === "roundOver") showRoundOver();
    else showContestOver();
  }
  function nextRound() {
    if (!s || s.phase !== "roundOver") return;
    closeDialog();
    R.nextRound(s);
    s.log.push({ r: s.r, P: null, text: `Round ${s.r}. ${s.opener === ME ? "You open." : "The computer opens."}` });
    R.advance(s);
    lastTs = 0; dismissed = null;
    save();
    ctx.render();
    step();
  }
  const myTurn = () => !!s && s.phase === "turn" && s.turn === ME && !busy;
  const myMoves = () => (myTurn() ? R.legalMoves(s, ME) : []);
  function status() {
    if (!s) return "Choose your binder and the computer's";
    const score = `you ${s.p[ME].wins}–${s.p[AI].wins} computer`;
    if (s.phase === "contestOver") return `Contest over · ${s.winner === null ? "a draw" : s.winner === ME ? "you won" : "the computer won"} · ${score}`;
    if (s.phase === "roundOver") return `Round ${s.r} over · ${score}`;
    const t = s.turn === ME ? (s.extras.length ? "your turn, one more card" : "your turn") : busy ? "the computer is thinking…" : "the computer's turn";
    return `Round ${s.r} of 3 · ${score} · ${t}`;
  }

  // ---------------------------------------------------------------- playing a card
  const keyOf = (pk) => JSON.stringify(pk);
  const matches = (m, picks) => picks.every((pk, k) => m.picks[k] && keyOf(m.picks[k]) === keyOf(pk));
  const faceShown = (id) => (R.C[id]?.meta ? "meta" : faceOf.get(id) || (ui.binderSide === "force" ? "force" : "permanence"));
  function flash(t) {
    flashMsg = t;
    ctx.render();
    clearTimeout(flashTimer);
    flashTimer = setTimeout(() => { flashMsg = ""; if (ctx.active()) ctx.render(); }, 2400);
  }
  function clickCard(id) {
    if (!s || s.phase !== "turn") return;
    if (s.turn !== ME || busy) return flash("It's the computer's turn.");
    const ms = myMoves().filter((m) => m.id === id);
    if (!ms.length) return flash(`${R.C[id].name} has no legal play right now.`);
    ctx.hidePreview();
    sel = { id, face: null, moves: ms, picks: [], options: null, note: "" };
    if (R.C[id].meta) return chooseFace("meta");
    const showing = faceShown(id) === "force" ? "force" : "perm";
    if (ms.some((m) => m.face === showing)) return chooseFace(showing); // play the side showing
    sel.note = `Its ${showing === "force" ? "force" : "permanence"} side can't be played right now.`;
    ctx.render();
  }
  function chooseFace(f) {
    sel.face = f;
    sel.moves = sel.moves.filter((m) => m.face === f);
    next();
  }
  function next() {
    const rem = sel.moves.filter((m) => matches(m, sel.picks));
    if (!rem.length) { sel = null; ctx.render(); return; }
    const k = sel.picks.length;
    const done = rem.find((m) => m.picks.length === k);
    if (done && rem.every((m) => m.picks.length === k)) return commit(done);
    const seen = new Map();
    for (const m of rem) if (m.picks[k]) seen.set(keyOf(m.picks[k]), m.picks[k]);
    sel.options = [...seen.values()];
    if (sel.options.length === 1 && sel.options[0].k === "face") { sel.picks.push(sel.options[0]); return next(); }
    ctx.render();
  }
  function pick(pk) {
    if (!sel || !sel.options || !pk) return;
    sel.picks.push(pk);
    next();
  }
  function commit(m) {
    sel = null;
    R.play(s, ME, m);
    lastTs = 0;
    save();
    ctx.render();
    step();
  }
  const PICK_WORDS = {
    cell: "choose where it goes", perm: "choose a permanence", world: "choose a world", player: "choose a player",
    force: "choose a force in play", void: "choose a card from your void", obinder: "choose a card from the computer's binder", face: "choose which face to play",
  };
  function pickHint() {
    const d = R.C[sel.id];
    const k = sel.picks.length;
    const kind = sel.options[0].k;
    let what = PICK_WORDS[kind];
    if (sel.face === "perm" && k > 0) {
      if (d.name === "Snowfield") what = "choose one of your permanences to return";
      else if (d.name === "Bluff") what = kind === "perm" ? "choose one of your permanences to move" : "choose where it moves";
      else if (d.name === "Hanging Valley") what = "choose two of your permanences to swap";
    }
    const sub = sel.picks[0] && sel.picks[0].k === "void" ? R.C[sel.picks[0].card] : null;
    const name = sel.face === "force" ? d.fname : d.name;
    const text = sel.face === "force" ? d.ftext : sel.face === "meta" ? d.text : d.ptext;
    return h("span", { class: "msg" }, h("b", { text: name }), text ? h("em", { text: ` ${text}` }) : null, sub ? ` → ${sub.name}` : "", ` · ${upper(what)}.`);
  }

  // ---------------------------------------------------------------- what the table shows
  // After a round ends the engine clears the table; show it as it stood until the next round.
  function shown() {
    if (s.phase !== "turn" && s.ended) return Object.assign({}, s, { inst: s.ended.inst, worlds: s.ended.worlds, _v: null, calm: false });
    return s;
  }
  const forcesOn = (iid) => R.forces(T).filter((f) => f.t === iid || f.t2 === iid);
  const forcesOnWorld = (wid) => R.forces(T).filter((f) => f.w === wid || f.w2 === wid);
  function whereIs(id) {
    if (s.p[ME].binder.includes(id)) return "binder";
    if (Object.values(s.inst).some((i) => i.card === id && i.owner === ME)) return "table";
    if (s.p[ME].void.includes(id)) return "void";
    return "gone";
  }
  function lookup(iid) {
    if (!s || typeof iid !== "string" || iid[1] !== ":") return null;
    const kind = iid[0], rest = iid.slice(2);
    const named = (id, face, P) => (cardsById.has(id) ? { inst: { id, face, owner: SEAT[P], original: false }, label: P === ME ? "Your card" : "The computer's card" } : null);
    if (kind === "b") return named(rest, faceShown(rest), ME);
    if (kind === "i" || kind === "f") {
      const i = (T || s).inst[rest];
      return i ? named(i.card, kind === "f" ? "force" : "permanence", i.owner) : null;
    }
    if (kind === "v") {
      const [P, k] = rest.split(":").map(Number);
      const id = s.p[P]?.void[k];
      return id ? named(id, "permanence", P) : null;
    }
    return null;
  }

  function render() {
    if (!s) ui.binderOpen = true; // binders are chosen in the binder panel
    T = s ? shown() : null;
    renderBinder();
    renderTable();
    renderVoid();
    renderLog();
    if (!s || s.phase === "turn") closeDialog();
  }

  // ---- the binder
  function renderBinder() {
    const panel = $("#binderPanel");
    panel.replaceChildren();
    $("#main").classList.toggle("binder-open", ui.binderOpen);
    if (!ui.binderOpen) return;
    if (!s) return chooseBinders(panel);
    const playable = new Set(myMoves().map((m) => m.id));
    const counts = { binder: 0, table: 0, void: 0 };
    for (const id of s.order[ME]) { const w = whereIs(id); if (counts[w] !== undefined) counts[w]++; }
    buildAlbum(panel, {
      name: s.binderNames[ME],
      owner: "Your binder",
      slots: s.order[ME],
      keys: `${counts.binder} in the binder · ${counts.table} on the table · ${counts.void} in the void · click a card to play the side showing, ↻ flips one`,
      fillPocket(pocket, id) {
        const card = cardsById.get(id);
        const at = whereIs(id);
        if (at !== "binder") {
          const label = card.meta ? card.meta.name : faceShown(id) === "force" && card.force ? card.force.name : card.permanence.name;
          pocket.append(goneSleeve(label, at === "table" ? "on the table" : at === "void" ? "in the void" : "out of the binder"));
          return;
        }
        const node = renderFace(card, faceShown(id), { size: "full", inst: { iid: `b:${id}`, owner: SEAT[ME] } });
        node.dataset.card = id;
        if (s.phase === "turn" && !playable.has(id)) node.classList.add("unplayable");
        if (sel && sel.id === id) pocket.classList.add("sel");
        pocket.append(node);
        if (!card.meta) pocket.append(h("button", { class: "flip", "data-act": "flip", "data-card": id, title: "Flip this card", "aria-label": "Flip" }, "↻"));
      },
    });
  }
  function chooseBinders(panel) {
    panel.append(
      h("h2", { class: "binder-pick-title", text: "Play the computer" }),
      h("p", {
        class: "hint",
        text: "The page applies every card's rules and the computer plays the other seat. Best of three rounds, 10 cards a round; a world worth 3 world points wins the contest on the spot.",
      })
    );
    for (const [which, title] of [["mine", "Your binder"], ["theirs", "The computer's binder"]]) {
      panel.append(h("h3", { class: "binder-pick-sub", text: title }));
      const list = h("div", { class: "binder-list" });
      binders.forEach((b, k) => {
        const on = choice[which] === k;
        list.append(
          h(
            "button",
            { class: `binder-choice${on ? " on" : ""}`, "data-act": "cpu-choose", "data-which": which, "data-k": String(k), "aria-pressed": String(on) },
            h("strong", { text: short(b.name) }),
            h("span", { text: `${b.cards.length} cards · ${elementLine(b.cards)}` }),
            b.note ? h("small", { text: b.note }) : null
          )
        );
      });
      panel.append(list);
    }
    panel.append(h("div", { class: "cpu-start" }, h("button", { class: "primary", "data-act": "cpu-start" }, "Start the contest")));
  }

  // ---- the table: the computer's worlds, the scoreboard, your worlds
  function renderTable() {
    const table = $("#table");
    if (!s) {
      table.replaceChildren(
        h("section", { class: "area theirs cpu-area" }, h("div", { class: "eworlds own-p2" }, h("p", { class: "eempty", text: "The computer's worlds appear here." }))),
        h("div", { class: "scoreboard cpu" }, h("div", { class: "cpu-prompt" }, h("span", { class: "msg muted", text: "Choose your binder and the computer's on the right, then start the contest." }))),
        h("section", { class: "area mine cpu-area" }, h("div", { class: "eworlds own-p1" }, h("p", { class: "eempty", text: "Your worlds appear here." })))
      );
      return;
    }
    const sc = R.score(T), v = R.view(T);
    const picks = new Map();
    if (sel && sel.options) {
      sel.options.forEach((pk, i) => {
        if (pk.k === "perm") picks.set(`perm:${pk.id}`, i);
        else if (pk.k === "world") picks.set(`world:${pk.id}`, i);
        else if (pk.k === "cell") picks.set(`cell:${pk.w}:${pk.cell}`, i);
        else if (pk.k === "force") picks.set(`force:${pk.id}`, i);
      });
    }
    table.replaceChildren(area(AI, v, sc, picks), scoreboard(sc, picks), area(ME, v, sc, picks));
  }
  const pickAttr = (i) => (i === undefined ? null : String(i));
  function area(P, v, sc, picks) {
    const seat = SEAT[P];
    const box = h("section", { class: `area ${P === ME ? "mine" : "theirs"} area-${seat} cpu-area`, "aria-label": P === ME ? "Your worlds" : "The computer's worlds" });
    const row = h("div", { class: `eworlds own-${seat}` });
    const cellPicks = sel && sel.options ? sel.options.filter((o) => o.k === "cell") : [];
    for (const w of R.worldsOf(T, P)) row.append(world(w, P, v, sc, picks, cellPicks));
    const nw = picks.get("cell:new:0");
    if (P === ME && nw !== undefined) {
      row.append(
        h("div", { class: "eworld new" }, h("div", { class: "ewlabel" }, h("span", { text: "New world" })), h("div", { class: "egrid" }, h("div", { class: "cell guide pickable", "data-pick": pickAttr(nw), title: "Start a new world" })))
      );
    }
    if (!row.children.length) row.append(h("p", { class: "eempty", text: P === ME ? "Your worlds appear here." : "The computer's worlds appear here." }));
    box.append(row);
    return box;
  }
  function world(w, P, v, sc, picks, cellPicks) {
    const ws = sc[P].worlds.find((x) => x.id === w.id) || { k: 0 };
    const wk = picks.get(`world:${w.id}`);
    const wb = h("div", { class: `eworld${wk !== undefined ? " pickable" : ""}`, "data-wid": String(w.id), "data-pick": pickAttr(wk) });
    const label = h("div", { class: "ewlabel" }, h("span", { text: `World ${w.n}` }), h("span", { class: `pts${ws.k >= 2 ? " hot" : ""}`, text: `${ws.k} pt${ws.k === 1 ? "" : "s"}` }));
    for (const f of forcesOnWorld(w.id)) label.append(forceTag(f, picks, false));
    // a world shows only the rows and columns it fills, unless a card is being placed in it
    const full = cellPicks.some((o) => o.w === w.id);
    const occ = [0, 1, 2, 3].filter((c) => w.cells[c] !== null);
    const rows = full ? [0, 1] : [...new Set(occ.map((c) => c >> 1))].sort();
    const cols = full ? [0, 1] : [...new Set(occ.map((c) => c & 1))].sort();
    const g = h("div", { class: "egrid" });
    g.style.gridTemplateColumns = `repeat(${cols.length}, var(--cw))`;
    for (const r of rows) {
      for (const c of cols) {
        const cell = r * 2 + c;
        const iid = w.cells[cell];
        if (iid === null) {
          const ck = picks.get(`cell:${w.id}:${cell}`);
          g.append(h("div", { class: `cell guide${ck !== undefined ? " pickable" : ""}`, "data-pick": pickAttr(ck) }));
        } else g.append(permCell(T.inst[iid], v, picks));
      }
    }
    wb.append(label, g);
    return wb;
  }
  function permCell(i, v, picks) {
    const pk = picks.get(`perm:${i.id}`);
    const cell = h("div", { class: `cell${pk !== undefined ? " pickable" : ""}`, "data-pick": pickAttr(pk) });
    const tok = renderFace(cardsById.get(i.card), "permanence", { size: "token", inst: { iid: `i:${i.id}`, owner: SEAT[i.owner] } });
    if (v.blank[i.id]) tok.classList.add("blanked");
    if (lastTs && i.ts >= lastTs) tok.classList.add("lastplay");
    cell.append(tok);
    forcesOn(i.id).forEach((f, k) => {
      const m = renderFace(cardsById.get(f.card), "force", { size: "token", inst: { iid: `f:${f.id}`, owner: SEAT[f.owner] } });
      m.classList.add("mini");
      m.style.setProperty("--k", String(k));
      if (lastTs && f.ts >= lastTs) m.classList.add("lastplay");
      cell.append(m);
    });
    // its affinities right now, when an effect has changed them from what's printed
    const blank = !!v.blank[i.id];
    const now = v.tok[i.id] || [], printed = R.C[i.card].aff;
    if (blank || now.length !== printed.length || now.some((t, k) => t !== printed[k])) {
      const chips = h("div", { class: "echips", title: "Its affinities right now" });
      chips.innerHTML = blank || !now.length ? '<span class="none">no affinities</span>' : now.map(chipSvg).join("");
      cell.append(chips);
    }
    return cell;
  }
  function forceTag(f, picks, withWhere) {
    const d = R.C[f.card];
    let text = d.fname;
    if (withWhere) {
      let where = "everywhere";
      if (f.t) where = `on ${T.inst[f.t] ? R.C[T.inst[f.t].card].name : "?"}${f.t2 && T.inst[f.t2] ? ` and ${R.C[T.inst[f.t2].card].name}` : ""}`;
      else if (f.w) where = `on ${R.worldLabel(T, f.w, ME)}${f.w2 ? ` and ${R.worldLabel(T, f.w2, ME)}` : ""}`;
      else if (/^Your /.test(d.ftext)) where = f.owner === ME ? "your worlds" : "the computer's worlds";
      if (d.fname === "Whiteout") where = `until ${f.owner === ME ? "your" : "the computer's"} next turn`;
      text += ` · ${where}`;
    }
    const pk = picks.get(`force:${f.id}`);
    return h("span", { class: `etag own-${SEAT[f.owner]}${pk !== undefined ? " pickable" : ""}${lastTs && f.ts >= lastTs ? " fresh" : ""}`, "data-pick": pickAttr(pk), title: `${d.fname}: ${d.ftext}` }, text);
  }
  const stat = (label, value, cls = "", title = null) => h("div", { class: `ctr ${cls}`, title }, h("span", { class: "label", text: label }), h("span", { class: "val", text: value }));
  function voidPile(P) {
    const n = s.p[P].void.length, seat = SEAT[P];
    const pile = h("button", {
      class: `void-pile ${ui.voidOpen === seat ? "on" : ""} ${n ? "" : "empty"}`,
      "data-act": "cpu-void",
      "data-seat": seat,
      title: `${P === ME ? "Your" : "The computer's"} void: ${n} card${n === 1 ? "" : "s"}. Click to look.`,
    });
    pile.innerHTML = n
      ? '<svg class="pile" viewBox="0 0 16 20" width="14" height="18" aria-hidden="true"><rect x="5" y="1" width="10" height="14" rx="2"/><rect x="1" y="5" width="10" height="14" rx="2"/></svg>'
      : '<svg class="pile" viewBox="0 0 16 20" width="14" height="18" aria-hidden="true"><rect x="3" y="3" width="10" height="14" rx="2" stroke-dasharray="2 2"/></svg>';
    pile.append(h("span", { class: "label", text: "Void" }), h("span", { class: "val", text: String(n) }));
    return pile;
  }
  function scoreRow(P, sc) {
    const pl = s.p[P], seat = SEAT[P];
    const turn = s.phase === "turn" && s.turn === P;
    return h(
      "div",
      { class: `score-row ${P === ME ? "mine" : "theirs"} own-${seat} ${turn ? "active" : ""}` },
      h(
        "div",
        { class: "who-block" },
        h("button", { class: `who own-${seat}`, disabled: true }, P === ME ? "You" : "Computer"),
        h("span", { class: "you", text: s.binderNames[P] }),
        pl.passed ? h("span", { class: "badge passed", text: "passed" }) : turn ? h("span", { class: "badge turn", text: P === ME ? "your turn" : busy ? "thinking" : "to play" }) : null,
        pl.skip ? h("span", { class: "badge passed", text: "skips next turn" }) : null,
        h("span", { class: "muted small", text: `${pl.binder.length} left` })
      ),
      stat("Played", `${pl.played}/${s.cap}`, `played ${pl.played >= s.cap ? "full" : ""}`),
      stat("World pts", String(sc[P].pts)),
      stat("Tie-break", String(sc[P].tie), "", "Breaks a tie in world points: the most of any one element across all their permanences"),
      stat("Rounds", String(pl.wins)),
      voidPile(P)
    );
  }
  function shared() {
    let acts;
    if (s.phase !== "turn") acts = h("span", { class: "turn-acts muted small", text: s.phase === "contestOver" ? "Contest over" : "Round over" });
    else if (myTurn()) {
      acts = h(
        "span",
        { class: "turn-acts" },
        h("button", { "data-act": "cpu-pass", title: s.extras.length ? "End your turn" : "You're out for the rest of the round" }, s.extras.length ? "End turn" : "Pass for the round")
      );
    } else acts = h("span", { class: "turn-acts small own-p2", text: s.turn === ME ? "" : busy ? "Computer thinking…" : "Computer to play" });
    return h("div", { class: "shared" }, stat("Round", `${s.r}/3`), stat("Cap", String(s.cap), "", "Most cards each player can play this round"), acts);
  }
  function scoreboard(sc, picks) {
    const parts = [scoreRow(AI, sc), shared(), scoreRow(ME, sc)];
    const fs = R.forces(T);
    if (fs.length || s.calm) {
      const strip = h("div", { class: "cpu-inplay" }, h("span", { class: "label", text: "In play" }));
      if (s.calm) strip.append(h("span", { class: "etag warn", text: "Calm: no forces this round" }));
      for (const f of fs) strip.append(forceTag(f, picks, true));
      parts.push(strip);
    }
    parts.push(promptRow());
    return h("div", { class: "scoreboard cpu" }, ...parts);
  }
  function promptRow() {
    const row = h("div", { class: "cpu-prompt" });
    if (flashMsg) row.append(h("span", { class: "msg flash", text: flashMsg }));
    if (sel && !sel.face) {
      const d = R.C[sel.id];
      row.append(h("span", { class: "msg" }, h("b", { text: d.name }), `${sel.note ? ` · ${sel.note}` : ""} · Play it as`));
      for (const f of [...new Set(sel.moves.map((m) => m.face))]) {
        row.append(h("button", { class: "primary", "data-act": "cpu-face", "data-face": f }, f === "perm" ? `the permanence, ${d.name}` : `the force, ${d.fname}`));
      }
      row.append(h("button", { class: "quiet", "data-act": "cpu-cancel", title: "Esc" }, "Cancel"));
    } else if (sel && sel.options) {
      row.append(pickHint());
      sel.options.forEach((pk, i) => {
        if (["player", "void", "obinder", "face", "force"].includes(pk.k) || sel.options.length <= 12 || pk.w === "new") {
          row.append(h("button", { "data-pick": String(i) }, upper(R.describePick(s, pk, ME))));
        }
      });
      row.append(h("button", { class: "quiet", "data-act": "cpu-cancel", title: "Esc" }, "Cancel"));
    } else if (s.phase === "roundOver") {
      row.append(h("span", { class: "msg muted", text: `Round ${s.r} is over.` }), h("button", { class: "primary", "data-act": "cpu-next-round" }, "Next round"));
    } else if (s.phase === "contestOver") {
      row.append(h("span", { class: "msg muted", text: "The contest is over." }), h("button", { "data-act": "cpu-rematch" }, "Rematch"), h("button", { class: "primary", "data-act": "cpu-new" }, "New contest"));
    } else if (myTurn()) {
      row.append(
        h("span", {
          class: "msg muted",
          text: s.extras.length ? `You may play another card${s.extras.includes("any") ? "" : " (a fire card)"}.` : "Your turn: click a card in your binder to play the side showing.",
        })
      );
    } else if (!flashMsg) row.append(h("span", { class: "msg muted", text: "The computer is playing…" }));
    return row;
  }

  // ---- the void and the log, in the dock
  function renderVoid() {
    const pop = $("#voidPanel");
    pop.replaceChildren();
    pop.hidden = !ui.voidOpen || !s;
    if (pop.hidden) return;
    const P = ui.voidOpen === SEAT[ME] ? ME : AI;
    const ids = s.p[P].void;
    pop.append(
      h(
        "div",
        { class: "pop-head" },
        h("strong", { text: P === ME ? "Your void" : "The computer's void" }),
        h("span", { class: "muted", text: `${ids.length} card${ids.length === 1 ? "" : "s"} · both players see it` }),
        h("button", { "data-act": "close-void", class: "icon quiet", title: "Close", "aria-label": "Close" }, "×")
      )
    );
    const list = h("div", { class: "void-list" });
    ids.forEach((id, k) => list.append(renderFace(cardsById.get(id), "permanence", { size: "token", inst: { iid: `v:${P}:${k}`, owner: SEAT[P] } })));
    if (!ids.length) list.append(h("p", { class: "hint", text: "Empty." }));
    pop.append(list);
  }
  function renderLog() {
    const panel = $("#logPanel");
    panel.hidden = !ui.logOpen;
    if (!ui.logOpen) return;
    panel.replaceChildren(h("div", { class: "pop-head" }, h("strong", { text: "Log" }), h("button", { "data-act": "toggle-log", class: "icon quiet", title: "Close", "aria-label": "Close" }, "×")));
    const list = h("ol", { class: "log-list" });
    for (const l of s ? s.log : []) list.append(h("li", { class: l.P === ME || l.P === AI ? `own-${SEAT[l.P]}` : "sys", text: l.text }));
    if (!s) list.append(h("li", { class: "sys", text: "No contest yet." }));
    panel.append(list);
    list.scrollTop = list.scrollHeight;
  }

  // ---- round and contest summaries
  function dialog(title, body, actions) {
    const o = $("#overlay");
    o.replaceChildren(h("div", { class: "dialog", role: "dialog", "aria-modal": "true", "aria-label": title }, h("h2", { text: title }), ...body, h("div", { class: "actions" }, ...actions)));
    o.hidden = false;
  }
  function closeDialog() {
    const o = $("#overlay");
    o.hidden = true;
    o.replaceChildren();
  }
  const look = () => h("button", { "data-act": "cpu-look" }, "Look at the table");
  function showRoundOver() {
    if (!ctx.active() || dismissed === `round:${s.rounds.length}`) return;
    const rec = s.rounds[s.rounds.length - 1];
    const head = rec.winner === null ? `Round ${rec.r} is a draw` : rec.winner === ME ? `You win round ${rec.r}` : `The computer wins round ${rec.r}`;
    const tbl = h("table", {}, h("tr", {}, h("th", {}), h("th", { text: "World points" }), h("th", { text: "Tie-break" }), h("th", { text: "Worlds" })));
    for (const P of [ME, AI]) {
      const r = rec.score[P];
      tbl.append(h("tr", {}, h("td", { text: P === ME ? "You" : "Computer" }), h("td", { text: String(r.pts) }), h("td", { text: String(r.tie) }), h("td", { text: r.worlds.map((w) => `${w.cards} card${w.cards > 1 ? "s" : ""}: ${w.k}`).join(" · ") || "none" })));
    }
    dialog(head, [h("p", { text: `Decided by ${rec.why}. Rounds won: you ${s.p[ME].wins}, the computer ${s.p[AI].wins}.` }), tbl], [look(), h("button", { class: "primary", "data-act": "cpu-next-round" }, "Next round")]);
  }
  function showContestOver() {
    if (!ctx.active() || dismissed === "contest") return;
    const head = s.winner === null ? "The contest is a draw" : s.winner === ME ? "You win the contest" : "The computer wins the contest";
    const why = s.why === "3-point world" ? "with a world worth 3 world points" : s.why === "Cradle" ? "with Cradle (3 of each affinity)" : `on rounds, ${s.p[ME].wins}–${s.p[AI].wins}`;
    const tbl = h("table", {}, h("tr", {}, h("th", { text: "Round" }), h("th", { text: "Winner" }), h("th", { text: "How" }), h("th", { text: "You" }), h("th", { text: "Computer" })));
    const pts = (x) => `${x.pts} point${x.pts === 1 ? "" : "s"}, tie ${x.tie}`;
    for (const r of s.rounds) tbl.append(h("tr", {}, h("td", { text: String(r.r) }), h("td", { text: r.winner === null ? "draw" : r.winner === ME ? "you" : "computer" }), h("td", { text: r.why }), h("td", { text: pts(r.score[0]) }), h("td", { text: pts(r.score[1]) })));
    dialog(head, [h("p", { text: `Won ${why}.` }), tbl], [look(), h("button", { "data-act": "cpu-rematch" }, "Rematch"), h("button", { class: "primary", "data-act": "cpu-new" }, "New contest")]);
  }

  // ---------------------------------------------------------------- input
  function click(e) {
    const pk = e.target.closest("[data-pick]");
    if (pk && sel && sel.options) { pick(sel.options[Number(pk.dataset.pick)]); return true; }
    const btn = e.target.closest("[data-act]");
    if (btn) {
      const d = btn.dataset;
      switch (d.act) {
        case "cpu-choose":
          choice[d.which] = Number(d.k);
          store.set("tfc:cpu:choice", choice);
          ctx.render();
          return true;
        case "cpu-start":
        case "cpu-rematch":
          start();
          return true;
        case "cpu-new":
          newContest();
          return true;
        case "reset":
          if (!s || s.phase === "contestOver" || confirm("End this contest and choose binders again?")) newContest();
          return true;
        case "cpu-face":
          if (sel) chooseFace(d.face);
          return true;
        case "cpu-cancel":
          sel = null;
          ctx.render();
          return true;
        case "cpu-pass":
          if (myTurn()) { sel = null; R.pass(s, ME); save(); ctx.render(); step(); }
          return true;
        case "cpu-next-round":
          nextRound();
          return true;
        case "cpu-look":
          dismissed = s.phase === "contestOver" ? "contest" : `round:${s.rounds.length}`;
          closeDialog();
          return true;
        case "cpu-void":
          ui.voidOpen = ui.voidOpen === d.seat ? null : d.seat;
          ctx.render();
          return true;
        case "binder-faces":
          ui.binderSide = d.face;
          faceOf.clear();
          renderBinder();
          return true;
        case "binder-page":
          ui.binderPage = Number(d.page);
          renderBinder();
          return true;
        case "flip":
          faceOf.set(d.card, faceShown(d.card) === "force" ? "permanence" : "force");
          renderBinder();
          return true;
      }
      return false; // the binder, log and opponent buttons are the table's
    }
    const card = e.target.closest("#binderPanel .pocket .card[data-card]");
    if (card) { clickCard(card.dataset.card); return true; }
    return false;
  }
  function key(k) {
    if (k === "escape") { if (sel) { sel = null; ctx.render(); } return; }
    if (!s || !$("#overlay").hidden) return;
    if (k === "f") {
      ui.binderSide = ui.binderSide === "force" ? "permanence" : "force";
      faceOf.clear();
      renderBinder();
    } else if (k === "arrowright" || k === "arrowleft") {
      ui.binderPage += k === "arrowright" ? 1 : -1;
      renderBinder();
    }
  }

  return { render, click, key, lookup, status, resume };
}
