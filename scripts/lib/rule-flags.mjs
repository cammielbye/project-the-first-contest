// The simulator's rule switches. Defaults since Nov 11 (Cam, fifth pass): best of three rounds, no card cap, worlds of up
// to 2x2, a world scores one world point at most (one of each element or four of one element, Nov 10), and the reveal
// decides who opens round 1 (each player reveals the permanence with the most pips in their binder; the most pips goes
// second; a tie is a coin flip).
//   --bo1        one round (the default Nov 8-10)
//   --cap[=N]    a cap of N cards a round per player (10 if no N)
//   --open       open worlds, no cap on size (the default Nov 8-9)
//   --sets       the scoring before Nov 10: a point per complete set, Perfect World at 3
//   --coin       a coin flip decides who opens, with no reveal (the rule before Nov 11)
// --square, --bo3 and --nocap are still accepted; they're the defaults.
import * as R from "../../js/game/rules.js";

export function ruleFlags(args) {
  const c = args.find((a) => a === "--cap" || a.startsWith("--cap="));
  return { bo1: args.includes("--bo1"), nocap: !c, cap: c && c.includes("=") ? Number(c.split("=")[1]) : 10, open: args.includes("--open"), sets: args.includes("--sets"), coin: args.includes("--coin") };
}
export const contestOpts = (f) => ({ openWorlds: f.open, bestOf: f.bo1 ? 1 : 3, noCap: f.nocap, cap: f.cap, scoring: f.sets ? "sets" : "point" });
export const ruleLabel = (f) => `${f.bo1 ? "one round" : "best of three"}, ${f.nocap ? "no card cap" : `cap of ${f.cap}`}, ${f.open ? "open worlds" : "worlds of up to 2x2"}, ${f.sets ? "a point per set" : "one point a world"}, ${f.coin ? "a coin decides who opens" : "the reveal decides who opens"}`;
// Who opens round 1: the reveal (each side reveals its most pips; the most pips goes second; a tie is the coin), or the
// coin alone with --coin. coin: a number in [0, 1). Returns { opener, reveals, byCoin }.
export function openerFor(f, idsA, idsB, coin) {
  const c = coin < 0.5 ? 0 : 1;
  if (f.coin) return { opener: c, reveals: null, byCoin: true };
  const reveals = [R.bestReveal(idsA), R.bestReveal(idsB)];
  const pa = R.revealPips(reveals[0]), pb = R.revealPips(reveals[1]);
  return { opener: R.revealOpener(reveals[0], reveals[1], c), reveals, byCoin: pa === pb };
}
