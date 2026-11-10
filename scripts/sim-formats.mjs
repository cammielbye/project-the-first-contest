// Format comparison (Nov 10, for Cam): the same random 15-card binders played under each format, quick computer.
// Formats: worlds of up to 2x2 or open; one round or best of three; a cap on cards a round per player, or none.
// Scoring is the Nov 10 rule throughout (one world point per world, for one of each element or four of one element).
// Usage: node scripts/sim-formats.mjs [contests per format] [--seed n] [--only key,key] [--json out.json]
import { Worker, isMainThread, parentPort, workerData } from "node:worker_threads";
import { writeFileSync } from "node:fs";
import { cpus } from "node:os";
import * as R from "../js/game/rules.js";
import { makeAI, STYLES } from "../js/game/ai.js";
import { C, mulberry, randomBinder, contestSeed } from "./lib/field.mjs";

export const FORMATS = [];
for (const open of [false, true])
  for (const [bestOf, cap] of [[1, 0], [1, 10], [1, 7], [3, 0], [3, 5], [3, 7]])
    FORMATS.push({ key: `${open ? "open" : "2x2"}-${bestOf === 1 ? "bo1" : "bo3"}-${cap ? "cap" + cap : "nocap"}`, open, bestOf, cap });
const pips = (id) => (C[id].aff ? C[id].aff.length : 0);

function playOne(seed, f) {
  const setup = mulberry(seed), rng = mulberry(seed ^ 0x5bd1e995);
  const A = randomBinder(setup), B = randomBinder(setup);
  const styles = [0, 1].map(() => STYLES[Math.floor(setup() * STYLES.length)]);
  const opener = setup() < 0.5 ? 0 : 1;
  const s = R.newContest(A.ids, B.ids, opener, ["A", "B"], { openWorlds: f.open, bestOf: f.bestOf, noCap: !f.cap, cap: f.cap || undefined });
  const ai = styles.map((st) => makeAI({ rng, style: st, ply: 1 }));
  const plays = [0, 0], asPerm = [{}, {}], any = [{}, {}], asForce = [0, 0], asMeta = [0, 0];
  let lastP = null, flip = false; // who made the contest's last play, and whether it changed who was ahead
  R.advance(s);
  for (let guard = 0; guard < 900 && s.phase !== "contestOver"; guard++) {
    if (s.phase === "roundOver") { R.nextRound(s); continue; }
    const P = s.turn, m = ai[P].choose(s, P);
    if (m) {
      const before = R.outcome(R.score(s), 0), nr = s.rounds.length;
      plays[P]++; any[P][m.id] = 1;
      if (m.face === "perm") asPerm[P][m.id] = (asPerm[P][m.id] || 0) + 1; else if (m.face === "force") asForce[P]++; else asMeta[P]++;
      R.play(s, P, m);
      // if the play ended the round, the table has gone to the void: read the result from the round's record
      const after = s.rounds.length > nr ? (w => w === 0 ? 1 : w === 1 ? -1 : 0)(s.rounds[s.rounds.length - 1].winner) : R.outcome(R.score(s), 0);
      lastP = P; flip = after !== before;
    } else R.pass(s, P);
  }
  if (s.phase !== "contestOver") return null;
  // each binder card with a permanence side: pips, and whether it was ever played as a permanence
  const perm = [A.ids, B.ids].map((ids, P) => ids.filter((id) => C[id].aff).map((id) => [pips(id), asPerm[P][id] ? 1 : 0, any[P][id] ? 1 : 0]));
  const last = s.rounds[s.rounds.length - 1];
  return { last: lastP, flip, opener, winner: s.winner, why: s.why === "rounds" ? last.why : s.why, rounds: s.rounds.map((r) => r.winner), plays, forces: asForce, metas: asMeta, perm, pts: s.rounds.map((r) => r.score.map((x) => x.pts)) };
}

if (!isMainThread) {
  const { ks, seed, f } = workerData, out = [];
  for (const k of ks) { const r = playOne(contestSeed(seed, k), f); if (r) out.push(r); }
  parentPort.postMessage(out);
} else {
  const args = process.argv.slice(2);
  const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
  const N = Number(args.find((a, i) => /^\d+$/.test(a) && !args[i - 1]?.startsWith("--")) || 500);
  const seed = Number(opt("--seed", 1110)), only = opt("--only", null), W = cpus().length;
  const results = {};
  for (const f of FORMATS.filter((x) => !only || only.split(",").includes(x.key))) {
    const t0 = Date.now();
    const parts = await Promise.all(Array.from({ length: W }, (_, w) => new Promise((res, rej) => {
      const ks = []; for (let k = w; k < N; k += W) ks.push(k);
      const wk = new Worker(new URL(import.meta.url), { workerData: { ks, seed, f } });
      wk.on("message", res); wk.on("error", rej);
    })));
    const rows = parts.flat(), n = rows.length, dec = rows.filter((r) => r.winner !== null);
    const pct = (x, d) => Math.round((100 * x) / Math.max(1, d));
    const by = (k) => pct(rows.filter((r) => r.why === k).length, n);
    const permRate = (p, j) => { let a = 0, b = 0; for (const r of rows) for (const side of r.perm) for (const x of side) if (x[0] === p) { a++; b += x[j]; } return pct(b, a); };
    const bo3 = rows.filter((r) => r.rounds.length >= 2);
    const comeback = bo3.filter((r) => r.rounds[0] !== null && r.winner !== null && r.winner !== r.rounds[0]).length;
    results[f.key] = {
      ...f, contests: n, secs: Math.round((Date.now() - t0) / 1000),
      won: { worldPoints: by("world points"), tieBreak: by("tie-break"), draw: by("draw") },
      firstPlayer: pct(dec.filter((r) => r.winner === r.opener).length, dec.length),
      secondPlaysLast: pct(rows.filter((r) => r.last !== null && r.last !== r.opener).length, n), // in the final round
      lastPlayFlips: pct(rows.filter((r) => r.flip).length, n), // the final play changed who was ahead (or a draw)
      plays: +(rows.reduce((a, r) => a + r.plays[0] + r.plays[1], 0) / (2 * n)).toFixed(1),
      forcesPlayed: +(rows.reduce((a, r) => a + r.forces[0] + r.forces[1], 0) / (2 * n)).toFixed(1),
      worldPoints: +(rows.reduce((a, r) => a + r.pts.reduce((x, p) => x + p[0] + p[1], 0) / r.pts.length, 0) / (2 * n)).toFixed(2), // per player per round
      threeRounds: f.bestOf === 3 ? pct(rows.filter((r) => r.rounds.length === 3).length, n) : null,
      comeback: f.bestOf === 3 ? pct(comeback, n) : null,
      permPlayed: { 1: permRate(1, 1), 2: permRate(2, 1), 3: permRate(3, 1) }, // % of binder permanences by pips played as a permanence
      cardPlayed: { 1: permRate(1, 2), 2: permRate(2, 2), 3: permRate(3, 2) }, // % played at all, either side
    };
    console.log(f.key, JSON.stringify(results[f.key]));
  }
  if (opt("--json", null)) writeFileSync(opt("--json", null), JSON.stringify(results, null, 1));
}
