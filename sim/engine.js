// The First Contest: rules engine for the current loop (world points), second-pass cards.
// Readings of open rules are marked READING.
'use strict';
const fs = require('fs');

const EL = ['fire', 'water', 'air', 'earth'];
const BIT = { fire: 1, water: 2, air: 4, earth: 8 };
const ANY = 15;
const POP = [0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4];
const ADJ = [[1, 2], [0, 3], [0, 3], [1, 2]]; // 2x2 cells: 0 1 / 2 3 ; diagonals don't touch
const RAR = { C: 0, B: 1, A: 2, S: 3 };

function maskOf(tok) {
  if (tok === 'any') return ANY;
  if (tok.includes('|')) return tok.split('|').reduce((m, e) => m | BIT[e], 0);
  return BIT[tok];
}

let C = {};
function loadCards(repo) {
  const cards = JSON.parse(fs.readFileSync(repo + '/data/cards.json', 'utf8')).cards;
  const binders = JSON.parse(fs.readFileSync(repo + '/data/binders.json', 'utf8')).binders;
  C = {};
  for (const c of cards) {
    if (c.meta) C[c.id] = { id: c.id, meta: true, name: c.meta.name, rarity: c.rarity, text: c.meta.text };
    else C[c.id] = {
      id: c.id, no: c.no, name: c.permanence.name, rarity: c.rarity, aff: c.permanence.affinities.map(maskOf),
      ptext: c.permanence.text, fname: c.force.name, fdur: /once/i.test(c.force.duration) ? 'once' : 'round', ftext: c.force.text,
    };
  }
  return { C, binders };
}
const card = (id) => C[id];
const oneAff = (id) => C[id].aff && C[id].aff.length === 1;

// ---------- state ----------
function newPlayer(ids) {
  return { binder: ids.slice(), void: [], played: 0, passed: false, skip: false, wins: 0, last: null };
}
function newState(idsA, idsB, opener) {
  return { r: 1, cap: 10, turn: opener, opener, p: [newPlayer(idsA), newPlayer(idsB)], inst: {}, worlds: {}, nid: 1, ts: 1 };
}
function clone(s) {
  const inst = {};
  for (const k in s.inst) inst[k] = Object.assign({}, s.inst[k]);
  const worlds = {};
  for (const k in s.worlds) { const w = s.worlds[k]; worlds[k] = { id: w.id, owner: w.owner, cells: w.cells.slice() }; }
  return {
    r: s.r, cap: s.cap, turn: s.turn, opener: s.opener, nid: s.nid, ts: s.ts, inst, worlds,
    p: s.p.map((x) => ({ binder: x.binder.slice(), void: x.void.slice(), played: x.played, passed: x.passed, skip: x.skip, wins: x.wins, last: x.last })),
  };
}

// ---------- queries ----------
function perms(s) { const o = []; for (const k in s.inst) if (s.inst[k].kind === 'perm') o.push(s.inst[k]); return o; }
function worldsOf(s, P) { const o = []; for (const k in s.worlds) if (s.worlds[k].owner === P) o.push(s.worlds[k]); return o; }
function worldSize(w) { let n = 0; for (const c of w.cells) if (c !== null) n++; return n; }
function touching(s, i) { // perm insts orthogonally next to inst i
  const w = s.worlds[i.w]; const o = [];
  for (const c of ADJ[i.cell]) if (w.cells[c] !== null) o.push(s.inst[w.cells[c]]);
  return o;
}
function hasPerm(s, P, name) { for (const k in s.inst) { const i = s.inst[k]; if (i.kind === 'perm' && i.owner === P && C[i.card].name === name) return i; } return null; }
function anyPerm(s, name) { for (const k in s.inst) { const i = s.inst[k]; if (i.kind === 'perm' && C[i.card].name === name) return i; } return null; }
function forceName(i) { return C[i.card].fname; }
function forcesOnWorld(s, wid) { const o = []; for (const k in s.inst) { const i = s.inst[k]; if (i.kind === 'force' && i.onW === wid) o.push(i); } return o; }
function attachedTo(s, iid) { const o = []; for (const k in s.inst) { const i = s.inst[k]; if ((i.kind === 'force' || i.kind === 'sit') && (i.on === iid || i.on2 === iid)) o.push(i); } return o; }

// protection from forces
function worldIgnoresAll(s, wid, exceptIid) {
  for (const f of forcesOnWorld(s, wid)) if (forceName(f) === 'Uplift' && f.id !== exceptIid) return true;
  return false;
}
function worldIgnoresCommon(s, wid) {
  for (const f of forcesOnWorld(s, wid)) if (forceName(f) === 'Overgrowth') return true;
  return false;
}
function ignoresCommon(s, i) {
  const n = C[i.card].name;
  if (n === 'Cave' || n === 'Tide Pool') return true;
  const hv = hasPerm(s, i.owner, 'Hidden Valley');
  if (hv && hv.id !== i.id) return true;
  if (i.w && worldIgnoresCommon(s, i.w)) return true;
  return false;
}
// can a force of this rarity reach this perm (target it, or keep affecting it)
function forceReaches(s, i, rarity, exceptIid) {
  if (worldIgnoresAll(s, i.w, exceptIid)) return false;
  if (rarity === 'C' && ignoresCommon(s, i)) return false;
  return true;
}
function forceReachesWorld(s, wid, rarity, exceptIid) {
  if (worldIgnoresAll(s, wid, exceptIid)) return false;
  if (rarity === 'C' && worldIgnoresCommon(s, wid)) return false;
  return true;
}
function activeOnWorld(s, wid, name) { // a lasting world force that still applies
  for (const f of forcesOnWorld(s, wid)) if (forceName(f) === name && forceReachesWorld(s, wid, C[f.card].rarity, f.id)) return f;
  return null;
}
function activeOnCard(s, i, name) {
  for (const f of attachedTo(s, i.id)) if (f.kind === 'force' && forceName(f) === name && forceReaches(s, i, C[f.card].rarity)) return f;
  return null;
}
// byForce: rarity string of the force, or null for a meta card
function canRemove(s, i, byForce) {
  if (i.kind !== 'perm') return true;
  if (byForce) {
    if (C[i.card].name === 'Bedrock') return false;
    if (!forceReaches(s, i, byForce)) return false;
  }
  if (activeOnCard(s, i, 'Shelter')) return false;
  if (oneAff(i.card) && activeOnWorld(s, i.w, 'Freeze')) return false;
  for (const t of touching(s, i)) if (t.owner === i.owner && C[t.card].name === 'Thicket') return false;
  return true;
}
function canMove(s, i, byForce) {
  if (byForce) {
    if (C[i.card].name === 'Spire') return false;
    if (!forceReaches(s, i, byForce)) return false;
  }
  if (activeOnWorld(s, i.w, 'Tangle')) return false;
  return true;
}
function canGrow(s, w) {
  if (worldSize(w) >= 4) return false;
  if (activeOnWorld(s, w.id, 'Fog')) return false;
  if (activeOnWorld(s, w.id, 'Mire')) return false;
  return true;
}
function openCells(w) { // empty cells touching an occupied cell
  const n = worldSize(w); const o = [];
  if (n === 0) return [0];
  for (let c = 0; c < 4; c++) {
    if (w.cells[c] !== null) continue;
    if (ADJ[c].some((a) => w.cells[a] !== null)) o.push(c);
  }
  if (n === 1 && o.length === 2) return [o[0]]; // the two open cells of a lone card are equivalent
  return o;
}

// ---------- table changes ----------
function newInst(s, P, cardId, kind, extra) {
  const id = 'i' + s.nid++;
  s.inst[id] = Object.assign({ id, card: cardId, owner: P, kind, w: null, cell: null, on: null, on2: null, onW: null, ts: s.ts++, keep: 0 }, extra || {});
  return s.inst[id];
}
function newWorld(s, P) { const id = 'w' + s.nid++; s.worlds[id] = { id, owner: P, cells: [null, null, null, null] }; return s.worlds[id]; }
function sendTo(s, i, where) { // where: 'void' | 'binder'
  const pl = s.p[i.owner];
  if (where === 'binder') pl.binder.push(i.card); else pl.void.push(i.card);
}
function detach(s, i) { // take inst off the table (cascade), returns nothing
  delete s.inst[i.id];
  for (const a of attachedTo(s, i.id)) { delete s.inst[a.id]; sendTo(s, a, 'void'); }
  if (i.kind === 'perm' && i.w) {
    const w = s.worlds[i.w];
    w.cells[i.cell] = null;
    fixWorld(s, w.id);
  }
}
function leave(s, i, where) { detach(s, i); sendTo(s, i, where); }
function fixWorld(s, wid) {
  const w = s.worlds[wid]; if (!w) return;
  const occ = []; for (let c = 0; c < 4; c++) if (w.cells[c] !== null) occ.push(c);
  if (occ.length === 0) {
    delete s.worlds[wid];
    for (const f of forcesOnWorld(s, wid)) { delete s.inst[f.id]; sendTo(s, f, 'void'); }
    return;
  }
  // components
  const seen = new Set(); const comps = [];
  for (const c0 of occ) {
    if (seen.has(c0)) continue;
    const comp = []; const st = [c0]; seen.add(c0);
    while (st.length) { const c = st.pop(); comp.push(c); for (const a of ADJ[c]) if (w.cells[a] !== null && !seen.has(a)) { seen.add(a); st.push(a); } }
    comps.push(comp);
  }
  if (comps.length === 1) return;
  comps.sort((a, b) => b.length - a.length);
  for (let k = 1; k < comps.length; k++) {
    const nw = newWorld(s, w.owner);
    for (const c of comps[k]) { const iid = w.cells[c]; nw.cells[c] = iid; w.cells[c] = null; s.inst[iid].w = nw.id; }
  }
}
function place(s, i, w, cell) { i.w = w.id; i.cell = cell; w.cells[cell] = i.id; }
function moveTo(s, i, w2, cell) {
  const w1 = s.worlds[i.w]; w1.cells[i.cell] = null;
  place(s, i, w2, cell);
  fixWorld(s, w1.id);
}

// ---------- scoring ----------
const SETS_CACHE = new Map();
function feasible(c, flex, need) {
  const d = [0, 0, 0, 0]; let any = false;
  for (let e = 0; e < 4; e++) { d[e] = Math.max(0, need[e] - c[e]); if (d[e]) any = true; }
  if (!any) return true;
  for (let S = 1; S < 16; S++) {
    let sd = 0; for (let e = 0; e < 4; e++) if (S & (1 << e)) sd += d[e];
    if (!sd) continue;
    let cnt = 0; for (const t of flex) if (t & S) cnt++;
    if (cnt < sd) return false;
  }
  return true;
}
// sets and coverage toward the next set
function setsOf(tokens) {
  const key = tokens.slice().sort((a, b) => a - b).join(',');
  const hit = SETS_CACHE.get(key); if (hit) return hit;
  const c = [0, 0, 0, 0]; const flex = [];
  for (const t of tokens) { if (POP[t] === 1) c[Math.log2(t)]++; else if (t) flex.push(t); }
  let k = Math.floor(tokens.length / 4);
  while (k > 0 && !feasible(c, flex, [k, k, k, k])) k--;
  let cov = 0;
  for (let T = 15; T > 0 && cov < 3; T--) {
    const sz = POP[T]; if (sz >= 4 || sz <= cov) continue;
    const need = [0, 1, 2, 3].map((e) => (T & (1 << e) ? k + 1 : k));
    if (feasible(c, flex, need)) cov = sz;
  }
  const r = { k, cov };
  if (SETS_CACHE.size > 200000) SETS_CACHE.clear();
  SETS_CACHE.set(key, r);
  return r;
}

// effective affinity options for a perm: array of token arrays (more than one only for Mirage)
// plus flags. Returns null tokens if it doesn't count.
function cardView(s, i, ice) {
  const def = C[i.card];
  let opts;
  if (def.name === 'Mirage') { // READING: copies the printed affinities of one touching card (best choice)
    opts = [def.aff.slice()];
    for (const t of touching(s, i)) if (C[t.card].name !== 'Mirage') opts.push(C[t.card].aff.slice());
  } else opts = [def.aff.slice()];
  let nocount = false; let tie2 = def.name === 'Ashfield' || def.name === 'Summit';
  const mods = attachedTo(s, i.id).sort((a, b) => a.ts - b.ts);
  for (const m of mods) {
    let eff;
    if (m.kind === 'sit') eff = C[m.card].name; // Snowfield, Glacier, Salt Flat
    else { if (!forceReaches(s, i, C[m.card].rarity)) continue; eff = forceName(m); }
    for (const o of opts) for (let k = 0; k < o.length; k++) {
      switch (eff) {
        case 'Snowfield': case 'Rain': o[k] = BIT.water; break;
        case 'Glacier': if (o[k] & 8) o[k] = (o[k] & ~8) | 2; break; // READING: the target's earth becomes water
        case 'Spark': case 'Drought': o[k] = BIT.fire; break;
        case 'Breeze': case 'Updraft': o[k] = BIT.air; break;
        case 'Landslide': case 'Rockslide': case 'Downdraft': o[k] = BIT.earth; break;
        case 'Shimmer': case 'Haze': o[k] = ANY; break;
        case 'Drizzle': o[k] |= BIT.water; break; // READING: "also counts as" = either element
        case 'Bloom': o[k] |= BIT.earth; break;
        case 'Sea Breeze': o[k] |= BIT.air; break;
      }
    }
    if (eff === 'Salt Flat' || eff === 'Brushfire' || eff === 'Heatwave' || eff === 'Ash Cloud' || eff === 'Steam Burst') nocount = true;
    if (eff === 'Lichen') tie2 = true;
  }
  const w = i.w;
  let tieOut = false;
  if (activeOnWorld(s, w, 'Deluge')) { nocount = true; }
  if (oneAff(i.card)) { const rs = activeOnWorld(s, w, 'Rising Sea'); if (rs) nocount = true; }
  if (activeOnWorld(s, w, 'Smoke') && !(ignoresCommon(s, i))) tieOut = true;
  if (ice) for (const o of opts) for (let k = 0; k < o.length; k++) o[k] &= ~1;
  return { opts: opts.map((o) => o.filter((t) => t)), nocount, tie2, tieOut };
}

// full round view: points, tie value, alt win
function score(s) {
  const ice = !!anyPerm(s, 'Ice Sheet'); // READING: stops fire for both players while in a world
  const res = [0, 1].map(() => ({ pts: 0, tie: 0, water: 0, earth: 0, alt: false, mtn: 0, worlds: [], tot: [0, 0, 0, 0] }));
  const hv = [!!hasPerm(s, 0, 'Hanging Valley'), !!hasPerm(s, 1, 'Hanging Valley')];
  const views = {};
  for (const k in s.worlds) {
    const w = s.worlds[k]; const P = w.owner; const R = res[P];
    const fixed = []; const mirageOpts = [];
    let cards = 0;
    for (const iid of w.cells) {
      if (iid === null) continue; cards++;
      const i = s.inst[iid]; const v = cardView(s, i, ice); views[iid] = v;
      if (v.nocount) continue;
      if (v.opts.length > 1) mirageOpts.push(v.opts); else fixed.push(...v.opts[0]);
      // tie and totals (per element, best option)
      if (!v.tieOut) for (let e = 0; e < 4; e++) {
        let best = 0;
        for (const o of v.opts) { let n = 0; for (const t of o) if (t & (1 << e)) n += (e === 2 && hv[P] ? 2 : 1); best = Math.max(best, n); }
        R.tot[e] += best * (v.tie2 ? 2 : 1);
      }
      let bw = 0, be = 0;
      for (const o of v.opts) { let nw = 0, ne = 0; for (const t of o) { if (t & 2) nw++; if (t & 8) ne++; } bw = Math.max(bw, nw); be = Math.max(be, ne); }
      R.water += bw; R.earth += be;
    }
    let best = { k: 0, cov: 0 };
    if (mirageOpts.length === 0) best = setsOf(fixed);
    else {
      const rec = (j, acc) => {
        if (j === mirageOpts.length) { const r = setsOf(acc); if (r.k > best.k || (r.k === best.k && r.cov > best.cov)) best = r; return; }
        for (const o of mirageOpts[j]) rec(j + 1, acc.concat(o));
      };
      rec(0, fixed);
    }
    R.pts += best.k;
    R.worlds.push({ id: w.id, cards, k: best.k, cov: best.cov });
  }
  // sitting permanence counts toward its owner's affinity only
  for (const k in s.inst) {
    const i = s.inst[k]; if (i.kind !== 'sit') continue;
    for (const t0 of C[i.card].aff) { const t = ice ? t0 & ~1 : t0; for (let e = 0; e < 4; e++) if (t & (1 << e)) res[i.owner].tot[e] += 1; if (t & 2) res[i.owner].water++; if (t & 8) res[i.owner].earth++; }
  }
  for (const P of [0, 1]) {
    const R = res[P];
    R.tie = Math.max(...R.tot);
    if (hasPerm(s, P, 'Mountain Range')) { R.mtn = Math.floor(R.earth / 4); R.pts += R.mtn; }
    if (hasPerm(s, P, 'Archipelago') && R.water >= 10) R.alt = true;
  }
  return res;
}
// +1 P wins, 0 draw, -1 P loses
function outcome(sc, P) {
  const Q = 1 - P; const a = sc[P], b = sc[Q];
  if (a.alt !== b.alt) return a.alt ? 1 : -1;
  if (a.pts !== b.pts) return a.pts > b.pts ? 1 : -1;
  if (a.tie !== b.tie) return a.tie > b.tie ? 1 : -1;
  return 0;
}

module.exports = {
  EL, BIT, ANY, POP, ADJ, RAR, loadCards, card, oneAff, newState, clone, perms, worldsOf, worldSize, touching, hasPerm, anyPerm,
  forceName, forcesOnWorld, attachedTo, ignoresCommon, forceReaches, forceReachesWorld, activeOnWorld, activeOnCard, canRemove, canMove, canGrow,
  openCells, newInst, newWorld, sendTo, detach, leave, fixWorld, place, moveTo, score, outcome, setsOf, cardView,
  get C() { return C; },
};
