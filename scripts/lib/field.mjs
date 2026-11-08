// Shared by sim3-rate.mjs and sim3-sweep.mjs: random binders, one contest, and running many on worker threads.
// Contest k of a run is set up from its own seed (binders, styles, first player), so two runs with the same seed
// play the same match-ups: a sweep compares rule settings on paired contests.
import { readFileSync } from "node:fs";
import { Worker } from "node:worker_threads";
import { cpus } from "node:os";
import * as R from "../../js/game/rules.js";
import { makeAI, STYLES } from "../../js/game/ai.js";

const root = new URL("../..", import.meta.url);
R.loadCards(JSON.parse(readFileSync(new URL("data/cards.json", root), "utf8")));
export const C = R.C;
export { STYLES };
export const ELS = ["water", "earth", "fire", "air"]; // the order on the cards
const BIT = { fire: 1, water: 2, air: 4, earth: 8 };

export function mulberry(seed) {
  return () => { seed |= 0; seed = (seed + 0x6d2b79f5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}

// one of each card: 14 commons, 7 uncommons, 4 rares (meta cards at their rarity), no pinnacles or Origin,
// leaning toward no element (20%), one (30%) or two (50%): a card's weight is 1 + 3 x its share of rings in the lean
const POOL = Object.values(C).filter((d) => d.rarity !== "S");
const byRarity = { C: POOL.filter((d) => d.rarity === "C"), B: POOL.filter((d) => d.rarity === "B"), A: POOL.filter((d) => d.rarity === "A") };
const TEMPLATE = { C: 14, B: 7, A: 4 };
function leanShare(d, mask) {
  if (d.meta || !d.aff || !d.aff.length) return 0;
  let k = 0;
  for (const t of d.aff) k += t === 15 ? 0.5 : t & mask ? 1 : 0;
  return k / d.aff.length;
}
export function randomBinder(rng) {
  const u = rng();
  const els = ELS.slice().sort(() => rng() - 0.5);
  const lean = u < 0.2 ? [] : u < 0.5 ? [els[0]] : [els[0], els[1]];
  const mask = lean.reduce((m, e) => m | BIT[e], 0);
  const ids = [];
  for (const r of ["C", "B", "A"]) {
    const cands = byRarity[r].slice();
    const w = cands.map((d) => (lean.length ? 1 + 3 * leanShare(d, mask) : 1));
    for (let k = 0; k < TEMPLATE[r]; k++) {
      let x = rng() * w.reduce((a, b) => a + b, 0), j = 0;
      for (; j < cands.length - 1; j++) { x -= w[j]; if (x <= 0) break; }
      ids.push(cands[j].id); cands.splice(j, 1); w.splice(j, 1);
    }
  }
  return { ids, lean: lean.slice().sort((a, b) => ELS.indexOf(a) - ELS.indexOf(b)).join("+") || "none" };
}

// cfg: { bo1, nocap, open, quick, styles: [...], ai: {...}, knobs: {...} }
export function playOne(seed, cfg) {
  const setup = mulberry(seed), rng = mulberry(seed ^ 0x5bd1e995);
  const A = randomBinder(setup), B = randomBinder(setup);
  // cfg.forceA: cards side A always holds, each replacing a random card of its rarity (for sweeps on one card)
  for (const id of cfg.forceA || []) if (!A.ids.includes(id)) {
    const same = A.ids.filter((x) => C[x].rarity === C[id].rarity);
    A.ids[A.ids.indexOf(same[Math.floor(setup() * same.length)])] = id;
  }
  const styles = [0, 1].map(() => cfg.styles[Math.floor(setup() * cfg.styles.length)]);
  const opener = setup() < 0.5 ? 0 : 1;
  const s = R.newContest(A.ids, B.ids, opener, ["A", "B"], { openWorlds: cfg.open, bestOf: cfg.bo1 ? 1 : 3, noCap: cfg.nocap, knobs: cfg.knobs || null });
  const ai = styles.map((st) => makeAI(Object.assign({ rng, style: st }, cfg.quick ? { ply: 1 } : {}, cfg.ai || {})));
  const played = [[], []];
  R.advance(s);
  for (let guard = 0; guard < 800 && s.phase !== "contestOver"; guard++) {
    if (s.phase === "roundOver") { R.nextRound(s); continue; }
    const P = s.turn, m = ai[P].choose(s, P);
    if (m) { played[P].push(m.id); R.play(s, P, m); } else R.pass(s, P);
  }
  if (s.phase !== "contestOver") return null;
  return { a: A.ids, b: B.ids, lean: [A.lean, B.lean], styles, opener, winner: s.winner, why: s.why === "rounds" ? s.rounds[s.rounds.length - 1].why : s.why, played };
}

// contests from..from+n-1 of the run with this seed, spread over worker threads
export async function runField(from, n, seed, cfg, workers = cpus().length) {
  const W = Math.max(1, Math.min(workers, n));
  const parts = await Promise.all(Array.from({ length: W }, (_, w) => new Promise((res, rej) => {
    const ks = []; for (let k = from + w; k < from + n; k += W) ks.push(k);
    const wk = new Worker(new URL("./field-worker.mjs", import.meta.url), { workerData: { ks, seed, cfg } });
    wk.on("message", (m) => res(m));
    wk.on("error", rej);
  })));
  return parts.flat().filter(Boolean).sort((x, y) => x.k - y.k);
}
export const contestSeed = (seed, k) => (seed * 1000003 + k * 7919) | 0;
