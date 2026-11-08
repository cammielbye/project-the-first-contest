// Runs one piece of a big simulation request, or merges the pieces (used by .github/workflows/sims.yml).
//   node sims/run.mjs shard <i>   play shard i of sims/request.json into sims/out/shard-<i>.json
//   node sims/run.mjs merge       summarize every shard into sims/results/<name>/
import { readFileSync, readdirSync, mkdirSync, writeFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { cpus } from "node:os";

const here = new URL(".", import.meta.url).pathname;
const req = JSON.parse(readFileSync(here + "request.json", "utf8"));
const [mode, i] = process.argv.slice(2);
const script = here + "../scripts/" + (req.script || "sim3-rate") + ".mjs";
if (mode === "shard") {
  const per = Math.ceil(req.contests / req.shards), first = Number(i) * per, n = Math.min(per, req.contests - first);
  mkdirSync(here + "out", { recursive: true });
  if (n > 0) execFileSync("node", [script, String(n), "--first", String(first), "--seed", String(req.seed || 1), "--workers", String(cpus().length), ...(req.args || []), "--json", `${here}out/shard-${i}.json`], { stdio: "inherit" });
} else if (mode === "merge") {
  const files = readdirSync(here + "out").filter((f) => f.endsWith(".json")).map((f) => here + "out/" + f);
  const dir = `${here}results/${req.name}`;
  mkdirSync(dir, { recursive: true });
  const out = execFileSync("node", [script, "--from", files.join(","), "--csv", dir + "/ratings.csv"], { encoding: "utf8", maxBuffer: 1 << 26 });
  writeFileSync(dir + "/summary.txt", out);
  writeFileSync(dir + "/request.json", JSON.stringify(req, null, 2) + "\n");
  console.log(out);
} else throw new Error("usage: run.mjs shard <i> | merge");
