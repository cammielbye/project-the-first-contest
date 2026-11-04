import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
from commons import ell, ground, back, rocks, grass, conifers, roundtrees, sunp, cloudp, windp, birdsp, steamp

def r_geyserbasin(i):
    pools = [ell(70, 222, 30, 8), ell(200, 236, 40, 10), ell(130, 254, 24, 6)]
    return (back('M0 110 L60 80 L120 100 L190 70 L288 96')
      + ground(180, -4)
      + EM(pools, i, 1.8) + F(pools, DEEP)
      + L(['M90 190 C84 150 96 120 90 70', 'M164 200 C158 160 172 130 164 50', 'M230 196 C224 166 236 140 230 106'], WAT, 1.8)
      + L([cloudp(56, 70, 3, 14), cloudp(130, 50, 3, 16), cloudp(200, 100, 3, 14)], AIR, 1.4, shadow=False)
      + DOTS([(80, 96, 1.6), (100, 110, 1.4), (154, 80, 1.8), (176, 92, 1.4), (222, 124, 1.4), (240, 132, 1.2)], WAT))
def r_ashenrange(i):
    rng = 'M0 230 L40 150 L70 176 L110 90 L150 150 L184 110 L224 170 L254 130 L288 190 L288 280 L0 280 Z'
    return (F([rng]) + L([rng.replace(' L288 280 L0 280 Z', '')], HI, 2)
      + L(['M110 90 L100 150 L92 220 M184 110 L192 170 M254 130 L248 190'], MID, 1.3)
      + EM(['M110 92 L106 110 L114 124 L108 140'], i, 2)
      + L(['M110 88 C120 60 160 54 190 44 C220 36 250 40 288 30', 'M112 80 C130 50 170 38 200 24'], LOW, 6, shadow=False, op='0.6')
      + L(['M110 88 C120 60 160 54 190 44 C220 36 250 40 288 30'], AIR, 1.4, shadow=False)
      + DOTS([(150, 80, 1.4), (190, 70, 1.2), (230, 64, 1.4), (170, 100, 1.2), (250, 90, 1.2), (210, 110, 1.2)], MID))
def r_rainforest(i):
    canopy = ' '.join(ell(x, y, r, r * 0.75) for x, y, r in [(30, 170, 26), (78, 160, 30), (130, 172, 26), (178, 156, 32), (232, 168, 28), (272, 160, 22), (54, 206, 26), (110, 214, 28), (160, 204, 26), (214, 212, 30), (262, 206, 22)])
    return (L(['M20 30 l-6 16 M60 20 l-6 16 M110 34 l-6 16 M170 22 l-6 16 M220 30 l-6 16 M266 20 l-6 16', 'M40 70 l-6 16 M140 64 l-6 16 M250 70 l-6 16'], WAT, 1.2, shadow=False)
      + L([cloudp(0, 120, 9, 16)], AIR, 1.4, shadow=False, op='0.85')
      + F([canopy]) + L([canopy], HI, 1.5)
      + F(['M0 246 L288 246 L288 280 L0 280 Z'], DEEP)
      + L(['M0 246 Q144 236 288 248', wave(0, 266, 4, 28, 11)], WAT, 1.4))
def r_savanna(i):
    acacia = lambda x, y, s: 'M%g %g v%g M%g %g q%g %g %g 0 M%g %g l%g %g M%g %g l%g %g' % (x, y, -40 * s, x - 34 * s, y - 40 * s, 34 * s, -14 * s, 68 * s, x, y - 26 * s, -14 * s, -14 * s, x, y - 26 * s, 14 * s, -14 * s)
    return (L([sunp(144, 120, 40, False)], HI, 1.5)
      + F(['M0 170 L288 170 L288 280 L0 280 Z']) + L(['M0 170 H288'], HI, 1.8)
      + L([acacia(60, 200, 1.1), acacia(220, 214, 1.3)], HI, 1.8)
      + EM(['M110 176 q6 -10 12 0 q6 -8 12 0 q6 -10 12 0 q6 -8 12 0'], i, 1.8)
      + L(['M120 174 C116 150 130 140 124 120'], MID, 1.2, shadow=False)
      + L([' '.join('M%g %g l4 -10' % (x, y) for x, y in [(20, 240), (50, 256), (100, 236), (140, 260), (180, 240), (250, 258), (270, 236)])], MID, 1.3))
def r_dunesea(i):
    return (L([sunp(220, 56, 22)], HI, 1.5)
      + F(['M0 140 Q40 120 80 136 Q130 112 180 132 Q230 110 288 128 L288 280 L0 280 Z'])
      + L(['M0 140 Q40 120 80 136 Q130 112 180 132 Q230 110 288 128'], HI, 1.8)
      + L(['M0 186 Q50 160 100 182 Q160 150 220 178 Q256 166 288 176', 'M0 236 Q70 206 140 232 Q210 200 288 228'], HI, 1.6)
      + L(['M100 182 Q110 220 104 280', 'M220 178 Q228 210 222 250'], MID, 1.3)
      + L(['M130 116 q20 -8 40 -4', 'M228 112 q22 -8 44 -2', 'M60 158 q24 -10 48 -4'], AIR, 1.4)
      + L([windp(10, 70, 90)], AIR, 1.4))
def r_icesheet(i):
    return (L([sunp(60, 70, 14, False)], HI, 1.4)
      + L(['M0 90 H288'], HI, 1.4)
      + F(['M0 90 L288 90 L288 280 L0 280 Z'], '#3E4547')
      + L(['M0 120 L40 112 L70 122 L110 108 L150 118 L190 106 L230 116 L288 104', 'M0 160 L50 150 L90 162 L140 146 L200 158 L250 144 L288 152'], AIR, 1.6)
      + L(['M60 124 L70 150 M150 120 L144 154 M230 118 L240 148', 'M100 164 L96 196 M200 160 L208 196'], WAT, 1.3)
      + L([windp(150, 50, 110), windp(170, 76, 90)], AIR, 1.4))
def r_mountainrange(i):
    rng = 'M0 200 L30 140 L60 160 L96 70 L130 130 L160 100 L196 40 L236 120 L262 96 L288 140 L288 200 Z'
    return (back('M0 110 L40 80 L90 96 L150 60 L210 84 L288 70')
      + F([rng]) + L([rng.replace(' L288 200 Z', '')], HI, 2)
      + L(['M96 70 L86 98 L100 92 L112 106', 'M196 40 L184 74 L198 66 L212 80 L220 92'], AIR, 1.6)
      + L(['M96 70 L84 200 M196 40 L180 200 M160 100 L170 200'], MID, 1.2, shadow=False))
def p_core(i):
    return (L([ell(144, 140, 120, 120)], HI, 2)
      + F(['M144 20 A120 120 0 0 1 264 140 L144 140 Z'], '#232726')
      + L(['M144 20 A120 120 0 0 1 264 140 L144 140 Z'], HI, 1.8)
      + L(['M144 50 A90 90 0 0 1 234 140', 'M144 80 A60 60 0 0 1 204 140'], MID, 1.4)
      + F([ell(144, 140, 34, 34)], '#3A2420')
      + EM([ell(144, 140, 34, 34), ell(144, 140, 18, 18)], i, 2.2)
      + EM(['M144 106 L150 120 M178 140 L166 146 M144 174 L138 160 M110 140 L122 134'], i, 1.6)
      + L(['M40 120 Q60 100 80 116 M200 230 Q220 214 240 226', 'M60 200 Q80 186 100 198'], LOW, 1.3, shadow=False))
def p_pangaea(i):
    land = 'M70 70 Q120 40 170 60 Q220 50 236 90 Q260 120 230 150 Q246 190 210 210 Q180 240 140 226 Q100 246 80 210 Q40 196 52 160 Q30 120 56 100 Q50 80 70 70 Z'
    return (F(['M0 0 L288 0 L288 280 L0 280 Z'], DEEP)
      + L([wave(0, 30, 3, 24, 12), wave(0, 256, 3, 24, 12), wave(-10, 140, 3, 24, 3), wave(250, 140, 3, 24, 2)], WAT, 1.1, shadow=False, op='0.6')
      + F([land]) + L([land], HI, 2)
      + L(['M100 90 L120 110 L114 140 L136 170 L130 200', 'M180 80 L200 110 L190 140 L210 170'], EARTHC, 1.6)
      + L(['M110 100 l6 -8 l6 8 M126 150 l6 -8 l6 8 M192 120 l6 -8 l6 8'], MID, 1.2, shadow=False))
def p_tradewinds(i):
    return (L(['M0 210 H288'], LOW, 1.2, shadow=False)
      + L([wave(0, 236, 5, 32, 10), wave(0, 260, 6, 40, 8)], WAT, 1.4)
      + L(['M-10 60 C60 30 140 90 210 60 C250 44 270 50 300 40', 'M-10 100 C70 70 150 130 220 100 C256 86 274 92 300 84', 'M-10 140 C80 110 160 170 230 140 C262 126 278 130 300 124', 'M-10 180 C90 150 170 200 240 176 C266 168 280 170 300 164'], AIR, 1.8)
      + L([cloudp(30, 52, 2, 12), cloudp(150, 116, 2, 12), cloudp(80, 168, 2, 12)], HI, 1.3, shadow=False))

ICE = "Fire affinities don’t count, for either player, while Ice Sheet stands."
RANGE = "Every four earth affinities you control also count as one world point."
ARCH = "Win the round with 10 water affinities."
RARES = [
 ('Geyser Basin', 86, 'A', ['fire', 'water', 'air'], None, r_geyserbasin),
 ('Ashen Range', 87, 'A', ['fire', 'air', 'earth'], None, r_ashenrange),
 ('Caldera Lake', 88, 'A', ['fire', 'earth', 'water'], None, art_caldera),
 ('Rainforest', 89, 'A', ['water', 'air', 'earth'], None, r_rainforest),
 ('Savanna', 90, 'A', ['fire', 'fire', 'earth'], None, r_savanna),
 ('Stone Towers', 91, 'A', ['air', 'air', 'earth'], None, art_pillars),
 ('Dune Sea', 92, 'A', ['fire', 'fire', 'air'], None, r_dunesea),
 ('Archipelago', 93, 'A', ['water', 'water', 'earth'], ARCH, art_archipelago),
 ('Ice Sheet', 94, 'A', ['water', 'water'], ICE, r_icesheet),
 ('Mountain Range', 95, 'A', ['earth', 'air'], RANGE, r_mountainrange),
]
PINNACLES = [
 ('Core', 96, 'S', ['fire'] * 4, None, p_core),
 ('Pangaea', 97, 'S', ['earth'] * 4, None, p_pangaea),
 ('Ocean', 98, 'S', ['water'] * 4, None, art_ocean),
 ('Trade Winds', 99, 'S', ['air'] * 4, None, p_tradewinds),
]

PLACEHOLDER = '''<div style="position: relative; width: 320px; height: 448px; flex: none; box-sizing: border-box; border-radius: 14px; border: 2px dashed #4A504A; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; text-align: center; padding: 32px">
<div style="font-size: 24px; font-weight: 600; color: #A9ADA2">Reserved</div>
<div style="font-size: 18px; line-height: 1.3; color: #A9ADA2">The fifth pinnacle: one face, a move on the game itself</div>
<div style="position: absolute; left: 22px; bottom: 12px; height: 32px; display: flex; align-items: center; font-family: 'IBM Plex Mono', monospace; font-size: 14px; letter-spacing: 0.04em; color: #8E9389">100/100</div>
</div>'''

W, H = 1856, 1700
def build(outdir):
    def tally(cards):
        t = {e: 0 for e in ['fire', 'water', 'air', 'earth']}
        for c in cards:
            for x in c[3]:
                if x in t: t[x] += 1
        return t
    tr = tally(RARES)
    idx = 0; body = ''
    for label, row in [('RARE · A · 86–95', RARES[0:5]), ('', RARES[5:10]), ('PINNACLE · S · 96–100', PINNACLES)]:
        html = ''
        for name, num, rar, tags, rule, art in row:
            idx += 1
            html += card(idx, name, num, rar, tags, rule, art)
        if label.startswith('PINNACLE'):
            html += PLACEHOLDER
        lab = ('<div style="font-family: \'IBM Plex Mono\', monospace; font-size: 12px; letter-spacing: 0.12em; color: #A9ADA2">%s</div>' % label) if label else ''
        body += '<div style="display: flex; flex-direction: column; gap: 14px">%s<div style="display: flex; gap: 40px">%s</div></div>\n' % (lab, html)
    sub = ('Rares carry three affinities, or fewer and an effect: fire %d, water %d, air %d, earth %d. Pinnacles carry four of one element. '
           'Whole pool so far (99 cards): fire 36, water 37, air 36, earth 37, plus one wildcard.') % (tr['fire'], tr['water'], tr['air'], tr['earth'])
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Rares and pinnacles</title>
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
<div style="width: {W}px; height: {H}px; box-sizing: border-box; padding: 48px; background: #191B1A; color: #ECE6D6; font-family: 'Cormorant Garamond', Georgia, serif; display: flex; flex-direction: column; gap: 32px">
<div style="display: flex; flex-direction: column; gap: 6px">
<h1 style="margin: 0; font-size: 40px; font-weight: 600">Rares and pinnacles</h1>
<p style="margin: 0; font-family: 'IBM Plex Mono', monospace; font-size: 13px; color: #A9ADA2; max-width: 1300px">{sub}</p>
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
    open(os.path.join(outdir, 'Rares-and-pinnacles.dc.html'), 'w').write(html)
    print('ok', tr)

if __name__ == '__main__':
    build(sys.argv[1])
