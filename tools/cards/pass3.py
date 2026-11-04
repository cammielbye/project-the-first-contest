# Third pass: the full pool (101 cards), text-first. Data + checks + markdown.
import collections, re, sys

# (no, name, rarity, affinities, permanence text, force name, duration, force text)
# affinities: list of 'fire' 'water' 'air' 'earth' 'any' or 'a|b' (either-or); [] = none
F, W, A, E = 'fire', 'water', 'air', 'earth'
R, O = 'round', 'once'
C_ = [
 # fire commons
 (1, 'Cinder Field', 'C', [F], '', 'Smolder', R, "An earth permanence with one affinity loses it."),
 (2, 'Dune', 'C', [F], '', 'Updraft', R, "An air permanence becomes fire."),
 (3, 'Fumarole', 'C', [F], "Returns at round end.", 'Flare-up', O, "Remove a common force."),
 (4, 'Ashfield', 'C', [F], "Ignores water forces.", 'Brushfire', R, "An earth permanence becomes fire."),
 (5, 'Lava Field', 'C', [F], "Adjacent earth permanences become fire.", 'Spark', R, "An air permanence with one affinity becomes fire."),
 (6, 'Badlands', 'C', [F], "Loses its affinities if adjacent to water.", 'Ember', R, "A lone permanence loses its affinities."),
 (7, 'Barrens', 'C', [F], "Ignores common forces.", 'Kindling', R, "An earth permanence with one affinity becomes fire."),
 # water commons
 (8, 'Lagoon', 'C', [W], '', 'Shower', R, "A fire permanence becomes water."),
 (9, 'Ice Floe', 'C', [W], '', 'Current', R, "An earth permanence becomes water."),
 (10, 'Spring', 'C', [W], "Returns at round end.", 'Low Tide', O, "Return one of your worlds."),
 (11, 'Tide Pool', 'C', [W], "Ignores air forces.", 'Drizzle', R, "A fire permanence with one affinity loses it."),
 (12, 'Shoal', 'C', [W], "Adjacent fire permanences become water.", 'Rain', R, "A fire permanence with one affinity becomes water."),
 (13, 'Fen', 'C', [W], "Loses its affinities if adjacent to air.", 'Snowmelt', R, "An earth permanence with one affinity becomes water."),
 (14, 'Snowfield', 'C', [W], "When played, return one of your permanences.", 'Freeze', R, "A world's water permanences can't be removed."),
 # air commons
 (15, 'Ledge', 'C', [A], '', 'Gust', O, "An air permanence with one affinity becomes its own world."),
 (16, 'Ridge', 'C', [A], '', 'Breeze', R, "A water permanence with one affinity becomes air."),
 (17, 'Eyrie', 'C', [A], "Returns at round end.", 'Drift', O, "Move one of your permanences to another world."),
 (18, 'Summit', 'C', [A], "Ignores earth forces.", 'Crosswind', O, "Swap two permanences between worlds."),
 (19, 'Peak', 'C', [A], "Adjacent water permanences become air.", 'Thermal', R, "A fire permanence with one affinity becomes air."),
 (20, 'Wind Gap', 'C', [A], "Loses its affinities if adjacent to earth.", 'Downdraft', O, "A fire permanence with one affinity becomes its own world."),
 (21, 'Bluff', 'C', [A], "When played, move one of your permanences.", 'Eddy', O, "Swap two permanences in a world."),
 # earth commons
 (22, 'Hill', 'C', [E], '', 'Rockfall', R, "An air permanence becomes earth."),
 (23, 'Grove', 'C', [E], "Returns at round end.", 'Overgrowth', R, "One of your worlds ignores common forces."),
 (24, 'Stone Field', 'C', [E], "Ignores fire forces.", 'Dust', R, "An air permanence with one affinity loses it."),
 (25, 'Meadow', 'C', [E], "Adjacent air permanences become earth.", 'Silt', R, "A water permanence with one affinity becomes earth."),
 (26, 'Moor', 'C', [E], "Loses its affinities if adjacent to fire.", 'Dustfall', R, "An air permanence with one affinity becomes earth."),
 (27, 'Bedrock', 'C', [E], "Can't be moved.", 'Tangle', R, "A world's permanences can't be moved."),
 (28, 'Thicket', 'C', [E], "Your adjacent permanences can't be moved.", 'Shelter', R, "A permanence can't be moved or removed."),
 # either-or commons
 (29, 'Flint', 'C', ['fire|earth'], '', 'Sinkhole', O, "An earth permanence with one affinity becomes its own world."),
 (30, 'Scrubland', 'C', ['fire|air'], '', 'Dust Devil', R, "An earth permanence becomes air."),
 (31, 'Steam Vent', 'C', ['fire|water'], '', 'Vent', O, "Return one of your permanences."),
 (32, 'Marsh', 'C', ['water|earth'], '', 'Mire', R, "A world of two can't grow."),
 (33, 'Sea Stack', 'C', ['water|air'], '', 'Riptide', R, "An air permanence becomes water."),
 (34, 'Pass', 'C', ['air|earth'], '', 'Whirl', O, "Move a permanence to another world."),
 (35, 'Hot Mud', 'C', ['fire|water'], "Ignores air and earth forces.", 'Steam', R, "A world of three can't grow."),
 (36, 'Heath', 'C', ['fire|air'], "Ignores water and earth forces.", 'Dry Wind', R, "A water permanence becomes air."),
 (37, 'Peat Bog', 'C', ['fire|earth'], "Ignores water and air forces.", 'Firebreak', R, "Your worlds ignore fire forces."),
 (38, 'Spray Coast', 'C', ['water|air'], "Ignores fire and earth forces.", 'Drying Wind', R, "A water permanence with one affinity loses it."),
 (39, 'Mudflat', 'C', ['water|earth'], "Ignores fire and air forces.", 'Tremor', O, "A world of two splits apart."),
 (40, 'Foothills', 'C', ['air|earth'], "Ignores fire and water forces.", 'Windbreak', R, "Your worlds ignore air forces."),
]
B_ = [
 # two different affinities, no text
 (41, 'Hot Spring', 'B', [F, W], '', 'Scald', O, "Remove a fire or earth permanence with one affinity."),
 (42, 'Desert', 'B', [F, A], '', 'Heatwave', R, "Two earth permanences lose their affinities."),
 (43, 'Volcano', 'B', [F, E], '', 'Lava Bomb', O, "Remove an earth or air permanence with one affinity."),
 (44, 'Cloud Forest', 'B', [W, A], '', 'Fog', R, "A world can't grow."),
 (45, 'Delta', 'B', [W, E], '', 'Flood', O, "Return two adjacent permanences."),
 (46, 'Sea Cliff', 'B', [A, E], '', 'Gale', O, "Move two permanences to other worlds."),
 # two different affinities, with text
 (47, 'Mud Pots', 'B', [F, W], "Your adjacent permanences ignore air forces.", 'Downpour', R, "A world's fire permanences become water."),
 (48, 'Savanna', 'B', [F, A], "Your adjacent permanences ignore water forces.", 'Sandstorm', R, "A world's earth permanences become fire."),
 (49, 'Cinder Cone', 'B', [F, E], "Your adjacent permanences ignore fire forces.", 'Ashfall', R, "A world's air permanences lose their affinities."),
 (50, 'Waterfall', 'B', [W, A], "Your adjacent permanences ignore earth forces.", 'Cloudburst', R, "A permanence becomes water."),
 (51, 'Mangrove', 'B', [W, E], "Can't be moved.", 'Undertow', O, "Return a world of two."),
 (52, 'Canyon', 'B', [A, E], "Its world can't be split.", 'Dust Storm', R, "A world's air permanences become earth."),
 # two of the same affinity (one cycle)
 (53, 'Lava Lake', 'B', [F, F], '', 'Heat Dome', R, "Fire permanences can't be removed."),
 (54, 'Deep Lake', 'B', [W, W], '', 'Ice Storm', R, "Water permanences can't be moved."),
 (55, 'Twin Peaks', 'B', [A, A], '', 'High Pressure', R, "Air permanences can't be removed."),
 (56, 'Plateau', 'B', [E, E], '', 'Permafrost', R, "Earth permanences can't be moved."),
 # the wildcard and Mirage
 (57, 'Wilderness', 'B', ['any'], '', 'Thunderstorm', O, "Remove a ◯ permanence."),
 (58, 'Mirage', 'B', [], "Copies every adjacent permanence's affinities.", 'Heat Shimmer', R, "A permanence copies an adjacent permanence."),
 # one affinity, stronger effects
 (59, 'Lava Flow', 'B', [F], "When played, play another fire card.", 'Lightning', O, "Remove a lone permanence."),
 (60, 'Obsidian', 'B', [F], "Your fire permanences ignore water forces.", 'Scorch', R, "A world's earth permanences lose their affinities."),
 (61, 'Tidal Flat', 'B', [W], "Your water permanences ignore air forces.", 'Hail', O, "Remove a fire or air permanence with one affinity."),
 (62, 'Glacier', 'B', [W], "Can't be moved. Ignores air forces.", 'Thaw', O, "Remove a force."),
 (63, 'Spire', 'B', [A], "Can't be moved. Ignores earth forces.", 'Whirlwind', O, "Two permanences become separate worlds."),
 (64, 'Hanging Valley', 'B', [A], "When played, swap two of your permanences.", 'Squall', O, "A permanence becomes its own world."),
 (65, 'Sky Isle', 'B', [A], "Your air permanences ignore earth forces.", 'Waterspout', R, "A world's water permanences become air."),
 (66, 'Hidden Valley', 'B', [E], "Your earth permanences ignore fire forces.", 'Landslide', O, "Remove an air or water permanence with one affinity."),
 (67, 'Old Growth', 'B', [E], "Its world's permanences can't be moved.", 'Bramble', R, "Your worlds' permanences can't be moved."),
 (68, 'Cavern', 'B', [E], "Ignores common and uncommon forces.", 'Cave-in', O, "Remove two adjacent ◯ permanences."),
]
A_ = [
 # three different elements
 (69, 'Caldera Lake', 'A', [F, W, E], '', 'Collapse', O, "Remove a permanence."),
 (70, 'Geyser Basin', 'A', [F, W, A], '', 'Typhoon', O, "A world's permanences become separate worlds."),
 (71, 'Red Canyon', 'A', [F, A, E], '', 'Firestorm', R, "A world becomes fire."),
 (72, 'Rainforest', 'A', [W, A, E], '', 'Monsoon', O, "Return every lone permanence."),
 # two and one
 (73, 'Lava Coast', 'A', [F, F, W], '', 'Steam Explosion', R, "Two adjacent permanences lose their affinities."),
 (74, 'Sand Sea', 'A', [F, F, A], '', 'Drought', O, "Remove a world's water permanences."),
 (75, 'Lava Plain', 'A', [F, F, E], '', 'Wildfire', O, "Remove a world's earth permanences."),
 (76, 'Boiling Lake', 'A', [W, W, F], '', 'Flash Flood', O, "Remove a world's fire permanences."),
 (77, 'Misty Fjord', 'A', [W, W, A], '', 'Whiteout', R, "Worlds can't grow until your next turn."),
 (78, 'Archipelago', 'A', [W, W, E], "At the start of your turn, if you have 8 water, you win the round.", 'Tsunami', R, "A world becomes water."),
 (79, 'High Desert', 'A', [A, A, F], '', 'Tornado', O, "Return two permanences."),
 (80, 'Cloud Sea', 'A', [A, A, W], '', 'Hurricane', O, "Rearrange a player's worlds."),
 (81, 'Stone Towers', 'A', [A, A, E], '', 'Gale Force', O, "Move three permanences to other worlds."),
 (82, 'Smoking Hills', 'A', [E, E, F], '', 'Eruption', R, "A world loses its affinities."),
 (83, 'Floodplain', 'A', [E, E, W], '', 'Mudflow', O, "Return a world of three."),
 (84, 'Highlands', 'A', [E, E, A], '', 'Earthquake', O, "Split each of a player's worlds."),
 # rares with a special permanence
 (85, 'Ice Sheet', 'A', [W], "Fire permanences lose their affinities.", 'Blizzard', O, "Return a world."),
 (86, 'Mountain Range', 'A', [A, E], "Score a point per four earth affinities.", 'Avalanche', O, "Remove a world's air permanences."),
 (87, 'Massif', 'A', [E], "Your worlds ignore common forces.", 'Uplift', R, "A world ignores all forces."),
 (88, 'Cradle', 'A', [], "At the start of your turn, if you have 3 of each affinity, you win the contest.", 'Equinox', O, "Return 3 cards from your void."),
]
META = [  # (no, name, rarity, text)
 (89, 'Echo', 'B', "Play a card from your void."),
 (90, 'Ebb', 'B', "Remove your opponent's last common."),
 (91, 'Verge', 'B', "Play two more cards this turn."),
 (92, 'Horizon', 'B', "Remove a card from your opponent's binder."),
 (93, 'Hollow', 'B', "Return a card from your void."),
 (94, 'Calm', 'B', "No forces this round."),
 (95, 'Lull', 'A', "Your opponent skips their next turn."),
]
S_ = [
 (96, 'Core', 'S', [F] * 4, '', 'Solar Flare', O, "Remove every ◯ permanence."),
 (97, 'Ocean', 'S', [W] * 4, '', 'Deluge', R, "Two worlds lose their affinities."),
 (98, 'Pangaea', 'S', [E] * 4, '', 'World Quake', O, "Every permanence becomes its own world."),
 (99, 'Trade Winds', 'S', [A] * 4, '', 'Jet Stream', O, "Every permanence becomes its own world."),
]
GAP = (100, 'Gap', 'S', "Remove a world.")
ORIGIN = (101, 'Origin', 'S', [F, W, A, E], '', 'Unmaking', O, "Remove every world.")

ALL = C_ + B_ + A_ + S_ + [ORIGIN]
EXCEPTIONS = {'Archipelago', 'Cradle'}  # Cam's own wording for the alternate wins (CARD-23 exceptions)

FAMILY = [
 ('Remove', r'^Remove (an?|two|every|a world)|Remove a (fire|water|air|earth|lone|permanence)|^Remove a ◯|^Remove two'),
 ('Return', r'^Return|returns? one'),
 ('Lose affinities', r'lose(s)? (its|their) affinities'),
 ('Change element', r'becomes? (fire|water|air|earth)'),
 ('Move, swap or split', r'^Move|^Swap|own world|separate worlds|splits?|Split|Rearrange'),
 ('Protect', r"can't be (moved|removed)|ignores?"),
 ('Stop growth', r"can't grow"),
]
def family(t):
    for name, rx in FAMILY:
        if re.search(rx, t): return name
    return 'Other'

def words(t): return len(t.replace('—', ' ').split())

def check():
    probs = []
    names = collections.Counter([c[1] for c in ALL] + [m[1] for m in META] + [GAP[1]])
    for n, k in names.items():
        if k > 1: probs.append(('duplicate name', n))
    fnames = collections.Counter([c[5] for c in ALL])
    for n, k in fnames.items():
        if k > 1: probs.append(('duplicate force name', n))
    pn = set(names); clash = pn & set(fnames)
    for n in clash: probs.append(('name used on both faces', n))
    texts = collections.Counter([c[7] for c in ALL] + [m[3] for m in META] + [GAP[3]])
    for t, k in texts.items():
        if k > 1: probs.append(('duplicate force text', t))
    ptexts = collections.Counter([c[4] for c in ALL if c[4]])
    for t, k in ptexts.items():
        if k > 1 and 'Returns at round end' not in t: probs.append(('repeated permanence text x%d' % k, t))
    for c in ALL:
        for t in (c[4], c[7]):
            if t and words(t) >= 8 and c[1] not in EXCEPTIONS: probs.append(('8+ words', c[1], t, words(t)))
    for m in META + [GAP]:
        if words(m[3]) >= 8: probs.append(('8+ words', m[1], m[3]))
    nums = sorted([c[0] for c in ALL] + [m[0] for m in META] + [GAP[0]])
    if nums != list(range(1, 102)): probs.append(('numbering', [n for n in range(1, 102) if n not in nums]))
    for c in ALL:
        if c[2] == 'C' and len(c[3]) != 1: probs.append(('common must have one affinity', c[1]))
    trip = [tuple(sorted(c[3])) for c in A_ if len(c[3]) == 3]
    if len(set(trip)) != 16 or len(trip) != 16: probs.append(('triples', len(trip), len(set(trip))))
    return probs

def tally():
    t = collections.Counter()
    for c in ALL:
        if c[0] == 101: continue
        for a in c[3]:
            if '|' in a:
                for x in a.split('|'): t[x + ' (either-or)'] += 1
            else: t[a] += 1
    return t

if __name__ == '__main__':
    p = check()
    print('problems:', len(p))
    for x in p: print('  ', x)
    t = tally()
    for e in [F, W, A, E]: print(e, t[e], '+', t[e + ' (either-or)'], 'either-or')
    print('any', t['any'])
    rc = collections.Counter(c[2] for c in ALL if c[0] != 101)
    print('rarity', dict(rc), 'meta', len(META), '+ Gap')
    fam = collections.Counter((c[2], family(c[7])) for c in ALL)
    for r in 'CBAS':
        print(r, {k[1]: v for k, v in fam.items() if k[0] == r})
    others = [(c[1], c[5], c[7]) for c in ALL if family(c[7]) == 'Other']
    print('other:', others)
    ntext = collections.Counter(c[2] for c in ALL if not c[4] and c[0] != 101)
    print('no permanence text by rarity', dict(ntext))
