# The Branch B card pool: the sixth pass (the last 100-card pool, data/cards.json) under Branch B's rules.
# Usage: python3 branchb_pool.py [--json out.json] [--md out.md]
#
# Cam, Nov 23, 2026: "let's get the card pool back into a 100 card playable state like it once was. Find the last 100
# card pool and update it with any changes we've made to core rules since then." His answers to Claude's three questions:
#   fronts:   "return the abilities to the idea pool so we don't forget about them, then create the card pool list view
#              like before so I can look through the pool (front and back)."
#   void and meta cards: "Keep both"
#   blockers: "A cycle of eight" (two per element, all commons).
# Everything else here is Claude's draft against Branch B's settled rules, not adopted.
import collections, json, re, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import pass6

ROOT = __file__.rsplit('/', 3)[0]
SRC = json.load(open(ROOT + '/data/cards.json'))
E = ['water', 'earth', 'fire', 'air']

def words(t):  # a run of element symbols counts as one word, as on the cards
    return len(re.sub(r'\b(water|earth|fire|air)( (water|earth|fire|air))+\b', 'X', t).split())

# ------------------------------------------------------------------ the rules that changed since the sixth pass
# 1. Fronts are vanilla: every front ability goes to the idea pool (Cam, Nov 23).
# 2. A turn is one landscape and one force, and a force is used by flipping its card in play. So:
#    - "Lasts the round" (there is one round now) becomes "while flipped": the effect lives on the flipped card, as
#      Cave-in's does, and ends if the card is flipped back or leaves play.
#    - "Remove a force" (a force on the table) becomes "flip back": the forces on the table are flipped cards now.
#    - "last round" becomes the last permanence you played.
#    - The extra plays come back from the idea pool. They left on Nov 12 because "with uncapped turns, playing extra
#      cards in a row doesnt do anything" (Cam); a Branch B turn has one landscape, so they do something again.
# 3. Backs have their own pips, "almost always fewer or even no element affinities" (Cam), losing an element only
#    where it feels thematic ("it shouldn't be a consistent thing for every multi-colored card").
# 4. A few cards flip back on their own, from natural cycles (Cam: "once a card flips, it can't flip back on it's own
#    in most cases"): tides, seasons, regrowth, bubbling mud, a shimmering mirage.
# 5. Blockers: "Can be played on an opponent's world." on a cycle of eight commons, two per element (Cam, Nov 23).
# 6. Meta cards are played in place of the turn's landscape; cards that leave play go to their owner's void.

DUR = {'Once': 'Once', 'Until your next turn': 'Until your next turn', 'Lasts the round': 'While flipped'}

TEXT = {  # back texts that change with the rules (sixth pass -> Branch B), and why
    'Glacier': ('Flip back a common permanence.', 'was "Remove a common force."; the forces on the table are flipped cards now'),
    'Cavern': ('This world ignores your opponent\'s forces.', 'was "Your world …"; "this" names the world it is in'),
    'Eyrie': ('Return the last permanence you played.', 'was "Return a card you played last round."; one round now'),
    'High Desert': ('Return the last two permanences you played.', 'was "Return two cards you played last round."; one round now'),
}
RESTORED = {  # the Nov 12 extra plays, back from the idea pool, worded for a capped turn. Cam, Nov 23: '"play two more"
    # is definitely too strong. "Play one more" and moving it to a 1 or 2 pip card instead of a 3 pip card.'
    'Play another earth card.': 'Play another earth permanence this turn.',
    'Play another fire card.': 'Play another fire permanence this turn.',
    'Play another card.': 'Play another permanence this turn.',
    'Play two more fire cards.': 'Play another fire permanence this turn.',
    'Play two more cards.': 'Play another permanence this turn.',
}
ONE_MORE = 'Cam, Nov 23: "play two more" is definitely too strong; "play one more"'
OFF_THREE = 'Cam, Nov 23: extra plays go on a 1 or 2 pip card, not a 3 pip card; open until a force is chosen'
FLIPS_BACK = {  # the natural cycles
    'Tide Pool': 'the tide comes back in', 'Tidal Flat': 'the tide', 'Spring': 'low tide, then high', 'Snowfield': 'the seasons',
    'Grove': 'a forest regrows', 'Savanna': 'grass burns and grows back', 'Mud Pots': 'mud bubbles up again', 'Mirage': 'a mirage comes and goes',
}
BLOCKERS = {  # two per element; landscapes that drift or spread into a neighbour's land
    'Ice Floe': 'drifts', 'Shoal': 'a hazard in their water', 'Hill': 'one of the test blockers (Hills)', 'Meadow': 'one of the test blockers',
    'Lava Flow': 'flows into their land', 'Dune': 'dunes wander', 'Ridge': 'a ridge divides', 'Eyrie': 'nests on their cliffs',
}
BACK = {  # back pips, in the order water, earth, fire, air; anything not listed here loses every pip
    'Bedrock': ['earth'],  # bedrock stays
    'Delta': ['water'], 'Hot Spring': ['water'], 'Cloud Forest': ['water'], 'Volcano': ['fire'], 'Sea Cliff': ['air'], 'Desert': ['fire'],
    'Mangrove': ['earth'], 'Mud Pots': ['earth'], 'Waterfall': ['water'], 'Cinder Cone': ['earth'], 'Canyon': ['earth'], 'Savanna': ['air'],
    'Spring': ['water'], 'Mountain Range': ['earth'], 'Fumarole': ['air'], 'Sky Isle': ['air'], 'Tidal Flat': ['water'],
    'Old Growth': ['earth', 'any'], 'Obsidian': ['earth'], 'Hidden Valley': ['any'], 'Deep Lake': ['water'], 'Plateau': ['earth', 'earth'],
    'Lava Lake': ['fire'], 'Twin Peaks': ['air'], 'Fen': ['water'], 'Crater': ['earth'],
    'Caldera Lake': ['water', 'earth'], 'Rainforest': ['water', 'earth'], 'Geyser Basin': ['water', 'fire'], 'Red Canyon': ['earth', 'fire'],
    'Archipelago': ['water', 'water'], 'Boiling Lake': ['water', 'water'], 'Misty Fjord': ['water', 'water'], 'Floodplain': ['water', 'earth'],
    'Smoking Hills': ['earth', 'earth'], 'Highlands': ['earth', 'earth'], 'Lava Coast': ['water', 'earth'], 'Lava Plain': ['earth', 'fire'],
    'Sand Sea': ['fire', 'air'], 'Cloud Sea': ['water'], 'Stone Towers': ['earth', 'air'], 'High Desert': ['fire', 'air'],
    'Lagoon': ['water', 'water'], 'Moor': ['earth', 'earth'], 'Cinder Field': ['fire', 'fire'], 'Peak': ['air', 'air'],
    'Ocean': ['water', 'water'], 'Pangaea': ['earth', 'earth'], 'Core': ['fire', 'fire'], 'Trade Winds': ['air', 'air'],
}
WHY_BACK = {  # where a back changes element or keeps every pip
    'Bedrock': 'keeps its pip: bedrock stays', 'Mud Pots': 'water and fire make mud', 'Obsidian': 'lava cools to glass',
    'Lava Coast': 'lava meets the sea and makes land', 'Old Growth': 'keeps both: old growth endures', 'Plateau': 'keeps both, as the test Plateau did',
}
META_TEXT = {  # meta cards whose words the rules changed
    'Calm': ('No forces until your next turn.', 'was "No forces this round."; one round now'),
    'Aftershock': ('Your opponent has the next two turns.', 'was "… takes …"; "take" is kept for the ante'),
    'Stillness': ('Your opponent plays no permanence next turn.', 'was "Your opponent passes."; no passing now, and passing for the round would end their contest'),
    'Sunlight': ('Flip back every permanence.', 'was "Remove every force."; the forces on the table are flipped cards now'),
    'Thunder': ('Play a permanence after the last turn.', 'was "Play once more after both players pass."; the contest ends after the shared 10th turn'),
    'Haze': ("Your opponent can't use forces next turn.", 'was "… can\'t play forces …"; forces are used now'),
}
ROLE = dict(pass6.ROLE)

def build():
    cards, idea = [], collections.OrderedDict()
    for c in sorted(SRC['cards'], key=lambda c: c['no']):
        if 'meta' in c:
            m = c['meta']; t, why = META_TEXT.get(m['name'], (m['text'], None))
            cards.append({'no': c['no'], 'id': c['id'], 'name': m['name'], 'meta': True, 'rarity': c['rarity'], 'text': t,
                          'was': m['text'] if why else None, 'changes': [why] if why else []})
            continue
        p, f = c['permanence'], c.get('force') or {}
        n, changes = p['name'], []
        if p['text']:
            idea.setdefault(p['text'], []).append(n)
            changes.append('front text to the idea pool: "%s"' % p['text'])
        front_text = ''
        if n in BLOCKERS:
            assert len(p['affinities']) == 1 and c['rarity'] == 'C', n
            front_text = "Can be played on an opponent's world."
            changes.append('blocker: %s' % BLOCKERS[n])
        role = ROLE[n]
        if f.get('text'):
            fname, dur, ftext = f['name'], DUR[f['duration']], f['text']
            if f['duration'] == 'Lasts the round': changes.append('lasted the round; now while flipped')
        elif len(p['affinities']) >= 3:  # no extra plays on 3-pip cards (Cam, Nov 23): open
            fname, dur, ftext, role = '', '', '', 'open'
            changes.append('open: its Nov 12 extra play ("%s") stays in the idea pool. %s' % (pass6.FORCES[n][2], OFF_THREE))
        else:  # an open face: its Nov 12 extra play comes back, as one more
            fname, d0, old, _r = pass6.FORCES[n]
            dur, ftext, role = 'Once', RESTORED[old], pass6.SELF
            changes.append('extra play back from the idea pool (was "%s")' % old)
            if 'two more' in old: changes.append(ONE_MORE)
        if n in TEXT:
            ftext, why = TEXT[n]; changes.append(why)
        fb = n in FLIPS_BACK
        if fb:
            assert ftext, n
            ftext += ' Next turn, flip this back.'
            changes.append('flips back: %s' % FLIPS_BACK[n])
        back = BACK.get(n, [])
        if n in WHY_BACK: changes.append('back pips: %s' % WHY_BACK[n])
        cards.append({'no': c['no'], 'id': c['id'], 'name': n, 'rarity': c['rarity'], 'role': role,
                      'front': {'pips': p['affinities'], 'text': front_text}, 'blocker': n in BLOCKERS,
                      'back': {'name': fname, 'pips': back, 'duration': dur, 'text': ftext, 'flipsBack': fb},
                      'sixth': {'text': p['text'], 'force': f.get('name', ''), 'duration': f.get('duration', ''), 'forceText': f.get('text', '')},
                      'changes': changes})
    return cards, idea

CARDS, IDEA = build()
LAND = [c for c in CARDS if not c.get('meta')]
META = [c for c in CARDS if c.get('meta')]

def pipcount(ps): return len(ps)
def check():
    probs = []
    if [c['no'] for c in CARDS] != list(range(1, 101)): probs.append(('numbering',))
    names = collections.Counter([c['name'] for c in CARDS] + [c['back']['name'] for c in LAND if c['back']['name']])
    probs += [('duplicate name', k) for k, v in names.items() if v > 1]
    for c in LAND:
        b = c['back']
        if len(b['pips']) > len(c['front']['pips']): probs.append(('back has more pips', c['name']))
        if not b['text'] and c['role'] != 'open': probs.append(('no back text', c['name']))
        if 'two more' in b['text']: probs.append(('two more', c['name']))
        if b['text'].startswith('Play another') and len(c['front']['pips']) >= 3: probs.append(('extra play on a 3-pip card', c['name']))
        core = b['text'].replace(' Next turn, flip this back.', '')
        if words(core) >= 8: probs.append(('8+ words', c['name'], core))
        if words(b['text']) > 16: probs.append(('16+ words on a back', c['name'], b['text']))
        if c['front']['text'] and words(c['front']['text']) >= 8: probs.append(('8+ words', c['name'], c['front']['text']))
        m = re.search(r'\b(common|uncommon|rare)\b', b['text'])
        if m and {'common': 'C', 'uncommon': 'B', 'rare': 'A'}[m.group(1)] != c['rarity']: probs.append(('rarity gate', c['name'], b['text']))
        for t in (b['text'], c['front']['text'], b['name'], c['name']):
            if re.search(r'\b(hand|deal|deals|dealt|take|takes|taken|round|pass|passes)\b', t, re.I) and c['name'] != 'Pass': probs.append(('word', c['name'], t))
            if t.startswith('The '): probs.append(('"The" in a name', t))
        if any(e not in E + ['any'] and '|' not in e for e in b['pips']): probs.append(('pip', c['name'], b['pips']))
        if b['pips'] != sorted(b['pips'], key=lambda e: (E + ['any']).index(e)): probs.append(('pip order', c['name'], b['pips']))
    for m in META:
        if words(m['text']) >= 8: probs.append(('8+ words', m['name'], m['text']))
        if re.search(r'\b(hand|deal|take|takes|round|passes)\b', m['text']): probs.append(('word', m['name'], m['text']))
    bl = collections.Counter(c['front']['pips'][0] for c in LAND if c['blocker'])
    if bl != collections.Counter({e: 2 for e in E}): probs.append(('blocker cycle', dict(bl)))
    if sum(len(v) for v in IDEA.values()) != 38: probs.append(('idea pool count', sum(len(v) for v in IDEA.values())))
    return probs

def stats():
    s = collections.Counter()
    for c in LAND:
        f, b = c['front']['pips'], c['back']['pips']
        if not f: s['no pips either side'] += 1
        elif not b: s['loses every pip'] += 1
        elif len(b) == len(f): s['keeps every pip'] += 1
        else: s['loses some'] += 1
        if b and set(b) - set(x for p in f for x in p.split('|')) - {'any'}: s['changes element'] += 1
        if c['back']['flipsBack']: s['flips back'] += 1
        s['dur ' + (c['back']['duration'] or 'open')] += 1
        if c['back']['text'].startswith('Play another'): s['extra plays'] += 1
    return s

ELWORD = {'water': 'water', 'earth': 'earth', 'fire': 'fire', 'air': 'air', 'any': 'any'}
def pips_md(ps):
    if not ps: return 'none'
    out = collections.Counter(ps)
    return ', '.join('%d %s' % (n, e.replace('|', ' or ')) for e, n in sorted(out.items(), key=lambda kv: (E + ['any']).index(kv[0].split('|')[0]) if kv[0].split('|')[0] in E + ['any'] else 9))

RWORD = {'C': 'common', 'B': 'uncommon', 'A': 'rare', 'S': 'pinnacle'}
def markdown():
    s = stats()
    rows = []
    for c in LAND:
        b = c['back']
        rows.append('| %d | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            c['no'], c['name'], c['rarity'], pips_md(c['front']['pips']), c['front']['text'] or '—',
            b['name'] or '—', pips_md(b['pips']), (b['duration'] or '—') + (', flips back' if b['flipsBack'] else ''), b['text'] or 'Open: no force for the moment.'))
    mrows = ['| %d | %s | %s | %s |' % (m['no'], m['name'], m['text'], m['was'] or '—') for m in META]
    ideas = ['- "%s" (%s)' % (t, ', '.join(ns)) for t, ns in IDEA.items()]
    return f'''# Branch B card pool (first draft, Nov 23, 2026)

> Cam (Nov 23): "let's get the card pool back into a 100 card playable state like it once was. Find the last 100 card pool and update it with any changes we've made to core rules since then." On the fronts: "return the abilities to the idea pool so we don't forget about them, then create the card pool list view like before so I can look through the pool (front and back)." The void and meta cards: "Keep both". Blockers: "A cycle of eight". Everything else is Claude's draft against Branch B's settled rules, not adopted.

List view, front and back: [Branch B Card Pool](https://claude.ai/artifact/SPVNbQcNGnatLHGeF2fqow). Source: the sixth pass (design/card-pool.md; data/cards.json in the playtest repo). Data: data/cards-branch-b.json, made by tools/cards/branchb_pool.py.

**What changed, and why.**
- **Fronts are vanilla.** The {sum(len(v) for v in IDEA.values())} front abilities are in the idea pool (listed below). The only front text left is the blockers'.
- **Blockers, a cycle of eight** (two commons per element): {', '.join(c['name'] for c in LAND if c['blocker'])}. "Can be played on an opponent's world."
- **Backs have pips.** Most cards lose a pip when flipped, and every one-pip card but Bedrock loses its only pip. Counts: {s['loses every pip']} lose every pip, {s['loses some']} lose some, {s['keeps every pip']} keep every pip, {s['no pips either side']} have none on either side; {s['changes element']} change element where it's thematic (mud, obsidian, a lava coast making land).
- **Durations.** "Lasts the round" (one round now) is "while flipped": the effect lives on the flipped card, as Cave-in's does, and ends if the card is flipped back or leaves play. {s['dur Once']} once, {s['dur Until your next turn']} until your next turn, {s['dur While flipped']} while flipped, {s['dur open']} open.
- **Forces on the table are flipped cards,** so "remove a force" is "flip back" (Thaw, Sunlight).
- **The extra plays are back, one more at most, on 1- and 2-pip cards only.** They went to the idea pool on Nov 12 because "with uncapped turns, playing extra cards in a row doesnt do anything" (Cam). A Branch B turn has one landscape, so they matter again: {s['extra plays']} cards. Cam (Nov 23): "'play two more' is definitely too strong. 'Play one more' and moving it to a 1 or 2 pip card instead of a 3 pip card." The five 3-pip cards that had one ({', '.join(c['name'] for c in LAND if c['role'] == 'open')}) are open until a force is chosen.
- **{s['flips back']} cards flip back on their own,** from natural cycles: {', '.join(c['name'] for c in LAND if c['back']['flipsBack'])}.
- **Meta cards** are played in place of the turn's landscape, then go to the void (Claude's reading). Six changed words for the new turn: Calm, Aftershock, Stillness, Sunlight, Thunder, Haze.
- **Rarities** are unchanged. One-pip rares stay: Cam (Nov 23), "I'd like to have some 1 pip rares and just because I think it's interesting. we'll figure out what their effects have to be to qualify them as rares." Ice Sheet, Thicket, Badlands and Wind Gap keep their sixth-pass backs until then. The two no-pip uncommons (Mirage, Hanging Valley) were uncommon for their front text, which is now in the idea pool.

## Landscapes (86)

| No. | Card | Rarity | Front pips | Front text | Force | Back pips | Duration | Back text |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(rows)}

## Meta cards (14)

Played in place of the turn's landscape.

| No. | Card | Text | Sixth pass, where it changed |
| --- | --- | --- | --- |
{chr(10).join(mrows)}

## Front abilities, now in the idea pool (38)

{chr(10).join(ideas)}
'''

if __name__ == '__main__':
    probs = check()
    print('problems:', probs or 'none'); print(dict(stats()))
    if '--json' in sys.argv:
        out = {'pass': 'Branch B pool, first draft (Nov 23, 2026)', 'source': 'sixth pass, data/cards.json',
               'rules': 'Branch B: fronts vanilla but blockers; backs with their own pips; meta cards in place of the landscape',
               'counts': {'landscapes': len(LAND), 'meta': len(META)}, 'ideaPool': [{'text': t, 'cards': ns} for t, ns in IDEA.items()], 'cards': CARDS}
        json.dump(out, open(sys.argv[sys.argv.index('--json') + 1], 'w'), indent=1, ensure_ascii=False)
    if '--md' in sys.argv:
        open(sys.argv[sys.argv.index('--md') + 1], 'w').write(markdown())
