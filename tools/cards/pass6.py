# Sixth pass (Nov 11, 2026): fewer force faces that reach the other player, and answers gated by rarity.
# Cam: playing a permanence and having it answered at once feels worse than in Magic, because every card is double-sided
# and so every card can be interaction. He wants to keep double-sided cards ("persist with double sided until I feel
# there's no way to make it work") and:
#   - about one force in ten is hard removal, one in ten moves or swaps the other player's cards, one in ten negates
#     the other player's forces; the rest help their owner;
#   - a force that reaches the other player reaches only permanences of its own rarity (rarity symbols in the text,
#     like element symbols);
#   - no more "loses its affinities" ("it doesn't feel right"), and as few forces staying on the table as possible.
# Everything below is Claude's draft against that brief. The fifth pass (pass5.py) is the base.
import collections, copy, re, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import pass4, pass5
from pass4 import W, E, F, A, aff_cell, HEAD, words

R, O = 'round', 'once'
GROUPS = copy.deepcopy(pass5.GROUPS)
BY = {c['name']: c for k, t, b, cs in GROUPS for c in cs}

# role: rem (hard removal), mov (moves or swaps the other player's cards), neg (stops the other player's forces),
# self (helps its owner only). Texts naming a rarity reach only permanences (or forces) of that rarity.
REM, MOV, NEG, SELF = 'removal', 'move', 'negate', 'self'
UNTIL = 'until'  # lasts until the caster's next turn
FORCES = {
    # ---- commons
    'Glacier': ('Thaw', O, 'Remove a common force.', NEG),
    'Bedrock': ('Tangle', UNTIL, 'No common forces until your next turn.', NEG),
    'Lava Field': ('Ash', O, 'Remove a common permanence.', REM),
    'Spire': ('Whirlwind', O, 'Split one of your worlds.', SELF),
    'Tide Pool': ('Drizzle', O, 'Return a card from your void.', SELF),
    'Stone Field': ('Dust', UNTIL, 'No common forces until your next turn.', NEG),
    'Ashfield': ('Brushfire', R, 'One of your permanences becomes fire.', SELF),
    'Summit': ('Crosswind', O, 'Swap two common permanences.', MOV),
    'Snowfield': ('Freeze', O, 'Play a permanence from your void.', SELF),
    'Grove': ('Overgrowth', O, 'Play another earth card.', SELF),
    'Lava Flow': ('Lightning', O, 'Remove a common permanence.', REM),
    'Bluff': ('Eddy', O, 'Swap two of your permanences.', SELF),
    'Marsh': ('Mire', O, 'Return a card from your void.', SELF),
    'Steam Vent': ('Vent', O, 'Return one of your permanences.', SELF),
    'Sea Stack': ('Riptide', R, 'One of your permanences becomes water.', SELF),
    'Flint': ('Spark', O, 'Play another fire card.', SELF),
    'Pass': ('Whirl', O, 'Move a common permanence to another world.', MOV),
    'Scrubland': ('Dust Devil', R, 'One of your permanences becomes air.', SELF),
    'Wilderness': ('Thunderstorm', O, 'Remove a common permanence.', REM),
    'Ice Floe': ('Current', O, 'Play a permanence from your void.', SELF),
    'Hill': ('Rockfall', R, 'One of your permanences becomes earth.', SELF),
    'Dune': ('Updraft', O, 'Play another fire card.', SELF),
    'Ledge': ('Gust', O, 'A common permanence becomes its own world.', MOV),
    'Shoal': ('Mist', O, 'Move one of your permanences.', SELF),
    'Meadow': ('Mudslide', O, 'Move one of your permanences.', SELF),
    'Barrens': ('Smoke', O, 'Swap two of your permanences.', SELF),
    'Ridge': ('Breeze', O, 'Move one of your permanences.', SELF),
    'Cavern': ('Sinkhole', R, "A world can't lose permanences.", NEG),
    'Eyrie': ('Cyclone', O, 'Return a card you played last round.', SELF),
    # ---- uncommons
    'Delta': ('Flood', O, 'Return two of your permanences.', SELF),
    'Hot Spring': ('Scald', O, 'Remove an uncommon permanence.', REM),
    'Cloud Forest': ('Fog', UNTIL, 'No uncommon forces until your next turn.', NEG),
    'Volcano': ('Lava Bomb', O, 'Remove an uncommon permanence.', REM),
    'Sea Cliff': ('Gale', O, 'Move an uncommon permanence to another world.', MOV),
    'Desert': ('Heatwave', O, 'Play another card.', SELF),
    'Mangrove': ('Undertow', O, 'Return one of your worlds.', SELF),
    'Mud Pots': ('Downpour', O, 'Play a permanence from your void.', SELF),
    'Waterfall': ('Cloudburst', O, 'Return two cards from your void.', SELF),
    'Cinder Cone': ('Ashfall', O, 'Split one of your worlds.', SELF),
    'Canyon': ('Dust Storm', O, 'Swap two of your permanences.', SELF),
    'Savanna': ('Sandstorm', O, 'Play another card.', SELF),
    'Spring': ('Low Tide', O, 'Return one of your worlds.', SELF),
    'Mountain Range': ('Rockslide', O, 'Move one of your permanences.', SELF),
    'Fumarole': ('Flare-up', UNTIL, 'No uncommon forces until your next turn.', NEG),
    'Sky Isle': ('Waterspout', O, 'Split one of your worlds.', SELF),
    'Tidal Flat': ('Hail', O, 'Return two of your permanences.', SELF),
    'Old Growth': ('Bramble', UNTIL, 'No uncommon forces until your next turn.', NEG),
    'Obsidian': ('Scorch', O, 'Remove an uncommon permanence.', REM),
    'Hidden Valley': ('Landslide', O, 'An uncommon permanence becomes its own world.', MOV),
    'Deep Lake': ('Ice Storm', O, 'Return two cards from your void.', SELF),
    'Plateau': ('Permafrost', O, 'Play another card.', SELF),
    'Lava Lake': ('Heat Dome', O, 'Play another fire card.', SELF),
    'Twin Peaks': ('High Pressure', O, 'Swap two of your permanences.', SELF),
    'Mirage': ('Heat Shimmer', O, 'Move one of your permanences.', SELF),
    'Hanging Valley': ('Squall', O, 'Swap two of your permanences.', SELF),
    'Fen': ('Whirlpool', O, 'Play a card from a void.', SELF),
    'Crater': ('Meteor', O, 'Play two more fire cards.', SELF),
    # ---- rares
    'Ice Sheet': ('Blizzard', UNTIL, 'No rare forces until your next turn.', NEG),
    'Thicket': ('Shelter', UNTIL, 'No rare forces until your next turn.', NEG),
    'Badlands': ('Ember', O, 'Play two more cards.', SELF),
    'Wind Gap': ('Downdraft', O, 'A rare permanence becomes its own world.', MOV),
    'Caldera Lake': ('Collapse', O, 'Remove a rare permanence.', REM),
    'Rainforest': ('Monsoon', O, 'Play a card from your void.', SELF),
    'Geyser Basin': ('Typhoon', O, 'Move two of your permanences.', SELF),
    'Red Canyon': ('Erosion', O, 'Return two of your worlds.', SELF),
    'Archipelago': ('Surge', O, 'Return three cards from your void.', SELF),
    'Boiling Lake': ('Torrent', O, 'Play a card from your void.', SELF),
    'Misty Fjord': ('Whiteout', O, 'Play a card from your void.', SELF),
    'Floodplain': ('Mudflow', O, 'Return two of your worlds.', SELF),
    'Smoking Hills': ('Eruption', O, 'Play two more cards.', SELF),
    'Highlands': ('Earthquake', O, 'Return two of your worlds.', SELF),
    'Lava Coast': ('Steam Explosion', O, 'Play two more cards.', SELF),
    'Lava Plain': ('Magma', O, 'Play two more cards.', SELF),
    'Sand Sea': ('Supercell', O, 'Play two more cards.', SELF),
    'Cloud Sea': ('Hurricane', O, 'Move two of your permanences.', SELF),
    'Stone Towers': ('Gale Force', O, 'Move two of your permanences.', SELF),
    'High Desert': ('Tornado', O, 'Return two cards you played last round.', SELF),
    'Lagoon': ('Flash Flood', O, 'Return three cards from your void.', SELF),
    'Moor': ('Avalanche', O, 'Return two of your worlds.', SELF),
    'Cinder Field': ('Wildfire', O, 'Play two more cards.', SELF),
    'Peak': ('Drought', O, 'Move two of your permanences.', SELF),
    # ---- pinnacles: world-scale disasters, kept from the fifth pass. READING: the rarity gate doesn't fit them (no single
    # permanence is aimed at, and almost nothing else is a pinnacle), so they reach every rarity; open for Cam
    'Ocean': ('Tsunami', O, "Return a player's worlds.", MOV),
    'Pangaea': ('World Quake', O, 'Split every world.', MOV),
    'Core': ('Firestorm', O, 'Remove a world.', REM),
    'Trade Winds': ('Jet Stream', O, 'Every permanence becomes its own world.', MOV),
    'Origin': ('Unmaking', O, 'Remove every world.', REM),
}
# the rare cycle that blanked the opposite element (Ice Sheet's) now builds its own world instead (Cam: no more
# "loses its affinities"); positional, like idea 11
TEXTS = {
    'Ice Sheet': 'Each permanence in its world gains water.',
    'Thicket': 'Each permanence in its world gains earth.',
    'Badlands': 'Each permanence in its world gains fire.',
    'Wind Gap': 'Each permanence in its world gains air.',
}
ROLE = {}
CHANGED = {}
for n, (f, d, t, role) in FORCES.items():
    c = BY[n]
    if c['force_text'] != t or c['force'] != f:
        CHANGED[n] = ['force: was "%s"' % c['force_text']]
    c.update(force=f, duration=d, force_text=t)
    ROLE[n] = role
for n, t in TEXTS.items():
    c = BY[n]; CHANGED.setdefault(n, []).append('text: was "%s"' % c['text']); c['text'] = t

META, META_NO, NEW_META = pass5.META, pass5.META_NO, pass5.NEW_META
ALL = [c for k, t, b, cs in GROUPS for c in cs]
PROVISIONAL_BINDERS = pass4.PROVISIONAL_BINDERS
RWORDS = ('common', 'uncommon', 'rare')

def check():
    probs = []
    names = collections.Counter([c['name'] for c in ALL] + [m[0] for m in META])
    probs += [('duplicate name', k) for k, v in names.items() if v > 1]
    fnames = collections.Counter(c['force'] for c in ALL)
    probs += [('duplicate force name', k) for k, v in fnames.items() if v > 1]
    probs += [('force name is a card name', c['force']) for c in ALL if c['force'] in names]
    nums = sorted([c['no'] for c in ALL] + list(META_NO.values()))
    if nums != list(range(1, 101)): probs.append(('numbering', len(nums)))
    if set(FORCES) != {c['name'] for c in ALL}: probs.append(('unassigned', {c['name'] for c in ALL} - set(FORCES)))
    for c in ALL:
        for t in (c['text'], c['force_text']):
            if t and words(t) >= 8 and t not in pass4.POINT_TEXT.values() and t != pass4.WORLD_TEXT: probs.append(('8+ words', c['name'], t))
            if t and 'affinities' in t and 'lose' in t: probs.append(('loses its affinities', c['name'], t))
        # the rarity gate: a force naming a rarity names its own
        m = re.search(r'\b(common|uncommon|rare)\b', c['force_text'])
        if m and {'common': 'C', 'uncommon': 'B', 'rare': 'A'}[m.group(1)] != c['rarity']: probs.append(('rarity gate', c['name'], c['rarity'], c['force_text']))
        if ROLE[c['name']] in (REM, MOV) and c['rarity'] != 'S' and not m: probs.append(('ungated answer', c['name'], c['force_text']))
    return probs

def dur_label(c):
    return 'Until your next turn' if c['duration'] == UNTIL else 'Lasts the round' if c['duration'] == R else 'Once'

def row(c):
    return '| %d | %s | %s | %s | %s | %s | %s | %s |' % (c['no'], c['name'], c['rarity'], aff_cell(c['affinities']), c['text'] or '—', c['force'], dur_label(c), c['force_text'])

ORDER_KEYS = pass5.ORDER_KEYS
TITLES = dict(pass5.TITLES); TITLES['a-blank'] = "One pip, rare: each permanence in its world gains its element (the opposite-element blanks until Nov 11)"

def roles():
    return collections.Counter(ROLE.values()), collections.Counter((ROLE[c['name']], c['rarity']) for c in ALL)

def markdown():
    rc = collections.Counter(c['rarity'] for c in ALL)
    tot, by = roles()
    lasting = [c for c in ALL if c['duration'] in (R, UNTIL)]
    lst = lambda role, r: ', '.join(sorted(c['name'] for c in ALL if ROLE[c['name']] == role and c['rarity'] == r)) or 'none'
    md = f'''## Sixth pass: fewer answers, gated by rarity (Nov 11, 2026)

> Cam (Nov 11): playing a permanence and having it answered at once "feels worse for some reason than it does in magic. I think it's because magic decks normally have way fewer pieces of interaction than creatures or threats." He wants to keep double-sided cards ("I want to persist with double sided until I feel there's no way to make it work") and: "let's go with one in ten are hard removal. one in ten can move or swap opponents cards. another one in ten can negate enemy forces." A force that reaches the other player reaches only permanences of its own rarity, shown with rarity symbols in the text like element symbols. "I want to get rid of all the \\"x loses its affinities\\" because it doesn't feel right. I want to generally avoid forces sticking around on the table where possible." Everything new here is Claude's draft against that brief, not adopted. The fifth pass as it ended is saved in the repo at `data/versions/card-pool-2026-11-11-fifth-pass-final.md` (branch `saved/card-pool-2026-11-11-fifth-pass-final`).

**The format** is unchanged from the fifth pass: best of three, no cap on cards a round, the reveal for who goes second, worlds up to 2×2, one world point at most from a world's affinities with card effects adding to it.

**The 86 force faces by role.**
- **Hard removal ({tot[REM]}):** commons {lst(REM, 'C')}: "Remove a common permanence." Uncommons {lst(REM, 'B')}: "Remove an uncommon permanence." Rare {lst(REM, 'A')}: "Remove a rare permanence." Pinnacles {lst(REM, 'S')}: a world, every world.
- **Moving or swapping the other player's cards ({tot[MOV]}):** commons {lst(MOV, 'C')}; uncommons {lst(MOV, 'B')}; rare {lst(MOV, 'A')}; pinnacles {lst(MOV, 'S')}.
- **Stopping the other player's forces ({tot[NEG]}):** commons {lst(NEG, 'C')}; uncommons {lst(NEG, 'B')}; rares {lst(NEG, 'A')}. "No common forces until your next turn" stops that rarity's forces for the other player's next turn; Thaw removes a common force; Sinkhole holds a world.
- **Helping their owner ({tot[SELF]}):** each element leans on its own verbs. Water brings cards back (from your void to your binder, or straight into play) and returns your own permanences and worlds to your binder, which saves them for a later round; earth returns whole worlds and holds; fire plays more cards in a turn; air moves, swaps and splits your own cards, which matters now that positions give pips and a split can turn one world point into two. Four commons change one of your own permanences' element for the round, one per element.
- **The rarity gate:** "only its own rarity" (Cam). The pinnacles keep their world-scale forces, which aim at no single permanence (Claude's reading; open).
- **Lasting forces:** {len(lasting)} of 86 stay on the table (down from about 40): the {sum(1 for c in lasting if c['duration'] == UNTIL)} "No … forces until your next turn", Sinkhole, and the four commons that change an element for the round.
- **No "loses its affinities"** anywhere: the twelve blanking forces are gone, and Ice Sheet's rare cycle now reads "Each permanence in its world gains water" (and earth, fire, air).
- **Unchanged:** the permanence faces apart from Ice Sheet's cycle, the restrictions on the three-pip rares, the meta cards, and the pinnacles' forces.

**Counts.** {rc['C']} commons, {rc['B']} uncommons, {rc['A']} rares, {rc['S']} pinnacles and {len(META)} meta cards: 100 cards.

'''
    for key in ORDER_KEYS:
        k, title, blurb, cs = next(g for g in GROUPS if g[0] == key)
        md += '**%s (%d).**%s\n\n%s\n%s\n\n' % (TITLES.get(key, title), len(cs), (' ' + blurb) if blurb and key not in TITLES else '', HEAD, '\n'.join(row(c) for c in sorted(cs, key=lambda c: c['no'])))
    md += '**Fifth-pillar meta cards, no rarity (%d).** One face, usable by either player. Unchanged from the fifth pass.\n\n| Card | No. | Text |\n| --- | --- | --- |\n' % len(META)
    md += '\n'.join('| %s | %d | %s |' % (m[0], META_NO[m[0]], m[1]) for m in sorted(META, key=lambda m: META_NO[m[0]])) + '\n\n'
    md += '**Provisional test binders (Claude, Nov 8), %d.** Carried over: 16 cards each (10 commons, 4 uncommons, 2 rares), drawn at random until Cam builds real ones.\n\n' % len(PROVISIONAL_BINDERS)
    md += ''.join('- **Binder %s, %s.** %s. %s.\n' % (chr(65 + k), bn, d, ', '.join(cs)) for k, (bn, d, cs) in enumerate(PROVISIONAL_BINDERS))
    return md

if __name__ == '__main__':
    p = check()
    print('problems:', len(p))
    for x in p: print('  ', x)
    tot, by = roles()
    print('roles', dict(tot), {k: v for k, v in sorted(by.items())})
    print('lasting', sum(1 for c in ALL if c['duration'] in (R, UNTIL)))
    if '--md' in sys.argv:
        open(sys.argv[sys.argv.index('--md') + 1], 'w').write(markdown())
