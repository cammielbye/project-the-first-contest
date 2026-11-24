// Branch B rules engine (Nov 23). Pure functions on one plain state object, shared by the table, the computer and the
// tests. Rules settled by Cam (Nov 18-20, the Branch B doc): 24-card binders, best of one, whole turns back and forth,
// 9 each, then a shared 10th that both players lock in and reveal together; each turn up to one landscape played and up
// to one force used; using a force flips the card, so its front pips stop counting and its back pips count instead;
// a world (up to 2x2) scores a world point for one of each element or four of one, as many as it holds; a world worth
// 3 is a perfect world and wins at once; otherwise most world points after turn 10 wins.
// Claude's readings (marked in the doc): a landscape can't use its force the turn it's played; a card flipped by
// another card's force doesn't use its own force unless the text says "Its force happens"; "Next turn, flip this back"
// happens at the start of its owner's next turn; in the shared 10th, forces resolve in turn order (first player first).

export const CARDS = [
  ["Spring", ["water"], "Overflow", [], "Play another permanence this turn."],
  ["Lake", ["water", "water"], "Flood", ["water"], "Return an opponent's permanence with one pip to its owner's binder."],
  ["Tidal Flat", ["water", "earth"], "High Tide", ["water", "water"], "Next turn, flip this back.", 1],
  ["Cloud Forest", ["water", "earth", "air"], "Downpour", ["water"], "Flip back each flipped permanence in this world."],
  ["Glacier", ["water", "water", "earth"], "Meltwater", ["water", "water"], "Return a flipped permanence of yours to your binder."],
  ["Ocean", ["water", "water", "water", "water"], "Tsunami", ["water", "water"], "Return each permanence with one pip in one opponent's world to its owner's binder."],
  ["Hills", ["earth"], "Rockslide", [], "Swap two of your permanences in different worlds."],
  ["Plateau", ["earth", "earth"], "Uplift", ["earth", "earth"], "Join two of your worlds into one, if they fit in a 2×2."],
  ["Cavern", ["earth", "earth"], "Cave-in", ["earth"], "Your opponent's forces can't touch other permanences in this world."],
  ["Forest", ["water", "earth"], "Wildfire", ["fire"], "Flip an opponent's permanence with one pip. Next turn, flip this back.", 1],
  ["Fault Line", ["earth", "fire"], "Earthquake", [], "Split one of your opponent's worlds into two."],
  ["Highlands", ["earth", "earth", "earth"], "Erosion", ["earth", "earth"], "Move another permanence in this world to another of your worlds."],
  ["Ash Plain", ["fire"], "Kindling", [], "Flip another permanence in this world. Its force happens."],
  ["Lava Field", ["fire", "fire"], "Lava Flow", ["fire"], "Return another permanence in this world to your binder. Play another permanence this turn."],
  ["Volcano", ["earth", "fire"], "Eruption", ["fire"], "Flip an opponent's permanence."],
  ["Desert", ["fire", "fire", "air"], "Mirage", ["any", "any"], ""],
  ["Hot Springs", ["water", "fire"], "Geyser", ["water"], "Play another permanence this turn. Next turn, flip this back.", 1],
  ["Caldera", ["fire", "fire", "fire"], "Supervolcano", ["fire", "fire"], "Flip every other permanence, yours and your opponent's."],
  ["Meadow", ["air"], "Gust", [], "Move a permanence of yours to another world, or a new one."],
  ["Trade Winds", ["water", "air"], "Hurricane", ["air"], "Move an opponent's permanence into a new world of its own."],
  ["Cliffs", ["earth", "air"], "Seedwind", ["air"], "Play another permanence this turn, into a different world."],
  ["Dunes", ["fire", "air"], "Wandering Dunes", ["fire", "air"], "Move this to another of your worlds, or a new one."],
  ["Cloud Sea", ["water", "air", "air"], "Rain", ["water"], "Flip back a permanence of yours."],
  ["Peak", ["air", "air", "air"], "Gale", ["air", "air"], "Move up to two permanences of yours to other worlds, or new ones."],
].map(([n, p, b, bp, t, fb], i) => ({ i, no: i + 1, n, p, b, bp, t, fb: !!fb, away: false, ft: "" }));
// Cam, Nov 23: "if we add some of the single pip cards to say 'can be played on an opponents world' - it would make
// their permanences into interaction and would be a way to prevent perfect worlds more easily." All four single-pip
// cards, one per element. Such a card stays its owner's: it counts toward the world it's in, its owner can use its
// force, and it returns to its owner's binder.
for (const n of ["Spring", "Hills", "Ash Plain", "Meadow"]) { const c = CARDS.find((x) => x.n === n); c.away = true; c.ft = "Can be played on an opponent's world."; }

export const E = ["water", "earth", "fire", "air"];
const K = Object.fromEntries(CARDS.map((c) => [c.n, c.i]));
export const NAMES = ["Player 1", "Player 2"];

// ---------------------------------------------------------------- state
// Binders by how far into the game a player is (Cam, Nov 23: cards are found on a steep curve by pip count, so most
// binders hold few big cards). The same stages as the simulations: early, every card with 1 or 2 pips; mid, that plus
// one card with 3 pips picked at random; late, the whole pool.
export const STAGES = ["early", "mid", "late"];
export function binderFor(stage) {
  const small = CARDS.filter((c) => c.p.length <= 2).map((c) => c.i);
  if (stage === "early") return small;
  if (stage === "mid") { const three = CARDS.filter((c) => c.p.length === 3); return [...small, three[Math.floor(Math.random() * three.length)].i].sort((a, b) => a - b); }
  return CARDS.map((c) => c.i);
}
export function newGame(first = Math.random() < 0.5 ? 0 : 1, names = NAMES, stage = "late") {
  const s = {
    v: 1, first, half: 0, phase: "turn", names: names.slice(), seq: 0, ts: 0, quiet: false,
    played: 0, forced: 0, extra: 0, notWith: null, pending: null, queue: [],
    stage: [{}, {}], locked: [false, false], winner: null,
    stage, inst: {}, P: [0, 1].map(() => { const b = binderFor(stage); return { deck: b.slice(), binder: b, worlds: [] }; }), log: [],
  };
  say(s, null, `${vb(s, first, "goes", "go")} first (coin toss).`);
  say(s, null, `Turn 1: ${s.names[first]}.`);
  return s;
}
export const clone = (s) => {
  const log = s.log; s.log = [];
  const c = JSON.parse(JSON.stringify(s));
  s.log = log; c.log = []; c.quiet = true;
  return c;
};
function say(s, P, text) { if (!s.quiet) s.log.push({ P, text, ts: s.ts }); }
// "You" takes the plural verb and "your" (the computer table names its player You)
const vb = (s, P, one, many) => `${s.names[P]} ${s.names[P] === "You" ? many : one}`;
const poss = (s, P) => (s.names[P] === "You" ? "your" : `${s.names[P]}'s`);

export const shared = (s) => s.half >= 18;
export const turnNo = (s) => (shared(s) ? 10 : Math.floor(s.half / 2) + 1);
export function active(s) {
  if (s.phase === "over") return null;
  if (s.pending) return s.pending.P;
  if (s.phase === "lock") return s.locked[s.first] ? 1 - s.first : s.first;
  if (s.phase === "resolve") return null;
  return s.half % 2 === 0 ? s.first : 1 - s.first;
}
export const card = (s, id) => CARDS[s.inst[id].c];
export const pipsOf = (s, id) => (s.inst[id].f ? CARDS[s.inst[id].c].bp : CARDS[s.inst[id].c].p);
export function findCard(s, id) {
  for (const side of [0, 1]) {
    const W = s.P[side].worlds;
    for (let w = 0; w < W.length; w++) { const k = W[w].indexOf(id); if (k >= 0) return { side, w, k }; }
  }
  return null;
}
const worldOf = (s, id) => { const f = findCard(s, id); return f ? s.P[f.side].worlds[f.w] : null; };
export const sideCards = (s, P) => s.P[P].worlds.flat(); // the cards in P's worlds, whoever owns them
export const ownedCards = (s, P) => [0, 1].flatMap((X) => s.P[X].worlds.flat()).filter((id) => s.inst[id].o === P);

// ---------------------------------------------------------------- scoring
const PTS = new Map();
export function pointsOfPips(list) {
  const key = list.slice().sort().join();
  let v = PTS.get(key);
  if (v === undefined) { v = pointsRaw(list); if (PTS.size > 50000) PTS.clear(); PTS.set(key, v); }
  return v;
}
function pointsRaw(list) {
  const c = { water: 0, earth: 0, fire: 0, air: 0 };
  let any = 0;
  for (const p of list) p === "any" ? any++ : c[p]++;
  let best = 0;
  const rec = (i) => {
    if (i === any) {
      const m = Math.min(c.water, c.earth, c.fire, c.air);
      for (let k = 0; k <= m; k++) {
        const v = k + Math.floor((c.water - k) / 4) + Math.floor((c.earth - k) / 4) + Math.floor((c.fire - k) / 4) + Math.floor((c.air - k) / 4);
        if (v > best) best = v;
      }
      return;
    }
    for (const e of E) { c[e]++; rec(i + 1); c[e]--; }
  };
  rec(0);
  return best;
}
export const worldPts = (s, ids) => pointsOfPips(ids.flatMap((id) => pipsOf(s, id)));
export const total = (s, P) => s.P[P].worlds.reduce((a, w) => a + worldPts(s, w), 0);

function checkWin(s) {
  if (s.winner) return;
  const perf = [0, 1].map((P) => s.P[P].worlds.some((w) => worldPts(s, w) >= 3));
  if (!perf[0] && !perf[1]) return;
  if (perf[0] && perf[1]) {
    const d = total(s, 0) - total(s, 1);
    s.winner = { P: d > 0 ? 0 : d < 0 ? 1 : null, why: "both-perfect" };
  } else s.winner = { P: perf[0] ? 0 : 1, why: "perfect" };
  s.phase = "over"; s.pending = null; s.queue = [];
  say(s, s.winner.P, s.winner.P === null ? "Both players make a perfect world at once with equal points: a draw." : `${vb(s, s.winner.P, "has", "have")} a perfect world (3 world points in one world) and ${s.names[s.winner.P] === "You" ? "win" : "wins"}.`);
}
function finish(s) {
  if (s.winner) return;
  const d = total(s, 0) - total(s, 1);
  s.winner = { P: d > 0 ? 0 : d < 0 ? 1 : null, why: "points" };
  s.phase = "over"; s.pending = null;
  say(s, null, `Contest over: ${s.names[0]} ${total(s, 0)}, ${s.names[1]} ${total(s, 1)}. ${s.winner.P === null ? "A draw." : `${vb(s, s.winner.P, "wins", "win")}.`}`);
}

// ---------------------------------------------------------------- turns
function startTurn(s) {
  const owners = shared(s) ? [0, 1] : [active(s)];
  for (const P of owners)
    for (const id of ownedCards(s, P))
      if (s.inst[id].f && card(s, id).fb) { s.inst[id].f = false; say(s, P, `${card(s, id).b} flips back to ${card(s, id).n}.`); }
  s.played = 0; s.forced = 0; s.extra = 0; s.notWith = null;
}
export function endTurn(s) {
  if (s.phase !== "turn" || s.pending) return false;
  s.ts++;
  if (s.half < 17) {
    s.half++;
    say(s, null, `Turn ${turnNo(s)}: ${s.names[active(s)]}.`);
    startTurn(s);
  } else {
    s.half = 18; s.phase = "lock"; s.stage = [{}, {}]; s.locked = [false, false];
    say(s, null, "Turn 10, shared: both players lock in a landscape and a force, then reveal together.");
    startTurn(s);
  }
  checkWin(s);
  return true;
}

// ---------------------------------------------------------------- playing landscapes
export function legalPlays(s, P) {
  if (P === null || P === undefined || s.pending) return [];
  if (s.phase === "turn") { if (active(s) !== P || s.played >= 1 + s.extra) return []; }
  else if (s.phase === "lock") { if (active(s) !== P || s.stage[P].play) return []; }
  else return [];
  const W = s.P[P].worlds, out = [];
  const blocked = s.phase === "turn" && s.notWith && s.inst[s.notWith] ? worldOf(s, s.notWith) : null;
  for (const ci of s.P[P].binder) {
    W.forEach((w, wi) => { if (w.length < 4 && w !== blocked) out.push({ ci, w: wi, side: P }); });
    out.push({ ci, w: "new", side: P });
    if (CARDS[ci].away) s.P[1 - P].worlds.forEach((w, wi) => { if (w.length < 4 && w !== blocked) out.push({ ci, w: wi, side: 1 - P }); });
  }
  return out;
}
export function play(s, P, ci, w, side = P) {
  if (!legalPlays(s, P).some((m) => m.ci === ci && m.w === w && m.side === side)) return false;
  s.ts++;
  if (s.phase === "lock") { s.stage[P].play = { ci, w, side }; say(s, P, `${vb(s, P, "chooses", "choose")} a landscape (hidden until the reveal).`); return true; }
  place(s, P, ci, w, side);
  s.played++;
  s.notWith = null;
  checkWin(s);
  return true;
}
function place(s, P, ci, w, side = P) {
  const id = "c" + ++s.seq;
  s.inst[id] = { c: ci, o: P, f: false, h: s.half };
  s.P[P].binder.splice(s.P[P].binder.indexOf(ci), 1);
  const W = s.P[side].worlds, into = w !== "new" && W[w] && W[w].length < 4;
  if (into) W[w].push(id); else s.P[P].worlds.push([id]);
  say(s, P, `${vb(s, P, "plays", "play")} ${CARDS[ci].n}${!into ? " into a new world" : side !== P ? ` into ${poss(s, side)} world ${w + 1}` : ` into world ${w + 1}`}.`);
  return id;
}

// ---------------------------------------------------------------- forces
export function canUseForce(s, P, id) {
  const i = s.inst[id];
  if (!i || s.pending || i.f) return false;
  if (!findCard(s, id) || i.o !== P) return false;
  if (s.phase === "turn") return active(s) === P && i.h !== s.half && s.forced < 1;
  if (s.phase === "lock") return active(s) === P && !s.stage[P].force;
  return false;
}
export function beginForce(s, P, id) {
  if (!canUseForce(s, P, id)) return false;
  s.ts++;
  if (s.phase === "lock") { s.stage[P].force = id; say(s, P, `${vb(s, P, "chooses", "choose")} a force (hidden until the reveal).`); return true; }
  s.forced++;
  s.pending = { P, id, picks: [] };
  settle(s);
  return true;
}
export function cancelForce(s) {
  if (!s.pending || s.pending.picks.length || s.pending.locked) return false;
  s.forced = Math.max(0, s.forced - 1);
  s.pending = null; s.ts++;
  return true;
}
export function choices(s) {
  const pd = s.pending;
  if (!pd || !s.inst[pd.id]) return null;
  const st = FORCES[s.inst[pd.id].c].step?.(s, pd.P, pd.id, pd.picks);
  return st && st.opts.length ? st : null;
}
const same = (a, b) => a.t === b.t && a.id === b.id && a.side === b.side && a.w === b.w;
export function pick(s, opt) {
  const st = choices(s);
  if (!st) return false;
  if (opt.t === "stop") { if (!st.canStop) return false; s.pending.stopped = true; }
  else { if (!st.opts.some((o) => same(o, opt))) return false; s.pending.picks.push(opt); }
  s.ts++;
  settle(s);
  return true;
}
// resolve the pending force once it needs no more choices
function settle(s) {
  while (s.pending && (s.pending.stopped || !choices(s))) {
    if (!s.inst[s.pending.id] || !findCard(s, s.pending.id)) { // its card left play before its turn to resolve
      s.pending = s.queue.shift() || null;
      if (s.phase === "resolve" && !s.pending) finish(s);
      continue;
    }
    const { P, id, picks, nested } = s.pending;
    s.pending = null;
    const c = card(s, id);
    if (!nested) { s.inst[id].f = true; say(s, P, `${vb(s, P, "uses", "use")} ${c.n}: ${c.b}.${c.t ? ` "${c.t}"` : ""}`); }
    else say(s, P, `${c.b} happens.`);
    const next = FORCES[c.i].apply?.(s, P, id, picks);
    if (next) s.pending = next;
    else if (s.queue.length) s.pending = s.queue.shift();
    checkWin(s);
    if (s.phase === "resolve" && !s.pending) finish(s);
  }
}

// helpers for the forces
// a face-down Cave-in shields the other cards in its world from its owner's opponent's forces
const caveIn = (s, x, P) => s.inst[x].f && s.inst[x].c === K["Cavern"] && s.inst[x].o !== P;
const guarded = (s, id, P) => { const w = worldOf(s, id); return !!w && w.some((x) => x !== id && caveIn(s, x, P)); };
const worldGuarded = (s, side, w, P) => s.P[side].worlds[w].some((x) => caveIn(s, x, P));
const oppTargets = (s, P, test) => ownedCards(s, 1 - P).filter((x) => !guarded(s, x, P) && test(x)).map((id) => ({ t: "card", id }));
const ownCards = (s, P, test) => ownedCards(s, P).filter(test).map((id) => ({ t: "card", id }));
function dests(s, P, id, allowNew) { // other worlds of P with room for id, and a new world
  const W = s.P[P].worlds, cur = worldOf(s, id), out = [];
  W.forEach((w, wi) => { if (w !== cur && w.length < 4) out.push({ t: "world", side: P, w: wi }); });
  if (allowNew && cur && (cur.length > 1 || findCard(s, id).side !== P)) out.push({ t: "new", side: P });
  return out;
}
function moveTo(s, id, d) {
  const f = findCard(s, id), to = d.side ?? f.side;
  const target = d.t === "new" ? null : s.P[to].worlds[d.w];
  s.P[f.side].worlds[f.w].splice(f.k, 1);
  if (target) target.push(id); else s.P[to].worlds.push([id]);
  for (const X of [0, 1]) s.P[X].worlds = s.P[X].worlds.filter((w) => w.length);
}
function toBinder(s, id) {
  const f = findCard(s, id), c = s.inst[id].c, o = s.inst[id].o;
  s.P[f.side].worlds[f.w].splice(f.k, 1);
  s.P[f.side].worlds = s.P[f.side].worlds.filter((w) => w.length);
  delete s.inst[id];
  s.P[o].binder.push(c);
  s.P[o].binder.sort((a, b) => a - b);
  say(s, o, `${CARDS[c].n} returns to ${poss(s, o)} binder.`);
}
const flip = (s, id) => { s.inst[id].f = true; say(s, null, `${card(s, id).n} is flipped.`); };
const unflip = (s, id) => { s.inst[id].f = false; say(s, null, `${card(s, id).b} flips back to ${card(s, id).n}.`); };
const one = (s, id) => pipsOf(s, id).length === 1;
const step = (prompt, opts, canStop = false) => ({ prompt, opts, canStop });

const FORCES = {
  [K["Spring"]]: { apply: (s) => { s.extra++; } },
  [K["Lake"]]: {
    step: (s, P, id, pk) => (pk.length ? null : step("Choose an opponent's permanence with one pip to return.", oppTargets(s, P, (x) => one(s, x)))),
    apply: (s, P, id, pk) => { if (pk[0]) toBinder(s, pk[0].id); },
  },
  [K["Tidal Flat"]]: {},
  [K["Cloud Forest"]]: { apply: (s, P, id) => { for (const x of worldOf(s, id)) if (x !== id && s.inst[x].f) unflip(s, x); } },
  [K["Glacier"]]: {
    step: (s, P, id, pk) => (pk.length ? null : step("Choose a flipped permanence of yours to return to your binder.", ownCards(s, P, (x) => x !== id && s.inst[x].f))),
    apply: (s, P, id, pk) => { if (pk[0]) toBinder(s, pk[0].id); },
  },
  [K["Ocean"]]: {
    step: (s, P, id, pk) => {
      if (pk.length) return null;
      const opts = [];
      s.P[1 - P].worlds.forEach((w, wi) => { if (w.some((x) => !guarded(s, x, P) && one(s, x))) opts.push({ t: "world", side: 1 - P, w: wi }); });
      return step("Choose one of your opponent's worlds.", opts);
    },
    apply: (s, P, id, pk) => {
      if (!pk[0]) return;
      const w = s.P[pk[0].side].worlds[pk[0].w];
      for (const x of w.filter((x) => !guarded(s, x, P) && one(s, x))) toBinder(s, x);
    },
  },
  [K["Hills"]]: {
    step: (s, P, id, pk) => {
      if (pk.length === 0) return step("Choose a permanence of yours to swap.", ownCards(s, P, (x) => sideCards(s, P).some((y) => worldOf(s, y) !== worldOf(s, x))));
      if (pk.length === 1) return step("Choose one in a different world to swap it with.", ownCards(s, P, (y) => worldOf(s, y) !== worldOf(s, pk[0].id)));
      return null;
    },
    apply: (s, P, id, pk) => {
      if (pk.length < 2) return;
      const a = findCard(s, pk[0].id), b = findCard(s, pk[1].id);
      s.P[a.side].worlds[a.w][a.k] = pk[1].id; s.P[b.side].worlds[b.w][b.k] = pk[0].id;
      say(s, P, `${card(s, pk[0].id).n} and ${card(s, pk[1].id).n} swap worlds.`);
    },
  },
  [K["Plateau"]]: {
    step: (s, P, id, pk) => {
      const W = s.P[P].worlds;
      const fits = (a, b) => a !== b && W[a].length + W[b].length <= 4;
      if (pk.length === 0) return step("Choose a world of yours to join.", W.map((_, a) => a).filter((a) => W.some((_, b) => fits(a, b))).map((w) => ({ t: "world", side: P, w })));
      if (pk.length === 1) return step("Choose the world to join into it.", W.map((_, b) => b).filter((b) => fits(pk[0].w, b)).map((w) => ({ t: "world", side: P, w })));
      return null;
    },
    apply: (s, P, id, pk) => {
      if (pk.length < 2) return;
      const W = s.P[P].worlds, a = W[pk[0].w], b = W[pk[1].w];
      a.push(...b.splice(0));
      s.P[P].worlds = W.filter((w) => w.length);
      say(s, P, `Two of ${poss(s, P)} worlds join.`);
    },
  },
  [K["Cavern"]]: {},
  [K["Forest"]]: {
    step: (s, P, id, pk) => (pk.length ? null : step("Choose an opponent's permanence with one pip to flip.", oppTargets(s, P, (x) => !s.inst[x].f && one(s, x)))),
    apply: (s, P, id, pk) => { if (pk[0]) flip(s, pk[0].id); },
  },
  [K["Fault Line"]]: {
    step: (s, P, id, pk) => {
      const Q = 1 - P, W = s.P[Q].worlds;
      if (pk.length === 0) return step("Choose one of your opponent's worlds to split.", W.map((w, wi) => wi).filter((wi) => W[wi].length > 1 && !worldGuarded(s, Q, wi, P)).map((w) => ({ t: "world", side: Q, w })));
      const w = W[pk[0].w], chosen = pk.slice(1).map((p) => p.id);
      if (chosen.length >= w.length - 1) return null;
      return step("Choose the permanences that split off into a new world.", w.filter((x) => !chosen.includes(x)).map((x) => ({ t: "card", id: x })), chosen.length > 0);
    },
    apply: (s, P, id, pk) => {
      if (pk.length < 2) return;
      const Q = 1 - P, moved = pk.slice(1).map((p) => p.id);
      const W = s.P[Q].worlds, w = W[pk[0].w];
      for (const x of moved) w.splice(w.indexOf(x), 1);
      W.push(moved);
      say(s, P, `One of ${poss(s, Q)} worlds splits in two.`);
    },
  },
  [K["Highlands"]]: {
    step: (s, P, id, pk) => {
      const here = worldOf(s, id);
      if (pk.length === 0) return step("Choose another permanence in this world to move.", here.filter((x) => x !== id && dests(s, P, x, false).length).map((x) => ({ t: "card", id: x })));
      if (pk.length === 1) return step("Choose which of your worlds it moves to.", dests(s, P, pk[0].id, false));
      return null;
    },
    apply: (s, P, id, pk) => { if (pk.length === 2) { moveTo(s, pk[0].id, pk[1]); say(s, P, `${card(s, pk[0].id).n} moves.`); } },
  },
  [K["Ash Plain"]]: {
    step: (s, P, id, pk) => (pk.length ? null : step("Choose another permanence in this world to flip. Its force happens.", worldOf(s, id).filter((x) => x !== id && !s.inst[x].f).map((x) => ({ t: "card", id: x })))),
    apply: (s, P, id, pk) => {
      if (!pk[0]) return null;
      flip(s, pk[0].id);
      return { P: s.inst[pk[0].id].o, id: pk[0].id, picks: [], nested: true, locked: true }; // its owner's force
    },
  },
  [K["Lava Field"]]: {
    step: (s, P, id, pk) => (pk.length ? null : step("Choose another permanence in this world to return to your binder.", worldOf(s, id).filter((x) => x !== id).map((x) => ({ t: "card", id: x })))),
    apply: (s, P, id, pk) => { if (pk[0]) toBinder(s, pk[0].id); s.extra++; },
  },
  [K["Volcano"]]: {
    step: (s, P, id, pk) => (pk.length ? null : step("Choose an opponent's permanence to flip.", oppTargets(s, P, (x) => !s.inst[x].f))),
    apply: (s, P, id, pk) => { if (pk[0]) flip(s, pk[0].id); },
  },
  [K["Desert"]]: {},
  [K["Hot Springs"]]: { apply: (s) => { s.extra++; } },
  [K["Caldera"]]: {
    apply: (s, P, id) => {
      for (const Q of [0, 1]) for (const x of sideCards(s, Q)) if (x !== id && !s.inst[x].f && !guarded(s, x, P)) s.inst[x].f = true;
      say(s, P, "Every other permanence flips.");
    },
  },
  [K["Meadow"]]: {
    step: (s, P, id, pk) => {
      if (pk.length === 0) return step("Choose a permanence of yours to move.", ownCards(s, P, (x) => dests(s, P, x, true).length));
      if (pk.length === 1) return step("Choose where it goes.", dests(s, P, pk[0].id, true));
      return null;
    },
    apply: (s, P, id, pk) => { if (pk.length === 2) { moveTo(s, pk[0].id, pk[1]); say(s, P, `${card(s, pk[0].id).n} moves.`); } },
  },
  [K["Trade Winds"]]: {
    step: (s, P, id, pk) => (pk.length ? null : step("Choose an opponent's permanence to blow into a new world.", oppTargets(s, P, (x) => worldOf(s, x).length > 1))),
    apply: (s, P, id, pk) => { if (pk[0]) { moveTo(s, pk[0].id, { t: "new", side: findCard(s, pk[0].id).side }); say(s, P, `${card(s, pk[0].id).n} is blown into a new world.`); } },
  },
  [K["Cliffs"]]: { apply: (s, P, id) => { s.extra++; s.notWith = id; } },
  [K["Dunes"]]: {
    step: (s, P, id, pk) => (pk.length ? null : step("Choose where the dunes wander.", dests(s, P, id, true))),
    apply: (s, P, id, pk) => { if (pk[0]) { moveTo(s, id, pk[0]); say(s, P, "Wandering Dunes moves."); } },
  },
  [K["Cloud Sea"]]: {
    step: (s, P, id, pk) => (pk.length ? null : step("Choose a flipped permanence of yours to flip back.", ownCards(s, P, (x) => x !== id && s.inst[x].f))),
    apply: (s, P, id, pk) => { if (pk[0]) unflip(s, pk[0].id); },
  },
  [K["Peak"]]: {
    // up to two moves; the second is chosen against the worlds as they stand after the first
    step: (s, P, id, pk) => {
      let t = s;
      if (pk.length >= 2) { t = clone(s); moveTo(t, pk[0].id, pk[1]); }
      if (pk.length === 0 || pk.length === 2) return step(pk.length ? "Choose a second permanence to move, or stop." : "Choose a permanence of yours to move, or stop.", ownCards(t, P, (x) => dests(t, P, x, true).length), true);
      if (pk.length === 1 || pk.length === 3) return step("Choose where it goes.", dests(t, P, pk[pk.length - 1].id, true));
      return null;
    },
    apply: (s, P, id, pk) => {
      for (let k = 0; k + 1 < pk.length; k += 2) { moveTo(s, pk[k].id, pk[k + 1]); say(s, P, `${card(s, pk[k].id).n} moves.`); }
    },
  },
};

// ---------------------------------------------------------------- the shared 10th
export function lockIn(s, P) {
  if (s.phase !== "lock" || active(s) !== P) return false;
  s.ts++;
  s.locked[P] = true;
  say(s, P, `${vb(s, P, "locks", "lock")} in.`);
  if (s.locked[0] && s.locked[1]) reveal(s);
  return true;
}
export function clearStage(s, P) { if (s.phase === "lock" && active(s) === P) { s.stage[P] = {}; s.ts++; } }
function reveal(s) {
  for (const P of [s.first, 1 - s.first]) {
    const st = s.stage[P];
    if (st.play) { say(s, P, "Reveal:"); place(s, P, st.play.ci, st.play.w, st.play.side ?? P); }
  }
  // both locked-in forces are used at once: both cards flip now, and their effects then happen in turn order
  s.queue = [];
  for (const P of [s.first, 1 - s.first]) {
    const id = s.stage[P].force;
    if (id && s.inst[id] && !s.inst[id].f) {
      s.inst[id].f = true;
      say(s, P, `Reveal: ${vb(s, P, "uses", "use")} ${card(s, id).n}: ${card(s, id).b}.${card(s, id).t ? ` "${card(s, id).t}"` : ""}`);
      s.queue.push({ P, id, picks: [], locked: true, nested: true });
    }
  }
  s.phase = "resolve";
  checkWin(s);
  if (s.phase !== "resolve") return;
  s.pending = s.queue.shift() || null;
  if (!s.pending) return finish(s);
  settle(s);
}
