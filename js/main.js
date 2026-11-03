import { SEATS, GRID, other, cellKey, initialState, apply, findInst, capFor, playedIn } from "./state.js";
import { renderFace, otherFace, setFaceArt } from "./cards.js";
import { createNet, peerOptionsFromUrl } from "./net.js";
import { createComputer } from "./computer.js";

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

// Who you play. A friend: the page only knows where cards are and you apply every effect by
// hand. The computer (a table without a room only): the rules engine applies every card and
// the computer plays the other seat (js/computer.js). ?vs=computer opens straight to it.
let cpu = null;
let opponent =
  mode !== "solo" ? "friend" : params.get("vs") === "computer" ? "computer" : params.get("vs") === "friend" ? "friend" : store.get("tfc:opponent", "friend");
const vsComputer = () => opponent === "computer" && !!cpu;

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
  binderPage: 0, // which two-page spread of the binder is open
  binderSide: "permanence", // the side the binder's tabs last turned every card to
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
    } else if (msg.type === "state" && msg.state && msg.state.v === 5) {
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

// A card dropped on a void pile goes to its owner's void. Straight from the
// binder, that's playing it (a force that happens once).
function playToVoid(iid) {
  const priv = privates[mySeat];
  if (!priv) return;
  const idx = priv.cards.findIndex((c) => c.iid === iid);
  if (idx === -1) return;
  if (mode === "guest" && (!net || !net.isOpen())) return toast("Not connected to the host yet.");
  const [inst] = priv.cards.splice(idx, 1);
  savePrivate(mySeat);
  dispatch({ type: "placeVoid", inst });
}

function sendToVoid(sel) {
  if (!sel) return;
  if (sel.from === "binder") playToVoid(sel.iid);
  else if (sel.from === "table") dispatch({ type: "toVoid", iid: sel.iid });
  ui.selected = null;
  render();
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
  dispatch({ type: "toBinder", iid, undo: true });
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
  p.delete("vs");
  p.set("room", code);
  location.search = p.toString();
}

function setOpponent(v) {
  if (mode !== "solo" || (v !== "friend" && v !== "computer") || v === opponent) return;
  opponent = v;
  store.set("tfc:opponent", v);
  const p = new URLSearchParams(location.search);
  if (v === "computer") p.set("vs", "computer");
  else p.delete("vs");
  const q = p.toString();
  history.replaceState(null, "", location.pathname + (q ? `?${q}` : "") + location.hash);
  ui.selected = null;
  ui.voidOpen = null;
  hidePreview();
  render();
  if (vsComputer()) cpu.resume();
}

function leaveRoom() {
  const p = new URLSearchParams(params);
  p.delete("room");
  const q = p.toString();
  location.href = location.pathname + (q ? `?${q}` : "");
}

function inviteLink() {
  const p = new URLSearchParams(params);
  p.delete("vs");
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
  document.body.classList.toggle("vs-computer", vsComputer());
  if (vsComputer()) {
    document.body.classList.remove("selecting");
    $("#main").classList.toggle("dock-open", !!(ui.voidOpen || ui.logOpen));
    renderTopbar();
    cpu.render();
    layout();
    return;
  }
  $("#overlay").hidden = true;
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
      return "Solo, both seats";
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

  if (mode === "solo") {
    const seg = h("div", { class: "seg", role: "group", "aria-label": "Opponent" });
    for (const [v, label, title] of [
      ["friend", "Friend", "Play a friend: the page knows where cards are, and you apply their effects by hand"],
      ["computer", "Computer", "Play the computer: the page applies every card's rules"],
    ]) {
      seg.append(h("button", { class: opponent === v ? "on" : "", "data-act": "opponent", "data-vs": v, title, "aria-pressed": String(opponent === v) }, label));
    }
    bar.append(seg);
  }

  const conn = h("div", { class: `conn conn-${vsComputer() ? "solo" : link.kind}` });
  conn.append(h("span", { class: "dot" }));
  if (vsComputer()) {
    conn.append(h("span", { class: "status", text: cpu.status() }));
  } else if (mode === "solo") {
    conn.append(
      h("span", { class: "status", text: linkText() }),
      h("button", { "data-act": "switch-seat", class: "quiet", title: `Play as ${state.players[other(mySeat)].name}` }, "Switch seat"),
      h("button", { "data-act": "host", class: "primary" }, "Host a contest")
    );
  } else {
    if (room) conn.append(h("span", { class: "room", text: room }));
    conn.append(h("span", { class: "status", text: linkText() }));
    if (mode === "host") conn.append(h("button", { "data-act": "copy-invite", class: "primary" }, "Copy invite link"));
    conn.append(h("button", { "data-act": "leave", class: "quiet" }, "Leave"));
  }
  bar.append(conn);

  bar.append(
    h(
      "div",
      { class: "group right" },
      h("button", { "data-act": "toggle-binder", class: ui.binderOpen ? "on" : "", title: "Open or close your binder (B)" }, "Binder"),
      h("button", { "data-act": "toggle-log", class: ui.logOpen ? "on" : "", title: "Show the action log (L)" }, "Log"),
      vsComputer()
        ? h("button", { "data-act": "reset", class: "quiet danger", title: "End this contest and choose binders again" }, "New contest")
        : h("button", { "data-act": "reset", class: "quiet danger", title: "Clear the table for both players" }, "Reset")
    )
  );
}

// The binder is an old leather album open flat: two pages of nine pockets. Every card keeps
// its pocket (the binder's order); a card that's out leaves an empty sleeve saying where it is.
const PER_PAGE = 9;
function binderSlots(priv) {
  const b = binders.find((x) => x.id === priv.binderId);
  const ids = b ? [...new Set(b.cards.map(String))].filter((id) => cardsById.has(id)) : priv.cards.map((c) => c.id);
  for (const c of priv.cards) if (!ids.includes(c.id)) ids.push(c.id); // anything else that came back
  return ids.sort((x, y) => (cardOrder.get(x) ?? 1e6) - (cardOrder.get(y) ?? 1e6));
}
function whereMine(id) {
  for (const area of SEATS) for (const stack of Object.values(state.table[area] || {})) if (stack.some((c) => c.id === id && c.owner === mySeat)) return "on the table";
  if ((state.voids[mySeat] || []).some((c) => c.id === id)) return "in the void";
  return "out of the binder";
}
function fitBinder() {
  const panel = $("#binderPanel");
  if (!panel || !ui.binderOpen) return;
  const w = panel.clientWidth - 28 - 30, hgt = panel.clientHeight - 110;
  const sc = Math.max(0.16, Math.min((w - 174) / 1920, (hgt - 160) / 1344, 0.5));
  panel.style.setProperty("--bs", sc.toFixed(3));
}
function spineSvg(hgt) {
  let d = "", holes = "";
  const n = Math.max(6, Math.round(hgt / 70));
  for (let k = 0; k <= n; k++) {
    const y = 20 + ((hgt - 40) * k) / n;
    holes += `<circle cx="15" cy="${y.toFixed(1)}" r="2.6" fill="#140a04"/>`;
    if (k < n) { const y2 = 20 + ((hgt - 40) * (k + 1)) / n; d += `M15 ${y.toFixed(1)} C4 ${((y + y2) / 2).toFixed(1)} 26 ${((y + y2) / 2).toFixed(1)} 15 ${y2.toFixed(1)} `; }
  }
  return `<svg viewBox="0 0 30 ${hgt}" preserveAspectRatio="none" aria-hidden="true">${holes}<path d="${d}" stroke="#1a0e06" stroke-width="3.2" fill="none" transform="translate(0.8 1)"/><path d="${d}" stroke="#b58a52" stroke-width="2.2" fill="none" stroke-linecap="round"/></svg>`;
}
function renderBinder() {
  const panel = $("#binderPanel");
  panel.replaceChildren();
  $("#main").classList.toggle("binder-open", ui.binderOpen);
  if (!ui.binderOpen) return;

  const priv = privates[mySeat];
  const who = state.players[mySeat].name;

  if (!priv) {
    panel.append(h("h2", { class: "binder-pick-title", text: `Choose a binder for ${who}` }));
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
          h("strong", { text: b.name.replace(/^Binder \w, /, "") }),
          h("span", { text: `${b.cards.length} cards` }),
          b.note ? h("small", { text: b.note }) : null
        )
      );
    }
    panel.append(list);
    return;
  }

  const slots = binderSlots(priv);
  const inBinder = new Map(priv.cards.map((c) => [c.id, c]));
  buildAlbum(panel, {
    name: priv.binderName.replace(/^Binder \w, /, ""),
    owner: `${who}'s binder`,
    slots,
    keys: `${priv.cards.length} of ${slots.length} in the binder · click or drag a card onto a world; it goes down on the face showing, ↻ flips one`,
    fillPocket(pocket, id) {
      const inst = inBinder.get(id);
      const card = cardsById.get(id);
      if (inst) {
        const face = renderFace(card, inst.face, { size: "full", inst });
        face.dataset.from = "binder";
        face.draggable = true;
        if (ui.selected?.iid === inst.iid) { face.classList.add("selected"); pocket.classList.add("sel"); }
        const flip = card.meta ? null : h("button", { class: "flip", "data-act": "flip", "data-from": "binder", "data-iid": inst.iid, title: "Flip this card (F)", "aria-label": "Flip" }, "↻");
        pocket.append(face);
        if (flip) pocket.append(flip);
      } else {
        const label = card.meta ? card.meta.name : ui.binderSide === "force" && card.force ? card.force.name : card.permanence.name;
        pocket.append(goneSleeve(label, whereMine(id)));
      }
    },
  });
}

// An empty sleeve, saying where its card went.
const goneSleeve = (label, where) => h("div", { class: "gone" }, h("span", {}, h("b", { text: label }), where));

// The album, for either opponent: two pages of nine pockets, page tabs on top, the
// permanence/force tabs down the right edge. fillPocket(pocket, id) fills one pocket.
function buildAlbum(panel, { name, owner, slots, keys, fillPocket }) {
  fitBinder();
  const spreads = Math.max(1, Math.ceil(slots.length / (2 * PER_PAGE)));
  ui.binderPage = Math.min(Math.max(0, ui.binderPage), spreads - 1);

  const leaf = (pg, which) => {
    const page = h("div", { class: `leaf ${which}` });
    page.append(h("div", { class: "phead" }, h("span", { text: which === "left" ? name : "" }), h("span", { text: which === "right" ? owner : "" })));
    const grid = h("div", { class: "pockets" });
    for (let k = 0; k < PER_PAGE; k++) {
      const id = slots[pg * PER_PAGE + k];
      const pocket = h("div", { class: "pocket" });
      if (!id) pocket.classList.add("blank");
      else fillPocket(pocket, id);
      grid.append(pocket);
    }
    page.append(grid, h("div", { class: `pfoot ${which}`, text: String(pg + 1) }));
    return page;
  };

  const cover = h("div", { class: "cover" });
  const sides = h("div", { class: "stabs" });
  for (const [f, label] of [["permanence", "Permanence side"], ["force", "Force side"]]) {
    sides.append(h("button", { class: ui.binderSide === f ? "on" : "", "data-act": "binder-faces", "data-face": f, title: `Turn every card to its ${f} face` }, label));
  }
  const tabs = h("div", { class: "ptabs" });
  for (let k = 0; k < spreads; k++) {
    tabs.append(h("button", { class: k === ui.binderPage ? "on" : "", "data-act": "binder-page", "data-page": String(k), title: `Pages ${2 * k + 1} and ${2 * k + 2}` }, `Pages ${2 * k + 1}–${2 * k + 2}`));
  }
  const pageH = Math.round(24 + 26 + 1344 * Number(panel.style.getPropertyValue("--bs") || 0.3) + 18 + 14 + 26);
  cover.append(sides, leaf(2 * ui.binderPage, "left"), h("div", { class: "spine" }), leaf(2 * ui.binderPage + 1, "right"), tabs);
  cover.querySelector(".spine").innerHTML = spineSvg(pageH);

  const nav = h(
    "div",
    { class: "bnav" },
    h("button", { "data-act": "binder-page", "data-page": String(ui.binderPage - 1), disabled: ui.binderPage === 0, title: "Previous pages (←)" }, "‹"),
    h("span", { text: `Pages ${2 * ui.binderPage + 1}–${2 * ui.binderPage + 2} of ${2 * spreads}` }),
    h("button", { "data-act": "binder-page", "data-page": String(ui.binderPage + 1), disabled: ui.binderPage >= spreads - 1, title: "Next pages (→)" }, "›"),
    h("span", { class: "keys", text: keys })
  );
  panel.append(h("div", { class: "album" }, cover, nav));
}

// ---- counters: a value with a small up and down arrow beside it ------------------
const svgTemplate = document.createElement("template");
const svg = (markup) => {
  svgTemplate.innerHTML = markup;
  return svgTemplate.content.firstElementChild;
};
const CHEVRON = (up) =>
  `<svg viewBox="0 0 10 6" width="10" height="6" aria-hidden="true"><path d="${up ? "M1 5 L5 1 L9 5" : "M1 1 L5 5 L9 1"}"/></svg>`;

function arrows(attrs, what) {
  const up = h("button", { class: "arr", ...attrs, "data-delta": "1", title: `Raise ${what}`, "aria-label": `Raise ${what}` });
  up.append(svg(CHEVRON(true)));
  const down = h("button", { class: "arr", ...attrs, "data-delta": "-1", title: `Lower ${what}`, "aria-label": `Lower ${what}` });
  down.append(svg(CHEVRON(false)));
  return h("span", { class: "arrows" }, up, down);
}

function counterEl(label, value, attrs, what, { cls = "", title = null } = {}) {
  return h(
    "div",
    { class: `ctr ${cls}`, title },
    h("span", { class: "label", text: label }),
    h("span", { class: "val", text: value }),
    arrows(attrs, what)
  );
}

function voidPile(seat) {
  const n = state.voids[seat].length;
  const pile = h(
    "button",
    {
      class: `void-pile ${ui.voidOpen === seat ? "on" : ""} ${n ? "" : "empty"}`,
      "data-act": "open-void",
      "data-seat": seat,
      "data-void": seat,
      title: `${state.players[seat].name}'s void: ${plural(n, "card")}. Click to look; drop a card here to send it to its owner's void.`,
    },
    svg(
      n
        ? '<svg class="pile" viewBox="0 0 16 20" width="14" height="18" aria-hidden="true"><rect x="5" y="1" width="10" height="14" rx="2"/><rect x="1" y="5" width="10" height="14" rx="2"/></svg>'
        : '<svg class="pile" viewBox="0 0 16 20" width="14" height="18" aria-hidden="true"><rect x="3" y="3" width="10" height="14" rx="2" stroke-dasharray="2 2"/></svg>'
    ),
    h("span", { class: "label", text: "Void" }),
    h("span", { class: "val", text: String(n) })
  );
  return pile;
}

function scoreRow(seat) {
  const p = state.players[seat];
  const mine = seat === mySeat;
  const n = playedIn(state, seat);
  const cap = capFor(state);
  const earlier = Object.keys(p.played)
    .map(Number)
    .filter((r) => r !== state.round && p.played[r] > 0)
    .sort((a, b) => a - b)
    .map((r) => `round ${r}: ${p.played[r]}`)
    .join(", ");
  const canRename = mode === "solo" || mine;
  const isTurn = state.turn === seat;

  return h(
    "div",
    { class: `score-row ${mine ? "mine" : "theirs"} own-${seat} ${isTurn ? "active" : ""}` },
    h(
      "div",
      { class: "who-block" },
      h(
        "button",
        { class: `who own-${seat}`, "data-act": canRename ? "rename" : null, "data-seat": seat, title: canRename ? "Rename" : null, disabled: !canRename },
        p.name
      ),
      mine ? h("span", { class: "you", text: "you" }) : null,
      p.passed ? h("span", { class: "badge passed", text: "passed" }) : null,
      h("span", {
        class: "muted small",
        text: p.binderChosen ? `${p.binderCount} left` : "no binder yet",
        title: p.binderChosen ? `${plural(p.binderCount, "card")} left in ${p.name}'s binder` : null,
      })
    ),
    counterEl("Played", `${n}/${cap}`, { "data-act": "played", "data-target": seat }, `${p.name}'s cards played this round`, {
      cls: `played ${n > cap ? "over" : n === cap ? "full" : ""}`,
      title: `Cards ${p.name} has played from their binder this round; it counts itself. ${earlier ? `Earlier, ${earlier}.` : ""}`,
    }),
    counterEl("World pts", String(p.worldPoints), { "data-act": "counter", "data-target": seat, "data-field": "worldPoints" }, `${p.name}'s world points`),
    counterEl("Rounds", String(p.roundsWon), { "data-act": "counter", "data-target": seat, "data-field": "roundsWon" }, `${p.name}'s rounds won`),
    voidPile(seat)
  );
}

function renderScoreboard() {
  const shared = h(
    "div",
    { class: "shared" },
    counterEl("Round", String(state.round), { "data-act": "round" }, "the round"),
    counterEl("Cap", String(capFor(state)), { "data-act": "cap" }, "this round's cap", {
      title: "Most cards each player can play this round",
    }),
    (() => {
      const b = h("button", { "data-act": "opener", class: "icon-btn", title: "Pick who opens at random", "aria-label": "Pick who opens at random" });
      b.append(
        svg(
          '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true"><rect x="4" y="4" width="16" height="16" rx="3"/><circle cx="9" cy="9" r="1.6" fill="currentColor" stroke="none"/><circle cx="15" cy="15" r="1.6" fill="currentColor" stroke="none"/><circle cx="15" cy="9" r="1.6" fill="currentColor" stroke="none"/><circle cx="9" cy="15" r="1.6" fill="currentColor" stroke="none"/><circle cx="12" cy="12" r="1.6" fill="currentColor" stroke="none"/></svg>'
        )
      );
      return b;
    })(),
    turnControls()
  );
  return h("div", { class: "scoreboard" }, scoreRow(other(mySeat)), shared, scoreRow(mySeat));
}

// End turn and Pass, for whoever is to play (in solo you play both seats).
function turnControls() {
  const t = state.turn;
  if (!t) return h("span", { class: "turn-acts muted small", text: "Roll for the opener" });
  if (mode !== "solo" && t !== mySeat) {
    return h("span", { class: `turn-acts small own-${t}`, text: `${state.players[t].name} to play` });
  }
  return h(
    "span",
    { class: "turn-acts" },
    h("button", { "data-act": "end-turn", "data-seat": t, title: `End ${state.players[t].name}'s turn` }, "End turn"),
    h("button", { "data-act": "pass", "data-seat": t, class: "quiet", title: `${state.players[t].name} passes` }, "Pass")
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

// The guide: the four spots in the top-left corner, drawn dotted, show what a
// complete world looks like. Every other spot is invisible until you place a card.
const GUIDE = new Set(["0,0", "0,1", "1,0", "1,1"]);

function renderArea(seat) {
  const area = h("section", {
    class: `area ${seat === mySeat ? "mine" : "theirs"} area-${seat}`,
    "data-area": seat,
    "aria-label": `${state.players[seat].name}'s area`,
  });
  const board = h("div", { class: `board own-${seat}` });
  board.style.setProperty("--cols", String(GRID.cols));
  for (let r = 0; r < GRID.rows; r++) {
    for (let c = 0; c < GRID.cols; c++) {
      const key = cellKey(r, c);
      const guide = GUIDE.has(key);
      const cell = h("div", {
        class: `cell${guide ? " guide" : ""}`,
        "data-area": seat,
        "data-key": key,
        title: guide ? "A world: up to four of your cards in a 2×2 square" : null,
      });
      const stack = state.table[seat][key] || [];
      stack.forEach((inst, i) => {
        const t = tokenFor(inst, "table");
        t.style.setProperty("--depth", i);
        cell.append(t);
      });
      if (stack.length > 1) cell.append(h("span", { class: "stack-count", text: String(stack.length) }));
      board.append(cell);
    }
  }
  area.append(board);
  return area;
}

function renderTable() {
  const table = $("#table");
  table.replaceChildren(renderArea(other(mySeat)), renderScoreboard(), renderArea(mySeat));
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
      h("button", { "data-act": "close-void", class: "icon quiet", title: "Close", "aria-label": "Close" }, "×")
    )
  );
  const list = h("div", { class: "void-list" });
  for (const inst of state.voids[seat]) list.append(tokenFor(inst, "void"));
  if (!state.voids[seat].length) list.append(h("p", { class: "hint", text: "Empty." }));
  pop.append(list);
  pop.append(h("p", { class: "hint", text: "Drag a card out, or click it and then a spot. Right-click for more." }));
}

function renderLog() {
  const panel = $("#logPanel");
  panel.hidden = !ui.logOpen;
  if (!ui.logOpen) return;
  panel.replaceChildren(
    h("div", { class: "pop-head" }, h("strong", { text: "Log" }), h("button", { "data-act": "toggle-log", class: "icon quiet", title: "Close", "aria-label": "Close" }, "×"))
  );
  const list = h("ol", { class: "log-list" });
  for (const entry of state.log) list.append(h("li", { class: `own-${entry.seat}`, text: entry.text }));
  panel.append(list);
  list.scrollTop = list.scrollHeight;
}

// Size the cards so the whole grid fits the space each area has.
const GAP = 6;
function layout() {
  const table = $("#table");
  const area = table.querySelector(".area");
  if (!area) return;
  const cs = getComputedStyle(area);
  const w = area.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
  const hgt = area.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
  const pad = 2 * 8; // the board's padding
  // against the computer, worlds sit side by side: two rows of cards under a label, eight across
  const cols = vsComputer() ? 8 : GRID.cols, rows = vsComputer() ? 2 : GRID.rows, labels = vsComputer() ? 30 : 0;
  const byW = (w - pad - GAP * (cols - 1)) / cols;
  const byH = (hgt - pad - labels - GAP * (rows - 1)) / rows / 1.4;
  const cw = Math.max(36, Math.floor(Math.min(byW, byH)));
  table.style.setProperty("--cw", `${cw}px`);
  table.style.setProperty("--ts", String(cw / 320));
  table.style.setProperty("--gap", `${GAP}px`);
}

// A starfield for the table, drawn once: two tiles of different sizes so the
// repeat doesn't show.
function starTile(size, count, seed, dim = 1) {
  const c = document.createElement("canvas");
  c.width = c.height = size;
  const g = c.getContext("2d");
  let s = seed;
  const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
  for (let i = 0; i < count; i++) {
    const x = rnd() * size;
    const y = rnd() * size;
    const big = rnd() > 0.94;
    const r = big ? 0.9 + rnd() * 0.7 : 0.3 + rnd() * 0.55;
    const a = (big ? 0.7 + rnd() * 0.3 : 0.18 + rnd() * 0.5) * dim;
    const t = rnd();
    const rgb = t < 0.12 ? "190,208,255" : t < 0.2 ? "255,226,196" : "255,255,255";
    if (big) {
      const glow = g.createRadialGradient(x, y, 0, x, y, r * 4);
      glow.addColorStop(0, `rgba(${rgb},${a * 0.35})`);
      glow.addColorStop(1, `rgba(${rgb},0)`);
      g.fillStyle = glow;
      g.fillRect(x - r * 4, y - r * 4, r * 8, r * 8);
    }
    g.fillStyle = `rgba(${rgb},${a})`;
    g.beginPath();
    g.arc(x, y, r, 0, Math.PI * 2);
    g.fill();
  }
  return c.toDataURL("image/png");
}
function paintStars() {
  try {
    const a = starTile(512, 90, 1931, 0.42); // a faint sky over the felt
    const b = starTile(733, 60, 7177, 0.42);
    $("#table").style.setProperty("--stars", `url(${a}), url(${b})`);
  } catch {}
}

// ---- preview and menus --------------------------------------------------------------
function showPreview(iid, x) {
  const found = vsComputer() ? cpu.lookup(iid) : lookup(iid);
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
  pv.append(h("div", { class: "pv-label", text: found.label || `${owner}'s card${found.inst.original ? " · original" : " · copy"}` }));
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
    if (found.inst.owner === mySeat) items.push(["undo", "Take back (doesn't count as played)"]);
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
    if (vsComputer() && cpu.click(e)) return;
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
      else if (act === "undo") returnToMyBinder(iid);
      return;
    }
    closeMenu();

    const btn = e.target.closest("[data-act]");
    if (btn) {
      const d = btn.dataset;
      switch (d.act) {
        case "opponent":
          setOpponent(d.vs);
          break;
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
          dispatch({ type: "endTurn", seat: mode === "solo" ? d.seat : undefined });
          break;
        case "pass":
          dispatch({ type: "pass", seat: mode === "solo" ? d.seat : undefined });
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
          ui.binderSide = d.face;
          setAllBinderFaces(d.face);
          break;
        case "binder-page":
          ui.binderPage = Number(d.page);
          renderBinder();
          break;
        case "flip":
          flipCard(d.from, d.iid);
          break;
        case "rename":
          renameSeat(d.seat);
          break;
        case "played":
          dispatch({ type: "played", target: d.target, delta: Number(d.delta) });
          break;
        case "cap":
          dispatch({ type: "cap", delta: Number(d.delta) });
          break;
        case "counter":
          dispatch({ type: "counter", target: d.target, field: d.field, delta: Number(d.delta) });
          break;
        case "open-void":
          if (ui.selected) {
            sendToVoid(ui.selected);
            break;
          }
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
    if (vsComputer()) return; // against the computer, cards are played through the rules

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
    if (vsComputer()) return;
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
    if (vsComputer()) return;
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
    const pile = drag && drag.from !== "void" ? e.target.closest("[data-void]") : null;
    const binder = drag && drag.from !== "binder" ? binderTarget(e.target) : null;
    const target = cell || pile || binder;
    if (!target) return;
    e.preventDefault();
    document.querySelectorAll(".over, .drop-over").forEach((n) => n !== target && n.classList.remove("over", "drop-over"));
    target.classList.add(cell ? "over" : "drop-over");
  });
  document.addEventListener("drop", (e) => {
    const cell = e.target.closest(".cell");
    const pile = e.target.closest("[data-void]");
    const binder = binderTarget(e.target);
    if (!cell && !pile && !binder) return;
    e.preventDefault();
    clearOver();
    let sel = drag;
    try {
      sel = JSON.parse(e.dataTransfer.getData("application/x-tfc"));
    } catch {}
    if (!sel) return;
    if (cell) dropOn(sel, { area: cell.dataset.area, key: cell.dataset.key });
    else if (pile) sendToVoid(sel);
    else if (sel.from !== "binder") returnToMyBinder(sel.iid);
  });

  document.addEventListener("keydown", (e) => {
    if (e.target.closest("input, textarea") || e.metaKey || e.ctrlKey || e.altKey) return;
    const k = e.key.toLowerCase();
    if (vsComputer() && k !== "b" && k !== "l") {
      cpu.key(k);
      return;
    }
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
    } else if (!ui.hover && k === "f" && ui.binderOpen && privates[mySeat]) {
      ui.binderSide = ui.binderSide === "force" ? "permanence" : "force";
      setAllBinderFaces(ui.binderSide);
    } else if ((k === "arrowright" || k === "arrowleft") && ui.binderOpen && privates[mySeat]) {
      ui.binderPage += k === "arrowright" ? 1 : -1;
      renderBinder();
    } else if (ui.hover && k === "v" && ui.hover.from === "table") {
      dispatch({ type: "toVoid", iid: ui.hover.iid });
    } else if (ui.hover && k === "r" && ui.hover.from !== "binder") {
      dispatch({ type: "toBinder", iid: ui.hover.iid });
    }
  });

  window.addEventListener("resize", () => { layout(); fitBinder(); });
}

// ---- start -------------------------------------------------------------------------------------
async function init() {
  let cardsJson;
  try {
    let bindersJson, facesJson;
    [cardsJson, bindersJson, facesJson] = await Promise.all([
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
    if (!state || state.v !== 5) {
      state = initialState(mode === "host" ? { p1: store.get("tfc:name", "") || undefined } : {});
      saveState();
    }
  }
  if (mode === "guest" && !store.get("tfc:name", "")) {
    const n = prompt("Your name for the contest", "");
    if (n && n.trim()) store.set("tfc:name", n.trim());
  }

  if (mode === "solo") {
    try {
      cpu = createComputer({ h, renderFace, buildAlbum, goneSleeve, hidePreview, toast, store, $, ui, cardsJson, cardsById, cardOrder, binders, active: vsComputer, render: () => render() });
    } catch (err) {
      console.error("The computer opponent didn't start:", err);
      cpu = null;
    }
  }

  paintStars();
  bindInput();
  render();
  if (vsComputer()) cpu.resume();

  if (mode !== "solo") {
    net = createNet({ mode, room, peerOptions: peerOptionsFromUrl(params), onMessage: onNetMessage, onStatus: onNetStatus });
  }
}

init();
