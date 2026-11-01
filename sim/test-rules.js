const E = require('./engine'); const M = require('./moves');
const { C } = E.loadCards(require('path').join(__dirname, '..'));
const id = (n) => Object.values(C).find((c) => c.name === n || c.fname === n).id;
let fails = 0; const ok = (c, msg) => { if (!c) { fails++; console.log('FAIL', msg); } else console.log('ok  ', msg); };
function st(a, b) { return E.newState(a.map(id), b.map(id), 0); }
function put(s, P, name, w, cell) { M.applyMove(s, P, { id: id(name), face: 'perm', w, cell }); return Object.values(s.inst).find(i => C[i.card].name === name && i.owner === P); }
// 1 sets
let s = st(['Ocean', 'Caldera Lake', 'Stone Towers'], ['Core']);
let a = put(s, 0, 'Ocean', 'new', 0); put(s, 0, 'Caldera Lake', a.w, 1); put(s, 0, 'Stone Towers', a.w, 2);
ok(E.score(s)[0].pts === 1, 'Ocean + Caldera Lake + Stone Towers = 1 set');
// 2 four pinnacles style: Core(F4) + Ocean(W4) + Stone Towers*... use Haze any
// 3 Ice Sheet zeroes fire for both
s = st(['Ice Sheet', 'Hot Spring', 'Desert', 'Stone Towers'], ['Volcano', 'Cloud Forest']);
a = put(s, 0, 'Hot Spring', 'new', 0); put(s, 0, 'Desert', a.w, 1); put(s, 0, 'Stone Towers', a.w, 2);
ok(E.score(s)[0].pts === 1, 'Hot Spring + Desert + Stone Towers = 1 set');
put(s, 0, 'Ice Sheet', 'new', 0);
ok(E.score(s)[0].pts === 0, 'Ice Sheet stops the fire, set gone');
// 4 removal splits an L
s = st(['Ledge', 'Spire', 'Peak'], ['Volcano']);
a = put(s, 0, 'Ledge', 'new', 0); const b = put(s, 0, 'Spire', a.w, 1); put(s, 0, 'Peak', a.w, 2);
M.applyMove(s, 1, { id: id('Eruption'), face: 'force', t: a.id });
ok(Object.keys(s.worlds).length === 2, 'removing the corner of an L leaves two worlds');
// 5 Thicket protects touching
s = st(['Thicket', 'Hill'], ['Volcano']);
a = put(s, 0, 'Thicket', 'new', 0); const h = put(s, 0, 'Hill', a.w, 1);
ok(!E.canRemove(s, h, 'B'), 'Thicket protects a touching card');
ok(E.canRemove(s, a, 'B'), 'Thicket itself can be removed');
// 6 Archipelago alt win with Mirage copying Ocean
s = st(['Ocean', 'Archipelago', 'Mirage'], ['Core']);
a = put(s, 0, 'Ocean', 'new', 0); put(s, 0, 'Archipelago', a.w, 1); put(s, 0, 'Mirage', a.w, 2);
const sc = E.score(s)[0];
ok(sc.water === 10 && sc.alt, 'Ocean + Archipelago + Mirage (copying Ocean) = 10 water, alt win (water ' + sc.water + ')');
// 7 Hanging Valley doubles air in ties
s = st(['Hanging Valley', 'Spire'], ['Core']);
a = put(s, 0, 'Hanging Valley', 'new', 0); put(s, 0, 'Spire', 'new', 0);
ok(E.score(s)[0].tie === 4, 'Hanging Valley: 2 air count 4 in ties');
// 8 Mountain Range
s = st(['Mountain Range', 'Volcano', 'Bedrock', 'Meadow'], ['Core']);
a = put(s, 0, 'Mountain Range', 'new', 0); put(s, 0, 'Volcano', a.w, 1); put(s, 0, 'Bedrock', 'new', 0); put(s, 0, 'Meadow', 'new', 0);
ok(E.score(s)[0].mtn === 1, 'Mountain Range: 4 earth = 1 point');
// 9 Bedrock vs Collapse; Shelter
s = st(['Bedrock'], ['Caldera Lake']); a = put(s, 0, 'Bedrock', 'new', 0);
ok(!E.canRemove(s, a, 'A'), 'forces cannot remove Bedrock');
// 10 Cave ignores common forces: Brushfire can't target
s = st(['Cave'], ['Cinder Field']); a = put(s, 0, 'Cave', 'new', 0);
ok(!M.genMoves(s, 1).some(m => m.face === 'force' && C[m.id].fname === 'Brushfire' && m.t === a.id), 'Brushfire cannot target Cave');
// 11 Solar Flare spares multi-affinity
s = st(['Ledge', 'Delta'], ['Core']); put(s, 0, 'Ledge', 'new', 0); put(s, 0, 'Delta', 'new', 0);
M.applyMove(s, 1, { id: id('Solar Flare'), face: 'force' });
ok(E.perms(s).length === 1 && C[E.perms(s)[0].card].name === 'Delta', 'Solar Flare removes one-affinity cards only');
// 12 either-or chooses
s = st(['Flint', 'Hot Spring', 'Sea Cliff'], ['Core']);
a = put(s, 0, 'Flint', 'new', 0); put(s, 0, 'Hot Spring', a.w, 1); put(s, 0, 'Sea Cliff', a.w, 2);
ok(E.score(s)[0].pts === 1, 'Flint as fire or earth completes a set');
// 13 Glacier turns earth to water
s = st(['Glacier'], ['Volcano', 'Hot Spring', 'Desert']);
a = put(s, 1, 'Volcano', 'new', 0); put(s, 1, 'Cloud Forest' in {} ? 'x' : 'Hot Spring', a.w, 1);
M.applyMove(s, 0, { id: id('Glacier'), face: 'sit', t: a.id });
const v = E.cardView(s, a, false); ok(v.opts[0].join() === '1,2', 'Glacier: Volcano becomes fire + water (' + v.opts[0] + ')');
console.log(fails ? fails + ' FAILED' : 'all passed');
