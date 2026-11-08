// The simulator's rule switches. Since Nov 8 (Cam: the game is one round again) the defaults are one round,
// no card cap and open worlds; --bo3, --cap and --square switch back to best of three, a cap of 10 cards a
// round and worlds of up to 4 (2x2). The old --bo1, --nocap and --open are still accepted; they're the defaults now.
export function ruleFlags(args) {
  return { bo1: !args.includes("--bo3"), nocap: !args.includes("--cap"), open: !args.includes("--square") };
}
export const contestOpts = (f) => ({ openWorlds: f.open, bestOf: f.bo1 ? 1 : 3, noCap: f.nocap });
export const ruleLabel = (f) => `${f.bo1 ? "one round" : "best of three"}, ${f.nocap ? "no card cap" : "cap of 10"}, ${f.open ? "open worlds" : "worlds of up to 4"}`;
