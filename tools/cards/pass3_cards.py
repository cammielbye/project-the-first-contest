# Third pass: card faces with line-work art, text below the affinity rings (at most 2 lines).
import sys, os, json, html as _html
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lib import *
import lib, commons, uncommons, rares, forces, art3, pass3
from fontcss import local_fonts
lib.CIRCLED = True

# ---------- art lookup ----------
OLD = {}
for lst in (commons.FIRE, commons.WATER, commons.AIRL, commons.EARTHL):
    for n, a in lst: OLD[n] = a
for c in uncommons.CARDS: OLD[c[0]] = c[4]
for c in rares.RARES + rares.PINNACLES: OLD[c[0]] = c[5]
ALIAS = {'Fumarole': 'Crater', 'Shoal': 'Cove', 'Fen': 'Bog', 'Eyrie': 'Overlook', 'Stone Field': 'Boulder', 'Heath': 'Steppe',
         'Peat Bog': 'Swamp', 'Spray Coast': 'Cliff', 'Mudflat': 'Clay Bank', 'Foothills': 'Prairie', 'Canyon': 'Echo Canyon',
         'Deep Lake': 'Lake', 'Twin Peaks': 'Mountain', 'Wilderness': 'Forest', 'Tidal Flat': 'Estuary', 'Old Growth': 'Woodland',
         'Cavern': 'Cave', 'Sand Sea': 'Dune Sea', 'Misty Fjord': 'Fjord', 'High Desert': 'Mesa', 'Smoking Hills': 'Ashen Range'}
OLD_FORCE = {'Brushfire': forces.art_brushfire, 'Gust': forces.art_gust, 'Overgrowth': forces.art_overgrowth, 'Fog': forces.art_fog,
             'Gale': forces.art_gale, 'Thaw': forces.art_thaw, 'Collapse': forces.art_collapse, 'Steam Explosion': forces.art_steamburst,
             'Deluge': forces.art_deluge}
CROPF = os.path.join(HERE, 'crop3.json')
CROP = json.load(open(CROPF)) if os.path.exists(CROPF) else {}
SIZES = json.load(open(os.path.join(HERE, 'sizes3.json')))

PH, FH = 220, 214  # art panel heights (permanence, force)
def perm_art(name):
    """(art function, viewBox) for a permanence face."""
    if name in art3.NEW_PERM: return art3.NEW_PERM[name], '0 0 288 %d' % PH
    src = ALIAS.get(name, name)
    y0 = CROP.get(src, 30)
    return OLD[src], '0 %g 288 %d' % (y0, PH)
def force_art(fname):
    if fname in art3.FORCE_ART: return art3.FORCE_ART[fname], '0 0 288 %d' % FH, 'xMidYMid meet'
    return OLD_FORCE[fname], '0 0 288 192', 'xMidYMid slice'

# ---------- text ----------
INLINE_RING = ('<svg viewBox="0 0 32 32" style="width: 0.74em; height: 0.74em; vertical-align: -0.06em" fill="none" aria-label="one-affinity">'
               '<circle cx="16.7" cy="16.7" r="13.4" stroke="#0D0F0D" stroke-width="2.6"></circle><circle cx="16" cy="16" r="13.4" stroke="%s" stroke-width="2.6"></circle></svg>' % RING)
# Elements in rules text are drawn, never written (Cam, Nov 2). The element a card turns
# something INTO ("becomes fire") is ringed, as an affinity; every other mention is the bare symbol.
import re as _re
def inline_bare(el):
    d, c = GLYPH[el]
    return (f'<svg viewBox="0 0 24 24" role="img" aria-label="{el}" style="width: 0.78em; height: 0.78em; vertical-align: -0.07em; margin: 0 0.04em" fill="none" '
            f'stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"><g transform="translate(1 1)" stroke="{SH}"><path d="{d}"></path></g><g stroke="{c}"><path d="{d}"></path></g></svg>')
def inline_ringed(el):
    d, c = GLYPH[el]
    t = 'translate(6.4 6.8) scale(0.8)'
    return (f'<svg viewBox="0 0 32 32" role="img" aria-label="{el} affinity" style="width: 0.98em; height: 0.98em; vertical-align: -0.17em; margin: 0 0.03em" fill="none" '
            f'stroke-linejoin="round" stroke-linecap="round"><circle cx="16.8" cy="16.8" r="14" stroke="{SH}" stroke-width="2.2"></circle><circle cx="16" cy="16" r="14" stroke="{RING}" stroke-width="2"></circle>'
            f'<g transform="translate(0.9 0.9)"><g transform="{t}" stroke="{SH}" stroke-width="2.6"><path d="{d}"></path></g></g><g transform="{t}" stroke="{c}" stroke-width="2.6"><path d="{d}"></path></g></svg>')
_EL = r'(fire|water|air|earth)'
def elements_drawn(t):
    t = _re.sub(r'\b(becomes?|become)\s+' + _EL + r'\b', lambda m: m.group(1) + ' \x00R' + m.group(2).lower() + '\x00', t, flags=_re.I)
    t = _re.sub(r'\b' + _EL + r'\b', lambda m: '\x00B' + m.group(1).lower() + '\x00', t, flags=_re.I)
    # a symbol keeps the punctuation after it on its line
    return _re.sub('\x00([RB])(fire|water|air|earth)\x00([.,;:]?)',
                   lambda m: '<span style="white-space: nowrap">' + (inline_ringed if m.group(1) == 'R' else inline_bare)(m.group(2)) + m.group(3) + '</span>', t)
def fmt(t): return elements_drawn(_html.escape(t, quote=False).replace("'", '’').replace('◯', INLINE_RING))
def textbox(t, size, italic, top, h, color='#ECE6D6'):
    if not t: return ''
    st = 'italic' if italic else 'normal'
    return (f'<div class="rules3" style="position: absolute; left: 12px; width: 296px; top: {top}px; height: {h}px; display: flex; align-items: center; justify-content: center; '
            f'text-align: center; font-size: {size}px; font-style: {st}; font-weight: 500; line-height: 1.08; color: {color}; text-shadow: 1px 1px 0 #0D0F0D">'
            f'<div>{fmt(t)}</div></div>')

# ---------- shared bits ----------
def grain(i, op=0.16, extra=''):
    return (f'<svg width="320" height="448" style="position: absolute; top: 0; left: 0" aria-hidden="true"><defs><filter id="grain{i}"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="3" stitchTiles="stitch" seed="{i}"></feTurbulence>'
            f'<feColorMatrix type="saturate" values="0"></feColorMatrix></filter></defs><rect width="320" height="448" rx="14" filter="url(#grain{i})" opacity="{op}"></rect>{extra}</svg>')
EMBERDEF = '<defs><filter id="ember{i}" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.2" result="b"></feGaussianBlur><feMerge><feMergeNode in="b"></feMergeNode><feMergeNode in="SourceGraphic"></feMergeNode></feMerge></filter></defs>'
def panel(i, name, h, fn, vb, par='xMidYMid meet', bg='rgba(0,0,0,0.2)'):
    return (f'<div role="img" aria-label="{name}" style="position: absolute; top: 50px; left: 16px; width: 288px; height: {h}px; border-radius: 10px; background: {bg}; '
            f'box-shadow: inset 0 4px 12px rgba(0,0,0,0.65), inset 0 -1px 0 rgba(255,255,255,0.07); overflow: hidden">'
            f'<svg width="288" height="{h}" viewBox="{vb}" preserveAspectRatio="{par}" fill="none" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            + EMBERDEF.format(i=i) + fn(i) + '</svg></div>')
def title(name, italic=False, top=10, size=26):
    st = 'font-style: italic; ' if italic else ''
    return (f'<div style="position: absolute; top: {top}px; left: 16px; width: 288px; height: 38px; display: flex; align-items: center; justify-content: center; '
            f'font-size: {size}px; font-weight: 600; {st}color: #ECE6D6; text-shadow: 1px 1px 0 #0D0F0D">{name}</div>')
DIVIDER = ('<svg width="288" height="10" viewBox="0 0 288 10" style="position: absolute; top: 384px; left: 16px" aria-hidden="true"><path d="M32 5 H256" stroke="#0D0F0D" stroke-width="3" transform="translate(0 1)"></path>'
           '<path d="M32 5 H256" stroke="#7E827A" stroke-width="1.4"></path><path d="M24 5 L32 1 L40 5 L32 9 Z M248 5 L256 1 L264 5 L256 9 Z" fill="#7E827A"></path></svg>')
def footer(num, rar, numc='#B9BCB0'):
    rc = '#C9973A' if rar == 'S' else '#C2C5B8'
    return (f'<div style="position: absolute; left: 22px; top: 404px; height: 32px; display: flex; align-items: center; font-family: \'IBM Plex Mono\', monospace; font-size: 14px; letter-spacing: 0.04em; color: {numc}">{num}/100</div>'
            f'<div role="img" aria-label="Rarity {rar}, {RARITY[rar]}" style="position: absolute; right: 18px; top: 402px; width: 36px; height: 36px">'
            f'<div style="position: absolute; top: 7px; left: 7px; width: 20px; height: 20px; transform: rotate(45deg); border: 1.6px solid {rc}; box-shadow: 1px 1px 0 #0D0F0D"></div>'
            f'<div style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-size: 19px; font-weight: 700; color: {rc}; text-shadow: 1px 1px 0 #0D0F0D">{rar}</div></div>')
NO_AFF = ('<svg width="44" height="44" viewBox="0 0 32 32" fill="none" aria-hidden="true"><circle cx="16" cy="16" r="14.6" stroke="#7E827A" stroke-width="1.2" stroke-dasharray="2.5 3.5"></circle></svg>'
          '<div style="font-family: \'IBM Plex Mono\', monospace; font-size: 11px; letter-spacing: 0.12em; color: #8E9288">NO AFFINITY</div>')
def small_glyph(el, size=17):
    d, c = GLYPH[el]
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" aria-hidden="true">'
            f'<g transform="translate(0.8 0.8)" stroke="#0D0F0D"><path d="{d}"></path></g><g stroke="{c}"><path d="{d}"></path></g></svg>')
def elements_of(affs):
    out = []
    for a in affs:
        for e in a.split('|'):
            if e != 'any' and e not in out: out.append(e)
    return [e for e in ['fire', 'water', 'air', 'earth'] if e in out]

# ---------- faces ----------
def perm_face(i, c):
    no, name, rar, affs, ptxt, *_ = c
    fn, vb = perm_art(name)
    rings = ''.join(ringed(a, 44, 0.9) for a in affs) if affs else NO_AFF  # bigger affinity rings (Cam, Nov 3)
    label = affinity_label(affs) if affs else 'none'
    return (f'<div class="face perm" style="position: relative; width: 320px; height: 448px; flex: none; border-radius: 14px; background: #353A35; '
            f'box-shadow: 0 14px 32px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.08), inset 0 -4px 10px rgba(0,0,0,0.45)">'
            + grain(i) + title(name) + panel(i, name, PH, fn, vb)
            + f'<div role="img" aria-label="Affinity: {label}" style="position: absolute; top: 271px; left: 16px; width: 288px; height: 44px; display: flex; align-items: center; justify-content: center; gap: 10px">{rings}</div>'
            + textbox(ptxt, SIZES.get('p:' + name, 28), True, 316, 64)
            + DIVIDER + footer(no, rar) + '</div>')

FORCE_BG = '#2A2F32'
def force_face(i, c):
    no, name, rar, affs, ptxt, fname, dur, ftxt = c
    fn, vb, par = force_art(fname)
    durtxt = 'LASTS THE ROUND' if dur == 'round' else 'ONCE'
    els = elements_of(affs)
    marks = ''.join(small_glyph(e) for e in els)
    ellab = ', '.join(els) if els else 'no element'
    hatch = (f'<defs><pattern id="hatch{i}" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)"><path d="M0 0 V9" stroke="#C2C5B8" stroke-width="1"></path></pattern></defs>'
             f'<rect width="320" height="448" rx="14" fill="url(#hatch{i})" opacity="0.05"></rect>'
             '<rect x="5.5" y="5.5" width="309" height="437" rx="10" fill="none" stroke="#7E8A90" stroke-width="1" stroke-dasharray="3 5" opacity="0.55"></rect>')
    return (f'<div class="face force" style="position: relative; width: 320px; height: 448px; flex: none; border-radius: 14px; background: {FORCE_BG}; '
            f'box-shadow: 0 14px 32px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.06), inset 0 -4px 10px rgba(0,0,0,0.5)">'
            + grain(i, 0.14, hatch) + title(fname, italic=True) + panel(i, fname, FH, fn, vb, par, 'rgba(0,0,0,0.22)')
            + f'<div role="img" aria-label="Force, {durtxt.lower()}; element: {ellab}" style="position: absolute; top: 270px; left: 16px; width: 288px; height: 20px; display: flex; align-items: center; justify-content: center; gap: 8px; '
              f'font-family: \'IBM Plex Mono\', monospace; font-size: 11px; letter-spacing: 0.12em; color: #A9B3B8; white-space: nowrap"><span style="display: flex; gap: 3px">{marks}</span><span>FORCE · {durtxt}</span></div>'
            + textbox(ftxt, SIZES.get('f:' + fname, 28), False, 298, 80)
            + DIVIDER + footer(no, rar) + '</div>')

VOIDC = art3.VOIDC
def meta_face(i, no, name, rar, text):
    border = (f'<rect x="5.5" y="5.5" width="309" height="437" rx="10" fill="none" stroke="{VOIDC}" stroke-width="1" opacity="0.45"></rect>'
              f'<rect x="10.5" y="10.5" width="299" height="427" rx="7" fill="none" stroke="{VOIDC}" stroke-width="0.6" opacity="0.25"></rect>')
    return (f'<div class="face meta" style="position: relative; width: 320px; height: 448px; flex: none; border-radius: 14px; background: #1E1F24; '
            f'box-shadow: 0 14px 32px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.05), inset 0 -4px 10px rgba(0,0,0,0.5)">'
            + grain(i, 0.12, border) + title(name) + panel(i, name, 214, art3.META_ART[name], '0 0 288 182', 'xMidYMid meet', 'rgba(0,0,0,0.28)')
            + f'<div style="position: absolute; top: 270px; left: 16px; width: 288px; height: 20px; display: flex; align-items: center; justify-content: center; font-family: \'IBM Plex Mono\', monospace; font-size: 11px; letter-spacing: 0.12em; color: #A9A3B8">META · ONE FACE · EITHER PLAYER</div>'
            + textbox(text, SIZES.get('m:' + name, 28), False, 298, 80)
            + DIVIDER + footer(no, rar, '#8F8A9C') + '</div>')

CAP = "font-family: 'IBM Plex Mono', monospace; font-size: 11px; letter-spacing: 0.1em; color: #7E827A"
def pair(i, c):
    return (f'<div style="display: flex; flex-direction: column; gap: 10px"><div style="display: flex; gap: 12px">{perm_face(i, c)}{force_face(i + 1, c)}</div>'
            f'<div style="display: flex; gap: 12px; {CAP}"><div style="width: 320px; text-align: center">PERMANENCE</div><div style="width: 320px; text-align: center">FORCE</div></div></div>')
def single(i, m):
    no, name, rar, text = m
    return (f'<div style="display: flex; flex-direction: column; gap: 10px">{meta_face(i, no, name, rar, text)}'
            f'<div style="{CAP}; text-align: center">META</div></div>')

# ---------- boards ----------
HEAD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
{local}
</head>
<body>
<x-dc>
<helmet>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500;1,600&amp;family=IBM+Plex+Mono:wght@400;500;600&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0}}
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
<div>Each ring is one affinity; a capsule with two symbols is one affinity, either element. In rules text a bare symbol names an element, and a ringed one is the single affinity a card becomes.</div>
<div>The small marks beside FORCE are the force’s elements, from its card: they decide what “ignores air forces” and the like ignore.</div>
<div>“Loses its affinities”: counts toward neither world points nor the tie-break. “Adjacent”: shares a side. “Remove”: to the void. “Return”: to the binder.</div>
<div>Force tiers: common forces are everyday weather, uncommon ones are severe, rare ones are disasters.</div>
</div>'''
def header(t, sub):
    return f'''<div style="display: flex; justify-content: space-between; align-items: flex-end; gap: 40px">
<div style="display: flex; flex-direction: column; gap: 6px">
<h1 style="margin: 0; font-size: 40px; font-weight: 600">{t}</h1>
<p style="margin: 0; {MONO}; font-size: 13px; color: #A9ADA2; max-width: 1200px">{sub}</p>
</div>
{LEGEND}
</div>
'''
def label(t): return f'<div style="{MONO}; font-size: 12px; letter-spacing: 0.12em; color: #A9ADA2">{t}</div>'
def rows_of(items, n, gap=56):
    return ''.join(f'<div style="display: flex; gap: {gap}px">{"".join(items[k:k + n])}</div>\n' for k in range(0, len(items), n))
def group(lab, items, n=4, gap=56):
    return f'<div style="display: flex; flex-direction: column; gap: 14px">{label(lab)}<div style="display: flex; flex-direction: column; gap: 28px">{rows_of(items, n, gap)}</div></div>\n'

W = 2880
def boards():
    out = {}
    C = pass3.C_
    groups = [('FIRE · 7', C[0:7]), ('WATER · 7', C[7:14]), ('AIR · 7', C[14:21]), ('EARTH · 7', C[21:28]), ('EITHER-OR · 12', C[28:40])]
    idx = 1000; body = header('Third pass: commons (40)', 'Nov 2, 2026. One affinity or an either-or capsule. Common forces are everyday weather. Art is line-work after the first Volcano; rules text sits below the rings, two lines at most.')
    for lab, cs in groups:
        items = []
        for c in cs: idx += 2; items.append(pair(idx, c))
        body += group('COMMON · ' + lab, items)
    out['Pass3-Commons.dc.html'] = ('Third pass: commons (40)', body)
    B = pass3.B_
    idx = 1200; body = header('Third pass: uncommons (28)', 'Two affinities, two of one element, the wildcard, Mirage, and single affinities with stronger text. Uncommon forces are severe weather.')
    bg = [('TWO ELEMENTS · 12', B[0:12]), ('TWO OF ONE · 4', B[12:16]), ('WILDCARD AND MIRAGE · 2', B[16:18]), ('ONE AFFINITY, STRONGER TEXT · 10', B[18:28])]
    for lab, cs in bg:
        items = []
        for c in cs: idx += 2; items.append(pair(idx, c))
        body += group('UNCOMMON · ' + lab, items)
    out['Pass3-Uncommons.dc.html'] = ('Third pass: uncommons (28)', body)
    A = pass3.A_
    idx = 1400; body = header('Third pass: rares (20)', 'Every combination of three elements, every two-and-one split, and four rules-benders. Rare forces are disasters.')
    ag = [('THREE ELEMENTS · 4', A[0:4]), ('TWO AND ONE · 12', A[4:16]), ('RULES-BENDERS · 4', A[16:20])]
    for lab, cs in ag:
        items = []
        for c in cs: idx += 2; items.append(pair(idx, c))
        body += group('RARE · ' + lab, items)
    out['Pass3-Rares.dc.html'] = ('Third pass: rares (20)', body)
    idx = 1600; body = header('Third pass: pinnacles, Origin and meta', 'Four pinnacles, the meta pinnacle Gap, card 101 (Origin, one of each affinity), and seven meta cards: one face, usable by either player.')
    items = []
    for c in pass3.S_: idx += 2; items.append(pair(idx, c))
    body += group('PINNACLE · S · 4', items)
    idx += 2
    body += f'<div style="display: flex; gap: 56px">{group("CARD 101 · S", [pair(idx, pass3.ORIGIN)], 1)}'
    idx += 2
    body += group('META PINNACLE · S', [single(idx, pass3.GAP)], 1) + '</div>\n'
    ms = []
    for m in pass3.META: idx += 1; ms.append(single(idx, m))
    body += group('META · 7', ms, 7, 34)
    out['Pass3-Pinnacles-meta.dc.html'] = ('Third pass: pinnacles, Origin and meta', body)
    return out

def write(outdir, H, local=False):
    for fname, (t, body) in boards().items():
        h = H.get(fname, 3000)
        doc = HEAD.format(title=t, W=W, H=h, local=local_fonts() if local else '') + body + TAIL.format(W=W, H=h)
        open(os.path.join(outdir, fname), 'w').write(doc)
        print('wrote', fname, len(doc), h)

# crop measuring page for reused permanence art
def crop_page(path):
    names = sorted(set(ALIAS.get(c[1], c[1]) for c in pass3.ALL if c[1] not in art3.NEW_PERM))
    body = ''.join(f'<svg class="cr" data-n="{n}" width="288" height="280" viewBox="0 0 288 280" fill="none">{EMBERDEF.format(i=k)}{OLD[n](k)}</svg>' for k, n in enumerate(names))
    open(path, 'w').write('<!doctype html><html><body style="margin:0">' + body + '</body></html>')

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'crop': crop_page(sys.argv[2])
    else:
        H = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else {}
        write(sys.argv[2], H, local=(cmd == 'preview'))
