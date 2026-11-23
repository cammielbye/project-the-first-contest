// Checks for the Branch B rules engine (branch-b/js/rules-b.js). Run: node scripts/test-branch-b.mjs
import * as R from "../branch-b/js/rules-b.js";

let fails = 0, n = 0;
const ok = (cond, what) => { n++; if (!cond) { fails++; console.log("FAIL", what); } };
const ci = (name) => R.CARDS.find((c) => c.n === name).i;
// put a card straight into a world, as if played on an earlier turn
function put(s, P, name, w = "new", flipped = false) {
  const id = "t" + ++s.seq;
  s.inst[id] = { c: ci(name), o: P, f: flipped, h: -1 };
  s.P[P].binder = s.P[P].binder.filter((x) => x !== ci(name));
  if (w === "new") s.P[P].worlds.push([id]); else s.P[P].worlds[w].push(id);
  return id;
}
const idOf = (s, name) => Object.keys(s.inst).find((k) => R.card(s, k).n === name);
const quiet = (first = 0) => { const s = R.newGame(first); return s; };

// scoring
ok(R.pointsOfPips(["water", "earth", "fire", "air"]) === 1, "one of each");
ok(R.pointsOfPips(["water", "water", "water", "water", "water", "earth", "fire", "air"]) === 2, "a set and four water");
ok(R.pointsOfPips(Array(12).fill("earth")) === 3, "twelve earth");
ok(R.pointsOfPips(["any", "any", "fire", "air"]) === 1, "any pips fill a set");
ok(R.pointsOfPips(["water", "water", "water"]) === 0, "three water score nothing");

// turns: one landscape a turn, alternate, 9 each, then the shared 10th
{
  const s = quiet(0);
  ok(R.play(s, 0, ci("Lake"), "new"), "play a landscape");
  ok(!R.play(s, 0, ci("Spring"), "new"), "no second landscape");
  ok(!R.canUseForce(s, 0, idOf(s, "Lake")), "no force the turn it's played");
  R.endTurn(s);
  ok(R.active(s) === 1 && R.turnNo(s) === 1, "player 2's turn 1");
  for (let k = 0; k < 16; k++) R.endTurn(s);
  ok(R.turnNo(s) === 9 && R.active(s) === 1, "player 2's turn 9");
  R.endTurn(s);
  ok(s.phase === "lock" && R.turnNo(s) === 10, "the shared 10th");
}

// a force a turn, from a card played earlier; front pips stop counting
{
  const s = quiet(0);
  const lake = put(s, 0, "Lake");
  const spring = put(s, 0, "Spring", 0);
  const opp = put(s, 1, "Meadow");
  ok(R.canUseForce(s, 0, lake), "can use an older card's force");
  R.beginForce(s, 0, lake);
  ok(R.choices(s).opts.length === 1, "Flood offers the one-pip card");
  R.pick(s, { t: "card", id: opp });
  ok(!s.inst[opp] && s.P[1].binder.includes(ci("Meadow")), "Meadow returns to its owner's binder");
  ok(s.inst[lake].f && R.pipsOf(s, lake).length === 1, "Lake flipped to Flood with one water");
  ok(!R.canUseForce(s, 0, spring), "only one force a turn");
}

// Cave-in shields the other cards in its world from the opponent's forces
{
  const s = quiet(0);
  const v = put(s, 0, "Volcano");
  put(s, 1, "Cavern", "new", true);
  const m = put(s, 1, "Meadow", 0);
  const h = put(s, 1, "Hills");
  R.beginForce(s, 0, v);
  const ids = R.choices(s).opts.map((o) => o.id);
  ok(!ids.includes(m) && ids.includes(h), "Eruption can't reach past Cave-in");
}

// next turn, flip this back
{
  const s = quiet(0);
  const t = put(s, 0, "Tidal Flat");
  R.beginForce(s, 0, t);
  ok(s.inst[t].f && R.pipsOf(s, t).join() === "water,water", "High Tide shows two water");
  R.endTurn(s); ok(s.inst[t].f, "still High Tide on the other player's turn");
  R.endTurn(s); ok(!s.inst[t].f, "Tidal Flat flips back at its owner's next turn");
}

// Kindling: its force happens
{
  const s = quiet(0);
  const a = put(s, 0, "Ash Plain");
  const l = put(s, 0, "Lake", 0);
  const opp = put(s, 1, "Spring");
  R.beginForce(s, 0, a);
  R.pick(s, { t: "card", id: l });
  ok(s.inst[l].f && s.pending && s.pending.nested, "Kindling flips Lake and Flood waits for a choice");
  R.pick(s, { t: "card", id: opp });
  ok(!s.inst[opp] && !s.pending, "Flood happens");
  ok(s.forced === 1, "Kindling's chained force doesn't count as a second force");
}

// Gale: two moves, the second against the worlds after the first
{
  const s = quiet(0);
  const g = put(s, 0, "Peak");
  const x = put(s, 0, "Hills", 0);
  const y = put(s, 0, "Spring", 0);
  R.beginForce(s, 0, g);
  R.pick(s, { t: "card", id: x }); R.pick(s, { t: "new", side: 0 });
  R.pick(s, { t: "card", id: y });
  const st = R.choices(s);
  ok(st.opts.some((o) => o.t === "world"), "the second move can join the new world");
  R.pick(s, st.opts.find((o) => o.t === "world" && s.P[0].worlds.length && true));
  ok(!s.pending && s.P[0].worlds.length === 2, "Gale finishes with two worlds");
}

// Seedwind: the extra play goes into a different world
{
  const s = quiet(0);
  const c = put(s, 0, "Cliffs");
  R.beginForce(s, 0, c);
  ok(s.extra === 1, "Seedwind gives another play");
  ok(R.legalPlays(s, 0).every((m) => m.w !== 0), "not into Cliffs' world");
}

// Earthquake splits an opponent's world
{
  const s = quiet(0);
  const f = put(s, 0, "Fault Line");
  put(s, 1, "Hills"); const b = put(s, 1, "Spring", 0); put(s, 1, "Meadow", 0);
  R.beginForce(s, 0, f);
  R.pick(s, { t: "world", side: 1, w: 0 });
  R.pick(s, { t: "card", id: b });
  R.pick(s, { t: "stop" });
  ok(s.P[1].worlds.length === 2 && s.P[1].worlds[1][0] === b, "Spring splits off");
}

// Supervolcano spares guarded cards
{
  const s = quiet(0);
  const c = put(s, 0, "Caldera"); const mine = put(s, 0, "Hills", 0);
  put(s, 1, "Cavern", "new", true); const safe = put(s, 1, "Spring", 0); const hit = put(s, 1, "Meadow");
  R.beginForce(s, 0, c);
  ok(s.inst[mine].f && s.inst[hit].f && !s.inst[safe].f, "everything flips but the guarded card");
}

// a perfect world wins at once
{
  const s = quiet(0);
  put(s, 0, "Ocean"); put(s, 0, "Caldera", 0); put(s, 0, "Highlands", 0);
  R.play(s, 0, ci("Peak"), 0);
  ok(s.phase === "over" && s.winner.P === 0 && s.winner.why === "perfect", "perfect world wins");
}

// the shared 10th: lock in, reveal, resolve in turn order, finish
{
  const s = quiet(1);
  for (let k = 0; k < 18; k++) R.endTurn(s);
  const l = put(s, 0, "Lake"); const v = put(s, 1, "Volcano");
  ok(R.active(s) === 1, "the first player locks in first");
  R.play(s, 1, ci("Spring"), "new"); R.beginForce(s, 1, v); R.lockIn(s, 1);
  ok(R.active(s) === 0, "then the second");
  R.play(s, 0, ci("Meadow"), "new"); R.beginForce(s, 0, l); R.lockIn(s, 0);
  ok(s.phase === "resolve" && s.pending && s.pending.P === 1, "Eruption resolves first");
  ok(!R.cancelForce(s), "a locked-in force can't be cancelled");
  R.pick(s, { t: "card", id: idOf(s, "Meadow") });
  ok(s.pending && s.pending.P === 0, "then Flood");
  R.pick(s, { t: "card", id: idOf(s, "Spring") });
  ok(s.phase === "over" && s.winner, "the contest ends");
}

// single-pip cards can be played on an opponent's world (Cam, Nov 23)
{
  const s = quiet(0);
  put(s, 1, "Ocean"); put(s, 1, "Highlands", 0); put(s, 1, "Caldera", 0);
  ok(R.legalPlays(s, 0).some((m) => m.ci === ci("Hills") && m.side === 1 && m.w === 0), "Hills can go into the other player's world");
  ok(!R.legalPlays(s, 0).some((m) => m.ci === ci("Lake") && m.side === 1), "Lake can't");
  R.play(s, 0, ci("Hills"), 0, 1);
  const h = idOf(s, "Hills");
  ok(R.findCard(s, h).side === 1 && s.inst[h].o === 0, "Hills sits in their world and stays player 1's");
  ok(s.P[1].worlds[0].length === 4 && R.worldPts(s, s.P[1].worlds[0]) === 2, "their world is full at 2 points, no perfect world");
  R.endTurn(s); R.endTurn(s);
  ok(R.canUseForce(s, 0, h), "its owner can still use its force there");
  const m = put(s, 0, "Meadow", "new");
  R.beginForce(s, 0, m);
  ok(R.choices(s).opts.some((o) => o.t === "card" && o.id === h), "Gust can bring it home");
}
{
  const s = quiet(1);
  put(s, 1, "Lake");
  const sp = put(s, 1, "Spring", 0); s.inst[sp].o = 0; // player 1's Spring in player 2's world
  R.beginForce(s, 1, idOf(s, "Lake"));
  R.pick(s, { t: "card", id: sp });
  ok(s.P[0].binder.includes(ci("Spring")) && !s.P[1].binder.includes(ci("Spring")), "Flood sends it back to its owner's binder");
}

console.log(`${n - fails}/${n} checks pass`);
process.exit(fails ? 1 : 0);
