import collections
from pass3 import *

def aff_cell(affs):
    if not affs: return 'none'
    out = []; cnt = collections.Counter()
    order = []
    for a in affs:
        if a not in cnt: order.append(a)
        cnt[a] += 1
    for a in order:
        if '|' in a: out.append('%d either-or (%s or %s)' % ((cnt[a],) + tuple(a.split('|'))))
        else: out.append('%d %s' % (cnt[a], a))
    return ', '.join(out)

def row(c):
    no, name, rar, affs, pt, fn, dur, ft = c
    return '| %d | %s | %s | %s | %s | %s | %s | %s |' % (no, name, rar, aff_cell(affs), pt or '—', fn, 'Lasts the round' if dur == R else 'Once', ft)

HEAD = '| No. | Permanence | Rarity | Affinities | Permanence text | Force | Duration | Force text |\n| --- | --- | --- | --- | --- | --- | --- | --- |'
def table(title, cards):
    return '**%s (%d)**\n\n%s\n%s\n' % (title, len(cards), HEAD, '\n'.join(row(c) for c in cards))

t = tally()
groups = [
 ('Fire commons', [c for c in C_ if c[0] <= 7]),
 ('Water commons', [c for c in C_ if 8 <= c[0] <= 14]),
 ('Air commons', [c for c in C_ if 15 <= c[0] <= 21]),
 ('Earth commons', [c for c in C_ if 22 <= c[0] <= 28]),
 ('Either-or commons', [c for c in C_ if c[0] >= 29]),
 ('Uncommons with two affinities', [c for c in B_ if c[0] <= 52]),
 ('Uncommons with two of the same affinity', [c for c in B_ if 53 <= c[0] <= 56]),
 ('Uncommons, the wildcard and Mirage', [c for c in B_ if 57 <= c[0] <= 58]),
 ('Uncommons with one affinity', [c for c in B_ if c[0] >= 59]),
 ('Rares with three affinities', [c for c in A_ if c[0] <= 84]),
 ('Rares with a special permanence', [c for c in A_ if c[0] >= 85]),
 ('Pinnacles, and card 101', S_ + [ORIGIN]),
]
binA = ('Binder A, Tides', 'Water and air, built around Ocean, with Archipelago as its alternate win.',
  ['Ocean', 'Archipelago', 'Cloud Sea', 'Rainforest', 'Geyser Basin', 'Cloud Forest', 'Waterfall', 'Delta', 'Hot Spring', 'Glacier', 'Mirage', 'Deep Lake', 'Sky Isle',
   'Lagoon', 'Spring', 'Tide Pool', 'Snowfield', 'Ledge', 'Eyrie', 'Bluff', 'Sea Stack', 'Steam Vent', 'Foothills', 'Echo', 'Calm'])
binB = ('Binder B, Embers', 'Fire and earth, built around Core, with Mountain Range for stacking earth.',
  ['Core', 'Caldera Lake', 'Lava Plain', 'Red Canyon', 'Mountain Range', 'Volcano', 'Desert', 'Savanna', 'Cinder Cone', 'Lava Flow', 'Obsidian', 'Hidden Valley', 'Plateau',
   'Cinder Field', 'Fumarole', 'Ashfield', 'Lava Field', 'Flint', 'Hill', 'Grove', 'Bedrock', 'Hot Mud', 'Pass', 'Ebb', 'Lull'])
names = set(c[1] for c in ALL) | set(m[1] for m in META)
for b in (binA, binB):
    miss = [x for x in b[2] if x not in names]; assert not miss and len(b[2]) == 25 and len(set(b[2])) == 25, (b[0], miss, len(b[2]))

intro = f'''## Third pass: the full pool, 101 cards (Nov 2, 2026)

> Claude's draft at Cam's request, nothing Decided. This is the third pass with both faces; the Oct 31 section further down, also called a third pass, covered permanence faces only. Built from Cam's walkthrough of every effect bucket (design/third-pass-brief.md). Text-first: no faces drawn yet. Commons 1–40, uncommons 41–68, rares 69–88, fifth-pillar meta cards 89–95, pinnacles 96–100 (the fifth-pillar pinnacle at 100), and card 101 outside the pool (CARD-13).

**How the text reads.** One wording per idea, used the same way on every card:

- **loses its affinities**: counts toward neither world points nor affinity.
- **adjacent**: shares a side in a 2×2; diagonal cards aren't adjacent.
- **remove**: to its owner's void. **return**: to its owner's binder.
- **lone**: alone in its world. **one of yours**: one of your permanences.
- **a fire permanence**: any permanence showing fire, an either-or included.
- **◯ permanence**: a permanence with one affinity, an either-or included (drawn as a single ring on the card).
- **can't be moved** and **ignores … forces** are the only protection wordings. Nothing in the pool says "can't be removed" on its own permanence.
- **A force has its card's elements.** Gust is an air force because Ledge is air; Hot Spring's Scald is both a fire and a water force. Force tiers follow card rarity: common forces are everyday weather, uncommon ones are severe, rare ones are disasters.
- **"When played"** effects happen once, as the permanence goes down.

**The elemental cycle (Claude's proposal, not adopted).** Each element presses on one other: water douses fire, fire burns earth, earth blocks air, air dries water. At common, removal and "loses its affinities" follow it (fire removes or blanks earth, water fire, earth air, air water); uncommons reach two elements or two cards; rares reach any permanence or a whole world. The same cycle sets which forces a single-affinity common ignores (its predator's: "Ashfield ignores water forces"), which neighbor it turns to its own element ("Lava Field turns adjacent earth to fire"), and which neighbor it can't stand ("Badlands loses its affinities if adjacent to water"). Conversion forces are looser: each element has one that follows the cycle and one that doesn't.

**What's new from the brief.** All 16 three-affinity rares (four with three different elements, twelve two-and-one splits); one cycle of two-of-the-same uncommons; a wildcard uncommon (Wilderness); twelve either-or commons, six of them ignoring the forces of the two elements they lack; one cycle of commons that return to the binder at round end (Fumarole, Spring, Eyrie, Grove); returns only for several cards, a whole world, or your own card as bait; more moves, mostly air; removal climbing by element; Archipelago at 8 water, checked at the start of your turn; Cradle, which wins the contest with 3 of each affinity; Mirage copying every adjacent card with no affinity of its own; Lull at rare; Echo and Ebb limited to commons; Horizon as a binder discard.

**Gone from the second pass.** Permanence played on another card (Snowfield, Glacier and Salt Flat's old faces), Petrified Forest, "also counts as" forces, Shimmer and Haze, and counting double toward affinity.

**Counts.** {len(C_)} commons, {len(B_)} uncommons, {len(A_)} rares, {len(S_)} elemental pinnacles, {len(META)} meta cards and the Gap, plus card 101. Affinities across the 100: fire {t[F]}, water {t[W]}, air {t[A]}, earth {t[E]}, plus {t[F+' (either-or)']} either-or capsules for each element and one wildcard. Rules text stays under 8 words except Archipelago and Cradle, which keep Cam's wording for their win conditions.

**Keep me honest (CORE-07).** These could be fun for one player and miserable for the other, so they're the first to watch in testing: Great Uplift (Pangaea's force, your worlds ignore all forces for the round), Massif (your worlds ignore common forces, all the time), Calm (no forces until your next turn), Whiteout (no world grows until your next turn), the four element-wide protections on the two-of-the-same uncommons, and Lull. Each one either lasts a single round or turn, can itself be removed (Thaw removes a force), or applies to both players.

**Open.** The cycle above; whether the commons' restriction text ("Loses its affinities if adjacent to water") is worth its words; Horizon's final shape; card 101's force; names that may sit at the wrong tier.
'''

md = intro + '\n' + '\n'.join(table(g, cs) for g, cs in groups)
md += '\n**Fifth-pillar meta cards, uncommon (6).** One face, usable by either player.\n\n| Card | No. | Text |\n| --- | --- | --- |\n' + '\n'.join('| %s | %d | %s |' % (m[1], m[0], m[3]) for m in META if m[2] == 'B') + '\n'
md += '\n**Fifth-pillar meta cards, rare (1).**\n\n| Card | No. | Text |\n| --- | --- | --- |\n' + '\n'.join('| %s | %d | %s |' % (m[1], m[0], m[3]) for m in META if m[2] == 'A') + '\n'
# (Gap, the meta pinnacle at #100, was cut on Nov 8.)
md += '\n**Two test binders** of 25, one of each card, for the table and the simulator:\n\n'
for b in (binA, binB): md += '- **%s.** %s %s.\n' % (b[0], b[1], ', '.join(b[2]))
open('pass3.md', 'w').write(md)
print(len(md.splitlines()), 'lines')
