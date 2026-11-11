# Fifth pass (Nov 11, 2026): the fourth pass made playable again, at Cam's request.
# Cam: every permanence has a force; effects may repeat (especially on commons, on different elements); fill the gaps from
# the effect idea pool and the feedback so far; readjust the forces he's said he doesn't like; new cards from the idea pool,
# names from the lists, themes and effects loosely tied to their affinity; the cards unique to one element double down on
# their element's effect with a twist (his example: an air return that brings back a card played in a previous round);
# two- and three-pip permanences can stay vanilla or take a restriction ("can only be played on the first turn of a round").
# Everything below is Claude's draft against that brief. Data + checks + markdown; the fourth pass (pass4.py) is the base.
import collections, copy, re, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import pass4
from pass4 import W, E, F, A, ANY, ORDER, aff_cell, HEAD, words

R, O = 'round', 'once'
GROUPS = copy.deepcopy(pass4.GROUPS)
G = {k: cs for k, t, b, cs in GROUPS}
BY = {c['name']: c for k, t, b, cs in GROUPS for c in cs}

# ---------------------------------------------------------------- forces and texts changed on fourth-pass cards
# name: (force, duration, force text, why) ; why tags the change for the notes
FORCES = {
    # one restriction at most (Cam, Nov 8): "with one affinity" dropped where an element already restricts
    'Lava Field': ('Ash', R, 'An earth permanence loses its affinities.', 'one restriction; was Spark, two restrictions and the same as Updraft'),
    'Tide Pool': ('Drizzle', R, 'A fire permanence loses its affinities.', 'one restriction'),
    'Stone Field': ('Dust', R, 'An air permanence loses its affinities.', 'one restriction'),
    'Flint': ('Spark', R, 'An air permanence loses its affinities.', "one restriction; was Sinkhole (a move, with no air on the card); Dust's effect on a second element"),
    'Ledge': ('Gust', O, 'A ◯ permanence becomes its own world.', 'one restriction'),
    'Hot Spring': ('Scald', O, 'Remove a fire or earth permanence.', 'one restriction; the uncommon step of the Nov 2 removal ladder'),
    'Volcano': ('Lava Bomb', O, 'Remove an earth or air permanence.', 'one restriction'),
    'Tidal Flat': ('Hail', O, 'Remove a fire or air permanence.', 'one restriction'),
    'Hidden Valley': ('Landslide', O, 'Remove an air or water permanence.', 'one restriction'),
    'Wind Gap': ('Downdraft', O, 'A fire permanence becomes its own world.', 'one restriction'),
    # removing a world's permanences of one element could hit 3-4 cards (Cam, Nov 8): now two at most
    'Lagoon': ('Flash Flood', O, 'Remove two fire permanences.', "was a world's fire permanences"),
    'Moor': ('Avalanche', O, 'Remove two air permanences.', "was a world's air permanences"),
    'Cinder Field': ('Wildfire', O, 'Remove two earth permanences.', "was a world's earth permanences"),
    'Peak': ('Drought', O, 'Remove two water permanences.', "was a world's water permanences"),
    # returns: the weakest forces in the Nov 8 sim; air's twist (Cam's example) on the one that wasn't on a water card
    'High Desert': ('Tornado', O, 'Return two cards you played last round.', "air's twist on returning (Cam's example); was \"Return two permanences.\""),
    # cards that had no force
    'Mountain Range': ('Rockslide', R, 'An air permanence becomes earth.', "new; Rockfall's effect on a second card"),
    'Red Canyon': ('Erosion', R, 'Two permanences lose their affinities.', 'new'),
    'Archipelago': ('Surge', O, 'Return a permanence and its adjacent permanences.', 'new'),
    'Boiling Lake': ('Torrent', O, 'Return two fire permanences.', 'new'),
    'Lava Plain': ('Magma', O, 'Remove two adjacent permanences.', 'new'),
    'Sand Sea': ('Supercell', O, 'Remove two lone permanences.', 'new'),
    # pinnacles: Tsunami and Firestorm too weak (Cam, Nov 10); World Quake read the same as Jet Stream; Origin had none
    'Ocean': ('Tsunami', O, "Return a player's worlds.", 'too weak before (Cam, Nov 10)'),
    'Core': ('Firestorm', O, 'Remove a world.', 'too weak before (Cam, Nov 10)'),
    'Pangaea': ('World Quake', O, 'Split every world.', 'read the same as Jet Stream'),
    'Origin': ('Unmaking', O, 'Remove every world.', "Origin's third-pass force, back (Cam, Nov 2: \"Unmaking and Origin are great\")"),
}
TEXTS = {
    # restrictions on three-pip permanences (Cam: "in some cases it might even make sense to put a restriction on them")
    'Lagoon': 'Play only on your first turn.', 'Moor': 'Play only on your first turn.',
    'Cinder Field': 'Play only on your first turn.', 'Peak': 'Play only on your first turn.',
    'Caldera Lake': 'Play only on a new world.', 'Rainforest': 'Play only on a new world.',
    'Geyser Basin': 'Play only on a new world.', 'Red Canyon': 'Play only on a new world.',
    # Hanging Valley's +1 world point does nothing since a world scores one point at most (Nov 10)
    'Hanging Valley': 'Its world scores with one pip fewer.',
}
CHANGED = {}
for n, (f, d, t, why) in FORCES.items():
    c = BY[n]; CHANGED[n] = ['force: ' + why]
    c.update(force=f, duration=d, force_text=t)
for n, t in TEXTS.items():
    c = BY[n]; CHANGED.setdefault(n, []).append('text: ' + ('restriction, new' if t.startswith('Play only') else 'was "%s"' % c['text']))
    c['text'] = t

# ---------------------------------------------------------------- the slots unique to one element, filled
def new(no, name, rar, affs, text, force, dur, ftext, note):
    return dict(no=no, name=name, rarity=rar, affinities=affs, text=text, how='new', note=note, force=force, duration=dur, force_text=ftext)
# positional permanences (idea 11, Cam Nov 11), each element its own direction in the 2x2: water flows down, air rises,
# fire spreads sideways, earth reaches across
POSITIONAL = [
    new(84, 'Shoal', 'C', [W], 'The permanence below this gains water.', 'Mist', R, 'An air permanence becomes water.', 'positional (idea 11)'),
    new(87, 'Meadow', 'C', [E], 'The permanence across from this gains earth.', 'Mudslide', R, 'A fire permanence becomes earth.', 'positional (idea 11)'),
    new(90, 'Barrens', 'C', [F], 'The permanence beside this gains fire.', 'Smoke', R, 'A water permanence loses its affinities.', 'positional (idea 11)'),
    new(93, 'Ridge', 'C', [A], 'The permanence above this gains air.', 'Breeze', R, 'A water permanence becomes air.', 'positional (idea 11)'),
]
# each element's own effect, doubled down with a twist no other element gets
TWISTS = [
    new(85, 'Fen', 'B', [W, E], '', 'Whirlpool', O, 'Play a card from a void.', "water's twist on returning: from either void (idea 12)"),
    new(88, 'Cavern', 'C', [E], "Its world can't be split.", 'Sinkhole', R, "A world can't lose permanences.", "earth's twist on holding (permanence: idea 9)"),
    new(91, 'Crater', 'B', [E, F], '', 'Meteor', O, 'Remove a permanence played last turn.', "fire's twist on removing"),
    new(94, 'Eyrie', 'C', [A], '', 'Cyclone', O, 'Return a card you played last round.', "air's twist on returning (Cam's example)"),
]
GROUPS.append(('u-pos', 'Unique to one element: positional', "Cam (Nov 11): positional conditions and buffs (idea 11). In a 2×2 world each card has one card beside it, one above or below it, and one across the diagonal; each element gets its own direction, so no two are the same effect.", POSITIONAL))
GROUPS.append(('u-twist', "Unique to one element: the element's effect, twisted", "Cam (Nov 11): the cards unique to one element lean into the effect and element relationship and double down, with an unusual twist on an existing mechanic left unique to that element; his example was an air return that brings back a card played in a previous round.", TWISTS))
G = {k: cs for k, t, b, cs in GROUPS}

# ---------------------------------------------------------------- meta cards: the eight, plus six new ones
META = list(pass4.META)
META_NO = dict(pass4.META_NO)
NEW_META = [
    (77, 'Aftershock', 'Your opponent takes the next two turns.', 'idea 6 (Cam, Nov 10)'),
    (78, 'Stillness', 'Your opponent passes.', "Gwent's passing, forced"),
    (79, 'Sunlight', 'Remove every force.', 'idea 5 (Cam, Nov 9)'),
    (80, 'Weathering', 'Return the last card your opponent played.', 'take back a move (Oct 29 list)'),
    (81, 'Thunder', 'Play once more after both players pass.', 'the last play (Nov 10 numbers)'),
    (82, 'Haze', "Your opponent can't play forces next turn.", 'a one-turn Calm for one player'),
]
for no, n, t, why in NEW_META: META.append((n, t)); META_NO[n] = no

ALL = [c for k, t, b, cs in GROUPS for c in cs]

# ---------------------------------------------------------------- binders: the fourth pass's five, unchanged
PROVISIONAL_BINDERS = pass4.PROVISIONAL_BINDERS

def check():
    probs = []
    names = collections.Counter([c['name'] for c in ALL] + [m[0] for m in META])
    probs += [('duplicate name', k) for k, v in names.items() if v > 1]
    fnames = collections.Counter(c['force'] for c in ALL if c['force'])
    probs += [('duplicate force name', k) for k, v in fnames.items() if v > 1]
    probs += [('force name is a card name', c['force']) for c in ALL if c['force'] in names]
    nums = sorted([c['no'] for c in ALL] + list(META_NO.values()))
    if nums != list(range(1, 101)): probs.append(('numbering', [n for n in range(1, 101) if n not in nums], len(nums)))
    for c in ALL:
        if not c['force']: probs.append(('no force', c['name']))
        p = len(c['affinities']); want = {1: 'C', 2: 'B', 3: 'A', 4: 'S'}.get(p)
        if c['rarity'] != want and not (p == 1 and c in G['a-blank']) and not (p == 0 and c['rarity'] == 'B'):
            probs.append(('pip rule', c['name'], p, c['rarity']))
        for t in (c['text'], c['force_text']):
            if t and words(t) >= 8 and t not in pass4.POINT_TEXT.values(): probs.append(('8+ words', c['name'], t))
        if re.search(r'with one affinity', c['force_text'] or ''): probs.append(('two restrictions', c['name'], c['force_text']))
    for m in META:
        if words(m[1]) >= 8: probs.append(('8+ words', m[0], m[1]))
    known = {c['name'] for c in ALL} | {m[0] for m in META}
    for bn, _d, cs in PROVISIONAL_BINDERS:
        if len(cs) != 16 or set(cs) - known: probs.append(('binder', bn, len(cs), set(cs) - known))
    return probs

def row(c):
    dur = 'Lasts the round' if c['duration'] == R else 'Once'
    return '| %d | %s | %s | %s | %s | %s | %s | %s |' % (c['no'], c['name'], c['rarity'], aff_cell(c['affinities']), c['text'] or '—', c['force'], dur, c['force_text'])

ORDER_KEYS = ['c-still', 'c-ignore', 'c-played', 'c-either', 'c-any', 'c-point', 'b-two', 'b-two-text', 'b-score', 'b-any', 'b-same', 'b-none', 'b-none-open',
              'a-three', 'a-two-one', 'a-triple', 'a-blank', 'u-pos', 'u-twist', 's']
TITLES = {'b-two-text': 'Two pips, uncommon: two different elements, no text since Nov 10', 'a-three': 'Three pips, rare: three different elements, start a new world',
          'a-triple': 'Three pips, rare: three of one element, first turn only', 's': 'Pinnacles'}

def markdown():
    rc = collections.Counter(c['rarity'] for c in ALL)
    reworded = [n for n in FORCES if FORCES[n][3].startswith('one restriction')]
    md = f'''## Fifth pass: playable again (Nov 11, 2026)

> Cam (Nov 11): "let's do a 5th pass at the card pool. I just want to get it back to a playable state so I can get more test games in." Every permanence has a force; effects may repeat, especially on commons and on different elements; gaps filled from the effect idea pool and the feedback so far; forces he's said he doesn't like readjusted; new cards from the idea pool, names from the word lists, themes and effects loosely tied to their affinity. Everything new here is Claude's draft against that brief, not adopted. The fourth pass as it ended is saved in the repo at `data/versions/card-pool-2026-11-11-fourth-pass-final.md` (branch `saved/card-pool-2026-11-11-fourth-pass-final`).

**The format for test games (Cam, Nov 11).** Best of three rounds, no cap on cards per round. Who goes second: before the contest, each player may reveal a permanence from their binder, and whoever reveals the most pips goes second (Cam: "let's see what that adds to the mix, it might be stupid and should just be a dice roll"). Claude's readings: revealing is optional (no reveal counts as zero pips); a tie is a coin flip; the revealed card stays in the binder, known to the other player; it decides round 1 only, and the openers alternate after that. A world scores one world point at most, for one of each element or four of one element (Nov 10); worlds go up to 2×2; returns only put cards into their owners' binders (Nov 11).

**What changed, and why.**
- **One restriction at most** (Cam, Nov 8): {', '.join('%s (%s)' % (FORCES[n][0], n) for n in reworded)} drop "with one affinity." The four uncommon removals now read the way Cam's Nov 2 ladder has an uncommon remove ("an earth or air permanence").
- **Removing a world's permanences of one element** hit 3–4 cards (Cam, Nov 8): the four three-of-one-element rares now remove two permanences of their element.
- **Returns** rated weakest in the Nov 8 sim; Tornado (High Desert, no water) becomes air's twist: "Return two cards you played last round."
- **Every card has a force:** Mountain Range, Red Canyon, Archipelago, Boiling Lake, Lava Plain, Sand Sea and Origin get one.
- **Pinnacles:** Tsunami and Firestorm were too weak (Cam, Nov 10) and now return a player's worlds and remove a world; World Quake read the same as Jet Stream and now splits every world; Origin gets back Unmaking ("Remove every world").
- **Restrictions on three-pip permanences** (Cam: "in some cases it might even make sense"): the three-of-one-element rares play only on your first turn (each makes a world point with one more pip of its element); the three-different-element rares play only on a new world (so they can't finish a world as a last play).
- **Hanging Valley** did nothing under the one-point rule; it now reads "Its world scores with one pip fewer."
- **The slots unique to one element are filled**: a positional permanence for each element, each with its own direction (idea 11), and one card per element that doubles down on its element's effect with a twist: water plays a card from either void (Whirlpool, idea 12), earth holds a world together (Sinkhole; Cavern's world can't be split, idea 9), fire removes the permanence just played (Meteor), air returns cards you played last round (Cyclone, and Tornado at rare).
- **Six new meta cards** fill the meta slots: Aftershock (idea 6), Stillness, Sunlight (idea 5), Weathering, Thunder and Haze.
- **Two- and three-pip permanences** otherwise stay vanilla (Cam: "they're strong because of their contribution to winning the rounds").

**Element identity, as this pass leaves it.** Water returns cards and plays from the void; earth holds things in place; fire takes pips away and removes what was just played; air moves cards and brings back last round's cards; removal stays spread across all four. Each element also turns other elements into itself. Removal and pip-stripping still follow two rules for which element an element presses on (the cycle and the opposites; `design/element-identity.md`); that's left as it was.

**Counts.** {rc['C']} commons, {rc['B']} uncommons, {rc['A']} rares, {rc['S']} pinnacles and {len(META)} meta cards: 100 cards, no placeholders, no open slots.

'''
    for key in ORDER_KEYS:
        k, title, blurb, cs = next(g for g in GROUPS if g[0] == key)
        md += '**%s (%d).**%s\n\n%s\n%s\n\n' % (TITLES.get(key, title), len(cs), (' ' + blurb) if blurb and key not in TITLES else '', HEAD, '\n'.join(row(c) for c in sorted(cs, key=lambda c: c['no'])))
    md += '**Fifth-pillar meta cards, no rarity (%d).** One face, usable by either player. Numbers 77–82 are new in this pass (Claude\'s drafts).\n\n| Card | No. | Text |\n| --- | --- | --- |\n' % len(META)
    md += '\n'.join('| %s | %d | %s |' % (m[0], META_NO[m[0]], m[1]) for m in sorted(META, key=lambda m: META_NO[m[0]])) + '\n\n'
    md += '**Provisional test binders (Claude, Nov 8), %d.** Carried over from the fourth pass: 16 cards each (10 commons, 4 uncommons, 2 rares), drawn at random until Cam builds real ones. Not designed: swap them out freely.\n\n' % len(PROVISIONAL_BINDERS)
    md += ''.join('- **Binder %s, %s.** %s. %s.\n' % (chr(65 + k), bn, d, ', '.join(cs)) for k, (bn, d, cs) in enumerate(PROVISIONAL_BINDERS))
    return md

if __name__ == '__main__':
    p = check()
    print('problems:', len(p))
    for x in p: print('  ', x)
    print('rarity', dict(collections.Counter(c['rarity'] for c in ALL)), 'meta', len(META), 'cards', len(ALL) + len(META))
    if '--md' in sys.argv:
        open(sys.argv[sys.argv.index('--md') + 1], 'w').write(markdown())
