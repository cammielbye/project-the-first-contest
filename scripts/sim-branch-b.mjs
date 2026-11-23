// Computer-v-computer contests for Branch B. Run: node scripts/sim-branch-b.mjs [contests]
// Reports how contests end (perfect world or world points), the first player's record, and which forces get used.
import * as R from "../branch-b/js/rules-b.js";
import { planFor, act } from "../branch-b/js/ai-b.js";

const N = Number(process.argv[2] || 200);
if (process.env.NOAWAY) for (const c of R.CARDS) c.away = false; // compare: no card can be played on the other player's world
const res = { away: 0, perfect: 0, points: 0, draw: 0, firstWins: 0, secondWins: 0, pts: [], perfectTurn: {}, used: {} };
const t0 = Date.now();
for (let g = 0; g < N; g++) {
  const s = R.newGame(g % 2);
  s.quiet = true;
  let guard = 0;
  while (s.phase !== "over" && guard++ < 400) {
    const P = s.pending ? s.pending.P : R.active(s);
    const plan = planFor(s, P);
    if (!plan.length) break;
    for (const a of plan) {
      if (a.k === "play" && a.side !== undefined && a.side !== P) res.away++;
      if (a.k === "force") { const n = R.card(s, a.id).b; res.used[n] = (res.used[n] || 0) + 1; }
      if (!act(s, P, a)) break;
      if (s.phase === "over") break;
      if (s.pending && s.pending.P !== P) break;
    }
  }
  const w = s.winner;
  if (!w || w.P === null) res.draw++;
  else {
    if (w.why === "perfect" || w.why === "both-perfect") { res.perfect++; const t = R.turnNo(s); res.perfectTurn[t] = (res.perfectTurn[t] || 0) + 1; }
    else res.points++;
    if (w.P === s.first) res.firstWins++; else res.secondWins++;
  }
  res.pts.push(R.total(s, 0) + R.total(s, 1));
}
const pc = (x) => `${((100 * x) / N).toFixed(1)}%`;
console.log(`${N} contests in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
console.log(`won by a perfect world ${pc(res.perfect)}, on world points ${pc(res.points)}, drawn ${pc(res.draw)}`);
console.log(`first player won ${pc(res.firstWins)}, second ${pc(res.secondWins)}`);
console.log(`world points at the end, both players together: average ${(res.pts.reduce((a, b) => a + b, 0) / N).toFixed(2)}`);
console.log(`single-pip cards played on the other player's world: ${(res.away / N).toFixed(2)} a contest`);
console.log("perfect worlds by turn:", JSON.stringify(res.perfectTurn));
console.log("forces used per contest:", Object.entries(res.used).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k} ${(v / N).toFixed(2)}`).join(", "));
