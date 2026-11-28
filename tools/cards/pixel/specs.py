# One scene per card for the framework set. Backs are the same place when its force is used.
def F(name, **kw): return (name, kw)
L = {
 'Glacier': dict(sky='arctic', hz=0.56, feats=[F('glacier')], extras=[F('clouds', n=2)]),
 'Bedrock': dict(sky='dusk', far='ridges', feats=[F('mesa', w=34, h=7, pal='stone')], ground='rock', extras=[F('rocks', n=8)]),
 'Lava Field': dict(sky='red', far='ridges', farcol='#2A1414', ground='ash', gtop=0.6, extras=[F('cracks', n=7, col='#D0663F'), F('embers', n=14), F('smoke', x=36, n=6)]),
 'Spire': dict(sky='day', hz=0.7, feats=[F('spire', h=34)], ground='rock', extras=[F('clouds', n=3), F('birds', n=2)]),
 'Stone Field': dict(sky='overcast', far='hills', farcol='#4A4E52', ground='rock', gtop=0.56, extras=[F('rocks', n=18), F('boulders', n=4)]),
 'Ashfield': dict(sky='haze', far='ridges', farcol='#6A6058', ground='ash', gtop=0.6, feats2=[F('trees', n=6, pal='black', size=4)], extras=[F('embers', n=10)]),
 'Summit': dict(sky='day', far='mountains', farcol='#5E7088', feats=[F('peak', h=26, snow=5)], extras=[F('fog', y0=26, h=10, col='#E2E8EC')]),
 'Snowfield': dict(sky='arctic', far='mountains', farcol='#7A90A8', ground='snow', gtop=0.58, feats2=[F('trees', n=4, pal='black', size=4, y0=30)], extras=[F('snow', n=26)]),
 'Grove': dict(sky='day', ground='grass', gtop=0.66, feats2=[F('trees', n=7, conifer=False, size=6, y0=33)], extras=[F('birds', n=2), F('flowers', n=10)]),
 'Lava Flow': dict(sky='dusk', feats=[F('hill', w=26, h=14, pal='dark')], ground='ash', gtop=0.72, extras=[F('lava', x=22, y=16, n=3), F('glow')]),
 'Bluff': dict(sky='dawn', hz=0.58, water_far=[F('sea')], feats=[F('cliff', side='right', top=16)], extras=[F('birds', n=3)]),
 'Marsh': dict(sky='overcast', ground='moss', gtop=0.6, water=[F('lake', pal='storm', rx=18)], extras=[F('reeds', n=18), F('fog', y0=24, h=6)]),
 'Steam Vent': dict(sky='storm', far='ridges', ground='rock', gtop=0.6, extras=[F('cracks', n=4), F('steam', xs=[14, 26, 36], y=40)]),
 'Sea Stack': dict(sky='dawn', hz=0.52, water_far=[F('sea')], feats=[F('stack', cx=30, h=20)], extras=[F('birds', n=3)]),
 'Flint': dict(sky='dusk', far='hills', farcol='#2A2630', ground='dark', gtop=0.6, extras=[F('rocks', n=14, col='#5A5E64'), F('embers', n=6)]),
 'Pass': dict(sky='day', feats=[F('canyon', pal='stone', gap=16)], ground='rock', gtop=0.8, extras=[F('clouds', n=2), F('snow', n=8)]),
 'Scrubland': dict(sky='haze', ground='sand', gtop=0.6, feats2=[F('trees', n=9, pal='olive', size=2.5, conifer=False, y0=36)], extras=[F('sun', x=12, r=3)]),
 'Wilderness': dict(sky='day', far='mountains', feats=[F('range', pal='stone', snow=2, n=3, hmax=16)], ground='grass', gtop=0.68, feats2=[F('trees', n=6, size=5, y0=34)], extras=[F('birds', n=2)]),
 'Delta': dict(sky='day', hz=0.5, water_far=[F('sea')], ground='mud', gtop=0.6, water=[F('river', pal='blue')], extras=[F('reeds', n=12), F('birds', n=2)]),
 'Hot Spring': dict(sky='dawn', ground='rock', gtop=0.58, water=[F('lake', pal='hot', rx=14)], extras=[F('steam', xs=[16, 26, 32], y=34)]),
 'Cloud Forest': dict(sky='teal', feats=[F('hill', w=30, h=16, pal='green')], feats2=[F('trees', n=10, size=5, y0=28)], extras=[F('fog', y0=18, h=12, col='#B8C8C8')]),
 'Sea Cliff': dict(sky='day', hz=0.5, water_far=[F('sea')], feats=[F('cliff', side='left', top=14)], extras=[F('birds', n=3), F('clouds', n=2)]),
 'Desert': dict(sky='haze', hz=0.56, feats=[F('dunes', n=3)], extras=[F('sun', x=34, y=8, r=4), F('shimmer')]),
 'Mangrove': dict(sky='teal', hz=0.58, water_far=[F('sea', pal='teal')], feats2=[F('trees', n=6, conifer=False, size=4, y0=30)], extras=[F('reeds', n=14, y0=34)]),
 'Mud Pots': dict(sky='overcast', ground='mud', gtop=0.56, water=[F('lake', pal='mud', rx=10, cx=16), F('lake', pal='mud', rx=8, cx=34, cy=38)], extras=[F('steam', xs=[14, 34], y=34)]),
 'Waterfall': dict(sky='day', hz=0.66, feats=[F('mesa', w=60, h=20, pal='stone')], water=[F('fall', x0=21, top=10), F('lake', pal='blue', rx=16, cy=38)], extras=[F('fog', y0=28, h=4)]),
 'Cinder Cone': dict(sky='dusk', feats=[F('cone', h=18, crater=4, pal='dark')], ground='ash', gtop=0.72, extras=[F('smoke', x=24, y=8, n=8)]),
 'Canyon': dict(sky='day', feats=[F('canyon', pal='red', gap=14)], water=[F('river', pal='blue')], extras=[F('birds', n=2)]),
 'Savanna': dict(sky='gold', ground='sand', gtop=0.66, feats2=[F('bigtree', cx=30, pal='olive')], extras=[F('sun', x=12, y=20, r=4, col='#F2C27A'), F('birds', n=2)]),
 'Spring': dict(sky='day', ground='grass', gtop=0.6, water=[F('lake', pal='teal', rx=10)], extras=[F('reeds', n=8), F('flowers', n=12)]),
 'Mountain Range': dict(sky='day', far='mountains', farcol='#6A7C94', feats=[F('range', pal='snowrock', snow=3, n=5, hmax=22)], ground='grass', gtop=0.76),
 'Fumarole': dict(sky='haze', ground='rock', gtop=0.56, extras=[F('cracks', n=5), F('steam', xs=[10, 20, 30, 40], y=40), F('rocks', n=6, col='#B8A84A')]),
 'Sky Isle': dict(sky='day', hz=0.9, feats=[F('island', cy=16, w=14)], water=[F('fall', x0=30, top=18)], extras=[F('clouds', n=4), F('birds', n=2)]),
 'Tidal Flat': dict(sky='dawn', hz=0.5, water_far=[F('sea', depth=5)], ground='shore', gtop=0.6, water=[F('lake', pal='blue', rx=6, cx=14, cy=36), F('lake', pal='blue', rx=8, cx=34, cy=40)], extras=[F('birds', n=3)]),
 'Old Growth': dict(sky='teal', ground='moss', gtop=0.78, feats2=[F('trees', n=5, size=8, y0=40), F('bigtree', cx=24)], extras=[F('fog', y0=30, h=6, col='#9AB0A8')]),
 'Obsidian': dict(sky='night', ground='dark', gtop=0.7, feats=[F('towers', pal='black', n=4, hmax=16)], extras=[F('stars', n=18), F('moon')]),
 'Hidden Valley': dict(sky='dawn', feats=[F('canyon', pal='stone', gap=28)], ground='grass', gtop=0.72, water=[F('river', pal='teal')], feats2=[F('trees', n=5, size=3, y0=38)]),
 'Deep Lake': dict(sky='dusk', far='mountains', farcol='#2A2838', ground='grass', gtop=0.6, water=[F('lake', pal='deep', rx=22)], extras=[F('stars', n=10)]),
 'Plateau': dict(sky='day', feats=[F('mesa', w=30, h=14, pal='earth')], ground='sand', gtop=0.66, extras=[F('clouds', n=3)]),
 'Lava Lake': dict(sky='red', ground='ash', gtop=0.58, water=[F('lake', pal='lava', rx=18)], extras=[F('embers', n=18), F('glow')]),
 'Twin Peaks': dict(sky='dawn', far='mountains', farcol='#55687C', feats=[F('peak', cx=15, h=20, snow=3), F('peak', cx=34, h=22, snow=3)], ground='snow', gtop=0.66, extras=[F('clouds', n=2)]),
 'Mirage': dict(sky='haze', hz=0.56, feats=[F('dunes', n=2)], water=[F('lake', pal='ice', rx=20, ry=2, cy=29)], extras=[F('shimmer', col='#F0E4C0'), F('sun', x=36, y=7, r=3)]),
 'Caldera Lake': dict(sky='dawn', feats=[F('cone', h=16, crater=20, pal='earth', glow=False, lake='#3A8290')], ground='grass', gtop=0.74, extras=[F('clouds', n=2)]),
 'Rainforest': dict(sky='teal', ground='moss', gtop=0.76, feats2=[F('trees', n=16, size=7, conifer=False, y0=42)], extras=[F('rain', n=24, col='#8AA8A0'), F('birds', n=2)]),
 'Geyser Basin': dict(sky='day', ground='rock', gtop=0.6, water=[F('lake', pal='hot', rx=8, cx=14, cy=38)], extras=[F('geyser', x=32, y=40, h=24), F('steam', xs=[14], y=36)]),
 'Red Canyon': dict(sky='gold', feats=[F('canyon', pal='red', gap=10)], extras=[F('sun', x=24, y=8, r=3)]),
 'Archipelago': dict(sky='day', hz=0.44, water_far=[F('sea')], feats=[F('hill', cx=10, w=6, h=5), F('hill', cx=28, w=8, h=8), F('hill', cx=42, w=5, h=4)], extras=[F('birds', n=2), F('clouds', n=2)]),
 'Boiling Lake': dict(sky='storm', ground='rock', gtop=0.56, water=[F('lake', pal='hot', rx=19)], extras=[F('steam', xs=[10, 18, 26, 34, 40], y=38)]),
 'Misty Fjord': dict(sky='overcast', hz=0.56, water_far=[F('sea', pal='deep')], feats=[F('canyon', pal='stone', gap=20)], extras=[F('fog', y0=18, h=12)]),
 'Floodplain': dict(sky='storm', ground='grass', gtop=0.6, water=[F('lake', pal='storm', rx=22, ry=6), F('river', pal='storm')], extras=[F('rain', n=30)]),
 'Smoking Hills': dict(sky='dusk', feats=[F('hill', cx=14, w=14, h=12, pal='earth'), F('hill', cx=34, w=16, h=15, pal='earth')], ground='ash', gtop=0.78, extras=[F('smoke', x=14, y=16, n=6), F('smoke', x=34, y=12, n=8)]),
 'Highlands': dict(sky='overcast', feats=[F('range', pal='olive', n=4, hmax=12)], ground='moss', gtop=0.66, extras=[F('fog', y0=22, h=6), F('rocks', n=8)]),
 'Lava Coast': dict(sky='red', hz=0.5, water_far=[F('sea')], feats=[F('cliff', side='right', top=16, pal='dark', grass=False)], extras=[F('lava', x=36, y=16, n=2), F('steam', xs=[26, 30], y=26)]),
 'Lava Plain': dict(sky='dusk', far='ridges', ground='ash', gtop=0.56, extras=[F('cracks', n=10, col='#F2A23A'), F('glow', col='#7A2A18'), F('embers', n=8)]),
 'Sand Sea': dict(sky='gold', hz=0.5, feats=[F('dunes', n=4)], extras=[F('sun', x=36, y=6, r=4, col='#F4D29A')]),
 'Cloud Sea': dict(sky='dawn', hz=0.7, feats=[F('peak', h=24, snow=4)], extras=[F('fog', y0=20, h=16, col='#E2E6EA'), F('clouds', n=2)]),
 'Stone Towers': dict(sky='day', feats=[F('towers', n=5, hmax=26)], ground='rock', gtop=0.68, extras=[F('clouds', n=2), F('birds', n=2)]),
 'High Desert': dict(sky='gold', feats=[F('mesa', cx=34, w=16, h=16, pal='red')], ground='sand', gtop=0.66, extras=[F('cactus', n=4), F('sun', x=10, y=8, r=3)]),
 'Lagoon': dict(sky='day', hz=0.46, water_far=[F('sea', pal='teal')], ground='sand', gtop=0.6, water=[F('lake', pal='teal', rx=19, ry=6)], feats2=[F('trees', n=3, size=3, conifer=False, y0=29)]),
 'Moor': dict(sky='overcast', feats=[F('hill', w=30, h=8, pal='olive')], ground='moss', gtop=0.6, extras=[F('fog', y0=24, h=8), F('rocks', n=6)]),
 'Cinder Field': dict(sky='red', far='ridges', farcol='#241010', ground='ash', gtop=0.52, extras=[F('embers', n=40), F('cracks', n=6, col='#D0663F'), F('smoke', x=12, y=20, n=5)]),
 'Peak': dict(sky='arctic', far='mountains', farcol='#7088A0', feats=[F('peak', h=27, snow=6, w=0.68)], extras=[F('clouds', n=2), F('wind', n=6)]),
 'Ice Sheet': dict(sky='night', hz=0.5, ground='ice', gtop=0.5, extras=[F('aurora'), F('stars', n=12), F('cracks', n=5, col='#5E7E94')]),
 'Thicket': dict(sky='teal', ground='moss', gtop=0.6, feats2=[F('trees', n=20, size=5, conifer=False, y0=44), F('trees', n=10, size=4, conifer=False, y0=36)]),
 'Badlands': dict(sky='haze', feats=[F('towers', pal='red', n=5, hmax=14)], ground='red', gtop=0.64, extras=[F('cracks', n=5)]),
 'Wind Gap': dict(sky='overcast', feats=[F('canyon', pal='stone', gap=10)], extras=[F('wind', n=16)]),
 'Ice Floe': dict(sky='arctic', hz=0.48, water_far=[F('sea', pal='deep')], water=[F('lake', pal='ice', rx=9, ry=2.2, cx=15, cy=31), F('lake', pal='ice', rx=6, ry=1.6, cx=34, cy=27), F('lake', pal='ice', rx=4, ry=1.2, cx=40, cy=38)], extras=[F('clouds', n=2)]),
 'Shoal': dict(sky='day', hz=0.48, water_far=[F('sea', pal='teal')], feats2=[F('hill', cx=24, w=22, h=2, pal='sand')], extras=[F('birds', n=3), F('ripples', pts=((12, 36), (38, 34)))]),
 'Fen': dict(sky='overcast', ground='moss', gtop=0.58, water=[F('lake', pal='storm', rx=14)], extras=[F('reeds', n=22), F('fog', y0=22, h=8)]),
 'Hill': dict(sky='day', feats=[F('hill', w=26, h=14)], ground='grass', gtop=0.72, extras=[F('clouds', n=2), F('sun', x=38, y=7, r=3)]),
 'Meadow': dict(sky='day', ground='grass', gtop=0.58, extras=[F('flowers', n=40), F('clouds', n=3), F('birds', n=1)]),
 'Cavern': dict(sky='dusk', hz=0.6, ground='rock', gtop=0.8, feats=[F('cave', pal='stone')], extras=[F('stars', n=6)]),
 'Dune': dict(sky='haze', hz=0.6, feats=[F('dunes', n=2)], extras=[F('sun', x=14, y=8, r=3)]),
 'Barrens': dict(sky='haze', ground='rock', gtop=0.56, extras=[F('cracks', n=8), F('rocks', n=8), F('sun', x=36, y=8, r=3, col='#E8D8B0')]),
 'Crater': dict(sky='night', ground='rock', gtop=0.56, water=[F('lake', pal='crater', rx=17, ry=6)], extras=[F('stars', n=16), F('moon', x=10, y=6)]),
 'Ledge': dict(sky='dawn', far='mountains', farcol='#55687C', ground='grass', gtop=0.84, feats2=[F('cliff', side='left', top=24)], extras=[F('birds', n=2), F('fog', y0=33, h=6)]),
 'Ridge': dict(sky='dusk', far='mountains', farcol='#2A2438', feats=[F('range', pal='violet', n=2, hmax=16)], ground='dark', gtop=0.82),
 'Eyrie': dict(sky='day', hz=0.74, feats=[F('spire', cx=32, h=28)], ground='rock', extras=[F('birds', n=4), F('clouds', n=2)]),
 'Hanging Valley': dict(sky='teal', hz=0.7, feats=[F('mesa', w=36, h=20, pal='stone')], water=[F('fall', x0=12, top=12), F('lake', pal='teal', rx=10, cx=14, cy=40)], extras=[F('fog', y0=30, h=4)]),
 'Ocean': dict(sky='day', hz=0.4, water_far=[F('sea', pal='deep')], extras=[F('sun', x=36, y=6, r=3), F('clouds', n=3), F('birds', n=2)]),
 'Pangaea': dict(sky='dawn', far='mountains', farcol='#4A4058', feats=[F('range', pal='earth', n=7, hmax=22)], ground='grass', gtop=0.74, extras=[F('clouds', n=2)]),
 'Core': dict(sky='red', hz=0.2, extras=[F('core')]),
 'Trade Winds': dict(sky='day', hz=0.62, water_far=[F('sea')], extras=[F('clouds', n=5), F('wind', n=14), F('birds', n=2)]),
 'Origin': dict(sky='dawn', hz=0.6, water_far=[F('sea')], feats=[F('peak', cx=18, h=22, snow=2), F('cone', cx=36, h=14, crater=3, pal='dark')], extras=[F('smoke', x=36, y=22, n=6), F('wind', n=6), F('sun', x=8, y=8, r=3)]),
}
META = {
 'Echo': dict(sky='dusk', feats=[F('canyon', pal='violet', gap=18)], extras=[F('sound')]),
 'Hollow': dict(sky='night', ground='rock', gtop=0.85, feats=[F('cave', pal='stone')], extras=[F('stars', n=10)]),
 'Equinox': dict(sky='day', hz=0.6, water_far=[F('sea')], extras=[F('equinox')]),
 'Verge': dict(sky='dawn', hz=0.6, water_far=[F('sea', pal='deep')], feats=[F('cliff', side='left', top=10)], extras=[F('birds', n=2)]),
 'Lull': dict(sky='dusk', hz=0.5, water_far=[F('sea', pal='deep')], extras=[F('moon'), F('stars', n=12)]),
 'Ebb': dict(sky='dawn', hz=0.42, water_far=[F('sea', depth=4)], ground='shore', gtop=0.56, extras=[F('ripples', pts=((14, 22), (32, 24)))]),
 'Horizon': dict(sky='gold', hz=0.56, water_far=[F('sea')], extras=[F('sun', x=24, y=17, r=5, col='#F4C890')]),
 'Calm': dict(sky='dawn', far='mountains', farcol='#4A5468', water_far=[F('sea', pal='blue')], extras=[F('birds', n=1)]),
 'Aftershock': dict(sky='dusk', ground='rock', gtop=0.5, extras=[F('cracks', n=9), F('boulders', n=6)]),
 'Stillness': dict(sky='night', ground='snow', gtop=0.6, feats2=[F('trees', n=4, pal='black', size=4, y0=20)], extras=[F('stars', n=20), F('moon')]),
 'Sunlight': dict(sky='day', ground='grass', gtop=0.72, extras=[F('rays', x=24, y=3)]),
 'Weathering': dict(sky='haze', feats=[F('arch', pal='red')], ground='sand', gtop=0.82, extras=[F('wind', n=8, col='#E8D8B8')]),
 'Thunder': dict(sky='storm', far='ridges', farcol='#1A1E22', extras=[F('lightning', x=28), F('rain', n=50)]),
 'Haze': dict(sky='haze', far='mountains', farcol='#9A8C76', ground='sand', gtop=0.74, extras=[F('sun', x=30, y=9, r=4, col='#EADCB8'), F('fog', y0=4, h=20, col='#D8CCB0')]),
}
WEATHER = {
    'fire': {'Ash', 'Brushfire', 'Spark', 'Scorch', 'Heatwave', 'Flare-up', 'Heat Dome', 'Ember', 'Firestorm', 'Smoke', 'Scald', 'Ashfall', 'Meteor', 'Lava Bomb', 'Wildfire'},
    'storm': {'Lightning', 'Thunderstorm', 'Typhoon', 'Hurricane'},
    'cold': {'Thaw', 'Freeze', 'Blizzard', 'Whiteout', 'Ice Storm', 'Hail', 'Permafrost', 'Avalanche'},
    'fog': {'Fog', 'Mist', 'Squall', 'Heat Shimmer'},
    'funnel': {'Whirlwind', 'Dust Devil', 'Tornado', 'Cyclone', 'Whirl', 'Waterspout', 'Whirlpool'},
    'flood': {'Flood', 'Flash Flood', 'Surge', 'Torrent', 'Tsunami', 'Mudflow', 'Cloudburst', 'Monsoon', 'Downpour', 'Drizzle', 'Current', 'Undertow', 'Riptide'},
    'quake': {'Earthquake', 'World Quake', 'Rockslide', 'Rockfall', 'Landslide', 'Collapse', 'Sinkhole', 'Mudslide', 'Erosion', 'Tangle', 'Bramble', 'Overgrowth', 'Shelter', 'Unmaking'},
    'wind': {'Gale', 'Gale Force', 'Gust', 'Breeze', 'Crosswind', 'Eddy', 'Updraft', 'Downdraft', 'Jet Stream', 'High Pressure', 'Vent'},
    'dust': {'Dust', 'Dust Storm', 'Sandstorm', 'Drought', 'Mire'},
    'tide': {'Low Tide'},
}
def back_spec(spec, force, el):
    s = {k: (list(v) if isinstance(v, list) else v) for k, v in spec.items()}
    kind = next((k for k, names in WEATHER.items() if force in names), None)
    if not force: kind = 'quiet'
    kind = kind or {'fire': 'fire', 'water': 'flood', 'earth': 'quake', 'air': 'wind'}.get(el, 'wind')
    ex = [e for e in s.get('extras', []) if e[0] not in ('sun', 'birds', 'flowers', 'rays')]
    if kind == 'fire': s['sky'] = 'red'; ex += [F('flames', n=7), F('embers', n=30)]
    elif kind == 'storm': s['sky'] = 'storm'; ex += [F('lightning', x=30), F('rain', n=50)]
    elif kind == 'cold': s['sky'] = 'arctic'; ex += [F('snow', n=80)] if force != 'Hail' else [F('hail', n=40)]
    elif kind == 'fog': s['sky'] = 'overcast'; ex += [F('fog', y0=4, h=24)]
    elif kind == 'funnel': s['sky'] = 'storm'; ex += [F('funnel', x=30), F('wind', n=8)]
    elif kind == 'flood': s['sky'] = 'storm'; ex += ([F('wave')] if force == 'Tsunami' else []) + [F('rain', n=60)]
    elif kind == 'quake': s['sky'] = 'dusk'; ex += [F('cracks', n=8), F('boulders', n=7)]
    elif kind == 'wind': s['sky'] = 'overcast'; ex += [F('wind', n=16), F('clouds', n=3, col='#9AA2A6')]
    elif kind == 'dust': s['sky'] = 'haze'; ex += [F('fog', y0=4, h=26, col='#C8B48A'), F('wind', n=10, col='#D8C8A0')]
    elif kind == 'tide': s['sky'] = 'dawn'; s['water'] = []; ex += [F('ripples')]
    elif kind == 'quiet': s['sky'] = 'night'; ex = [e for e in ex if e[0] not in ('clouds',)] + [F('stars', n=14)]
    s['extras'] = ex
    return s, kind
