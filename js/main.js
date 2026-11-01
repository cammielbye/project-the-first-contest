import { SEATS, GRID, other, cellKey, initialState, apply, findInst } from "./state.js";
import { renderFace, otherFace, setFaceArt } from "./cards.js";
import { createNet, peerOptionsFromUrl } from "./net.js";

// ---- where we are ----------------------------------------------------------
const params = new URLSearchParams(location.search);
const room = (params.get("room") || "").toLowerCase().replace(/[^a-z0-9]/g, "") || null;

const store = {
  get(k, d) {
    try {
      const v = localStorage.getItem(k);
      return v == null ? d : JSON.parse(v);
    } catch {
      return d;
    }
  },
  set(k, v) {
    try {
      localStorage.setItem(k, JSON.stringify(v));
    } catch {}
  },
  del(k) {
    try {
      localStorage.removeItem(k);
    } catch {}
  },
};

const mode = !room ? "solo" : store.get(`tfc:host:${room}`, false) ? "host" : "guest";
const ns = room ? `tfc:${room}` : "tfc:solo";
let mySeat = mode === "guest" ? "p2" : mode === "host" ? "p1" : store.get("tfc:solo:seat", "p1");
const managesSeat = (seat) => mode === "solo" || seat === mySeat;

// ---- data ------------------------------------------------------------------
let cardsById = new Map();
let cardOrder = new Map(); // id -> position in the pool, for sorting binders
let binders = [];
let state = null;
const privates = {}; // seat -> { binderId, binderName, cards: [inst] }
const ui = {
  binderOpen: store.get("tfc:ui:binderOpen", true),
  logOpen: false,
  selected: null, // { from: "binder"|"table"|"void", iid }
  voidOpen: null, // seat whose void is shown
  hover: null, // iid under the pointer
};
let net = null;
let link = { kind: mode === "solo" ? "solo" : "starting" };

// ---- persistence -------------------------------------------------------------
function saveState() {
  if (mode !== "guest") store.set(`${ns}:state`, state);
}
function savePrivate(seat) {
  store.set(`${ns}:private:${seat}`, privates[seat] || null);
}
function loadPrivates() {
  for (const seat of SEATS) {
    if (!managesSeat(seat)) continue;
    const p = store.get(`${ns}:private:${seat}`, null);
    if (p && Array.isArray(p.cards) && p.cards.every((c) => typeof c.id === "string")) privates[seat] = p;
  }
}

// ---- actions -----------------------------------------------------------------
function dispatch(action) {
  action.seat = action.seat || mySeat;
  if (mode === "guest") {
    if (!net || !net.isOpen()) {
      toast("Not connected to the host yet.");
      return false;
    }
    net.send({ type: "action", action });
    return true;
  }
  hostApply(action);
  return true;
}

function hostApply(action) {
  const { state: next, effects } = apply(state, action, cardsById);
  if (next === state) return;
  state = next;
  saveState();
  for (const e of effects) handleEffect(e);
  if (net && net.isOpen()) net.send({ type: "state", state, effects });
  render();
}

function handleEffect(e) {
  if (e.kind === "clearPrivate") {
    for (const seat of SEATS) {
      if (!managesSeat(seat)) continue;
      delete privates[seat];
      savePrivate(seat);
    }
    ui.selected = null;
    ui.voidOpen = null;
    ui.binderOpen = true;
  } else if (e.kind === "toBinder" && managesSeat(e.seat) && privates[e.seat]) {
    const inst = { ...e.inst, face: e.inst.face === "meta" ? "meta" : "permanence" };
    privates[e.seat].cards.push(inst);
    sortBinder(privates[e.seat].cards);
    savePrivate(e.seat);
  }
}

function onNetMessage(msg) {
  if (!msg || typeof msg !== "object") return;
  if (mode === "host") {
    if (msg.type === "_linked") {
      net.send({ type: "state", state, effects: [] });
    } else if (msg.type === "hello") {
      if (msg.name) hostApply({ seat: "p2", type: "setName", name: msg.name });
      net.send({ type: "state", state, effects: [] });
    } else if (msg.type === "action" && msg.action && typeof msg.action === "object") {
      hostApply({ ...msg.action, seat: "p2" });
    }
  } else if (mode === "guest") {
    if (msg.type === "_linked") {
      net.send({ type: "hello", name: store.get("tfc:name", "") });
    } else if (msg.type === "state" && msg.state && msg.state.v === 3) {
      state = msg.state;
      for (const e of msg.effects || []) handleEffect(e);
      render();
    } else if (msg.type === "busy") {
      link = { kind: "full" };
      render();
    }
  }
}

function onNetStatus(s) {
  link = s;
  renderTopbar();
}

// ---- player intents ----------------------------------------------------------------
const newIid = (seat, id) => `${seat}-${id}-${Math.random().toString(36).slice(2, 7)}`;
const sortBinder = (cards) => cards.sort((a, b) => (cardOrder.get(a.id) ?? 1e6) - (cardOrder.get(b.id) ?? 1e6));

function chooseBinder(binderId) {
  const b = binders.find((x) => x.id === binderId);
  if (!b) return;
  if (mode === "guest" && (!net || !net.isOpen())) return toast("Not connected to the host yet.");
  const originals = new Set((b.originals || []).map(String));
  const cards = sortBinder(
    [...new Set(b.cards.map(String))]
      .filter((id) => cardsById.has(id))
      .map((id) => ({
        iid: newIid(mySeat, id),
        id,
        face: cardsById.get(id).meta ? "meta" : "permanence",
        owner: mySeat,
        original: originals.has(id),
      }))
  );
  privates[mySeat] = { binderId: b.id, binderName: b.name, cards };
  savePrivate(mySeat);
  dispatch({ type: "chooseBinder", count: cards.length });
  render();
}

function placeFromBinder(iid, to) {
  const priv = privates[mySeat];
  if (!priv) return;
  const idx = priv.cards.findIndex((c) => c.iid === iid);
  if (idx === -1) return;
  if (mode === "guest" && (!net || !net.isOpen())) return toast("Not connected to the host yet.");
  const [inst] = priv.cards.splice(idx, 1);
  savePrivate(mySeat);
  dispatch({ type: "place", inst, to });
}

function dropOn(sel, to) {
  if (!sel) return;
  if (sel.from === "binder") placeFromBinder(sel.iid, to);
  else dispatch({ type: "move", iid: sel.iid, to });
  ui.selected = null;
  render();
}

// Undo a play: put one of your own cards from the table or a void back in your binder.
function returnToMyBinder(iid) {
  const found = lookup(iid);
  if (!found || found.from === "binder") return;
  const owner = found.inst.owner;
  if (owner !== mySeat) {
    const whose = state.players[owner].name;
    toast(
      mode === "solo"
        ? `That's ${whose}'s card. Switch seat to put it in their binder, or right-click it.`
        : `That's ${whose}'s card. Right-click it to return it to their binder.`
    );
    return;
  }
  if (!privates[mySeat]) return toast("Choose a binder first.");
  dispatch({ type: "toBinder", iid });
}

function flipCard(from, iid) {
  if (from === "binder") {
    const inst = privates[mySeat]?.cards.find((c) => c.iid === iid);
    if (!inst || inst.face === "meta") return;
    inst.face = otherFace(inst.face);
    savePrivate(mySeat);
    render();
  } else {
    dispatch({ type: "flip", iid });
  }
}

function setAllBinderFaces(face) {
  const priv = privates[mySeat];
  if (!priv) return;
  for (const c of priv.cards) if (c.face !== "meta") c.face = face;
  savePrivate(mySeat);
  render();
}

function resetGame() {
  if (!confirm("Reset the game for both players? The table, voids and counters are cleared, and both players choose a binder again.")) return;
  dispatch({ type: "reset" });
}

function renameSeat(seat) {
  const current = state.players[seat].name;
  const n = prompt("Name", current);
  if (!n || !n.trim()) return;
  if (mode !== "solo") store.set("tfc:name", n.trim());
  dispatch({ type: "setName", seat, name: n.trim() });
}

function hostContest() {
  const alphabet = "abcdefghjkmnpqrstuvwxyz23456789";
  let code = "";
  for (let i = 0; i < 6; i++) code += alphabet[Math.floor(Math.random() * alphabet.length)];
  store.set(`tfc:host:${code}`, true);
  if (!store.get("tfc:name", "")) {
    const n = prompt("Your name for the contest", "");
    if (n && n.trim()) store.set("tfc:name", n.trim());
  }
  const p = new URLSearchParams(params);
  p.set("room", code);
  location.search = p.toString();
}

function leaveRoom() {
  const p = new URLSearchParams(params);
  p.delete("room");
  const q = p.toString();
  location.href = location.pathname + (q ? `?${q}` : "");
}

function inviteLink() {
  const p = new URLSearchParams(params);
  p.set("room", room);
  return `${location.origin}${location.pathname}?${p.toString()}`;
}

async function copyInvite() {
  const url = inviteLink();
  try {
    await navigator.clipboard.writeText(url);
    toast("Invite link copied. Paste it in Discord.");
  } catch {
    prompt("Copy this link and send it to your friend:", url);
  }
}

// ---- lookups ----------------------------------------------------------------------
function lookup(iid) {
  for (const seat of SEATS) {
    const inst = privates[seat]?.cards.find((c) => c.iid === iid);
    if (inst) return { from: "binder", inst };
  }
  const loc = findInst(state, iid);
  if (loc) return { from: loc.where, inst: loc.inst };
  return null;
}

// ---- rendering ----------------------------------------------------------------------
const $ = (sel) => document.querySelector(sel);
const plural = (n, word) => `${n} ${word}${n === 1 ? "" : "s"}`;
const h = (tag, attrs = {}, ...kids) => {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v == null || v === false) continue;
    if (k === "class") n.className = v;
    else if (k === "text") n.textContent = v;
    else if (k.startsWith("data-")) n.setAttribute(k, v);
    else if (k === "title") n.title = v;
    else n.setAttribute(k, v === true ? "" : v);
  }
  for (const kid of kids.flat()) if (kid != null) n.append(kid);
  return n;
};

function render() {
  if (!state) return;
  if (!privates[mySeat] && !state.players[mySeat].binderChosen) ui.binderOpen = true;
  document.body.classList.toggle("selecting", !!ui.selected);
  $("#main").classList.toggle("dock-open", !!(ui.voidOpen || ui.logOpen));
  renderTopbar();
  renderBinder();
  renderTable();
  renderVoid();
  renderLog();
  layout();
}

function linkText() {
  const opp = state ? state.players[other(mySeat)].name : "your friend";
  switch (link.kind) {
    case "solo":
      return "Solo: you play both seats";
    case "starting":
      return "Starting…";
    case "waiting":
      return "Waiting for your friend to open the link";
    case "linked":
      return mode === "host" ? `${opp} is connected` : "Connected";
    case "unlinked":
      return mode === "host" ? `${opp} disconnected; waiting` : "Disconnected; reconnecting…";
    case "connecting":
      return "Connecting…";
    case "host-missing":
      return "Can't find the host yet; retrying…";
    case "busy-id":
      return "Reopening the room…";
    case "broker-lost":
      return "Lost the connection broker; retrying…";
    case "full":
      return "This contest already has two players";
    case "error":
      return `Connection problem: ${link.message}`;
    default:
      return link.kind;
  }
}

function renderTopbar() {
  const bar = $("#topbar");
  if (!state) return;
  bar.replaceChildren();
  bar.append(h("div", { class: "brand" }, h("span", { text: "The First Contest" }), h("small", { text: "playtest table" })));

  const conn = h("div", { class: `conn conn-${link.kind}` });
  conn.append(h("span", { class: "dot" }));
  if (room) conn.append(h("span", { class: "room", text: `Room ${room}` }));
  conn.append(h("span", { class: "status", text: linkText() }));
  if (mode === "solo") {
    conn.append(
      h("button", { "data-act": "switch-seat", title: `Play as ${state.players[other(mySeat)].name}` }, "Switch seat"),
      h("button", { "data-act": "host", class: "primary" }, "Host a contest")
    );
  } else {
    if (mode === "host") conn.append(h("button", { "data-act": "copy-invite", class: "primary" }, "Copy invite link"));
    conn.append(h("button", { "data-act": "leave" }, "Leave"));
  }
  bar.append(conn);

  bar.append(
    h(
      "div",
      { class: "group" },
      h("span", { class: "label", text: "Round" }),
      h("button", { "data-act": "round", "data-delta": "-1", class: "icon", title: "Previous round" }, "−"),
      h("span", { class: "big", text: String(state.round) }),
      h("button", { "data-act": "round", "data-delta": "1", class: "icon", title: "Next round" }, "+")
    )
  );

  const turnName = state.turn ? state.players[state.turn].name : "nobody yet";
  bar.append(
    h(
      "div",
      { class: "group" },
      h("span", { class: "label", text: "Turn" }),
      h("span", { class: `turn-name ${state.turn ? `own-${state.turn}` : ""}`, text: turnName }),
      h("button", { "data-act": "opener", title: "Pick who opens at random" }, "Random opener"),
      h("button", { "data-act": "end-turn" }, "End turn"),
      h("button", { "data-act": "pass" }, "Pass")
    )
  );

  bar.append(
    h(
      "div",
      { class: "group right" },
      h("button", { "data-act": "toggle-binder", class: ui.binderOpen ? "on" : "", title: "Open or close your binder (B)" }, ui.binderOpen ? "Close binder" : "Open binder"),
      h("button", { "data-act": "toggle-log", class: ui.logOpen ? "on" : "", title: "Show the action log (L)" }, "Log"),
      h("button", { "data-act": "reset", class: "danger" }, "Reset game")
    )
  );
}

function renderBinder() {
  const panel = $("#binderPanel");
  panel.replaceChildren();
  $("#main").classList.toggle("binder-open", ui.binderOpen);
  if (!ui.binderOpen) return;

  const priv = privates[mySeat];
  const who = state.players[mySeat].name;

  if (!priv) {
    panel.append(h("h2", { text: `Choose a binder for ${who}` }));
    if (state.players[mySeat].binderChosen) {
      panel.append(
        h("p", {
          class: "hint",
          text: "The table says you already chose a binder, but this browser doesn't have it (another browser or cleared storage). Reset the game to choose again.",
        })
      );
    }
    const list = h("div", { class: "binder-list" });
    for (const b of binders) {
      list.append(
        h(
          "button",
          { class: "binder-choice", "data-act": "choose-binder", "data-binder": b.id },
          h("strong", { text: b.name }),
          h("span", { text: `${b.cards.length} cards` }),
          b.note ? h("small", { text: b.note }) : null
        )
      );
    }
    panel.append(list);
    return;
  }

  const head = h(
    "div",
    { class: "binder-head" },
    h("h2", { text: `${who}'s binder` }),
    h("span", { class: "muted", text: `${priv.binderName} · ${plural(priv.cards.length, "card")} left` }),
    h(
      "div",
      { class: "seg" },
      h("span", { class: "label", text: "Show" }),
      h("button", { "data-act": "binder-faces", "data-face": "permanence" }, "Permanence"),
      h("button", { "data-act": "binder-faces", "data-face": "force" }, "Force")
    )
  );
  panel.append(head);
  panel.append(
    h("p", {
      class: "hint",
      text: "Click a card, then click a spot on the table (or drag it there). It goes down on the face you see. ↻ flips it. Made a mistake? Drag your card from the table back here.",
    })
  );

  const grid = h("div", { class: "binder-grid" });
  for (const inst of priv.cards) {
    const card = cardsById.get(inst.id);
    if (!card) continue;
    const face = renderFace(card, inst.face, { size: "full", inst });
    face.dataset.from = "binder";
    face.draggable = true;
    if (ui.selected?.iid === inst.iid) face.classList.add("selected");
    const flip = card.meta ? null : h("button", { class: "flip", "data-act": "flip", "data-from": "binder", "data-iid": inst.iid, title: "Flip (F)" }, "↻");
    const wrap = h("div", { class: "binder-slot" }, face, flip);
    grid.append(wrap);
  }
  if (!priv.cards.length) grid.append(h("p", { class: "hint", text: "Your binder is empty." }));
  panel.append(grid);
}

function areaHeader(seat) {
  const p = state.players[seat];
  const mine = seat === mySeat;
  const counter = (field, label) =>
    h(
      "div",
      { class: "counter" },
      h("span", { class: "label", text: label }),
      h("button", { "data-act": "counter", "data-target": seat, "data-field": field, "data-delta": "-1", class: "icon" }, "−"),
      h("span", { class: "big", text: String(p[field]) }),
      h("button", { "data-act": "counter", "data-target": seat, "data-field": field, "data-delta": "1", class: "icon" }, "+")
    );
  const canRename = mode === "solo" || mine;
  return h(
    "div",
    { class: "area-head" },
    h(
      "button",
      { class: `who own-${seat}`, "data-act": canRename ? "rename" : null, "data-seat": seat, title: canRename ? "Rename" : null, disabled: !canRename },
      p.name
    ),
    h("span", { class: "muted", text: mine ? "(you)" : "" }),
    state.turn === seat ? h("span", { class: "badge turn", text: "to play" }) : null,
    p.passed ? h("span", { class: "badge passed", text: "passed" }) : null,
    h("span", { class: "muted", text: p.binderChosen ? `binder: ${plural(p.binderCount, "card")}` : "no binder chosen" }),
    h("span", { class: "spacer" }),
    counter("worldPoints", "World points"),
    counter("roundsWon", "Rounds won"),
    h("button", { "data-act": "open-void", "data-seat": seat, class: ui.voidOpen === seat ? "on" : "" }, `Void (${state.voids[seat].length})`)
  );
}

function tokenFor(inst, from) {
  const card = cardsById.get(inst.id) || { id: inst.id, no: null, rarity: "C", permanence: { name: `${inst.id} (not in pool)`, affinities: [], text: "" }, force: null };
  const t = renderFace(card, inst.face, { size: "token", inst });
  t.dataset.from = from;
  t.draggable = true;
  if (ui.selected?.iid === inst.iid) t.classList.add("selected");
  return t;
}

function renderTable() {
  const table = $("#table");
  table.replaceChildren();
  for (const seat of [other(mySeat), mySeat]) {
    const area = h("section", { class: `area ${seat === mySeat ? "mine" : "theirs"} area-${seat}`, "data-area": seat });
    area.append(areaHeader(seat));
    const grid = h("div", { class: "grid" });
    grid.style.setProperty("--cols", String(GRID.cols));
    for (let r = 0; r < GRID.rows; r++) {
      for (let c = 0; c < GRID.cols; c++) {
        const key = cellKey(r, c);
        const cell = h("div", { class: "cell", "data-area": seat, "data-key": key });
        const stack = state.table[seat][key] || [];
        stack.forEach((inst, i) => {
          const t = tokenFor(inst, "table");
          t.style.setProperty("--depth", i);
          cell.append(t);
        });
        if (stack.length > 1) cell.append(h("span", { class: "stack-count", text: String(stack.length) }));
        grid.append(cell);
      }
    }
    area.append(grid);
    table.append(area);
  }
}

function renderVoid() {
  const pop = $("#voidPanel");
  pop.replaceChildren();
  pop.hidden = !ui.voidOpen;
  if (!ui.voidOpen) return;
  const seat = ui.voidOpen;
  pop.append(
    h(
      "div",
      { class: "pop-head" },
      h("strong", { text: `${state.players[seat].name}'s void` }),
      h("span", { class: "muted", text: `${plural(state.voids[seat].length, "card")} · both players see it` }),
      h("button", { "data-act": "close-void", class: "icon", title: "Close" }, "×")
    )
  );
  const list = h("div", { class: "void-list" });
  for (const inst of state.voids[seat]) list.append(tokenFor(inst, "void"));
  if (!state.voids[seat].length) list.append(h("p", { class: "hint", text: "Empty." }));
  pop.append(list);
  pop.append(h("p", { class: "hint", text: "Drag a card out, or click it and then a spot on the table. Right-click for more." }));
}

function renderLog() {
  const panel = $("#logPanel");
  panel.hidden = !ui.logOpen;
  if (!ui.logOpen) return;
  panel.replaceChildren(
    h("div", { class: "pop-head" }, h("strong", { text: "Log" }), h("button", { "data-act": "toggle-log", class: "icon", title: "Close" }, "×"))
  );
  const list = h("ol", { class: "log-list" });
  for (const entry of state.log) list.append(h("li", { class: `own-${entry.seat}`, text: entry.text }));
  panel.append(list);
  list.scrollTop = list.scrollHeight;
}

// Size the table cells to fit the space they have.
function layout() {
  const table = $("#table");
  const grid = table.querySelector(".area .grid");
  if (!grid) return;
  const gap = 6;
  const w = grid.clientWidth;
  const hgt = grid.clientHeight;
  const byW = (w - gap * (GRID.cols - 1)) / GRID.cols;
  const byH = ((hgt - gap * (GRID.rows - 1) - 18) / GRID.rows) * (5 / 7);
  const cw = Math.max(40, Math.floor(Math.min(byW, byH)));
  table.style.setProperty("--cw", `${cw}px`);
  table.style.setProperty("--ts", String(cw / 320));
  table.style.setProperty("--gap", `${gap}px`);
}

// ---- preview and menus --------------------------------------------------------------
function showPreview(iid, x) {
  const found = lookup(iid);
  const pv = $("#preview");
  if (!found) {
    pv.hidden = true;
    return;
  }
  const card = cardsById.get(found.inst.id);
  if (!card) return;
  pv.replaceChildren(renderFace(card, found.inst.face, { size: "preview", inst: found.inst }));
  if (card.meta) {
    pv.append(h("div", { class: "pv-label", text: "Meta card: one face, playable by either player" }));
  } else {
    const back = renderFace(card, otherFace(found.inst.face), { size: "preview", inst: { ...found.inst, iid: "" } });
    back.classList.add("pv-other");
    pv.append(h("div", { class: "pv-label", text: "Other face" }), back);
  }
  const owner = state.players[found.inst.owner]?.name;
  pv.append(h("div", { class: "pv-label", text: `${owner}'s card${found.inst.original ? " · original" : " · copy"}` }));
  pv.classList.toggle("left", x > window.innerWidth / 2);
  pv.hidden = false;
}

function hidePreview() {
  $("#preview").hidden = true;
}

function openMenu(x, y, from, iid) {
  const menu = $("#menu");
  const found = lookup(iid);
  if (!found) return;
  const items = found.inst.face === "meta" ? [] : [["flip", "Flip  (F)"]];
  if (from !== "binder") {
    items.push(["select", "Move…  (click a spot)"]);
    if (from === "table") items.push(["to-void", `Send to ${state.players[found.inst.owner].name}'s void  (V)`]);
    items.push(["to-binder", `Return to ${state.players[found.inst.owner].name}'s binder  (R)`]);
  } else {
    items.push(["select", "Play…  (click a spot)"]);
  }
  menu.replaceChildren(...items.map(([act, text]) => h("button", { "data-menu": act, "data-from": from, "data-iid": iid }, text)));
  menu.style.left = `${Math.min(x, window.innerWidth - 240)}px`;
  menu.style.top = `${Math.min(y, window.innerHeight - 40 * items.length - 10)}px`;
  menu.hidden = false;
}

function closeMenu() {
  $("#menu").hidden = true;
}

function toast(text) {
  const t = $("#toast");
  t.textContent = text;
  t.hidden = false;
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => (t.hidden = true), 2600);
}

// ---- input ---------------------------------------------------------------------------------
function bindInput() {
  document.addEventListener("click", (e) => {
    const menuBtn = e.target.closest("[data-menu]");
    if (menuBtn) {
      const { menu: act, from, iid } = menuBtn.dataset;
      closeMenu();
      if (act === "flip") flipCard(from, iid);
      else if (act === "select") {
        ui.selected = { from, iid };
        render();
      } else if (act === "to-void") dispatch({ type: "toVoid", iid });
      else if (act === "to-binder") dispatch({ type: "toBinder", iid });
      return;
    }
    closeMenu();

    const btn = e.target.closest("[data-act]");
    if (btn) {
      const d = btn.dataset;
      switch (d.act) {
        case "switch-seat":
          mySeat = other(mySeat);
          store.set("tfc:solo:seat", mySeat);
          ui.selected = null;
          render();
          break;
        case "host":
          hostContest();
          break;
        case "copy-invite":
          copyInvite();
          break;
        case "leave":
          leaveRoom();
          break;
        case "round":
          dispatch({ type: "round", delta: Number(d.delta) });
          break;
        case "opener":
          dispatch({ type: "opener", pick: Math.random() < 0.5 ? "p1" : "p2" });
          break;
        case "end-turn":
          dispatch({ type: "endTurn" });
          break;
        case "pass":
          dispatch({ type: "pass" });
          break;
        case "toggle-binder":
          ui.binderOpen = !ui.binderOpen;
          store.set("tfc:ui:binderOpen", ui.binderOpen);
          render();
          break;
        case "toggle-log":
          ui.logOpen = !ui.logOpen;
          render();
          break;
        case "reset":
          resetGame();
          break;
        case "choose-binder":
          chooseBinder(d.binder);
          break;
        case "binder-faces":
          setAllBinderFaces(d.face);
          break;
        case "flip":
          flipCard(d.from, d.iid);
          break;
        case "rename":
          renameSeat(d.seat);
          break;
        case "counter":
          dispatch({ type: "counter", target: d.target, field: d.field, delta: Number(d.delta) });
          break;
        case "open-void":
          ui.voidOpen = ui.voidOpen === d.seat ? null : d.seat;
          render();
          break;
        case "close-void":
          ui.voidOpen = null;
          render();
          break;
      }
      return;
    }

    const cardEl = e.target.closest(".card[data-iid]");
    if (cardEl && cardEl.dataset.iid) {
      const { iid, from } = cardEl.dataset;
      // A card on the table that's already the target of a selection acts as its cell.
      if (ui.selected && from === "table" && ui.selected.iid !== iid) {
        const cell = cardEl.closest(".cell");
        dropOn(ui.selected, { area: cell.dataset.area, key: cell.dataset.key });
        return;
      }
      ui.selected = ui.selected?.iid === iid ? null : { from, iid };
      render();
      return;
    }

    const cell = e.target.closest(".cell");
    if (cell && ui.selected) {
      dropOn(ui.selected, { area: cell.dataset.area, key: cell.dataset.key });
      return;
    }
  });

  document.addEventListener("contextmenu", (e) => {
    const cardEl = e.target.closest(".card[data-iid]");
    if (!cardEl || !cardEl.dataset.iid) return;
    e.preventDefault();
    openMenu(e.clientX, e.clientY, cardEl.dataset.from, cardEl.dataset.iid);
  });

  // Hover preview.
  document.addEventListener("mouseover", (e) => {
    const cardEl = e.target.closest(".card[data-iid]");
    if (cardEl && cardEl.dataset.iid && !cardEl.closest("#preview")) {
      ui.hover = { iid: cardEl.dataset.iid, from: cardEl.dataset.from };
      showPreview(cardEl.dataset.iid, e.clientX);
    }
  });
  document.addEventListener("mouseout", (e) => {
    const cardEl = e.target.closest(".card[data-iid]");
    if (cardEl && !cardEl.contains(e.relatedTarget)) {
      ui.hover = null;
      hidePreview();
    }
  });

  // Drag and drop. A card from the table or a void can also be dragged back
  // onto your binder (the panel, or the Open binder button when it's closed).
  let drag = null; // { from, iid }
  const clearOver = () => document.querySelectorAll(".over, .drop-over").forEach((n) => n.classList.remove("over", "drop-over"));
  const binderTarget = (t) => t.closest("#binderPanel") || t.closest('[data-act="toggle-binder"]');

  document.addEventListener("dragstart", (e) => {
    const cardEl = e.target.closest(".card[data-iid]");
    if (!cardEl) return;
    drag = { from: cardEl.dataset.from, iid: cardEl.dataset.iid };
    e.dataTransfer.setData("application/x-tfc", JSON.stringify(drag));
    e.dataTransfer.effectAllowed = "move";
    hidePreview();
    document.body.classList.add("dragging");
    if (drag.from !== "binder") document.body.classList.add("dragging-back");
  });
  document.addEventListener("dragend", () => {
    drag = null;
    document.body.classList.remove("dragging", "dragging-back");
    clearOver();
  });
  document.addEventListener("dragover", (e) => {
    const cell = e.target.closest(".cell");
    const binder = drag && drag.from !== "binder" ? binderTarget(e.target) : null;
    const target = cell || binder;
    if (!target) return;
    e.preventDefault();
    document.querySelectorAll(".over, .drop-over").forEach((n) => n !== target && n.classList.remove("over", "drop-over"));
    target.classList.add(cell ? "over" : "drop-over");
  });
  document.addEventListener("drop", (e) => {
    const cell = e.target.closest(".cell");
    const binder = binderTarget(e.target);
    if (!cell && !binder) return;
    e.preventDefault();
    clearOver();
    let sel = drag;
    try {
      sel = JSON.parse(e.dataTransfer.getData("application/x-tfc"));
    } catch {}
    if (!sel) return;
    if (cell) dropOn(sel, { area: cell.dataset.area, key: cell.dataset.key });
    else if (sel.from !== "binder") returnToMyBinder(sel.iid);
  });

  document.addEventListener("keydown", (e) => {
    if (e.target.closest("input, textarea") || e.metaKey || e.ctrlKey || e.altKey) return;
    const k = e.key.toLowerCase();
    if (k === "escape") {
      ui.selected = null;
      closeMenu();
      render();
    } else if (k === "b") {
      ui.binderOpen = !ui.binderOpen;
      store.set("tfc:ui:binderOpen", ui.binderOpen);
      render();
    } else if (k === "l") {
      ui.logOpen = !ui.logOpen;
      render();
    } else if (ui.hover && k === "f") {
      flipCard(ui.hover.from, ui.hover.iid);
    } else if (ui.hover && k === "v" && ui.hover.from === "table") {
      dispatch({ type: "toVoid", iid: ui.hover.iid });
    } else if (ui.hover && k === "r" && ui.hover.from !== "binder") {
      dispatch({ type: "toBinder", iid: ui.hover.iid });
    }
  });

  window.addEventListener("resize", layout);
}

// ---- start -------------------------------------------------------------------------------------
async function init() {
  try {
    const [cardsJson, bindersJson, facesJson] = await Promise.all([
      fetch("data/cards.json", { cache: "no-cache" }).then((r) => r.json()),
      fetch("data/binders.json", { cache: "no-cache" }).then((r) => r.json()),
      fetch("data/card-faces.json", { cache: "no-cache" })
        .then((r) => (r.ok ? r.json() : null))
        .catch(() => null),
    ]);
    setFaceArt(facesJson?.faces);
    cardsById = new Map(cardsJson.cards.map((c) => [c.id, c]));
    cardOrder = new Map(cardsJson.cards.map((c, i) => [c.id, i]));
    binders = bindersJson.binders || [];
    $("#footer").textContent = `Cards synced ${new Date(cardsJson.syncedAt).toLocaleString()} · ${cardsJson.counts.cards} cards (${cardsJson.counts.meta} meta), ${cardsJson.counts.withForceFace} with both faces`;
  } catch (err) {
    document.body.textContent = `Couldn't load the card data: ${err}`;
    return;
  }

  loadPrivates();
  if (mode === "guest") {
    state = initialState({ p2: store.get("tfc:name", "") || undefined });
  } else {
    state = store.get(`${ns}:state`, null);
    if (!state || state.v !== 3) {
      state = initialState(mode === "host" ? { p1: store.get("tfc:name", "") || undefined } : {});
      saveState();
    }
  }
  if (mode === "guest" && !store.get("tfc:name", "")) {
    const n = prompt("Your name for the contest", "");
    if (n && n.trim()) store.set("tfc:name", n.trim());
  }

  bindInput();
  render();

  if (mode !== "solo") {
    net = createNet({ mode, room, peerOptions: peerOptionsFromUrl(params), onMessage: onNetMessage, onStatus: onNetStatus });
  }
}

init();
