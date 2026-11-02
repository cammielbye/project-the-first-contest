// Computer vs computer on the third-pass rules engine (js/game/rules.js), for checking the
// rules and seeing trends. Usage: node scripts/sim3.mjs [contests per pairing] [--seed n] [--log]
import { readFileSync } from "node:fs";
import * as R from "../js/game/rules.js";
import { makeAI } from "../js/game/ai.js";

const args = process.argv.slice(2);
const N = Number(args.find((a) => /^\d+$/.test(a)) || 4);
const seedArg = args.indexOf("--seed");
let seed = seedArg >= 0 ? Number(args[seedArg + 1]) : 1;
const showLog = args.includes("--log");
const rng = () => { seed |= 0; seed = (seed + 0x6d2b79f5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };

const root = new URL("..", import.meta.url);
R.loadCards(JSON.parse(readFileSync(new URL("data/cards.json", root), "utf8")));
const binders = JSON.parse(readFileSync(new URL("data/binders.json", root), "utf8")).binders;

function contest(bA, bB) {
  const s = R.newContest(bA.cards, bB.cards, rng() < 0.5 ? 0 : 1, [bA.name.replace(/^Binder \w, /, ""), bB.name.replace(/^Binder \w, /, "")]);
  const ai = [makeAI({ rng }), makeAI({ rng })];
  const plays = [0, 0];
  R.advance(s);
  for (let guard = 0; guard < 400 && s.phase !== "contestOver"; guard++) {
    if (s.phase === "roundOver") { R.nextRound(s); continue; }
    const P = s.turn;
    const m = ai[P].choose(s, P);
    if (m) { R.play(s, P, m); plays[P]++; } else R.pass(s, P);
  }
  if (s.phase !== "contestOver") throw new Error("contest did not finish");
  return { s, plays };
}

const stats = {};
const t0 = Date.now();
let n = 0;
for (let a = 0; a < binders.length; a++) for (let b = a + 1; b < binders.length; b++) {
  const key = `${binders[a].name.replace(/^Binder \w, /, "")} v ${binders[b].name.replace(/^Binder \w, /, "")}`;
  const st = (stats[key] = { contests: 0, wins: [0, 0], draws: 0, decisive: 0, archipelago: 0, cradle: 0, rounds: 0, byPoints: 0, byTie: 0, roundDraws: 0, zeroZero: 0, cards: 0 });
  for (let k = 0; k < N; k++) {
    const swap = k % 2 === 1;
    const [x, y] = swap ? [binders[b], binders[a]] : [binders[a], binders[b]];
    const { s, plays } = contest(x, y);
    n++;
    st.contests++;
    const w = s.winner === null ? null : swap ? 1 - s.winner : s.winner;
    if (w === null) st.draws++; else st.wins[w]++;
    if (s.why === "3-point world") st.decisive++;
    if (s.why === "Cradle") st.cradle++;
    for (const r of s.rounds) {
      st.rounds++;
      if (r.why === "Archipelago") st.archipelago++;
      else if (r.why === "world points") st.byPoints++;
      else if (r.why === "tie-break") st.byTie++;
      else st.roundDraws++;
      if (r.score[0].pts === 0 && r.score[1].pts === 0) st.zeroZero++;
    }
    st.cards += plays[0] + plays[1];
    if (showLog && k === 0) for (const l of s.log) console.log(`  R${l.r} ${l.text}`);
  }
}
console.log(`${n} contests in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
for (const [k, st] of Object.entries(stats)) {
  const pct = (x, of) => `${Math.round((100 * x) / Math.max(1, of))}%`;
  console.log(`${k}: wins ${st.wins[0]}-${st.wins[1]} (${st.draws} drawn) · decided by a 3-point world ${st.decisive}, Cradle ${st.cradle} · rounds ${st.rounds}: world points ${pct(st.byPoints, st.rounds)}, tie-break ${pct(st.byTie, st.rounds)}, Archipelago ${st.archipelago}, drawn ${st.roundDraws}, 0-0 ${pct(st.zeroZero, st.rounds)} · ${(st.cards / st.contests).toFixed(1)} cards a contest`);
}
