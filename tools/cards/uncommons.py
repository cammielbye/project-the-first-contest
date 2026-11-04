import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
from commons import ell, ground, back, rockp, rocks, grass, conifers, roundtrees, sunp, cloudp, windp, birdsp, steamp, reeds

# ---------- art, 288 x 280 panel; effect cards keep the key art above y 200 ----------
def u_boilinglake(i):
    bubbles = ' '.join(ell(x, y, r, r * 0.7) for x, y, r in [(110, 206, 5), (150, 214, 7), (184, 204, 4), (132, 226, 4), (170, 230, 5)])
    return (back('M0 120 L60 84 L110 108 L170 70 L230 100 L288 86')
      + ground(176, -4)
      + F([ell(144, 216, 112, 34)], DEEP) + L([ell(144, 216, 112, 34)], WAT, 1.8)
      + L([bubbles], WAT, 1.3)
      + L([steamp(104, 196, 90), steamp(150, 190, 110), steamp(194, 196, 86)], HI, 1.4)
      + EM(['M40 222 q10 -6 20 0', 'M226 220 q10 -6 20 0'], i, 2))
def u_desert(i):
    return (L([sunp(222, 62, 20)], HI, 1.5)
      + F(['M0 170 Q60 140 120 160 Q190 128 288 156 L288 280 L0 280 Z'])
      + L(['M0 170 Q60 140 120 160 Q190 128 288 156'], HI, 1.8)
      + L(['M0 220 Q80 186 160 214 Q220 190 288 210', 'M0 258 Q100 232 200 256 Q250 246 288 252'], MID, 1.4)
      + L([windp(10, 96, 100), windp(130, 112, 110), windp(30, 130, 80)], AIR, 1.5))
def u_badlands(i):
    hoodoos = ['M30 230 L36 150 Q52 136 66 150 L72 230 Z', 'M96 230 L104 120 Q122 104 140 120 L148 230 Z', 'M176 230 L182 160 Q196 148 210 160 L216 230 Z', 'M234 230 L238 182 Q250 172 262 182 L266 230 Z']
    return (L([sunp(240, 56, 14, False)], HI, 1.4)
      + F(hoodoos) + L([h[:-2] for h in hoodoos], HI, 1.8)
      + L(['M38 176 H70 M36 204 H71 M104 150 H144 M103 186 H146 M182 186 H212 M236 206 H264'], EARTHC, 1.3, shadow=False)
      + ground(230, 0)
      + L([windp(10, 70, 90), windp(120, 84, 100)], AIR, 1.5))
def u_volcano(i):
    return ('<g transform="translate(0 -8)">'
      + L(['M168 92 a32 32 0 1 0 64 0 a32 32 0 1 0 -64 0', 'M176 92 a24 24 0 1 0 48 0 a24 24 0 1 0 -48 0', 'M200 48v8 M200 128v8 M156 92h8 M236 92h8 M169 61l6 6 M225 117l6 6 M231 61l-6 6 M175 117l-6 6'], HI, 1.6)
      + L(['M0 186 L34 158 L58 170 L90 138 L118 160 L150 146 L182 162 L214 140 L246 164 L288 150'], LOW, 1.4, shadow=False)
      + F(['M22 250 L126 104 L138 112 L150 112 L162 104 L266 250 Z'])
      + L(['M22 250 L126 104 L138 112 L150 112 L162 104 L266 250', 'M126 104 Q144 96 162 104'], HI, 2)
      + L(['M96 148 Q144 138 192 148 M70 184 Q144 170 218 184 M48 216 Q144 198 240 216', 'M126 104 L104 160 L84 214 M162 104 L184 160 L204 214'], MID, 1.4)
      + EM(['M140 114 L134 140 L142 156 L132 186'], i, 2)
      + L(['M6 258 H282 M26 266 H262 M52 274 H236'], MID, 1.3, shadow=False)
      + '</g>')
def u_basalt(i):
    cols = []
    for k, (x, top) in enumerate([(20, 150), (52, 130), (84, 112), (116, 96), (148, 112), (180, 132), (212, 150), (244, 172)]):
        cols.append('M%d 280 L%d %d L%d %d L%d %d L%d %d L%d 280 Z' % (x, x, top, x + 8, top - 8, x + 24, top - 8, x + 32, top, x + 32))
    return (L([wave(0, 236, 6, 32, 10)], WAT, 1.4, shadow=False)
      + F(cols) + L([c[:-2] for c in cols], HI, 1.6)
      + L(['M28 200 H48 M60 180 H80 M92 160 H112 M124 150 H144 M156 170 H176 M188 190 H208'], MID, 1.2, shadow=False)
      + EM(['M100 230 v-20 M164 236 v-18'], i, 1.6)
      + back(cloudp(10, 60, 3, 16)))
def u_cloudsea(i):
    return (L([sunp(60, 56, 16)], HI, 1.4)
      + F(['M60 200 L120 90 L150 110 L190 70 L250 200 Z']) + L(['M60 200 L120 90 L150 110 L190 70 L250 200'], HI, 2)
      + L(['M120 90 L112 118 L126 110 L140 124 L150 110', 'M190 70 L180 102 L194 94 L206 108'], AIR, 1.5)
      + F(['M0 190 L288 190 L288 280 L0 280 Z'], '#33393A')
      + L([cloudp(0, 196, 9, 16), cloudp(16, 226, 8, 16), cloudp(0, 256, 9, 16)], AIR, 1.5, shadow=False, op='0.9'))
def u_delta(i):
    river = ['M144 60 C140 100 150 120 144 150', 'M144 150 C120 180 90 210 40 270', 'M144 150 C140 190 130 230 120 278', 'M144 150 C170 186 200 220 250 272', 'M144 150 C160 200 176 240 190 278']
    return (back('M0 70 Q144 50 288 70')
      + F(['M0 80 Q144 64 288 80 L288 280 L0 280 Z'])
      + L(['M0 80 Q144 64 288 80'], HI, 1.6)
      + L(river, WAT, 2)
      + grass((80, 160), (210, 170), (70, 230), (220, 236), (150, 250))
      + L([wave(0, 272, 3, 24, 12)], WAT, 1.1, shadow=False))
def u_fjord(i):
    l, r = 'M0 30 L90 50 L110 120 L122 220 L0 280 Z', 'M288 40 L200 52 L180 120 L166 220 L288 280 Z'
    return (back('M110 50 L130 30 L150 44 L170 26 L196 48')
      + F([l, r]) + L(['M0 30 L90 50 L110 120 L122 220 L0 280', 'M288 40 L200 52 L180 120 L166 220 L288 280'], HI, 2)
      + F(['M122 220 L166 220 L250 280 L40 280 Z'], DEEP)
      + L(['M126 230 H162 M108 246 H180 M84 262 H204'], WAT, 1.4)
      + L(['M10 90 H70 M14 150 H90 M216 100 H280 M200 160 H276'], MID, 1.2, shadow=False))
def u_estuary(i):
    return (L(['M0 96 H288'], LOW, 1.2, shadow=False)
      + L([wave(0, 112, 5, 32, 9)], WAT, 1.4)
      + F(['M0 140 L100 140 Q130 170 120 280 L0 280 Z', 'M288 140 L200 140 Q170 170 180 280 L288 280 Z'])
      + L(['M0 140 L100 140 Q130 170 120 280', 'M288 140 L200 140 Q170 170 180 280'], HI, 1.8)
      + L(['M144 280 Q140 220 150 140', 'M130 200 q8 -3 16 0 M150 240 q8 -3 16 0'], WAT, 1.4)
      + L([ell(150, 128, 26, 5), ell(214, 124, 16, 4)], MID, 1.3)
      + reeds((40, 170, 30), (54, 174, 40), (240, 172, 34), (254, 176, 26)))
def u_mountain(i):
    m = 'M0 250 L70 120 L104 150 L160 50 L216 140 L244 120 L288 190 L288 280 L0 280 Z'
    return (F([m]) + L(['M0 250 L70 120 L104 150 L160 50 L216 140 L244 120 L288 190'], HI, 2)
      + L(['M160 50 L146 86 L162 78 L176 94 L186 84', 'M70 120 L62 144 L74 138 L86 148'], AIR, 1.6)
      + L(['M160 50 L140 150 L128 250 M160 50 L180 150 L196 250'], MID, 1.3)
      + L([windp(190, 40, 90), windp(10, 60, 70)], AIR, 1.5))
def u_lavalake(i):
    crust = ['M70 210 L104 200 L118 214 L92 226 Z', 'M150 204 L186 200 L196 214 L160 222 Z', 'M120 230 L150 226 L160 240 L128 244 Z']
    return (back('M0 110 L80 70 L150 96 L220 64 L288 96')
      + F(['M10 190 Q144 150 278 190 L278 280 L10 280 Z'])
      + L(['M10 190 Q144 150 278 190'], HI, 2)
      + F([ell(144, 222, 104, 32)], '#3A2420') + EM([ell(144, 222, 104, 32)], i, 2.2)
      + F(crust, '#2B2F2B') + L(crust, MID, 1.2, shadow=False)
      + EM(['M104 214 L120 224 M186 210 L200 222 M90 232 L110 240'], i, 1.8)
      + L([steamp(144, 186, 90)], HI, 1.3))
def u_lake(i):
    return (back(cloudp(20, 60, 3, 16), cloudp(180, 74, 3, 14))
      + F(['M0 140 Q70 100 140 128 Q210 96 288 132 L288 150 L0 150 Z']) + L(['M0 140 Q70 100 140 128 Q210 96 288 132'], HI, 1.8)
      + F(['M0 150 L288 150 L288 280 L0 280 Z'], DEEP) + L(['M0 150 H288'], WAT, 1.6)
      + L(['M30 170 H110 M160 176 H260 M60 200 H200 M20 230 H130 M170 240 H270 M90 262 H200'], WAT, 1.2, shadow=False, op='0.8')
      + F([ell(200, 196, 30, 8)]) + L([ell(200, 196, 30, 8)], HI, 1.4)
      + conifers((196, 194, 0.6), (208, 192, 0.5)))
def u_highlands(i):
    return (back(cloudp(0, 90, 6, 16))
      + F(['M0 150 Q50 110 100 140 Q150 100 200 136 Q250 106 288 130 L288 280 L0 280 Z'])
      + L(['M0 150 Q50 110 100 140 Q150 100 200 136 Q250 106 288 130'], HI, 2)
      + L(['M0 200 Q70 170 140 196 Q210 168 288 190', 'M0 246 Q90 222 180 244 Q240 230 288 240'], MID, 1.4)
      + rocks((150, 136, 30, 22))
      + L([windp(10, 60, 100), windp(150, 50, 110), windp(70, 172, 80)], AIR, 1.5))
def u_forest(i):
    return (back('M0 110 Q144 90 288 110')
      + L([tree(x, 150, 0.7) for x in range(14, 290, 26)], LOW, 1.2, shadow=False)
      + L([tree(x, 196, 0.95) for x in range(0, 300, 32)], MID, 1.4)
      + ground(240, 0)
      + conifers(*[(x, 250, 1.3) for x in range(20, 290, 44)]))
def u_saltflat(i):
    cells = ' '.join('M%d %d l14 -6 l14 6 l-14 6 Z' % (x, y) for y in (120, 140, 160, 180) for x in range(-10 + (y % 40), 300, 40))
    return (L([sunp(144, 56, 18)], HI, 1.5)
      + L(['M0 104 H288'], HI, 1.6)
      + F(['M0 104 L288 104 L288 280 L0 280 Z'], '#3E4441')
      + L([cells], MID, 1.1, shadow=False))
def u_mirage(i):
    return (L([sunp(230, 50, 14)], HI, 1.4)
      + F(['M0 120 L288 120 L288 280 L0 280 Z']) + L(['M0 120 H288'], HI, 1.6)
      + L(['M40 120 L80 76 L104 96 L130 66 L170 120'], HI, 1.8)
      + L(['M40 122 L80 166 L104 146 L130 176 L170 122'], AIR, 1.4, shadow=False, op='0.6', dash='4 4')
      + L(['M190 140 q-4 -8 0 -16 q4 -8 0 -16', 'M230 150 q-4 -8 0 -16 q4 -8 0 -16'], MID, 1.2, shadow=False))
def u_confluence(i):
    return (back('M0 60 Q144 40 288 60')
      + F(['M0 70 Q144 54 288 70 L288 280 L0 280 Z'])
      + L(['M0 70 Q144 54 288 70'], HI, 1.6)
      + F(['M10 80 C60 110 120 130 136 190 L152 190 C120 120 70 96 30 76 Z', 'M278 80 C230 110 168 130 152 190 L136 190 C166 120 214 96 258 76 Z'], DEEP)
      + L(['M10 80 C60 110 120 130 136 190', 'M30 76 C70 96 120 120 152 190', 'M278 80 C230 110 168 130 152 190', 'M258 76 C214 96 166 120 136 190'], WAT, 1.8)
      + grass((40, 150), (240, 150), (144, 120)))
def u_hangingvalley(i):
    return (F(['M0 70 L120 70 L120 120 L0 120 Z']) + L(['M0 70 L120 70 L120 196'], HI, 2)
      + L(['M10 96 q20 -4 40 0 t40 0'], WAT, 1.4)
      + L(['M118 100 V196', 'M112 100 V192'], WAT, 1.6)
      + F(['M120 196 L288 196 L288 280 L120 280 Z']) + L(['M120 196 H288'], HI, 1.6)
      + conifers((24, 70, 0.6), (50, 70, 0.6), (82, 70, 0.6))
      + L([windp(150, 60, 100), windp(170, 100, 90), windp(150, 140, 100)], AIR, 1.5))
def u_echocanyon(i):
    l, r = 'M0 40 L100 50 L110 200 L0 200 Z', 'M288 40 L188 50 L178 200 L288 200 Z'
    arcs = ' '.join('M%g %g a%g %g 0 0 1 0 %g' % (124 + k * 12, 110 - 10 - k * 8, 10 + k * 8, 10 + k * 8, 20 + k * 16) for k in range(4))
    return (F([l, r]) + L(['M0 40 L100 50 L110 200', 'M288 40 L188 50 L178 200'], HI, 2)
      + L(['M10 90 L96 94 M10 140 L104 144', 'M278 90 L192 94 M278 140 L184 144'], MID, 1.2, shadow=False)
      + L([arcs], AIR, 1.5))
def u_hiddenvalley(i):
    return (F(['M0 200 L0 60 L40 40 L80 100 L120 70 L144 120 L170 64 L210 104 L250 44 L288 70 L288 200 Z'])
      + L(['M0 60 L40 40 L80 100 L120 70 L144 120 L170 64 L210 104 L250 44 L288 70'], HI, 2)
      + F(['M60 200 Q144 130 230 200 Z'], '#232726')
      + roundtrees((110, 196, 12), (140, 190, 14), (172, 196, 12))
      + L([cloudp(40, 150, 3, 14), cloudp(170, 156, 3, 14)], AIR, 1.3, shadow=False, op='0.8'))
def u_petrified(i):
    logs = ['M30 190 L120 176 L124 192 L34 206 Z', 'M150 196 L250 186 L252 200 L152 210 Z']
    return (L([sunp(230, 50, 14, False)], HI, 1.4)
      + ground(170, -4)
      + F(logs) + L(logs, HI, 1.8)
      + L(['M50 186 L52 202 M74 183 L76 199 M98 179 L100 195', 'M174 193 L175 207 M200 191 L201 205 M226 188 L227 202'], EARTHC, 1.3, shadow=False)
      + L([ell(124, 184, 6, 8), ell(252, 193, 5, 7)], MID, 1.3, shadow=False)
      + L(['M80 150 V112 M80 130 l-10 -8 M196 156 V126'], HI, 2))

GL = "Play on earth permanence. It becomes water."
CARDS = [
 ('Boiling Lake', 61, ['fire', 'water'], None, u_boilinglake),
 ('Desert', 62, ['fire', 'air'], None, u_desert),
 ('Hot Spring', 63, ['water', 'fire'], None, art_hotspring),
 ('Badlands', 64, ['fire', 'air'], None, u_badlands),
 ('Volcano', 65, ['fire', 'earth'], None, u_volcano),
 ('Glacier', 66, ['water'], GL, art_glacier),
 ('Basalt Columns', 67, ['fire', 'earth'], None, u_basalt),
 ('Cloud Sea', 68, ['water', 'air'], None, u_cloudsea),
 ('Delta', 69, ['water', 'earth'], None, u_delta),
 ('Fjord', 70, ['water', 'earth'], None, u_fjord),
 ('Sea Cliff', 71, ['earth', 'air'], None, art_seacliff),
 ('Estuary', 72, ['water', 'earth'], None, u_estuary),
 ('Mountain', 73, ['earth', 'air'], None, u_mountain),
 ('Lava Lake', 74, ['fire', 'fire'], None, u_lavalake),
 ('Lake', 75, ['water', 'water'], None, u_lake),
 ('Highlands', 76, ['air', 'air'], None, u_highlands),
 ('Forest', 77, ['earth', 'earth'], None, u_forest),
 ('Cloud Forest', 78, ['air', 'water'], None, art_cloudforest),
 ('Salt Flat', 79, ['fire'], "Choose one affinity on any permanence. It doesn’t count while Salt Flat stands.", u_saltflat),
 ('Mirage', 80, ['fire'], "Also copies the affinities of the permanence played just before it.", u_mirage),
 ('Confluence', 81, ['water', 'any'], "Also counts as one affinity of any element, chosen at the end of the round.", u_confluence),
 ('Hanging Valley', 82, ['air'], "Your air affinities count double.", u_hangingvalley),
 ('Echo Canyon', 83, ['air'], "Also copies the affinities of the next permanence played after it.", u_echocanyon),
 ('Hidden Valley', 84, ['earth'], "Nothing can be played on your other permanence, and their affinities can’t be negated.", u_hiddenvalley),
 ('Petrified Forest', 85, ['earth'], "Stays on the table into the next round, like an original.", u_petrified),
]

W, H = 1856, 2640
def build(outdir):
    tally = {e: 0 for e in ['fire', 'water', 'air', 'earth']}
    for c in CARDS:
        for t in c[2]:
            if t in tally: tally[t] += 1
    rows = [CARDS[k:k + 5] for k in range(0, 25, 5)]
    body = ''; idx = 0
    for r in rows:
        html = ''
        for name, num, tags, rule, art in r:
            idx += 1
            html += card(idx, name, num, 'B', tags, rule, art)
        body += '<div style="display: flex; gap: 40px">%s</div>\n' % html
    effects = sum(1 for c in CARDS if c[3])
    sub = ('Twenty-five permanence faces, numbers 61 to 85: two affinities each, or one affinity and an effect (%d cards). '
           'Affinities in all: fire %d, water %d, air %d, earth %d, plus one wildcard.') % (effects, tally['fire'], tally['water'], tally['air'], tally['earth'])
    legend = ''.join('<div style="display: flex; align-items: center; gap: 8px">%s<span style="font-family: \'IBM Plex Mono\', monospace; font-size: 13px; color: #ECE6D6">%s</span></div>' % (glyph(e, 22), lab) for e, lab in [('fire', 'Fire'), ('water', 'Water'), ('air', 'Air'), ('earth', 'Earth'), ('any', 'Any element')])
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Uncommons</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&amp;family=IBM+Plex+Mono:wght@400;500;600&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0}}
a{{color:#D9A441}}a:hover{{color:#ECE6D6}}
</style>
</helmet>
<div style="width: {W}px; height: {H}px; box-sizing: border-box; padding: 48px; background: #191B1A; color: #ECE6D6; font-family: 'Cormorant Garamond', Georgia, serif; display: flex; flex-direction: column; gap: 40px">
<div style="display: flex; justify-content: space-between; align-items: flex-end; gap: 32px">
<div style="display: flex; flex-direction: column; gap: 6px">
<h1 style="margin: 0; font-size: 40px; font-weight: 600">Uncommons</h1>
<p style="margin: 0; font-family: 'IBM Plex Mono', monospace; font-size: 13px; color: #A9ADA2; max-width: 1100px">{sub}</p>
</div>
<div style="display: flex; gap: 22px">{legend}</div>
</div>
{body}</div>
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
    open(os.path.join(outdir, 'Uncommons.dc.html'), 'w').write(html)
    print('ok', tally, effects)

if __name__ == '__main__':
    build(sys.argv[1])
