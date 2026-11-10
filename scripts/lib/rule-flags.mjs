// The simulator's rule switches. Defaults since Nov 10 (Cam): one round, no card cap, worlds of up to 2x2, and a world
// scores one world point at most (one of each element or four of one element), with no Perfect World.
//   --bo3        best of three rounds
//   --cap[=N]    a cap of N cards a round per player (10 if no N)
//   --open       open worlds, no cap on size (the default Nov 8-9)
//   --sets       the scoring before Nov 10: a point per complete set, Perfect World at 3
// --square, --bo1 and --nocap are still accepted; they're the defaults.
export function ruleFlags(args) {
  const c = args.find((a) => a === "--cap" || a.startsWith("--cap="));
  return { bo1: !args.includes("--bo3"), nocap: !c, cap: c && c.includes("=") ? Number(c.split("=")[1]) : 10, open: args.includes("--open"), sets: args.includes("--sets") };
}
export const contestOpts = (f) => ({ openWorlds: f.open, bestOf: f.bo1 ? 1 : 3, noCap: f.nocap, cap: f.cap, scoring: f.sets ? "sets" : "point" });
export const ruleLabel = (f) => `${f.bo1 ? "one round" : "best of three"}, ${f.nocap ? "no card cap" : `cap of ${f.cap}`}, ${f.open ? "open worlds" : "worlds of up to 2x2"}, ${f.sets ? "a point per set" : "one point a world"}`;
