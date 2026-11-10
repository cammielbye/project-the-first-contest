// Every 2x2 world of four permanences (fourth pass) that scores 3 or more world points, by the engine (Nov 9, for Cam).
// Usage: node scripts/three-point-worlds.mjs <out.json>. A 2x2 holds four cards; Mirage rows try all three arrangements.
import { readFileSync, writeFileSync } from "node:fs";
const ROOT = new URL("..", import.meta.url).pathname;
const R = await import(ROOT + "/js/game/rules.js");
const data = JSON.parse(readFileSync(ROOT + "/data/cards.json", "utf8"));
R.loadCards(data);
const perms = data.cards.filter((c) => !c.meta).map((c) => ({ id: c.no, name: c.permanence.name, aff: c.permanence.affinities, text: c.permanence.text || "" }));
const EL = ["water", "earth", "fire", "air"];
// upper bound on tokens per element for the prefilter (either-or and any count toward every element they can show)
for (const p of perms) {
  p.ub = [0, 0, 0, 0]; p.n = p.aff.length;
  for (const a of p.aff) EL.forEach((e, k) => { if (a === "any" || a.split("|").includes(e)) p.ub[k]++; });
  if (/^Copies every adjacent/.test(p.text)) { p.mirage = true; p.n = 8; p.ub = [8, 8, 8, 8]; }
  if (/^\+1 (\w+) if you have a world point/.test(p.text)) { const e = p.text.match(/^\+1 (\w+)/)[1]; p.n += 1; p.ub[EL.indexOf(e)]++; }
  if (/^\+1 world point if this world has/.test(p.text)) p.hv = true;
}
const N = perms.length;
const ARR = [[0, 1, 2, 3], [0, 1, 3, 2], [0, 3, 1, 2]]; // card order into cells 0 1 / 2 3; the three ways up to symmetry
const ONE = { bestOf: 1, noCap: true, scoring: "sets" }; // the scoring before Nov 10, when a world could be worth 3
function scoreArr(cs) {
  const s = R.newContest(cs.map((c) => c.id), [], 0, ["A", "B"], ONE); R.advance(s);
  // place into cells 0,1,2,3 in an order that keeps each placement touching a placed card: 0,1,3,2 works for any fill
  const order = [0, 1, 3, 2];
  let w = null;
  for (const cell of order) {
    const c = cs[cell];
    const m = { id: c.id, face: "perm", w: w === null ? "new" : w, cell: w === null ? 0 : cell };
    R.applyMove(s, 0, m);
    if (w === null) w = R.perms(s).find((i) => i.card === c.id).w;
    s.turn = 0;
  }
  const sc = R.score(s)[0];
  return { k: Math.max(...sc.worlds.map((x) => x.k)), worlds: sc.worlds.length };
}
const out = [];
let checked = 0;
for (let a = 0; a < N; a++) for (let b = a + 1; b < N; b++) for (let c = b + 1; c < N; c++) for (let d = c + 1; d < N; d++) {
  const cs = [perms[a], perms[b], perms[c], perms[d]];
  const hv = cs.filter((x) => x.hv).length;
  const need = 3 - hv; // sets needed
  if (need <= 0) continue;
  let tot = 0; const ub = [0, 0, 0, 0];
  for (const x of cs) { tot += x.n; for (let k = 0; k < 4; k++) ub[k] += x.ub[k]; }
  if (tot < 4 * need || ub.some((u) => u < need)) continue;
  checked++;
  const hasMirage = cs.some((x) => x.mirage);
  const arrs = hasMirage ? ARR : [ARR[0]];
  const ok = [];
  for (const arr of arrs) {
    const placed = arr.map((i) => cs[i]);
    const r = scoreArr(placed);
    if (r.worlds === 1 && r.k >= 3) ok.push({ cells: placed.map((x) => x.name), k: r.k });
  }
  if (ok.length) out.push({ cards: cs.map((x) => x.name), k: Math.max(...ok.map((o) => o.k)), arrangements: hasMirage ? ok.map((o) => o.cells) : null });
}
writeFileSync(process.argv[2], JSON.stringify(out, null, 1));
console.log("checked", checked, "found", out.length);
