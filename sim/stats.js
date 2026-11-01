// Turns contest records into stats, keyed by binder (the name after the comma: "Binder A, Tides" -> "Tides").
'use strict';
const E = require('./engine');

const short = (name) => name.split(',').pop().trim();
const pct = (a, b) => (b ? Math.round((1000 * a) / b) / 10 : 0);
const mean = (a) => (a.length ? Math.round((100 * a.reduce((x, y) => x + y, 0)) / a.length) / 100 : 0);
const RR = { S: 4, A: 3, B: 2, C: 1 };

function summarize(games, binders) {
  const C = E.C;
  const names = binders.map((b) => short(b.name));
  const per = () => Object.fromEntries(names.map((n) => [n, 0]));
  const perArr = () => Object.fromEntries(names.map((n) => [n, []]));
  const S = { contests: games.length, wins: per(), draws: 0, threeRounds: 0, r1OpenerWins: 0, decided: 0 };
  const R = { n: 0, byPoints: 0, byTieBreak: 0, byAlt: 0, drawn: 0, zeroZero: 0, openerWins: 0, openerDecided: 0,
    pts: perArr(), cards: Object.fromEntries(names.map((n) => [n, { 1: [], 2: [], 3: [] }])), altWins: per(), bonusRounds: 0,
    firstPass: { ahead: 0, behind: 0, level: 0 }, capHit: 0, worldSizes: [0, 0, 0, 0] };
  const faces = Object.fromEntries(names.map((n) => [n, { perm: 0, sit: 0, force: 0, meta: 0 }]));
  const cards = {}; const taken = {}; const stake = {};
  const gamesBy = per(), winsBy = per();

  for (const g of games) {
    const seat = g.seats.map(short);
    if (g.winner === null) S.draws++; else { S.wins[seat[g.winner]]++; S.decided++; if (g.winner === g.opener) S.r1OpenerWins++; }
    if (g.rounds.length === 3) S.threeRounds++;
    for (const P of [0, 1]) { gamesBy[seat[P]]++; if (g.winner === P) winsBy[seat[P]]++; }
    const playedIn = [new Set(), new Set()]; const played = [[], []];
    for (const r of g.rounds) {
      R.n++;
      if (r.winner === null) R.drawn++; else if (r.byAlt) R.byAlt++; else if (r.byTie) R.byTieBreak++; else R.byPoints++;
      if (r.byAlt) for (const P of [0, 1]) if (r.score[P].alt) R.altWins[seat[P]]++;
      if (r.score[0].pts === 0 && r.score[1].pts === 0) R.zeroZero++;
      if (r.winner !== null) { R.openerDecided++; if (r.winner === r.opener) R.openerWins++; }
      if (r.score[0].mtn || r.score[1].mtn) R.bonusRounds++;
      const fp = r.passOrder[0];
      if (fp) R.firstPass[fp.standing > 0 ? 'ahead' : fp.standing < 0 ? 'behind' : 'level']++;
      for (const P of [0, 1]) {
        const b = seat[P];
        R.pts[b].push(r.score[P].pts);
        for (const w of r.score[P].worlds) R.worldSizes[w.cards - 1]++;
        const plays = r.plays[P].filter((p) => !p.skip);
        R.cards[b][r.r].push(plays.length);
        if (plays.length >= 10) R.capHit++;
        for (const p of plays) {
          faces[b][p.face]++;
          const k = b + '|' + p.id;
          const c = cards[k] || (cards[k] = { binder: b, id: p.id, plays: 0, perm: 0, sit: 0, force: 0, meta: 0, contests: 0, wins: 0 });
          c.plays++; c[p.face]++;
          playedIn[P].add(p.id); played[P].push(p.id);
          const n = (p.ev.removed.length + p.ev.returned.length);
          if (n) { const by = p.face === 'meta' ? C[p.id].name : C[p.id].fname; const t = taken[by] || (taken[by] = { binder: b, removed: 0, returned: 0 }); t.removed += p.ev.removed.length; t.returned += p.ev.returned.length; }
        }
      }
    }
    for (const P of [0, 1]) for (const id of playedIn[P]) { const c = cards[seat[P] + '|' + id]; c.contests++; if (g.winner === P) c.wins++; }
    if (g.winner !== null && played[1 - g.winner].length) {
      // READING: for the stake stat, the winner picks the rarest card the loser played
      const pick = played[1 - g.winner].slice().sort((x, y) => (RR[C[y].rarity] - RR[C[x].rarity]) || ((C[y].no || 0) - (C[x].no || 0)))[0];
      const k = seat[1 - g.winner] + ': ' + C[pick].name; stake[k] = (stake[k] || 0) + 1;
    }
  }

  const cardRows = [];
  for (const b of binders) for (const id of b.cards) {
    const bn = short(b.name); const c = cards[bn + '|' + id]; const d = C[id];
    const notGames = gamesBy[bn] - (c ? c.contests : 0), notWins = winsBy[bn] - (c ? c.wins : 0);
    cardRows.push({
      binder: bn, card: d.name, rarity: d.meta ? 'meta' : d.rarity, force: d.fname || null,
      playedIn: c ? pct(c.contests, gamesBy[bn]) : 0, plays: c ? c.plays : 0,
      asPermanence: c && c.plays ? pct(c.perm + c.sit, c.plays) : null, asForce: c && c.plays ? pct(c.force, c.plays) : null,
      winWhenPlayed: c && c.contests ? pct(c.wins, c.contests) : null, winWhenNot: notGames >= 20 ? pct(notWins, notGames) : null,
    });
  }
  const fpTot = R.firstPass.ahead + R.firstPass.behind + R.firstPass.level;
  const wsTot = R.worldSizes.reduce((a, b) => a + b, 0);
  return {
    contests: S.contests,
    winPct: Object.fromEntries(names.map((n) => [n, pct(S.wins[n], S.contests)])), drawPct: pct(S.draws, S.contests),
    threeRoundsPct: pct(S.threeRounds, S.contests), r1OpenerWinsPct: pct(S.r1OpenerWins, S.decided),
    rounds: {
      n: R.n, byPointsPct: pct(R.byPoints, R.n), byTieBreakPct: pct(R.byTieBreak, R.n), byAltPct: pct(R.byAlt, R.n), drawnPct: pct(R.drawn, R.n),
      zeroZeroPct: pct(R.zeroZero, R.n), openerWinsPct: pct(R.openerWins, R.openerDecided), altWins: R.altWins, bonusPointRoundsPct: pct(R.bonusRounds, R.n),
      pointsMean: Object.fromEntries(names.map((n) => [n, mean(R.pts[n])])),
      cardsPerRound: Object.fromEntries(names.map((n) => [n, [1, 2, 3].map((r) => mean(R.cards[n][r]))])),
      firstPasserBehindPct: pct(R.firstPass.behind, fpTot), capHitPct: pct(R.capHit, R.n * 2),
      worldSizePct: R.worldSizes.map((x) => pct(x, wsTot)),
    },
    forceSharePct: Object.fromEntries(names.map((n) => { const f = faces[n]; return [n, pct(f.force, f.perm + f.sit + f.force + f.meta)]; })),
    takenOffTable: Object.entries(taken).sort((a, b) => (b[1].removed + b[1].returned) - (a[1].removed + a[1].returned)).map(([by, t]) => ({ by, ...t })),
    stakePicks: Object.entries(stake).sort((a, b) => b[1] - a[1]).slice(0, 8).map(([pick, n]) => ({ pick, contests: n })),
    cards: cardRows,
  };
}

function report(s, label) {
  const L = [];
  const names = Object.keys(s.winPct);
  L.push(`${label}: ${s.contests} contests`);
  L.push(`  Contest wins: ${names.map((n) => `${n} ${s.winPct[n]}%`).join(', ')}, drawn ${s.drawPct}%. Went to 3 rounds: ${s.threeRoundsPct}%.`);
  const r = s.rounds;
  L.push(`  Rounds (${r.n}): won on world points ${r.byPointsPct}%, by affinity tie-break ${r.byTieBreakPct}%, by a card's own win condition ${r.byAltPct}%, drawn ${r.drawnPct}%. Ended 0-0: ${r.zeroZeroPct}%.`);
  L.push(`  World points per round: ${names.map((n) => `${n} ${r.pointsMean[n]}`).join(', ')}. Cards per round (R1/R2/R3): ${names.map((n) => `${n} ${r.cardsPerRound[n].join('/')}`).join(', ')}.`);
  L.push(`  Force faces: ${names.map((n) => `${n} ${s.forceSharePct[n]}% of plays`).join(', ')}. Worlds at round end by size 1/2/3/4: ${r.worldSizePct.join('% / ')}%.`);
  L.push(`  First player to pass was behind ${r.firstPasserBehindPct}% of the time. Round opener won ${r.openerWinsPct}% of decided rounds.`);
  L.push(`  Taken off the table: ${s.takenOffTable.slice(0, 8).map((t) => `${t.by} (${t.binder}) ${t.removed + t.returned}${t.returned ? `, ${t.returned} returned` : ''}`).join('; ')}`);
  L.push(`  Least played: ${s.cards.slice().sort((a, b) => a.playedIn - b.playedIn).slice(0, 6).map((c) => `${c.card} (${c.binder}) ${c.playedIn}%`).join(', ')}`);
  return L.join('\n');
}

module.exports = { summarize, report, short };
