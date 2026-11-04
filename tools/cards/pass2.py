import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
import commons, uncommons, rares, forces
import lib
lib.CIRCLED = True

# ---------------- the pass: 30 C, 13 B, 5 A, 2 S, plus 5 meta ----------------
# (num, name, rarity, affinities, permanence text, force name, duration, force text)
COMMONS = {
 'fire': [
  (12, 'Cinder Field', 'C', ['fire'], None, 'Brushfire', 'round', 'A one-affinity card doesn’t count.'),
  (2, 'Flint', 'C', ['fire|earth'], None, 'Spark', 'round', 'A one-affinity card becomes fire.'),
  (3, 'Obsidian', 'C', ['fire'], 'Forces can’t remove this.', 'Ash Cloud', 'round', 'A one-affinity air card doesn’t count.'),
  (6, 'Scrubland', 'C', ['fire|air'], None, 'Controlled Burn', 'once', 'Remove one of your cards.'),
  (7, 'Ashfield', 'C', ['fire'], 'Counts double in affinity ties.', 'Smoke', 'round', 'A world doesn’t count in ties.'),
  (9, 'Dune', 'C', ['fire'], None, 'Shimmer', 'round', 'A one-affinity card counts as any element.'),
  (10, 'Barrens', 'C', ['fire'], None, 'Lightning', 'once', 'Remove a lone one-affinity card.'),
  (11, 'Steam Vent', 'C', ['fire|water'], None, 'Vent', 'once', 'Return your card to your binder.'),
 ],
 'water': [
  (23, 'Spring', 'C', ['water'], 'Returns to your binder at round end.', 'Drizzle', 'round', 'A one-affinity card also counts as water.'),
  (24, 'Marsh', 'C', ['water|earth'], None, 'Mire', 'round', 'A world of two can’t grow.'),
  (28, 'Snowfield', 'C', ['water'], 'Play on one-affinity air. It becomes water.', 'Rain', 'round', 'A one-affinity card becomes water.'),
  (29, 'Tide Pool', 'C', ['water'], 'Ignores common forces.', 'Freeze', 'round', 'A world’s one-affinity cards can’t be removed.'),
 ],
 'air': [
  (41, 'Ledge', 'C', ['air'], None, 'Gust', 'once', 'A one-affinity card becomes its own world.'),
  (33, 'Summit', 'C', ['air'], 'Counts double in affinity ties.', 'Breeze', 'round', 'A one-affinity card becomes air.'),
  (38, 'Pass', 'C', ['air|earth'], None, 'Drift', 'once', 'Move your card to another world.'),
  (45, 'Wind Gap', 'C', ['air'], None, 'Crosswind', 'once', 'Swap two one-affinity cards between worlds.'),
  (37, 'Peak', 'C', ['air'], None, 'Downdraft', 'round', 'A one-affinity air card becomes earth.'),
  (32, 'Sea Stack', 'C', ['water|air'], None, 'Sea Breeze', 'round', 'A one-affinity card also counts as air.'),
  (36, 'Ridge', 'C', ['air'], None, 'Lift', 'once', 'Remove a common sitting on another.'),
  (31, 'Spire', 'C', ['air'], 'Forces can’t move this.', 'Vortex', 'once', 'Move a one-affinity card between worlds.'),
  (39, 'Bluff', 'C', ['air'], None, 'Eddy', 'once', 'Swap two cards in one world.'),
 ],
 'earth': [
  (52, 'Hill', 'C', ['earth'], None, 'Overgrowth', 'round', 'One of your worlds ignores common forces.'),
  (47, 'Bedrock', 'C', ['earth'], 'Forces can’t remove this.', 'Landslide', 'round', 'A one-affinity card becomes earth.'),
  (48, 'Cave', 'C', ['earth'], 'Ignores common forces.', 'Shelter', 'round', 'A card can’t be removed.'),
  (49, 'Meadow', 'C', ['earth'], None, 'Bloom', 'round', 'A one-affinity card also counts as earth.'),
  (50, 'Grove', 'C', ['earth'], 'Returns to your binder at round end.', 'Lichen', 'round', 'A one-affinity card counts double in ties.'),
  (59, 'Mesa', 'C', ['earth'], None, 'Fault Line', 'once', 'Split a world of three or fewer.'),
  (57, 'Ravine', 'C', ['earth'], None, 'Washout', 'once', 'Return a one-affinity card to its binder.'),
  (46, 'Boulder', 'C', ['earth'], None, 'Rockfall', 'once', 'Remove a lone one-affinity card.'),
  (54, 'Thicket', 'C', ['earth'], 'Your touching cards can’t be removed.', 'Tangle', 'round', 'Cards in a world can’t be moved.'),
 ],
}
UNCOMMONS = [
  (63, 'Hot Spring', 'B', ['water', 'fire'], None, 'Steam Burst', 'round', 'A touching fire-water pair doesn’t count.'),
  (62, 'Desert', 'B', ['fire', 'air'], None, 'Heatwave', 'round', 'A card doesn’t count.'),
  (65, 'Volcano', 'B', ['fire', 'earth'], None, 'Eruption', 'once', 'Remove a one-affinity card.'),
  (78, 'Cloud Forest', 'B', ['air', 'water'], None, 'Fog', 'round', 'A world can’t grow.'),
  (69, 'Delta', 'B', ['water', 'earth'], None, 'Flood', 'once', 'Return a card to its binder.'),
  (71, 'Sea Cliff', 'B', ['earth', 'air'], None, 'Gale', 'once', 'Swap two cards between one player’s worlds.'),
  (66, 'Glacier', 'B', ['water'], 'Play on earth permanence. It becomes water.', 'Thaw', 'once', 'Remove a card sitting on another.'),
  (79, 'Salt Flat', 'B', ['fire'], 'Play on one-affinity permanence. It doesn’t count.', 'Drought', 'round', 'A card becomes fire.'),
  (80, 'Mirage', 'B', ['air'], 'Copies a touching card’s affinities.', 'Haze', 'round', 'A card counts as any element.'),
  (84, 'Hidden Valley', 'B', ['earth'], 'Your other cards ignore common forces.', 'Rockslide', 'round', 'A card becomes earth.'),
  (85, 'Petrified Forest', 'B', ['earth'], 'Stays into the next round.', 'Uplift', 'round', 'A world ignores all forces.'),
  (82, 'Hanging Valley', 'B', ['air'], 'Your air counts double in ties.', 'Updraft', 'round', 'A card becomes air.'),
  (81, 'Confluence', 'B', ['water', 'any'], None, 'Current', 'once', 'Move a card between its owner’s worlds.'),
]
RARES_P = [
  (88, 'Caldera Lake', 'A', ['fire', 'earth', 'water'], None, 'Collapse', 'once', 'Remove any card.'),
  (91, 'Stone Towers', 'A', ['air', 'air', 'earth'], None, 'Erosion', 'once', 'Split a world in two.'),
  (93, 'Archipelago', 'A', ['water', 'water', 'earth'], 'Win the round with 10 water affinities.', 'Rising Sea', 'round', 'One-affinity cards in a world don’t count.'),
  (94, 'Ice Sheet', 'A', ['water'], 'Fire affinities don’t count.', 'Blizzard', 'once', 'Return a world to its owner’s binder.'),
  (95, 'Mountain Range', 'A', ['earth', 'air'], 'Score a point per four earth affinities.', 'Avalanche', 'once', 'Remove two touching one-affinity cards.'),
]
PINN_P = [
  (96, 'Core', 'S', ['fire'] * 4, None, 'Solar Flare', 'once', 'Remove all one-affinity cards.'),
  (98, 'Ocean', 'S', ['water'] * 4, None, 'Deluge', 'round', 'A world doesn’t count.'),
]
META = [
  ('Echo', 'Play a one-affinity card from your void.'),
  ('Ebb', 'Remove your opponent’s last card.'),
  ('Horizon', 'Look through your opponent’s binder.'),
  ('Lull', 'Your opponent skips their next turn.'),
  ('Verge', 'Play two cards this turn.'),
]
BINDERS = {
 'A': ('Tides', 'Water and air, control and turtling, built around Ocean.',
       ['Ocean', 'Archipelago', 'Ice Sheet', 'Stone Towers', 'Cloud Forest', 'Glacier', 'Confluence', 'Hanging Valley', 'Mirage', 'Delta', 'Sea Cliff',
        'Echo', 'Lull', 'Horizon',
        'Cinder Field', 'Flint', 'Steam Vent', 'Ashfield', 'Dune', 'Hill', 'Cave', 'Thicket', 'Ledge', 'Spire', 'Spring']),
 'B': ('Embers', 'Fire and earth, removal and pressure, built around Core.',
       ['Core', 'Caldera Lake', 'Mountain Range', 'Stone Towers', 'Hot Spring', 'Desert', 'Volcano', 'Salt Flat', 'Hidden Valley', 'Petrified Forest',
        'Ebb', 'Verge', 'Horizon',
        'Marsh', 'Snowfield', 'Tide Pool', 'Spring', 'Summit', 'Pass', 'Wind Gap', 'Peak', 'Bedrock', 'Meadow', 'Grove', 'Barrens']),
}

# ---------------- art lookup ----------------
ART = {}
for lst in (commons.FIRE, commons.WATER, commons.AIRL, commons.EARTHL):
    for n, a in lst: ART[n] = a
for c in uncommons.CARDS: ART[c[0]] = c[4]
for c in rares.RARES + rares.PINNACLES: ART[c[0]] = c[5]
FART = {'Brushfire': forces.art_brushfire, 'Washout': forces.art_washout, 'Gust': forces.art_gust, 'Overgrowth': forces.art_overgrowth,
        'Steam Burst': forces.art_steamburst, 'Gale': forces.art_gale, 'Fog': forces.art_fog, 'Thaw': forces.art_thaw,
        'Collapse': forces.art_collapse, 'Erosion': forces.art_erosion, 'Rising Sea': forces.art_risingsea, 'Deluge': forces.art_deluge}

def placeholder(el):
    d, c = GLYPH[el]
    return ('<g transform="translate(84 36) scale(5)" fill="none" stroke="%s" stroke-width="0.5" stroke-linejoin="round" opacity="0.32"><path d="%s"></path></g>' % (c, d)
            + '<text x="144" y="182" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="10" letter-spacing="1.5" fill="#7E8A90">ART TO COME</text>')

def all_cards():
    out = []
    for el in ['fire', 'water', 'air', 'earth']: out += COMMONS[el]
    return out + UNCOMMONS + RARES_P + PINN_P

def words(t): return len(t.replace('—', ' ').split())

def check():
    probs = []
    tally = {e: 0 for e in ['fire', 'water', 'air', 'earth', 'any', 'either-or']}
    for c in all_cards():
        for t in (c[4], c[7]):
            if t and words(t) >= 8: probs.append((c[1], t, words(t)))
        for a in c[3]: tally['either-or' if '|' in a else a] += 1
    for n, t in META:
        if words(t) >= 8: probs.append((n, t, words(t)))
    names = [c[1] for c in all_cards()] + [m[0] for m in META]
    for k, (title, desc, lst) in BINDERS.items():
        missing = [x for x in lst if x not in names]
        print('binder', k, len(lst), 'missing', missing, 'dupes', len(lst) - len(set(lst)))
    print('counts', {r: sum(1 for c in all_cards() if c[2] == r) for r in 'CBAS'}, 'meta', len(META))
    print('affinities', tally)
    print('over 7 words', probs)
    return tally

def pair(i, c):
    num, name, rar, affs, ptxt, fname, dur, ftxt = c
    front = card(i, name, num, rar, affs, ptxt, ART[name])
    el = affs[0].split('|')[0] if affs[0] != 'any' else 'water'
    fart = FART.get(fname) or (lambda j, el=el: placeholder(el))
    back_ = forces.force(i + 1, fname, num, rar, dur, ftxt, fart)
    return f'''<div style="display: flex; flex-direction: column; gap: 10px">
<div style="display: flex; gap: 12px">{front}{back_}</div>
<div style="display: flex; gap: 12px; font-family: 'IBM Plex Mono', monospace; font-size: 11px; letter-spacing: 0.1em; color: #7E827A"><div style="width: 320px; text-align: center">PERMANENCE</div><div style="width: 320px; text-align: center">FORCE</div></div>
</div>'''

VOIDC = '#B9A6D6'
def meta_card(i, name, text):
    d = 'M4.5 12 a7.5 7.5 0 1 0 15 0 a7.5 7.5 0 1 0 -15 0 M10.5 12 a1.5 1.5 0 1 0 3 0 a1.5 1.5 0 1 0 -3 0'
    return f'''<div style="display: flex; flex-direction: column; gap: 10px">
<div style="position: relative; width: 320px; height: 448px; flex: none; border-radius: 14px; background: #1E1F24; box-shadow: 0 14px 32px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.05), inset 0 -4px 10px rgba(0,0,0,0.5)">
<svg width="320" height="448" style="position: absolute; top: 0; left: 0" aria-hidden="true"><defs><filter id="grain{i}"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="3" stitchTiles="stitch" seed="{i}"></feTurbulence><feColorMatrix type="saturate" values="0"></feColorMatrix></filter></defs><rect width="320" height="448" rx="14" filter="url(#grain{i})" opacity="0.12"></rect><rect x="5.5" y="5.5" width="309" height="437" rx="10" fill="none" stroke="{VOIDC}" stroke-width="1" opacity="0.45"></rect><rect x="10.5" y="10.5" width="299" height="427" rx="7" fill="none" stroke="{VOIDC}" stroke-width="0.6" opacity="0.25"></rect></svg>
<div style="position: absolute; top: 18px; left: 16px; width: 288px; text-align: center; font-family: 'IBM Plex Mono', monospace; font-size: 11px; letter-spacing: 0.14em; color: {VOIDC}">FIFTH PILLAR · META</div>
<div style="position: absolute; top: 40px; left: 16px; width: 288px; height: 38px; display: flex; align-items: center; justify-content: center; font-size: 28px; font-weight: 600; color: #ECE6D6; text-shadow: 1px 1px 0 #0D0F0D">{name}</div>
<div style="position: absolute; top: 88px; left: 16px; width: 288px; bottom: 66px; display: flex; flex-direction: column; gap: 6px">
<div role="img" aria-label="{name}" style="flex: 1 1 0; min-height: 0; border-radius: 10px; background: rgba(0,0,0,0.28); box-shadow: inset 0 4px 12px rgba(0,0,0,0.65); display: flex; align-items: center; justify-content: center; overflow: hidden">
<svg style="height: 72%; max-height: 120px; aspect-ratio: 1" viewBox="0 0 24 24" fill="none" stroke="{VOIDC}" stroke-width="0.7" opacity="0.7" aria-hidden="true"><path d="{d}"></path><path d="M12 1.5 V3.5 M12 20.5 V22.5 M1.5 12 H3.5 M20.5 12 H22.5" opacity="0.6"></path></svg>
</div>
<div style="flex: none; height: 16px; display: flex; align-items: center; justify-content: center; font-family: 'IBM Plex Mono', monospace; font-size: 11px; letter-spacing: 0.1em; color: #A9A3B8">ONE FACE · EITHER PLAYER · ONCE</div>
<div class="rules" style="flex: none; box-sizing: border-box; padding: 6px 10px; border-radius: 8px; background: rgba(13,15,13,0.55); border: 1px solid rgba(185,166,214,0.28); text-align: center; font-size: 42px; line-height: 1.04; color: #ECE6D6">{text}</div>
</div>
<div style="position: absolute; left: 22px; top: 404px; height: 32px; display: flex; align-items: center; font-family: 'IBM Plex Mono', monospace; font-size: 14px; letter-spacing: 0.04em; color: #8F8A9C">—/100</div>
<div role="img" aria-label="Rarity B, uncommon" style="position: absolute; right: 18px; top: 402px; width: 36px; height: 36px">
<div style="position: absolute; top: 7px; left: 7px; width: 20px; height: 20px; transform: rotate(45deg); border: 1.6px solid #C2C5B8; box-shadow: 1px 1px 0 #0D0F0D"></div>
<div style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-size: 19px; font-weight: 700; color: #C2C5B8; text-shadow: 1px 1px 0 #0D0F0D">B</div>
</div>
</div>
<div style="font-family: 'IBM Plex Mono', monospace; font-size: 11px; letter-spacing: 0.1em; color: #7E827A; text-align: center">META</div>
</div>'''

HEAD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500;1,600&amp;family=IBM+Plex+Mono:wght@400;500;600&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0}}
a{{color:#D9A441}}a:hover{{color:#ECE6D6}}
</style>
</helmet>
<div style="width: {W}px; height: {H}px; box-sizing: border-box; padding: 48px; background: #191B1A; color: #ECE6D6; font-family: 'Cormorant Garamond', Georgia, serif; display: flex; flex-direction: column; gap: 30px">
'''
TAIL = '''</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{W},"height":{H}}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
'''
MONO = "font-family: 'IBM Plex Mono', monospace"
LEGEND = f'''<div style="display: flex; flex-direction: column; gap: 6px; align-items: flex-end; {MONO}; font-size: 13px; color: #A9ADA2; text-align: right">
<div>Rules text under 8 words (CARD-23). Effects grow and restrictions shrink with rarity (CARD-24).</div>
<div>Forces target either player’s cards unless they say otherwise; moves and swaps never change a card’s owner.</div>
<div><span style="color: #ECE6D6">LASTS THE ROUND</span>: sits on one card or beside one world, then goes to the void. <span style="color: #ECE6D6">ONCE</span>: happens, then goes to the void.</div>
<div>“Remove” sends a card to its owner’s void. A card that “doesn’t count” is treated as if it weren’t there.</div>
<div>Each ring is one affinity. A capsule holding two symbols is one affinity: either element, chosen at round end.</div>
</div>'''

def header(title, sub):
    return f'''<div style="display: flex; justify-content: space-between; align-items: flex-end; gap: 40px">
<div style="display: flex; flex-direction: column; gap: 6px">
<h1 style="margin: 0; font-size: 40px; font-weight: 600">{title}</h1>
<p style="margin: 0; {MONO}; font-size: 13px; color: #A9ADA2; max-width: 1300px">{sub}</p>
</div>
{LEGEND}
</div>
'''

def label(t): return f'<div style="{MONO}; font-size: 12px; letter-spacing: 0.12em; color: #A9ADA2">{t}</div>'

def rows_of(items, n, gap=56):
    out = ''
    for k in range(0, len(items), n):
        out += f'<div style="display: flex; gap: {gap}px">{"".join(items[k:k + n])}</div>\n'
    return out

def write(outdir, fname, title, W, H, body):
    html = HEAD.format(title=title, W=W, H=H) + body + TAIL.format(W=W, H=H)
    open(os.path.join(outdir, fname), 'w').write(html)
    print('wrote', fname, len(html))

def build(outdir):
    tally = check()
    W = 2880
    # commons
    idx = 600; body = header('Second pass: commons (30)', 'Half the pool, both faces, text-first: Nov 1, 2026. Commons carry one affinity. Eleven also carry a subtle permanence effect, and six carry an either-or capsule instead, one for each pair of elements. Every common force reaches only one-affinity cards (or only your own cards).')
    for el in ['fire', 'water', 'air', 'earth']:
        items = []
        for c in COMMONS[el]:
            idx += 2; items.append(pair(idx, c))
        body += f'<div style="display: flex; flex-direction: column; gap: 14px">{label("%s · %d COMMONS" % (el.upper(), len(COMMONS[el])))}<div style="display: flex; flex-direction: column; gap: 28px">{rows_of(items, 4)}</div></div>\n'
    write(outdir, 'Pass2-Commons.dc.html', 'Second pass: commons', W, 4820, body)
    # uncommons
    idx = 700; body = header('Second pass: uncommons (13)', 'Two affinities, or one and a permanence effect. Uncommon forces reach any card or a whole world, with lighter restrictions.')
    items = []
    for c in UNCOMMONS:
        idx += 2; items.append(pair(idx, c))
    body += f'<div style="display: flex; flex-direction: column; gap: 28px">{rows_of(items, 4)}</div>\n'
    write(outdir, 'Pass2-Uncommons.dc.html', 'Second pass: uncommons', W, 2200, body)
    # rares, pinnacles, meta
    idx = 800; body = header('Second pass: rares, pinnacles and meta', 'Five rares, two pinnacles, and five weaker fifth-pillar meta cards: one face, usable by either player, numbers still to be placed.')
    items = []
    for c in RARES_P:
        idx += 2; items.append(pair(idx, c))
    body += f'<div style="display: flex; flex-direction: column; gap: 14px">{label("RARE · A · FIVE")}<div style="display: flex; flex-direction: column; gap: 28px">{rows_of(items, 4)}</div></div>\n'
    items = []
    for c in PINN_P:
        idx += 2; items.append(pair(idx, c))
    metas = []
    for n, t in META:
        idx += 1; metas.append(meta_card(idx, n, t))
    body += f'''<div style="display: flex; gap: 56px">
<div style="display: flex; flex-direction: column; gap: 14px">{label("PINNACLE · S · TWO")}<div style="display: flex; gap: 56px">{"".join(items)}</div></div>
</div>
<div style="display: flex; flex-direction: column; gap: 14px">{label("FIFTH PILLAR · META · FIVE, WEAKER ONES")}<div style="display: flex; gap: 40px">{"".join(metas)}</div></div>
'''
    write(outdir, 'Pass2-Rares-meta.dc.html', 'Second pass: rares, pinnacles and meta', W, 2290, body)
    # binders
    lookup = {c[1]: c for c in all_cards()}
    cols = ''
    for k, (title, desc, lst) in BINDERS.items():
        t = {e: 0 for e in ['fire', 'water', 'air', 'earth', 'any', 'either-or']}
        rows = ''
        order = {'S': 0, 'A': 1, 'B': 2, 'C': 3}
        def key(n):
            return (4 if n not in lookup else order[lookup[n][2]], n)
        for n in sorted(lst, key=key):
            if n in lookup:
                c = lookup[n]
                for a in c[3]: t['either-or' if '|' in a else a] += 1
                gl = ''.join(glyph(a, 18) for a in c[3])
                rows += f'<div style="display: grid; grid-template-columns: 34px 1fr 150px; align-items: center; gap: 10px; padding: 5px 0; border-bottom: 1px solid rgba(194,197,184,0.12)"><div style="{MONO}; font-size: 13px; color: #A9ADA2">{c[2]}</div><div style="font-size: 22px">{n} <span style="font-style: italic; color: #A9B3B8">/ {c[5]}</span></div><div style="display: flex; gap: 4px">{gl}</div></div>'
            else:
                rows += f'<div style="display: grid; grid-template-columns: 34px 1fr 150px; align-items: center; gap: 10px; padding: 5px 0; border-bottom: 1px solid rgba(194,197,184,0.12)"><div style="{MONO}; font-size: 13px; color: {VOIDC}">M</div><div style="font-size: 22px">{n} <span style="font-style: italic; color: #A9A3B8">/ meta</span></div><div></div></div>'
        tot = ' · '.join('%s %d' % (e, t[e]) for e in ['fire', 'water', 'air', 'earth']) + (' · either-or %d' % t['either-or'] if t['either-or'] else '') + (' · any %d' % t['any'] if t['any'] else '')
        cols += f'''<div style="flex: 1; display: flex; flex-direction: column; gap: 10px">
<div style="{MONO}; font-size: 12px; letter-spacing: 0.12em; color: #A9ADA2">BINDER {k} · 25 CARDS</div>
<div style="font-size: 36px; font-weight: 600">{title}</div>
<div style="font-size: 20px; font-style: italic; color: #C9CCC0">{desc}</div>
<div style="{MONO}; font-size: 13px; color: #ECE6D6">Affinities: {tot}</div>
<div style="display: flex; flex-direction: column">{rows}</div>
</div>'''
    shared = sorted(set(BINDERS['A'][2]) & set(BINDERS['B'][2]))
    unused = sorted(set(c[1] for c in all_cards()) | set(m[0] for m in META) - set(BINDERS['A'][2]) - set(BINDERS['B'][2]))
    unused = [n for n in unused if n not in BINDERS['A'][2] and n not in BINDERS['B'][2]]
    body = f'''<div style="display: flex; flex-direction: column; gap: 6px">
<h1 style="margin: 0; font-size: 40px; font-weight: 600">Two playtest binders</h1>
<p style="margin: 0; {MONO}; font-size: 13px; color: #A9ADA2; max-width: 1500px">Built from the second pass: 25 cards each, one of each card, 2–3 meta cards each. Shared: {", ".join(shared)}. Not in either binder: {", ".join(unused)}. Each row shows permanence / force.</p>
</div>
<div style="display: flex; gap: 64px">{cols}</div>
'''
    write(outdir, 'Pass2-Binders.dc.html', 'Two playtest binders', 1600, 1320, body)

if __name__ == '__main__':
    if len(sys.argv) > 1: build(sys.argv[1])
    else: check()
