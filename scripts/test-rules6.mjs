// Checks of the rules engine with the sixth-pass cards (data/cards.json, Nov 11), on hand-built tables.
// The older passes keep their own checks against saved copies: test-rules3/4/5.mjs. Run: node scripts/test-rules6.mjs
import { readFileSync } from "node:fs";
import assert from "node:assert/strict";
import * as R from "../js/game/rules.js";

const DATA = JSON.parse(readFileSync(new URL("../data/cards.json", import.meta.url), "utf8"));
R.loadCards(DATA);
const ID = {};
for (const c of Object.values(R.C)) { ID[c.name] = c.id; if (c.fname) ID[c.fname] = c.id; }
const id = (name) => { assert.ok(ID[name], "no card " + name); return ID[name]; };
const BO3 = { bestOf: 3, noCap: true };
function table(b0, b1) { const s = R.newContest(b0.map(id), b1.map(id), 0, ["A", "B"], BO3); R.advance(s); return s; }
const findPerm = (s, name) => R.perms(s).find((i) => R.C[i.card].name === name);
function put(s, P, name, nextTo, cell) {
  const m = { id: id(name), face: "perm", w: "new", cell: 0 };
  if (nextTo) { const i = findPerm(s, nextTo); m.w = i.w; m.cell = cell; }
  if (!s.p[P].binder.includes(m.id)) s.p[P].binder.push(m.id);
  R.applyMove(s, P, m);
  return findPerm(s, name);
}
const forceTargets = (s, P, force) => R.movesFor(s, P, false).filter((m) => m.face === "force" && m.id === id(force));
const names = (s, ids) => ids.map((x) => R.C[s.inst[x].card].name).sort();
const { water: Wt, earth: Et, fire: Ft, air: At } = R.BIT;

let n = 0;
const test = (name, fn) => { fn(); n++; console.log("ok -", name); };

test("the engine reads every sixth-pass permanence text", () => assert.deepEqual(R.C.__unknown, []));
test("no card loses its affinities any more (Cam, Nov 11)", () => {
  for (const c of DATA.cards) {
    assert.ok(!/lose(s)? (its|their) affinities/.test((c.permanence && c.permanence.text) || ""), c.name);
    assert.ok(!/lose(s)? (its|their) affinities/.test((c.force && c.force.text) || ""), c.name);
  }
});
test("every force and meta card is implemented", () => {
  const s = table([], []);
  put(s, 0, "Ice Floe"); put(s, 0, "Delta", "Ice Floe", 1); put(s, 0, "Lagoon", "Ice Floe", 2); put(s, 0, "Hill");
  put(s, 1, "Volcano"); put(s, 1, "Dune", "Volcano", 1); put(s, 1, "Caldera Lake"); put(s, 1, "Ledge");
  for (const nm of ["Glacier", "Hot Spring", "Echo"]) s.p[0].void.push(id(nm));
  for (const nm of ["Marsh", "Moor"]) s.p[1].void.push(id(nm));
  s.p[0].lastRound = [id("Glacier"), id("Hot Spring")];
  for (const d of Object.values(R.C)) if (d.id) for (const P of [0, 1]) { const s2 = R.clone(s); s2.p[P].binder = [d.id]; R.movesFor(s2, P, false); }
});
test("removal reaches only its own rarity: Ash (common), Scald (uncommon), Collapse (rare)", () => {
  const s = table(["Lava Field", "Hot Spring", "Caldera Lake"], []);
  put(s, 1, "Ice Floe"); put(s, 1, "Volcano"); put(s, 1, "Lagoon"); put(s, 1, "Hill");
  assert.deepEqual(names(s, forceTargets(s, 0, "Ash").map((m) => m.t)), ["Hill", "Ice Floe"]);
  assert.deepEqual(names(s, forceTargets(s, 0, "Scald").map((m) => m.t)), ["Volcano"]);
  assert.deepEqual(names(s, forceTargets(s, 0, "Collapse").map((m) => m.t)), ["Lagoon"]);
});
test("moving the other player's cards is gated too: Crosswind swaps two commons of one player; Gust, Landslide, Downdraft by rarity", () => {
  const s = table(["Summit", "Ledge", "Hidden Valley", "Wind Gap"], []);
  put(s, 1, "Ice Floe"); put(s, 1, "Volcano", "Ice Floe", 1); put(s, 1, "Hill"); put(s, 1, "Lagoon", "Hill", 1);
  const cw = forceTargets(s, 0, "Crosswind");
  assert.equal(cw.length, 1); assert.deepEqual(names(s, [cw[0].t, cw[0].t2]), ["Hill", "Ice Floe"]);
  assert.deepEqual(names(s, forceTargets(s, 0, "Gust").map((m) => m.t)), ["Hill", "Ice Floe"]);
  assert.deepEqual(names(s, forceTargets(s, 0, "Landslide").map((m) => m.t)), ["Volcano"]);
  assert.deepEqual(names(s, forceTargets(s, 0, "Downdraft").map((m) => m.t)), ["Lagoon"]);
});
test("Tangle: no common forces for the other player until your next turn; uncommon forces still play", () => {
  const s = table(["Bedrock", "Ice Floe"], ["Lava Field", "Hot Spring", "Hill"]);
  put(s, 0, "Dune"); put(s, 0, "Volcano");
  R.play(s, 0, R.legalMoves(s, 0).find((m) => m.id === id("Bedrock") && m.face === "force"));
  const ms = R.legalMoves(s, 1);
  assert.ok(!ms.some((m) => m.id === id("Lava Field") && m.face === "force"));
  assert.ok(ms.some((m) => m.id === id("Hot Spring") && m.face === "force"));
  assert.ok(ms.some((m) => m.id === id("Lava Field") && m.face === "perm"));
  R.play(s, 1, ms.find((m) => m.id === id("Hill")));
  assert.equal(R.forces(s).length, 0); // gone at the start of A's next turn
});
test("Thaw removes a common force only; while \"No common forces\" is up, Thaw can't be played either", () => {
  const s = table(["Glacier"], ["Ashfield", "Cloud Forest", "Stone Field"]);
  put(s, 1, "Hill");
  s.turn = 1; R.applyMove(s, 1, forceTargets(s, 1, "Brushfire")[0]); R.applyMove(s, 1, forceTargets(s, 1, "Fog")[0]); s.turn = 0;
  assert.equal(R.forces(s).length, 2);
  const th = forceTargets(s, 0, "Thaw");
  assert.equal(th.length, 1); assert.equal(R.C[s.inst[th[0].f].card].name, "Ashfield");
  s.turn = 1; R.applyMove(s, 1, forceTargets(s, 1, "Dust")[0]); s.turn = 0;
  assert.equal(forceTargets(s, 0, "Thaw").length, 0);
});
test("forces that help their owner touch only their owner's cards", () => {
  const s = table(["Bluff", "Shoal", "Steam Vent", "Ashfield", "Delta", "Mangrove"], []);
  put(s, 0, "Ice Floe"); put(s, 0, "Hill", "Ice Floe", 1);
  put(s, 1, "Dune"); put(s, 1, "Ledge", "Dune", 1);
  const mine = new Set(R.perms(s).filter((i) => i.owner === 0).map((i) => i.id));
  for (const f of ["Eddy", "Mist", "Vent", "Brushfire", "Flood"]) for (const m of forceTargets(s, 0, f)) for (const t of [m.t, m.t2].filter(Boolean)) assert.ok(mine.has(t), f);
  for (const m of forceTargets(s, 0, "Undertow")) assert.equal(s.worlds[m.w].owner, 0);
});
test("Whirlwind splits your own world, and a split can turn one world point into two", () => {
  const s = table(["Spire"], []);
  put(s, 0, "Delta"); put(s, 0, "Hot Spring", "Delta", 1); put(s, 0, "Desert", "Delta", 2); put(s, 0, "Sea Cliff", "Delta", 3);
  // left column water+earth over fire+air, right column water+fire over earth+air: one of each twice over, one point
  assert.equal(R.score(s)[0].pts, 1);
  R.applyMove(s, 0, forceTargets(s, 0, "Whirlwind")[0]);
  assert.equal(R.worldsOf(s, 0).length, 2);
  assert.equal(R.score(s)[0].pts, 2);
});
test("the void forces: Drizzle returns a card from your void; Freeze plays a permanence from it; Surge returns up to three", () => {
  const s = table(["Tide Pool", "Snowfield", "Archipelago"], []);
  s.p[0].void.push(id("Hill"), id("Echo"));
  const dz = forceTargets(s, 0, "Drizzle");
  assert.deepEqual(dz.map((m) => R.C[m.cards[0]].name).sort(), ["Echo", "Hill"]);
  const fr = forceTargets(s, 0, "Freeze");
  assert.ok(fr.length && fr.every((m) => m.sub.face === "perm" && m.sub.id === id("Hill")));
  R.applyMove(s, 0, fr[0]);
  assert.ok(findPerm(s, "Hill") && !s.p[0].void.includes(id("Hill")) && s.p[0].void.includes(id("Snowfield")));
  const su = forceTargets(s, 0, "Surge");
  assert.equal(su.length, 1); assert.equal(su[0].cards.length, 2); // Echo and Snowfield
});
test("Overgrowth: play another earth card, and only an earth card", () => {
  const s = table(["Grove", "Hill", "Dune", "Volcano"], ["Spire"]);
  R.play(s, 0, R.legalMoves(s, 0).find((m) => m.id === id("Grove") && m.face === "force"));
  assert.equal(s.turn, 0);
  const ms = R.legalMoves(s, 0);
  assert.deepEqual([...new Set(ms.map((m) => R.C[m.id].name))].sort(), ["Hill", "Volcano"]);
});
test("Meteor: two more fire cards; Ember: two more of any card", () => {
  const s = table(["Crater", "Dune", "Lava Lake", "Hill"], ["Spire"]);
  R.play(s, 0, R.legalMoves(s, 0).find((m) => m.id === id("Crater") && m.face === "force"));
  assert.deepEqual(s.extras, ["fire", "fire"]);
  R.play(s, 0, R.legalMoves(s, 0).find((m) => m.id === id("Dune") && m.face === "perm"));
  assert.equal(s.turn, 0);
  const t = table(["Badlands", "Hill", "Ice Floe", "Ledge"], ["Spire"]);
  R.play(t, 0, R.legalMoves(t, 0).find((m) => m.id === id("Badlands") && m.face === "force"));
  R.play(t, 0, R.legalMoves(t, 0).find((m) => m.id === id("Hill")));
  R.play(t, 0, R.legalMoves(t, 0).find((m) => m.id === id("Ice Floe")));
  assert.equal(t.turn, 1);
});
test("Ice Sheet: each permanence in its world gains water, itself included", () => {
  const s = table([], []);
  const is = put(s, 0, "Ice Sheet"); const h = put(s, 0, "Hill", "Ice Sheet", 1);
  assert.deepEqual(R.view(s).tok[is.id], [Wt, Wt]);
  assert.deepEqual(R.view(s).tok[h.id], [Et, Wt]);
  assert.equal(R.score(s)[0].pts, 0);
  put(s, 0, "Dune", "Ice Sheet", 2); // water 2 + 1 + 1 = four water
  assert.equal(R.score(s)[0].pts, 1);
});
test("Erosion returns two of your worlds; Typhoon moves two of your permanences", () => {
  const s = table(["Red Canyon", "Geyser Basin"], []);
  put(s, 0, "Ice Floe"); put(s, 0, "Hill"); put(s, 0, "Dune", "Hill", 1); put(s, 1, "Ledge");
  const er = forceTargets(s, 0, "Erosion");
  assert.equal(er.length, 1);
  const ty = forceTargets(s, 0, "Typhoon");
  assert.ok(ty.length > 0 && ty.every((m) => s.inst[m.t].owner === 0 && s.inst[m.t2].owner === 0));
  R.applyMove(s, 0, er[0]);
  assert.equal(R.worldsOf(s, 0).length, 0); assert.equal(s.p[0].binder.length, 4); // the three permanences and Geyser Basin
});
console.log(`${n} rule checks passed`);
