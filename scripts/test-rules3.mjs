// Checks of the rules engine on hand-built tables, with the third-pass cards (a saved copy: scripts/fixtures/cards-third-pass.json,
// synced from data/versions/card-pool-2026-11-08-third-pass.md), so the engine keeps playing the old pass the same way.
// The fourth pass has its own checks: scripts/test-rules4.mjs. Run: node scripts/test-rules3.mjs
import { readFileSync } from "node:fs";
import assert from "node:assert/strict";
import * as R from "../js/game/rules.js";

R.loadCards(JSON.parse(readFileSync(new URL("./fixtures/cards-third-pass.json", import.meta.url), "utf8")));
const ID = {};
for (const c of Object.values(R.C)) { ID[c.name] = c.id; if (c.fname) ID[c.fname] = c.id; }
const id = (name) => { assert.ok(ID[name], "no card " + name); return ID[name]; };

// a contest where both binders hold the named cards, P0 to play
// the third pass was played under the scoring before Nov 10 (a point per set, Perfect World at 3)
const SETS = { scoring: "sets" };
function table(b0, b1) { const s = R.newContest(b0.map(id), b1.map(id), 0, ["You", "Computer"], SETS); R.advance(s); return s; }
const findPerm = (s, name) => R.perms(s).find((i) => R.C[i.card].name === name);
// put a permanence down for P (bypassing turns); into a new world, or next to another card
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

test("Brushfire overwrites an earth permanence of any size to a single fire for the round", () => {
  const s = table(["Ashfield"], ["Hill", "Red Canyon"]);
  put(s, 1, "Hill"); const v = put(s, 1, "Red Canyon");
  assert.equal(R.C[v.card].aff.length, 3);
  assert.deepEqual(targetNames(s, forceTargets(s, 0, "Brushfire")), ["Hill", "Red Canyon"]);
  R.applyMove(s, 0, forceTargets(s, 0, "Brushfire").find((m) => m.t === v.id));
  assert.deepEqual(R.view(s).tok[v.id], [R.BIT.fire]);
  assert.ok(findPerm(s, "Red Canyon"), "it stays on the table");
});
test("Flare-up removes a common force, not an uncommon one", () => {
  const s = table(["Fumarole", "Ashfield", "Cloud Forest"], []);
  const h = put(s, 1, "Hill"); put(s, 1, "Grove");
  R.applyMove(s, 0, forceTargets(s, 0, "Brushfire").find((m) => m.t === h.id));
  R.applyMove(s, 0, forceTargets(s, 0, "Fog")[0]);
  const ms = forceTargets(s, 0, "Flare-up");
  assert.deepEqual(ms.map((m) => R.C[s.inst[m.f].card].fname), ["Brushfire"]);
  R.applyMove(s, 0, ms[0]);
  assert.deepEqual(R.view(s).tok[h.id], [R.BIT.earth]);
});
test("Equinox returns three cards from your void", () => {
  const s = R.newContest([id("Cradle")], [id("Ridge")], 0, ["You", "Computer"], SETS);
  for (const n of ["Hill", "Grove", "Ledge", "Lagoon", "Dune"]) s.p[0].void.push(id(n));
  R.advance(s);
  const m = R.legalMoves(s, 0).find((x) => x.face === "force");
  R.applyMove(s, 0, m);
  assert.equal(s.p[0].binder.length, 3);
  assert.equal(s.p[0].void.length, 3); // two left, plus Cradle itself
});
test("Option A: uncommon removal reaches two elements, still one affinity", () => {
  const s = table(["Hot Spring"], []);
  put(s, 1, "Hill"); put(s, 1, "Volcano"); put(s, 1, "Cinder Field");
  assert.deepEqual(targetNames(s, forceTargets(s, 0, "Scald")), ["Cinder Field", "Hill"]);
});
test("a world worth 3 world points wins the contest at once", () => {
  const s = table(["Rainforest"], []);
  put(s, 0, "Caldera Lake"); put(s, 0, "Geyser Basin", "Caldera Lake", 1); put(s, 0, "Red Canyon", "Caldera Lake", 2);
  const m = R.legalMoves(s, 0).find((x) => x.face === "perm" && x.w === findPerm(s, "Caldera Lake").w && x.cell === 3);
  R.play(s, 0, m);
  assert.equal(s.phase, "contestOver");
  assert.equal(s.winner, 0);
  assert.equal(s.why, "3-point world");
});
test("ignores water forces: Shower can't reach Ashfield", () => {
  const s = table(["Lagoon"], []);
  put(s, 1, "Ashfield"); put(s, 1, "Cinder Field");
  assert.deepEqual(targetNames(s, forceTargets(s, 0, "Shower")), ["Cinder Field"]);
});
test("Heat Dome: fire permanences can't be removed", () => {
  const s = table(["Hot Spring", "Lava Lake"], []);
  put(s, 1, "Cinder Field");
  assert.equal(forceTargets(s, 0, "Scald").length, 1);
  R.applyMove(s, 0, forceTargets(s, 0, "Heat Dome")[0]);
  assert.equal(forceTargets(s, 0, "Scald").length, 0);
});
test("Thicket: your adjacent permanences can't be moved", () => {
  const s = table(["Eyrie"], []);
  put(s, 0, "Thicket"); put(s, 0, "Hill", "Thicket", 1); put(s, 0, "Grove");
  assert.ok(!forceTargets(s, 0, "Drift").some((m) => R.C[s.inst[m.t].card].name === "Hill"));
  assert.ok(forceTargets(s, 0, "Drift").some((m) => R.C[s.inst[m.t].card].name === "Grove"));
});
test("Lava Field turns adjacent earth to fire; Mirage copies its neighbours", () => {
  const s = table([], []);
  put(s, 0, "Lava Field"); const hill = put(s, 0, "Hill", "Lava Field", 1);
  assert.deepEqual(R.view(s).tok[hill.id], [R.BIT.fire]);
  const mi = put(s, 0, "Mirage", "Lava Field", 2);
  assert.deepEqual(R.view(s).tok[mi.id], [R.BIT.fire]);
});
test("every 'becomes' overwrites to one affinity: Lava Field's neighbour, Firestorm's world", () => {
  const s = table([], []);
  put(s, 0, "Lava Field"); const rc = put(s, 0, "Red Canyon", "Lava Field", 1);
  assert.deepEqual(R.view(s).tok[rc.id], [R.BIT.fire]);
  const t = table(["Red Canyon"], []);
  const v = put(t, 1, "Volcano"); const hill = put(t, 1, "Hill", "Volcano", 1);
  R.applyMove(t, 0, forceTargets(t, 0, "Firestorm").find((m) => m.w === v.w));
  assert.deepEqual(R.view(t).tok[v.id], [R.BIT.fire]);
  assert.deepEqual(R.view(t).tok[hill.id], [R.BIT.fire]);
});
test("Badlands loses its affinities next to water", () => {
  const s = table([], []);
  const b = put(s, 0, "Badlands"); put(s, 0, "Lagoon", "Badlands", 1);
  assert.deepEqual(R.view(s).tok[b.id], []);
});
test("Archipelago wins the round at the start of its owner's turn with 10 water (Nov 7)", () => {
  const s = table(["Hill", "Ridge"], ["Hill"]);
  put(s, 0, "Archipelago"); put(s, 0, "Ocean"); put(s, 0, "Misty Fjord"); put(s, 0, "Deep Lake");
  R.play(s, 0, R.legalMoves(s, 0).find((m) => m.face === "perm")); // not yet: P1 gets a turn
  assert.equal(s.rounds.length, 0);
  R.play(s, 1, R.legalMoves(s, 1)[0]); // then P0's turn starts
  assert.equal(s.rounds.length, 1);
  assert.equal(s.rounds[0].why, "Archipelago");
  assert.equal(s.rounds[0].winner, 0);
});
test("Archipelago doesn't win with 8 water", () => {
  const s = table(["Hill", "Ridge"], ["Hill", "Ridge"]);
  put(s, 0, "Archipelago"); put(s, 0, "Ocean"); put(s, 0, "Misty Fjord");
  R.play(s, 0, R.legalMoves(s, 0).find((m) => m.face === "perm"));
  R.play(s, 1, R.legalMoves(s, 1).find((m) => m.face === "perm"));
  assert.equal(s.rounds.length, 0);
});
test("Open worlds (simulator switch) grow past four cards; a one-card world offers one cell", () => {
  const names = ["Hill", "Ridge", "Ledge", "Flint", "Bedrock", "Lagoon"];
  const s = R.newContest(names.map(id), ["Hill"].map(id), 0, ["A", "B"], { openWorlds: true, scoring: "sets" }); R.advance(s);
  R.applyMove(s, 0, { id: id("Hill"), face: "perm", w: "new", cell: 0 });
  const w = Object.values(s.worlds)[0];
  assert.equal(R.movesFor(s, 0, false).filter((m) => m.face === "perm" && m.id === id("Ridge") && m.w === w.id).length, 1);
  for (const nm of names.slice(1)) R.applyMove(s, 0, R.movesFor(s, 0, false).find((m) => m.face === "perm" && m.id === id(nm) && m.w === w.id));
  assert.equal(R.worldSize(s.worlds[w.id]), 6);
  assert.ok(R.canGrow(s, s.worlds[w.id]));
});
test("The square stays capped at four", () => {
  const names = ["Hill", "Ridge", "Ledge", "Flint", "Bedrock"];
  const s = table(names, ["Hill"]);
  R.applyMove(s, 0, { id: id("Hill"), face: "perm", w: "new", cell: 0 });
  const w = Object.values(s.worlds)[0];
  for (const nm of names.slice(1, 4)) R.applyMove(s, 0, R.movesFor(s, 0, false).find((m) => m.face === "perm" && m.id === id(nm) && m.w === w.id));
  assert.equal(R.worldSize(s.worlds[w.id]), 4);
  assert.equal(R.movesFor(s, 0, false).filter((m) => m.face === "perm" && m.w === w.id).length, 0);
});
test("Calm stops force faces for the round", () => {
  const s = table(["Calm", "Lagoon"], []);
  put(s, 1, "Cinder Field");
  R.play(s, 0, R.legalMoves(s, 0).find((m) => m.face === "meta"));
  assert.equal(R.movesFor(s, 0, false).filter((m) => m.face === "force").length, 0);
});
test("Echo plays a card from the void without counting toward the cap", () => {
  const s = R.newContest([id("Echo")], [id("Ridge")], 0, ["You", "Computer"], SETS);
  s.p[0].void.push(id("Hill"));
  R.advance(s);
  const m = R.legalMoves(s, 0).find((x) => x.face === "meta" && x.sub.id === id("Hill") && x.sub.face === "perm");
  R.applyMove(s, 0, m);
  assert.ok(findPerm(s, "Hill"));
  assert.equal(s.p[0].played, 1);
});
test("Tremor splits a world of two; Canyon's world can't be split", () => {
  const s = table(["Mudflat"], []);
  put(s, 1, "Hill"); put(s, 1, "Grove", "Hill", 1);
  R.applyMove(s, 0, forceTargets(s, 0, "Tremor")[0]);
  assert.equal(R.worldsOf(s, 1).length, 2);
  const t = table(["Mudflat"], []);
  put(t, 1, "Canyon"); put(t, 1, "Grove", "Canyon", 1);
  assert.equal(forceTargets(t, 0, "Tremor").length, 0);
});
test("Verge gives two more plays this turn", () => {
  const s = table(["Verge", "Hill", "Grove", "Ridge"], ["Lagoon"]);
  R.play(s, 0, R.legalMoves(s, 0).find((m) => m.face === "meta"));
  assert.equal(s.turn, 0);
  R.play(s, 0, R.legalMoves(s, 0).find((m) => m.face === "perm"));
  R.play(s, 0, R.legalMoves(s, 0).find((m) => m.face === "perm"));
  assert.equal(s.turn, 1);
});
test("round end: Spring returns to the binder, the rest go to the void", () => {
  const s = table(["Spring", "Hill"], ["Ridge"]);
  R.play(s, 0, R.legalMoves(s, 0).find((m) => m.id === id("Spring") && m.face === "perm"));
  R.pass(s, 1); R.pass(s, 0);
  assert.ok(s.p[0].binder.includes(id("Spring")));
  assert.equal(s.phase, "roundOver");
});
test("Ice Sheet: fire permanences lose their affinities for both players", () => {
  const s = table([], []);
  const c = put(s, 1, "Cinder Field"); put(s, 0, "Ice Sheet");
  assert.deepEqual(R.view(s).tok[c.id], []);
});
console.log(`${n} rule checks passed`);
