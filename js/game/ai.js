// The computer opponent: a heuristic player on the third-pass rules engine.
// It scores every legal move, looks at the other player's best reply to the strongest few,
// weighs the gain against the cost of spending the card, and passes the way Gwent players do:
// pass when ahead and the other player can't catch up, and chase a round only when it doesn't
// cost too many cards. It plays to win, not to teach.
//
// Nov 7 (Cam):
// - Hidden binders (opts.hidden, on by default): it doesn't see the other player's binder. It knows how many
//   cards are in it and every card that player has shown, and fills the rest with a guess from the card pool,
//   leaning toward the elements that player has shown and the usual make-up of a binder (14 commons,
//   6 uncommons, 4 rares, 1 meta). A card it has seen go back into the binder counts as known.
// - A plan for the rounds (opts.plan, on by default): at the start of each round it sets a card budget for the
//   round and shares its strong cards (uncommons, rares, meta) out across the rounds still to come. Playing a
//   card held back for a later round, or going over the round's budget, costs extra, so it does it only for a
//   real gain. The last round, and a round it must win, are all in.
import * as R from "./rules.js";

const PV = [0, 0.15, 0.35, 0.6]; // a growing world, by elements already covered toward its next set
const WORTH = { C: 0.04, B: 0.06, A: 0.09, S: 0.12 };
const META_WORTH = 0.05;
const RETURNS = /^Returns at round end/;
const POWER = { C: 1, B: 1.5, A: 2.2, S: 3 }; // how strong a card is, for planning the rounds
const power = (d) => (d.meta ? 1.4 : POWER[d.rarity] + 0.15 * (d.aff ? d.aff.length : 0));
const TEMPLATE = { C: 14, B: 6, A: 4, meta: 1 }; // the test binders' make-up
const rkey = (d) => (d.meta ? "meta" : d.rarity);
const BITS = [0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4];

export function makeAI(opts = {}) {
  const o = Object.assign({
    k: 2.0, noise: 0.02, chaseSteps: 5, rng: Math.random, top: 8, sample: 40, ply: 2,
    hidden: true, plan: true, reserveK: 0.08, overK: 0.08, weights: [1, 1, 0.75],
  }, opts);
  const C = () => R.C;
  const mem = new WeakMap(); // per contest (keyed on the real state): what each player has shown, and round plans
  const memOf = (s) => { let m = mem.get(s); if (!m) { m = { seen: [new Map(), new Map()], now: [null, null], plans: new Map() }; mem.set(s, m); } return m; };

  // ---------------------------------------------------------------- what can be seen
  function observe(s, M) {
    for (const Q of [0, 1]) {
      const now = new Map();
      for (const k in s.inst) { const i = s.inst[k]; if (i.owner === Q) now.set(i.card, (now.get(i.card) || 0) + 1); }
      for (const c of s.p[Q].void) now.set(c, (now.get(c) || 0) + 1);
      const seen = M.seen[Q];
      for (const [c, n] of now) if ((seen.get(c) || 0) < n) seen.set(c, n);
      M.now[Q] = now;
    }
  }
  let POOL = null, POOL_C = null;
  const pool = () => {
    if (POOL_C !== R.C) { POOL_C = R.C; POOL = Object.values(R.C).filter((d) => d.rarity !== "S"); }
    return POOL;
  };
  // a guess at Q's binder: the cards known to be in it, then unseen cards from the pool
  function guessBinder(s, Q, M) {
    const need = s.p[Q].binder.length, seen = M.seen[Q], now = M.now[Q];
    const known = [];
    for (const [c, n] of seen) { const k = n - (now.get(c) || 0); for (let j = 0; j < k; j++) known.push(c); }
    if (known.length >= need) return known.slice(0, need);
    const left = Object.assign({}, TEMPLATE); let shown = 0;
    for (const [c] of seen) { const d = C()[c]; left[rkey(d)] = (left[rkey(d)] || 0) - 1; shown |= d.el || 0; }
    const keys = Object.keys(TEMPLATE);
    let q = keys.map((r) => Math.max(0, left[r] || 0));
    if (!q.some((x) => x > 0)) q = keys.map((r) => TEMPLATE[r]);
    const slots = need - known.length, tot = q.reduce((a, b) => a + b, 0);
    const want = q.map((x) => Math.floor((slots * x) / tot));
    const rem = q.map((x, k) => [(slots * x) / tot - want[k], k]).sort((a, b) => b[0] - a[0]);
    for (let j = 0; want.reduce((a, b) => a + b, 0) < slots; j++) want[rem[j % rem.length][1]]++;
    const out = known.slice();
    const taken = new Set(seen.keys());
    const draw = (cands) => {
      let tw = 0; const ws = cands.map((d) => { const w = 1 + (shown && !d.meta ? 2 * BITS[d.el & shown] : 0); tw += w; return w; });
      let x = o.rng() * tw;
      for (let k = 0; k < cands.length; k++) { x -= ws[k]; if (x <= 0) return cands[k]; }
      return cands[cands.length - 1];
    };
    keys.forEach((r, k) => {
      for (let j = 0; j < want[k]; j++) {
        let cands = pool().filter((d) => rkey(d) === r && !taken.has(d.id));
        if (!cands.length) cands = pool().filter((d) => !taken.has(d.id));
        if (!cands.length) return;
        const d = draw(cands); taken.add(d.id); out.push(d.id);
      }
    });
    return out;
  }
  function withGuess(s, Q, M) {
    const sv = R.clone(s);
    sv.p[Q].binder = guessBinder(s, Q, M);
    return sv;
  }

  // ---------------------------------------------------------------- a plan for the rounds
  function planFor(s, P, M) {
    const key = `${P}|${s.r}|${s.p[0].wins}|${s.p[1].wins}`;
    const hit = M.plans.get(key); if (hit) return hit;
    const pl = s.p[P], mine = pl.wins, theirs = s.p[1 - P].wins;
    let wts;
    if (s.r === 3 || (mine >= 1 && theirs >= 1)) wts = [1]; // the last round
    else if (theirs >= 1) wts = [1, 1]; // behind: this round and the next must both be won
    else if (mine >= 1) wts = [0.85, 1.15]; // ahead: one more win needed; keep a little more for the last round
    else wts = o.weights.slice(); // round 1, level: a third round isn't certain
    const ids = pl.binder.slice();
    const avail = ids.length + 0.8 * (wts.length - 1); // about one card a round comes back
    const sum = wts.reduce((a, b) => a + b, 0);
    const budget = wts.length === 1 ? s.cap : Math.max(3, Math.min(s.cap, Math.round((avail * wts[0]) / sum)));
    const strong = ids.filter((id) => C()[id].meta || C()[id].rarity !== "C").sort((a, b) => power(C()[b]) - power(C()[a]));
    const got = wts.map(() => 0), held = new Map();
    for (const id of strong) {
      let best = 0;
      for (let k = 1; k < wts.length; k++) if (got[k] / wts[k] < got[best] / wts[best]) best = k;
      got[best] += power(C()[id]);
      if (best > 0) held.set(id, (held.get(id) || 0) + 1);
    }
    const plan = { budget, held, wts };
    M.plans.set(key, plan);
    return plan;
  }

  // ---------------------------------------------------------------- judging a table
  function potential(s, P, sc) {
    const pl = s.p[P];
    if (pl.passed || pl.played >= s.cap) return 0;
    let avail = 0;
    for (const id of pl.binder) { const d = C()[id]; if (d.aff) for (const t of d.aff) avail |= t; }
    let pot = 0;
    for (const wv of sc[P].worlds) {
      const w = s.worlds[wv.id];
      if (!w || !R.canGrow(s, w)) continue;
      pot += PV[wv.cov] * (avail === 15 ? 1 : 0.6);
      if (wv.k === R.DECISIVE_POINTS - 1) pot += 0.12 * wv.cov; // closing in on the 3-point world
    }
    const owns = (n) => R.perms(s).some((i) => i.owner === P && C()[i.card].name === n);
    if (owns("Archipelago")) pot += Math.max(0, sc[P].water - 4) * 0.18;
    if (owns("Mountain Range")) pot += (sc[P].earth % 4) * 0.12;
    return Math.min(pot, (s.cap - pl.played) * 0.35);
  }
  function x(s, P, sc) {
    const Q = 1 - P, a = sc[P], b = sc[Q];
    let v = a.pts - b.pts;
    if (a.pts === b.pts) v += 0.4 * Math.sign(a.tie - b.tie);
    v += 0.02 * Math.max(-5, Math.min(5, a.tie - b.tie));
    return v + potential(s, P, sc) - potential(s, Q, sc);
  }
  // chance P wins this round from here (1.5 / -0.5 for a contest the move decides)
  function wp(s, P, sc) {
    for (const Q of [0, 1]) if (sc[Q].worlds.some((w) => w.k >= R.DECISIVE_POINTS)) return Q === P ? 1.5 : -0.5;
    return 1 / (1 + Math.exp(-o.k * x(s, P, sc)));
  }
  // X's turn ends on this table with Archipelago's 8 water: X wins the round (checked at the end of the turn)
  const archWin = (s, X, sc) => !s.extras.length && R.archipelagoWins(s, X, sc);
  const mustWin = (s, P) => s.r === 3 || s.p[1 - P].wins >= 1;
  const roundWeight = (s) => (s.p[0].wins + s.p[1].wins >= 1 && s.r < 3 ? 1.5 : 1);
  function costFactor(s, P) {
    if (s.r === 3) return 0;
    const future = (3 - s.r) * s.cap, left = s.p[P].binder.length - 1;
    return (s.r === 1 ? 1 : 0.8) * (left >= future ? 0.15 : 1);
  }
  function cost(s, P, m, plan) {
    const d = C()[m.id];
    let w = d.meta ? META_WORTH : WORTH[d.rarity];
    if (m.face === "perm" && RETURNS.test(d.ptext || "")) w *= 0.2;
    w *= costFactor(s, P);
    if (plan && plan.wts.length > 1) {
      if (plan.held.has(m.id)) w += o.reserveK * power(d); // held back for a later round
      const over = s.p[P].played + 1 - plan.budget;
      if (over > 0) w += o.overK * over; // past this round's budget
    }
    return w;
  }
  function moves(s, P, fireOnly) {
    const ms = R.movesFor(s, P, fireOnly);
    if (ms.length <= o.sample * 4) return ms;
    // thin out cards with very many options (Gale Force, Echo) so a turn stays quick
    const by = new Map();
    for (const m of ms) { const k = m.id + m.face; if (!by.has(k)) by.set(k, []); by.get(k).push(m); }
    const out = [];
    for (const list of by.values()) {
      if (list.length <= o.sample) { out.push(...list); continue; }
      for (let k = 0; k < o.sample; k++) out.push(list[Math.floor(o.rng() * list.length)]);
    }
    return out;
  }
  // try each move on a copy of s; Horizon looks at the real binder, so it's tried on the real table (real)
  function tryAll(s, P, ms, real) {
    return ms.map((m) => {
      const base = real && C()[m.id].meta && C()[m.id].name === "Horizon" ? real : s;
      const s2 = R.clone(base); R.applyMove(s2, P, m); return { m, s2, sc: R.score(s2) };
    });
  }
  // X plays alone (the other player has passed): can X take the round, and in how many cards?
  function chase(s, X, steps, plan) {
    let s1 = R.clone(s); s1.p[1 - X].passed = true; s1.extras = [];
    let first = null, draw = null;
    const n = Math.min(steps, s.cap - s.p[X].played);
    for (let k = 0; k < n; k++) {
      const res = tryAll(s1, X, moves(s1, X, false));
      if (!res.length) break;
      let win = null, best = null, bv = -Infinity;
      for (const r of res) {
        if (r.sc[X].worlds.some((w) => w.k >= R.DECISIVE_POINTS) || R.outcome(r.sc, X) === 1 || archWin(r.s2, X, r.sc)) { const c = cost(s1, X, r.m, plan); if (!win || c < win.c) win = { r, c }; }
        const v = wp(r.s2, X, r.sc) - cost(s1, X, r.m, plan);
        if (v > bv) { bv = v; best = r; }
      }
      if (win) return { win: true, cards: k + 1, first: first || win.r.m };
      if (!draw) { const dr = res.find((r) => R.outcome(r.sc, X) === 0); if (dr) draw = { cards: k + 1, first: first || dr.m }; }
      if (!first) first = best.m;
      s1 = best.s2;
    }
    return { win: false, draw };
  }

  // the move P should make now, or null to pass (or, during extra plays, to stop)
  function choose(s, P) {
    const pl = s.p[P], Q = 1 - P, opp = s.p[Q];
    const ms = R.legalMoves(s, P);
    if (!ms.length) return null;
    const M = memOf(s);
    if (o.hidden) observe(s, M);
    const plan = o.plan ? planFor(s, P, M) : null;
    const sv = o.hidden ? withGuess(s, Q, M) : s; // the table as P can know it
    const pool = ms.length <= o.sample * 4 ? ms : moves(s, P, s.extras.length > 0 && !s.extras.includes("any"));
    const sc0 = R.score(sv);
    const now = R.outcome(sc0, P);
    const tried = tryAll(sv, P, pool, s);
    // a move that wins the contest outright, then one that ends the turn with Archipelago's round win
    for (const r of tried) if (r.sc[P].worlds.some((w) => w.k >= R.DECISIVE_POINTS)) return r.m;
    for (const r of tried) if (archWin(r.s2, P, r.sc)) return r.m;
    if (opp.passed) {
      if (now === 1) return null;
      const ch = chase(sv, P, o.chaseSteps + 3, plan);
      const allowance = mustWin(s, P) ? 99 : Math.max(1, opp.played - pl.played + 2, plan ? plan.budget - pl.played : 0);
      if (ch.win && ch.cards <= allowance) return ch.first;
      if (now === -1 && ch.draw && mustWin(s, P)) return ch.draw.first;
      return null;
    }
    if (now === 1 && !s.extras.length) {
      const och = chase(sv, Q, o.chaseSteps);
      if (!och.win) return null;
      if (s.r < 3 && och.cards >= 3) return null;
    }
    const Wt = roundWeight(s);
    const reply = (s2, sc2) => {
      const qs = moves(s2, Q, false); if (!qs.length) return null;
      let best = null, bv = Wt * wp(s2, Q, sc2);
      for (const r of tryAll(s2, Q, qs)) {
        const v = Wt * (archWin(r.s2, Q, r.sc) ? 1.2 : wp(r.s2, Q, r.sc)) - cost(s2, Q, r.m);
        if (v > bv) { bv = v; best = r; }
      }
      return best;
    };
    const after = (s2, sc2) => {
      const q = s2.p[Q];
      if (sc2[P].worlds.some((w) => w.k >= R.DECISIVE_POINTS)) return 1.5;
      if (archWin(s2, P, sc2)) return 1.2;
      if (o.ply < 2 || q.passed || q.skip || q.played >= s2.cap) return wp(s2, P, sc2);
      const r = reply(s2, sc2);
      if (r && archWin(r.s2, Q, r.sc)) return -0.2;
      return r ? wp(r.s2, P, r.sc) : wp(s2, P, sc2);
    };
    const base = Wt * after(sv, sc0);
    const res = tried.map((r) => Object.assign(r, { v1: Wt * wp(r.s2, P, r.sc) - cost(sv, P, r.m, plan) }));
    res.sort((a, b) => b.v1 - a.v1);
    const cand = o.ply < 2 ? res : res.slice(0, o.top);
    let best = null, bv = -Infinity;
    for (const r of cand) {
      const v = (o.ply < 2 ? r.v1 : Wt * after(r.s2, r.sc) - cost(sv, P, r.m, plan)) + (o.rng() - 0.5) * 2 * o.noise;
      if (v > bv) { bv = v; best = r.m; }
    }
    return bv > base ? best : null;
  }
  return { choose };
}
