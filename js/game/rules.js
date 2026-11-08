// The First Contest: rules engine for the third-pass cards (Nov 2, 2026).
//
// Runs in the browser (the table's Computer mode, js/computer.js) and in node (scripts/sim3.mjs, scripts/test-rules3.mjs).
// It enforces the current loop: worlds of up to 2x2 (open worlds, uncapped, as a simulator switch), one world point per complete set of the
// four elements in a world, the highest single-element count as the tie-break, best of three
// rounds, Gwent-style passing, 10 cards a round, and the test rule from Nov 2: a player who
// makes a world worth 3 world points wins the contest at once.
//
// Every card effect is written by hand below, keyed by card name. Where a card's text leaves
// a question open, the engine picks one reading; each is marked READING and listed in
// README.md under "Rule readings".

export const BIT = { fire: 1, water: 2, air: 4, earth: 8 };
export const ELS = ["fire", "water", "air", "earth"];
const F = 1, W = 2, A = 4, E = 8, ANY = 15;
const POP = [0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4];
const ADJ = [[1, 2], [0, 3], [0, 3], [1, 2]]; // cells 0 1 / 2 3; diagonals aren't adjacent
// World geometry. The table plays worlds of up to 2x2 (the square). The simulator can switch on open
// worlds (newContest(..., { openWorlds: true })): an 11x11 grid with no size cap, starting in the middle.
// A world's geometry follows from the length of its cells array, so a world carries it wherever it goes.
const SQUARE = { n: 4, cols: 2, adj: ADJ, cap: 4, start: 0, open: false };
const OPEN = (() => {
  const G = 11, adj = [];
  for (let c = 0; c < G * G; c++) {
    const x = c % G, y = (c / G) | 0, a = [];
    if (x > 0) a.push(c - 1); if (x < G - 1) a.push(c + 1); if (y > 0) a.push(c - G); if (y < G - 1) a.push(c + G);
    adj.push(a);
  }
  return { n: G * G, cols: G, adj, cap: Infinity, start: (G >> 1) * G + (G >> 1), open: true };
})();
const geoOf = (w) => (w.cells.length === SQUARE.n ? SQUARE : OPEN);
const geo = (s) => (s.open ? OPEN : SQUARE);
export const CELL_NAMES = ["top left", "top right", "bottom left", "bottom right"];
export const DEFAULT_CAP = 10;
export const DECISIVE_POINTS = 3; // Nov 2 test rule: the Perfect World
// Win-condition numbers a simulation can change per contest (newContest opts.knobs); the table uses these.
export const KNOBS = { perfectWorld: DECISIVE_POINTS, archipelagoWater: 10, mountainPer: 4, cradleEach: 3 };
export const knob = (s, k) => (s.knobs && s.knobs[k] !== undefined ? s.knobs[k] : KNOBS[k]);

const maskOf = (tok) => (tok === "any" ? ANY : tok.includes("|") ? tok.split("|").reduce((m, e) => m | BIT[e], 0) : BIT[tok]);
const hasBit = (toks, b) => toks.some((t) => t & b);

// ---------------------------------------------------------------- cards
export let C = {};
export function loadCards(json) {
  C = {};
  for (const c of json.cards) {
    if (c.meta) {
      C[c.id] = { id: c.id, no: c.no, meta: true, name: c.meta.name, rarity: c.rarity, text: c.meta.text, aff: null, el: 0, fireCard: false };
      continue;
    }
    const aff = c.permanence.affinities.map(maskOf);
    let el = 0;
    for (const t of aff) if (t !== ANY) el |= t; // READING: a wildcard affinity gives its force no element
    C[c.id] = {
      id: c.id, no: c.no, rarity: c.rarity, name: c.permanence.name, aff, ptext: c.permanence.text,
      fname: c.force ? c.force.name : null, fdur: c.force && /once/i.test(c.force.duration) ? "once" : "round",
      ftext: c.force ? c.force.text : "", el, fireCard: aff.some((t) => t & F),
    };
  }
  return C;
}
export const card = (id) => C[id];
const one = (i) => C[i.card].aff.length === 1; // "with one affinity": one ring printed on the card

// ---------------------------------------------------------------- state
function newPlayer(ids, name) {
  return { name, binder: ids.slice(), size: ids.length, void: [], played: 0, passed: false, skip: false, wins: 0, commons: [] };
}
// opts (simulator switches; the table uses none): openWorlds (no cap on world size), bestOf (1 or 3 rounds, default 3),
// noCap (no limit on cards a round: whole binders can be played)
export function newContest(idsA, idsB, opener, names = ["You", "Computer"], opts = {}) {
  const s = {
    r: 1, cap: opts.noCap ? 1e9 : DEFAULT_CAP, bestOf: opts.bestOf || 3, knobs: opts.knobs || null, turn: opener, opener, p: [newPlayer(idsA, names[0]), newPlayer(idsB, names[1])], open: !!opts.openWorlds,
    inst: {}, worlds: {}, nid: 1, ts: 1, extras: [], calm: false, phase: "turn", winner: null, rounds: [], log: [], decisive: null,
  };
  return s;
}
export function clone(s) {
  const inst = {};
  for (const k in s.inst) inst[k] = Object.assign({}, s.inst[k]);
  const worlds = {};
  for (const k in s.worlds) { const w = s.worlds[k]; worlds[k] = { id: w.id, owner: w.owner, cells: w.cells.slice(), n: w.n }; }
  return {
    r: s.r, cap: s.cap, bestOf: s.bestOf, knobs: s.knobs, turn: s.turn, opener: s.opener, open: s.open, nid: s.nid, ts: s.ts, inst, worlds, extras: s.extras.slice(), calm: s.calm,
    phase: s.phase, winner: s.winner, rounds: s.rounds, log: [], decisive: s.decisive, turnStarted: s.turnStarted, why: s.why,
    p: s.p.map((x) => ({ name: x.name, binder: x.binder.slice(), size: x.size, void: x.void.slice(), played: x.played, passed: x.passed, skip: x.skip, wins: x.wins, commons: x.commons.slice() })),
  };
}
const dirty = (s) => { s._v = null; };

// ---------------------------------------------------------------- queries
// The permanence and force lists, in play order, cached on the table (not saved with it). Instances are only added
// (newInst) or deleted (drop), and both bump s._g, so s._g says when the lists are stale.
// Callers get the cached arrays: treat them as read-only.
const drop = (s, id) => { delete s.inst[id]; s._g = (s._g || 0) + 1; };
function lists(s) {
  const sig = s._g || 0;
  if (s._l && s._l.sig === sig) return s._l;
  const ps = [], fs = [], owns = new Set();
  for (const k in s.inst) { const i = s.inst[k]; if (i.kind === "perm") ps.push(i); else if (i.kind === "force") fs.push(i); }
  ps.sort((a, b) => a.ts - b.ts); fs.sort((a, b) => a.ts - b.ts);
  for (const i of ps) owns.add(i.owner + "|" + C[i.card].name);
  Object.defineProperty(s, "_l", { value: { sig, perms: ps, forces: fs, owns }, writable: true, configurable: true, enumerable: false });
  return s._l;
}
export function perms(s) { return lists(s).perms; }
export function forces(s) { return lists(s).forces; }
export function worldsOf(s, P) { const o = []; for (const k in s.worlds) if (s.worlds[k].owner === P) o.push(s.worlds[k]); return o.sort((a, b) => a.n - b.n); }
export const worldSize = (w) => w.cells.reduce((n, c) => n + (c !== null ? 1 : 0), 0);
export function adjacent(s, i) {
  const w = s.worlds[i.w]; const o = [];
  if (!w) return o;
  for (const c of geoOf(w).adj[i.cell]) if (w.cells[c] !== null) o.push(s.inst[w.cells[c]]);
  return o;
}
const isAdj = (s, a, b) => a.w === b.w && !!s.worlds[a.w] && geoOf(s.worlds[a.w]).adj[a.cell].includes(b.cell);
const permsIn = (s, w) => w.cells.filter((c) => c !== null).map((id) => s.inst[id]);
const ownPerms = (s, P) => perms(s).filter((i) => i.owner === P);
const named = (i) => C[i.card].name;
const fname = (f) => C[f.card].fname;
const ownsPerm = (s, P, name) => lists(s).owns.has(P + "|" + name);
export const isLone = (s, i) => worldSize(s.worlds[i.w]) === 1;

// ---------------------------------------------------------------- ignoring forces
// src: { card, caster, fid } — the force's card, who played it, and its instance (lasting forces).
const SELF_IGNORE = {
  Ashfield: { el: W }, Barrens: { tiers: "C" }, "Tide Pool": { el: A }, Summit: { el: E }, "Stone Field": { el: F },
  "Hot Mud": { el: A | E }, Heath: { el: W | E }, "Peat Bog": { el: W | A }, "Spray Coast": { el: F | E }, Mudflat: { el: F | A },
  Foothills: { el: F | W }, Glacier: { el: A }, Spire: { el: E }, Cavern: { tiers: "CB" },
};
const ADJ_IGNORE = { "Mud Pots": A, Savanna: W, "Cinder Cone": F, Waterfall: E }; // your adjacent permanences ignore …
const KIND_IGNORE = { Obsidian: [F, W], "Tidal Flat": [W, A], "Sky Isle": [A, E], "Hidden Valley": [E, F] }; // your X permanences ignore Y forces
function worldIgnores(s, wid, src) {
  const w = s.worlds[wid]; if (!w) return false;
  const d = C[src.card]; const P = w.owner;
  if (d.rarity === "C" && ownsPerm(s, P, "Massif")) return true;
  for (const f of forces(s)) {
    if (f.id === src.fid) continue;
    const n = fname(f);
    if (n === "Uplift" && f.w === wid) return true;
    if (n === "Overgrowth" && f.w === wid && d.rarity === "C") return true;
    if (n === "Firebreak" && f.owner === P && d.el & F) return true;
    if (n === "Windbreak" && f.owner === P && d.el & A) return true;
  }
  return false;
}
export function permIgnores(s, i, src) {
  const d = C[src.card]; const n = named(i);
  const si = SELF_IGNORE[n];
  if (si && ((si.el && d.el & si.el) || (si.tiers && si.tiers.includes(d.rarity)))) return true;
  for (const t of adjacent(s, i)) { const el = ADJ_IGNORE[named(t)]; if (el && t.owner === i.owner && d.el & el) return true; }
  const printed = C[i.card].aff.reduce((m, t) => m | t, 0);
  for (const o of ownPerms(s, i.owner)) { const k = KIND_IGNORE[named(o)]; if (k && printed & k[0] && d.el & k[1]) return true; }
  return worldIgnores(s, i.w, src);
}
const applies = (s, f, i) => !permIgnores(s, i, { card: f.card, caster: f.owner, fid: f.id });
const appliesW = (s, f, wid) => !worldIgnores(s, wid, { card: f.card, caster: f.owner, fid: f.id });

// ---------------------------------------------------------------- the view: each permanence's affinities now
const SET_EL = { Spark: F, Kindling: F, Rain: W, Snowmelt: W, Breeze: A, Thermal: A, Silt: E, Dustfall: E, Cloudburst: W,
  Updraft: F, Brushfire: F, Shower: W, Current: W, Rockfall: E, "Dust Devil": A, Riptide: W, "Dry Wind": A };
const WORLD_SHIFT = { Downpour: [F, W], Sandstorm: [E, F], Waterspout: [W, A], "Dust Storm": [A, E] };
const WORLD_BECOMES = { Firestorm: F, Tsunami: W };
const CARD_BLANK = new Set(["Smolder", "Drizzle", "Dust", "Drying Wind", "Ember"]);
const PAIR_BLANK = new Set(["Heatwave", "Steam Explosion"]);
const WORLD_BLANK_KIND = { Ashfall: A, Scorch: E };
const ADJ_SHIFT = { "Lava Field": [E, F], Shoal: [F, W], Peak: [W, A], Meadow: [A, E] }; // adjacent X permanences become Y
const DRAWBACK = { Badlands: W, Fen: A, "Wind Gap": E, Moor: F }; // loses its affinities if adjacent to X
export function view(s) {
  if (s._v) return s._v;
  const ps = perms(s), fs = forces(s);
  const tok = {}, blank = {};
  for (const i of ps) tok[i.id] = C[i.card].aff.slice();
  // copies
  for (const f of fs) if (fname(f) === "Heat Shimmer") {
    const i = s.inst[f.t], src = s.inst[f.src];
    if (i && src && applies(s, f, i)) tok[i.id] = C[src.card].aff.slice(); // READING: copies the printed affinities
  }
  for (const i of ps) if (named(i) === "Mirage") {
    tok[i.id] = [];
    for (const t of adjacent(s, i)) if (named(t) !== "Mirage") tok[i.id].push(...tok[t.id]);
  }
  // element changes: permanence first, then lasting forces in the order they were played.
  // "Becomes X" overwrites: the permanence is left with a single X affinity, however many it
  // had. Nothing changes every affinity on a card unless its text says so (Cam, Nov 2).
  for (const i of ps) {
    const sh = ADJ_SHIFT[named(i)]; if (!sh) continue;
    for (const t of adjacent(s, i)) if (hasBit(tok[t.id], sh[0])) tok[t.id] = [sh[1]];
  }
  for (const f of fs) {
    const n = fname(f);
    if (SET_EL[n] !== undefined) { const i = s.inst[f.t]; if (i && applies(s, f, i)) tok[i.id] = [SET_EL[n]]; }
    else if (WORLD_SHIFT[n]) {
      const w = s.worlds[f.w]; if (!w) continue; const [x, y] = WORLD_SHIFT[n];
      for (const i of permsIn(s, w)) if (applies(s, f, i) && hasBit(tok[i.id], x)) tok[i.id] = [y];
    } else if (WORLD_BECOMES[n] !== undefined) {
      const w = s.worlds[f.w]; if (!w) continue;
      for (const i of permsIn(s, w)) if (applies(s, f, i)) tok[i.id] = [WORLD_BECOMES[n]];
    }
  }
  // losing affinities
  for (const f of fs) {
    const n = fname(f);
    if (CARD_BLANK.has(n)) { const i = s.inst[f.t]; if (i && applies(s, f, i)) blank[i.id] = true; }
    else if (PAIR_BLANK.has(n)) { for (const t of [f.t, f.t2]) { const i = s.inst[t]; if (i && applies(s, f, i)) blank[i.id] = true; } }
    else if (WORLD_BLANK_KIND[n]) {
      const w = s.worlds[f.w]; if (!w) continue;
      for (const i of permsIn(s, w)) if (applies(s, f, i) && hasBit(tok[i.id], WORLD_BLANK_KIND[n])) blank[i.id] = true;
    } else if (n === "Eruption" || n === "Deluge") {
      for (const wid of [f.w, f.w2]) { const w = s.worlds[wid]; if (!w) continue; for (const i of permsIn(s, w)) if (applies(s, f, i)) blank[i.id] = true; }
    }
  }
  if (ps.some((i) => named(i) === "Ice Sheet")) for (const i of ps) if (hasBit(tok[i.id], F)) blank[i.id] = true; // READING: both players
  for (const i of ps) {
    const x = DRAWBACK[named(i)];
    if (x && adjacent(s, i).some((t) => !blank[t.id] && hasBit(tok[t.id], x))) blank[i.id] = true;
  }
  const cur = {};
  for (const i of ps) cur[i.id] = blank[i.id] ? [] : tok[i.id];
  s._v = { tok: cur, blank };
  return s._v;
}
// a permanence "showing" an element now
const shows = (s, i, b) => hasBit(view(s).tok[i.id] || [], b);

// ---------------------------------------------------------------- protections
function protForce(s, i, name) { return forces(s).some((f) => fname(f) === name && applies(s, f, i)); }
// can i be removed? src: force src, or null for a meta card or a permanence's text
export function canRemove(s, i, src) {
  if (i.kind !== "perm") return true;
  if (src && permIgnores(s, i, src)) return false;
  for (const f of forces(s)) {
    if (!applies(s, f, i)) continue;
    const n = fname(f);
    if (n === "Shelter" && f.t === i.id) return false;
    if (n === "Freeze" && f.w === i.w && shows(s, i, W)) return false;
    if (n === "Heat Dome" && shows(s, i, F)) return false;
    if (n === "High Pressure" && shows(s, i, A)) return false;
  }
  return true;
}
const UNMOVABLE = new Set(["Bedrock", "Mangrove", "Glacier", "Spire"]);
export function canMove(s, i, src) {
  if (UNMOVABLE.has(named(i))) return false;
  if (src && permIgnores(s, i, src)) return false;
  for (const t of adjacent(s, i)) if (t.owner === i.owner && named(t) === "Thicket") return false;
  const w = s.worlds[i.w];
  if (w && permsIn(s, w).some((t) => named(t) === "Old Growth")) return false;
  for (const f of forces(s)) {
    if (!applies(s, f, i)) continue;
    const n = fname(f);
    if (n === "Shelter" && f.t === i.id) return false;
    if (n === "Tangle" && f.w === i.w) return false;
    if (n === "Bramble" && f.owner === i.owner) return false;
    if (n === "Ice Storm" && shows(s, i, W)) return false;
    if (n === "Permafrost" && shows(s, i, E)) return false;
  }
  return true;
}
export function canGrow(s, w) {
  if (worldSize(w) >= geoOf(w).cap) return false;
  for (const f of forces(s)) {
    const n = fname(f);
    if ((n === "Fog" || n === "Mire" || n === "Steam") && f.w === w.id && appliesW(s, f, w.id)) return false;
    if (n === "Whiteout" && appliesW(s, f, w.id)) return false;
  }
  return true;
}
const canSplit = (s, w) => !permsIn(s, w).some((i) => named(i) === "Canyon");
export function openCells(w) {
  const g = geoOf(w); const o = [];
  if (worldSize(w) === 0) return [g.start];
  for (let c = 0; c < g.n; c++) if (w.cells[c] === null && g.adj[c].some((a) => w.cells[a] !== null)) o.push(c);
  return o;
}
// Open worlds have many open cells; the moves offer one cell per set of neighbours it would touch
// (the one nearest the world's middle), since adjacency is all a cell decides.
function cellChoices(w) {
  const cells = openCells(w), g = geoOf(w);
  if (!g.open || cells.length <= 1) return cells;
  let sx = 0, sy = 0, k = 0;
  for (let c = 0; c < g.n; c++) if (w.cells[c] !== null) { sx += c % g.cols; sy += (c / g.cols) | 0; k++; }
  const cx = sx / k, cy = sy / k, best = new Map();
  for (const c of cells) {
    const key = g.adj[c].filter((a) => w.cells[a] !== null).map((a) => w.cells[a]).sort().join(",");
    const d = (c % g.cols - cx) ** 2 + (((c / g.cols) | 0) - cy) ** 2;
    const b = best.get(key); if (!b || d < b.d) best.set(key, { c, d });
  }
  return [...best.values()].map((b) => b.c).sort((a, b) => a - b);
}

// ---------------------------------------------------------------- table changes
function newInst(s, P, cardId, kind, extra) {
  const id = "i" + s.nid++;
  s.inst[id] = Object.assign({ id, card: cardId, owner: P, kind, w: null, cell: null, ts: s.ts++ }, extra || {});
  s._g = (s._g || 0) + 1;
  dirty(s);
  return s.inst[id];
}
function newWorld(s, P) {
  const id = "w" + s.nid++;
  const n = 1 + Math.max(0, ...worldsOf(s, P).map((w) => w.n));
  s.worlds[id] = { id, owner: P, cells: new Array(geo(s).n).fill(null), n };
  return s.worlds[id];
}
function toPile(s, i, where) { const pl = s.p[i.owner]; (where === "binder" ? pl.binder : pl.void).push(i.card); }
function dropForcesOn(s, iid) {
  for (const f of forces(s)) if (f.t === iid || f.t2 === iid || f.src === iid) { drop(s, f.id); toPile(s, f, "void"); }
}
function dropForcesOnWorld(s, wid) {
  for (const f of forces(s)) if (f.w === wid || f.w2 === wid) { drop(s, f.id); toPile(s, f, "void"); }
}
function lift(s, i) { // take a permanence out of its world (it stays an instance)
  const w = s.worlds[i.w]; if (!w) return;
  w.cells[i.cell] = null; i.w = null; i.cell = null;
  fixWorld(s, w.id);
  dirty(s);
}
export function leave(s, i, where) { // a permanence or lasting force leaves the table
  if (!s.inst[i.id]) return;
  if (i.kind === "perm") { dropForcesOn(s, i.id); lift(s, i); }
  drop(s, i.id);
  toPile(s, i, where);
  dirty(s);
}
function fixWorld(s, wid) {
  const w = s.worlds[wid]; if (!w) return;
  const g = geoOf(w); const occ = []; for (let c = 0; c < g.n; c++) if (w.cells[c] !== null) occ.push(c);
  if (!occ.length) { delete s.worlds[wid]; dropForcesOnWorld(s, wid); return; }
  const seen = new Set(), comps = [];
  for (const c0 of occ) {
    if (seen.has(c0)) continue;
    const comp = [], st = [c0]; seen.add(c0);
    while (st.length) { const c = st.pop(); comp.push(c); for (const a of g.adj[c]) if (w.cells[a] !== null && !seen.has(a)) { seen.add(a); st.push(a); } }
    comps.push(comp);
  }
  if (comps.length === 1) return;
  comps.sort((a, b) => b.length - a.length || Math.min(...a) - Math.min(...b));
  for (let k = 1; k < comps.length; k++) {
    const nw = newWorld(s, w.owner);
    for (const c of comps[k]) { const iid = w.cells[c]; nw.cells[c] = iid; w.cells[c] = null; s.inst[iid].w = nw.id; }
  }
}
function put(s, i, w, cell) { i.w = w.id; i.cell = cell; w.cells[cell] = i.id; dirty(s); }
function moveTo(s, i, w2, cell) { lift(s, i); if (s.worlds[w2.id] && w2.cells[cell] === null) put(s, i, w2, cell); else { const nw = newWorld(s, i.owner); put(s, i, nw, geoOf(nw).start); } }
function ownWorld(s, i) { lift(s, i); const nw = newWorld(s, i.owner); put(s, i, nw, geoOf(nw).start); }
function swap(s, a, b) {
  const wa = s.worlds[a.w], wb = s.worlds[b.w], ca = a.cell, cb = b.cell;
  wa.cells[ca] = b.id; wb.cells[cb] = a.id; a.w = wb.id; a.cell = cb; b.w = wa.id; b.cell = ca;
  dirty(s);
}
function returnWorld(s, w, ev) { for (const i of permsIn(s, w)) { ev.returned.push(i.card); leave(s, i, "binder"); } }
function scatter(s, w, src) { // every movable permanence of w becomes its own world
  const list = permsIn(s, w);
  for (const i of list.slice(1)) if (s.inst[i.id] && (!src || canMove(s, i, src))) ownWorld(s, i);
}
function splitParts(w) { // READING: a split cuts a world down its middle, left from right (or top from bottom)
  const g = geoOf(w);
  if (g.open) { // open worlds: cut the occupied cells' bounding box down its middle (a middle column or row goes left or top)
    const occ = []; for (let c = 0; c < g.n; c++) if (w.cells[c] !== null) occ.push(c);
    const xs = occ.map((c) => c % g.cols), ys = occ.map((c) => (c / g.cols) | 0);
    const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
    if (x1 > x0) { const mid = (x0 + x1 + 1) / 2; return [occ.filter((c) => c % g.cols < mid), occ.filter((c) => c % g.cols >= mid)]; }
    if (y1 > y0) { const mid = (y0 + y1 + 1) / 2; return [occ.filter((c) => ((c / g.cols) | 0) < mid), occ.filter((c) => ((c / g.cols) | 0) >= mid)]; }
    return null;
  }
  const left = [0, 2].filter((c) => w.cells[c] !== null), right = [1, 3].filter((c) => w.cells[c] !== null);
  if (left.length && right.length) return [left, right];
  const top = [0, 1].filter((c) => w.cells[c] !== null), bot = [2, 3].filter((c) => w.cells[c] !== null);
  if (top.length && bot.length) return [top, bot];
  return null;
}
function splitWorld(s, w, src) {
  if (worldSize(w) < 2 || !canSplit(s, w)) return false;
  const parts = splitParts(w); if (!parts) return false;
  for (const part of [parts[1], parts[0]]) {
    const ins = part.map((c) => s.inst[w.cells[c]]);
    if (ins.every((i) => !src || canMove(s, i, src))) {
      const nw = newWorld(s, w.owner);
      for (const i of ins) { w.cells[i.cell] = null; nw.cells[i.cell] = i.id; i.w = nw.id; }
      fixWorld(s, w.id); fixWorld(s, nw.id); dirty(s);
      return true;
    }
  }
  return false;
}

// ---------------------------------------------------------------- scoring
const SETS = new Map();
function feasible(c, flex, need) {
  const d = [0, 0, 0, 0]; let any = false;
  for (let e = 0; e < 4; e++) { d[e] = Math.max(0, need[e] - c[e]); if (d[e]) any = true; }
  if (!any) return true;
  for (let S = 1; S < 16; S++) {
    let sd = 0; for (let e = 0; e < 4; e++) if (S & (1 << e)) sd += d[e];
    if (!sd) continue;
    let cnt = 0; for (const t of flex) if (t & S) cnt++;
    if (cnt < sd) return false;
  }
  return true;
}
function split(tokens) { const c = [0, 0, 0, 0], flex = []; for (const t of tokens) { if (POP[t] === 1) c[Math.log2(t)]++; else if (t) flex.push(t); } return { c, flex }; }
export function setsOf(tokens) {
  const key = tokens.slice().sort((a, b) => a - b).join(",");
  const hit = SETS.get(key); if (hit) return hit;
  const { c, flex } = split(tokens);
  let k = Math.floor(tokens.length / 4);
  while (k > 0 && !feasible(c, flex, [k, k, k, k])) k--;
  let cov = 0; // elements already covered toward the next set
  for (let T = 15; T > 0 && cov < 3; T--) {
    const sz = POP[T]; if (sz >= 4 || sz <= cov) continue;
    const need = [0, 1, 2, 3].map((e) => (T & (1 << e) ? k + 1 : k));
    if (feasible(c, flex, need)) cov = sz;
  }
  const r = { k, cov };
  if (SETS.size > 200000) SETS.clear();
  SETS.set(key, r);
  return r;
}
const hasEach = (tokens, n) => { const { c, flex } = split(tokens); return feasible(c, flex, [n, n, n, n]); };
export function score(s) {
  const v = view(s);
  const pw = knob(s, "perfectWorld");
  const res = [0, 1].map(() => ({ pts: 0, tie: 0, tot: [0, 0, 0, 0], water: 0, earth: 0, worlds: [], all: [], mtn: 0, pw }));
  for (const k in s.worlds) {
    const w = s.worlds[k], R = res[w.owner], toks = [];
    for (const iid of w.cells) if (iid !== null) toks.push(...v.tok[iid]);
    const st = setsOf(toks);
    R.pts += st.k; R.worlds.push({ id: w.id, n: w.n, k: st.k, cov: st.cov, cards: worldSize(w), perfect: st.k >= pw });
    R.all.push(...toks);
    for (const t of toks) { for (let e = 0; e < 4; e++) if (t & (1 << e)) R.tot[e]++; if (t & W) R.water++; if (t & E) R.earth++; }
  }
  for (const P of [0, 1]) {
    const R = res[P];
    R.tie = Math.max(...R.tot);
    if (ownsPerm(s, P, "Mountain Range")) { R.mtn = Math.floor(R.earth / knob(s, "mountainPer")); R.pts += R.mtn; }
    R.worlds.sort((a, b) => a.n - b.n);
  }
  return res;
}
// +1: P is ahead, 0: level, -1: behind
export function outcome(sc, P) {
  const a = sc[P], b = sc[1 - P];
  if (a.pts !== b.pts) return a.pts > b.pts ? 1 : -1;
  if (a.tie !== b.tie) return a.tie > b.tie ? 1 : -1;
  return 0;
}
const decisiveWorld = (sc, P) => sc[P].worlds.some((w) => w.perfect);

// ---------------------------------------------------------------- move generation
// A move: { id, face: "perm" | "force" | "meta", ...targets, picks: [...] }. picks lists the
// player's choices in order, for the play page: { k: "cell" | "perm" | "world" | "player" | "force" | "void" | "obinder" | "face", ... }.
const cellPick = (w, cell) => ({ k: "cell", w, cell });
const permPick = (id) => ({ k: "perm", id });
const worldPick = (id) => ({ k: "world", id });

function placements(s, P) {
  const out = [{ w: "new", cell: 0 }];
  for (const w of worldsOf(s, P)) { if (!canGrow(s, w)) continue; for (const cell of cellChoices(w)) out.push({ w: w.id, cell }); }
  return out;
}
function destinations(s, i, canonical) { // other worlds of its owner it can move into
  const out = [];
  for (const w of worldsOf(s, i.owner)) {
    if (w.id === i.w || !canGrow(s, w)) continue;
    const cells = cellChoices(w);
    for (const cell of canonical ? cells.slice(0, 1) : cells) out.push({ w2: w.id, cell });
  }
  return out;
}
function permMoves(s, P, id, out, base) {
  const n = C[id].name; const mk = (m) => out.push(Object.assign({ id, face: "perm" }, base || {}, m));
  for (const pl of placements(s, P)) {
    const picks = [cellPick(pl.w, pl.cell)];
    if (n === "Snowfield" || n === "Bluff" || n === "Hanging Valley") {
      // the "when played" choice is made on the table as it stands once the card is down
      const s2 = clone(s); const me = placeFresh(s2, P, id, pl);
      const mine = ownPerms(s2, P).filter((i) => i.id !== me.id);
      const srcP = null; let any = false;
      if (n === "Snowfield") for (const i of mine) { any = true; mk({ w: pl.w, cell: pl.cell, t: i.id, picks: picks.concat([permPick(i.id)]) }); }
      if (n === "Bluff") for (const i of mine) if (canMove(s2, i, srcP)) for (const d of destinations(s2, i)) {
        any = true; mk({ w: pl.w, cell: pl.cell, t: i.id, w2: d.w2, cell2: d.cell, picks: picks.concat([permPick(i.id), cellPick(d.w2, d.cell)]) });
      }
      if (n === "Hanging Valley") {
        const all = ownPerms(s2, P).filter((i) => canMove(s2, i, null));
        for (let a = 0; a < all.length; a++) for (let b = a + 1; b < all.length; b++) {
          any = true; mk({ w: pl.w, cell: pl.cell, t: all[a].id, t2: all[b].id, picks: picks.concat([permPick(all[a].id), permPick(all[b].id)]) });
        }
      }
      if (!any) mk({ w: pl.w, cell: pl.cell, picks });
    } else mk({ w: pl.w, cell: pl.cell, picks });
  }
}
// placeFresh: put a new permanence down (used for the "when played" lookahead and for applying)
function placeFresh(s, P, id, pl) {
  const i = newInst(s, P, id, "perm");
  const w = pl.w === "new" ? newWorld(s, P) : s.worlds[pl.w];
  put(s, i, w, pl.w === "new" ? geoOf(w).start : pl.cell);
  return i;
}

const REMOVE_ONE = { Scald: F | E, "Lava Bomb": E | A, Hail: F | A, Landslide: A | W };
const MOVE_ONE = {};
// common forces that turn a permanence of any size to their element for the round (Nov 2): the element they reach
const CARD_LASTING_ANY = { Updraft: A, Brushfire: E, Shower: F, Current: E, Rockfall: A, "Dust Devil": E, Riptide: A, "Dry Wind": W };
const OWN_WORLD_ONE = { Gust: A, Downdraft: F, Sinkhole: E };
const CARD_LASTING_ONE = { Smolder: E, Drizzle: F, Dust: A, "Drying Wind": W, Spark: A, Kindling: E, Rain: F, Snowmelt: E, Breeze: W, Thermal: F, Silt: W, Dustfall: A };
const WORLD_LASTING = new Set(["Freeze", "Tangle", "Fog", "Downpour", "Sandstorm", "Ashfall", "Dust Storm", "Scorch", "Waterspout", "Firestorm", "Eruption", "Tsunami", "Uplift"]);
const GLOBAL_LASTING = new Set(["Firebreak", "Windbreak", "Heat Dome", "Ice Storm", "High Pressure", "Permafrost", "Bramble", "Whiteout"]);
const REMOVE_KIND = { Drought: W, Wildfire: E, "Flash Flood": F, Avalanche: A };

function forceMoves(s, P, id, out) {
  const d = C[id]; const n = d.fname; if (!n) return;
  const src = { card: id, caster: P, fid: null };
  const all = perms(s);
  const tp = all.filter((i) => !permIgnores(s, i, src));
  const tw = Object.values(s.worlds).filter((w) => !worldIgnores(s, w.id, src)).sort((a, b) => a.owner - b.owner || a.n - b.n);
  const mk = (m, picks) => out.push(Object.assign({ id, face: "force" }, m, { picks: picks || [] }));
  const forT = (list) => { for (const i of list) mk({ t: i.id }, [permPick(i.id)]); };
  const pairs = (list, ok, extra) => {
    for (let a = 0; a < list.length; a++) for (let b = a + 1; b < list.length; b++) if (!ok || ok(list[a], list[b])) mk({ t: list[a].id, t2: list[b].id, ...(extra || {}) }, [permPick(list[a].id), permPick(list[b].id)]);
  };
  const movesOf = (list) => { for (const i of list) if (canMove(s, i, src)) for (const dd of destinations(s, i)) mk({ t: i.id, w2: dd.w2, cell: dd.cell }, [permPick(i.id), cellPick(dd.w2, dd.cell)]); };
  const big = (i) => worldSize(s.worlds[i.w]) >= 2;
  if (REMOVE_ONE[n] !== undefined) { forT(tp.filter((i) => one(i) && shows(s, i, REMOVE_ONE[n]) && canRemove(s, i, src))); return; }
  if (MOVE_ONE[n] !== undefined) { movesOf(tp.filter((i) => one(i) && shows(s, i, MOVE_ONE[n]))); return; }
  if (OWN_WORLD_ONE[n] !== undefined) { forT(tp.filter((i) => one(i) && shows(s, i, OWN_WORLD_ONE[n]) && big(i) && canMove(s, i, src))); return; }
  if (CARD_LASTING_ONE[n] !== undefined) { forT(tp.filter((i) => one(i) && shows(s, i, CARD_LASTING_ONE[n]))); return; }
  if (CARD_LASTING_ANY[n] !== undefined) { forT(tp.filter((i) => shows(s, i, CARD_LASTING_ANY[n]))); return; }
  if (WORLD_LASTING.has(n)) { for (const w of tw) mk({ w: w.id }, [worldPick(w.id)]); return; }
  if (GLOBAL_LASTING.has(n)) { mk({}); return; }
  if (REMOVE_KIND[n] !== undefined) {
    for (const w of tw) if (permsIn(s, w).some((i) => !permIgnores(s, i, src) && shows(s, i, REMOVE_KIND[n]) && canRemove(s, i, src))) mk({ w: w.id }, [worldPick(w.id)]);
    return;
  }
  switch (n) {
    case "Flare-up": for (const f of forces(s)) if (C[f.card].rarity === "C") mk({ f: f.id }, [{ k: "force", id: f.id }]); return;
    case "Ember": forT(tp.filter((i) => isLone(s, i))); return;
    case "Low Tide": for (const w of tw) if (w.owner === P) mk({ w: w.id }, [worldPick(w.id)]); return;
    case "Drift": movesOf(tp.filter((i) => i.owner === P)); return;
    case "Whirl": movesOf(tp); return;
    case "Crosswind": pairs(tp, (a, b) => a.owner === b.owner && a.w !== b.w && canMove(s, a, src) && canMove(s, b, src)); return;
    case "Eddy": pairs(tp, (a, b) => a.w === b.w && canMove(s, a, src) && canMove(s, b, src)); return;
    case "Overgrowth": for (const w of tw) if (w.owner === P) mk({ w: w.id }, [worldPick(w.id)]); return;
    case "Shelter": case "Cloudburst": forT(tp); return;
    case "Vent": forT(tp.filter((i) => i.owner === P)); return;
    case "Mire": for (const w of tw) if (worldSize(w) === 2) mk({ w: w.id }, [worldPick(w.id)]); return;
    case "Steam": for (const w of tw) if (worldSize(w) === 3) mk({ w: w.id }, [worldPick(w.id)]); return;
    case "Tremor": for (const w of tw) if (worldSize(w) === 2 && canSplit(s, w) && permsIn(s, w).some((i) => canMove(s, i, src))) mk({ w: w.id }, [worldPick(w.id)]); return;
    case "Heatwave": pairs(tp.filter((i) => shows(s, i, E))); return;
    case "Flood": pairs(tp, (a, b) => isAdj(s, a, b)); return;
    case "Gale": {
      const mv = tp.filter((i) => canMove(s, i, src));
      for (let a = 0; a < mv.length; a++) for (let b = a + 1; b < mv.length; b++) {
        for (const d1 of destinations(s, mv[a], true)) for (const d2 of destinations(s, mv[b], true)) {
          if (d1.w2 === mv[b].w && d2.w2 === mv[a].w) continue; // that's a swap: Crosswind's job
          mk({ t: mv[a].id, w2: d1.w2, cell: d1.cell, t2: mv[b].id, w3: d2.w2, cell3: d2.cell }, [permPick(mv[a].id), cellPick(d1.w2, d1.cell), permPick(mv[b].id), cellPick(d2.w2, d2.cell)]);
        }
      }
      return;
    }
    case "Gale Force": {
      const mv = tp.filter((i) => canMove(s, i, src) && destinations(s, i, true).length);
      for (let a = 0; a < mv.length; a++) for (let b = a + 1; b < mv.length; b++) for (let c = b + 1; c < mv.length; c++) {
        const trio = [mv[a], mv[b], mv[c]];
        const ds = trio.map((i) => destinations(s, i, true));
        for (const d1 of ds[0]) for (const d2 of ds[1]) for (const d3 of ds[2]) {
          const ts = trio.map((i) => i.id), dd = [d1, d2, d3];
          mk({ ts, ds: dd.map((x) => ({ w2: x.w2, cell: x.cell })) }, trio.flatMap((i, k) => [permPick(i.id), cellPick(dd[k].w2, dd[k].cell)]));
        }
      }
      return;
    }
    case "Undertow": for (const w of tw) if (worldSize(w) === 2) mk({ w: w.id }, [worldPick(w.id)]); return;
    case "Mudflow": for (const w of tw) if (worldSize(w) === 3) mk({ w: w.id }, [worldPick(w.id)]); return;
    case "Blizzard": for (const w of tw) mk({ w: w.id }, [worldPick(w.id)]); return;
    case "Thunderstorm": forT(tp.filter((i) => one(i) && canRemove(s, i, src))); return;
    case "Heat Shimmer": for (const i of tp) for (const t of adjacent(s, i)) mk({ t: i.id, src: t.id }, [permPick(i.id), permPick(t.id)]); return;
    case "Lightning": forT(tp.filter((i) => isLone(s, i) && canRemove(s, i, src))); return;
    case "Thaw": for (const f of forces(s)) mk({ f: f.id }, [{ k: "force", id: f.id }]); return;
    case "Whirlwind": pairs(tp.filter((i) => big(i) && canMove(s, i, src))); return;
    case "Squall": forT(tp.filter((i) => big(i) && canMove(s, i, src))); return;
    case "Cave-in": pairs(tp.filter((i) => one(i) && canRemove(s, i, src)), (a, b) => isAdj(s, a, b)); return;
    case "Collapse": forT(tp.filter((i) => canRemove(s, i, src))); return;
    case "Typhoon": for (const w of tw) if (worldSize(w) >= 2 && canSplit(s, w)) mk({ w: w.id }, [worldPick(w.id)]); return;
    case "Monsoon": if (tp.some((i) => isLone(s, i))) mk({}); return;
    case "Steam Explosion": pairs(tp, (a, b) => isAdj(s, a, b)); return;
    case "Tornado": pairs(tp); return;
    case "Hurricane": for (const Q of [0, 1]) if (worldsOf(s, Q).some((w) => worldSize(w) >= 2 && canSplit(s, w))) mk({ P2: Q }, [{ k: "player", P: Q }]); return;
    case "Earthquake": for (const Q of [0, 1]) if (worldsOf(s, Q).some((w) => worldSize(w) >= 2 && canSplit(s, w))) mk({ P2: Q }, [{ k: "player", P: Q }]); return;
    case "Equinox": { // return 3 cards from your void, chosen in any order
      const v = [...new Set(s.p[P].void)];
      if (!v.length) return;
      if (v.length <= 3) { mk({ cards: v }, v.map((c) => ({ k: "void", card: c }))); return; }
      for (const a of v) for (const b of v) for (const c of v) if (a !== b && a !== c && b !== c) mk({ cards: [a, b, c] }, [{ k: "void", card: a }, { k: "void", card: b }, { k: "void", card: c }]);
      return;
    }
    case "Solar Flare": if (tp.some((i) => one(i) && canRemove(s, i, src))) mk({}); return;
    case "Deluge": for (let a = 0; a < tw.length; a++) for (let b = a + 1; b < tw.length; b++) mk({ w: tw[a].id, w2: tw[b].id }, [worldPick(tw[a].id), worldPick(tw[b].id)]); return;
    case "Jet Stream": if (Object.values(s.worlds).some((w) => worldSize(w) >= 2 && canSplit(s, w))) mk({}); return;
    case "World Quake": if (Object.values(s.worlds).some((w) => worldSize(w) >= 2 && canSplit(s, w))) mk({}); return;
    case "Unmaking": if (tp.some((i) => canRemove(s, i, src))) mk({}); return;
    default: throw new Error("force not implemented: " + n);
  }
}

function metaMoves(s, P, id, out, inEcho) {
  const n = C[id].name; const pl = s.p[P], opp = s.p[1 - P];
  const mk = (m, picks) => out.push(Object.assign({ id, face: "meta" }, m, { picks: picks || [] }));
  switch (n) {
    case "Echo": {
      if (inEcho) return;
      const seen = new Set();
      for (const v of pl.void) {
        if (seen.has(v) || C[v].name === "Echo") continue; seen.add(v);
        const sub = [];
        cardMoves(s, P, v, sub, true);
        for (const m of sub) mk({ sub: m }, [{ k: "void", card: v }, { k: "face", face: m.face }].concat(m.picks));
      }
      return;
    }
    case "Ebb": { const i = lastCommon(s, 1 - P); if (i && (i.kind !== "perm" || canRemove(s, i, null))) mk({ t: i.id }, []); return; }
    case "Verge": if (pl.played + 1 < s.cap) mk({}); return;
    case "Horizon": { const seen = new Set(); for (const v of opp.binder) if (!seen.has(v)) { seen.add(v); mk({ card: v }, [{ k: "obinder", card: v }]); } return; }
    case "Hollow": { const seen = new Set(); for (const v of pl.void) if (!seen.has(v)) { seen.add(v); mk({ card: v }, [{ k: "void", card: v }]); } return; }
    case "Calm": if (!s.calm) mk({}); return;
    case "Lull": if (!opp.passed && !opp.skip) mk({}); return;
    case "Gap": for (const w of Object.values(s.worlds)) if (permsIn(s, w).some((i) => canRemove(s, i, null))) mk({ w: w.id }, [worldPick(w.id)]); return;
    default: throw new Error("meta not implemented: " + n);
  }
}
function lastCommon(s, P) {
  const L = s.p[P].commons;
  for (let k = L.length - 1; k >= 0; k--) { const i = s.inst[L[k]]; if (i) return i; }
  return null;
}
function cardMoves(s, P, id, out, inEcho) {
  const d = C[id];
  if (d.meta) { metaMoves(s, P, id, out, inEcho); return; }
  permMoves(s, P, id, out);
  if (!s.calm) forceMoves(s, P, id, out);
}
// what P may do now (empty when they can't play)
export function legalMoves(s, P) {
  const pl = s.p[P];
  if (s.phase !== "turn" || s.turn !== P || pl.passed || pl.played >= s.cap) return [];
  return movesFor(s, P, s.extras.length > 0 && !s.extras.includes("any"));
}
// every move P's binder allows on this table, whoever's turn it is (for the computer's lookahead)
export function movesFor(s, P, fireOnly) {
  const pl = s.p[P];
  const out = []; const seen = new Set();
  for (const id of pl.binder) {
    if (seen.has(id)) continue; seen.add(id);
    if (fireOnly && !C[id].fireCard) continue;
    cardMoves(s, P, id, out, false);
  }
  return out;
}

// ---------------------------------------------------------------- applying a move
const removeOne = (arr, id) => { const k = arr.indexOf(id); if (k >= 0) arr.splice(k, 1); return k >= 0; };
// apply m for P: the card leaves the binder (or the void, for Echo), the effect happens.
// Returns { removed, returned, text }.
export function applyMove(s, P, m, fromVoid) {
  const pl = s.p[P], opp = s.p[1 - P]; const d = C[m.id];
  const ev = { removed: [], returned: [], moved: 0 };
  if (fromVoid) removeOne(pl.void, m.id);
  else {
    removeOne(pl.binder, m.id); pl.played++;
    if (s.extras.length) { const k = d.fireCard && s.extras.includes("fire") ? s.extras.indexOf("fire") : s.extras.indexOf("any"); s.extras.splice(k >= 0 ? k : 0, 1); }
  }
  const noteCommon = (iid) => { if (d.rarity === "C" && iid) pl.commons.push(iid); };
  const gone = (i, where) => { if (!i || !s.inst[i.id]) return; (where === "void" ? ev.removed : ev.returned).push(i.card); leave(s, i, where); };
  if (m.face === "perm") {
    const i = placeFresh(s, P, m.id, m); noteCommon(i.id);
    const n = d.name;
    if (n === "Snowfield" && m.t && s.inst[m.t]) gone(s.inst[m.t], "binder");
    if (n === "Bluff" && m.t && s.inst[m.t] && s.worlds[m.w2]) { moveTo(s, s.inst[m.t], s.worlds[m.w2], m.cell2); ev.moved++; }
    if (n === "Hanging Valley" && m.t && s.inst[m.t] && s.inst[m.t2]) swap(s, s.inst[m.t], s.inst[m.t2]);
    if (n === "Lava Flow") s.extras.push("fire");
    dirty(s);
    return ev;
  }
  if (m.face === "meta") {
    pl.void.push(m.id);
    switch (d.name) {
      case "Echo": applyMove(s, P, m.sub, true); break; // READING: the card from the void doesn't count toward the cap
      case "Ebb": { const i = s.inst[m.t]; if (i) gone(i, "void"); break; }
      case "Verge": s.extras.push("any", "any"); break;
      case "Horizon": if (removeOne(opp.binder, m.card)) opp.void.push(m.card); break;
      case "Hollow": if (removeOne(pl.void, m.card)) pl.binder.push(m.card); break;
      case "Calm": s.calm = true; break;
      case "Lull": opp.skip = true; break;
      case "Gap": { const w = s.worlds[m.w]; if (w) for (const i of permsIn(s, w)) if (canRemove(s, i, null)) gone(i, "void"); break; }
    }
    dirty(s);
    return ev;
  }
  // force face
  const n = d.fname; const src = { card: m.id, caster: P, fid: null };
  if (d.fdur === "round") {
    const f = newInst(s, P, m.id, "force", { t: m.t || null, t2: m.t2 || null, src: m.src || null, w: m.w || null, w2: m.w2 || null });
    if (n === "Whiteout") f.until = P; // ends at the start of the caster's next turn
    noteCommon(f.id);
    dirty(s);
    return ev;
  }
  pl.void.push(m.id);
  const T = m.t ? s.inst[m.t] : null, T2 = m.t2 ? s.inst[m.t2] : null, Wd = m.w ? s.worlds[m.w] : null;
  if (REMOVE_ONE[n] !== undefined || n === "Thunderstorm" || n === "Lightning" || n === "Collapse") gone(T, "void");
  else if (MOVE_ONE[n] !== undefined || n === "Drift" || n === "Whirl") { if (T && s.worlds[m.w2]) { moveTo(s, T, s.worlds[m.w2], m.cell); ev.moved++; } }
  else if (OWN_WORLD_ONE[n] !== undefined || n === "Squall") { if (T) { ownWorld(s, T); ev.moved++; } }
  else if (REMOVE_KIND[n] !== undefined) { if (Wd) for (const i of permsIn(s, Wd)) if (!permIgnores(s, i, src) && shows(s, i, REMOVE_KIND[n]) && canRemove(s, i, src)) gone(i, "void"); }
  else switch (n) {
    case "Flare-up": { const f = s.inst[m.f]; if (f) gone(f, "void"); break; }
    case "Low Tide": case "Blizzard": case "Undertow": case "Mudflow": if (Wd) returnWorld(s, Wd, ev); break; // READING: returning isn't removal, so "can't be removed" doesn't stop it
    case "Crosswind": case "Eddy": if (T && T2) { swap(s, T, T2); ev.moved += 2; } break;
    case "Vent": gone(T, "binder"); break;
    case "Tremor": if (Wd) splitWorld(s, Wd, src); break;
    case "Flood": case "Tornado": gone(T, "binder"); gone(T2, "binder"); break;
    case "Gale": {
      if (T && s.worlds[m.w2] && s.worlds[m.w2].cells[m.cell] === null) { moveTo(s, T, s.worlds[m.w2], m.cell); ev.moved++; }
      const w3 = s.worlds[m.w3]; if (T2 && w3) { const c = w3.cells[m.cell3] === null ? m.cell3 : openCells(w3)[0]; if (c !== undefined && worldSize(w3) < geoOf(w3).cap) { moveTo(s, T2, w3, c); ev.moved++; } }
      break;
    }
    case "Gale Force":
      m.ts.forEach((iid, k) => {
        const i = s.inst[iid], w2 = s.worlds[m.ds[k].w2];
        if (!i || !w2 || worldSize(w2) >= geoOf(w2).cap) return;
        const c = w2.cells[m.ds[k].cell] === null ? m.ds[k].cell : openCells(w2)[0];
        if (c !== undefined) { moveTo(s, i, w2, c); ev.moved++; }
      });
      break;
    case "Thaw": { const f = s.inst[m.f]; if (f) gone(f, "void"); break; }
    case "Whirlwind": for (const i of [T, T2]) if (i && s.inst[i.id] && worldSize(s.worlds[i.w]) >= 2) { ownWorld(s, i); ev.moved++; } break;
    case "Cave-in": gone(T, "void"); gone(T2, "void"); break;
    case "Typhoon": if (Wd) scatter(s, Wd, src); break;
    case "Monsoon": for (const i of perms(s)) if (isLone(s, i) && !permIgnores(s, i, src)) gone(i, "binder"); break;
    case "Hurricane": for (const w of worldsOf(s, m.P2)) if (!worldIgnores(s, w.id, src) && canSplit(s, w)) scatter(s, w, src); break; // READING: scatters that player's worlds
    case "Earthquake": for (const w of worldsOf(s, m.P2)) if (!worldIgnores(s, w.id, src)) splitWorld(s, w, src); break;
    case "Equinox": for (const c of m.cards || []) if (removeOne(pl.void, c)) pl.binder.push(c); break;
    case "Solar Flare": for (const i of perms(s)) if (one(i) && !permIgnores(s, i, src) && canRemove(s, i, src)) gone(i, "void"); break;
    case "Jet Stream": for (const w of Object.values(s.worlds)) if (canSplit(s, w)) scatter(s, w, src); break;
    case "World Quake": for (const w of Object.values(s.worlds)) if (canSplit(s, w)) scatter(s, w, src); break;
    case "Unmaking": for (const i of perms(s)) if (!permIgnores(s, i, src) && canRemove(s, i, src)) gone(i, "void"); break;
    default: throw new Error("once force not implemented: " + n);
  }
  dirty(s);
  return ev;
}

// ---------------------------------------------------------------- turns and rounds
const say = (s, text, P) => { s.log.push({ r: s.r, P, text }); };
const verb = (name, third, base) => (name === "You" ? base : third); // "You pass", "Computer passes"
// Moves the game to the next decision point: the player to act, or a round or contest end.
export function advance(s) {
  for (let guard = 0; guard < 8; guard++) {
    if (s.phase !== "turn") return;
    if (s.p[0].passed && s.p[1].passed) { endRound(s, null); return; }
    const P = s.turn, pl = s.p[P];
    if (pl.passed) { s.turn = 1 - P; continue; }
    if (!s.turnStarted) {
      s.turnStarted = true;
      for (const f of forces(s)) if (fname(f) === "Whiteout" && f.until === P) { drop(s, f.id); toPile(s, f, "void"); dirty(s); say(s, "Whiteout ends.", P); }
      const sc = score(s);
      if (ownsPerm(s, P, "Cradle") && hasEach(sc[P].all, knob(s, "cradleEach"))) { say(s, `${pl.name} ${verb(pl.name, "has", "have")} ${knob(s, "cradleEach")} of each affinity: Cradle wins the contest.`, P); endContest(s, P, "Cradle"); return; }
      if (archipelagoWins(s, P, sc)) { say(s, `${pl.name} ${verb(pl.name, "has", "have")} ${knob(s, "archipelagoWater")} water: Archipelago wins the round.`, P); endRound(s, P, "Archipelago"); return; }
      if (pl.skip) { pl.skip = false; say(s, `${pl.name} ${verb(pl.name, "skips", "skip")} this turn (Lull).`, P); endTurn(s); continue; }
    }
    if (pl.played >= s.cap || !legalMoves(s, P).length) {
      if (s.extras.length) { endTurn(s); continue; }
      pl.passed = true; say(s, `${pl.name} ${verb(pl.name, "passes", "pass")}${pl.played >= s.cap ? " (at the cap)" : " (nothing to play)"}.`, P);
      endTurn(s); continue;
    }
    return; // waiting for P
  }
}
export function endTurn(s) { s.extras = []; s.turn = 1 - s.turn; s.turnStarted = false; }
// Archipelago: checked at the start of its owner's turn, at 10 water (Cam, Nov 7, for the uncapped one-round test;
// earlier the same day it was the end of the turn at 8, and before that the start of the turn at 8)
export const ARCHIPELAGO_WATER = KNOBS.archipelagoWater; // kept for older imports
export const archipelagoWins = (s, P, sc) => ownsPerm(s, P, "Archipelago") && sc[P].water >= knob(s, "archipelagoWater");
// P plays m; returns the move's record
export function play(s, P, m) {
  const text = describe(s, P, m);
  const ev = applyMove(s, P, m);
  say(s, text, P);
  const sc = score(s);
  const dw = [0, 1].filter((Q) => decisiveWorld(sc, Q));
  if (dw.length) {
    const Q = dw.includes(P) ? P : dw[0];
    say(s, `${s.p[Q].name} ${verb(s.p[Q].name, "has", "have")} a world worth ${knob(s, "perfectWorld")} world points and ${verb(s.p[Q].name, "wins", "win")} the contest.`, Q);
    s.decisive = Q; endContest(s, Q, "3-point world"); return ev;
  }
  if (!(s.extras.length && s.p[P].played < s.cap)) endTurn(s);
  advance(s);
  return ev;
}
export function pass(s, P) {
  if (s.extras.length) { say(s, `${s.p[P].name} ${verb(s.p[P].name, "ends their", "end your")} turn.`, P); endTurn(s); advance(s); return; }
  s.p[P].passed = true; say(s, `${s.p[P].name} ${verb(s.p[P].name, "passes", "pass")}.`, P);
  endTurn(s); advance(s);
}
function endRound(s, forced, why) {
  const sc = score(s);
  let winner = forced;
  if (forced === null) { const o = outcome(sc, 0); winner = o === 1 ? 0 : o === -1 ? 1 : null; }
  const rec = { r: s.r, winner, why: why || (winner === null ? "draw" : sc[0].pts !== sc[1].pts ? "world points" : "tie-break"), score: sc.map((x) => ({ pts: x.pts, tie: x.tie, worlds: x.worlds })) };
  s.rounds = s.rounds.concat([rec]);
  if (winner === null) { s.p[0].wins++; s.p[1].wins++; } else s.p[winner].wins++; // READING: a drawn round counts for both (Gwent)
  say(s, winner === null ? `Round ${s.r} is a draw.` : `${s.p[winner].name} ${verb(s.p[winner].name, "wins", "win")} round ${s.r} (${rec.why}).`, winner);
  // keep a copy of the table as it stood, for showing after the round
  s.ended = { inst: Object.fromEntries(Object.entries(s.inst).map(([k, i]) => [k, Object.assign({}, i)])), worlds: Object.fromEntries(Object.entries(s.worlds).map(([k, w]) => [k, Object.assign({}, w, { cells: w.cells.slice() })])) };
  // round end: permanence that returns goes to the binder; everything else to the void
  for (const i of Object.values(s.inst)) {
    const back = i.kind === "perm" && /^Returns at round end/.test(C[i.card].ptext || "");
    drop(s, i.id); toPile(s, i, back ? "binder" : "void");
  }
  s.worlds = {}; s.calm = false; s.extras = []; dirty(s);
  for (const pl of s.p) { pl.played = 0; pl.passed = false; pl.skip = false; pl.commons = []; }
  const [a, b] = [s.p[0].wins, s.p[1].wins];
  const bestOf = s.bestOf || 3, need = Math.ceil(bestOf / 2);
  if (a >= need || b >= need || s.r >= bestOf) { endContest(s, a > b ? 0 : b > a ? 1 : null, "rounds"); return; }
  s.phase = "roundOver";
}
export function nextRound(s) {
  if (s.phase !== "roundOver") return;
  s.ended = null; s.r++; s.opener = 1 - s.opener; s.turn = s.opener; s.turnStarted = false; s.phase = "turn"; // READING: openers alternate
  advance(s);
}
function endContest(s, winner, why) {
  s.phase = "contestOver"; s.winner = winner; s.why = why;
  if (why !== "rounds") say(s, `Contest over: ${winner === null ? "a draw" : s.p[winner].name + " " + verb(s.p[winner].name, "wins", "win")}.`, winner);
}

// ---------------------------------------------------------------- words
const possessive = (name) => (name === "You" ? "your" : /s$/.test(name) ? name + "'" : name + "'s");
export function worldLabel(s, wid, me) {
  const w = s.worlds[wid]; if (!w) return "the new world";
  return `${w.owner === me ? "your" : possessive(s.p[w.owner].name)} world ${w.n}`;
}
function permLabel(s, iid) { const i = s.inst[iid]; return i ? C[i.card].name : "a permanence"; }
export function describePick(s, pk, me) {
  switch (pk.k) {
    case "cell": return pk.w === "new" ? "a new world" : `${worldLabel(s, pk.w, me)}, ${CELL_NAMES[pk.cell] || "cell " + pk.cell}`;
    case "perm": { const i = s.inst[pk.id]; return i ? `${C[i.card].name} (${worldLabel(s, i.w, me)})` : "?"; }
    case "world": return worldLabel(s, pk.id, me);
    case "player": return pk.P === me ? "you" : s.p[pk.P].name;
    case "force": { const f = s.inst[pk.id]; return f ? `${fname(f)} (${f.owner === me ? "yours" : possessive(s.p[f.owner].name).replace(/'s?$/, "") + "'s"})` : "?"; }
    case "void": case "obinder": return C[pk.card].meta ? C[pk.card].name : `${C[pk.card].name} / ${C[pk.card].fname}`;
    case "face": return pk.face === "perm" ? "as a permanence" : pk.face === "force" ? "as a force" : "";
    default: return "";
  }
}
export function describe(s, P, m) {
  const d = C[m.id]; const who = s.p[P].name;
  if (m.face === "perm") {
    let t = `${who} played ${d.name} into ${m.w === "new" ? "a new world" : worldLabel(s, m.w, -1)}`;
    if (d.name === "Snowfield" && m.t) t += `, returning ${permLabel(s, m.t)}`;
    if (d.name === "Bluff" && m.t) t += `, moving ${permLabel(s, m.t)} to ${worldLabel(s, m.w2, -1)}`;
    if (d.name === "Hanging Valley" && m.t) t += `, swapping ${permLabel(s, m.t)} and ${permLabel(s, m.t2)}`;
    return t + ".";
  }
  if (m.face === "meta") {
    if (d.name === "Echo") return `${who} played Echo: ${describe(s, P, m.sub).replace(who + " played ", "")}`.replace(/\.$/, "") + " from the void.";
    const extra = m.card ? ` (${C[m.card].name})` : m.w ? ` on ${worldLabel(s, m.w, -1)}` : m.t ? ` on ${permLabel(s, m.t)}` : "";
    return `${who} played ${d.name}${extra}.`;
  }
  const bits = [];
  if (m.t) bits.push(permLabel(s, m.t));
  if (m.t2) bits.push(permLabel(s, m.t2));
  if (m.ts) bits.push(...m.ts.map((x) => permLabel(s, x)));
  if (m.src) bits.push("copying " + permLabel(s, m.src));
  if (m.w) bits.push(worldLabel(s, m.w, -1));
  if (m.w2 && !m.t) bits.push(worldLabel(s, m.w2, -1));
  if (m.P2 !== undefined) bits.push(s.p[m.P2].name);
  if (m.f) bits.push(fname(s.inst[m.f]));
  if (m.cards) return `${who} played ${d.fname} (${d.name}'s force), returning ${m.cards.map((c) => C[c].name).join(", ")} to their binder.`;
  return `${who} played ${d.fname} (${d.name}'s force)${bits.length ? " on " + bits.join(", ") : ""}.`;
}
