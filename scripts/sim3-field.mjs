// A field of binders, computer vs computer: each contest, each side picks a binder at random (mirror matches allowed).
// Usage: node scripts/sim3-field.mjs [contests] [--binders Tides,Embers,Gales,Roots] [--seed n] [--json out.json]
//        [--bo3] [--cap] [--square]   the rule switches, as in sim3-pair.mjs (default: one round, no cap, open worlds)
//        [--ai k=v,k=v]               options for both computers, e.g. bigWorld=2
//        [--from a.json,b.json]       skip playing: summarize saved runs together
import { ruleFlags, contestOpts, openerFor } from "./lib/rule-flags.mjs";
import { readFileSync, writeFileSync } from "node:fs";
import * as R from "../js/game/rules.js";
import { makeAI } from "../js/game/ai.js";

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const N = Number(args.find((a, i) => /^\d+$/.test(a) && !args[i - 1]?.startsWith("--")) || 500);
let seed = Number(opt("--seed", 1));
const rng = () => { seed |= 0; seed = (seed + 0x6d2b79f5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
const FL = ruleFlags(args), { open, bo1, nocap } = FL;
const aiOpts = Object.fromEntries((opt("--ai", "") || "").split(",").filter(Boolean).map((kv) => { const [a, b] = kv.split("="); return [a, b === "false" ? false : b === "true" ? true : isNaN(Number(b)) ? b : Number(b)]; }));

const root = new URL("..", import.meta.url);
R.loadCards(JSON.parse(readFileSync(new URL("data/cards.json", root), "utf8")));
const all = JSON.parse(readFileSync(new URL("data/binders.json", root), "utf8")).binders;
const short = (b) => b.name.replace(/^Binder \w, /, "");
const field = (opt("--binders", "Tides,Embers,Gales,Roots")).split(",").map((n) => {
  const b = all.find((x) => short(x).toLowerCase() === n.toLowerCase());
  if (!b) throw new Error("binder not found: " + n);
  return b;
});

function contest() {
  const ia = Math.floor(rng() * field.length), ib = Math.floor(rng() * field.length);
  const A = field[ia], B = field[ib];
  const names = ia === ib ? [`${short(A)} 1`, `${short(B)} 2`] : [short(A), short(B)];
  const { opener, reveals } = openerFor(FL, A.cards, B.cards, rng()); // the reveal (Nov 11), or the coin with --coin
  const s = R.newContest(A.cards, B.cards, opener, names, { ...contestOpts(FL), reveals });
  const ai = [makeAI(Object.assign({ rng }, aiOpts)), makeAI(Object.assign({ rng }, aiOpts))];
  const plays = [0, 0];
  R.advance(s);
  for (let guard = 0; guard < 600 && s.phase !== "contestOver"; guard++) {
    if (s.phase === "roundOver") { R.nextRound(s); continue; }
    const P = s.turn, m = ai[P].choose(s, P);
    if (m) { plays[P]++; R.play(s, P, m); } else R.pass(s, P);
  }
  if (s.phase !== "contestOver") throw new Error("contest did not finish");
  const fin = s.why === "3-point world" ? R.score(s) : s.rounds[s.rounds.length - 1].score;
  return {
    binders: [short(A), short(B)], opener, winner: s.winner, why: s.why, roundWhy: s.rounds.map((r) => r.why), rounds: s.rounds.length,
    plays, left: [s.p[0].binder.length, s.p[1].binder.length],
    stopped: names.map((n) => s.log.some((l) => l.text === `${n} passes.`)),
    worlds: fin.map((x) => x.worlds.map((w) => ({ cards: w.cards, k: w.k }))), pts: fin.map((x) => x.pts),
  };
}

let out, label;
const from = opt("--from", null);
if (from) {
  const runs = from.split(",").map((f) => JSON.parse(readFileSync(f, "utf8")));
  out = runs.flatMap((r) => r.contests); label = runs[0].label + ` (${runs.length} files merged)`;
} else {
  const t0 = Date.now();
  out = []; for (let k = 0; k < N; k++) out.push(contest());
  label = `${field.map(short).join(", ")}; ${bo1 ? "one round" : "best of three"}, ${nocap ? "no card cap" : "cap of 10"}, ${open ? "open worlds" : "worlds of up to 4"}; computer ${JSON.stringify(aiOpts)}`;
  console.log(`(${((Date.now() - t0) / 1000).toFixed(0)}s)`);
  const j = opt("--json", null);
  if (j) writeFileSync(j, JSON.stringify({ label, seed: Number(opt("--seed", 1)), contests: out }));
}

// ---- summary
const pct = (a, b) => `${((100 * a) / Math.max(1, b)).toFixed(0)}%`;
const mean = (a) => (a.length ? a.reduce((x, y) => x + y, 0) / a.length : 0);
const names = [...new Set(out.flatMap((c) => c.binders))];
const how = (c) => (c.why === "3-point world" ? "3-point world" : c.roundWhy[c.roundWhy.length - 1] || "rounds");
console.log(`${out.length} contests: ${label}`);
const dec = out.filter((c) => c.winner !== null);
console.log(`first player won ${pct(dec.filter((c) => c.winner === c.opener).length, dec.length)} of decided; drawn ${pct(out.length - dec.length, out.length)}`);
const ways = {}; for (const c of out) ways[how(c)] = (ways[how(c)] || 0) + 1;
console.log(`how contests ended: ${Object.entries(ways).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k} ${v} (${pct(v, out.length)})`).join(", ")}`);
// each binder against the others (mirrors left out of the win rates)
console.log("\nbinder | contests (not mirrors) | won | lost | drawn | ways it won");
for (const n of names) {
  let g = 0, w = 0, l = 0, d = 0; const wy = {};
  for (const c of out) {
    if (c.binders[0] === c.binders[1]) continue;
    const P = c.binders.indexOf(n); if (P < 0) continue;
    g++;
    if (c.winner === null) d++; else if (c.winner === P) { w++; wy[how(c)] = (wy[how(c)] || 0) + 1; } else l++;
  }
  console.log(`${n} | ${g} | ${pct(w, g)} | ${pct(l, g)} | ${pct(d, g)} | ${Object.entries(wy).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k} ${v}`).join(", ")}`);
}
console.log("\nmatchups: row binder's win rate against column binder (decided and drawn counted; n in brackets)");
console.log(["", ...names].join(" | "));
for (const a of names) {
  const row = [a];
  for (const b of names) {
    let g = 0, w = 0;
    for (const c of out) {
      if (a === b) { if (c.binders[0] === a && c.binders[1] === a) { g++; } continue; }
      const P = c.binders.indexOf(a); if (P < 0 || c.binders[1 - P] !== b) continue;
      g++; if (c.winner === P) w++;
    }
    row.push(a === b ? `mirror (${g})` : `${pct(w, g)} (${g})`);
  }
  console.log(row.join(" | "));
}
// 3-point worlds and Archipelago / Cradle by binder
const tpw = out.filter((c) => c.why === "3-point world");
const by = {}; for (const c of tpw) { const n = c.binders[c.winner]; by[n] = (by[n] || 0) + 1; }
console.log(`\n3-point worlds: ${tpw.length} (${pct(tpw.length, out.length)}); by ${Object.entries(by).map(([k, v]) => `${k} ${v}`).join(", ")}; winning world's size mean ${mean(tpw.map((c) => Math.max(...c.worlds[c.winner].filter((w) => w.k >= 3).map((w) => w.cards)))).toFixed(1)}`);
const big = out.flatMap((c) => [0, 1].map((P) => c.worlds[P].length ? Math.max(...c.worlds[P].map((w) => w.cards)) : 0));
console.log(`biggest world per player at the end: mean ${mean(big).toFixed(1)}, max ${Math.max(...big)}; world points per player at the end: mean ${mean(out.flatMap((c) => c.pts)).toFixed(2)}`);
const left = out.flatMap((c) => c.left);
console.log(`plays per player: mean ${mean(out.flatMap((c) => c.plays)).toFixed(1)}; cards left: mean ${mean(left).toFixed(1)}, 5 or fewer ${pct(left.filter((v) => v <= 5).length, left.length)}, empty ${pct(left.filter((v) => v === 0).length, left.length)}`);
for (const n of names) {
  const l = [], p = [];
  for (const c of out) c.binders.forEach((b, P) => { if (b === n) { l.push(c.left[P]); p.push(c.plays[P]); } });
  console.log(`  ${n}: plays ${mean(p).toFixed(1)}, cards left ${mean(l).toFixed(1)}, 5 or fewer ${pct(l.filter((v) => v <= 5).length, l.length)}`);
}
