// Runs simulated contests between two binders and prints what happened.
//
//   node sim/sim.js [contests] [--style main|thrifty|greedy|noforces] [--seed N] [--workers N] [--binders tides,embers]
//
// Writes every contest to sim/out/<style>-<contests>-<seed>.json and the stats to the same name with -summary.json.
'use strict';
const path = require('path');
const fs = require('fs');
const os = require('os');
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');
const E = require('./engine');
const { makeAI } = require('./ai');
const { playContest, rngOf } = require('./game');
const { summarize, report } = require('./stats');

const ROOT = path.join(__dirname, '..');
const STYLES = {
  main: {},                    // looks at the opponent's best reply to each move
  thrifty: { costScale: 2.5 }, // values its cards 2.5 times as much, so it passes sooner
  greedy: { ply: 1 },          // no lookahead
  noforces: { forces: false }, // never plays a force face (a building-only control)
};

function runSlice({ from, to, seed, style, binderIds }) {
  const { binders } = E.loadCards(ROOT);
  const bs = binderIds.map((id) => binders.find((b) => b.id === id));
  const out = [];
  for (let g = from; g < to; g++) {
    const rng = rngOf(seed + g * 7919);
    const pair = g % 2 ? [bs[1], bs[0]] : [bs[0], bs[1]]; // each binder takes each seat half the time
    const opt = Object.assign({ rng }, STYLES[style]);
    const rec = playContest([pair[0].cards, pair[1].cards], [makeAI(opt), makeAI(opt)], { rng });
    rec.seats = [pair[0].name, pair[1].name];
    for (const R of rec.rounds) delete R.table;
    out.push(rec);
  }
  return out;
}

if (!isMainThread) {
  parentPort.postMessage(runSlice(workerData));
  return;
}

const args = process.argv.slice(2);
const opt = (name, dflt) => { const k = args.indexOf('--' + name); return k >= 0 ? args[k + 1] : dflt; };
const contests = +(args.find((a) => /^\d+$/.test(a)) || 200);
const style = opt('style', 'main');
const seed = +opt('seed', 1);
const workers = Math.max(1, Math.min(+opt('workers', os.cpus().length), contests));
if (!STYLES[style]) { console.error(`Unknown style "${style}". Use one of: ${Object.keys(STYLES).join(', ')}`); process.exit(1); }

const { binders: all } = E.loadCards(ROOT);
const want = (opt('binders', '') || '').split(',').filter(Boolean);
const chosen = want.length === 2 ? want.map((w) => all.find((b) => b.id.includes(w.toLowerCase()) || b.name.toLowerCase().includes(w.toLowerCase()))) : all.slice(0, 2);
if (chosen.some((b) => !b)) { console.error('Binder not found. Binders: ' + all.map((b) => b.name).join('; ')); process.exit(1); }
const binderIds = chosen.map((b) => b.id);

console.log(`Simulating ${contests} contests, ${chosen.map((b) => b.name).join(' vs ')}, style ${style}, seed ${seed}, ${workers} worker(s)...`);
const t0 = Date.now();
const per = Math.ceil(contests / workers);
const jobs = [];
for (let w = 0; w < workers; w++) {
  const from = w * per, to = Math.min(contests, from + per);
  if (from >= to) continue;
  jobs.push(new Promise((resolve, reject) => {
    const wk = new Worker(__filename, { workerData: { from, to, seed, style, binderIds } });
    wk.on('message', resolve); wk.on('error', reject);
  }));
}
Promise.all(jobs).then((parts) => {
  const games = parts.flat();
  const summary = summarize(games, chosen);
  const dir = path.join(__dirname, 'out');
  fs.mkdirSync(dir, { recursive: true });
  const base = path.join(dir, `${style}-${contests}-${seed}`);
  fs.writeFileSync(base + '.json', JSON.stringify({ style, seed, binders: chosen.map((b) => b.name), games }));
  fs.writeFileSync(base + '-summary.json', JSON.stringify(summary, null, 1));
  console.log(report(summary, `Style ${style}`));
  console.log(`\nDone in ${Math.round((Date.now() - t0) / 1000)}s. Contests: ${path.relative(ROOT, base)}.json  Stats: ${path.relative(ROOT, base)}-summary.json`);
  console.log(`Read a contest move by move: node sim/show.js ${path.relative(ROOT, base)}.json 0`);
}).catch((e) => { console.error(e); process.exit(1); });
