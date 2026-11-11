// How few cards a world point takes, and how many world points a binder could make at most (Nov 11, for Cam: 16-card
// binders, four binder pages of 2x2). Pips only: card text is left out (Mirage's copies, the +1 cards, Hanging Valley).
// Nov 10 scoring: a world of up to 2x2 scores one point for one of each element or four of one element, one point at most.
// Usage: node scripts/point-ceiling.mjs [random binders, default 4000]
import { C, mulberry, randomBinder } from "./lib/field.mjs";
import { readFileSync } from "node:fs";

const each = (toks) => { // a distinct pip for each element (matching)
  const n = toks.length; if (n < 4) return false;
  const used = new Array(n).fill(false);
  const go = (e) => { if (e === 4) return true; for (let i = 0; i < n; i++) if (!used[i] && toks[i] & (1 << e)) { used[i] = true; if (go(e + 1)) return true; used[i] = false; } return false; };
  return go(0);
};
const same = (toks) => { for (let e = 0; e < 4; e++) { let k = 0; for (const t of toks) if (t & (1 << e)) k++; if (k >= 4) return true; } return false; };
const scores = (ids) => { const toks = ids.flatMap((id) => C[id].aff); return each(toks) || same(toks); };

// the most world points a set of permanences can make in worlds of up to four, and the fewest cards that does it with
function ceiling(ids) {
  const n = ids.length, groups = [];
  for (let m = 1; m < 1 << n; m++) { let k = 0; for (let x = m; x; x &= x - 1) k++; if (k > 4) continue; const g = []; for (let i = 0; i < n; i++) if (m & (1 << i)) g.push(ids[i]); if (scores(g)) groups.push([m, k]); }
  // keep only minimal groups (no scoring group inside them): a spare card never adds a point
  const minimal = groups.filter(([m]) => !groups.some(([o]) => o !== m && (o & m) === o));
  const memo = new Map();
  const f = (mask) => {
    if (memo.has(mask)) return memo.get(mask);
    let best = [0, 0];
    for (const [m, k] of minimal) if ((m & mask) === m) { const r = f(mask & ~m); if (r[0] + 1 > best[0] || (r[0] + 1 === best[0] && r[1] + k < best[1])) best = [r[0] + 1, r[1] + k]; }
    memo.set(mask, best); return best;
  };
  return f((1 << n) - 1);
}

const perms = (ids) => ids.filter((id) => C[id] && !C[id].meta && C[id].aff);
const N = Number(process.argv[2] || 4000), rng = mulberry(1111);
const dist = {}, sizes = {}; let pts = 0, cards = 0, pc = 0;
for (let k = 0; k < N; k++) {
  const ids = perms(randomBinder(rng).ids); pc += ids.length;
  const [p, c] = ceiling(ids); dist[p] = (dist[p] || 0) + 1; pts += p; cards += c;
}
console.log(`random 16-card binders (${N}): permanences ${(pc / N).toFixed(1)}; most world points ${JSON.stringify(dist)}; mean ${(pts / N).toFixed(2)}, using ${(cards / Math.max(1, pts)).toFixed(2)} cards a point`);
const B = JSON.parse(readFileSync(new URL("../data/binders.json", import.meta.url), "utf8")).binders;
for (const b of B) { const ids = perms(b.cards.map((x) => x.id ?? x)); const [p, c] = ceiling(ids); console.log(`${b.name}: ${ids.length} permanences, at most ${p} world points from ${c} cards`); }

// the smallest scoring groups in the pool, by size and rarity (pinnacles apart)
const pool = Object.values(C).filter((d) => d && d.id && !d.meta && d.aff && d.rarity !== "S");
const bySize = { 1: {}, 2: {}, 3: {}, 4: {} }, add = (s, g) => { const key = g.map((id) => C[id].rarity).sort().join(""); bySize[s][key] = (bySize[s][key] || 0) + 1; };
const P = pool.map((d) => d.id), pairs = new Set();
for (const a of P) if (scores([a])) add(1, [a]);
for (let i = 0; i < P.length; i++) for (let j = i + 1; j < P.length; j++) if (scores([P[i], P[j]])) { add(2, [P[i], P[j]]); pairs.add(P[i] + "," + P[j]); }
const hasPair = (g) => g.some((a, i) => g.some((b, j) => j > i && pairs.has(Math.min(a, b) + "," + Math.max(a, b))));
const com = P.filter((id) => C[id].rarity === "C");
for (let i = 0; i < P.length; i++) for (let j = i + 1; j < P.length; j++) for (let k = j + 1; k < P.length; k++) { const g = [P[i], P[j], P[k]]; if (!hasPair(g) && scores(g)) add(3, g); }
let four = 0; for (let a = 0; a < com.length; a++) for (let b = a + 1; b < com.length; b++) for (let c = b + 1; c < com.length; c++) for (let d = c + 1; d < com.length; d++) if (scores([com[a], com[b], com[c], com[d]])) four++;
console.log("smallest scoring groups (no pinnacles), by rarity:", JSON.stringify(bySize), "four commons:", four);
console.log("pinnacles that score alone:", Object.values(C).filter((d) => d && d.rarity === "S" && d.aff && scores([d.id])).map((d) => d.name).join(", "));
