// One pairing, computer vs computer, with how each binder gets used up.
// Usage: node scripts/sim3-pair.mjs [contests] [--a Tides] [--b Embers] [--seed n] [--json out.json]
//        [--bo3] [--cap] [--square]  best of three, a cap of 10 a round, worlds of up to 4 (the defaults since Nov 8
//                                 are one round, no cap and open worlds; see lib/rule-flags.mjs)
//        [--aiA k=v,k=v] [--aiB …] options for each side's computer, e.g. plan=0,hidden=0 for the Nov 1 player
//        [--show k]               print contest k (counting from 0) play by play
// The opener of round 1 is random in every contest (R.nextRound alternates it after that).
import { ruleFlags, contestOpts } from "./lib/rule-flags.mjs";
import { readFileSync, writeFileSync } from "node:fs";
import * as R from "../js/game/rules.js";
import { makeAI } from "../js/game/ai.js";

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const N = Number(args.find((a) => /^\d+$/.test(a) && !args[args.indexOf(a) - 1]?.startsWith("--")) || 500);
let seed = Number(opt("--seed", 1));
const rng = () => { seed |= 0; seed = (seed + 0x6d2b79f5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };

const root = new URL("..", import.meta.url);
R.loadCards(JSON.parse(readFileSync(new URL("data/cards.json", root), "utf8")));
const binders = JSON.parse(readFileSync(new URL("data/binders.json", root), "utf8")).binders;
const short = (b) => b.name.replace(/^Binder \w, /, "");
const find = (n) => binders.find((b) => short(b).toLowerCase() === n.toLowerCase());
const A = find(opt("--a", "Tides")), B = find(opt("--b", "Embers"));
if (!A || !B) throw new Error("binder not found: " + binders.map(short).join(", "));
const names = [short(A), short(B)];
const FL = ruleFlags(args), { open, bo1, nocap } = FL;
const aiOpts = (k) => Object.fromEntries((opt(k, "") || "").split(",").filter(Boolean).map((kv) => { const [a, b] = kv.split("="); return [a, b === "false" ? false : b === "true" ? true : isNaN(Number(b)) ? b : Number(b)]; }));
const optsA = aiOpts("--aiA"), optsB = aiOpts("--aiB");
const show = Number(opt("--show", -1));

function contest(k) {
  const opener = rng() < 0.5 ? 0 : 1;
  const s = R.newContest(A.cards, B.cards, opener, names, contestOpts(FL));
  const ai = [makeAI(Object.assign({ rng }, optsA)), makeAI(Object.assign({ rng }, optsB))];
  const rounds = []; // per round: { start: [binder sizes], moves: [n, n], ids: [[...], [...]] }
  const begin = () => rounds.push({ r: s.r, start: [s.p[0].binder.length, s.p[1].binder.length], moves: [0, 0], ids: [[], []] });
  R.advance(s); begin();
  for (let guard = 0; guard < 400 && s.phase !== "contestOver"; guard++) {
    if (s.phase === "roundOver") { R.nextRound(s); begin(); continue; }
    const P = s.turn;
    const m = ai[P].choose(s, P);
    if (m) { const cur = rounds[rounds.length - 1]; cur.moves[P]++; cur.ids[P].push(m.id); R.play(s, P, m); } else R.pass(s, P);
  }
  if (s.phase !== "contestOver") throw new Error("contest did not finish");
  if (k === show) { console.log(`contest ${k}:`); for (const l of s.log) console.log(`  R${l.r} ${l.text}`); }
  for (const l of s.log) if (/\(at the cap\)/.test(l.text)) { const rr = rounds.find((x) => x.r === l.r); const P = names.findIndex((n) => l.text.startsWith(n)); if (rr && P >= 0) (rr.cap ||= [false, false])[P] = true; }
  // worlds at each round's end (and on the table when a 3-point world ends the contest): [player][world] = { cards, k }
  const worlds = s.rounds.map((r) => r.score.map((x) => x.worlds.map((w) => ({ cards: w.cards, k: w.k }))));
  if (s.why === "3-point world") worlds.push(R.score(s).map((x) => x.worlds.map((w) => ({ cards: w.cards, k: w.k }))));
  const stopped = names.map((n) => s.log.some((l) => l.text === `${n} passes.`)); // passed (stopped, conceding in effect) with cards left to play
  return { stopped, opener, winner: s.winner, why: s.why, rounds, left: [s.p[0].binder.length, s.p[1].binder.length], roundWins: s.rounds.map((r) => r.winner), roundWhy: s.rounds.map((r) => r.why), roundPts: s.rounds.map((r) => r.score.map((x) => x.pts)), worlds };
}

const t0 = Date.now();
const out = [];
for (let k = 0; k < N; k++) out.push(contest(k));
const secs = ((Date.now() - t0) / 1000).toFixed(1);

// ---- summary
const pct = (x, of) => `${((100 * x) / Math.max(1, of)).toFixed(0)}%`;
const mean = (a) => (a.length ? a.reduce((x, y) => x + y, 0) / a.length : 0);
const hist = (a) => { const h = {}; for (const v of a) h[v] = (h[v] || 0) + 1; return Object.keys(h).map(Number).sort((x, y) => x - y).map((v) => `${v}:${h[v]}`).join(" "); };
const wins = [0, 0]; let draws = 0, openerWins = 0;
const ends = {};
for (const c of out) {
  if (c.winner === null) draws++; else { wins[c.winner]++; if (c.winner === c.opener) openerWins++; }
  const shape = c.why === "rounds" ? (bo1 ? "on the count at the end of the round" : `${c.rounds.length} rounds`) : `${c.why} in round ${c.rounds.length}`;
  ends[shape] = (ends[shape] || 0) + 1;
}
console.log(`${N} contests, ${names[0]} v ${names[1]}, random opener, ${bo1 ? "one round" : "best of three"}, ${nocap ? "no card cap" : "cap of 10"}, ${open ? "open worlds" : "worlds of up to 4"}, computer ${JSON.stringify(optsA)} v ${JSON.stringify(optsB)} (${secs}s)`);
console.log(`wins: ${names[0]} ${wins[0]} (${pct(wins[0], N)}), ${names[1]} ${wins[1]} (${pct(wins[1], N)}), drawn ${draws}`);
console.log(`the round-1 opener won ${openerWins} of ${N - draws} decided contests (${pct(openerWins, N - draws)})`);
console.log(`how contests ended: ${Object.entries(ends).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k} ${v}`).join(", ")}`);
console.log(`stopped with cards still playable (passed): ${names[0]} ${pct(out.filter((c) => c.stopped[0]).length, N)}, ${names[1]} ${pct(out.filter((c) => c.stopped[1]).length, N)}`);
for (const P of [0, 1]) {
  const left = out.map((c) => c.left[P]);
  console.log(`${names[P]}: cards left in binder at the end — mean ${mean(left).toFixed(1)}, ≤5 in ${pct(left.filter((v) => v <= 5).length, N)}; spread ${hist(left)}`);
}
for (const r of [1, 2, 3]) {
  const rs = out.map((c) => c.rounds.find((x) => x.r === r)).filter(Boolean);
  if (!rs.length) continue;
  const line = [0, 1].map((P) => `${names[P]} starts with ${mean(rs.map((x) => x.start[P])).toFixed(1)}, plays ${mean(rs.map((x) => x.moves[P])).toFixed(1)} (at the cap ${pct(rs.filter((x) => x.cap?.[P]).length, rs.length)})`).join("; ");
  console.log(`round ${r} (${rs.length} played): ${line}`);
}
// worlds at round end (and at a 3-point win)
{
  const all = [], biggest = [], pts = [];
  for (const c of out) for (const tab of c.worlds) for (const P of [0, 1]) {
    for (const w of tab[P]) all.push(w);
    if (tab[P].length) biggest.push(Math.max(...tab[P].map((w) => w.cards)));
  }
  for (const c of out) for (const rp of c.roundPts) pts.push(...rp);
  const by = {}; for (const w of all) by[w.cards] = (by[w.cards] || 0) + 1;
  console.log(`worlds on the table at round end: ${all.length}; by size ${Object.entries(by).map(([k, v]) => `${k}: ${pct(v, all.length)}`).join(", ")}; biggest world per player per round, mean ${mean(biggest).toFixed(1)}, max ${Math.max(...biggest)}`);
  console.log(`world points per player per round: mean ${mean(pts).toFixed(2)}; spread ${hist(pts)}`);
  const dec = out.filter((c) => c.why === "3-point world");
  if (dec.length) console.log(`3-point worlds: ${dec.length} contests, in round ${hist(dec.map((c) => c.rounds.length))}; the winning world's size ${hist(dec.map((c) => Math.max(...c.worlds[c.worlds.length - 1][c.winner].filter((w) => w.k >= 3).map((w) => w.cards))))}`);
}
// which cards get played, and when
const C = R.C;
for (const P of [0, 1]) {
  const bind = [A, B][P].cards;
  const uniq = [...new Set(bind)];
  const rows = uniq.map((id) => {
    let contests = 0; const byR = [0, 0, 0];
    for (const c of out) { let any = false; for (const rr of c.rounds) { const n = rr.ids[P].filter((x) => x === id).length; if (n) { any = true; byR[rr.r - 1] += n; } } if (any) contests++; }
    return { id, name: C[id].meta ? C[id].name : `${C[id].name} / ${C[id].fname}`, rarity: C[id].meta ? "meta" : C[id].rarity, copies: bind.filter((x) => x === id).length, rate: contests / N, byR };
  });
  const byRarity = {};
  for (const row of rows) { const k = row.rarity; (byRarity[k] ||= []).push(row.rate); }
  console.log(`${names[P]} play rate by rarity (share of contests a card was played at all): ` + Object.entries(byRarity).map(([k, v]) => `${k} ${(100 * mean(v)).toFixed(0)}% (${v.length} cards)`).join(", "));
  rows.sort((a, b) => b.rate - a.rate);
  for (const row of rows) console.log(`   ${(100 * row.rate).toFixed(0).padStart(3)}%  ${row.rarity.padEnd(4)} ${row.name}${row.copies > 1 ? ` ×${row.copies}` : ""}  — plays by round ${row.byR.join("/")}`);
}
const jsonOut = opt("--json", null);
if (jsonOut) writeFileSync(jsonOut, JSON.stringify({ names, N, seed: Number(opt("--seed", 1)), contests: out }, null, 0));
