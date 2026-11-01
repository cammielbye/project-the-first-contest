// The shared table, as plain data, and every change that can happen to it.
//
// Nothing here enforces the game's rules. Like Cockatrice, the page only
// knows where each card is; players apply card effects by moving cards.
// Each player's binder is NOT in this state: it lives only in that
// player's own browser, so the other player never receives it.
//
// apply(state, action, cardsById) returns { state, effects } without
// touching the input. Effects are things a player's own browser must do to
// its private binder (a card returned to it, or a reset).

export const SEATS = ["p1", "p2"];
export const GRID = { cols: 8, rows: 3 };
export const COUNTERS = ["worldPoints", "roundsWon"];
const LOG_LIMIT = 500;

export const other = (seat) => (seat === "p1" ? "p2" : "p1");
export const cellKey = (row, col) => `${row},${col}`;

export function initialState(names = {}) {
  const player = (seat, fallback) => ({
    name: names[seat] || fallback,
    binderChosen: false,
    binderCount: 0,
    worldPoints: 0,
    roundsWon: 0,
    passed: false,
  });
  return {
    v: 3,
    seq: 0,
    round: 1,
    turn: null,
    players: { p1: player("p1", "Player 1"), p2: player("p2", "Player 2") },
    table: { p1: {}, p2: {} },
    voids: { p1: [], p2: [] },
    log: [],
  };
}

export function faceName(inst, cardsById) {
  const card = cardsById.get(inst.id);
  if (!card) return `card ${inst.id}`;
  if (card.meta) return card.meta.name;
  if (inst.face === "force") return card.force ? card.force.name : `${card.permanence.name} (force face)`;
  return card.permanence.name;
}

const FACES = ["permanence", "force", "meta"];

export function findInst(state, iid) {
  for (const area of SEATS) {
    for (const [key, stack] of Object.entries(state.table[area])) {
      const index = stack.findIndex((c) => c.iid === iid);
      if (index !== -1) return { where: "table", area, key, index, inst: stack[index] };
    }
  }
  for (const seat of SEATS) {
    const index = state.voids[seat].findIndex((c) => c.iid === iid);
    if (index !== -1) return { where: "void", seat, index, inst: state.voids[seat][index] };
  }
  return null;
}

function removeAt(state, loc) {
  if (loc.where === "table") {
    const stack = state.table[loc.area][loc.key];
    const [inst] = stack.splice(loc.index, 1);
    if (stack.length === 0) delete state.table[loc.area][loc.key];
    return inst;
  }
  const [inst] = state.voids[loc.seat].splice(loc.index, 1);
  return inst;
}

function validCell(to) {
  if (!to || !SEATS.includes(to.area) || typeof to.key !== "string") return false;
  const m = to.key.match(/^(\d+),(\d+)$/);
  if (!m) return false;
  const r = Number(m[1]);
  const c = Number(m[2]);
  return r >= 0 && r < GRID.rows && c >= 0 && c < GRID.cols;
}

function validInst(inst) {
  return (
    inst &&
    typeof inst.iid === "string" &&
    typeof inst.id === "string" &&
    FACES.includes(inst.face) &&
    SEATS.includes(inst.owner)
  );
}

export function apply(prev, action, cardsById) {
  const state = structuredClone(prev);
  const effects = [];
  const seat = action && SEATS.includes(action.seat) ? action.seat : null;
  if (!seat) return { state: prev, effects };

  const name = (s) => state.players[s].name;
  const label = (inst) => `${faceName(inst, cardsById)} (${inst.face})`;
  const log = (text) => {
    state.seq += 1;
    state.log.push({ n: state.seq, seat, text });
    if (state.log.length > LOG_LIMIT) state.log.splice(0, state.log.length - LOG_LIMIT);
  };
  const where = (to) => {
    const stack = state.table[to.area][to.key];
    const under = stack && stack.length ? stack[stack.length - 1] : null;
    return under
      ? `on ${faceName(under, cardsById)} in ${name(to.area)}'s area`
      : `into ${name(to.area)}'s area`;
  };
  const put = (inst, to) => {
    (state.table[to.area][to.key] ||= []).push(inst);
  };

  switch (action.type) {
    case "setName": {
      const n = String(action.name || "").trim().slice(0, 24);
      if (!n || n === name(seat)) return { state: prev, effects };
      const old = name(seat);
      state.players[seat].name = n;
      log(`${old} is now ${n}.`);
      break;
    }

    case "chooseBinder": {
      const count = Math.max(0, Math.min(200, Number(action.count) || 0));
      state.players[seat].binderChosen = true;
      state.players[seat].binderCount = count;
      log(`${name(seat)} chose a binder (${count} cards).`);
      break;
    }

    case "place": {
      // From the acting player's own binder onto the table.
      const inst = action.inst;
      if (!validInst(inst) || inst.owner !== seat || !validCell(action.to)) return { state: prev, effects };
      if (findInst(state, inst.iid)) return { state: prev, effects };
      const text = `${name(seat)} played ${label(inst)} ${where(action.to)}.`;
      put({ iid: inst.iid, id: inst.id, face: inst.face, owner: inst.owner, original: !!inst.original }, action.to);
      state.players[seat].binderCount = Math.max(0, state.players[seat].binderCount - 1);
      log(text);
      break;
    }

    case "move": {
      if (!validCell(action.to)) return { state: prev, effects };
      const loc = findInst(state, action.iid);
      if (!loc) return { state: prev, effects };
      if (loc.where === "table" && loc.area === action.to.area && loc.key === action.to.key) {
        return { state: prev, effects };
      }
      const inst = removeAt(state, loc);
      const from =
        loc.where === "void" ? ` from ${name(loc.seat)}'s void` : loc.area !== action.to.area ? ` from ${name(loc.area)}'s area` : "";
      const text = `${name(seat)} moved ${label(inst)}${from} ${where(action.to)}.`;
      put(inst, action.to);
      log(text);
      break;
    }

    case "flip": {
      const loc = findInst(state, action.iid);
      if (!loc) return { state: prev, effects };
      if (loc.inst.face === "meta") return { state: prev, effects };
      const before = faceName(loc.inst, cardsById);
      loc.inst.face = loc.inst.face === "force" ? "permanence" : "force";
      log(`${name(seat)} flipped ${before} to ${faceName(loc.inst, cardsById)}.`);
      break;
    }

    case "toVoid": {
      const loc = findInst(state, action.iid);
      if (!loc || loc.where === "void") return { state: prev, effects };
      const inst = removeAt(state, loc);
      state.voids[inst.owner].push(inst);
      log(`${name(seat)} sent ${label(inst)} to ${name(inst.owner)}'s void.`);
      break;
    }

    case "toBinder": {
      const loc = findInst(state, action.iid);
      if (!loc) return { state: prev, effects };
      const inst = removeAt(state, loc);
      state.players[inst.owner].binderCount += 1;
      effects.push({ kind: "toBinder", seat: inst.owner, inst });
      log(`${name(seat)} returned ${label(inst)} to ${name(inst.owner)}'s binder.`);
      break;
    }

    case "counter": {
      const target = SEATS.includes(action.target) ? action.target : null;
      if (!target || !COUNTERS.includes(action.field)) return { state: prev, effects };
      const delta = Math.sign(Number(action.delta) || 0);
      const p = state.players[target];
      const next = Math.max(0, Math.min(99, p[action.field] + delta));
      if (next === p[action.field]) return { state: prev, effects };
      p[action.field] = next;
      const what = action.field === "worldPoints" ? "world points" : "rounds won";
      log(`${name(seat)} set ${name(target)}'s ${what} to ${next}.`);
      break;
    }

    case "round": {
      const delta = Math.sign(Number(action.delta) || 0);
      const next = Math.max(1, Math.min(9, state.round + delta));
      if (next === state.round) return { state: prev, effects };
      state.round = next;
      for (const s of SEATS) state.players[s].passed = false;
      log(`${name(seat)} set the round to ${next}.`);
      break;
    }

    case "endTurn": {
      state.turn = other(seat);
      log(`${name(seat)} ended their turn. ${name(other(seat))} to play.`);
      break;
    }

    case "pass": {
      state.players[seat].passed = true;
      state.turn = other(seat);
      log(`${name(seat)} passed.`);
      break;
    }

    case "opener": {
      const pick = SEATS.includes(action.pick) ? action.pick : null;
      if (!pick) return { state: prev, effects };
      state.turn = pick;
      log(`${name(pick)} opens (picked at random by ${name(seat)}).`);
      break;
    }

    case "reset": {
      const fresh = initialState({ p1: name("p1"), p2: name("p2") });
      fresh.seq = state.seq;
      fresh.log = [];
      Object.assign(state, fresh);
      effects.push({ kind: "clearPrivate" });
      log(`${name(seat)} reset the game.`);
      break;
    }

    default:
      return { state: prev, effects };
  }

  return { state, effects };
}
