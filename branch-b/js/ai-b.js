// The computer for Branch B (Nov 23): it looks one turn ahead. It tries its plays and forces in both orders, with
// every way of resolving each force, and keeps the turn that leaves the best position: its world points against the
// other player's, how close each world is to another point or a perfect world, and the forces it still has to use.
// It doesn't predict the other player's reply.
import * as R from "./rules-b.js";

const W_OPP = 0.85;
function worldPotential(s, ids) {
  const c = { water: 0, earth: 0, fire: 0, air: 0 };
  let any = 0;
  for (const id of ids) for (const p of R.pipsOf(s, id)) p === "any" ? any++ : c[p]++;
  const pts = R.pointsOfPips(ids.flatMap((id) => R.pipsOf(s, id)));
  const room = 4 - ids.length;
  // what's left after the points: how close to another set or another four
  let k = 0;
  for (let t = Math.min(c.water, c.earth, c.fire, c.air); t >= 0; t--) {
    const v = t + ["water", "earth", "fire", "air"].reduce((a, e) => a + Math.floor((c[e] - t) / 4), 0);
    if (v === pts - 0 || v === pts) { k = t; break; }
  }
  const left = ["water", "earth", "fire", "air"].map((e) => { const x = c[e] - k; return x - 4 * Math.floor(x / 4); });
  const distinct = left.filter((x) => x > 0).length + Math.min(any, 4 - left.filter((x) => x > 0).length);
  const most = Math.max(...left) + any;
  const near = Math.max(distinct / 4, (most / 4) * 0.9);
  let v = near * (room > 0 ? 2.2 : 0.3);
  if (pts === 2 && room > 0) v += 3 + near * 3; // a perfect world is in reach
  return v;
}
// can X finish a perfect world with one landscape on their next turn?
function threat(s, X) {
  const plays = [...new Set(s.P[X].binder)];
  let n = 0;
  for (const w of s.P[X].worlds) {
    if (w.length >= 4) continue;
    const have = w.flatMap((id) => R.pipsOf(s, id));
    if (plays.some((ci) => R.pointsOfPips([...have, ...R.CARDS[ci].p]) >= 3)) n++;
  }
  return n;
}
export function evaluate(s, P) {
  if (s.winner) return s.winner.P === P ? 1e4 : s.winner.P === null ? 0 : -1e4;
  const Q = 1 - P;
  // the other player moves next: a perfect world they can finish with one card is nearly a loss
  if (s.phase === "turn" && !s.pending && threat(s, Q)) return -2000 - 100 * threat(s, Q) + 10 * (R.total(s, P) - R.total(s, Q));
  const late = Math.max(0.15, Math.min(1, (19 - s.half) / 8));
  let v = 10 * (R.total(s, P) - W_OPP * R.total(s, Q));
  for (const w of s.P[P].worlds) v += late * worldPotential(s, w);
  for (const w of s.P[Q].worlds) v -= late * W_OPP * worldPotential(s, w);
  const ready = (X) => R.ownedCards(s, X).filter((id) => !s.inst[id].f).length;
  v += 0.35 * late * (ready(P) - 0.6 * ready(Q));
  return v;
}

// every way to finish the force or choice now pending, as actions and the state each leaves
function finishes(c, acts, out, limit) {
  if (out.length >= limit) return;
  const st = c.pending ? R.choices(c) : null;
  if (!st) { out.push({ acts, s: c }); return; }
  const opts = st.opts.slice();
  for (let i = opts.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [opts[i], opts[j]] = [opts[j], opts[i]]; }
  if (st.canStop) opts.unshift({ t: "stop" });
  for (const o of opts) {
    const d = R.clone(c);
    if (!R.pick(d, o)) continue;
    finishes(d, [...acts, { k: "pick", opt: o }], out, limit);
    if (out.length >= limit) return;
  }
}
function forceLines(s, P, limit = 90) {
  const out = [];
  for (const id of R.ownedCards(s, P)) {
    if (!R.canUseForce(s, P, id)) continue;
    const c = R.clone(s);
    R.beginForce(c, P, id);
    finishes(c, [{ k: "force", id }], out, out.length + limit);
  }
  return out;
}
function bestPlays(s, P) {
  return R.legalPlays(s, P).map((m) => {
    const c = R.clone(s);
    R.play(c, P, m.ci, m.w, m.side);
    return { acts: [{ k: "play", ci: m.ci, w: m.w, side: m.side }], s: c, v: evaluate(c, P) + Math.random() * 0.05 };
  }).sort((a, b) => b.v - a.v);
}
function fill(line, P) { // play any landscapes still allowed, best first
  let cur = line;
  for (let g = 0; g < 4; g++) {
    const p = bestPlays(cur.s, P)[0];
    if (!p) break;
    cur = { acts: [...cur.acts, ...p.acts], s: p.s };
  }
  return cur;
}
const scored = (lines, P) => lines.map((l) => ({ ...l, v: evaluate(l.s, P) + Math.random() * 0.05 })).sort((a, b) => b.v - a.v);

// the whole turn for P, from s, as a list of actions; the caller plays them one by one
export function planTurn(s, P) {
  const cand = [];
  cand.push(fill({ acts: [], s: R.clone(s) }, P));
  const forcesFirst = scored(forceLines(s, P), P);
  for (const f of forcesFirst.slice(0, 8)) cand.push(fill(f, P));
  for (const p of bestPlays(s, P).slice(0, 5)) {
    cand.push(p);
    for (const f of scored(forceLines(p.s, P), P).slice(0, 10)) {
      const line = { acts: [...p.acts, ...f.acts], s: f.s };
      cand.push(line.s.extra > 0 ? fill(line, P) : line);
    }
  }
  const best = scored(cand, P)[0];
  return [...best.acts, { k: "end" }];
}

// the shared 10th: choose a landscape and a force to lock in, judged as if both happen
export function planLock(s, P) {
  const c = R.clone(s);
  c.phase = "turn"; c.first = P; c.played = 0; c.forced = 0; c.extra = 0;
  const plan = planTurn(c, P);
  const play = plan.find((a) => a.k === "play");
  const force = plan.find((a) => a.k === "force");
  return [...(play ? [play] : []), ...(force ? [force] : []), { k: "lock" }];
}

// a choice pending for P (a locked-in force at the reveal, or a force set off by Kindling)
export function planPicks(s, P) {
  const out = [];
  finishes(R.clone(s), [], out, 150);
  const best = scored(out, P)[0];
  return best ? best.acts : [];
}

export function planFor(s, P) {
  if (s.phase === "over") return [];
  if (s.pending) return s.pending.P === P ? planPicks(s, P) : [];
  if (R.active(s) !== P) return [];
  if (s.phase === "lock") return planLock(s, P);
  if (s.phase === "turn") return planTurn(s, P);
  return [];
}

// carry out one action; false if it no longer fits the state
export function act(s, P, a) {
  if (a.k === "play") return R.play(s, P, a.ci, a.w, a.side ?? P);
  if (a.k === "force") return R.beginForce(s, P, a.id);
  if (a.k === "pick") return R.pick(s, a.opt);
  if (a.k === "end") return R.endTurn(s);
  if (a.k === "lock") return R.lockIn(s, P);
  if (a.k === "cancel") return R.cancelForce(s);
  return false;
}
