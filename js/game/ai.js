// The computer opponent: a heuristic player on the third-pass rules engine.
// It scores every legal move, looks at the other player's best reply to the strongest few,
// weighs the gain against the cost of spending the card, and passes the way Gwent players do:
// pass when ahead and the other player can't catch up, and chase a round only when it doesn't
// cost too many cards. It sees both binders. It plays to win, not to teach.
import * as R from "./rules.js";

const PV = [0, 0.15, 0.35, 0.6]; // a growing world, by elements already covered toward its next set
const WORTH = { C: 0.04, B: 0.06, A: 0.09, S: 0.12 };
const META_WORTH = 0.05;
const RETURNS = /^Returns at round end/;

export function makeAI(opts = {}) {
  const o = Object.assign({ k: 2.0, noise: 0.02, chaseSteps: 5, rng: Math.random, top: 8, sample: 40, ply: 2 }, opts);
  const C = () => R.C;

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
  // chance P wins this round from here (1 / 0 for a contest the move decides)
  function wp(s, P, sc) {
    for (const Q of [0, 1]) if (sc[Q].worlds.some((w) => w.k >= R.DECISIVE_POINTS)) return Q === P ? 1.5 : -0.5;
    return 1 / (1 + Math.exp(-o.k * x(s, P, sc)));
  }
  const mustWin = (s, P) => s.r === 3 || s.p[1 - P].wins >= 1;
  const roundWeight = (s) => (s.p[0].wins + s.p[1].wins >= 1 && s.r < 3 ? 1.5 : 1);
  function costFactor(s, P) {
    if (s.r === 3) return 0;
    const future = (3 - s.r) * s.cap, left = s.p[P].binder.length - 1;
    return (s.r === 1 ? 1 : 0.8) * (left >= future ? 0.15 : 1);
  }
  function cost(s, P, m) {
    const d = C()[m.id];
    let w = d.meta ? META_WORTH : WORTH[d.rarity];
    if (m.face === "perm" && RETURNS.test(d.ptext || "")) w *= 0.2;
    return w * costFactor(s, P);
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
  function tryAll(s, P, ms) {
    return ms.map((m) => { const s2 = R.clone(s); R.applyMove(s2, P, m); return { m, s2, sc: R.score(s2) }; });
  }
  // X plays alone (the other player has passed): can X take the round, and in how many cards?
  function chase(s, X, steps) {
    let s1 = R.clone(s); s1.p[1 - X].passed = true; s1.extras = [];
    let first = null, draw = null;
    const n = Math.min(steps, s.cap - s.p[X].played);
    for (let k = 0; k < n; k++) {
      const res = tryAll(s1, X, moves(s1, X, false));
      if (!res.length) break;
      let win = null, best = null, bv = -Infinity;
      for (const r of res) {
        if (r.sc[X].worlds.some((w) => w.k >= R.DECISIVE_POINTS) || R.outcome(r.sc, X) === 1) { const c = cost(s1, X, r.m); if (!win || c < win.c) win = { r, c }; }
        const v = wp(r.s2, X, r.sc) - cost(s1, X, r.m);
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
    const pool = ms.length <= o.sample * 4 ? ms : moves(s, P, s.extras.length > 0 && !s.extras.includes("any"));
    const sc0 = R.score(s);
    const now = R.outcome(sc0, P);
    // a move that wins the contest outright
    for (const r of tryAll(s, P, pool)) if (r.sc[P].worlds.some((w) => w.k >= R.DECISIVE_POINTS)) return r.m;
    if (opp.passed) {
      if (now === 1) return null;
      const ch = chase(s, P, o.chaseSteps + 3);
      const allowance = mustWin(s, P) ? 99 : Math.max(1, opp.played - pl.played + 2);
      if (ch.win && ch.cards <= allowance) return ch.first;
      if (now === -1 && ch.draw && mustWin(s, P)) return ch.draw.first;
      return null;
    }
    if (now === 1 && !s.extras.length) {
      const och = chase(s, Q, o.chaseSteps);
      if (!och.win) return null;
      if (s.r < 3 && och.cards >= 3) return null;
    }
    const Wt = roundWeight(s);
    const reply = (s2, sc2) => {
      const qs = moves(s2, Q, false); if (!qs.length) return null;
      let best = null, bv = Wt * wp(s2, Q, sc2);
      for (const r of tryAll(s2, Q, qs)) { const v = Wt * wp(r.s2, Q, r.sc) - cost(s2, Q, r.m); if (v > bv) { bv = v; best = r; } }
      return best;
    };
    const after = (s2, sc2) => {
      const q = s2.p[Q];
      if (sc2[P].worlds.some((w) => w.k >= R.DECISIVE_POINTS)) return 1.5;
      if (o.ply < 2 || q.passed || q.skip || q.played >= s2.cap) return wp(s2, P, sc2);
      const r = reply(s2, sc2);
      return r ? wp(r.s2, P, r.sc) : wp(s2, P, sc2);
    };
    const base = Wt * after(s, sc0);
    const res = tryAll(s, P, pool).map((r) => Object.assign(r, { v1: Wt * wp(r.s2, P, r.sc) - cost(s, P, r.m) }));
    res.sort((a, b) => b.v1 - a.v1);
    const cand = o.ply < 2 ? res : res.slice(0, o.top);
    let best = null, bv = -Infinity;
    for (const r of cand) {
      const v = (o.ply < 2 ? r.v1 : Wt * after(r.s2, r.sc) - cost(s, P, r.m)) + (o.rng() - 0.5) * 2 * o.noise;
      if (v > bv) { bv = v; best = r.m; }
    }
    return bv > base ? best : null;
  }
  return { choose };
}
