// Prints simulated contests move by move.
//   node sim/show.js sim/out/<file>.json [contest numbers...]
// Marks: *force face, +meta card, ^played on another card, [x removed, ↩ returned to binder]
'use strict';
const path = require('path');
const fs = require('fs');
const E = require('./engine');
const { short } = require('./stats');
E.loadCards(path.join(__dirname, '..'));
const [file, ...nums] = process.argv.slice(2);
if (!file) { console.error('Usage: node sim/show.js sim/out/<file>.json [contest numbers...]'); process.exit(1); }
const d = JSON.parse(fs.readFileSync(file, 'utf8'));
const idx = nums.length ? nums.map(Number) : [0];
const C = E.C;
for (const k of idx) {
  const g = d.games[k];
  if (!g) { console.log(`#${k}: no such contest`); continue; }
  const seat = g.seats.map(short);
  console.log(`#${k}  P0 ${seat[0]}, P1 ${seat[1]}. Round 1 opener P${g.opener}. Winner: ${g.winner === null ? 'drawn' : seat[g.winner]}`);
  for (const R of g.rounds) {
    const how = R.winner === null ? 'drawn' : `${seat[R.winner]}${R.byAlt ? ' (card win condition)' : R.byTie ? ' (affinity tie-break)' : ''}`;
    console.log(` Round ${R.r}, P${R.opener} opens → ${how}. World points ${R.score.map((x) => x.pts).join('–')}, affinity ${R.score.map((x) => x.tie).join('–')}`);
    for (const P of [0, 1]) {
      const plays = R.plays[P].map((p) => {
        if (p.skip) return '(skipped)';
        const mark = p.face === 'force' ? '*' : p.face === 'meta' ? '+' : p.face === 'sit' ? '^' : '';
        const hit = p.ev.removed.map((c) => 'x' + C[c].name).concat(p.ev.returned.map((c) => '↩' + C[c].name));
        return mark + p.name + (hit.length ? `[${hit.join(', ')}]` : '');
      });
      console.log(`   P${P} ${seat[P]}: ${plays.join(', ') || '(no cards)'}`);
    }
    console.log('   Passes: ' + R.passOrder.map((p) => `P${p.P} after ${p.after} cards${p.oppPassed ? ' (other already passed)' : ''}, ${p.standing > 0 ? 'ahead' : p.standing < 0 ? 'behind' : 'level'}`).join('; '));
  }
}
