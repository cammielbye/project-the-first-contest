import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
import pass2 as P
import lib
lib.CIRCLED = False  # pass2 turns rings on; the comparison rows below draw the older marks

def path(el): return GLYPH[el]

def g(el, x, y, s):
    d, c = GLYPH[el]
    return (f'<g transform="translate({x + 0.8 * s} {y + 0.8 * s}) scale({s})" stroke="{SH}"><path d="{d}"></path></g>'
            f'<g transform="translate({x} {y}) scale({s})" stroke="{c}"><path d="{d}"></path></g>')

def svg(w, h, inner, label):
    return (f'<svg role="img" aria-label="{label}" width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" stroke-width="1.9" '
            f'stroke-linejoin="round" stroke-linecap="round" style="overflow: visible">{inner}</svg>')

def pill(a, b):
    inner = (f'<rect x="1.5" y="1.5" width="69" height="33" rx="16.5" stroke="#C2C5B8" stroke-width="1.4" opacity="0.7"></rect>'
             f'<path d="M36 7 V29" stroke="#C2C5B8" stroke-width="1.2" opacity="0.55"></path>'
             + g(a, 7, 6, 1.0) + g(b, 41, 6, 1.0))
    return svg(72, 36, inner, f'One affinity: {a} or {b}')

def halves(a, b):
    inner = (f'<circle cx="18" cy="18" r="16" stroke="#C2C5B8" stroke-width="1.4" opacity="0.7"></circle>'
             f'<path d="M18 4 V32" stroke="#C2C5B8" stroke-width="1.2" opacity="0.55"></path>'
             + g(a, 4.5, 12, 0.5) + g(b, 19.5, 12, 0.5))
    return svg(36, 36, inner, f'One affinity: {a} or {b}')

def slash(a, b):
    inner = (g(a, 0, 7, 0.85) + f'<path d="M24 31 L32 5" stroke="#C2C5B8" stroke-width="1.6" opacity="0.8"></path>' + g(b, 33, 7, 0.85))
    return svg(56, 36, inner, f'One affinity: {a} or {b}')

def plain(els):
    return ''.join(glyph(e) for e in els)

# hybrid: the left half of one symbol joined to the right half of the other, at the centre line
# every half spans the same height (y 4 to 20), so tops and bottoms meet at the seam
# One outline drawn as a single path (so its corners join cleanly), coloured by two clips that
# meet on the exact vertical line x = 12: left of it is the first element, right of it the second.
UP = ('fire', 'air')
BAR = {'air': 13.3, 'earth': 10.7}
_clip = [0]
def outline(a, b):
    right = 'L20.5 20 L12 20' if b in UP else 'L20.5 4 L12 20'
    left_back = 'L3.5 20 L12 4' if a in UP else 'L3.5 4 L12 4'
    return f'M12 4 {right} {left_back} Z'
def hybrid_inner(a, b):
    ca, cb = GLYPH[a][1], GLYPH[b][1]
    _clip[0] += 1; k = _clip[0]
    o = outline(a, b)
    bar_a = f'<path d="M3 {BAR[a]} H21"></path>' if a in BAR else ''
    bar_b = f'<path d="M3 {BAR[b]} H21"></path>' if b in BAR else ''
    return (f'<defs><clipPath id="hl{k}"><rect x="-2" y="-2" width="14" height="28"></rect></clipPath>'
            f'<clipPath id="hr{k}"><rect x="12" y="-2" width="14" height="28"></rect></clipPath></defs>'
            f'<g transform="translate(0.8 0.8)" stroke="{SH}"><g clip-path="url(#hl{k})"><path d="{o}"></path>{bar_a}</g>'
            f'<g clip-path="url(#hr{k})"><path d="{o}"></path>{bar_b}</g></g>'
            f'<g clip-path="url(#hl{k})" stroke="{ca}"><path d="{o}"></path>{bar_a}</g>'
            f'<g clip-path="url(#hr{k})" stroke="{cb}"><path d="{o}"></path>{bar_b}</g>')

def hybrid(a, b, size=28):
    return (f'<svg role="img" aria-label="One affinity: {a} or {b}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke-width="1.9" '
            f'stroke-linejoin="round" stroke-linecap="round">{hybrid_inner(a, b)}</svg>')

def card_custom(i, name, num, rar, glyph_html, rule, art, aria):
    html = card(i, name, num, rar, ['fire'], rule, art)
    # swap the affinity band contents
    return re.sub(r'(<div role="img" aria-label=")Affinity: [^"]*(" style="position: absolute; top: 342px[^>]*>).*?(</div>\n<svg width="288" height="10")',
                  lambda m: m.group(1) + aria + m.group(2) + glyph_html + m.group(3), html, flags=re.S)

look = {c[1]: c for c in P.all_cards()}
def mk(i, name, variant):
    c = look[name]
    if name in ('Flint', 'Steam Vent'):
        a, b = ('fire', 'earth') if name == 'Flint' else ('fire', 'water')
        gh = variant(a, b); aria = f'Affinity: one, {a} or {b}'
    else:
        gh = plain(c[3]); aria = 'Affinity: ' + affinity_label(c[3])
    return card_custom(i, name, c[0], c[2], gh, None, P.ART[name], aria)

MONO = "font-family: 'IBM Plex Mono', monospace"
rows = ''; i = 900
# E, chosen Nov 1: every affinity in a white ring; either-or = one capsule (from A) split by a slash (from C)
def capsule(a, b): return ringed(a + '|' + b, 32)
lib.CIRCLED = True
cards = ''
for n in ['Flint', 'Volcano', 'Steam Vent', 'Hot Spring']:
    i += 1; cards += mk(i, n, capsule)
strip = ''.join(f'''<div style="display: flex; flex-direction: column; align-items: center; gap: 10px; width: 150px">
{ringed(a + '|' + b, 64)}
<div style="{MONO}; font-size: 12px; letter-spacing: 0.08em; color: #A9ADA2">{a.upper()} OR {b.upper()}</div>
</div>''' for a, b in [('fire', 'water'), ('fire', 'air'), ('fire', 'earth'), ('water', 'air'), ('water', 'earth'), ('air', 'earth')])
singles = ''.join(ringed(e, 64) for e in ['fire', 'water', 'air', 'earth'])
lib.CIRCLED = False
rows += f'''<div style="display: flex; flex-direction: column; gap: 12px; padding: 22px; border: 1px solid #5A5E55; border-radius: 10px">
<div style="display: flex; align-items: baseline; gap: 18px"><div style="{MONO}; font-size: 13px; letter-spacing: 0.12em; color: #ECE6D6; white-space: nowrap">E · CHOSEN: RINGS AND CAPSULE</div><div style="{MONO}; font-size: 13px; color: #A9ADA2">Every affinity sits in a white ring. An either-or affinity is one capsule (from A) holding both symbols, divided by a slash (from C). One ring or one capsule is one affinity.</div></div>
<div style="display: flex; gap: 28px">{cards}</div>
<div style="display: flex; gap: 28px; {MONO}; font-size: 11px; letter-spacing: 0.1em; color: #7E827A"><div style="width: 320px; text-align: center">FLINT · FIRE OR EARTH · ONE AFFINITY</div><div style="width: 320px; text-align: center">VOLCANO · FIRE AND EARTH · TWO</div><div style="width: 320px; text-align: center">STEAM VENT · FIRE OR WATER · ONE</div><div style="width: 320px; text-align: center">HOT SPRING · FIRE AND WATER · TWO</div></div>
<div style="display: flex; align-items: center; gap: 24px; margin-top: 10px"><div style="display: flex; gap: 18px">{singles}</div><div style="width: 1px; height: 64px; background: #5A5E55"></div><div style="display: flex; gap: 8px">{strip}</div></div>
</div>
<div style="{MONO}; font-size: 13px; letter-spacing: 0.12em; color: #7E827A; margin-top: 6px">EARLIER TREATMENTS, FOR COMPARISON</div>
'''
for title, fn, note in [('A · CAPSULE', pill, 'Both symbols at full size inside one outline. Clearest that it is one item; widest.'),
                        ('B · SPLIT SEAL', halves, 'One circle, halved, a small symbol in each half. Same footprint as one symbol; smallest symbols.'),
                        ('C · SLASH', slash, 'Two symbols joined by a slash, no outline. Lightest; closest to looking like two affinities.'),
                        ('D · HYBRID', hybrid, 'Each symbol cut on an exact vertical line; the left half of one joined to the right half of the other. One mark, one affinity.')]:
    cards = ''
    for n in ['Flint', 'Volcano', 'Steam Vent', 'Hot Spring']:
        i += 1; cards += mk(i, n, fn)
    rows += f'''<div style="display: flex; flex-direction: column; gap: 12px">
<div style="display: flex; align-items: baseline; gap: 18px"><div style="{MONO}; font-size: 13px; letter-spacing: 0.12em; color: #ECE6D6">{title}</div><div style="{MONO}; font-size: 13px; color: #A9ADA2">{note}</div></div>
<div style="display: flex; gap: 28px">{cards}</div>
<div style="display: flex; gap: 28px; {MONO}; font-size: 11px; letter-spacing: 0.1em; color: #7E827A"><div style="width: 320px; text-align: center">FLINT · FIRE OR EARTH · ONE AFFINITY</div><div style="width: 320px; text-align: center">VOLCANO · FIRE AND EARTH · TWO</div><div style="width: 320px; text-align: center">STEAM VENT · FIRE OR WATER · ONE</div><div style="width: 320px; text-align: center">HOT SPRING · FIRE AND WATER · TWO</div></div>
</div>
'''
PAIRS6 = [('fire', 'water'), ('fire', 'air'), ('fire', 'earth'), ('water', 'air'), ('water', 'earth'), ('air', 'earth')]
strip = ''.join(f'''<div style="display: flex; flex-direction: column; align-items: center; gap: 10px; width: 200px">
<div style="display: flex; align-items: center; gap: 14px">{glyph(a, 40)}<span style="{MONO}; color: #7E827A">+</span>{glyph(b, 40)}<span style="{MONO}; color: #7E827A">→</span></div>
{hybrid(a, b, 96)}
<div style="{MONO}; font-size: 12px; letter-spacing: 0.08em; color: #A9ADA2">{a.upper()} OR {b.upper()}</div>
</div>''' for a, b in PAIRS6)
rows += f'''<div style="display: flex; flex-direction: column; gap: 14px">
<div style="display: flex; align-items: baseline; gap: 18px"><div style="{MONO}; font-size: 13px; letter-spacing: 0.12em; color: #ECE6D6">D · ALL SIX HYBRIDS, LARGE</div><div style="{MONO}; font-size: 13px; color: #A9ADA2">Left half from the first element in the order fire, water, air, earth. The colour changes on the vertical cut; no seam line.</div></div>
<div style="display: flex; gap: 24px">{strip}</div>
</div>
'''
W, H = 1520, 3330
html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Either-or affinity</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500;1,600&amp;family=IBM+Plex+Mono:wght@400;500;600&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0}}
</style>
</helmet>
<div style="width: {W}px; height: {H}px; box-sizing: border-box; padding: 48px; background: #191B1A; color: #ECE6D6; font-family: 'Cormorant Garamond', Georgia, serif; display: flex; flex-direction: column; gap: 34px">
<div style="display: flex; flex-direction: column; gap: 8px">
<h1 style="margin: 0; font-size: 40px; font-weight: 600">Either-or affinity: treatments</h1>
<p style="margin: 0; {MONO}; font-size: 13px; color: #A9ADA2; max-width: 1400px">Replaces the “Counts as X or Y” text on the six dual commons. Each either-or card sits beside a two-affinity card of the same elements, to test for confusion. Counting rule in every version: one mark is one affinity; an either-or mark is one affinity, its element chosen at round end. Chosen for now (Nov 1): E, at the top.</p>
</div>
{rows}</div>
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
out = sys.argv[1]
open(os.path.join(out, 'Either-or.dc.html'), 'w').write(html)
print('ok', len(html))
