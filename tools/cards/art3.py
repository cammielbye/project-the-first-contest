# Third pass art: line-work scenes in the style of the first Volcano.
# Force art is drawn in a 288 x 214 panel; new permanence art in 288 x 220.
import math
from lib import *
from commons import ell, cloudp, windp, birdsp, steamp, sunp, tree, roundtree

PALE = '#E8E4C8'
def GLOW(ds, i, color=PALE, w=2.2): return '<g filter="url(#ember%d)" stroke="%s" stroke-width="%s">%s</g>' % (i, color, w, P(ds))
def fill(ds, c=FILL): return F(ds, c)

# ---------- primitives ----------
def gnd(y=160, c=-8, top=HI):
    d = 'M0 %g Q144 %g 288 %g' % (y, y + c, y)
    return F([d + ' L288 230 L0 230 Z']) + L([d], top, 1.8)
def hills(y=110):
    return L(['M0 %d Q40 %d 80 %d T160 %d T240 %d T320 %d' % (y, y - 22, y, y - 4, y - 18, y)], LOW, 1.3, shadow=False)
def ridge(y=120):
    return L(['M0 %d L36 %d L62 %d L96 %d L128 %d L164 %d L198 %d L232 %d L262 %d L288 %d' % (y, y - 26, y - 12, y - 40, y - 18, y - 34, y - 10, y - 30, y - 14, y - 22)], LOW, 1.3, shadow=False)
def seaband(y, n=10, c=WAT, w=1.4, amp=5):
    return L([wave(0, y, amp, 30, n)], c, w, shadow=False)
def clouds(*specs, c=MID):  # (x, y, n, s)
    return L([cloudp(*s) for s in specs], c, 1.5)
def rain(x0, x1, y0, ln, n, dx=-6, c=WAT, w=1.4, rows=1, gap=18):
    ds = []
    for r in range(rows):
        for k in range(n):
            x = x0 + (x1 - x0) * (k + 0.5 * (r % 2)) / n
            y = y0 + r * gap
            ds.append('M%.1f %.1f l%.1f %.1f' % (x, y, dx, ln))
    return L([' '.join(ds)], c, w, shadow=False)
def flake(x, y, s=5):
    return ' '.join('M%.1f %.1f L%.1f %.1f' % (x - s * math.cos(a), y - s * math.sin(a), x + s * math.cos(a), y + s * math.sin(a)) for a in (0, math.pi / 3, 2 * math.pi / 3))
def flakes(pts, c=AIR): return L([' '.join(flake(*p) for p in pts)], c, 1.2, shadow=False)
def bolt(x, y0, y1, seg=5, jag=12):
    pts = [(x, y0)]; h = (y1 - y0) / seg
    for k in range(1, seg + 1):
        pts.append((x + (jag if k % 2 else -jag * 0.6), y0 + h * k))
    return 'M' + ' L'.join('%.1f %.1f' % p for p in pts)
def flame(x, y, h, w=None):
    w = w or h * 0.45
    return 'M%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f' % (
        x - w / 2, y, x - w / 2, y - h * 0.5, x - w * 0.1, y - h * 0.6, x, y - h, x + w * 0.2, y - h * 0.55, x + w / 2, y - h * 0.5, x + w / 2, y)
def flames(i, specs, w=2): return EM([flame(*s) for s in specs], i, w)
def swirl(cx, cy, r, turns=2.2, steps=60):
    pts = []
    for k in range(steps + 1):
        t = k / steps; a = t * turns * 2 * math.pi; rr = r * (1 - t * 0.85)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * 0.8))
    return 'M' + ' L'.join('%.1f %.1f' % p for p in pts)
def funnel(cx, top, bot, wt, wb, n=7, lean=18):
    ds = []
    for k in range(n):
        t = k / (n - 1); y = top + (bot - top) * t; w = wt + (wb - wt) * t; x = cx + lean * t * t
        ds.append(ell(x, y, w, w * 0.22))
    return ds
def curl(x, y, s=1.0):
    return 'M%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f' % (
        x - 60 * s, y, x - 30 * s, y - 10 * s, x - 10 * s, y - 70 * s, x + 30 * s, y - 70 * s,
        x + 60 * s, y - 70 * s, x + 56 * s, y - 34 * s, x + 30 * s, y - 34 * s)
def crack(x, y, ln, seg=6, jag=8):
    pts = [(x, y)]; h = ln / seg
    for k in range(1, seg + 1): pts.append((x + (jag if k % 2 else -jag), y + h * k))
    return 'M' + ' L'.join('%.1f %.1f' % p for p in pts)
def rock(x, y, s=10):
    return 'M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f Z' % (x - s, y, x - s * 0.6, y - s * 0.9, x + s * 0.4, y - s, x + s, y - s * 0.3, x + s * 0.7, y)
def rocks(specs, c=HI): return fill([rock(*s) for s in specs]) + L([rock(*s) for s in specs], c, 1.5)
def arrow(x0, y0, x1, y1, bend=-20, c=HI, w=1.6):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + bend
    ang = math.atan2(y1 - my, x1 - mx); a1, a2 = ang + 2.6, ang - 2.6
    head = 'M%.1f %.1f L%.1f %.1f L%.1f %.1f' % (x1 + 9 * math.cos(a1), y1 + 9 * math.sin(a1), x1, y1, x1 + 9 * math.cos(a2), y1 + 9 * math.sin(a2))
    return L(['M%.1f %.1f Q%.1f %.1f %.1f %.1f' % (x0, y0, mx, my, x1, y1), head], c, w)
def dome(cx, cy, r, c=HI, dash=None):
    return L(['M%.1f %.1f A%.1f %.1f 0 0 1 %.1f %.1f' % (cx - r, cy, r, r * 0.8, cx + r, cy)], c, 1.6, dash=dash)
def vines(x, y, ln, up=True):
    s = -1 if up else 1
    return 'M%.1f %.1f c6 %g 14 %g 8 %g s-14 %g -6 %g s14 %g 6 %g' % (x, y, s * ln * 0.2, s * ln * 0.2, s * ln * 0.4, s * ln * 0.2, s * ln * 0.4, s * ln * 0.2, s * ln * 0.4)
def fogbands(ys, x0=10, x1=278, c=AIR):
    return L(['M%d %d H%d' % (x0 + (k % 2) * 20, y, x1 - (k % 2) * 30) for k, y in enumerate(ys)], c, 1.4, shadow=False, dash='18 10')
def heat(xs, y0, y1):
    return ['M%d %d q6 %g 0 %g t0 %g t0 %g' % (x, y1, (y0 - y1) / 8, (y0 - y1) / 4, (y0 - y1) / 4, (y0 - y1) / 4) for x in xs]
def trees(specs): return L([tree(*s) for s in specs], HI, 1.5)
def rtrees(specs): return L([roundtree(*s) for s in specs], HI, 1.5)
def peak(x, y, w, h): return 'M%g %g L%g %g L%g %g' % (x - w / 2, y, x, y - h, x + w / 2, y)
def mountains(specs, c=HI):
    ds = [peak(*s) for s in specs]
    return fill([d + ' Z' for d in ds]) + L(ds, c, 1.8)
def lakeshape(cx, cy, rx, ry, c=WAT): return F([ell(cx, cy, rx, ry)], DEEP) + L([ell(cx, cy, rx, ry)], c, 1.8)
def sun(cx, cy, r, rays=True, c=HI): return L([sunp(cx, cy, r, rays)], c, 1.5)
def stones(pts, c=EARTHC): return DOTS([(x, y, r) for x, y, r in pts], c)

# ---------- force art (288 x 214) ----------
def f_smolder(i):
    return (gnd(150) + L(['M40 150 Q60 120 50 96', 'M140 146 Q160 116 150 88', 'M230 150 Q246 122 238 98'], MID, 1.4)
      + EM(['M30 170 q8 -6 16 0 q8 6 16 0', 'M120 182 q8 -6 16 0 q8 6 16 0', 'M210 172 q8 -6 16 0'], i, 1.8)
      + DOTS([(60, 160, 1.6), (180, 176, 1.4), (250, 186, 1.6)], EMB, i))
def f_updraft(i):
    return (gnd(176) + sun(144, 186, 22, False) + L([steamp(70, 170, 120), steamp(144, 160, 140), steamp(218, 170, 120)], HI, 1.5)
      + arrow(144, 120, 144, 34, bend=0) + L([birdsp(196, 56), birdsp(60, 70, 0.8)], MID, 1.3))
def f_flareup(i):
    return (gnd(164) + flames(i, [(80, 164, 50), (124, 164, 78), (168, 164, 96), (212, 164, 62)])
      + DOTS([(110, 70, 1.8), (150, 52, 1.6), (196, 80, 1.6), (230, 60, 1.4), (90, 96, 1.4)], EMB, i))
def f_spark(i):
    return (gnd(170) + L(['M180 66 l10 -14 M180 66 l16 2 M180 66 l4 16 M180 66 l-12 -8 M180 66 l-10 12'], EMB, 1.8)
      + GLOW(['M180 66 m-3 0 a3 3 0 1 0 6 0 a3 3 0 1 0 -6 0'], i, EMB) + L([windp(30, 110, 110), windp(70, 134, 90)], AIR, 1.4)
      + L(['M180 66 Q150 110 120 150'], EMB, 1.2, dash='3 6'))
def f_ember(i):
    return (gnd(168) + L(['M144 168 L144 120'], MID, 1.2, shadow=False) + flames(i, [(144, 168, 30, 16)], 1.8)
      + DOTS([(120, 120, 1.4), (160, 100, 1.6), (176, 130, 1.2), (134, 90, 1.2)], EMB, i) + back_hills())
def back_hills(): return hills(118)
def f_kindling(i):
    return (gnd(172) + L(['M100 172 L130 142 M120 172 L150 140 M160 172 L130 144 M176 172 L146 140'], EARTHC, 2)
      + flames(i, [(140, 152, 40), (126, 158, 26), (156, 158, 28)]) + L([steamp(140, 104, 70)], MID, 1.3))
def f_shower(i):
    return (clouds((30, 54, 4, 20), (150, 46, 4, 18)) + rain(30, 270, 66, 18, 16, rows=4, gap=22)
      + gnd(170) + EM(['M120 186 q10 -10 20 0'], i, 1.6) + L(['M120 176 q10 -16 20 0'], MID, 1.2))
def f_current(i):
    return (seaband(70, c=LOW, w=1.2) + seaband(100) + seaband(130) + seaband(160) + arrow(40, 120, 240, 124, bend=-24, c=WAT, w=2)
      + rocks([(200, 186, 12), (90, 196, 9)]))
def f_lowtide(i):
    return (L(['M0 112 H288'], LOW, 1.2, shadow=False, dash='6 6') + F(['M0 150 Q144 140 288 150 L288 230 L0 230 Z'], DEEP)
      + L([wave(0, 150, 4, 32, 10)], WAT, 1.6) + rocks([(70, 150, 14), (190, 148, 18), (240, 152, 10)])
      + L(['M110 132 Q150 126 180 134'], MID, 1.2, dash='3 5'))
def f_drizzle(i):
    return (clouds((20, 50, 5, 18), (170, 40, 3, 18), c=LOW) + rain(20, 270, 64, 8, 22, dx=-3, rows=5, gap=20, w=1.2)
      + gnd(176) + EM(['M140 196 q6 -8 12 0'], i, 1.4))
def f_rain(i):
    return (clouds((10, 46, 5, 20), (180, 40, 3, 22)) + rain(20, 270, 60, 22, 14, rows=4, gap=26) + gnd(170)
      + L(['M60 186 q10 -4 20 0 M150 196 q10 -4 20 0 M220 184 q10 -4 20 0'], WAT, 1.3, shadow=False))
def f_snowmelt(i):
    return (sun(250, 40, 12) + mountains([(80, 140, 120, 90), (200, 140, 140, 104)]) + L(['M58 82 L68 90 L78 80 L88 92 L100 78', 'M170 76 L182 86 L194 74 L206 88 L222 74'], AIR, 1.6)
      + L(['M80 140 Q86 170 76 200', 'M200 140 Q194 172 206 204'], WAT, 1.6) + seaband(200, c=WAT))
def f_freeze(i):
    return (gnd(156, 0, top=WAT) + L(['M20 172 L60 170 M110 176 L180 174 M210 168 L268 170'], AIR, 1.2, shadow=False)
      + flakes([(60, 60, 8), (130, 40, 6), (200, 70, 9), (250, 40, 5), (100, 100, 5), (230, 110, 6)])
      + L(['M60 156 l0 18 M76 156 l0 12 M190 156 l0 20 M206 156 l0 10'], AIR, 1.4))
def f_breeze(i):
    return (L([windp(20, 70, 120), windp(120, 96, 140), windp(40, 126, 110), windp(150, 150, 110)], AIR, 1.5) + gnd(184)
      + L(['M60 184 Q66 170 72 184 M90 184 Q96 172 102 184'], MID, 1.2))
def f_drift(i):
    return (gnd(176) + L([cloudp(40, 70, 3, 18)], HI, 1.6) + arrow(100, 74, 210, 64, bend=-18) + L([cloudp(214, 70, 2, 16)], MID, 1.4, dash='4 4'))
def f_crosswind(i):
    return (gnd(176) + L([windp(10, 80, 140), windp(150, 120, 130)], AIR, 1.6) + arrow(60, 140, 220, 100, bend=-10) + arrow(230, 150, 70, 110, bend=16))
def f_thermal(i):
    return (gnd(184) + flames(i, [(144, 184, 30)]) + L([steamp(144, 150, 110)], AIR, 1.6)
      + L(['M144 50 m-30 0 a30 12 0 1 0 60 0 a30 12 0 1 0 -60 0'], AIR, 1.3, dash='5 5') + L([birdsp(180, 50), birdsp(96, 70, 0.8)], MID, 1.3))
def f_downdraft(i):
    return (clouds((60, 40, 5, 18)) + L(['M100 60 Q104 110 84 150', 'M150 60 Q152 110 140 150', 'M196 60 Q192 110 206 150'], AIR, 1.5)
      + gnd(166) + flames(i, [(160, 166, 26), (60, 166, 18)]) + arrow(150, 120, 150, 154, bend=0))
def f_eddy(i):
    return (seaband(150, c=WAT) + L([swirl(144, 100, 56, 2.4)], AIR, 1.6) + gnd(188))
def f_rockfall(i):
    return (L(['M0 40 L120 160 L288 170'], HI, 1.8) + F(['M0 40 L120 160 L288 170 L288 230 L0 230 Z'])
      + rocks([(100, 120, 12), (140, 150, 14), (60, 80, 9)]) + L(['M86 108 l-10 -8 M128 138 l-10 -8 M50 72 l-8 -6'], MID, 1.2))
def f_dust(i):
    return (gnd(170) + DOTS([(x, y, 1.2) for x, y in [(40, 80), (70, 100), (110, 70), (150, 92), (190, 74), (230, 96), (260, 70), (90, 130), (170, 128), (220, 140)]], EARTHC)
      + L([windp(20, 110, 120), windp(140, 140, 120)], EARTHC, 1.3, shadow=False))
def f_silt(i):
    return (F(['M0 120 L288 120 L288 230 L0 230 Z'], DEEP) + seaband(120) + L(['M0 190 Q80 170 160 186 Q220 196 288 180'], EARTHC, 1.6)
      + DOTS([(60, 160, 1.4), (110, 150, 1.2), (170, 168, 1.4), (230, 156, 1.2), (140, 140, 1)], EARTHC))
def f_dustfall(i):
    return (clouds((40, 50, 4, 20), c=EARTHC) + DOTS([(x, y, 1.3) for x, y in [(60, 80), (90, 100), (120, 90), (150, 110), (180, 96), (100, 130), (160, 140), (130, 120)]], EARTHC)
      + gnd(168) + L(['M80 168 Q144 150 208 168'], EARTHC, 1.6))
def f_tangle(i):
    return (gnd(176) + L([vines(60, 176, 100), vines(120, 176, 120), vines(180, 176, 110), vines(240, 176, 90)], MID, 1.5)
      + L(['M40 120 Q144 90 250 120'], MID, 1.3))
def f_shelter(i):
    return (gnd(178) + rocks([(144, 178, 26)]) + dome(144, 178, 70) + rain(20, 270, 40, 16, 14, rows=2, gap=22))
def f_sinkhole(i):
    return (gnd(130) + F([ell(144, 160, 70, 20)], SH) + L([ell(144, 160, 70, 20)], HI, 1.8) + L([crack(100, 150, 40), crack(190, 152, 40)], MID, 1.2)
      + rtrees([(144, 150, 12)]) + arrow(144, 120, 144, 150, bend=0))
def f_dustdevil(i):
    return (gnd(180) + L(funnel(140, 50, 176, 34, 6), EARTHC, 1.4) + DOTS([(110, 80, 1.4), (172, 100, 1.2), (130, 130, 1.2)], EARTHC))
def f_vent(i):
    return (gnd(170) + F([ell(144, 172, 26, 7)], SH) + L([ell(144, 172, 26, 7)], HI, 1.6) + L([steamp(140, 160, 120), steamp(156, 160, 90)], HI, 1.5)
      + arrow(144, 150, 144, 194, bend=0, c=MID))
def f_mire(i):
    return (F(['M0 140 Q144 130 288 140 L288 230 L0 230 Z'], '#262B24') + L(['M0 140 Q144 130 288 140'], MID, 1.6)
      + L(['M40 170 q14 -6 28 0 M120 160 q14 -6 28 0 M200 176 q14 -6 28 0'], EARTHC, 1.3, shadow=False)
      + L([ell(90, 186, 10, 3), ell(176, 150, 8, 2.5)], MID, 1.2) + L(['M226 140 l0 -30 M232 140 l2 -24 M238 140 l-2 -34'], HI, 1.3))
def f_riptide(i):
    return (F(['M0 100 L288 100 L288 230 L0 230 Z'], DEEP) + seaband(100) + seaband(130, c=LOW, w=1.2)
      + arrow(160, 190, 200, 110, bend=30, c=WAT, w=2) + arrow(110, 190, 150, 116, bend=24, c=WAT, w=1.6)
      + flames(i, [(206, 104, 22)]))
def f_whirl(i):
    return (gnd(176) + L([swirl(150, 100, 70, 2.6)], AIR, 1.6) + rocks([(196, 74, 9)]) + L([windp(10, 160, 100)], AIR, 1.3))
def f_steam(i):
    return (gnd(176) + L([steamp(70, 170, 130), steamp(120, 176, 150), steamp(170, 172, 140), steamp(220, 176, 120)], HI, 1.5)
      + L(['M40 120 H250'], LOW, 1.2, shadow=False, dash='8 8'))
def f_drywind(i):
    return (gnd(150) + F([ell(144, 176, 80, 16)], DEEP) + L([ell(144, 176, 80, 16)], WAT, 1.4, dash='4 5')
      + L([windp(20, 80, 140), windp(110, 110, 160), windp(30, 130, 110)], AIR, 1.5) + sun(240, 50, 16, True))
def f_firebreak(i):
    return (gnd(170) + flames(i, [(50, 170, 40), (80, 170, 30)]) + L(['M120 170 L120 120 M136 170 L136 120'], EARTHC, 1.6)
      + L(['M110 170 L146 170'], EARTHC, 2.2) + trees([(196, 170, 1.0), (234, 170, 0.9)]))
def f_dryingwind(i):
    return (gnd(176) + lakeshape(144, 186, 70, 12) + L([windp(20, 90, 150), windp(110, 120, 150)], AIR, 1.5)
      + L([steamp(120, 176, 60), steamp(170, 178, 50)], MID, 1.2) + sun(60, 50, 16))
def f_tremor(i):
    return (gnd(150) + L([crack(144, 150, 64, 7, 10)], HI, 1.8) + L(['M70 150 l-6 -8 M220 150 l6 -8'], MID, 1.2)
      + rtrees([(90, 146, 12), (200, 146, 14)]))
def f_windbreak(i):
    return (gnd(176) + trees([(100, 176, 1.2), (130, 176, 1.3), (160, 176, 1.25), (190, 176, 1.15)])
      + L([windp(10, 110, 70), windp(14, 140, 60)], AIR, 1.5) + L(['M210 120 Q240 116 270 124'], MID, 1.2, dash='3 6'))
# uncommon
def f_scald(i):
    return (gnd(170) + F([ell(144, 178, 60, 10)], DEEP) + L([ell(144, 178, 60, 10)], WAT, 1.6)
      + L([steamp(110, 170, 110), steamp(144, 172, 140), steamp(180, 170, 120)], HI, 1.6) + EM(['M100 186 q10 -8 20 0 M168 188 q10 -8 20 0'], i, 1.6))
def f_heatwave(i):
    return (sun(144, 60, 28, True, c=EMB) + L(heat([40, 90, 140, 190, 240], 110, 160), EMB, 1.3) + gnd(170))
def f_lavabomb(i):
    return (mountains([(80, 190, 140, 110)]) + EM(['M80 80 Q140 20 200 120', 'M80 84 Q50 40 30 110'], i, 1.6)
      + DOTS([(200, 120, 5), (30, 110, 4), (150, 60, 3)], EMB, i) + gnd(196))
def f_flood(i):
    return (F(['M0 110 L288 110 L288 230 L0 230 Z'], DEEP) + seaband(110) + seaband(140, c=LOW, w=1.2)
      + rtrees([(70, 150, 14), (200, 156, 16)]) + L(['M60 104 l0 -20 M220 104 l0 -14'], MID, 1.2) + arrow(30, 80, 260, 80, bend=-10, c=WAT))
def f_downpour(i):
    return (clouds((0, 40, 6, 24), c=LOW) + rain(10, 278, 52, 30, 20, dx=-8, rows=4, gap=30, w=1.6) + gnd(184)
      + flames(i, [(150, 184, 16)]) + L([steamp(150, 168, 40)], MID, 1.2))
def f_sandstorm(i):
    return (L([windp(0, 60, 160), windp(100, 84, 180), windp(20, 110, 160), windp(120, 134, 160)], EARTHC, 1.6)
      + DOTS([(x, y, 1.2) for x, y in [(30, 70), (80, 96), (130, 72), (180, 100), (230, 80), (60, 126), (150, 120), (250, 116)]], EARTHC)
      + gnd(170) + sun(220, 40, 12, False, c=EMB))
def f_ashfall(i):
    return (L(['M0 40 Q144 20 288 40'], LOW, 1.2, shadow=False) + DOTS([(x, y, 1.6) for x, y in [(30, 60), (70, 80), (110, 66), (150, 90), (190, 70), (230, 86), (260, 64), (50, 110), (130, 120), (210, 112), (90, 140), (170, 146)]], MID)
      + gnd(170) + L(['M40 170 Q144 156 250 170'], MID, 1.6))
def f_cloudburst(i):
    return (L([cloudp(60, 66, 5, 20)], HI, 1.8) + rain(70, 240, 80, 70, 10, dx=-2, w=1.8, c=WAT) + gnd(176) + seaband(176, n=10))
def f_dust_storm(i):
    return (F(['M0 60 Q80 30 160 54 Q220 30 288 50 L288 150 Q144 140 0 150 Z'], '#3A3328') + L(['M0 60 Q80 30 160 54 Q220 30 288 50'], EARTHC, 1.6)
      + L([windp(20, 100, 120), windp(140, 120, 120)], EARTHC, 1.3) + gnd(170))
def f_heatdome(i):
    return (gnd(170) + dome(144, 170, 110, c=EMB) + flames(i, [(110, 170, 24), (150, 170, 30), (190, 170, 22)]) + sun(144, 70, 14, False, c=EMB))
def f_icestorm(i):
    return (clouds((20, 40, 5, 20), c=LOW) + rain(20, 270, 54, 14, 16, dx=-4, c=AIR, rows=3, gap=24) + gnd(168, 0, top=WAT)
      + L(['M60 168 l0 16 M64 168 l0 10 M140 168 l0 20 M146 168 l0 12 M220 168 l0 14'], AIR, 1.4))
def f_highpressure(i):
    return (sun(144, 90, 24) + L(['M144 90 m-70 0 a70 50 0 1 0 140 0 a70 50 0 1 0 -140 0', 'M144 90 m-110 0 a110 78 0 1 0 220 0 a110 78 0 1 0 -220 0'], AIR, 1.3, dash='6 6') + gnd(186))
def f_permafrost(i):
    return (gnd(120, 0, top=AIR) + L(['M0 150 H288 M0 176 H288 M0 200 H288'], AIR, 1.2, shadow=False, dash='12 8')
      + flakes([(60, 60, 7), (150, 44, 6), (230, 70, 8)]) + L([crack(100, 120, 30, 4, 4), crack(200, 120, 26, 4, 4)], AIR, 1.2))
def f_thunderstorm(i):
    return (clouds((0, 44, 6, 24), c=LOW) + GLOW([bolt(150, 60, 170, 5, 14)], i) + rain(10, 278, 70, 20, 12, rows=3, gap=30, w=1.2) + gnd(176))
def f_heatshimmer(i):
    return (gnd(150) + L(heat([60, 100, 140, 180, 220], 60, 140), AIR, 1.2) + L(['M90 150 Q144 120 198 150'], MID, 1.3, dash='4 5')
      + L(['M90 170 Q144 196 198 170'], MID, 1.3, dash='4 5'))
def f_lightning(i):
    return (clouds((20, 40, 5, 22), c=LOW) + GLOW([bolt(170, 54, 168, 6, 12)], i) + gnd(170) + rtrees([(170, 168, 16)]) + EM(['M160 156 q10 -10 20 0'], i, 1.6))
def f_scorch(i):
    return (sun(220, 50, 22, True, c=EMB) + gnd(160) + L(['M30 170 Q90 150 150 168 Q210 186 270 166'], EMB, 1.4, dash='3 6')
      + L(['M60 160 l6 -18 M120 164 l-4 -16 M200 172 l6 -14'], EARTHC, 1.4))
def f_hail(i):
    return (clouds((10, 44, 6, 22), c=LOW) + DOTS([(x, y, 3) for x, y in [(40, 80), (90, 110), (140, 76), (190, 120), (240, 90), (70, 140), (170, 150), (220, 160)]], AIR)
      + L(['M40 80 l-4 -12 M140 76 l-4 -12 M240 90 l-4 -12'], AIR, 1, shadow=False) + gnd(178))
def f_thaw_new(i): return ''
def f_whirlwind(i):
    return (gnd(184) + L(funnel(110, 40, 180, 40, 6, lean=10), AIR, 1.4) + L(funnel(200, 70, 182, 30, 5, lean=-8), AIR, 1.3))
def f_squall(i):
    return (clouds((0, 40, 6, 24), c=LOW) + L([windp(20, 90, 160), windp(80, 120, 180)], AIR, 1.8) + rain(20, 270, 60, 24, 10, dx=-16, rows=2, gap=40)
      + gnd(170) + rtrees([(220, 168, 14)]))
def f_waterspout(i):
    return (F(['M0 170 L288 170 L288 230 L0 230 Z'], DEEP) + seaband(170) + L(funnel(144, 40, 168, 36, 8, lean=6), WAT, 1.5) + clouds((60, 36, 4, 22), c=LOW))
def f_landslide(i):
    return (L(['M0 30 Q80 60 140 130 Q200 180 288 186'], HI, 1.8) + F(['M0 30 Q80 60 140 130 Q200 180 288 186 L288 230 L0 230 Z'])
      + rocks([(120, 120, 12), (160, 150, 10), (196, 170, 14), (90, 96, 8)]) + L(['M80 70 Q120 110 150 140'], EARTHC, 1.3, dash='3 5'))
def f_bramble(i):
    return (gnd(178) + L([vines(40, 178, 120), vines(90, 178, 140), vines(150, 178, 130), vines(210, 178, 140), vines(256, 178, 110)], MID, 1.5)
      + L(['M60 120 l6 -6 M120 100 l6 -6 M180 110 l6 -6 M230 120 l6 -6'], EARTHC, 1.3))
def f_cavein(i):
    return (F(['M0 0 L288 0 L288 40 Q144 70 0 40 Z'], '#232622') + L(['M0 40 Q144 70 0 40', 'M0 40 Q144 70 288 40'], HI, 1.6)
      + rocks([(110, 120, 14), (160, 150, 12), (140, 96, 9)]) + gnd(180) + L(['M110 100 l0 -30 M160 128 l0 -40'], MID, 1.1, dash='3 5'))
# rare
def f_typhoon(i):
    return (L([swirl(144, 100, 110, 3.0)], AIR, 1.7) + F(['M0 190 L288 190 L288 230 L0 230 Z'], DEEP) + seaband(190) + rocks([(60, 70, 8), (230, 140, 9)]))
def f_firestorm(i):
    return (gnd(176) + flames(i, [(40, 176, 60), (90, 176, 100), (144, 176, 130), (198, 176, 96), (248, 176, 70)], 2.2) + L([swirl(144, 70, 60, 1.6)], EMB, 1.2))
def f_monsoon(i):
    return (clouds((-10, 34, 7, 24), (60, 60, 6, 22), c=LOW) + rain(0, 288, 70, 34, 24, dx=-6, rows=4, gap=28, w=1.5) + F(['M0 186 L288 186 L288 230 L0 230 Z'], DEEP) + seaband(186))
def f_drought(i):
    return (sun(144, 56, 30, True, c=EMB) + gnd(150) + L([crack(60, 160, 40, 4), crack(144, 156, 50, 5), crack(220, 162, 40, 4), 'M60 176 L100 182 M144 186 L190 180'], EARTHC, 1.4)
      + L([ell(144, 196, 50, 8)], WAT, 1.2, dash='3 6'))
def f_wildfire(i):
    return (trees([(40, 170, 1.2), (80, 170, 1.4), (120, 170, 1.3), (160, 170, 1.5), (200, 170, 1.3), (240, 170, 1.4)]) + gnd(170)
      + flames(i, [(60, 170, 70), (120, 170, 100), (180, 170, 90), (240, 170, 70)], 2.2) + L([steamp(120, 70, 60), steamp(200, 74, 60)], MID, 1.3))
def f_flashflood(i):
    return (L(['M0 60 L60 80 L120 70'], LOW, 1.2, shadow=False) + F(['M0 120 Q80 100 160 130 Q220 150 288 140 L288 230 L0 230 Z'], DEEP)
      + L(['M0 120 Q80 100 160 130 Q220 150 288 140'], WAT, 2.2) + L([curl(200, 140, 0.7)], WAT, 1.8) + flames(i, [(80, 200, 18)]) + L([steamp(80, 182, 40)], MID, 1.2))
def f_whiteout(i):
    return (fogbands([50, 76, 102, 128, 154], c=AIR) + flakes([(40, 60, 6), (110, 90, 7), (180, 64, 6), (240, 110, 8), (80, 140, 6), (200, 150, 6)]) + gnd(184, 0, top=AIR))
def f_tsunami(i):
    return (F(['M0 150 L288 150 L288 230 L0 230 Z'], DEEP) + L([curl(150, 150, 1.4)], WAT, 2.4) + L(['M0 150 Q60 146 90 150'], WAT, 1.8)
      + L(['M240 190 l0 -40 l14 0 l0 40'], HI, 1.4) + seaband(196, c=LOW, w=1.2))
def f_tornado(i):
    return (clouds((20, 30, 6, 24), c=LOW) + L(funnel(150, 46, 184, 60, 6, n=9, lean=-20), AIR, 1.5) + gnd(186) + rocks([(70, 110, 8), (220, 90, 7)]))
def f_hurricane(i):
    return (L([swirl(144, 104, 120, 3.4)], AIR, 1.6) + L(['M144 104 m-8 0 a8 7 0 1 0 16 0 a8 7 0 1 0 -16 0'], HI, 1.6) + rtrees([(40, 196, 12), (250, 198, 14)]) + gnd(200))
def f_galeforce(i):
    return (L([windp(0, 50, 170), windp(60, 80, 200), windp(0, 110, 190), windp(80, 140, 190)], AIR, 1.9) + rocks([(200, 66, 9), (240, 108, 8), (150, 126, 10)]) + gnd(180))
def f_eruption(i):
    return (mountains([(144, 200, 210, 120)]) + flames(i, [(144, 84, 60)]) + L([steamp(130, 30, 30), steamp(160, 34, 30)], MID, 1.3)
      + EM(['M144 90 L130 130 L140 160 L126 196'], i, 2) + DOTS([(90, 50, 3), (200, 40, 3), (230, 70, 2)], EMB, i))
def f_mudflow(i):
    return (L(['M0 40 Q100 90 150 150 Q190 196 288 200'], HI, 1.8) + F(['M0 40 Q100 90 150 150 Q190 196 288 200 L288 230 L0 230 Z'], '#2E2A22')
      + L(['M40 80 Q110 120 150 168 M70 70 Q130 116 170 170'], EARTHC, 1.5) + rtrees([(200, 184, 12)]))
def f_earthquake(i):
    return (gnd(130) + L([crack(100, 130, 90, 8, 12), crack(200, 130, 90, 8, 10)], HI, 2) + L(['M20 120 l-6 -10 M270 118 l6 -10 M150 120 l0 -10'], MID, 1.3)
      + rtrees([(60, 126, 12), (150, 124, 14), (250, 126, 12)]))
def f_avalanche(i):
    return (mountains([(160, 190, 300, 160)], c=AIR) + L(['M60 120 Q110 150 150 190', 'M90 96 Q130 140 170 190', 'M120 70 Q150 120 190 190'], AIR, 1.4)
      + flakes([(100, 120, 6), (140, 150, 6), (170, 120, 5)]))
def f_uplift(i):
    return (gnd(176) + L(['M80 176 L100 120 L144 100 L188 120 L208 176'], HI, 1.8) + dome(144, 120, 100, c=AIR, dash='6 6') + arrow(144, 196, 144, 130, bend=0))
def f_equinox(i):
    return (L(['M144 106 m-40 0 a40 40 0 1 0 80 0 a40 40 0 1 0 -80 0'], HI, 1.6) + F(['M144 66 A40 40 0 0 1 144 146 Z'], '#3A3E39')
      + L(['M0 106 H288'], LOW, 1.2, shadow=False) + gnd(186))
def f_blizzard(i):
    return (L([windp(0, 60, 170), windp(70, 96, 190)], AIR, 1.5) + flakes([(x, y, 5) for x, y in [(30, 80), (70, 120), (120, 70), (160, 130), (210, 90), (250, 140), (100, 150), (200, 160)]])
      + gnd(184, 0, top=AIR))
# pinnacle and 101
def f_solarflare(i):
    return (L(['M144 110 m-46 0 a46 46 0 1 0 92 0 a46 46 0 1 0 -92 0'], EMB, 2) + EM(['M190 90 Q250 40 270 90', 'M98 120 Q30 170 20 110', 'M150 64 Q170 10 210 30'], i, 2)
      + DOTS([(60, 40, 2), (240, 170, 2), (30, 180, 1.6)], EMB, i))
def f_greatuplift(i):
    return (gnd(186) + L(['M30 186 L70 120 L110 140 L144 70 L180 130 L216 110 L258 186'], HI, 2) + dome(144, 186, 140, c=AIR) + dome(144, 186, 120, c=AIR, dash='6 6'))
def f_worldquake(i):
    pieces = ['M34 70 L118 54 L134 96 L112 124 L62 142 L28 112 Z', 'M146 48 L236 62 L254 104 L204 116 L152 98 Z',
              'M128 134 L200 124 L252 118 L264 164 L204 190 L122 180 Z', 'M36 160 L100 140 L110 184 L56 196 Z']
    return (F(pieces, '#2B2F2B') + L(pieces, HI, 1.8)
      + arrow(86, 96, 58, 82, bend=0) + arrow(202, 86, 230, 72, bend=0) + arrow(198, 158, 224, 174, bend=0) + arrow(74, 172, 52, 186, bend=0))
def f_jetstream(i):
    return (L(['M0 80 C60 40 120 120 180 70 S260 40 288 60', 'M0 100 C60 60 120 140 180 90 S260 60 288 80', 'M0 120 C60 80 120 160 180 110 S260 80 288 100'], AIR, 1.8)
      + rocks([(60, 150, 8), (144, 166, 9), (230, 150, 8)]) + gnd(196))
def f_unmaking(i):
    return (L(['M144 107 m-70 0 a70 70 0 1 0 140 0 a70 70 0 1 0 -140 0'], HI, 1.4, dash='3 7')
      + L([swirl(144, 107, 70, 2.8)], MID, 1.2) + F(['M144 107 m-16 0 a16 16 0 1 0 32 0 a16 16 0 1 0 -32 0'], SH) + L(['M144 107 m-16 0 a16 16 0 1 0 32 0 a16 16 0 1 0 -32 0'], HI, 1.6))
def f_deluge2(i): return ''

FORCE_ART = {
 'Smolder': f_smolder, 'Updraft': f_updraft, 'Flare-up': f_flareup, 'Spark': f_spark, 'Ember': f_ember, 'Kindling': f_kindling,
 'Shower': f_shower, 'Current': f_current, 'Low Tide': f_lowtide, 'Drizzle': f_drizzle, 'Rain': f_rain, 'Snowmelt': f_snowmelt, 'Freeze': f_freeze,
 'Breeze': f_breeze, 'Drift': f_drift, 'Crosswind': f_crosswind, 'Thermal': f_thermal, 'Downdraft': f_downdraft, 'Eddy': f_eddy,
 'Rockfall': f_rockfall, 'Dust': f_dust, 'Silt': f_silt, 'Dustfall': f_dustfall, 'Tangle': f_tangle, 'Shelter': f_shelter,
 'Sinkhole': f_sinkhole, 'Dust Devil': f_dustdevil, 'Vent': f_vent, 'Mire': f_mire, 'Riptide': f_riptide, 'Whirl': f_whirl,
 'Steam': f_steam, 'Dry Wind': f_drywind, 'Firebreak': f_firebreak, 'Drying Wind': f_dryingwind, 'Tremor': f_tremor, 'Windbreak': f_windbreak,
 'Scald': f_scald, 'Heatwave': f_heatwave, 'Lava Bomb': f_lavabomb, 'Flood': f_flood, 'Downpour': f_downpour, 'Sandstorm': f_sandstorm,
 'Ashfall': f_ashfall, 'Cloudburst': f_cloudburst, 'Dust Storm': f_dust_storm, 'Heat Dome': f_heatdome, 'Ice Storm': f_icestorm,
 'High Pressure': f_highpressure, 'Permafrost': f_permafrost, 'Thunderstorm': f_thunderstorm, 'Heat Shimmer': f_heatshimmer,
 'Lightning': f_lightning, 'Scorch': f_scorch, 'Hail': f_hail, 'Whirlwind': f_whirlwind, 'Squall': f_squall, 'Waterspout': f_waterspout,
 'Landslide': f_landslide, 'Bramble': f_bramble, 'Cave-in': f_cavein,
 'Typhoon': f_typhoon, 'Firestorm': f_firestorm, 'Monsoon': f_monsoon, 'Drought': f_drought, 'Wildfire': f_wildfire, 'Flash Flood': f_flashflood,
 'Whiteout': f_whiteout, 'Tsunami': f_tsunami, 'Tornado': f_tornado, 'Hurricane': f_hurricane, 'Gale Force': f_galeforce, 'Eruption': f_eruption,
 'Mudflow': f_mudflow, 'Earthquake': f_earthquake, 'Avalanche': f_avalanche, 'Uplift': f_uplift, 'Equinox': f_equinox, 'Blizzard': f_blizzard,
 'Solar Flare': f_solarflare, 'Great Uplift': f_greatuplift, 'World Quake': f_worldquake, 'Jet Stream': f_jetstream, 'Unmaking': f_unmaking,
}

# ---------- new permanence art (288 x 220) ----------
def p_icefloe(i):
    return (L(['M0 110 H288'], LOW, 1.2, shadow=False) + F(['M0 130 L288 130 L288 230 L0 230 Z'], DEEP) + seaband(130)
      + F(['M60 150 L90 132 L170 134 L210 150 L180 162 L80 162 Z'], '#3A4447') + L(['M60 150 L90 132 L170 134 L210 150 L180 162 L80 162 Z'], AIR, 1.8)
      + L(['M90 132 L100 150 L80 162 M170 134 L160 152 L180 162'], WAT, 1.2) + seaband(190, c=LOW, w=1.2))
def p_hotmud(i):
    bub = ' '.join(ell(x, y, r, r * 0.6) for x, y, r in [(90, 160, 8), (140, 172, 10), (196, 158, 7), (120, 190, 6), (220, 186, 8)])
    return (F(['M0 120 Q144 108 288 120 L288 230 L0 230 Z'], '#2E2A22') + L(['M0 120 Q144 108 288 120'], EARTHC, 1.8)
      + L([bub], EARTHC, 1.4) + L([steamp(140, 160, 90), steamp(196, 150, 70)], HI, 1.4) + EM(['M60 200 q10 -6 20 0'], i, 1.6))
def p_cindercone(i):
    return (back_hills() + F(['M60 190 L124 96 L164 96 L228 190 Z']) + L(['M60 190 L124 96 Q144 86 164 96 L228 190'], HI, 2)
      + L(['M100 150 Q144 140 188 150', 'M84 172 Q144 160 204 172'], MID, 1.3) + L([steamp(140, 92, 60)], MID, 1.3)
      + EM(['M132 100 q12 -6 24 0'], i, 1.6) + gnd(196, -4))
def p_skyisle(i):
    return (clouds((10, 170, 4, 18), (170, 186, 4, 16), c=LOW) + F(['M70 100 Q144 80 218 100 L190 130 L160 168 L144 186 L124 160 L96 132 Z'])
      + L(['M70 100 Q144 80 218 100 L190 130 L160 168 L144 186 L124 160 L96 132 Z'], HI, 1.8) + trees([(110, 98, 0.9), (168, 96, 0.8)])
      + L([birdsp(220, 50), birdsp(60, 60, 0.8)], MID, 1.3) + L(['M144 186 l0 14'], LOW, 1.2))
def p_lavacoast(i):
    return (L(['M0 90 L80 60 L150 80'], LOW, 1.3, shadow=False) + F(['M0 120 L150 80 L170 150 L0 160 Z']) + L(['M0 120 L150 80 L170 150'], HI, 1.8)
      + EM(['M40 128 L90 112 L130 120 L160 146'], i, 2) + F(['M150 150 L288 150 L288 230 L0 230 L0 170 Z'], DEEP) + seaband(160, n=10)
      + L([steamp(176, 150, 80), steamp(200, 152, 60)], HI, 1.4))
def p_massif(i):
    return (mountains([(144, 190, 300, 150), (60, 190, 120, 80), (240, 190, 120, 90)]) + L(['M110 90 L144 40 L178 90', 'M100 130 Q144 120 188 130'], MID, 1.4)
      + gnd(196, -4))
def p_cradle(i):
    return (L(['M20 120 Q144 30 268 120'], LOW, 1.3, shadow=False) + F(['M20 150 Q144 230 268 150 L268 150 Z']) + L(['M20 150 Q144 230 268 150'], HI, 1.8)
      + sun(144, 70, 16, False) + seaband(166, n=4, c=WAT) + EM(['M120 186 q8 -6 16 0'], i, 1.6) + rtrees([(90, 156, 10), (200, 156, 10)]) + L([windp(60, 110, 60)], AIR, 1.3))
def p_origin(i):
    return (L(['M144 110 m-80 0 a80 80 0 1 0 160 0 a80 80 0 1 0 -160 0'], HI, 1.4)
      + F(['M64 110 A80 80 0 0 1 224 110 Z'], '#2C3134') + L([wave(64, 130, 5, 20, 8)], WAT, 1.6)
      + EM(['M110 170 q8 -10 16 0 q8 -10 16 0'], i, 1.8) + L([windp(90, 72, 100)], AIR, 1.5) + L(['M64 110 H224'], EARTHC, 1.8))
NEW_PERM = {'Ice Floe': p_icefloe, 'Hot Mud': p_hotmud, 'Cinder Cone': p_cindercone, 'Sky Isle': p_skyisle, 'Lava Coast': p_lavacoast,
            'Massif': p_massif, 'Cradle': p_cradle, 'Origin': p_origin}

# ---------- meta glyphs (288 x 182), void colour ----------
VOIDC = '#B9A6D6'
def ring(cx, cy, r): return 'M%g %g m-%g 0 a%g %g 0 1 0 %g 0 a%g %g 0 1 0 -%g 0' % (cx, cy, r, r, r, 2 * r, r, r, 2 * r)
def mg(ds, w=1.6, dash=None): return L(ds, VOIDC, w, dash=dash)
META_ART = {
 'Echo': lambda i: mg([ring(144, 91, 14), ring(144, 91, 34), ring(144, 91, 56)], 1.4),
 'Ebb': lambda i: mg([wave(40, 100, 8, 34, 6), 'M60 130 H230'], 1.6) + mg(['M200 70 L150 70'], 1.4) + mg(['M158 62 L150 70 L158 78'], 1.4),
 'Verge': lambda i: mg(['M80 91 H200', 'M190 81 L204 91 L190 101', 'M80 121 H220', 'M210 111 L224 121 L210 131', 'M80 61 H180', 'M170 51 L184 61 L170 71']),
 'Horizon': lambda i: mg(['M30 100 H258', 'M144 100 m-40 0 a40 40 0 0 1 80 0']) + mg([ring(144, 86, 8)], 1.4),
 'Hollow': lambda i: mg([ring(144, 91, 46)], 2) + mg(['M144 91 m-6 0 a6 6 0 1 0 12 0 a6 6 0 1 0 -12 0'], 1.2),
 'Calm': lambda i: mg(['M40 91 H248', 'M70 111 H218', 'M100 71 H188'], 1.6),
 'Lull': lambda i: mg(['M160 50 A42 42 0 1 0 160 132 A32 32 0 1 1 160 50 Z'], 1.6) + mg(['M200 60 l4 -4 M210 80 l4 -4'], 1.2),
 'Gap': lambda i: mg([ring(144, 91, 60)], 1.2, dash='3 6') + F(['M144 91 m-30 0 a30 30 0 1 0 60 0 a30 30 0 1 0 -60 0'], SH) + mg([ring(144, 91, 30)], 2),
}

# ---------- more new permanence art ----------
def p_mudpots(i):
    pots = [(80, 170, 30, 9), (170, 160, 36, 10), (226, 192, 22, 7)]
    return (back_hills() + gnd(140, -6, top=EARTHC)
      + F([ell(*p) for p in pots], '#2E2A22') + L([ell(*p) for p in pots], EARTHC, 1.7)
      + L([ell(80, 170, 10, 3), ell(170, 160, 14, 4), ell(162, 156, 4, 1.5)], MID, 1.2)
      + L([steamp(80, 160, 80), steamp(176, 150, 100), steamp(226, 186, 60)], HI, 1.4))
def p_lavaflow(i):
    return (ridge(110) + gnd(130, -4)
      + F(['M150 130 Q130 160 150 186 Q170 210 140 230 L196 230 Q214 206 192 182 Q172 158 186 130 Z'], '#3A2620')
      + EM(['M150 130 Q130 160 150 186 Q170 210 140 230', 'M186 130 Q172 158 192 182 Q214 206 196 230'], i, 2)
      + EM(['M164 150 q8 6 4 14 M172 196 q-6 8 2 14'], i, 1.4) + rocks([(70, 170, 14), (250, 190, 12)])
      + L([steamp(168, 128, 70)], MID, 1.3))
def p_redcanyon(i):
    return (sun(222, 46, 16, True)
      + F(['M0 70 L90 70 L96 90 L110 96 L118 230 L0 230 Z', 'M288 84 L200 84 L194 104 L180 110 L172 230 L288 230 Z'])
      + L(['M0 70 L90 70 L96 90 L110 96 L118 230', 'M288 84 L200 84 L194 104 L180 110 L172 230'], HI, 1.9)
      + L(['M0 120 L104 120 M0 160 L112 160 M288 136 L186 136 M288 178 L178 178'], EARTHC, 1.4)
      + L(['M118 230 Q144 206 172 230'], WAT, 1.4) + L([birdsp(140, 60)], MID, 1.3))
def p_lavaplain(i):
    return (ridge(86) + F(['M0 108 Q144 98 288 108 L288 230 L0 230 Z']) + L(['M0 108 Q144 98 288 108'], HI, 1.8)
      + EM(['M20 140 L70 132 L96 150 L150 140 L196 156 L260 146', 'M40 188 L96 178 L130 196 L190 186 L250 200', 'M96 150 L110 178 M196 156 L190 186'], i, 1.8)
      + L(['M30 120 H80 M180 122 H250 M120 168 H160'], MID, 1.2, shadow=False) + rocks([(240, 128, 8), (60, 166, 7)]))
NEW_PERM.update({'Mud Pots': p_mudpots, 'Lava Flow': p_lavaflow, 'Red Canyon': p_redcanyon, 'Lava Plain': p_lavaplain})

def f_undertow(i):
    return (F(['M0 90 L288 90 L288 230 L0 230 Z'], DEEP) + seaband(90) + seaband(120, c=LOW, w=1.2)
      + L(['M220 160 Q150 200 60 150', 'M230 186 Q150 220 70 180'], WAT, 1.7) + L(['M70 142 L58 150 L68 160', 'M80 172 L68 180 L78 190'], WAT, 1.7)
      + rocks([(200, 150, 10), (236, 176, 8)]))
FORCE_ART['Undertow'] = f_undertow

# ---------- second round: richer versions of the thinnest forces ----------
def twister(cx, top, bot, wt, wb, lean=0, bands=6, c=HI, band_c=MID, fillc=FILL):
    n = 24; L_, R_ = [], []
    for k in range(n + 1):
        t = k / n; y = top + (bot - top) * t
        w = wb + (wt - wb) * (1 - t) ** 1.7; x = cx + lean * t * t
        L_.append((x - w, y)); R_.append((x + w, y))
    pl = lambda pts: 'M' + ' L'.join('%.1f %.1f' % p for p in pts)
    body = pl(L_) + ' L' + ' L'.join('%.1f %.1f' % p for p in reversed(R_)) + ' Z'
    bl = []
    for k in range(1, bands + 1):  # slanted wraps, so the funnel reads as turning
        j = int(n * (k - 0.6) / (bands + 0.4)); j2 = min(n, j + 2)
        (xl, y), (xr, y2) = L_[j], R_[j2]
        bl.append('M%.1f %.1f Q%.1f %.1f %.1f %.1f' % (xl, y, (xl + xr) / 2, (y + y2) / 2 + (xr - xl) * 0.22, xr, y2))
    return F([body], fillc) + L([pl(L_), pl(R_)], c, 1.7) + L(bl, band_c, 1.2)

def f_dustdevil(i):
    return (hills(110) + gnd(176, -4, top=EARTHC) + twister(150, 60, 172, 34, 5, lean=-10, band_c=EARTHC)
      + DOTS([(110, 90, 1.6), (186, 108, 1.4), (124, 136, 1.4), (178, 150, 1.6), (96, 160, 1.2), (200, 166, 1.2)], EARTHC)
      + L(['M120 186 q14 -4 28 0 M170 190 q10 -3 20 0'], EARTHC, 1.2, shadow=False))
def f_whirlwind(i):
    return (hills(112) + gnd(180) + twister(92, 46, 176, 32, 4, lean=8, bands=5) + twister(206, 70, 178, 26, 4, lean=-6, bands=4)
      + L([windp(20, 70, 50), windp(236, 46, 46)], AIR, 1.3) + rocks([(150, 182, 8)]))
def f_waterspout(i):
    return (clouds((40, 34, 5, 24), c=LOW) + F(['M0 166 L288 166 L288 230 L0 230 Z'], DEEP) + seaband(166)
      + twister(150, 40, 164, 30, 6, lean=8, bands=6, c=WAT, band_c=AIR, fillc='#253033')
      + L([ell(158, 168, 26, 5)], AIR, 1.4) + L(['M120 168 q-10 -14 -4 -26 M196 168 q10 -14 4 -26'], WAT, 1.3) + seaband(196, c=LOW, w=1.2))
def f_tornado(i):
    return (clouds((-10, 30, 7, 24), c=LOW) + L(['M0 40 Q144 54 288 40'], LOW, 1.3, shadow=False) + hills(150)
      + twister(146, 46, 182, 56, 7, lean=-16, bands=8) + gnd(184, -2)
      + rocks([(60, 104, 8), (226, 88, 7), (204, 128, 6)]) + L(['M50 112 l-10 4 M216 96 l12 -2'], MID, 1.2)
      + rtrees([(250, 184, 12)]))
def f_updraft(i):
    dune = 'M0 178 Q60 150 130 168 Q200 186 288 160'
    return (sun(228, 176, 22, False) + F([dune + ' L288 230 L0 230 Z']) + L([dune], HI, 1.8)
      + L(['M30 196 q20 -6 40 0 M150 200 q20 -6 40 0'], MID, 1.2, shadow=False)
      + arrow(70, 160, 96, 70, bend=0) + arrow(140, 164, 150, 50, bend=-10) + arrow(212, 150, 196, 76, bend=10)
      + L(['M62 120 q8 -4 4 -12 M150 104 q-8 -6 -2 -14 M204 116 q8 -4 4 -12'], AIR, 1.2, shadow=False)
      + L([birdsp(118, 34, 1.4), birdsp(186, 46, 0.9)], HI, 1.5))
def f_ember(i):
    return (hills(112) + gnd(164, -4) + F([rock(144, 170, 30)]) + L([rock(144, 170, 30)], HI, 1.8)
      + L(['M128 158 l10 -8 M150 150 l8 6'], MID, 1.2) + EM(['M140 140 q4 -10 8 0 q-4 4 -8 0'], i, 1.8)
      + L([steamp(144, 134, 76)], MID, 1.3)
      + DOTS([(170, 110, 1.8), (184, 92, 1.4), (120, 100, 1.2), (196, 120, 1.2)], EMB, i)
      + L(['M40 186 H90 M200 190 H250'], MID, 1.2, shadow=False))
def f_freeze(i):
    return (hills(96) + gnd(120, -2) + F([ell(144, 160, 116, 30)], '#2C3538') + L([ell(144, 160, 116, 30)], AIR, 1.8)
      + L(['M60 150 L96 160 L130 152 L170 166 L210 156', 'M96 160 L100 182 M170 166 L176 186', 'M130 152 L136 136'], AIR, 1.2)
      + L(['M30 132 l2 -34 M38 132 l-2 -28 M46 132 l4 -36 M244 128 l2 -30 M252 128 l-3 -24'], MID, 1.4)
      + L(['M28 110 v8 M44 108 v10 M250 108 v8'], AIR, 1.2) + flakes([(90, 44, 7), (170, 30, 6), (230, 56, 6), (124, 76, 5)]))
def f_breeze(i):
    return (hills(108) + gnd(168, -4) + lakeshape(110, 186, 70, 12)
      + L(['M60 180 q30 -30 60 -40 t60 -50', 'M100 184 q30 -30 70 -36 t50 -52', 'M140 182 q30 -24 60 -26 t40 -46'], AIR, 1.4)
      + L(['M226 54 q10 -8 4 -16 M234 86 q12 -6 8 -16'], AIR, 1.3)
      + L(['M210 168 q6 -16 18 -22 M222 168 q4 -14 14 -20 M234 168 q4 -12 12 -16'], MID, 1.3))
def f_drift(i):
    hl = 'M0 190 Q40 120 100 140 Q130 150 150 190 Z'; hr = 'M150 190 Q190 110 250 124 Q280 132 288 150 L288 190 Z'
    return (F([hl, hr]) + L(['M0 190 Q40 120 100 140 Q130 150 150 190', 'M150 190 Q190 110 250 124 Q280 132 288 150'], HI, 1.8)
      + L(['M0 190 H288'], HI, 1.6) + L([cloudp(118, 70, 3, 16)], HI, 1.7)
      + L(['M52 112 Q80 70 112 72'], MID, 1.3, dash='4 6') + arrow(176, 66, 214, 98, bend=-14, c=MID, w=1.3)
      + trees([(60, 132, 0.6), (232, 120, 0.6)]))
def f_dust(i):
    return (ridge(112) + L(['M200 60 m-20 0 a20 20 0 1 0 40 0 a20 20 0 1 0 -40 0'], MID, 1.3, dash='4 4')
      + F(['M0 120 Q80 100 160 116 Q230 128 288 112 L288 150 L0 150 Z'], '#34302A') + gnd(168, -4)
      + L([windp(10, 132, 110), windp(140, 146, 130)], EARTHC, 1.4)
      + DOTS([(x, y, 1.4) for x, y in [(30, 96), (60, 110), (96, 92), (130, 108), (170, 90), (232, 100), (262, 86), (84, 140), (196, 136), (240, 150)]], EARTHC))
def f_tangle(i):
    return (gnd(176) + rocks([(70, 176, 22), (150, 176, 30), (230, 176, 20)])
      + L(['M20 176 C50 120 90 200 120 140 S170 120 190 160 S250 130 270 176', 'M40 176 C70 140 110 170 140 130 S200 150 230 140'], MID, 1.6)
      + L([ell(92, 150, 5, 3), ell(168, 128, 5, 3), ell(214, 150, 5, 3), ell(56, 140, 4, 2.4)], HI, 1.2)
      + hills(110))
def f_bramble(i):
    arcs = ['M20 180 Q60 80 110 180', 'M70 180 Q120 60 170 180', 'M130 180 Q180 90 230 180', 'M190 180 Q236 100 276 180']
    th = []
    for x, y in [(44, 132), (60, 116), (96, 118), (110, 104), (140, 110), (156, 124), (168, 118), (196, 126), (210, 134), (232, 130), (250, 140)]:
        th.append('M%d %d l5 -4' % (x, y))
    return (hills(100) + gnd(180) + L(arcs, HI, 1.6) + L(th, MID, 1.2) + DOTS([(84, 140, 2.4), (150, 100, 2.4), (220, 150, 2.4)], EMB))
def f_cavein(i):
    return (F(['M0 0 H288 V214 H0 Z'], '#202320') + F(['M40 214 Q40 40 144 36 Q248 40 248 214 Z'], '#2D312D')
      + L(['M40 214 Q40 40 144 36 Q248 40 248 214'], HI, 1.8) + L([crack(110, 44, 40, 4, 6), crack(178, 46, 34, 4, 5)], HI, 1.3)
      + rocks([(130, 106, 12), (166, 136, 10), (110, 156, 8)]) + L(['M130 84 l0 -14 M166 118 l0 -16'], MID, 1.1, dash='3 4')
      + L(['M60 196 Q144 180 228 196'], MID, 1.4) + rocks([(90, 198, 10), (200, 200, 12), (150, 196, 8)])
      + DOTS([(120, 180, 1.2), (176, 176, 1.2), (150, 166, 1)], MID))
def f_icestorm(i):
    return (clouds((10, 34, 5, 22), c=LOW) + rain(20, 270, 50, 14, 14, dx=-5, c=AIR, rows=2, gap=24, w=1.2) + gnd(176, -2, top=AIR)
      + rtrees([(80, 176, 22), (200, 176, 26)]) + L(['M62 134 v8 M72 130 v10 M88 132 v7 M98 136 v6 M180 124 v9 M192 120 v11 M208 122 v8 M222 128 v7'], AIR, 1.3)
      + L(['M40 190 H120 M170 194 H260'], AIR, 1.2, shadow=False))
def f_vent(i):
    m = 'M60 180 Q144 120 228 180 Z'
    return (hills(110) + F([m]) + L(['M60 180 Q144 120 228 180'], HI, 1.8) + L(['M144 152 L138 166 L146 180'], SH, 2.2)
      + L(['M144 152 L138 166 L146 180'], EMB, 1.2) + L([steamp(144, 146, 120), steamp(158, 146, 96), steamp(130, 146, 84)], HI, 1.5)
      + gnd(182, 0) + L(['M30 196 H90 M200 198 H262'], MID, 1.2, shadow=False))
def f_rockfall(i):
    cl = 'M0 20 L60 30 L90 90 L110 170 L0 170 Z'
    return (hills(130) + F([cl]) + L(['M0 20 L60 30 L90 90 L110 170'], HI, 1.8) + L(['M0 70 L80 70 M0 110 L96 112 M0 146 L104 146'], MID, 1.2)
      + gnd(170, -2) + rocks([(140, 80, 12), (170, 120, 10), (200, 150, 14)])
      + L(['M124 70 l-12 -8 M156 112 l-12 -6 M186 142 l-12 -6'], MID, 1.2, shadow=False) + rocks([(124, 172, 9), (236, 172, 11), (210, 176, 6)]))
def f_landslide(i):
    s = 'M0 50 Q80 60 130 120 Q170 170 288 180 L288 230 L0 230 Z'
    return (L(['M0 30 Q120 20 288 60'], LOW, 1.3, shadow=False) + F([s]) + L(['M0 50 Q80 60 130 120 Q170 170 288 180'], HI, 1.8)
      + L(['M40 52 Q70 80 80 110', 'M80 110 Q120 130 150 150'], MID, 1.3, dash='5 4')
      + rocks([(150, 140, 12), (186, 164, 10), (220, 176, 14), (118, 120, 8)]) + trees([(70, 92, 0.8), (100, 104, 0.7)])
      + L(['M196 150 l-10 -6 M232 162 l-10 -6'], MID, 1.2, shadow=False))
def f_steam(i):
    pools = [(70, 180, 30, 7), (150, 186, 36, 8), (230, 178, 28, 7)]
    return (fogbands([70, 92, 114], c=MID) + gnd(176, -2) + F([ell(*p) for p in pools], DEEP) + L([ell(*p) for p in pools], WAT, 1.5)
      + L([steamp(70, 174, 110), steamp(150, 180, 130), steamp(230, 172, 106), steamp(110, 182, 80), steamp(190, 180, 90)], HI, 1.4))
def f_kindling(i):
    return (hills(110) + gnd(178, -2) + L(['M100 178 L136 136 M124 178 L148 132 M176 178 L140 134 M192 178 L152 138 M112 178 L180 170'], EARTHC, 2.2)
      + flames(i, [(146, 150, 56, 30), (128, 158, 32), (164, 158, 34)], 2) + L([steamp(146, 92, 60)], MID, 1.3)
      + DOTS([(120, 100, 1.6), (176, 86, 1.4), (190, 112, 1.2)], EMB, i))
def f_spark(i):
    tufts = ' '.join('M%d 176 l-4 -14 M%d 176 l2 -18 M%d 176 l7 -12' % (x, x, x) for x in (40, 100, 214, 250))
    return (hills(112) + gnd(176, -2) + L([tufts], MID, 1.3)
      + rocks([(150, 176, 20)]) + L(['M190 70 l12 -16 M190 70 l18 2 M190 70 l6 18 M190 70 l-14 -8 M190 70 l-12 14'], EMB, 1.8)
      + GLOW(['M190 70 m-3 0 a3 3 0 1 0 6 0 a3 3 0 1 0 -6 0'], i, EMB) + EM(['M184 80 Q150 120 112 162'], i, 1.3)
      + flames(i, [(108, 176, 22)], 1.8) + L([windp(30, 110, 70)], AIR, 1.3))
FORCE_ART.update({'Dust Devil': f_dustdevil, 'Whirlwind': f_whirlwind, 'Waterspout': f_waterspout, 'Tornado': f_tornado,
                  'Updraft': f_updraft, 'Ember': f_ember, 'Freeze': f_freeze, 'Breeze': f_breeze, 'Drift': f_drift, 'Dust': f_dust,
                  'Tangle': f_tangle, 'Bramble': f_bramble, 'Cave-in': f_cavein, 'Ice Storm': f_icestorm, 'Vent': f_vent,
                  'Rockfall': f_rockfall, 'Landslide': f_landslide, 'Steam': f_steam, 'Kindling': f_kindling, 'Spark': f_spark})
