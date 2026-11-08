# Big simulation runs

Runs too big for a laptop go to GitHub's runners (free for a public repo). Write a request to
`sims/request.json` on the `sim-runs` branch and push it; `.github/workflows/sims.yml` splits it
across parallel jobs (four processors each) and commits the summary and card ratings back to
`sim-runs` under `sims/results/<name>/` (`summary.txt`, `ratings.csv`, the request).

```json
{
  "name": "2026-11-09-ratings-20k",
  "script": "sim3-rate",
  "contests": 20000,
  "shards": 20,
  "seed": 900,
  "args": ["--quick"]
}
```

The rules default to one round, no card cap and open worlds, with random binders of 15 (since Nov 8);
add `--bo3`, `--cap` or `--square` to `args` to switch back.

A sharded run plays exactly the contests one long run would (contest k always uses the same
seed), so pieces can be split however is convenient.
