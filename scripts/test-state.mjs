// Quick checks of the table state. Run: node scripts/test-state.mjs
import { readFileSync } from "node:fs";
import assert from "node:assert/strict";
import { apply, initialState, findInst } from "../js/state.js";

const data = JSON.parse(readFileSync(new URL("../data/cards.json", import.meta.url), "utf8"));
const cardsById = new Map(data.cards.map((c) => [c.id, c]));

let s = initialState({ p1: "Cam", p2: "Alex" });
const run = (action) => {
  const r = apply(s, action, cardsById);
  s = r.state;
  return r.effects;
};
const inst = (owner, id, face = "permanence") => ({ iid: `${owner}-${id}`, id: String(id), face, owner, original: false });

run({ seat: "p1", type: "chooseBinder", count: 30 });
run({ seat: "p2", type: "chooseBinder", count: 30 });
assert.equal(s.players.p1.binderCount, 30);

// Play a permanence into your own area, then a force from the other player on top of it.
run({ seat: "p1", type: "place", inst: inst("p1", 41), to: { area: "p1", key: "1,1" } });
run({ seat: "p2", type: "place", inst: inst("p2", 12, "force"), to: { area: "p1", key: "1,1" } });
assert.equal(s.table.p1["1,1"].length, 2);
assert.equal(s.players.p1.binderCount, 29);
assert.equal(s.players.p2.binderCount, 29);
assert.match(s.log.at(-1).text, /Alex played Brushfire \(force\) on Ledge in Cam's world 1/);

// The force goes to its owner's void, not the area's owner.
run({ seat: "p1", type: "toVoid", iid: "p2-12" });
assert.equal(s.voids.p2.length, 1);
assert.equal(s.voids.p1.length, 0);
assert.equal(s.table.p1["1,1"].length, 1);

// Flip and move.
run({ seat: "p1", type: "flip", iid: "p1-41" });
assert.equal(findInst(s, "p1-41").inst.face, "force");
assert.match(s.log.at(-1).text, /flipped Ledge to Gust/);
run({ seat: "p2", type: "move", iid: "p1-41", to: { area: "p1", key: "0,3" } });
assert.equal(s.table.p1["1,1"], undefined);
assert.equal(s.table.p1["0,3"].length, 1);

// Returning to a binder produces an effect for the owner's browser.
const fx = run({ seat: "p2", type: "toBinder", iid: "p1-41" });
assert.deepEqual(fx.map((e) => [e.kind, e.seat]), [["toBinder", "p1"]]);
assert.equal(s.players.p1.binderCount, 30);

// From a void back onto the table.
run({ seat: "p2", type: "move", iid: "p2-12", to: { area: "p2", key: "1,7" } });
assert.equal(s.voids.p2.length, 0);

// Bad input is ignored.
const before = s;
run({ seat: "p1", type: "place", inst: inst("p2", 5), to: { area: "p1", key: "0,0" } }); // not your card
run({ seat: "p1", type: "move", iid: "p2-12", to: { area: "p1", key: "9,9" } }); // off the grid
run({ seat: "p3", type: "pass" });
run({ seat: "p1", type: "nonsense" });
assert.equal(s, before);

// Meta cards have one face: flipping does nothing.
run({ seat: "p2", type: "place", inst: inst("p2", "meta-lull", "meta"), to: { area: "p2", key: "0,0" } });
const metaBefore = s;
run({ seat: "p2", type: "flip", iid: "p2-meta-lull" });
assert.equal(s, metaBefore);
assert.match(s.log.at(-1).text, /Alex played Lull \(meta\)/);

// Counters, rounds, turns.
run({ seat: "p1", type: "counter", target: "p2", field: "worldPoints", delta: 1 });
run({ seat: "p1", type: "counter", target: "p2", field: "worldPoints", delta: -1 });
run({ seat: "p1", type: "counter", target: "p2", field: "worldPoints", delta: -1 });
assert.equal(s.players.p2.worldPoints, 0);
run({ seat: "p1", type: "opener", pick: "p2" });
assert.equal(s.turn, "p2");
run({ seat: "p2", type: "pass" });
assert.equal(s.players.p2.passed, true);
run({ seat: "p1", type: "round", delta: 1 });
assert.equal(s.round, 2);
assert.equal(s.players.p2.passed, false);

// Play tracker: plays from the binder count for the round they happen in.
{
  let t = initialState({ p1: "Cam", p2: "Alex" });
  const go = (a) => (t = apply(t, a, cardsById).state);
  go({ seat: "p1", type: "place", inst: inst("p1", 41), to: { area: "p1", key: "0,0" } });
  go({ seat: "p1", type: "place", inst: inst("p1", 52), to: { area: "p1", key: "0,1" } });
  go({ seat: "p2", type: "place", inst: inst("p2", 12, "force"), to: { area: "p1", key: "0,0" } });
  assert.equal(t.players.p1.played[1], 2);
  assert.equal(t.players.p2.played[1], 1);
  assert.match(t.log.at(-1).text, /\(1 of 10 this round\)/);

  // A card effect returning a card doesn't undo the play...
  go({ seat: "p2", type: "toBinder", iid: "p1-52" });
  assert.equal(t.players.p1.played[1], 2);
  // ...and neither can the other player's "undo"...
  go({ seat: "p2", type: "toBinder", iid: "p1-41", undo: true });
  assert.equal(t.players.p1.played[1], 2);
  // ...but the owner taking back their own play does.
  go({ seat: "p1", type: "place", inst: inst("p1", 23), to: { area: "p1", key: "1,1" } });
  assert.equal(t.players.p1.played[1], 3);
  go({ seat: "p1", type: "toBinder", iid: "p1-23", undo: true });
  assert.equal(t.players.p1.played[1], 2);
  assert.match(t.log.at(-1).text, /took back Spring/);

  // Each round counts separately, and has its own cap.
  go({ seat: "p1", type: "round", delta: 1 });
  assert.equal(t.players.p1.played[2] || 0, 0);
  go({ seat: "p1", type: "cap", delta: -1 });
  assert.equal(t.caps[2], 9);
  go({ seat: "p1", type: "round", delta: -1 });
  assert.equal(t.caps[1] ?? 10, 10);

  // Manual correction.
  go({ seat: "p2", type: "played", target: "p1", delta: 1 });
  assert.equal(t.players.p1.played[1], 3);
  go({ seat: "p2", type: "played", target: "p2", delta: -1 });
  go({ seat: "p2", type: "played", target: "p2", delta: -1 });
  assert.equal(t.players.p2.played[1], 0);
}

// A force that happens once can go straight from the binder to its owner's void, and counts as played.
{
  let t = initialState({ p1: "Cam", p2: "Alex" });
  t = apply(t, { seat: "p1", type: "placeVoid", inst: inst("p1", 88, "force") }, cardsById).state;
  assert.equal(t.voids.p1.length, 1);
  assert.equal(t.players.p1.played[1], 1);
  assert.match(t.log.at(-1).text, /Cam played Collapse \(force\) straight to their void/);
  const same = t;
  t = apply(t, { seat: "p2", type: "placeVoid", inst: inst("p1", 41) }, cardsById).state; // not your card
  assert.equal(t, same);
}

// Reset keeps names and clears everything else.
const rfx = run({ seat: "p2", type: "reset" });
assert.deepEqual(rfx, [{ kind: "clearPrivate" }]);
assert.equal(s.players.p1.name, "Cam");
assert.equal(s.players.p1.binderChosen, false);
assert.deepEqual(s.table, { p1: {}, p2: {} });
assert.equal(s.round, 1);
assert.equal(s.log.length, 1);

console.log("state tests passed");
