// Checks of the rules engine with the fourth-pass cards (data/cards.json, Nov 8), on hand-built tables.
// The third pass keeps its own checks against a saved copy: scripts/test-rules3.mjs. Run: node scripts/test-rules4.mjs
import { readFileSync } from "node:fs";
import assert from "node:assert/strict";
import * as R from "../js/game/rules.js";

R.loadCards(JSON.parse(readFileSync(new URL("../data/cards.json", import.meta.url), "utf8")));
const ID = {};
for (const c of Object.values(R.C)) { ID[c.name] = c.id; if (c.fname) ID[c.fname] = c.id; }
const id = (name) => { assert.ok(ID[name], "no card " + name); return ID[name]; };
const ONE_ROUND = { bestOf: 1, noCap: true };
function table(b0, b1, opts) { const s = R.newContest(b0.map(id), b1.map(id), 0, ["A", "B"], opts || ONE_ROUND); R.advance(s); return s; }
const findPerm = (s, name) => R.perms(s).find((i) => R.C[i.card].name === name);
function put(s, P, name, nextTo, cell) {
  const m = { id: id(name), face: "perm", w: "new", cell: 0 };
  if (nextTo) { const i = findPerm(s, nextTo); m.w = i.w; m.cell = cell; }
  if (!s.p[P].binder.includes(m.id)) s.p[P].binder.push(m.id);
  R.applyMove(s, P, m);
  return findPerm(s, name);
}
const forceTargets = (s, P, force) => R.movesFor(s, P, false).filter((m) => m.face === "force" && m.id === id(force));
const targetNames = (s, ms) => ms.map((m) => R.C[s.inst[m.t].card].name).sort();

let n = 0;
const test = (name, fn) => { fn(); n++; console.log("ok -", name); };

test("the engine reads every fourth-pass permanence text", () => {
  assert.deepEqual(R.C.__unknown, []);
});
test("Spring scores a point per four water affinities; Mountain Range per four earth", () => {
  const s = table([], []);
  put(s, 0, "Spring"); put(s, 0, "Lagoon"); // water: Spring 1 + Lagoon 3 = 4
  assert.equal(R.score(s)[0].mtn, 1);
  put(s, 1, "Mountain Range"); put(s, 1, "Moor"); // earth: 1 + 3 = 4
  assert.equal(R.score(s)[1].mtn, 1);
});
test("Sky Isle scores air, and an any ring counts toward it (reading)", () => {
  const s = table([], []);
  put(s, 0, "Sky Isle"); put(s, 0, "Twin Peaks"); // air 1 + any 1 + air 2 = 4
  assert.equal(R.score(s)[0].mtn, 1);
});
test("the blanking cycle: Badlands blanks water, Thicket air, Wind Gap earth, for both players", () => {
  const s = table([], []);
  const w = put(s, 1, "Deep Lake"); put(s, 0, "Badlands");
  assert.deepEqual(R.view(s).tok[w.id], []);
  const t = table([], []);
  const a = put(t, 1, "Twin Peaks"), e = put(t, 0, "Plateau"); put(t, 0, "Thicket");
  assert.deepEqual(R.view(t).tok[a.id], []);
  assert.notDeepEqual(R.view(t).tok[e.id], []);
  put(t, 1, "Wind Gap");
  assert.deepEqual(R.view(t).tok[e.id], []);
});
test("Grove, when played, removes a common force", () => {
  const s = table(["Grove"], ["Ashfield"]);
  const h = put(s, 0, "Bedrock");
  s.turn = 1; R.applyMove(s, 1, forceTargets(s, 1, "Brushfire").find((m) => m.t === h.id));
  assert.deepEqual(R.view(s).tok[h.id], [R.BIT.fire]);
  s.turn = 0;
  const ms = R.movesFor(s, 0, false).filter((m) => m.face === "perm" && m.id === id("Grove") && m.f);
  assert.ok(ms.length > 0);
  R.applyMove(s, 0, ms[0]);
  assert.deepEqual(R.view(s).tok[h.id], [R.BIT.earth]);
});
test("Lava Field can't be moved", () => {
  const s = table(["Bluff"], []);
  put(s, 0, "Lava Field"); put(s, 0, "Ashfield");
  const ms = R.movesFor(s, 0, false).filter((m) => m.face === "perm" && m.id === id("Bluff") && m.t);
  assert.ok(ms.length > 0);
  assert.ok(!ms.some((m) => R.C[s.inst[m.t].card].name === "Lava Field"));
});
test("Tide Pool ignores fire forces (it ignored air in the third pass)", () => {
  const s = table(["Lava Coast"], []);
  put(s, 1, "Tide Pool"); put(s, 1, "Deep Lake", "Tide Pool", 1);
  assert.equal(forceTargets(s, 0, "Steam Explosion").length, 0);
});
test("Ice Storm: water permanences can't be removed (Nov 8)", () => {
  const s = table(["Peak", "Deep Lake"], []);
  put(s, 1, "Tide Pool");
  assert.equal(forceTargets(s, 0, "Drought").length, 1);
  R.applyMove(s, 0, forceTargets(s, 0, "Ice Storm")[0]);
  assert.equal(forceTargets(s, 0, "Drought").length, 0);
});
test("Flash Flood (now Lagoon's, a water force) removes a world's fire permanences; Ashfield ignores it", () => {
  const s = table(["Lagoon"], []);
  put(s, 1, "Lava Field"); put(s, 1, "Bedrock", "Lava Field", 1); put(s, 1, "Ashfield", "Lava Field", 2);
  R.applyMove(s, 0, forceTargets(s, 0, "Flash Flood")[0]);
  assert.ok(!findPerm(s, "Lava Field")); assert.ok(findPerm(s, "Bedrock")); assert.ok(findPerm(s, "Ashfield"));
});
test("Tsunami (now Ocean's) turns a world's permanences to water", () => {
  const s = table(["Ocean"], []);
  const v = put(s, 1, "Volcano"); const b = put(s, 1, "Bedrock", "Volcano", 1);
  R.applyMove(s, 0, forceTargets(s, 0, "Tsunami").find((m) => m.w === v.w));
  assert.deepEqual(R.view(s).tok[v.id], [R.BIT.water]);
  assert.deepEqual(R.view(s).tok[b.id], [R.BIT.water]);
});
test("a card with no force (Lava Plain) can only be played as a permanence", () => {
  const s = table(["Lava Plain"], []);
  const ms = R.legalMoves(s, 0);
  assert.ok(ms.length > 0);
  assert.ok(ms.every((m) => m.face === "perm"));
});
test("Equinox is a meta card: return 3 cards from your void", () => {
  const s = R.newContest([id("Equinox")], [id("Bedrock")], 0, ["A", "B"], ONE_ROUND);
  for (const nm of ["Glacier", "Bedrock", "Spire", "Ashfield", "Summit"]) s.p[0].void.push(id(nm));
  R.advance(s);
  const m = R.legalMoves(s, 0).find((x) => x.face === "meta");
  assert.ok(m);
  R.applyMove(s, 0, m);
  assert.equal(s.p[0].binder.length, 3);
  assert.equal(s.p[0].void.length, 3); // two left, plus Equinox itself
});
test("Hidden Valley's two any rings fill a set with two one-element cards", () => {
  const s = table([], []);
  put(s, 0, "Hidden Valley"); put(s, 0, "Glacier", "Hidden Valley", 1); put(s, 0, "Bedrock", "Hidden Valley", 2);
  assert.equal(R.score(s)[0].pts, 1);
});
test("Dune: +1 fire once its player has a world point (the opponent's points don't count)", () => {
  const s = table([], []);
  const d = put(s, 0, "Dune");
  assert.deepEqual(R.view(s).tok[d.id], [R.BIT.fire]);
  put(s, 1, "Hidden Valley"); put(s, 1, "Glacier", "Hidden Valley", 1); put(s, 1, "Bedrock", "Hidden Valley", 2);
  assert.equal(R.score(s)[1].pts, 1);
  assert.deepEqual(R.view(s).tok[d.id], [R.BIT.fire]);
  put(s, 0, "Wilderness"); put(s, 0, "Tide Pool", "Wilderness", 1); put(s, 0, "Stone Field", "Wilderness", 2);
  put(s, 0, "Summit", "Wilderness", 3);
  assert.deepEqual(R.view(s).tok[d.id], [R.BIT.fire, R.BIT.fire]);
  assert.equal(R.score(s)[0].tot[0], 3); // fire: Dune two, Wilderness one
});
test("Ledge hit by Updraft shows fire, and its +1 air still comes after (reading)", () => {
  const s = table([], ["Dune"]);
  const l = put(s, 0, "Ledge");
  put(s, 0, "Wilderness"); put(s, 0, "Tide Pool", "Wilderness", 1); put(s, 0, "Stone Field", "Wilderness", 2); put(s, 0, "Summit", "Wilderness", 3);
  assert.deepEqual(R.view(s).tok[l.id], [R.BIT.air, R.BIT.air]);
  s.turn = 1; R.applyMove(s, 1, forceTargets(s, 1, "Updraft").find((m) => m.t === l.id));
  assert.deepEqual(R.view(s).tok[l.id], [R.BIT.fire, R.BIT.air]);
});
test("Hanging Valley, under the scoring before Nov 10: +1 world point for a world with one of each element (reading)", () => {
  const s = table([], [], { ...ONE_ROUND, scoring: "sets" });
  const h = put(s, 0, "Hanging Valley");
  assert.equal(R.score(s)[0].pts, 0);
  put(s, 0, "Hidden Valley", "Hanging Valley", 1); put(s, 0, "Glacier", "Hanging Valley", 2);
  assert.equal(R.score(s)[0].pts, 0); // any, any, water: no fire-earth-air set yet
  put(s, 0, "Bedrock", "Hanging Valley", 3);
  const sc = R.score(s)[0];
  assert.equal(sc.pts, 2);
  assert.equal(sc.worlds.find((w) => w.id === h.w).k, 2);
});
test("Nov 10: four of one element in a world is a world point (Lagoon's three water and Glacier)", () => {
  const s = table([], []);
  put(s, 0, "Lagoon"); assert.equal(R.score(s)[0].pts, 0);
  put(s, 0, "Glacier", "Lagoon", 1); assert.equal(R.score(s)[0].pts, 1);
});
test("Nov 10: a world scores one point at most (Origin and Ocean), and Hanging Valley adds nothing (reading)", () => {
  const s = table([], []);
  put(s, 0, "Origin"); put(s, 0, "Ocean", "Origin", 1);
  assert.equal(R.score(s)[0].pts, 1);
  put(s, 0, "Hanging Valley", "Origin", 2);
  assert.equal(R.score(s)[0].pts, 1);
  assert.equal(s.decisive, null); // no Perfect World
});
test("Nov 10: either-or and any pips count toward four of one element (reading)", () => {
  const s = table([], []);
  put(s, 0, "Hidden Valley"); put(s, 0, "Glacier", "Hidden Valley", 1); // any, any, water: three
  assert.equal(R.score(s)[0].pts, 0);
  put(s, 0, "Tide Pool", "Hidden Valley", 2); // four water
  assert.equal(R.score(s)[0].pts, 1);
});
test("one round: the contest ends when the round does, and there's no card cap", () => {
  const s = table(["Bedrock", "Glacier"], ["Spire"]);
  assert.ok(s.cap > 100);
  R.pass(s, 0); R.pass(s, 1);
  assert.equal(s.phase, "contestOver");
});
console.log(`${n} rule checks passed`);
