# Fourth pass (Nov 8, 2026): the third pass restructured by ring count, at Cam's direction.
# Data + checks + markdown. Built from the third pass (pass3.py): every card here is a third-pass
# card, a third-pass card with new permanence text or rarity, or a reclaimed third-pass slot
# (name, art and force face kept) given a new permanence. Forces are carried over unchanged.
import collections, re, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import pass3

W, E, F, A, ANY = 'water', 'earth', 'fire', 'air', 'any'
ORDER = [W, E, F, A]  # the order affinities show on the cards (Cam, Nov 8)
P3 = {c[1]: c for c in pass3.ALL}
P3META = {m[1]: m for m in pass3.META}

def eo(a, b):
    """either-or capsule, elements in card order"""
    x, y = sorted([a, b], key=ORDER.index)
    return x + '|' + y

# (name, rarity, affinities, permanence text, how it came from the third pass)
# how: 'kept' (as it was), 'changed' (same card, new text or rarity), 'reused' (reclaimed slot, new permanence)
def card(name, rar, affs, text, how, note=''):
    p = P3[name]
    if how == 'kept':
        assert p[4] == text, (name, p[4], text)
    return dict(name=name, rarity=rar, affinities=affs, text=text, how=how, note=note,
                force=p[5], duration=p[6], force_text=p[7], was=(p[2], p[3], p[4]))

GROUPS = []  # (key, title, blurb, [cards]) in number order
def group(key, title, blurb, cards):
    GROUPS.append((key, title, blurb, cards))

group('c-still', "One ring, common: can't be moved", "One per element.", [
 card('Glacier', 'C', [W], "Can't be moved.", 'changed', "was uncommon; \"Ignores air forces.\" dropped to fit the cycle"),
 card('Bedrock', 'C', [E], "Can't be moved.", 'kept'),
 card('Lava Field', 'C', [F], "Can't be moved.", 'reused', 'reclaimed slot'),
 card('Spire', 'C', [A], "Can't be moved.", 'changed', "was uncommon; \"Ignores earth forces.\" dropped to fit the cycle"),
])
group('c-ignore', 'One ring, common: ignores the opposite element', "Opposites: water and fire, earth and air (Cam, Nov 8).", [
 card('Tide Pool', 'C', [W], "Ignores fire forces.", 'changed', 'ignored air'),
 card('Stone Field', 'C', [E], "Ignores air forces.", 'changed', 'ignored fire'),
 card('Ashfield', 'C', [F], "Ignores water forces.", 'kept'),
 card('Summit', 'C', [A], "Ignores earth forces.", 'kept'),
])
group('c-played', 'One ring, common: when played', "One per element.", [
 card('Snowfield', 'C', [W], "When played, return one of your permanences.", 'kept'),
 card('Grove', 'C', [E], "When played, remove a common force.", 'reused', "reclaimed slot; Claude's draft text"),
 card('Lava Flow', 'C', [F], "When played, play another fire card.", 'changed', 'was uncommon'),
 card('Bluff', 'C', [A], "When played, move one of your permanences.", 'kept'),
])
EITHER = [('Marsh', W, E), ('Mudflat', W, E), ('Steam Vent', W, F), ('Hot Mud', W, F), ('Sea Stack', W, A), ('Spray Coast', W, A),
          ('Flint', E, F), ('Peat Bog', E, F), ('Pass', E, A), ('Foothills', E, A), ('Scrubland', F, A), ('Heath', F, A)]
group('c-either', 'One ring, common: either-or, no text', "Two for each pair of elements.", [
 card(n, 'C', [eo(a, b)], '', 'kept' if not P3[n][4] else 'changed', '' if not P3[n][4] else 'text removed') for n, a, b in EITHER])
group('c-any', 'One ring, common: any', "", [
 card('Wilderness', 'C', [ANY], '', 'changed', 'was uncommon')])
group('a-blank', 'One ring, rare: X permanences lose their affinities', "Each blanks its opposite element (Cam, Nov 8).", [
 card('Ice Sheet', 'A', [W], "Fire permanences lose their affinities.", 'kept'),
 card('Thicket', 'A', [E], "Air permanences lose their affinities.", 'reused', 'reclaimed slot'),
 card('Badlands', 'A', [F], "Water permanences lose their affinities.", 'reused', 'reclaimed slot'),
 card('Wind Gap', 'A', [A], "Earth permanences lose their affinities.", 'reused', 'reclaimed slot'),
])
group('b-two', 'Two rings, uncommon: two different elements, no text', "", [
 card(n, 'B', a, '', 'kept') for n, a in [('Delta', [W, E]), ('Hot Spring', [W, F]), ('Cloud Forest', [W, A]), ('Volcano', [E, F]), ('Sea Cliff', [E, A]), ('Desert', [F, A])]])
group('b-two-text', 'Two rings, uncommon: two different elements, with text', "", [
 card(n, 'B', a, P3[n][4], 'kept') for n, a in [('Mangrove', [W, E]), ('Mud Pots', [W, F]), ('Waterfall', [W, A]), ('Cinder Cone', [E, F]), ('Canyon', [E, A]), ('Savanna', [F, A])]])
group('b-score', 'Two rings, uncommon: scoring (the Mountain Range cycle)', "Each scores a point per four of its element (Cam, Nov 8).", [
 card('Spring', 'B', [W, F], "Score a point per four water affinities.", 'reused', 'reclaimed slot'),
 card('Mountain Range', 'B', [E, A], "Score a point per four earth affinities.", 'changed', 'was rare'),
 card('Fumarole', 'B', [F, A], "Score a point per four fire affinities.", 'reused', 'reclaimed slot'),
 card('Sky Isle', 'B', [A, ANY], "Score a point per four air affinities.", 'reused', 'reclaimed slot; also the air card of the any cycle'),
])
group('b-any', 'Two rings, uncommon: one element and one any', "Sky Isle (above) is the air card of this cycle.", [
 card('Tidal Flat', 'B', [W, ANY], '', 'reused', 'reclaimed slot'),
 card('Old Growth', 'B', [E, ANY], '', 'reused', 'reclaimed slot'),
 card('Obsidian', 'B', [F, ANY], '', 'reused', 'reclaimed slot'),
 card('Hidden Valley', 'B', [ANY, ANY], '', 'reused', 'reclaimed slot; two any'),
])
group('b-same', 'Two rings, uncommon: two of one element', "", [
 card(n, 'B', [e, e], '', 'kept') for n, e in [('Deep Lake', W), ('Plateau', E), ('Lava Lake', F), ('Twin Peaks', A)]])
group('b-none', 'No rings, uncommon', "No ring of its own, so the ring rule doesn't place it; kept at uncommon.", [
 card('Mirage', 'B', [], P3['Mirage'][4], 'kept')])
group('a-three', 'Three rings, rare: three different elements', "", [
 card(n, 'A', a, '', 'kept') for n, a in [('Caldera Lake', [W, E, F]), ('Rainforest', [W, E, A]), ('Geyser Basin', [W, F, A]), ('Red Canyon', [E, F, A])]])
group('a-two-one', 'Three rings, rare: two of one element and one of another', "", [
 card(n, 'A', a, '', 'changed', 'win condition removed for now') if n == 'Archipelago' else card(n, 'A', a, P3[n][4], 'kept') for n, a in [
  ('Archipelago', [W, W, E]), ('Boiling Lake', [W, W, F]), ('Misty Fjord', [W, W, A]),
  ('Floodplain', [E, E, W]), ('Smoking Hills', [E, E, F]), ('Highlands', [E, E, A]),
  ('Lava Coast', [F, F, W]), ('Lava Plain', [F, F, E]), ('Sand Sea', [F, F, A]),
  ('Cloud Sea', [A, A, W]), ('Stone Towers', [A, A, E]), ('High Desert', [A, A, F])]])
group('a-triple', 'Three rings, rare: three of one element', "", [
 card('Lagoon', 'A', [W, W, W], '', 'reused', 'reclaimed slot'),
 card('Moor', 'A', [E, E, E], '', 'reused', 'reclaimed slot'),
 card('Cinder Field', 'A', [F, F, F], '', 'reused', 'reclaimed slot'),
 card('Peak', 'A', [A, A, A], '', 'reused', 'reclaimed slot'),
])
group('s', 'Four rings, pinnacle', "", [
 card(n, 'S', a, '', 'kept') for n, a in [('Ocean', [W] * 4), ('Pangaea', [E] * 4), ('Core', [F] * 4), ('Trade Winds', [A] * 4), ('Origin', [W, E, F, A])]])

# force text changed in this pass (Cam, Nov 8): "X permanences can't be moved" becomes "can't be removed", stronger and clearer to him
# (new text, Cam's reason if he gave one)
FORCE_CHANGES = {'Deep Lake': ("Water permanences can't be removed.", "stronger, and makes more sense to him"),
                 'Plateau': ("Earth permanences can't be removed.", "stronger, and makes more sense to him"),
                 'Red Canyon': ("A world's permanences become fire.", "")}
for _k, _t, _b, _cs in GROUPS:
    for _c in _cs:
        if _c['name'] in FORCE_CHANGES:
            _c['force_was'] = _c['force_text']; _c['force_text'], _c['force_why'] = FORCE_CHANGES[_c['name']]

# rare forces dialed back (Cam, Nov 8: rare forces got much stronger once worlds were uncapped). The three-of-one-element
# rares lose their reused common forces and take the remove-a-world's-element forces (Wildfire, Drought, ...); the cards
# those forces came from have no force for the moment. Claude matched each force to the triple of its own element by name
# (Flash Flood water, Avalanche earth, Wildfire fire, Drought the air triple); the targets follow the third pass's cycle.
FORCE_FROM = {'Lagoon': 'Boiling Lake', 'Moor': 'Mountain Range', 'Cinder Field': 'Lava Plain', 'Peak': 'Sand Sea'}
_by = {c['name']: c for _k, _t, _b, _cs in GROUPS for c in _cs}
for _to, _fr in FORCE_FROM.items():
    a, b = _by[_to], _by[_fr]
    a['force_dropped'] = a['force']
    a['force'], a['duration'], a['force_text'], a['force_from'] = b['force'], b['duration'], b['force_text'], _fr
for _fr in FORCE_FROM.values():
    b = _by[_fr]; b['force_moved'] = b['force']; b['force'], b['duration'], b['force_text'] = None, None, ''

# meta cards: one face, no rarity (Cam, Nov 8). Equinox was Cradle's force face; Cradle's permanence is removed.
META = [
 ('Echo', P3META['Echo'][3], 'was uncommon'),
 ('Hollow', P3META['Hollow'][3], 'was uncommon'),
 ('Equinox', P3['Cradle'][7], "was Cradle's force face"),
 ('Verge', P3META['Verge'][3], 'was uncommon'),
 ('Lull', P3META['Lull'][3], 'was rare'),
 ('Ebb', P3META['Ebb'][3], 'was uncommon'),
 ('Horizon', P3META['Horizon'][3], 'was uncommon'),
 ('Calm', P3META['Calm'][3], 'was uncommon'),
]

# numbers: commons 1-25, uncommons 26-50, rares 51-74 (the four one-ring rares last), meta 75-82, open 83-95, pinnacles 96-100
NUM_ORDER = ['c-still', 'c-ignore', 'c-played', 'c-either', 'c-any',
             'b-two', 'b-two-text', 'b-score', 'b-any', 'b-same', 'b-none',
             'a-three', 'a-two-one', 'a-triple', 'a-blank']
G = {k: cs for k, t, b, cs in GROUPS}
n = 0
for k in NUM_ORDER:
    for c in G[k]:
        n += 1; c['no'] = n
META_NO = {m[0]: 75 + i for i, m in enumerate(META)}
# placeholders (Cam, Nov 8): some cards aren't part of a cycle; at least 3 per element whose effects have no equivalent in another element
UNIQUE_NOTE = "Not part of a cycle: its effect has no equivalent in another element. Rings, rarity and effect to come."
UNNAMED_NOTE = "Not part of a cycle: its effect has no equivalent in another element. Rings, rarity, effect and name to come."
# names from the cut third-pass cards, matched to the element (Cam, Nov 8: "might inspire ideas"); fire has only two free fire names
PH_NAMES = {W: ['Ice Floe', 'Shoal', 'Fen'], E: ['Hill', 'Meadow', 'Cavern'], F: ['Dune', 'Barrens', None], A: ['Ledge', 'Ridge', 'Eyrie']}
_free = list(range(75 + len(META), 96))
PLACEHOLDERS = [(_free[i * 3 + k], e, PH_NAMES[e][k]) for i, e in enumerate(ORDER) for k in range(3)]
OPEN = _free[len(PLACEHOLDERS):]
for i, c in enumerate(G['s']): c['no'] = 96 + i
ALL = [c for k, t, b, cs in GROUPS for c in cs]

# third-pass cards with no place here
PLACED = {c['name'] for c in ALL} | {m[0] for m in META}
CUT = [c for c in pass3.ALL if c[1] not in PLACED]

PH_USED = [p[2] for p in PLACEHOLDERS if p[2]]
FREE_NAMES = [c[1] for c in CUT if c[1] not in PH_USED and c[1] not in ('Massif', 'Cradle')]

def words(t): return len(t.split())

def check():
    probs = []
    names = collections.Counter([c['name'] for c in ALL] + [m[0] for m in META])
    probs += [('duplicate name', k) for k, v in names.items() if v > 1]
    nums = sorted([c['no'] for c in ALL] + list(META_NO.values()) + [p[0] for p in PLACEHOLDERS] + OPEN)
    phn = [p[2] for p in PLACEHOLDERS if p[2]]
    if set(phn) - {c[1] for c in CUT}: probs.append(('placeholder name not from a cut card', set(phn) - {c[1] for c in CUT}))
    if set(phn) & ({c['name'] for c in ALL} | {m[0] for m in META}): probs.append(('placeholder name in use', set(phn) & {c['name'] for c in ALL}))
    if nums != list(range(1, 101)): probs.append(('numbering', nums))
    for c in ALL:
        rings = len(c['affinities'])
        want = {1: 'C', 2: 'B', 3: 'A', 4: 'S'}.get(rings)
        if c['rarity'] != want and not (rings == 1 and c in G['a-blank']) and not (rings == 0 and c['name'] == 'Mirage'):
            probs.append(('ring rule', c['name'], rings, c['rarity']))
        if c['text'] and words(c['text']) >= 8 and c['name'] not in pass3.EXCEPTIONS: probs.append(('8+ words', c['name'], c['text']))
        if re.search(r'\b(hand|deal|the)\b', c['name'], re.I): probs.append(('name rule', c['name']))
    for m in META:
        if words(m[1]) >= 8: probs.append(('8+ words', m[0], m[1]))
    for k in ('c-still', 'c-ignore', 'c-played', 'a-blank', 'a-triple'):
        els = [next(a for a in c['affinities']) for c in G[k]]
        if els != ORDER: probs.append(('cycle order', k, els))
    pairs = collections.Counter(c['affinities'][0] for c in G['c-either'])
    if len(pairs) != 6 or set(pairs.values()) != {2}: probs.append(('either-or pairs', pairs))
    trip = {tuple(sorted(c['affinities'])) for c in G['a-three'] + G['a-two-one']}
    if len(trip) != 16: probs.append(('three-ring combos', len(trip)))
    return probs

def tally():
    t = collections.Counter()
    for c in ALL:
        for a in c['affinities']:
            if '|' in a:
                for x in a.split('|'): t[x + ' (either-or)'] += 1
            else: t[a] += 1
    return t

def aff_cell(affs):
    if not affs: return 'none'
    cnt = collections.Counter(affs)
    keys = sorted(cnt, key=lambda a: (ORDER.index(a.split('|')[0]) if a != ANY else 9, a))
    out = []
    for a in keys:
        if '|' in a: out.append('%d either-or (%s or %s)' % ((cnt[a],) + tuple(a.split('|'))))
        else: out.append('%d %s' % (cnt[a], a))
    return ', '.join(out)

RWORD = {'C': 'commons', 'B': 'uncommons', 'A': 'rares', 'S': 'pinnacles'}
HEAD = '| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |\n| --- | --- | --- | --- | --- | --- | --- | --- |'
def row(c):
    if not c['force']:
        return '| %d | %s | %s | %s | %s | — | — | No force for the moment. |' % (c['no'], c['name'], c['rarity'], aff_cell(c['affinities']), c['text'] or '—')
    dur = 'Lasts the round' if c['duration'] == pass3.R else 'Once'
    return '| %d | %s | %s | %s | %s | %s | %s | %s |' % (c['no'], c['name'], c['rarity'], aff_cell(c['affinities']), c['text'] or '—', c['force'], dur, c['force_text'])

def markdown():
    t = tally()
    rc = collections.Counter(c['rarity'] for c in ALL)
    reused = [c for c in ALL if c['how'] == 'reused']
    changed = [c for c in ALL if c['how'] == 'changed']
    md = f'''## Fourth pass: the pool by ring count (Nov 8, 2026)

> Cam's restructure of the third pass (Nov 8), applied to the card pool at his request. The third pass as it stood before this is saved in the repo at `data/versions/card-pool-2026-11-08-third-pass.md` (branch `saved/card-pool-2026-11-08-third-pass`). Forces are carried over from the third pass, so they haven't been tuned to the new rarities; the ones Cam has changed since are listed below. No binders yet: the playtest table, the computer and the simulator still play the saved third pass until the binders are rebuilt.

**The structure (Cam, Nov 8).** A card's rarity follows its rings: one ring at common, two at uncommon, three at rare, four at pinnacle. The exceptions are the four rares with one ring that blank their opposite element (Ice Sheet's cycle) and Mirage, which has no ring and stays uncommon. Meta cards have no rarity. Each element has three one-ring commons, one in each cycle: can't be moved, ignores its opposite element's forces, and an effect when played. The opposites are water and fire, earth and air. Two either-or commons per pair of elements, with no text. Wilderness moves to common. New cycles: one element and one any at uncommon, plus one card with two any; three of one element at rare; and a scoring cycle after Mountain Range (water and fire scores water, fire and air scores fire, air and any scores air; the air card is also the any cycle's air card). Cradle's permanence is removed and its force, Equinox, becomes a meta card. Massif is removed. On the any cycle: "the 'any' affinity might be too strong to leave uncommon but for now let's go with it."

**Reclaimed slots (Cam: reuse the existing names).** {len(reused)} cards take the name, art and force face of a cut third-pass card and get a new permanence: {', '.join(c['name'] for c in reused)}. Claude picked which name went where, by landform; Grove's text ("When played, remove a common force.") is Claude's draft, since earth had no when-played card.

**Changed in place.** {'; '.join('%s (%s)' % (c['name'], c['note']) for c in changed)}.

**Forces changed (Cam, Nov 8).** {'; '.join('%s (%s) now reads "%s" (was "%s"%s)' % (c['force'], c['name'], c['force_text'], c['force_was'], ': ' + c['force_why'] if c['force_why'] else '') for c in ALL if 'force_was' in c)}. Rare forces dialed back (Cam: they got much stronger once worlds were uncapped): the three-of-one-element rares drop their reused common forces ({', '.join('%s (%s)' % (c['force_dropped'], c['name']) for c in ALL if 'force_from' in c)}) and take the remove-a-world's-element forces: {'; '.join('%s now has %s, "%s" (from %s)' % (c['name'], c['force'], c['force_text'], c['force_from']) for c in ALL if 'force_from' in c)}. Claude matched each force to the triple of its element by name; Wildfire and Drought remove by the third pass's cycle (fire burns earth, air dries water), not the opposites. {', '.join(c['name'] for c in ALL if 'force_moved' in c)} have no force for the moment. Every other force is carried over from the third pass unchanged.

**Cut.** {len(CUT)} third-pass cards have no place: {', '.join(c[1] for c in CUT)}. {len(PH_USED)} of their names now sit on the placeholders for cards unique to one element (Cam: names "might inspire ideas"); still free: {', '.join(FREE_NAMES)}.

**Counts.** {rc['C']} commons, {rc['B']} uncommons, {rc['A']} rares, {rc['S']} pinnacles and {len(META)} meta cards: {len(ALL) + len(META)} cards, {len(PLACEHOLDERS)} placeholders (numbers {PLACEHOLDERS[0][0]}–{PLACEHOLDERS[-1][0]}) and {len(OPEN)} open {'slot' if len(OPEN) == 1 else 'slots'} ({', '.join(map(str, OPEN))}). Rings across the pool: water {t[W]}, earth {t[E]}, fire {t[F]}, air {t[A]}, plus {t[W + ' (either-or)']} either-or capsules for each element and {t[ANY]} any.

**Noted, not settled.** Forces moving to common with the ring rule now remove or move a permanence, which nothing at common did since Nov 2: Lightning (Lava Flow), Whirlwind (Spire) and Thunderstorm (Wilderness). The cycle that returned at round end (Fumarole, Spring, Eyrie, Grove) is gone. A vanilla one-ring cycle was a maybe and isn't included. The card text uses "affinities" in the order water, earth, fire, air from here on. The placeholders for cards unique to one element take 12 of the 13 open slots, which Cam had earmarked for more multi-affinity cards; their rings aren't set, so they may still be.

'''
    for key in NUM_ORDER + ['s']:
        k, title, blurb, cs = next(g for g in GROUPS if g[0] == key)
        lead = '**%s (%d).**' % (title, len(cs))
        md += '%s%s\n\n%s\n%s\n\n' % (lead, (' ' + blurb) if blurb else '', HEAD, '\n'.join(row(c) for c in cs))
    md += '**Fifth-pillar meta cards, no rarity (%d).** One face, usable by either player.\n\n| Card | No. | Text |\n| --- | --- | --- |\n' % len(META)
    md += '\n'.join('| %s | %d | %s |' % (m[0], META_NO[m[0]], m[1]) for m in META) + '\n\n'
    md += '**Placeholders: unique to one element (%d).** Cam (Nov 8): there should be some cards that aren\'t part of a cycle; ironically, a cycle of at least 3 cards in each element whose effects have no equivalent in other elements.\n\n| No. | Placeholder | Element | What it\'s for |\n| --- | --- | --- | --- |\n' % len(PLACEHOLDERS)
    md += '\n'.join('| %d | %s | %s | %s |' % (no, nm or 'Unique %s %d' % (e, k % 3 + 1), e, UNIQUE_NOTE if nm else UNNAMED_NOTE) for k, (no, e, nm) in enumerate(PLACEHOLDERS)) + '\n\n'
    md += '**Open %s (%d).** %s. Cam (Nov 8): the slots this opens should go to more multi-affinity cards.\n' % ('slot' if len(OPEN) == 1 else 'slots', len(OPEN), 'Number ' + str(OPEN[0]) if len(OPEN) == 1 else 'Numbers %d–%d' % (OPEN[0], OPEN[-1]))
    return md

if __name__ == '__main__':
    p = check()
    print('problems:', len(p))
    for x in p: print('  ', x)
    t = tally()
    print({e: t[e] for e in ORDER}, 'either-or', {e: t[e + ' (either-or)'] for e in ORDER}, 'any', t[ANY])
    print('rarity', dict(collections.Counter(c['rarity'] for c in ALL)), 'meta', len(META), 'placeholders', len(PLACEHOLDERS), 'open', OPEN)
    print('cut', [c[1] for c in CUT])
    if '--md' in sys.argv:
        open(sys.argv[sys.argv.index('--md') + 1], 'w').write(markdown())
