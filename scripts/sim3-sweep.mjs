// Sweep one win-condition number over a few values on the same random-binder contests (Nov 8), adding contests in
// batches and stopping once each value's main figure is known to within --precision points (or at --max).
// Usage: node scripts/sim3-sweep.mjs --knob archipelagoWater=8,10,12 [--bo3] [--cap] [--square] [--quick]
//        [--styles …] [--seed n] [--batch 200] [--max 2000] [--precision 3] [--workers n]
// Knobs: archipelagoWater (Archipelago's water), mountainPer (earth per Mountain Range point),
//        cradleEach (Cradle's count of each affinity), perfectWorld (world points that win the contest at once).
// The main figure: for a card's number, the score of binders holding that card (a win 1, a draw 0.5): side A always
// holds it, and side B sometimes does;
// for perfectWorld, the share of contests won by a Perfect World.
import { ruleFlags } from "./lib/rule-flags.mjs";
import { cpus } from "node:os";
import { C, ELS, STYLES, runField } from "./lib/field.mjs";

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const [knob, list] = (opt("--knob", "") || "").split("=");
if (!knob || !list) throw new Error("--knob name=v1,v2,…");
const values = list.split(",").map(Number);
const CARD = { archipelagoWater: "Archipelago", mountainPer: "Mountain Range", cradleEach: "Cradle" }[knob] || null;
const cardId = CARD ? Object.values(C).find((d) => d.name === CARD && !d.meta)?.id : null;
const cfg = {
  ...ruleFlags(args), quick: args.includes("--quick"),
  styles: (opt("--styles", Object.keys(STYLES).join(","))).split(","), ai: {},
  forceA: cardId ? [cardId] : [], // side A always holds the card, so every contest measures it
};
const seed = Number(opt("--seed", 1)), batch = Number(opt("--batch", 200)), max = Number(opt("--max", 2000));
const precision = Number(opt("--precision", 3)), workers = Number(opt("--workers", cpus().length));

const score = (r, P) => (r.winner === null ? 0.5 : r.winner === P ? 1 : 0);
const holders = (r) => [0, 1].filter((P) => (P === 0 ? r.a : r.b).includes(cardId));
// the main figure for one contest: the holders' average score (null if no side holds the card), or 1 for a Perfect World win
const main = (r) => {
  if (!CARD) return r.why === "3-point world" ? 1 : 0;
  const h = holders(r); if (!h.length) return null;
  return h.reduce((a, P) => a + score(r, P), 0) / h.length;
};
const stats = (xs) => { const v = xs.filter((x) => x !== null), n = v.length, m = v.reduce((a, b) => a + b, 0) / Math.max(1, n); const sd = Math.sqrt(v.reduce((a, b) => a + (b - m) ** 2, 0) / Math.max(1, n - 1)); return { n, m, ci: (196 * sd) / Math.sqrt(Math.max(1, n)) }; };

console.log(`sweep ${knob} over ${values.join(", ")}; ${cfg.bo1 ? "one round" : "best of three"}, ${cfg.nocap ? "no card cap" : "cap of 10"}, ${cfg.open ? "uncapped worlds" : "worlds of up to 4"}; ${cfg.quick ? "quick" : "full"} computer; seed ${seed}`);
console.log(`main figure: ${CARD ? `score of binders holding ${CARD}` : "share of contests won by a Perfect World"}; stopping at ±${precision} points or ${max} contests per value`);
const runs = values.map(() => []);
const t0 = Date.now();
for (let done = 0; done < max; ) {
  const n = Math.min(batch, max - done);
  for (let i = 0; i < values.length; i++) runs[i].push(...(await runField(done, n, seed, Object.assign({}, cfg, { knobs: { [knob]: values[i] } }), workers)));
  done += n;
  const widest = Math.max(...runs.map((rs) => stats(rs.map(main)).ci));
  console.log(`  ${done} contests per value (${((Date.now() - t0) / 1000).toFixed(0)}s): widest range ±${widest.toFixed(1)}`);
  if (widest <= precision) break;
}

console.log(`\n${knob} | main figure | change from the value before (same contests) | how contests were won | first player`);
for (let i = 0; i < values.length; i++) {
  const rs = runs[i], st = stats(rs.map(main));
  let diff = "";
  if (i > 0) { // paired by contest number
    const prev = new Map(runs[i - 1].map((r) => [r.k, main(r)]));
    const d = stats(rs.map((r) => { const a = main(r), b = prev.get(r.k); return a === null || b === null || b === undefined ? null : a - b; }));
    diff = `${d.m >= 0 ? "+" : ""}${(100 * d.m).toFixed(1)} ±${d.ci.toFixed(1)}`;
  }
  const ways = {}; for (const r of rs) ways[r.why] = (ways[r.why] || 0) + 1;
  const dec = rs.filter((r) => r.winner !== null);
  console.log(`${values[i]} | ${(100 * st.m).toFixed(1)}% ±${st.ci.toFixed(1)} (${st.n}) | ${diff || "—"} | ${Object.entries(ways).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k} ${((100 * v) / rs.length).toFixed(0)}%`).join(", ")} | ${((100 * dec.filter((r) => r.winner === r.opener).length) / Math.max(1, dec.length)).toFixed(0)}%`);
}
console.log("\nby element (binders leaning on it), per value:");
console.log(["element", ...values].join(" | "));
for (const e of ELS) {
  const row = [e];
  for (const rs of runs) { let n = 0, s = 0; for (const r of rs) for (const P of [0, 1]) if (r.lean[P].split("+").includes(e)) { n++; s += score(r, P); } row.push(`${((100 * s) / Math.max(1, n)).toFixed(0)}%`); }
  console.log(row.join(" | "));
}
