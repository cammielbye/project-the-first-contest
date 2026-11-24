// Computer-v-computer contests for Branch B. Run: node scripts/sim-branch-b.mjs [contests per stage] [stage]
// Cam, Nov 23: every computer-v-computer run comes in three batches, early, mid and late game, from the card pool as
// it stands. Cards are found on a steep (logarithmic) curve by pip count, so a binder's contents depend on how far
// into the game its player is. Stages, Claude's reading until Cam tunes them:
//   early: every card with 1 or 2 pips, nothing bigger;
//   mid:   that, plus one card with 3 pips, picked at random for each player;
//   late:  the whole pool.
// Reports how contests end (perfect world or world points), the first player's record, and which forces get used.
import * as R from "../branch-b/js/rules-b.js";
import { planFor, act } from "../branch-b/js/ai-b.js";

const N = Number(process.argv[2] || 100);
const STAGES = process.argv[3] ? [process.argv[3]] : ["early", "mid", "late"];
if (process.env.NOAWAY) for (const c of R.CARDS) c.away = false; // compare: no card can be played on the other player's world
for (const stage of STAGES) {
  const res = { away: 0, perfect: 0, points: 0, draw: 0, firstWins: 0, secondWins: 0, pts: [], perfectTurn: {}, used: {} };
  const t0 = Date.now();
  for (let g = 0; g < N; g++) {
    const s = R.newGame(g % 2);
    s.P[0].binder = R.binderFor(stage); s.P[1].binder = R.binderFor(stage);
    s.quiet = true;
    let guard = 0;
    while (s.phase !== "over" && guard++ < 400) {
      const P = s.pending ? s.pending.P : R.active(s);
      const plan = planFor(s, P);
      if (!plan.length) break;
      for (const a of plan) {
        const forceName = a.k === "force" && s.inst[a.id] ? R.card(s, a.id).b : null;
        if (!act(s, P, a)) break;
        if (a.k === "play" && a.side !== undefined && a.side !== P) res.away++; // counted only once it happened
        if (forceName) res.used[forceName] = (res.used[forceName] || 0) + 1;
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
  console.log(`\n${stage.toUpperCase()}: binders of ${R.binderFor(stage).length} cards${stage === "mid" ? " (one 3-pip card each)" : ""}`);
  console.log(`${N} contests in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
  console.log(`won by a perfect world ${pc(res.perfect)}, on world points ${pc(res.points)}, drawn ${pc(res.draw)}`);
  console.log(`first player won ${pc(res.firstWins)}, second ${pc(res.secondWins)}`);
  console.log(`world points at the end, both players together: average ${(res.pts.reduce((a, b) => a + b, 0) / N).toFixed(2)}`);
  console.log(`single-pip cards played on the other player's world: ${(res.away / N).toFixed(2)} a contest`);
  console.log("perfect worlds by turn:", JSON.stringify(res.perfectTurn));
  console.log("forces used per contest:", Object.entries(res.used).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k} ${(v / N).toFixed(2)}`).join(", "));
}
