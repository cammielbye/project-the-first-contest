// A heuristic AI player: scores every legal move, weighs it against the cost of spending the card,
// and passes the way Gwent players do (pass when ahead and the opponent can't catch up; chase only
// when it doesn't cost too many cards).
'use strict';
const E = require('./engine');
const M = require('./moves');
const C = () => E.C;

const PV = [0, 0.15, 0.35, 0.6];          // value of a growing world by elements covered toward its next set
const WORTH = { C: 0.04, B: 0.06, A: 0.09, S: 0.12 };
const META_WORTH = 0.05;
const PROTECT = new Set(['Thicket', 'Bedrock', 'Hidden Valley', 'Cave', 'Tide Pool', 'Shelter', 'Freeze', 'Uplift', 'Overgrowth', 'Tangle']);
const nameOf = (m) => (m.face === 'force' ? E.C[m.id].fname : E.C[m.id].name);

function makeAI(opts = {}) {
  const o = Object.assign({ k: 2.0, noise: 0.03, chaseSteps: 5, rng: Math.random, forces: true, costScale: 1, ply: 2, top: 8 }, opts);

  function potential(s, P, sc) {
    const pl = s.p[P];
    if (pl.passed || pl.played >= s.cap) return 0;
    let avail = 0;
    for (const id of pl.binder) { const d = C()[id]; if (d.aff) for (const t of d.aff) avail |= t; }
    let pot = 0;
    for (const wv of sc[P].worlds) {
      const w = s.worlds[wv.id];
      if (!w || !E.canGrow(s, w)) continue;
      pot += PV[wv.cov] * (avail === 15 ? 1 : 0.6);
    }
    if (E.hasPerm(s, P, 'Archipelago')) pot += Math.max(0, sc[P].water - 5) * 0.15;
    if (E.hasPerm(s, P, 'Mountain Range')) pot += (sc[P].earth % 4) * 0.12;
    return Math.min(pot, (s.cap - pl.played) * 0.35);
  }
  function x(s, P, sc) {
    const Q = 1 - P; const a = sc[P], b = sc[Q];
    let v = a.pts - b.pts;
    if (a.pts === b.pts) v += 0.4 * Math.sign(a.tie - b.tie);
    v += 0.02 * Math.max(-5, Math.min(5, a.tie - b.tie));
    if (a.alt) v += 4; if (b.alt) v -= 4;
    v += potential(s, P, sc) - potential(s, Q, sc);
    return v;
  }
  const wp = (s, P, sc) => 1 / (1 + Math.exp(-o.k * x(s, P, sc)));
  function mustWin(s, P) { return s.r === 3 || s.p[1 - P].wins >= 1; }
  function roundWeight(s, P) { return (s.p[0].wins + s.p[1].wins >= 1 && s.r < 3) ? 1.5 : 1; }
  function costFactor(s, P) {
    if (s.r === 3) return 0;
    // cards beyond what the later rounds can use are nearly free; the rest cost full price
    const future = (3 - s.r) * s.cap; const left = s.p[P].binder.length - 1;
    const scarcity = left >= future ? 0.15 : 1;
    return (s.r === 1 ? 1 : 0.8) * scarcity * o.costScale;
  }
  function cost(s, P, m) {
    const d = C()[m.id];
    let w = d.meta ? META_WORTH : WORTH[d.rarity];
    if (m.face === 'perm' && (d.name === 'Spring' || d.name === 'Grove')) w *= 0.2; // comes back to the binder
    return w * costFactor(s, P);
  }
  function moves(s, P) {
    let ms = M.genMoves(s, P);
    if (!o.forces) ms = ms.filter((m) => m.face !== 'force');
    return ms;
  }
  function tryAll(s, P, ms) {
    return ms.map((m) => { const s2 = E.clone(s); M.applyMove(s2, P, m); return { m, s2, sc: E.score(s2) }; });
  }
  // X plays alone (the other player has passed): can X take the round, and with how many cards?
  function chase(s, X, steps) {
    let s1 = E.clone(s); s1.p[1 - X].passed = true; let first = null; let draw = null;
    const n = Math.min(steps, s.cap - s.p[X].played);
    for (let k = 0; k < n; k++) {
      const res = tryAll(s1, X, moves(s1, X));
      if (!res.length) break;
      let win = null, best = null, bv = -Infinity;
      for (const r of res) {
        if (E.outcome(r.sc, X) === 1) { const c = cost(s1, X, r.m); if (!win || c < win.c) win = { r, c }; }
        const v = wp(r.s2, X, r.sc) - cost(s1, X, r.m);
        if (v > bv) { bv = v; best = r; }
      }
      if (win) return { win: true, cards: k + 1, first: first || win.r.m };
      if (!draw) { const dr = res.find((r) => E.outcome(r.sc, X) === 0); if (dr) draw = { cards: k + 1, first: first || dr.m }; }
      if (!first) first = best.m;
      s1 = best.s2;
    }
    return { win: false, draw };
  }

  function choose(s, P) {
    const pl = s.p[P], Q = 1 - P, opp = s.p[Q];
    if (pl.played >= s.cap) return null;
    const ms = moves(s, P);
    if (!ms.length) return null;
    const sc0 = E.score(s);
    const now = E.outcome(sc0, P);
    if (opp.passed) {
      if (now === 1) return null;
      const ch = chase(s, P, o.chaseSteps + 3);
      const allowance = mustWin(s, P) ? 99 : Math.max(1, opp.played - pl.played + 2);
      if (ch.win && ch.cards <= allowance) return ch.first;
      // no win in reach: settle for a drawn round when losing it would end the contest
      if (now === -1 && ch.draw && mustWin(s, P)) return ch.draw.first;
      return null;
    }
    if (now === 1) {
      const och = chase(s, Q, o.chaseSteps);
      if (!och.win) return null;
      if (s.r < 3 && och.cards >= 3) return null;
    }
    const W = roundWeight(s, P), Wq = roundWeight(s, Q);
    // the opponent's best reply to a position, or null if no card is worth spending
    const reply = (s2, sc2) => {
      const qs = moves(s2, Q); if (!qs.length) return null;
      let best = null, bv = Wq * wp(s2, Q, sc2);
      for (const r of tryAll(s2, Q, qs)) {
        const v = Wq * wp(r.s2, Q, r.sc) - cost(s2, Q, r.m);
        if (v > bv) { bv = v; best = r; }
      }
      return best;
    };
    const after = (s2, sc2) => {
      const q = s2.p[Q];
      if (o.ply < 2 || q.passed || q.skip || q.played >= s2.cap) return wp(s2, P, sc2);
      const r = reply(s2, sc2);
      return r ? wp(r.s2, P, r.sc) : wp(s2, P, sc2);
    };
    const base = W * after(s, sc0);
    const res = tryAll(s, P, ms).map((r) => Object.assign(r, { v1: W * wp(r.s2, P, r.sc) - cost(s, P, r.m) }));
    res.sort((a, b) => b.v1 - a.v1);
    const cand = o.ply < 2 ? res : res.slice(0, o.top).concat(res.slice(o.top).filter((r) => PROTECT.has(nameOf(r.m)) || o.rng() < 0.03));
    let best = null, bv = -Infinity;
    for (const r of cand) {
      const v = (o.ply < 2 ? r.v1 : W * after(r.s2, r.sc) - cost(s, P, r.m)) + (o.rng() - 0.5) * 2 * o.noise;
      if (v > bv) { bv = v; best = r.m; }
    }
    return bv > base ? best : null;
  }
  return { choose };
}

module.exports = { makeAI };
