// Checks of the rules engine with the fifth-pass cards, on hand-built tables: a saved copy (scripts/fixtures/cards-fifth-pass.json,
// synced from data/versions/card-pool-2026-11-11-fifth-pass-final.md), so the engine keeps playing the fifth pass the same way.
// The newest pass has test-rules6.mjs. Run: node scripts/test-rules5.mjs
import { readFileSync } from "node:fs";
import assert from "node:assert/strict";
import * as R from "../js/game/rules.js";

R.loadCards(JSON.parse(readFileSync(new URL("./fixtures/cards-fifth-pass.json", import.meta.url), "utf8")));
const ID = {};
for (const c of Object.values(R.C)) { ID[c.name] = c.id; if (c.fname) ID[c.fname] = c.id; }
const id = (name) => { assert.ok(ID[name], "no card " + name); return ID[name]; };
const BO3 = { bestOf: 3, noCap: true };
function table(b0, b1, opts) { const s = R.newContest(b0.map(id), b1.map(id), 0, ["A", "B"], opts || BO3); R.advance(s); return s; }
const findPerm = (s, name) => R.perms(s).find((i) => R.C[i.card].name === name);
function put(s, P, name, nextTo, cell) {
  const m = { id: id(name), face: "perm", w: "new", cell: 0 };
  if (nextTo) { const i = findPerm(s, nextTo); m.w = i.w; m.cell = cell; }
  if (!s.p[P].binder.includes(m.id)) s.p[P].binder.push(m.id);
  R.applyMove(s, P, m);
  return findPerm(s, name);
}
const forceTargets = (s, P, force) => R.movesFor(s, P, false).filter((m) => m.face === "force" && m.id === id(force));
const metaMove = (s, P, name) => R.movesFor(s, P, false).find((m) => m.face === "meta" && m.id === id(name));
const names = (s, ids) => ids.map((x) => R.C[s.inst[x].card].name).sort();
const { water: Wt, earth: Et, fire: Ft, air: At } = R.BIT;

let n = 0;
const test = (name, fn) => { fn(); n++; console.log("ok -", name); };

test("the engine reads every fifth-pass permanence text", () => assert.deepEqual(R.C.__unknown, []));
test("every permanence has a force, and every force and meta card is implemented", () => {
  const cards = Object.values(R.C);
  assert.ok(cards.filter((d) => !d.meta).every((d) => d.fname), "a permanence with no force");
  // a busy table: both players have worlds of several sizes, a lasting force each, cards in both voids, a round behind them
  const s = table([], [], BO3);
  put(s, 0, "Origin"); put(s, 0, "Ocean", "Origin", 1); put(s, 0, "Glacier", "Origin", 2); put(s, 0, "Spire");
  put(s, 1, "Volcano"); put(s, 1, "Desert", "Volcano", 1); put(s, 1, "Lava Field"); put(s, 1, "Plateau");
  R.applyMove(s, 0, Object.assign({ id: id("Bedrock"), face: "force" }, { w: findPerm(s, "Volcano").w })); // Tangle
  for (const nm of ["Bluff", "Summit", "Echo"]) s.p[0].void.push(id(nm));
  for (const nm of ["Marsh", "Lagoon"]) s.p[1].void.push(id(nm));
  s.p[0].lastRound = [id("Bluff"), id("Summit")];
  for (const d of cards) {
    for (const P of [0, 1]) {
      const s2 = R.clone(s); s2.p[P].binder = [d.id];
      R.movesFor(s2, P, false); // throws "not implemented" for an unknown force or meta card
    }
  }
});
test("forces with a reused effect: Mist is Riptide's, Rockslide Rockfall's (read from the text, Nov 11)", () => {
  assert.equal(R.C[id("Mist")].fkey, R.C[id("Riptide")].fkey);
  assert.equal(R.C[id("Rockslide")].fkey, R.C[id("Rockfall")].fkey);
  const s = table(["Shoal"], []);
  const a = put(s, 1, "Twin Peaks");
  R.applyMove(s, 0, forceTargets(s, 0, "Mist").find((m) => m.t === a.id));
  assert.deepEqual(R.view(s).tok[a.id], [Wt]);
});
test("Ash: an earth permanence of any size loses its affinities (one restriction)", () => {
  const s = table(["Lava Field"], []);
  const p = put(s, 1, "Plateau");
  R.applyMove(s, 0, forceTargets(s, 0, "Ash").find((m) => m.t === p.id));
  assert.deepEqual(R.view(s).tok[p.id], []);
});
test("Scald removes a fire or earth permanence of any size (Nov 11: \"with one affinity\" dropped)", () => {
  const s = table(["Hot Spring"], []);
  put(s, 1, "Lava Lake"); put(s, 1, "Glacier");
  assert.deepEqual(names(s, forceTargets(s, 0, "Scald").map((m) => m.t)), ["Lava Lake"]);
});
test("Gust: a one-pip permanence becomes its own world; Downdraft: a fire permanence of any size", () => {
  const s = table(["Ledge", "Wind Gap"], []);
  put(s, 1, "Volcano"); put(s, 1, "Ice Floe", "Volcano", 1); // (Glacier can't be moved)
  assert.deepEqual(names(s, forceTargets(s, 0, "Gust").map((m) => m.t)), ["Ice Floe"]);
  assert.deepEqual(names(s, forceTargets(s, 0, "Downdraft").map((m) => m.t)), ["Volcano"]);
});
test("Flash Flood removes two fire permanences, and needs two (reading)", () => {
  const s = table(["Lagoon"], []);
  put(s, 1, "Lava Field");
  assert.equal(forceTargets(s, 0, "Flash Flood").length, 0);
  put(s, 1, "Lava Lake"); put(s, 1, "Bedrock", "Lava Lake", 1);
  const ms = forceTargets(s, 0, "Flash Flood");
  assert.equal(ms.length, 1);
  R.applyMove(s, 0, ms[0]);
  assert.ok(!findPerm(s, "Lava Field") && !findPerm(s, "Lava Lake") && findPerm(s, "Bedrock"));
});
test("Lagoon plays only on your first turn of the round", () => {
  const s = table(["Lagoon", "Glacier", "Bedrock"], ["Spire", "Summit"]);
  assert.ok(R.legalMoves(s, 0).some((m) => m.id === id("Lagoon") && m.face === "perm"));
  R.play(s, 0, R.legalMoves(s, 0).find((m) => m.id === id("Glacier")));
  // B's first turn is still to come: the lookahead sees it can play a first-turn card
  R.play(s, 1, R.legalMoves(s, 1).find((m) => m.id === id("Spire")));
  const ms = R.legalMoves(s, 0);
  assert.ok(!ms.some((m) => m.id === id("Lagoon") && m.face === "perm"));
});
test("Caldera Lake plays only on a new world", () => {
  const s = table(["Caldera Lake"], []);
  put(s, 0, "Glacier");
  const ms = R.legalMoves(s, 0).filter((m) => m.id === id("Caldera Lake") && m.face === "perm");
  assert.ok(ms.length > 0 && ms.every((m) => m.w === "new"));
});
test("positional pips: Shoal gives the card below it water; Meadow the card beside; Barrens the card across; Ridge the card above", () => {
  const s = table([], []);
  put(s, 0, "Shoal"); const b = put(s, 0, "Bedrock", "Shoal", 2); const r = put(s, 0, "Ashfield", "Shoal", 1);
  assert.deepEqual(R.view(s).tok[b.id], [Et, Wt]); // below
  assert.deepEqual(R.view(s).tok[r.id], [Ft]); // beside, not below
  const t = table([], []);
  put(t, 0, "Meadow"); const g = put(t, 0, "Glacier", "Meadow", 1); const x = put(t, 0, "Summit", "Meadow", 3);
  assert.deepEqual(R.view(t).tok[g.id], [Wt, Et]); // beside (Cam, Nov 11)
  assert.deepEqual(R.view(t).tok[x.id], [At]); // across gets nothing
  const u = table([], []);
  put(u, 0, "Barrens"); const y = put(u, 0, "Glacier", "Barrens", 1); const z = put(u, 0, "Summit", "Barrens", 3);
  assert.deepEqual(R.view(u).tok[z.id], [At, Ft]); // across: the diagonal (Cam, Nov 11); Summit is unaffected by forces, and this isn't one
  assert.deepEqual(R.view(u).tok[y.id], [Wt]);
  const v = table([], []);
  const top = put(v, 0, "Glacier"); put(v, 0, "Ridge", "Glacier", 2);
  assert.deepEqual(R.view(v).tok[top.id], [Wt, At]);
});
test("a gained pip completes a world: Shoal, Bedrock, Lava Field and Spire with the water below counted once", () => {
  const s = table([], []);
  put(s, 0, "Bedrock"); put(s, 0, "Ashfield", "Bedrock", 1); put(s, 0, "Ridge", "Bedrock", 2); // earth, fire, air; Ridge gives Bedrock air
  assert.equal(R.score(s)[0].pts, 0);
  const t = table([], []);
  put(t, 0, "Shoal"); put(t, 0, "Bedrock", "Shoal", 2); put(t, 0, "Ashfield", "Shoal", 1); // water, earth+water, fire
  put(t, 0, "Summit", "Shoal", 3);
  assert.equal(R.score(t)[0].pts, 1);
});
test("one world point per world counts affinities only: Hanging Valley's +1 and the scoring cycle add to it (Cam, Nov 11)", () => {
  const s = table([], []);
  put(s, 0, "Hanging Valley"); put(s, 0, "Hidden Valley", "Hanging Valley", 1); put(s, 0, "Glacier", "Hanging Valley", 2);
  assert.equal(R.score(s)[0].pts, 0);
  put(s, 0, "Bedrock", "Hanging Valley", 3); // any, any, water, earth: one of each element
  assert.equal(R.score(s)[0].pts, 2);
  const t = table([], []);
  put(t, 0, "Hanging Valley"); put(t, 0, "Deep Lake", "Hanging Valley", 1); put(t, 0, "Glacier", "Hanging Valley", 2); // four of one element, not one of each
  assert.equal(R.score(t)[0].pts, 0);
  put(t, 0, "Ice Floe", "Hanging Valley", 3);
  assert.equal(R.score(t)[0].pts, 1);
  const u = table([], []);
  put(u, 0, "Spring"); put(u, 0, "Lagoon", "Spring", 1); // four water: the world's point, and Spring's point per four water
  assert.equal(R.score(u)[0].pts, 2);
});
test("Sinkhole: a held world loses nothing (no removal, no return, no move, no split)", () => {
  const s = table(["Cavern", "Caldera Lake", "Ice Sheet", "Spire", "Cloud Sea"], []);
  const v = put(s, 1, "Volcano"); put(s, 1, "Ice Floe", "Volcano", 1); put(s, 1, "Hill");
  assert.equal(forceTargets(s, 0, "Whirlwind").length, 1); // Volcano and Ice Floe, before Sinkhole
  R.applyMove(s, 0, forceTargets(s, 0, "Sinkhole").find((m) => m.w === v.w));
  assert.ok(!forceTargets(s, 0, "Collapse").some((m) => m.t === v.id));
  const bz = forceTargets(s, 0, "Blizzard").find((m) => m.w === v.w); // still a world to aim at
  assert.ok(bz); R.applyMove(s, 0, bz);
  assert.ok(findPerm(s, "Volcano") && findPerm(s, "Ice Floe"));
  assert.equal(forceTargets(s, 0, "Whirlwind").length, 0);
  const hu = forceTargets(s, 0, "Hurricane").find((m) => m.P2 === 1); // aimable, but nothing happens
  if (hu) R.applyMove(s, 0, hu);
  assert.equal(findPerm(s, "Volcano").w, findPerm(s, "Ice Floe").w);
});
test("Meteor removes only a permanence played last turn", () => {
  const s = table(["Crater", "Glacier"], ["Bedrock", "Spire"]);
  R.play(s, 0, R.legalMoves(s, 0).find((m) => m.id === id("Glacier")));
  R.play(s, 1, R.legalMoves(s, 1).find((m) => m.id === id("Bedrock")));
  assert.deepEqual(names(s, forceTargets(s, 0, "Meteor").map((m) => m.t)), ["Bedrock"]);
});
test("Cyclone returns a card you played last round from your void; Tornado up to two", () => {
  const s = table(["Glacier", "Bedrock", "Eyrie", "High Desert"], ["Spire"]);
  R.play(s, 0, R.legalMoves(s, 0).find((m) => m.id === id("Glacier")));
  R.pass(s, 1); R.play(s, 0, R.legalMoves(s, 0).find((m) => m.id === id("Bedrock"))); R.pass(s, 0);
  assert.equal(s.phase, "roundOver");
  R.nextRound(s);
  if (s.turn !== 0) R.pass(s, 1);
  const cy = forceTargets(s, 0, "Cyclone");
  assert.deepEqual(cy.map((m) => R.C[m.cards[0]].name).sort(), ["Bedrock", "Glacier"]);
  const to = forceTargets(s, 0, "Tornado");
  assert.equal(to.length, 1); assert.equal(to[0].cards.length, 2);
  R.applyMove(s, 0, to[0]);
  assert.ok(s.p[0].binder.includes(id("Glacier")) && s.p[0].binder.includes(id("Bedrock")));
});
test("Whirlpool plays a card from the other player's void; it goes back to that void at round end, or their binder when returned", () => {
  const s = table(["Fen", "Steam Vent"], ["Spire"]);
  s.p[1].void.push(id("Lava Lake"));
  const m = forceTargets(s, 0, "Whirlpool").find((x) => x.from === 1 && x.sub.id === id("Lava Lake") && x.sub.face === "perm");
  assert.ok(m);
  R.applyMove(s, 0, m);
  const ll = findPerm(s, "Lava Lake");
  assert.equal(ll.owner, 0); assert.equal(ll.home, 1);
  assert.ok(!s.p[1].void.includes(id("Lava Lake")));
  assert.ok(s.p[0].void.includes(id("Fen")));
  R.applyMove(s, 0, forceTargets(s, 0, "Vent").find((x) => x.t === ll.id)); // "Return one of your permanences."
  assert.ok(s.p[1].binder.includes(id("Lava Lake")) && !s.p[0].binder.includes(id("Lava Lake")));
  const t = table(["Fen"], ["Spire"]);
  t.p[1].void.push(id("Lava Lake"));
  R.applyMove(t, 0, forceTargets(t, 0, "Whirlpool").find((x) => x.from === 1 && x.sub.face === "perm"));
  R.pass(t, 0); R.pass(t, 1);
  assert.ok(t.p[1].void.includes(id("Lava Lake")) && !t.p[0].void.includes(id("Lava Lake")));
});
test("Tsunami returns a player's worlds; Firestorm removes a world; World Quake splits every world", () => {
  const s = table(["Ocean", "Core", "Pangaea"], []);
  put(s, 1, "Volcano"); put(s, 1, "Glacier", "Volcano", 1); put(s, 1, "Spire"); put(s, 0, "Bedrock");
  R.applyMove(s, 0, forceTargets(s, 0, "Tsunami").find((m) => m.P2 === 1));
  assert.equal(R.worldsOf(s, 1).length, 0); assert.equal(s.p[1].binder.length, 3);
  const t = table(["Core"], []);
  const v = put(t, 1, "Volcano"); put(t, 1, "Glacier", "Volcano", 1); put(t, 1, "Spire");
  R.applyMove(t, 0, forceTargets(t, 0, "Firestorm").find((m) => m.w === v.w));
  assert.ok(!findPerm(t, "Volcano") && !findPerm(t, "Glacier") && findPerm(t, "Spire"));
  const u = table(["Pangaea"], []);
  put(u, 1, "Volcano"); put(u, 1, "Ice Floe", "Volcano", 1); put(u, 1, "Hill", "Volcano", 2); put(u, 1, "Dune", "Volcano", 3); // (the c-still cycle can't be moved)
  R.applyMove(u, 0, forceTargets(u, 0, "World Quake")[0]);
  assert.equal(R.worldsOf(u, 1).length, 2);
});
test("Surge returns a permanence and the permanences adjacent to it, but not the one across", () => {
  const s = table(["Archipelago"], []);
  const v = put(s, 1, "Volcano"); put(s, 1, "Glacier", "Volcano", 1); put(s, 1, "Bedrock", "Volcano", 2); put(s, 1, "Spire", "Volcano", 3);
  R.applyMove(s, 0, forceTargets(s, 0, "Surge").find((m) => m.t === v.id));
  assert.deepEqual(R.perms(s).map((i) => R.C[i.card].name), ["Spire"]);
});
test("Aftershock: your opponent takes the next two turns", () => {
  const s = table(["Aftershock", "Glacier"], ["Spire", "Summit", "Bedrock"]);
  R.play(s, 0, metaMove(s, 0, "Aftershock"));
  assert.equal(s.turn, 1);
  R.play(s, 1, R.legalMoves(s, 1).find((m) => m.id === id("Spire")));
  assert.equal(s.turn, 1);
  R.play(s, 1, R.legalMoves(s, 1).find((m) => m.id === id("Summit")));
  assert.equal(s.turn, 0);
});
test("Stillness: your opponent passes; Haze: no forces on their next turn", () => {
  const s = table(["Stillness", "Haze", "Glacier"], ["Spire", "Summit"]);
  R.play(s, 0, metaMove(s, 0, "Haze"));
  assert.ok(R.legalMoves(s, 1).length > 0 && R.legalMoves(s, 1).every((m) => m.face === "perm"));
  R.play(s, 1, R.legalMoves(s, 1).find((m) => m.id === id("Spire")));
  assert.ok(!s.p[1].noForce);
  R.play(s, 0, metaMove(s, 0, "Stillness"));
  assert.ok(s.p[1].passed); assert.equal(s.turn, 0); assert.equal(s.phase, "turn");
});
test("Sunlight removes every force; Weathering returns the newest of the opponent's cards on the table", () => {
  const s = table(["Sunlight", "Weathering", "Bedrock"], ["Ashfield"]);
  const p = put(s, 0, "Plateau"); put(s, 1, "Spire"); const su = put(s, 1, "Summit");
  R.applyMove(s, 0, forceTargets(s, 0, "Tangle")[0]);
  s.turn = 1; R.applyMove(s, 1, forceTargets(s, 1, "Brushfire").find((m) => m.t === p.id)); s.turn = 0;
  assert.equal(R.forces(s).length, 2);
  R.applyMove(s, 0, metaMove(s, 0, "Sunlight"));
  assert.equal(R.forces(s).length, 0);
  assert.ok(s.p[1].void.includes(id("Ashfield")));
  const w = metaMove(s, 0, "Weathering");
  assert.equal(w.t, su.id); // Summit is unaffected by forces, but Weathering is a meta card
  R.applyMove(s, 0, w);
  assert.ok(s.p[1].binder.includes(id("Summit")) && !findPerm(s, "Summit"));
});
test("Thunder: one more play after both players pass", () => {
  const s = table(["Thunder", "Glacier"], ["Spire"]);
  R.play(s, 0, metaMove(s, 0, "Thunder"));
  R.pass(s, 1);
  R.pass(s, 0);
  assert.equal(s.phase, "turn"); assert.equal(s.turn, 0);
  R.play(s, 0, R.legalMoves(s, 0).find((m) => m.id === id("Glacier")));
  assert.equal(s.phase, "roundOver");
});
test("the reveal: the most pips goes second, a tie is the coin", () => {
  assert.equal(R.revealOpener(id("Origin"), id("Volcano"), 0), 1); // A revealed more: B opens
  assert.equal(R.revealOpener(null, id("Glacier"), 1), 0);
  assert.equal(R.revealOpener(id("Lagoon"), id("Moor"), 1), 1);
  assert.equal(R.bestReveal([id("Glacier"), id("Echo"), id("Volcano"), id("Lagoon"), id("Moor")]), id("Lagoon"));
});
console.log(`${n} rule checks passed`);
