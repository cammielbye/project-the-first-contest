import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import *


# ---------- small drawing helpers (panel is 288 x 280) ----------
def ell(cx, cy, rx, ry):
    return 'M%g %g a%g %g 0 1 0 %g 0 a%g %g 0 1 0 %g 0' % (cx - rx, cy, rx, ry, 2 * rx, rx, ry, -2 * rx)
def ground(y=200, c=-12):
    d = 'M0 %g Q144 %g 288 %g' % (y, y + c, y)
    return F([d + ' L288 280 L0 280 Z']) + L([d], HI, 1.8)
def back(*ds): return L(list(ds), LOW, 1.4, shadow=False)
def rockp(x, y, w, h):
    return 'M%g %g Q%g %g %g %g Q%g %g %g %g Z' % (x, y, x + w * 0.12, y - h, x + w * 0.5, y - h, x + w * 0.92, y - h * 0.92, x + w, y)
def rocks(*specs):
    ps = [rockp(*s) for s in specs]
    return F(ps) + L(ps, HI, 1.8)
def grass(*pts): return L([' '.join('M%g %g l3 -9 l3 9' % p for p in pts)], MID, 1.3)
def conifers(*specs): return L([tree(*s) for s in specs], HI, 1.5)
def roundtree(x, y, r):
    return 'M%g %g v%g M%g %g a%g %g 0 1 0 %g 0 a%g %g 0 1 0 %g 0' % (x, y, -r * 1.1, x - r, y - r * 1.9, r, r, 2 * r, r, r, -2 * r)
def roundtrees(*specs): return L([roundtree(*s) for s in specs], HI, 1.5)
def sunp(cx, cy, r, rays=True):
    d = ell(cx, cy, r, r)
    if rays:
        import math
        for k in range(8):
            a = k * math.pi / 4
            d += ' M%.1f %.1f L%.1f %.1f' % (cx + math.cos(a) * (r + 6), cy + math.sin(a) * (r + 6), cx + math.cos(a) * (r + 13), cy + math.sin(a) * (r + 13))
    return d
def cloudp(x, y, n, s=16): return 'M%g %g' % (x, y) + ''.join(' q%g %g %g 0' % (s, -s * 0.75, 2 * s) for _ in range(n))
def windp(x, y, ln): return 'M%g %g q%g -8 %g 0 t%g 0' % (x, y, ln / 4, ln / 2, ln / 2)
def birdsp(x, y, s=1): return 'M%g %g q%g %g %g 0 q%g %g %g 0' % (x, y, 6 * s, -5 * s, 12 * s, 6 * s, -5 * s, 12 * s)
def steamp(x, y, h): return 'M%g %g C%g %g %g %g %g %g C%g %g %g %g %g %g' % (x, y, x - 10, y - h * 0.3, x + 12, y - h * 0.5, x, y - h * 0.7, x - 8, y - h * 0.82, x + 6, y - h * 0.92, x, y - h)
def reeds(*pts):
    d = ''
    for x, y, h in pts:
        d += ' M%g %g v%g M%g %g a2.5 6 0 1 0 5 0 a2.5 6 0 1 0 -5 0' % (x, y, -h, x - 2.5, y - h - 2)
    return L([d.strip()], HI, 1.3)

# ---------- fire ----------
def a_emberbed(i):
    return (back(cloudp(30, 70, 3, 14))
      + ground(196, -6)
      + EM(['M70 214 q6 -10 12 0 q6 -12 12 0', 'M120 218 q7 -14 14 0 q7 -10 14 0 q6 -12 12 0', 'M190 212 q6 -10 12 0 q6 -9 12 0'], i, 2)
      + DOTS([(60, 230, 2), (84, 236, 1.6), (110, 232, 2.2), (136, 240, 1.8), (162, 230, 2), (186, 238, 1.6), (210, 228, 2), (232, 238, 1.6), (98, 248, 1.4), (150, 252, 1.6), (200, 250, 1.4)], EMB, i)
      + L([steamp(130, 196, 90), steamp(176, 192, 70)], MID, 1.4))
def a_flint(i):
    flint = 'M70 226 L92 150 L150 118 L214 140 L232 206 L190 238 L112 240 Z'
    return (ground(226, -4)
      + F([flint]) + L([flint], HI, 2)
      + L(['M110 168 Q126 150 150 146', 'M104 194 Q130 168 168 166', 'M118 222 Q150 196 200 192', 'M150 118 L160 180 L190 238'], MID, 1.3)
      + EM(['M236 96 l8 -18 M236 96 l18 -6 M236 96 l14 12 M236 96 l-4 16 M236 96 l-16 -6'], i, 2)
      + DOTS([(258, 72, 1.6), (264, 104, 1.4), (226, 70, 1.2)], EMB, i))
def a_obsidian(i):
    shards = ['M40 232 L64 136 L92 232 Z', 'M84 232 L122 96 L164 232 Z', 'M150 232 L196 120 L230 232 Z', 'M214 232 L246 168 L268 232 Z']
    return (back('M0 120 L60 88 L120 112 L180 80 L240 104 L288 92')
      + ground(232, 0) + F(shards, '#1E2020') + L(shards, HI, 1.8)
      + L(['M122 96 L134 170', 'M196 120 L204 176', 'M64 136 L70 190'], AIR, 1.6)
      + EM(['M110 214 L124 200 M176 216 L190 204'], i, 1.8))
def a_crater(i):
    return (back('M0 110 L70 84 L150 104 L230 80 L288 100')
      + ground(150, -4)
      + F([ell(144, 196, 108, 34)], '#1E2020') + L([ell(144, 196, 108, 34)], HI, 2)
      + L(['M60 196 Q144 226 228 196', 'M86 194 Q144 214 202 194'], MID, 1.4)
      + L(['M30 170 L12 160 M258 170 L276 160 M74 230 L56 252 M214 230 L232 252 M144 232 L144 262'], MID, 1.3)
      + DOTS([(144, 204, 2.4), (132, 208, 1.4), (156, 206, 1.6)], EMB, i))
def a_geyser(i):
    return (back('M0 130 L60 100 L120 124 L190 92 L288 128')
      + ground(214, -6) + rocks((96, 224, 96, 26))
      + L(['M144 200 C138 160 150 120 144 60', 'M136 200 C126 170 132 140 120 110', 'M152 200 C162 170 156 140 170 108'], WAT, 1.8)
      + L([steamp(144, 64, 50), steamp(118, 112, 40), steamp(172, 110, 40)], HI, 1.3)
      + DOTS([(126, 92, 1.8), (164, 86, 1.6), (110, 140, 1.4), (182, 138, 1.4)], WAT)
      + EM(['M112 226 l8 -6 M168 226 l8 -6'], i, 1.8))
def a_scrubland(i):
    shrubs = ' '.join('M%g %g l-6 -12 M%g %g l0 -16 M%g %g l6 -12 M%g %g l-10 -6 M%g %g l10 -6' % (x, y, x, y, x, y, x, y - 6, x, y - 6) for x, y in [(40, 214), (96, 226), (170, 218), (238, 230), (130, 246)])
    return (L([sunp(220, 74, 22)], HI, 1.5)
      + ground(196, -6) + L([shrubs], HI, 1.4)
      + L(['M20 250 L60 244 L80 256 M180 252 L214 246 L236 258 M110 262 L150 256'], MID, 1.2, shadow=False)
      + EM(['M60 206 l4 -6 M204 214 l4 -6'], i, 1.4))
def a_ashfield(i):
    return (back(cloudp(10, 60, 4, 18), cloudp(150, 86, 3, 16))
      + F(['M0 190 Q60 170 120 188 Q190 160 288 186 L288 280 L0 280 Z'])
      + L(['M0 190 Q60 170 120 188 Q190 160 288 186'], HI, 1.8)
      + L(['M10 220 Q80 204 150 222 Q220 200 288 218', 'M0 252 Q90 236 180 254 Q240 242 288 250'], MID, 1.3)
      + L(['M70 188 L68 140 M68 160 L56 150 M68 152 L80 140', 'M210 178 L212 120 M212 146 L224 132 M212 138 L200 128'], HI, 1.8)
      + DOTS([(40, 120, 1.4), (100, 100, 1.2), (150, 130, 1.4), (190, 90, 1.2), (250, 120, 1.4), (120, 160, 1.2), (240, 150, 1.2)], MID))
def a_lavafield(i):
    plates = ['M0 180 L60 170 L80 200 L30 214 L0 206 Z', 'M90 176 L160 168 L170 196 L110 210 Z', 'M180 172 L250 176 L270 204 L196 212 Z', 'M20 236 L90 226 L110 256 L40 266 Z', 'M130 230 L200 224 L224 254 L150 266 Z', 'M232 232 L288 230 L288 262 L246 266 Z']
    return (back('M0 120 L80 70 L120 96 L180 60 L288 116')
      + F(['M0 166 L288 166 L288 280 L0 280 Z'], '#1E2020') + F(plates) + L(plates, HI, 1.6)
      + EM(['M66 186 L84 206 L104 214 L120 222 L130 214', 'M168 200 L184 212 L230 222 L240 214', 'M30 222 L60 232 M110 262 L130 248', 'M224 248 L240 236'], i, 2.4))
def a_dune(i):
    return (L([sunp(70, 70, 20)], HI, 1.5)
      + F(['M0 210 Q70 150 140 176 Q210 120 288 170 L288 280 L0 280 Z'])
      + L(['M0 210 Q70 150 140 176 Q210 120 288 170'], HI, 2)
      + L(['M140 176 Q160 210 150 280', 'M226 140 Q240 180 230 240'], MID, 1.4)
      + L(['M20 236 q20 -6 40 0 t40 0', 'M170 220 q16 -5 32 0 t32 0', 'M40 260 q24 -6 48 0 t48 0 t48 0'], MID, 1.1, shadow=False))
def a_barrens(i):
    cells = ['M0 210 L60 206 L50 232 L0 236 Z', 'M60 206 L130 204 L136 234 L50 232 Z', 'M130 204 L210 206 L220 236 L136 234 Z', 'M210 206 L288 210 L288 238 L220 236 Z', 'M0 236 L50 232 L40 270 L0 274 Z', 'M50 232 L136 234 L130 276 L40 270 Z', 'M136 234 L220 236 L236 276 L130 276 Z', 'M220 236 L288 238 L288 278 L236 276 Z']
    return (L(['M0 200 H288'], HI, 1.6)
      + F(cells) + L(cells, MID, 1.3)
      + rocks((190, 200, 40, 26))
      + L(['M60 160 q-4 -8 0 -16 q4 -8 0 -16', 'M120 150 q-4 -8 0 -16 q4 -8 0 -16', 'M240 156 q-4 -8 0 -16 q4 -8 0 -16'], MID, 1.2, shadow=False)
      + L([sunp(144, 70, 16, False)], HI, 1.4))
def a_steamvent(i):
    return (back('M0 110 L90 70 L170 100 L288 76')
      + ground(196, -4) + rocks((30, 206, 70, 30), (200, 210, 64, 26))
      + EM(['M110 210 L124 222 L118 236 L136 248 L130 262', 'M160 206 L150 222 L164 236'], i, 2.2)
      + L([steamp(118, 200, 120), steamp(156, 196, 140), steamp(190, 204, 90)], HI, 1.5))
def a_magmapool(i):
    return (back('M0 100 L80 60 L160 90 L288 70')
      + ground(180, -4)
      + F([ell(144, 220, 98, 30)], '#3A2420')
      + EM([ell(144, 220, 98, 30), ell(144, 220, 62, 16)], i, 2)
      + rocks((30, 226, 50, 30), (210, 230, 56, 28), (120, 256, 50, 16))
      + EM([ell(120, 214, 5, 4), ell(170, 222, 6, 4), ell(150, 208, 3, 2)], i, 1.6))
def a_pumice(i):
    stone = 'M60 230 Q56 150 130 132 Q214 118 230 186 Q240 236 190 240 Q120 246 60 230 Z'
    holes = ' '.join(ell(x, y, r, r * 0.8) for x, y, r in [(110, 170, 6), (150, 152, 4), (180, 180, 7), (128, 204, 5), (196, 214, 4), (90, 214, 3), (160, 218, 3), (206, 166, 3)])
    return (back('M180 110 L220 60 L236 72 L260 110', 'M0 120 H288')
      + ground(232, 0) + F([stone]) + L([stone], HI, 2) + L([holes], MID, 1.3)
      + L([steamp(228, 60, 40)], LOW, 1.2, shadow=False))
def a_burnthollow(i):
    return (back(cloudp(40, 60, 3, 16))
      + F(['M0 170 Q80 170 110 210 Q144 240 178 210 Q208 170 288 170 L288 280 L0 280 Z'])
      + L(['M0 170 Q80 170 110 210 Q144 240 178 210 Q208 170 288 170'], HI, 1.8)
      + L(['M60 176 v-26 M56 160 l-8 -6 M90 192 v-18 M200 186 v-30 M204 168 l8 -8 M232 176 v-18 M130 222 v-12 M160 224 v-14'], HI, 2)
      + DOTS([(126, 232, 1.8), (150, 236, 1.6), (170, 230, 1.4), (96, 206, 1.4), (196, 204, 1.4)], EMB, i)
      + L([steamp(144, 216, 100)], MID, 1.3))

# ---------- water ----------
def a_stream(i):
    return (back('M0 110 L70 80 L140 104 L220 72 L288 100')
      + ground(120, 0)
      + F(['M130 120 L156 120 Q190 190 268 280 L40 280 Q130 190 130 120 Z'], DEEP)
      + L(['M130 120 Q130 190 40 280', 'M156 120 Q190 190 268 280'], WAT, 1.8)
      + L(['M138 150 q6 -3 12 0', 'M120 190 q10 -4 20 0 t20 0', 'M100 236 q14 -5 28 0 t28 0 t28 0'], WAT, 1.2, shadow=False)
      + rocks((30, 200, 40, 20), (226, 214, 44, 22))
      + grass((20, 250), (250, 254), (60, 150), (210, 160)))
def a_pond(i):
    pads = ' '.join(ell(x, y, 10, 4) for x, y in [(110, 214), (170, 224), (196, 206), (132, 236)])
    return (back(cloudp(150, 64, 3, 16))
      + ground(170, -4)
      + F([ell(144, 220, 116, 40)], DEEP) + L([ell(144, 220, 116, 40)], WAT, 1.8)
      + L([pads], HI, 1.3)
      + reeds((34, 210, 40), (46, 214, 52), (240, 206, 46), (254, 210, 36)))
def a_brook(i):
    pebbles = ' '.join(ell(x, y, rx, ry) for x, y, rx, ry in [(60, 210, 12, 6), (100, 228, 10, 5), (150, 214, 14, 6), (196, 232, 11, 5), (232, 212, 12, 6), (120, 252, 9, 4), (210, 256, 10, 4)])
    return (back('M0 96 Q144 70 288 96')
      + F(['M0 150 L120 150 L130 170 L288 170 L288 280 L0 280 Z'], DEEP)
      + L(['M0 150 L120 150 L130 170 L288 170'], HI, 1.8)
      + L(['M120 150 C124 156 126 162 130 170', 'M110 150 C116 158 116 164 120 172'], WAT, 1.6)
      + L([pebbles], MID, 1.4)
      + L([wave(0, 194, 4, 24, 12), wave(0, 240, 4, 24, 12)], WAT, 1.2, shadow=False))
def a_creek(i):
    return (back('M0 90 L80 60 L160 84 L288 64')
      + F(['M0 150 Q80 170 110 210 L178 210 Q208 170 288 150 L288 280 L0 280 Z'])
      + L(['M0 150 Q80 170 110 210', 'M178 210 Q208 170 288 150'], HI, 1.8)
      + F(['M110 210 L178 210 L198 280 L90 280 Z'], DEEP)
      + L([wave(96, 236, 4, 20, 5), wave(92, 262, 4, 20, 5)], WAT, 1.3, shadow=False)
      + L(['M60 196 L230 188', 'M60 204 L230 196'], HI, 1.8)
      + grass((30, 176), (250, 170), (70, 230), (220, 236)))
def a_cove(i):
    cl = ['M0 70 L60 80 L80 120 L60 170 L90 220 L60 280 L0 280 Z', 'M288 60 L230 74 L214 120 L236 170 L200 226 L230 280 L288 280 Z']
    return (F(cl) + L(['M0 70 L60 80 L80 120 L60 170 L90 220 L60 280', 'M288 60 L230 74 L214 120 L236 170 L200 226 L230 280'], HI, 1.8)
      + L(['M110 200 Q144 210 180 200', 'M100 230 Q144 242 190 230', 'M96 258 Q144 270 196 258'], WAT, 1.4)
      + L([wave(84, 120, 5, 24, 5)], WAT, 1.2, shadow=False)
      + L(['M90 40 H200'], LOW, 1.2, shadow=False))
def a_lagoon(i):
    return (L(['M0 100 H288'], LOW, 1.2, shadow=False)
      + L([wave(0, 120, 6, 32, 9)], WAT, 1.5)
      + F([ell(144, 196, 130, 56)], '#323631') + F([ell(144, 200, 104, 40)], DEEP)
      + L([ell(144, 196, 130, 56)], HI, 1.8) + L([ell(144, 200, 104, 40)], WAT, 1.6)
      + L(['M100 200 q22 -6 44 0 t44 0', 'M120 220 q12 -4 24 0 t24 0'], WAT, 1.1, shadow=False)
      + L(['M230 150 q-4 -22 4 -40 M234 110 q-14 -4 -20 6 M234 110 q14 -4 20 6'], HI, 1.4))
def a_bog(i):
    pools = ' '.join(ell(x, y, rx, ry) for x, y, rx, ry in [(70, 214, 34, 8), (180, 206, 40, 9), (120, 246, 46, 9), (240, 244, 30, 7)])
    return (back(windp(10, 120, 120), windp(150, 140, 120))
      + ground(184, -2) + F([pools], DEEP) + L([pools], WAT, 1.4)
      + grass((30, 196), (36, 200), (140, 200), (146, 204), (220, 222), (226, 226), (80, 236), (200, 262)))
def a_marsh(i):
    return (back('M0 120 Q144 100 288 120')
      + F(['M0 170 L288 170 L288 280 L0 280 Z'], DEEP) + L(['M0 170 H288'], WAT, 1.6)
      + L([wave(0, 214, 4, 24, 12), wave(10, 250, 4, 28, 10)], WAT, 1.2, shadow=False)
      + reeds((30, 200, 60), (44, 204, 74), (58, 198, 50), (110, 210, 64), (124, 206, 80), (190, 202, 58), (204, 208, 72), (250, 200, 62), (264, 206, 48)))
def a_swamp(i):
    trees = 'M60 230 C70 180 50 140 70 90 M70 90 C50 96 40 120 36 150 M70 90 C90 94 100 116 104 146 M210 236 C200 186 220 140 204 100 M204 100 C186 108 176 130 172 158 M204 100 C224 106 236 128 238 156'
    hang = 'M44 128 v26 M54 110 v34 M96 120 v30 M182 130 v28 M228 134 v26 M196 116 v30'
    return (F(['M0 220 L288 220 L288 280 L0 280 Z'], DEEP) + L(['M0 220 H288'], WAT, 1.6)
      + L([trees], HI, 2) + L([hang], MID, 1.2, shadow=False)
      + L(['M60 230 l-12 8 M60 230 l12 8 M210 236 l-12 8 M210 236 l14 8'], HI, 1.6)
      + L([wave(0, 250, 4, 30, 10)], WAT, 1.2, shadow=False))
def a_waterfall(i):
    cliff = ['M0 60 L110 60 L116 210 L0 210 Z', 'M178 60 L288 60 L288 210 L172 210 Z']
    return (F(cliff) + L(['M0 60 L110 60 L116 210', 'M288 60 L178 60 L172 210'], HI, 1.8)
      + L(['M116 62 V200', 'M128 62 V204', 'M140 62 V206', 'M152 62 V204', 'M164 62 V200'], WAT, 1.6)
      + F([ell(144, 230, 90, 20)], DEEP) + L([ell(144, 230, 90, 20)], WAT, 1.6)
      + L([cloudp(96, 210, 3, 16)], HI, 1.2, shadow=False)
      + L(['M20 100 H90 M20 150 H96 M196 110 H270 M190 160 H276'], MID, 1.2, shadow=False))
def a_mangrove(i):
    roots = 'M80 160 Q60 190 50 236 M80 160 Q74 200 70 238 M80 160 Q92 196 100 238 M80 160 Q104 186 120 236 M200 150 Q180 186 172 232 M200 150 Q198 196 196 236 M200 150 Q216 190 226 234 M200 150 Q232 180 248 230'
    return (F(['M0 214 L288 214 L288 280 L0 280 Z'], DEEP) + L(['M0 214 H288'], WAT, 1.6)
      + L([roots], HI, 1.6)
      + F(['M36 152 q-6 -26 22 -34 q10 -22 38 -14 q26 -6 30 18 q14 20 -10 32 q-30 10 -60 4 q-22 0 -20 -6 Z', 'M154 142 q-8 -28 22 -36 q12 -24 42 -14 q28 -4 30 20 q14 22 -12 32 q-32 10 -64 4 q-20 0 -18 -6 Z'])
      + L(['M36 152 q-6 -26 22 -34 q10 -22 38 -14 q26 -6 30 18 q14 20 -10 32 q-30 10 -60 4 q-22 0 -20 -6 Z', 'M154 142 q-8 -28 22 -36 q12 -24 42 -14 q28 -4 30 20 q14 22 -12 32 q-32 10 -64 4 q-20 0 -18 -6 Z'], HI, 1.8)
      + L([wave(0, 246, 4, 28, 11)], WAT, 1.2, shadow=False))
def a_snowfield(i):
    return (back('M0 110 L60 70 L110 98 L170 56 L230 94 L288 74')
      + F(['M0 170 Q90 140 170 162 Q230 150 288 166 L288 280 L0 280 Z'], '#3A403F')
      + L(['M0 170 Q90 140 170 162 Q230 150 288 166'], AIR, 2)
      + L(['M20 214 Q100 196 170 214 Q230 204 288 214', 'M0 250 Q120 232 220 252'], AIR, 1.2, shadow=False, op='0.7')
      + DOTS([(30, 40, 1.6), (70, 60, 1.4), (110, 34, 1.6), (150, 70, 1.4), (190, 44, 1.6), (230, 66, 1.4), (264, 30, 1.6), (50, 110, 1.4), (130, 120, 1.6), (210, 124, 1.4), (90, 140, 1.2), (250, 130, 1.2)], AIR))
def a_tidepool(i):
    pools = [ell(90, 206, 30, 9), ell(190, 224, 36, 10), ell(140, 252, 26, 7)]
    return (L([wave(0, 104, 6, 32, 9), wave(0, 130, 7, 40, 8)], WAT, 1.5)
      + F(['M0 160 Q60 150 120 166 Q200 150 288 162 L288 280 L0 280 Z'])
      + L(['M0 160 Q60 150 120 166 Q200 150 288 162'], HI, 1.8)
      + F(pools, DEEP) + L(pools, WAT, 1.5)
      + rocks((30, 240, 34, 20), (236, 254, 36, 22))
      + L(['M84 204 q6 -3 12 0 M184 222 q8 -3 16 0'], WAT, 1.1, shadow=False))
def a_floodplain(i):
    river = 'M0 190 C60 170 80 220 140 206 C200 192 190 160 240 168 C270 172 280 186 288 182'
    oxbow = ell(80, 244, 30, 10)
    return (back('M0 120 Q70 96 140 116 Q220 92 288 114')
      + ground(150, 0)
      + L([river], WAT, 2.2) + L([oxbow], WAT, 1.4)
      + grass((30, 230), (140, 250), (200, 230), (250, 262), (110, 176))
      + L(['M0 270 H288'], LOW, 1.1, shadow=False))

# ---------- air ----------
def a_spire(i):
    sp = 'M126 280 L132 140 L144 50 L156 140 L164 280 Z'
    return (L([windp(10, 70, 100), windp(180, 100, 90), windp(20, 140, 90), windp(190, 170, 80)], AIR, 1.5)
      + F([sp]) + L([sp[:-2]], HI, 2)
      + L(['M134 180 H160 M132 220 H162 M134 250 H160'], MID, 1.2, shadow=False)
      + L([birdsp(200, 50)], HI, 1.3)
      + back(cloudp(0, 250, 4, 16), cloudp(176, 256, 3, 16)))
def a_seastack(i):
    st = 'M110 220 L114 110 L130 92 L160 96 L170 120 L176 220 Z'
    return (L([wave(0, 220, 6, 32, 9), wave(0, 246, 7, 40, 8)], WAT, 1.5)
      + F([st]) + L([st[:-2]], HI, 2)
      + L(['M116 140 H170 M114 180 H174'], MID, 1.2, shadow=False)
      + L([windp(200, 80, 80), windp(10, 120, 80)], AIR, 1.5)
      + L([birdsp(40, 60), birdsp(210, 40, 0.8)], HI, 1.3))
def a_summit(i):
    m = 'M20 280 L120 70 L140 60 L160 72 L268 280 Z'
    return (F([m]) + L([m[:-2]], HI, 2)
      + L(['M120 70 L106 120 L124 108 L140 128 L156 110 L176 124 L160 72'], AIR, 1.6)
      + L(['M138 60 L136 44 L146 44 L144 60 M134 44 L140 36 L148 44'], HI, 1.4)
      + L([cloudp(0, 210, 4, 18), cloudp(150, 230, 4, 18)], AIR, 1.4, shadow=False, op='0.85')
      + L([windp(170, 40, 100), windp(10, 50, 90)], AIR, 1.4))
def a_cliff(i):
    c = 'M0 40 L170 40 L180 70 L162 110 L178 150 L160 200 L172 280 L0 280 Z'
    return (F([c]) + L(['M0 40 L170 40 L180 70 L162 110 L178 150 L160 200 L172 280'], HI, 2)
      + L(['M10 80 H150 M14 130 H150 M8 180 H140 M12 230 H150'], MID, 1.2, shadow=False)
      + L([cloudp(190, 240, 2, 22)], AIR, 1.4, shadow=False, op='0.85')
      + L([windp(196, 70, 80), windp(200, 120, 70), windp(192, 170, 80)], AIR, 1.5)
      + L(['M30 40 l5 -10 l5 10 M110 40 l4 -8 l4 8'], MID, 1.3))
def a_plateau(i):
    p = 'M20 280 L50 120 L238 116 L268 280 Z'
    return (F([p]) + L([p[:-2]], HI, 2)
      + L(['M50 120 L238 116'], AIR, 1.6)
      + L(['M46 150 L242 148 M40 190 L250 186 M32 236 L258 232'], MID, 1.2, shadow=False)
      + L([windp(30, 70, 100), windp(150, 90, 110), windp(60, 100, 80)], AIR, 1.5)
      + back(cloudp(0, 262, 2, 18), cloudp(232, 262, 1, 18)))
def a_ridge(i):
    r = 'M0 200 L40 170 L70 180 L110 130 L140 140 L180 110 L210 126 L250 100 L288 120 L288 280 L0 280 Z'
    return (back('M0 140 L50 110 L100 130 L160 90 L230 120 L288 96')
      + F([r]) + L([r.replace(' L288 280 L0 280 Z', '')], HI, 2)
      + L(['M110 130 L100 200 M180 110 L172 190 M250 100 L246 170'], MID, 1.3)
      + L([windp(10, 70, 90), windp(150, 54, 100), windp(60, 100, 80)], AIR, 1.5))
def a_peak(i):
    p = 'M30 280 L144 50 L258 280 Z'
    return (F([p]) + L([p[:-2]], HI, 2)
      + L(['M118 104 L130 96 L144 110 L158 96 L170 104'], AIR, 1.6)
      + L(['M144 50 Q190 40 230 52 Q262 60 288 54', 'M150 64 Q196 60 240 70'], AIR, 1.4, shadow=False, op='0.85')
      + L(['M144 110 L124 200 M144 110 L168 210'], MID, 1.3))
def a_pass(i):
    l, r = 'M0 280 L0 90 L60 70 L130 190 L140 280 Z', 'M288 280 L288 80 L230 66 L160 190 L150 280 Z'
    return (F([l, r]) + L(['M0 90 L60 70 L130 190 L140 280', 'M288 80 L230 66 L160 190 L150 280'], HI, 2)
      + L(['M145 280 Q140 240 146 214 Q152 196 144 186'], MID, 1.3, shadow=False, dash='4 5')
      + L(['M90 150 q28 -8 56 0 t56 0', 'M100 176 q22 -6 44 0 t44 0', 'M110 128 q24 -8 48 0 t48 0'], AIR, 1.6))
def a_bluff(i):
    b = 'M0 120 Q90 112 150 126 Q176 140 180 180 L184 220 L0 220 Z'
    return (F([b]) + L(['M0 120 Q90 112 150 126 Q176 140 180 180 L184 220'], HI, 2)
      + L([wave(170, 236, 4, 24, 5)], WAT, 1.3)
      + L(['M0 220 H288'], LOW, 1.2, shadow=False)
      + grass((20, 120), (60, 116), (110, 118))
      + L([windp(20, 70, 100), windp(160, 60, 100), windp(190, 100, 80)], AIR, 1.5))
def a_crag(i):
    c = 'M30 280 L40 200 L60 210 L74 140 L94 160 L110 90 L130 120 L150 70 L168 110 L190 96 L206 150 L230 140 L246 210 L262 280 Z'
    return (F([c]) + L([c[:-2]], HI, 2)
      + L(['M110 90 L104 160 M150 70 L146 150 M190 96 L196 170'], MID, 1.3)
      + L([birdsp(40, 60), birdsp(210, 40), birdsp(240, 76, 0.8)], HI, 1.3)
      + L([windp(170, 30, 90)], AIR, 1.4))
def a_moor(i):
    return (back(cloudp(0, 80, 5, 16), cloudp(100, 100, 5, 18))
      + F(['M0 170 Q70 150 140 168 Q210 146 288 166 L288 280 L0 280 Z'])
      + L(['M0 170 Q70 150 140 168 Q210 146 288 166'], HI, 1.8)
      + L([' '.join('M%g %g l6 -8 M%g %g l8 -6' % (x, y, x + 2, y) for x, y in [(30, 200), (70, 224), (120, 196), (160, 234), (210, 206), (250, 230), (100, 256), (200, 258)])], MID, 1.3)
      + L([windp(20, 130, 90), windp(160, 120, 100)], AIR, 1.5))
def a_steppe(i):
    blades = ' '.join('M%g %g q6 -14 16 -18' % (x, y) for x, y in [(10, 230), (40, 244), (70, 226), (100, 250), (130, 232), (160, 246), (190, 228), (220, 252), (250, 234), (30, 266), (90, 270), (150, 268), (210, 270), (264, 262)])
    return (L(['M0 190 H288'], HI, 1.6)
      + F(['M0 190 L288 190 L288 280 L0 280 Z'])
      + L([blades], MID, 1.3)
      + L([windp(10, 70, 110), windp(150, 60, 110), windp(60, 110, 100), windp(190, 130, 80)], AIR, 1.6))
def a_overlook(i):
    o = 'M0 110 L130 110 L142 124 L120 150 L130 200 L100 280 L0 280 Z'
    return (back('M150 260 Q200 230 288 250', 'M140 220 L180 200 L220 214 L288 190')
      + L(['M160 280 Q200 250 210 220 Q216 200 240 196'], WAT, 1.3, shadow=False)
      + F([o]) + L([o.replace(' L100 280 L0 280 Z', ' L100 280')], HI, 2)
      + L(['M40 110 L44 90 L54 90 L58 110 M38 90 L48 80 L60 90'], HI, 1.4)
      + L([windp(160, 70, 100), windp(170, 120, 90)], AIR, 1.5))
def a_windgap(i):
    r = 'M0 280 L0 120 L90 90 L120 130 L168 130 L198 86 L288 110 L288 280 Z'
    return (F([r]) + L(['M0 120 L90 90 L120 130 L168 130 L198 86 L288 110'], HI, 2)
      + L(['M40 150 L240 150 M30 200 L260 196'], MID, 1.2, shadow=False)
      + L(['M98 112 q23 -6 46 0 t46 0', 'M110 124 q17 -5 34 0 t34 0'], AIR, 1.6)
      + L([windp(200, 56, 80), windp(10, 64, 70)], AIR, 1.5))

# ---------- earth ----------
def a_boulder(i):
    return (back('M0 120 Q90 100 170 118 Q230 108 288 120')
      + ground(214, -4)
      + rocks((60, 232, 150, 120), (20, 236, 40, 22), (220, 240, 46, 28))
      + L(['M110 140 Q140 160 150 200', 'M170 150 L180 190'], MID, 1.3)
      + grass((40, 250), (210, 258), (120, 262)))
def a_bedrock(i):
    bands = ['M0 120 Q144 110 288 122', 'M0 160 Q144 150 288 164', 'M0 200 Q144 192 288 206', 'M0 240 Q144 234 288 246']
    return (F(['M0 80 L288 80 L288 280 L0 280 Z'])
      + L(['M0 80 Q144 74 288 82'], HI, 2) + L(bands, MID, 1.6)
      + L(['M80 80 L90 130 L84 170 M200 82 L196 140 L206 200 L200 250', 'M140 160 L150 210'], HI, 1.4)
      + grass((20, 80), (60, 78), (240, 80)))
def a_cave(i):
    face = 'M0 40 L288 40 L288 280 L0 280 Z'
    mouth = 'M70 280 Q70 140 144 130 Q218 140 218 280 Z'
    return (F([face]) + F([mouth], '#141615')
      + L(['M70 280 Q70 140 144 130 Q218 140 218 280'], HI, 2)
      + L(['M110 150 l6 22 l6 -22 M150 140 l5 26 l5 -26 M184 154 l5 18 l5 -18'], HI, 1.4)
      + L(['M0 90 Q60 84 120 96 M180 92 Q240 82 288 90 M10 200 H50 M240 210 H280'], MID, 1.2, shadow=False))
def a_meadow(i):
    flowers = ' '.join(ell(x, y, 3, 3) for x, y in [(40, 220), (70, 240), (110, 214), (150, 236), (180, 218), (220, 244), (250, 222), (90, 262), (200, 266), (130, 258)])
    return (L([sunp(220, 66, 18)], HI, 1.4)
      + ground(180, -10)
      + L([flowers], AIR, 1.3)
      + grass((30, 230), (60, 252), (100, 226), (140, 248), (170, 230), (210, 256), (240, 234)))
def a_grove(i):
    return (back('M0 120 Q144 100 288 120')
      + ground(230, -4)
      + roundtrees((60, 232, 24), (110, 226, 30), (170, 230, 26), (222, 234, 22))
      + grass((30, 252), (140, 258), (250, 254)))
def a_field(i):
    rows = ['M144 120 L%g 280' % x for x in [-40, 20, 80, 144, 208, 268, 328]]
    return (L([sunp(60, 70, 16, False)], HI, 1.4)
      + F(['M0 120 L288 120 L288 280 L0 280 Z']) + L(['M0 120 H288'], HI, 1.8)
      + L(rows, MID, 1.3)
      + back(cloudp(150, 70, 3, 16)))
def a_prairie(i):
    tall = ' '.join('M%g %g q-2 -30 6 -50' % (x, y) for x, y in [(20, 270), (44, 264), (70, 272), (96, 262), (124, 270), (150, 264), (176, 272), (200, 262), (226, 270), (252, 264), (276, 272)])
    return (back(cloudp(20, 70, 4, 18), cloudp(170, 90, 3, 16))
      + L(['M0 180 H288'], HI, 1.6) + F(['M0 180 L288 180 L288 280 L0 280 Z'])
      + L([tall], MID, 1.4)
      + L(['M20 220 l6 -30 M120 214 l4 -24 M220 220 l-4 -28'], HI, 1.2))
def a_thicket(i):
    tangle = 'M20 250 Q60 180 110 230 Q150 170 200 236 Q240 180 280 240 M30 230 Q80 160 140 210 Q190 150 260 220 M10 200 Q70 150 120 190 Q180 130 270 190 M40 260 L70 200 M90 260 L120 196 M160 262 L180 200 M220 262 L250 198'
    return (back('M0 130 Q144 110 288 130')
      + ground(244, -4) + L([tangle], HI, 1.5)
      + DOTS([(60, 200, 1.6), (130, 186, 1.6), (210, 196, 1.6), (240, 216, 1.4), (100, 224, 1.4)], MID))
def a_woodland(i):
    return (back('M0 120 Q144 100 288 120')
      + L([tree(30, 170, 0.8), tree(70, 166, 0.8), tree(120, 172, 0.8), tree(176, 168, 0.8), tree(230, 170, 0.8), tree(266, 166, 0.8)], MID, 1.3)
      + ground(220, -4)
      + conifers((40, 232, 1.3), (96, 240, 1.5), (156, 234, 1.3), (214, 242, 1.5), (262, 236, 1.2)))
def a_claybank(i):
    bank = 'M0 90 L170 90 Q190 120 180 160 L190 210 L0 210 Z'
    return (F([bank]) + L(['M0 90 L170 90 Q190 120 180 160 L190 210'], HI, 2)
      + L(['M0 120 L176 120', 'M0 146 L182 146', 'M0 174 L184 172', 'M0 196 L188 196'], EARTHC, 1.4)
      + F(['M0 210 L288 210 L288 280 L0 280 Z'], DEEP) + L([wave(0, 236, 4, 28, 11), wave(10, 262, 4, 32, 9)], WAT, 1.3, shadow=False)
      + grass((20, 90), (70, 88), (130, 90)))
def a_ravine(i):
    l, r = 'M0 60 L120 70 L136 280 L0 280 Z', 'M288 60 L168 70 L152 280 L288 280 Z'
    return (F([l, r]) + L(['M0 60 L120 70 L136 280', 'M288 60 L168 70 L152 280'], HI, 2)
      + L(['M20 110 L118 116 M14 170 L126 176 M20 230 L132 236', 'M268 110 L170 116 M274 170 L162 176 M268 230 L156 236'], MID, 1.2, shadow=False)
      + conifers((40, 60, 0.6), (80, 64, 0.6), (220, 62, 0.6), (256, 60, 0.6)))
def a_gulch(i):
    return (L([sunp(230, 56, 16, False)], HI, 1.4)
      + F(['M0 110 L80 120 Q110 200 144 220 Q178 200 208 120 L288 110 L288 280 L0 280 Z'])
      + L(['M0 110 L80 120 Q110 200 144 220 Q178 200 208 120 L288 110'], HI, 2)
      + rocks((110, 224, 22, 12), (150, 230, 26, 14), (126, 252, 18, 10))
      + L(['M20 150 L70 154 M230 150 L280 146 M30 200 L90 196'], MID, 1.2, shadow=False))
def a_mesa(i):
    m = 'M60 200 L80 100 L208 96 L228 200 Z'
    return (L([sunp(250, 56, 14, False)], HI, 1.4)
      + F([m]) + L([m[:-2]], HI, 2)
      + L(['M78 126 L212 124 M72 152 L218 150 M66 178 L222 176'], EARTHC, 1.4)
      + ground(200, 0)
      + L(['M20 236 l10 -8 l10 8 M240 244 l8 -6 l8 6'], MID, 1.3))
def a_plain(i):
    return (L([sunp(144, 150, 26, False)], HI, 1.5)
      + F(['M0 160 L288 160 L288 280 L0 280 Z']) + L(['M0 160 H288'], HI, 1.8)
      + L(['M20 200 H90 M150 210 H260 M40 240 H160 M200 252 H280'], MID, 1.2, shadow=False)
      + back(cloudp(10, 70, 3, 16), cloudp(190, 60, 2, 16)))

FIRE = [('Ember Bed', a_emberbed), ('Flint', a_flint), ('Obsidian', a_obsidian), ('Crater', a_crater), ('Geyser', a_geyser),
        ('Scrubland', a_scrubland), ('Ashfield', a_ashfield), ('Lava Field', a_lavafield), ('Dune', a_dune), ('Barrens', a_barrens),
        ('Steam Vent', a_steamvent), ('Cinder Field', art_cinder), ('Magma Pool', a_magmapool), ('Pumice', a_pumice), ('Burnt Hollow', a_burnthollow)]
WATER = [('Stream', a_stream), ('Pond', a_pond), ('Brook', a_brook), ('Creek', a_creek), ('Cove', a_cove),
         ('Lagoon', a_lagoon), ('Bog', a_bog), ('Spring', art_spring), ('Marsh', a_marsh), ('Swamp', a_swamp),
         ('Waterfall', a_waterfall), ('Mangrove', a_mangrove), ('Snowfield', a_snowfield), ('Tide Pool', a_tidepool), ('Floodplain', a_floodplain)]
AIRL = [('Spire', a_spire), ('Sea Stack', a_seastack), ('Summit', a_summit), ('Cliff', a_cliff), ('Plateau', a_plateau),
        ('Ridge', a_ridge), ('Peak', a_peak), ('Pass', a_pass), ('Bluff', a_bluff), ('Crag', a_crag),
        ('Ledge', art_ledge), ('Moor', a_moor), ('Steppe', a_steppe), ('Overlook', a_overlook), ('Wind Gap', a_windgap)]
EARTHL = [('Boulder', a_boulder), ('Bedrock', a_bedrock), ('Cave', a_cave), ('Meadow', a_meadow), ('Grove', a_grove),
          ('Field', a_field), ('Hill', art_hill), ('Prairie', a_prairie), ('Thicket', a_thicket), ('Woodland', a_woodland),
          ('Clay Bank', a_claybank), ('Ravine', a_ravine), ('Gulch', a_gulch), ('Mesa', a_mesa), ('Plain', a_plain)]

BOARDS = [('Commons-fire', 'fire', 1, FIRE), ('Commons-water', 'water', 16, WATER), ('Commons-air', 'air', 31, AIRL), ('Commons-earth', 'earth', 46, EARTHL)]
W, H = 1856, 1640

def board(el, start, cards):
    rows = [cards[0:5], cards[5:10], cards[10:15]]
    idx = 0; body = ''
    for r in rows:
        html = ''
        for name, art in r:
            idx += 1
            html += card(idx, name, start + idx - 1, 'C', [el], None, art)
        body += '<div style="display: flex; gap: 40px">%s</div>\n' % html
    title = '%s commons' % el.capitalize()
    sub = 'Fifteen permanence faces, numbers %d to %d. Each carries one %s affinity: 15 in all.' % (start, start + 14, el)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
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
<div style="display: flex; align-items: center; gap: 16px">
{glyph(el, 34)}
<div style="display: flex; flex-direction: column; gap: 6px">
<h1 style="margin: 0; font-size: 40px; font-weight: 600">{title}</h1>
<p style="margin: 0; font-family: 'IBM Plex Mono', monospace; font-size: 13px; color: #A9ADA2">{sub}</p>
</div>
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

if __name__ == '__main__':
    OUTDIR = sys.argv[1]
    for fname, el, start, cards in BOARDS:
        assert len(cards) == 15, fname
        open(os.path.join(OUTDIR, fname + '.dc.html'), 'w').write(board(el, start, cards))
        print(fname, 'ok')
