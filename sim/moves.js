// Legal moves and how they change the table.
'use strict';
const E = require('./engine');
const { ADJ } = E;
const C = () => E.C;

function removeOne(arr, id) { const k = arr.indexOf(id); if (k >= 0) arr.splice(k, 1); return k >= 0; }
function connected(cells) {
  if (cells.length <= 1) return true;
  const set = new Set(cells); const seen = new Set([cells[0]]); const st = [cells[0]];
  while (st.length) { const c = st.pop(); for (const a of ADJ[c]) if (set.has(a) && !seen.has(a)) { seen.add(a); st.push(a); } }
  return seen.size === cells.length;
}
function partitions(w) { // splits of a world into two connected parts; part = cells that leave
  const occ = []; for (let c = 0; c < 4; c++) if (w.cells[c] !== null) occ.push(c);
  const out = []; const n = occ.length;
  for (let mask = 1; mask < (1 << n) - 1; mask++) {
    if (mask & 1) continue; // the part holding the first card keeps the world
    const a = [], b = [];
    for (let k = 0; k < n; k++) (mask & (1 << k) ? b : a).push(occ[k]);
    if (connected(a) && connected(b)) out.push(b);
  }
  return out;
}

const SIT_RULE = {
  Snowfield: (i) => E.oneAff(i.card) && (C()[i.card].aff[0] & 4),
  Glacier: (i) => C()[i.card].aff.some((t) => t & 8),
  'Salt Flat': (i) => E.oneAff(i.card),
};

function placements(s, P, id, out, wrap) {
  const name = C()[id].name;
  const push = (m) => out.push(wrap ? wrap(m) : m);
  if (SIT_RULE[name]) {
    for (const i of E.perms(s)) if (SIT_RULE[name](i)) push({ id, face: 'sit', t: i.id });
    return;
  }
  push({ id, face: 'perm', w: 'new', cell: 0 });
  for (const w of E.worldsOf(s, P)) {
    if (!E.canGrow(s, w)) continue;
    for (const cell of E.openCells(w)) push({ id, face: 'perm', w: w.id, cell });
  }
}

function forceMoves(s, P, id, out) {
  const d = C()[id]; const rar = d.rarity; const f = d.fname;
  const all = E.perms(s);
  const targ = all.filter((i) => E.forceReaches(s, i, rar));
  const one = targ.filter((i) => E.oneAff(i.card));
  const worlds = Object.values(s.worlds).filter((w) => E.forceReachesWorld(s, w.id, rar));
  const push = (m) => out.push(Object.assign({ id, face: 'force' }, m));
  const sitters = Object.values(s.inst).filter((i) => i.kind === 'sit' || (i.kind === 'force' && i.on));
  const moveTargets = (list, sameOwnerOnly) => {
    for (const i of list) {
      if (!E.canMove(s, i, rar)) continue;
      if (sameOwnerOnly !== undefined && i.owner !== sameOwnerOnly) continue;
      for (const w2 of E.worldsOf(s, i.owner)) {
        if (w2.id === i.w || !E.canGrow(s, w2)) continue;
        for (const cell of E.openCells(w2)) push({ t: i.id, w2: w2.id, cell });
      }
    }
  };
  const pairs = (list, ok) => {
    for (let a = 0; a < list.length; a++) for (let b = a + 1; b < list.length; b++) if (ok(list[a], list[b])) push({ t: list[a].id, t2: list[b].id });
  };
  const touchPair = (a, b) => a.w === b.w && ADJ[a.cell].includes(b.cell);
  switch (f) {
    case 'Brushfire': case 'Spark': case 'Shimmer': case 'Drizzle': case 'Rain': case 'Breeze': case 'Landslide': case 'Bloom': case 'Lichen':
      for (const i of one) push({ t: i.id }); break;
    case 'Downdraft':
      for (const i of one) if (C()[i.card].aff[0] & 4) push({ t: i.id }); break;
    case 'Heatwave': case 'Drought': case 'Rockslide': case 'Updraft': case 'Haze': case 'Shelter':
      for (const i of targ) push({ t: i.id }); break;
    case 'Steam Burst':
      pairs(targ, (a, b) => {
        if (!touchPair(a, b)) return false;
        const ma = C()[a.card].aff.reduce((x, y) => x | y, 0), mb = C()[b.card].aff.reduce((x, y) => x | y, 0);
        return ((ma & 1) && (mb & 2)) || ((ma & 2) && (mb & 1));
      }); break;
    case 'Deluge': case 'Rising Sea': case 'Smoke': case 'Fog': case 'Freeze': case 'Tangle': case 'Uplift':
      for (const w of worlds) push({ w: w.id }); break;
    case 'Mire':
      for (const w of worlds) if (E.worldSize(w) === 2) push({ w: w.id }); break;
    case 'Overgrowth':
      for (const w of worlds) if (w.owner === P) push({ w: w.id }); break;
    case 'Blizzard':
      for (const w of worlds) push({ w: w.id }); break;
    case 'Erosion':
      for (const w of worlds) if (E.worldSize(w) >= 2) for (const part of partitions(w)) push({ w: w.id, part }); break;
    case 'Thaw':
      for (const i of sitters) push({ t: i.id }); break;
    case 'Current': moveTargets(targ); break;
    case 'Vortex': moveTargets(one); break;
    case 'Drift': moveTargets(targ, P); break;
    case 'Flood':
      for (const i of targ) push({ t: i.id });
      for (const i of sitters) if (i.kind === 'sit') push({ t: i.id });
      break;
    case 'Gale':
      pairs(targ, (a, b) => a.owner === b.owner && a.w !== b.w && E.canMove(s, a, rar) && E.canMove(s, b, rar)); break;
    case 'Crosswind':
      pairs(one, (a, b) => a.owner === b.owner && a.w !== b.w && E.canMove(s, a, rar) && E.canMove(s, b, rar)); break;
    case 'Vent':
      for (const i of targ) if (i.owner === P) push({ t: i.id }); break;
    case 'Gust':
      for (const i of one) if (E.worldSize(s.worlds[i.w]) >= 2 && E.canMove(s, i, rar)) push({ t: i.id }); break;
    case 'Solar Flare':
      if (all.some((i) => E.oneAff(i.card))) push({}); break;
    case 'Collapse':
      for (const i of all) if (E.canRemove(s, i, rar)) push({ t: i.id });
      for (const i of sitters) push({ t: i.id });
      break;
    case 'Eruption':
      for (const i of one) if (E.canRemove(s, i, rar)) push({ t: i.id }); break;
    case 'Lightning':
      for (const i of one) if (E.worldSize(s.worlds[i.w]) === 1 && E.canRemove(s, i, rar)) push({ t: i.id }); break;
    case 'Avalanche':
      pairs(one, (a, b) => touchPair(a, b) && E.canRemove(s, a, rar) && E.canRemove(s, b, rar)); break;
    default:
      throw new Error('force not implemented: ' + f);
  }
}

function genMoves(s, P) {
  const pl = s.p[P]; const out = []; const opp = s.p[1 - P];
  const done = new Set();
  for (const id of pl.binder) {
    if (done.has(id)) continue; done.add(id);
    const d = C()[id];
    if (d.meta) {
      switch (d.name) {
        case 'Echo': {
          const seen = new Set();
          for (const v of pl.void) if (!seen.has(v) && C()[v].aff && E.oneAff(v)) { seen.add(v); placements(s, P, v, out, (m) => ({ id, face: 'meta', echo: m })); }
          break;
        }
        case 'Ebb': { const i = opp.last && s.inst[opp.last]; if (i && E.canRemove(s, i, null)) out.push({ id, face: 'meta' }); break; }
        case 'Lull': if (!opp.passed) out.push({ id, face: 'meta' }); break;
        case 'Horizon': out.push({ id, face: 'meta' }); break;
        case 'Verge': if (pl.played + 1 < s.cap) out.push({ id, face: 'meta' }); break;
        default: throw new Error('meta not implemented: ' + d.name);
      }
      continue;
    }
    placements(s, P, id, out);
    forceMoves(s, P, id, out);
  }
  return out;
}

function applyPlacement(s, P, m) {
  const pl = s.p[P];
  if (m.face === 'sit') { const i = E.newInst(s, P, m.id, 'sit', { on: m.t }); pl.last = i.id; return i; }
  const i = E.newInst(s, P, m.id, 'perm');
  const w = m.w === 'new' ? E.newWorld(s, P) : s.worlds[m.w];
  E.place(s, i, w, m.w === 'new' ? 0 : m.cell);
  pl.last = i.id;
  return i;
}

// returns a short record of what happened (for stats)
function applyMove(s, P, m) {
  const pl = s.p[P]; const opp = s.p[1 - P];
  removeOne(pl.binder, m.id);
  pl.played++;
  const ev = { removed: [], returned: [] };
  if (m.face === 'perm' || m.face === 'sit') { applyPlacement(s, P, m); return ev; }
  if (m.face === 'meta') {
    const name = C()[m.id].name;
    pl.void.push(m.id);
    // READING: Echo's card from the void comes in as part of the same play
    if (name === 'Echo') { removeOne(pl.void, m.echo.id); applyPlacement(s, P, m.echo); }
    else if (name === 'Ebb') { const i = s.inst[opp.last]; ev.removed.push(i.card); E.leave(s, i, 'void'); }
    else if (name === 'Lull') opp.skip = true;
    return ev;
  }
  // force face
  const d = C()[m.id]; const f = d.fname; const rar = d.rarity;
  if (d.fdur === 'round') {
    const i = E.newInst(s, P, m.id, 'force', { on: m.t || null, on2: m.t2 || null, onW: m.w || null });
    pl.last = i.id;
    return ev;
  }
  pl.last = null;
  pl.void.push(m.id);
  const gone = (iid, where) => { const i = s.inst[iid]; if (!i) return; (where === 'void' ? ev.removed : ev.returned).push(i.card); E.leave(s, i, where); };
  switch (f) {
    case 'Blizzard': { const w = s.worlds[m.w]; for (const iid of w.cells.slice()) if (iid !== null) gone(iid, 'binder'); break; }
    case 'Erosion': {
      const w = s.worlds[m.w]; const nw = E.newWorld(s, w.owner);
      for (const c of m.part) { const iid = w.cells[c]; nw.cells[c] = iid; w.cells[c] = null; s.inst[iid].w = nw.id; }
      break;
    }
    case 'Thaw': case 'Collapse': case 'Eruption': case 'Lightning': gone(m.t, 'void'); break;
    case 'Avalanche': gone(m.t, 'void'); gone(m.t2, 'void'); break;
    case 'Flood': case 'Vent': gone(m.t, 'binder'); break; // READING: returning isn't removal, so protections don't stop it
    case 'Current': case 'Vortex': case 'Drift': E.moveTo(s, s.inst[m.t], s.worlds[m.w2], m.cell); break;
    case 'Gale': case 'Crosswind': {
      const a = s.inst[m.t], b = s.inst[m.t2]; const wa = s.worlds[a.w], wb = s.worlds[b.w]; const ca = a.cell, cb = b.cell;
      wa.cells[ca] = b.id; wb.cells[cb] = a.id; a.w = wb.id; a.cell = cb; b.w = wa.id; b.cell = ca;
      break;
    }
    case 'Gust': {
      const i = s.inst[m.t]; const w1 = s.worlds[i.w]; w1.cells[i.cell] = null;
      const nw = E.newWorld(s, i.owner); E.place(s, i, nw, 0); E.fixWorld(s, w1.id);
      break;
    }
    case 'Solar Flare': {
      const hit = E.perms(s).filter((i) => E.oneAff(i.card) && E.canRemove(s, i, rar)).map((i) => i.id);
      for (const iid of hit) gone(iid, 'void');
      break;
    }
    default: throw new Error('once force not implemented: ' + f);
  }
  return ev;
}

module.exports = { genMoves, applyMove, partitions };
