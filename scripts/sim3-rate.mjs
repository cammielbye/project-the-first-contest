// Card ratings from random binders (Nov 8). Each contest, each side gets a random legal binder: one of each card,
// 15 cards since Nov 8 (8 commons, 4 uncommons and 3 rares; meta cards counted at their rarity), no pinnacles or Origin, leaning toward
// none, one or two elements. Every card is then rated by how much having it in a binder changes the chance of
// winning, against an average card of its rarity, with the other 14 cards accounted for (a logistic regression).
//
// Usage: node scripts/sim3-rate.mjs [contests] [--bo3] [--cap] [--square] [--seed n] [--workers n] [--json out.json]
//        (rules default to one round, no card cap, open worlds: see lib/rule-flags.mjs)
//        [--quick]                     the quick computer (no reply lookahead), about 6x faster, for wide screens
//        [--styles plain,builder,…]    styles to draw from for each side, each contest (default: all six);
//                                      --styles builder for one style
//        [--ai k=v,…]                  extra computer settings for both sides
//        [--knobs archipelagoWater=12,…] win-condition numbers (perfectWorld, archipelagoWater, mountainPer, cradleEach)
//        [--first k]                   start at contest k of the run (to split one run across machines)
//        [--faces]                     rate each side of a card alone (Cam, Nov 8): every two-sided card splits into a
//                                      permanence-only and a force-only card, drawn into binders separately
//        [--from a.json,b.json]        summarize saved runs together instead of playing
//        [--csv out.csv]               the card ratings as a table
import { ruleFlags } from "./lib/rule-flags.mjs";
import { readFileSync, writeFileSync } from "node:fs";
import { cpus } from "node:os";
import { C, ELS, STYLES, runField, addFaceCards, sideLabel } from "./lib/field.mjs";

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const N = Number(args.find((a, i) => /^\d+$/.test(a) && !args[i - 1]?.startsWith("--")) || 1000);
const from = opt("--from", null);
let rows, label;
if (from) {
  const runs = from.split(",").map((f) => JSON.parse(readFileSync(f, "utf8")));
  rows = runs.flatMap((r) => r.contests); label = runs[0].label + ` (${runs.length} runs merged)`;
} else {
  const cfg = {
    ...ruleFlags(args), quick: args.includes("--quick"), faces: args.includes("--faces"),
    styles: (opt("--styles", Object.keys(STYLES).join(","))).split(","),
    ai: Object.fromEntries((opt("--ai", "") || "").split(",").filter(Boolean).map((kv) => { const [a, b] = kv.split("="); return [a, b === "false" ? false : b === "true" ? true : isNaN(Number(b)) ? b : Number(b)]; })),
    knobs: Object.fromEntries((opt("--knobs", "") || "").split(",").filter(Boolean).map((kv) => { const [a, b] = kv.split("="); return [a, Number(b)]; })),
  };
  for (const st of cfg.styles) if (!STYLES[st]) throw new Error("unknown style " + st);
  const seed = Number(opt("--seed", 1)), first = Number(opt("--first", 0));
  label = `${cfg.bo1 ? "one round" : "best of three"}, ${cfg.nocap ? "no card cap" : "cap of 10"}, ${cfg.open ? "uncapped worlds" : "worlds of up to 4"}; ${cfg.quick ? "quick" : "full"} computer, styles ${cfg.styles.join("/")}${Object.keys(cfg.ai).length ? " " + JSON.stringify(cfg.ai) : ""}${Object.keys(cfg.knobs).length ? "; " + JSON.stringify(cfg.knobs) : ""}${cfg.faces ? "; each side of a card rated alone" : ""}; seed ${seed}`;
  const t0 = Date.now();
  rows = await runField(first, N, seed, cfg, Number(opt("--workers", cpus().length)));
  console.log(`${rows.length} contests in ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  const j = opt("--json", null);
  if (j) writeFileSync(j, JSON.stringify({ label, contests: rows }));
}
if (rows.some((r) => r.a.some((id) => id >= 10000))) addFaceCards(); // one-sided cards (--faces)
report(rows, label, opt("--csv", null));

// ---------------------------------------------------------------- analysis
function report(rows, label, csv) {
  const pct = (a, b) => `${((100 * a) / Math.max(1, b)).toFixed(0)}%`;
  const score = (r, P) => (r.winner === null ? 0.5 : r.winner === P ? 1 : 0);
  console.log(`\n${rows.length} contests: ${label}`);
  const dec = rows.filter((r) => r.winner !== null);
  console.log(`first player won ${pct(dec.filter((r) => r.winner === r.opener).length, dec.length)} of decided; drawn ${pct(rows.length - dec.length, rows.length)}`);
  const ways = {}; for (const r of rows) ways[r.why] = (ways[r.why] || 0) + 1;
  console.log(`how contests were won: ${Object.entries(ways).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k} ${pct(v, rows.length)}`).join(", ")}`);

  // by lean and by style: each side's average score (1 win, 0.5 draw)
  const group = (key) => {
    const g = {};
    for (const r of rows) for (const P of [0, 1]) { const k = key(r, P); (g[k] ||= { n: 0, s: 0, ways: {} }); g[k].n++; g[k].s += score(r, P); if (r.winner === P) g[k].ways[r.why] = (g[k].ways[r.why] || 0) + 1; }
    return Object.entries(g).sort((a, b) => b[1].s / b[1].n - a[1].s / a[1].n);
  };
  console.log("\nby lean (each side's score: a win 1, a draw 0.5):");
  for (const [k, v] of group((r, P) => r.lean[P])) console.log(`  ${k.padEnd(12)} ${(100 * v.s / v.n).toFixed(0)}%  (${v.n} binders)  wins by ${Object.entries(v.ways).sort((a, b) => b[1] - a[1]).map(([w, n]) => `${w} ${n}`).join(", ")}`);
  console.log("\nby element (binders leaning on it, alone or with another):");
  for (const e of ELS) {
    let n = 0, s = 0;
    for (const r of rows) for (const P of [0, 1]) if (r.lean[P].split("+").includes(e)) { n++; s += score(r, P); }
    console.log(`  ${e.padEnd(6)} ${(100 * s / n).toFixed(0)}%  (${n} binders)`);
  }
  console.log("\nby computer style:");
  for (const [k, v] of group((r, P) => r.styles[P])) console.log(`  ${k.padEnd(8)} ${(100 * v.s / v.n).toFixed(0)}%  (${v.n})`);

  // per card: raw numbers
  const ids = [...new Set(rows.flatMap((r) => [...r.a, ...r.b]))];
  const col = new Map(ids.map((id, k) => [id, k]));
  const st = ids.map(() => ({ n: 0, s: 0, pn: 0, ps: 0 }));
  for (const r of rows) for (const P of [0, 1]) {
    const mine = P === 0 ? r.a : r.b, pl = new Set(r.played[P]);
    for (const id of mine) { const x = st[col.get(id)]; x.n++; x.s += score(r, P); if (pl.has(id)) { x.pn++; x.ps += score(r, P); } }
  }
  // logistic regression: P(A wins) = σ(β·x + γ·opener), x_c = [c in A] − [c in B], draws as 0.5
  const K = ids.length, lam = 2;
  const X = rows.map((r) => { const v = new Map(); for (const id of r.a) v.set(col.get(id), 1); for (const id of r.b) { const c = col.get(id); v.set(c, (v.get(c) || 0) - 1); } return [...v].filter(([, x]) => x); });
  const Y = rows.map((r) => score(r, 0)), O = rows.map((r) => (r.opener === 0 ? 1 : -1));
  const beta = new Float64Array(K); let gam = 0;
  const m1 = new Float64Array(K + 1), m2 = new Float64Array(K + 1);
  for (let it = 1; it <= 600; it++) {
    const g = new Float64Array(K + 1);
    for (let i = 0; i < rows.length; i++) {
      let z = gam * O[i]; for (const [c, x] of X[i]) z += beta[c] * x;
      const p = 1 / (1 + Math.exp(-z)), e = p - Y[i];
      for (const [c, x] of X[i]) g[c] += e * x;
      g[K] += e * O[i];
    }
    for (let c = 0; c < K; c++) g[c] += lam * beta[c];
    for (let c = 0; c <= K; c++) { // Adam
      m1[c] = 0.9 * m1[c] + 0.1 * g[c]; m2[c] = 0.999 * m2[c] + 0.001 * g[c] * g[c];
      const step = (0.05 * (m1[c] / (1 - 0.9 ** it))) / (Math.sqrt(m2[c] / (1 - 0.999 ** it)) + 1e-8);
      if (c < K) beta[c] -= step; else gam -= step;
    }
  }
  // standard errors from the information matrix's diagonal
  const info = new Float64Array(K).fill(lam);
  for (let i = 0; i < rows.length; i++) {
    let z = gam * O[i]; for (const [c, x] of X[i]) z += beta[c] * x;
    const p = 1 / (1 + Math.exp(-z));
    for (const [c, x] of X[i]) info[c] += p * (1 - p) * x * x;
  }
  // centre within each rarity: a rating is against an average card of the same rarity
  const rk = (id) => C[id].rarity;
  const mean = {}; for (const r of ["C", "B", "A"]) { const cs = ids.filter((id) => rk(id) === r); mean[r] = cs.reduce((a, id) => a + beta[col.get(id)], 0) / cs.length; }
  const out = ids.map((id) => {
    const c = col.get(id), d = C[id], x = st[c];
    return {
      no: d.no, card: sideLabel(d), side: d.meta ? "meta" : d.only === "perm" ? "permanence" : d.only === "force" ? "force" : "both", rarity: { C: "common", B: "uncommon", A: "rare" }[d.rarity] + (d.meta ? " (meta)" : ""),
      rating: 25 * (beta[c] - mean[d.rarity]), ci: 25 * 1.96 / Math.sqrt(info[c]),
      binders: x.n, score: x.s / x.n, playRate: x.pn / x.n, scoreWhenPlayed: x.pn ? x.ps / x.pn : null,
    };
  }).sort((a, b) => b.rating - a.rating);
  console.log(`\nfirst-player effect in the model: ${(25 * gam).toFixed(1)} points`);
  const line = (r) => `  ${(r.rating >= 0 ? "+" : "") + r.rating.toFixed(1).padStart(5)} ±${r.ci.toFixed(1)}  ${r.card.padEnd(r.side === "both" || r.side === "meta" ? 16 : 34)} ${r.rarity.padEnd(16)} in ${String(r.binders).padStart(4)} binders, played ${(100 * r.playRate).toFixed(0).padStart(3)}%, scored ${(100 * r.score).toFixed(0)}%`;
  console.log("\ncard ratings: points of win chance against an average card of the same rarity (± is the 95% range)");
  console.log(" strongest:"); out.slice(0, 15).forEach((r) => console.log(line(r)));
  console.log(" weakest:"); out.slice(-15).forEach((r) => console.log(line(r)));
  if (out.some((r) => r.side === "force")) {
    console.log("\naverage by side, within each rarity (points against the rarity's average card):");
    for (const [rr, word] of [["C", "common"], ["B", "uncommon"], ["A", "rare"]]) {
      const parts = ["permanence", "force", "meta"].map((sd) => { const xs = out.filter((r) => r.rarity.startsWith(word) && r.side === sd); return xs.length ? `${sd} ${(xs.reduce((a, r) => a + r.rating, 0) / xs.length >= 0 ? "+" : "")}${(xs.reduce((a, r) => a + r.rating, 0) / xs.length).toFixed(1)} (${xs.length})` : null; }).filter(Boolean);
      console.log(`  ${word.padEnd(9)} ${parts.join(", ")}`);
    }
  }
  const clear = out.filter((r) => Math.abs(r.rating) > r.ci);
  console.log(`\n${clear.length} of ${out.length} cards are clearly above or below average at this sample size`);
  if (csv) writeFileSync(csv, "no,card,side,rarity,rating,ci95,binders,score,play_rate,score_when_played\n" + out.map((r) => [r.no, `"${r.card}"`, r.side, r.rarity, r.rating.toFixed(2), r.ci.toFixed(2), r.binders, r.score.toFixed(3), r.playRate.toFixed(3), r.scoreWhenPlayed === null ? "" : r.scoreWhenPlayed.toFixed(3)].join(",")).join("\n") + "\n");
}
