// One contest: best of three rounds, alternating turns, Gwent-style passing, cap 10.
'use strict';
const E = require('./engine');
const M = require('./moves');
const C = () => E.C;

function rngOf(seed) { // mulberry32
  let a = seed >>> 0;
  return () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}

function describe(s, P, m) {
  const d = C()[m.id];
  if (m.face === 'meta') return d.name + (m.echo ? ' → ' + C()[m.echo.id].name : '');
  if (m.face === 'force') return d.fname;
  return d.name;
}

function endRound(s) {
  for (const k of Object.keys(s.inst)) {
    const i = s.inst[k]; if (!i) continue;
    const name = C()[i.card].name;
    if (i.kind === 'perm' && name === 'Petrified Forest' && i.keep === 0) { i.keep = 1; continue; } // READING: one extra round
    delete s.inst[k];
    if (i.kind === 'perm') { const w = s.worlds[i.w]; if (w) w.cells[i.cell] = null; }
    const back = i.kind === 'perm' && (name === 'Spring' || name === 'Grove');
    E.sendTo(s, i, back ? 'binder' : 'void');
  }
  for (const wid of Object.keys(s.worlds)) E.fixWorld(s, wid);
  for (const pl of s.p) { pl.played = 0; pl.passed = false; pl.skip = false; pl.last = null; }
}

// ais: [ai0, ai1]; returns a record of the whole contest
function playContest(binders, ais, opts) {
  const rng = opts.rng;
  const opener0 = rng() < 0.5 ? 0 : 1;
  const s = E.newState(binders[0], binders[1], opener0);
  const rec = { opener: opener0, rounds: [], plays: [], winner: null };
  for (let r = 1; r <= 3; r++) {
    s.r = r;
    s.turn = s.opener;
    const R = { r, opener: s.opener, plays: [[], []], passOrder: [], turns: 0 };
    let guard = 0;
    while (!(s.p[0].passed && s.p[1].passed)) {
      if (++guard > 200) throw new Error('round did not end');
      const P = s.turn, pl = s.p[P];
      if (!pl.passed) {
        if (pl.skip) { pl.skip = false; R.plays[P].push({ skip: true }); }
        else {
          let n = 1, verge = false;
          while (n-- > 0) {
            const m = ais[P].choose(s, P);
            if (!m) {
              if (!verge) { pl.passed = true; R.passOrder.push({ P, after: pl.played, oppPassed: s.p[1 - P].passed, standing: E.outcome(E.score(s), P) }); }
              break;
            }
            const before = E.score(s);
            const ev = M.applyMove(s, P, m);
            const after = E.score(s);
            R.plays[P].push({ id: m.id, face: m.face, name: describe(s, P, m), echo: m.echo ? m.echo.id : null, ev,
              target: m.t ? 'x' : null, dPts: [after[0].pts - before[0].pts, after[1].pts - before[1].pts] });
            // READING: Verge gives up to two more plays, each counting toward the cap
            if (m.face === 'meta' && C()[m.id].name === 'Verge') { n = Math.min(2, s.cap - pl.played); verge = true; }
            if (pl.played >= s.cap) break;
          }
        }
      }
      R.turns++;
      s.turn = 1 - P;
    }
    const sc = E.score(s);
    const out = E.outcome(sc, 0);
    R.score = sc.map((x) => ({ pts: x.pts, tie: x.tie, alt: x.alt, mtn: x.mtn, worlds: x.worlds.map((w) => ({ cards: w.cards, k: w.k })) }));
    R.winner = out === 1 ? 0 : out === -1 ? 1 : null;
    R.byTie = out !== 0 && sc[0].pts === sc[1].pts && !sc[0].alt && !sc[1].alt;
    R.byAlt = sc[0].alt || sc[1].alt;
    R.ice = !!E.anyPerm(s, 'Ice Sheet');
    R.table = Object.values(s.inst).map((i) => ({ owner: i.owner, kind: i.kind, card: i.card }));
    if (out === 1) s.p[0].wins++; else if (out === -1) s.p[1].wins++; else { s.p[0].wins++; s.p[1].wins++; } // READING: a drawn round counts for both (Gwent)
    R.wins = [s.p[0].wins, s.p[1].wins];
    rec.rounds.push(R);
    endRound(s);
    s.opener = 1 - s.opener; // READING: openers alternate
    if (s.p[0].wins >= 2 || s.p[1].wins >= 2) break;
  }
  const [a, b] = [s.p[0].wins, s.p[1].wins];
  rec.winner = a > b ? 0 : b > a ? 1 : null;
  rec.binderLeft = [s.p[0].binder.length, s.p[1].binder.length];
  return rec;
}

module.exports = { playContest, rngOf };
