# Pixel scene engine for the framework set: layered placeholder landscapes at 48 cells wide.
# A scene is a spec: sky, sun or moon, far silhouettes, a main feature, water, ground and extras.
import math, random
from PIL import Image

SKY = {
    'day': ['#4E7FA6', '#6E98BC', '#9DBCD2', '#C8D8DC'], 'dawn': ['#2A3646', '#55687C', '#A8928A', '#DEBC96'],
    'dusk': ['#1C2034', '#36304C', '#704660', '#BC6C58'], 'night': ['#0C101C', '#131A2A', '#1E2638', '#2A3248'],
    'storm': ['#1E2428', '#2E363C', '#424C52', '#566066'], 'overcast': ['#565E64', '#6A7378', '#828A8E', '#969EA0'],
    'red': ['#180A0C', '#341214', '#621C18', '#9C361E'], 'haze': ['#A8987E', '#BCAC8E', '#CEBE9E', '#DCCEAE'],
    'arctic': ['#40607E', '#7090A8', '#A0B8C8', '#CCDAE2'], 'teal': ['#1A343E', '#2A525C', '#467478', '#82A6A0'],
    'gold': ['#3A2E3E', '#6A4A4E', '#B4785A', '#E0B07A'],
}
GROUND = {
    'grass': ['#24381F', '#30482A', '#466236'], 'sand': ['#A6804E', '#BE9862', '#D6B47E'], 'rock': ['#333336', '#46464A', '#5E5E62'],
    'snow': ['#A8B8C6', '#C8D6E0', '#EAF0F4'], 'ash': ['#242020', '#342E2E', '#484040'], 'mud': ['#40322A', '#564434', '#6E5A44'],
    'ice': ['#7098AE', '#9CBCCC', '#CCE0E8'], 'moss': ['#323E28', '#46522E', '#62703E'], 'red': ['#5E2E22', '#7E402C', '#9E5638'],
    'dark': ['#161A18', '#202622', '#2A302C'], 'lava': ['#3A1A12', '#7A2A18', '#D0663F'], 'shore': ['#7E7A6E', '#9A9484', '#B6AE9C'],
}
WATER = {
    'crater': ['#1A1616', '#262020', '#4A4040'],
    'blue': ['#24506E', '#346A8A', '#7FA7B5'], 'teal': ['#286070', '#3A8290', '#A6D0D6'], 'deep': ['#14304A', '#1E4262', '#46729A'],
    'hot': ['#4A8890', '#6AA8AE', '#DCEAEA'], 'lava': ['#7A2A18', '#D0663F', '#F2B25A'], 'mud': ['#4A382A', '#665036', '#866E56'],
    'ice': ['#86ACC0', '#B0CCD8', '#E2EEF2'], 'storm': ['#22404E', '#30566A', '#6E8C98'],
}
FEAT = {  # lit, mid, shade
    'stone': ['#6A6670', '#4C4A54', '#34323A'], 'earth': ['#7E6048', '#5A4434', '#3A2E25'], 'snowrock': ['#5A6270', '#444A56', '#30343E'],
    'red': ['#A65A3C', '#844430', '#5C2E22'], 'dark': ['#3A2C24', '#2B211D', '#1E1714'], 'green': ['#4E6A3A', '#3A5230', '#283A22'],
    'sand': ['#D2AE78', '#B8945E', '#94744A'], 'ice': ['#C8DCE6', '#9ABCCC', '#6E92A8'], 'violet': ['#5A5068', '#463E54', '#322C40'],
    'black': ['#2A2A30', '#1E1E24', '#141418'], 'olive': ['#6A6A4A', '#525238', '#3C3C28'],
}
SKYSET = {c for v in SKY.values() for c in v}
def solid(g, x, y):
    c = g.get(x, y); return c is not None and c not in SKYSET
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
def dith(t, x, y): return t * 16 > BAYER[y % 4][x % 4] + 0.5

class G:
    def __init__(s, w, h): s.w, s.h = w, h; s.p = [[None] * w for _ in range(h)]
    def set(s, x, y, c):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < s.w and 0 <= y < s.h and c: s.p[y][x] = c
    def get(s, x, y):
        x, y = int(round(x)), int(round(y))
        return s.p[y][x] if 0 <= x < s.w and 0 <= y < s.h else None
    def png(s, path):
        im = Image.new('RGB', (s.w, s.h))
        im.putdata([tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) if c else (0, 0, 0) for row in s.p for c in row])
        im.save(path, optimize=True)

def bands(g, y0, y1, cols):
    n = len(cols) - 1
    for y in range(max(0, y0), min(g.h, y1)):
        f = (y - y0) / max(1, (y1 - y0 - 1)) * n; i = min(int(f), n - 1); t = f - i
        for x in range(g.w): g.set(x, y, cols[i + 1] if dith(t, x, y) else cols[i])

def disc(g, cx, cy, r, col, sy=1.0):
    for y in range(int(cy - r * sy) - 1, int(cy + r * sy) + 2):
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            if ((x - cx) / r) ** 2 + ((y - cy) / (r * sy)) ** 2 <= 1: g.set(x, y, col)

def fill_profile(g, hfun, base, pal, rnd, snow=None, strata=False, rough=0.6, snowline=None):
    """Fill from a height profile down to base, lit on rising slopes and shaded on falling ones."""
    tops = [hfun(x) for x in range(g.w)]
    for x in range(g.w):
        top = tops[x]
        if top is None: continue
        slope = (tops[min(x + 1, g.w - 1)] or top) - (tops[max(x - 1, 0)] or top)
        for y in range(int(round(top)), base):
            c = pal[0] if slope > 0.35 else (pal[2] if slope < -0.35 else pal[1])
            if c == pal[1] and dith(0.35, x, y): c = pal[2] if slope < 0 else pal[0]
            if snowline is not None and y < snowline + (x * 7 % 3) - 1: c = '#E6ECF0' if slope >= 0 else '#B8C6D2'
            elif snow and snowline is None and y < top + snow + (x * 7 % 3) - 1: c = '#E6ECF0' if slope >= 0 else '#B8C6D2'
            if strata and (y - int(top)) % 5 == 4 and rnd.random() < 0.5: c = pal[2]
            if rough and rnd.random() < rough * 0.08: c = pal[2] if c != pal[2] else pal[1]
            g.set(x, y, c)
    return tops

# ---------- features (each returns nothing; draws onto g)
def f_peak(g, rnd, hz, cx=24, h=24, w=0.75, pal='stone', snow=0, jag=0.8):
    def hf(x):
        d = abs(x - cx); y = hz - h + d / w + jag * math.sin(x * 1.7 + cx) * (0.3 + d / 30)
        return y if y < hz else None
    fill_profile(g, hf, hz + 2, FEAT[pal], rnd, snowline=(hz - h + snow * 1.6) if snow else None)
def f_range(g, rnd, hz, pal='stone', snow=0, n=4, hmax=18):
    cxs = sorted(rnd.uniform(4, 44) for _ in range(n)); hs = [rnd.uniform(hmax * 0.55, hmax) for _ in cxs]
    def hf(x):
        y = min(hz - h + abs(x - cx) * 1.1 for cx, h in zip(cxs, hs)) + math.sin(x * 2.1) * 0.5
        return y if y < hz else None
    fill_profile(g, hf, hz + 2, FEAT[pal], rnd, snowline=(hz - hmax + snow * 2.2) if snow else None)
def f_cone(g, rnd, hz, cx=24, h=24, crater=6, pal='earth', glow=True, lake=None):
    top = hz - h
    def hf(x):
        d = abs(x - cx) - crater / 2
        if d < 0: return top
        y = top + 1.4 * (d ** 1.15) / 1.6 + rnd.random() * 0.3
        return y if y < hz else None
    fill_profile(g, hf, hz + 2, FEAT[pal], rnd, strata=True)
    for x in range(int(cx - crater / 2), int(cx + crater / 2) + 1):
        g.set(x, top, lake or '#2A201C')
        if lake: g.set(x, top + 1, lake)
    if glow and not lake:
        for dx in (-1, 0, 1): g.set(cx + dx, top, '#D0663F' if dx else '#F2B25A')
def f_mesa(g, rnd, hz, cx=24, w=14, h=14, pal='red'):
    def hf(x):
        d = abs(x - cx) - w / 2
        y = hz - h if d < 0 else hz - h + d * 2.2
        return y if y < hz else None
    fill_profile(g, hf, hz + 2, FEAT[pal], rnd, strata=True)
def f_hill(g, rnd, hz, cx=24, w=22, h=10, pal='green'):
    def hf(x):
        d = (x - cx) / w
        return hz - h * math.exp(-d * d * 2.4) + 0.4 if abs(d) < 1.4 else None
    fill_profile(g, hf, hz + 2, FEAT[pal], rnd, rough=0.3)
def f_dunes(g, rnd, hz, pal='sand', n=3):
    for k in range(n):
        base = hz + k * 3; amp = 3 + k; ph = rnd.uniform(0, 6)
        fill_profile(g, lambda x, b=base, a=amp, p=ph: b - a * (0.6 + 0.4 * math.sin(x * 0.16 + p)), g.h, FEAT[pal], rnd, rough=0.1)
def f_towers(g, rnd, hz, pal='stone', n=4, hmax=24):
    xs = [6 + i * (36 / max(1, n - 1)) + rnd.uniform(-2, 2) for i in range(n)]
    for i, cx in enumerate(xs):
        h = rnd.uniform(hmax * 0.55, hmax); w = rnd.uniform(2.5, 4)
        for y in range(int(hz - h), hz + 2):
            for x in range(int(cx - w), int(cx + w) + 1):
                c = FEAT[pal][0] if x < cx - w / 3 else (FEAT[pal][2] if x > cx + w / 3 else FEAT[pal][1])
                if (y - int(hz - h)) % 4 == 3 and rnd.random() < 0.5: c = FEAT[pal][2]
                g.set(x, y, c)
        for x in range(int(cx - w), int(cx + w) + 1): g.set(x, int(hz - h), FEAT['green'][1] if rnd.random() < 0.5 else FEAT[pal][0])
def f_spire(g, rnd, hz, cx=24, h=30, pal='stone'):
    for y in range(int(hz - h), hz + 2):
        w = 0.6 + (y - (hz - h)) * 0.16
        for x in range(int(cx - w), int(cx + w) + 1):
            g.set(x, y, FEAT[pal][0] if x < cx else FEAT[pal][2])
def f_cliff(g, rnd, hz, side='left', top=None, pal='stone', grass=True):
    top = top if top is not None else hz - 16
    edge = 20 if side == 'left' else 28
    for x in range(g.w):
        inside = x < edge + rnd.uniform(-1, 1) if side == 'left' else x > edge + rnd.uniform(-1, 1)
        if not inside: continue
        for y in range(top, g.h):
            near = abs(x - edge) < 3
            c = FEAT[pal][2] if near else (FEAT[pal][1] if (x + y) % 5 else FEAT[pal][2])
            if y < top + 2 and grass: c = FEAT['green'][0]
            g.set(x, y, c)
def f_canyon(g, rnd, hz, pal='red', gap=12):
    l, r = 24 - gap / 2, 24 + gap / 2
    for x in range(g.w):
        for y in range(hz - 18, g.h):
            wl = l - (y - (hz - 18)) * 0.25; wr = r + (y - (hz - 18)) * 0.25
            if x < wl or x > wr:
                c = FEAT[pal][0] if x > wr else FEAT[pal][2]
                if (y % 4 == 0) and rnd.random() < 0.6: c = FEAT[pal][1]
                g.set(x, y, c)
def f_island(g, rnd, hz, cx=24, cy=None, w=14, pal='earth'):
    cy = cy if cy is not None else int(hz * 0.55)
    for x in range(int(cx - w), int(cx + w) + 1):
        d = abs(x - cx) / w
        depth = int((1 - d * d) * w * 0.9) + rnd.randint(0, 1)
        g.set(x, cy - 1, FEAT['green'][0]); g.set(x, cy, FEAT['green'][1])
        for y in range(cy + 1, cy + 1 + depth): g.set(x, y, FEAT[pal][0] if x < cx else FEAT[pal][2])
def f_trees(g, rnd, hz, n=9, pal='green', size=5, y0=None, conifer=True):
    y0 = y0 if y0 is not None else hz + 1
    for i in range(n):
        cx = rnd.uniform(1, 47); s = size * rnd.uniform(0.7, 1.2); base = y0 + rnd.uniform(-1, 3)
        if conifer:
            for k in range(int(s * 1.8)):
                y = base - k; w = (s * 1.8 - k) / 3.2
                for x in range(int(cx - w), int(cx + w) + 1):
                    g.set(x, y, FEAT[pal][0] if x < cx else FEAT[pal][2] if x > cx + w / 3 else FEAT[pal][1])
        else:
            for k in range(int(s * 0.5) + 1): g.set(cx, base - k, '#3A2E25')
            r = s * 0.62; cy = base - s * 0.5 - r * 0.7
            disc(g, cx, cy, r, FEAT[pal][2]); disc(g, cx - r * 0.25, cy - r * 0.2, r * 0.72, FEAT[pal][1]); disc(g, cx - r * 0.45, cy - r * 0.4, r * 0.35, FEAT[pal][0])
        g.set(cx, base + 1, '#3A2E25')
def f_bigtree(g, rnd, hz, cx=24, pal='green'):
    for y in range(hz - 10, hz + 3):
        for x in range(cx - 1, cx + 2): g.set(x, y, '#4A3A2C' if x < cx + 1 else '#34281E')
    for (dx, dy, r) in ((0, -16, 8), (-6, -12, 6), (6, -12, 6), (-3, -20, 5), (4, -19, 5)):
        disc(g, cx + dx, hz + dy, r, FEAT[pal][1]); disc(g, cx + dx - 1, hz + dy - 1, r * 0.6, FEAT[pal][0])
def f_cave(g, rnd, hz, pal='stone'):
    f_hill(g, rnd, hz + 4, cx=24, w=30, h=26, pal=pal)
    disc(g, 24, hz + 2, 8, '#0E0C0C', sy=1.4)
    for y in range(hz + 2, g.h):
        for x in range(16, 33): g.set(x, y, '#0E0C0C') if g.get(x, y) and abs(x - 24) < 8 - (y - hz - 2) * 0.1 else None
def f_arch(g, rnd, hz, pal='red'):
    f_mesa(g, rnd, hz, cx=24, w=26, h=16, pal=pal)
    disc(g, 24, hz + 1, 7, None)
    for y in range(hz - 8, hz + 2):
        for x in range(17, 32):
            if ((x - 24) / 7) ** 2 + ((y - hz - 1) / 8) ** 2 <= 1: g.p[y][x] = None
def f_glacier(g, rnd, hz, pal='ice'):
    tops = [hz - 12 + 2.0 * math.sin(x * 0.22) + rnd.uniform(-0.7, 0.7) for x in range(48)]
    front = g.h - 7
    for x in range(48):
        t = int(tops[x])
        for y in range(t, front):
            f = (y - t) / max(1, front - t)
            c = '#EEF4F6' if y <= t + 1 else (FEAT[pal][0] if f < 0.3 else FEAT[pal][1] if f < 0.75 else FEAT[pal][2])
            if 0.25 < f < 0.35 and dith(0.5, x, y): c = FEAT[pal][1]
            if 0.7 < f < 0.8 and dith(0.5, x, y): c = FEAT[pal][2]
            g.set(x, y, c)
    for _ in range(7):
        x = rnd.randrange(3, 45); y = int(tops[x]) + 3
        for k in range(rnd.randint(5, 12)): g.set(x, y + k, '#4E6E84')
    for y in range(front, g.h):
        for x in range(48): g.set(x, y, WATER['deep'][1] if dith((y - front) / 7, x, y) else WATER['deep'][0])
    for x in range(48): g.set(x, front, '#CCE0E8' if x % 3 else WATER['deep'][2])
def f_stack(g, rnd, hz, cx=30, h=18, pal='stone'):
    for y in range(int(hz - h), hz + 3):
        w = 2.5 + (y - (hz - h)) * 0.08
        for x in range(int(cx - w), int(cx + w) + 1): g.set(x, y, FEAT[pal][0] if x < cx else FEAT[pal][2])
    for x in range(int(cx - 2), int(cx + 3)): g.set(x, int(hz - h), FEAT['green'][0])

FEATURES = dict(peak=f_peak, range=f_range, cone=f_cone, mesa=f_mesa, hill=f_hill, dunes=f_dunes, towers=f_towers, spire=f_spire,
                cliff=f_cliff, canyon=f_canyon, island=f_island, trees=f_trees, bigtree=f_bigtree, cave=f_cave, arch=f_arch,
                glacier=f_glacier, stack=f_stack)

# ---------- water
def w_sea(g, rnd, hz, pal='blue', depth=None):
    depth = depth or g.h - hz
    for y in range(hz, min(g.h, hz + depth)):
        for x in range(g.w): g.set(x, y, WATER[pal][1] if dith((y - hz) / max(1, depth), x, y) else WATER[pal][0])
    for x in range(g.w): g.set(x, hz, WATER[pal][2])
    for _ in range(depth * 2): g.set(rnd.randrange(48), rnd.randrange(hz + 1, min(g.h, hz + depth)), WATER[pal][2])
def w_lake(g, rnd, hz, pal='blue', cy=None, rx=16, ry=None, cx=24):
    cy = cy if cy is not None else hz + (g.h - hz) * 0.55; ry = ry or max(2.5, (g.h - hz) * 0.24)
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            v = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if v <= 1: g.set(x, y, WATER[pal][0] if v < 0.4 and dith(0.6, x, y) else WATER[pal][1])
            elif v <= 1.3: g.set(x, y, '#1C2224')
    for _ in range(int(rx / 2)): g.set(cx + rnd.uniform(-rx * 0.7, rx * 0.7), cy + rnd.uniform(-ry * 0.5, ry * 0.5), WATER[pal][2])
def w_river(g, rnd, hz, pal='blue'):
    x = 24.0
    for y in range(hz, g.h):
        x += math.sin(y * 0.35) * 0.9; w = 1 + (y - hz) * 0.18
        for xx in range(int(x - w), int(x + w) + 1): g.set(xx, y, WATER[pal][1] if (xx + y) % 5 else WATER[pal][2])
def w_fall(g, rnd, hz, pal='blue', x0=22, top=None):
    top = top if top is not None else hz - 16
    for y in range(top, hz + 2):
        for x in range(x0, x0 + 5): g.set(x, y, WATER[pal][2] if (x + y * 2) % 5 == 0 else WATER[pal][1])
    for _ in range(14): g.set(x0 + rnd.uniform(-3, 8), hz + rnd.uniform(0, 3), '#E6F0F2')
WATERS = dict(sea=w_sea, lake=w_lake, river=w_river, fall=w_fall)

# ---------- extras
def e_sun(g, rnd, hz, x=36, y=None, r=3.4, col='#F2D29A'):
    disc(g, x, y if y is not None else hz - 8, r, col)
def e_moon(g, rnd, hz, x=37, y=6): disc(g, x, y, 2.6, '#DCE0D8'); disc(g, x + 1.2, y - 0.6, 2.2, None) if False else None
def e_stars(g, rnd, hz, n=16):
    for _ in range(n): g.set(rnd.randrange(48), rnd.randrange(max(1, hz - 6)), '#C9CFD6' if rnd.random() < 0.5 else '#7E8796')
def e_clouds(g, rnd, hz, n=3, col='#C8CED2', y0=3):
    for _ in range(n):
        cx, cy = rnd.uniform(0, 48), rnd.uniform(y0, max(y0 + 1, hz * 0.45))
        for k in range(4): disc(g, cx + k * 2.2 - 3, cy + (k % 2) * 0.5, rnd.uniform(1.4, 2.4), col, sy=0.6)
def e_smoke(g, rnd, hz, x=24, y=None, n=10, col='#6E6A70'):
    y = y if y is not None else hz - 20
    for i in range(n): disc(g, x + i * 0.9 + math.sin(i) * 1.1, y - i * 1.1, 1 + i * 0.25, col if i % 2 else '#55525A', sy=0.7)
def e_steam(g, rnd, hz, n=4, xs=None, y=None):
    for cx in (xs or [rnd.uniform(8, 40) for _ in range(n)]):
        for i in range(7): disc(g, cx + math.sin(i * 0.9) * 0.8, (y if y is not None else hz + 4) - i * 1.6, 0.8 + i * 0.22, '#D6DCDC' if i % 2 else '#B8C0C2', sy=0.8)
def e_geyser(g, rnd, hz, x=24, y=None, h=16):
    y = y if y is not None else hz + 4
    for k in range(h):
        for dx in (-1, 0, 1): g.set(x + dx + rnd.uniform(-0.4, 0.4), y - k, '#E6F0F2' if k % 3 else '#B8D4DA')
    disc(g, x, y - h, 3, '#E6F0F2', sy=0.7)
def e_embers(g, rnd, hz, n=26):
    for _ in range(n): g.set(rnd.randrange(48), rnd.randrange(g.h), '#F2A23A' if rnd.random() < 0.5 else '#D0663F')
def e_snow(g, rnd, hz, n=60):
    for _ in range(n): g.set(rnd.randrange(48), rnd.randrange(g.h), '#E6ECF0')
def e_rain(g, rnd, hz, n=40, col='#9AA8B0'):
    for _ in range(n):
        x, y = rnd.randrange(-4, 48), rnd.randrange(0, g.h)
        g.set(x, y, col); g.set(x - 1, y + 1, '#7E8C94')
def e_hail(g, rnd, hz, n=30):
    for _ in range(n): g.set(rnd.randrange(48), rnd.randrange(g.h), '#F0F4F6')
def e_birds(g, rnd, hz, n=2):
    for _ in range(n):
        x, y = rnd.uniform(6, 42), rnd.uniform(3, max(4, hz * 0.4))
        for (dx, dy) in ((0, 0), (-1, -1), (1, -1), (-2, -1), (2, -1)): g.set(x + dx, y + dy, '#1E2226')
def e_fog(g, rnd, hz, y0=None, h=8, col='#C8D0D2'):
    y0 = y0 if y0 is not None else hz - 3
    for y in range(y0, y0 + h):
        for x in range(48):
            if dith(0.45 - abs(y - y0 - h / 2) / h * 0.6, x, y): g.set(x, y, col)
def e_aurora(g, rnd, hz):
    for k, col in enumerate(('#4E9A7A', '#6ABA8E', '#3E7A86')):
        for x in range(48):
            y = 5 + k * 2 + 2 * math.sin(x * 0.25 + k)
            if dith(0.6, x, int(y)): g.set(x, y, col); g.set(x, y + 1, col if x % 2 else None)
def e_lightning(g, rnd, hz, x=30):
    y = 0
    while y < hz:
        g.set(x, y, '#F4F0C8'); g.set(x + 1, y, '#C8C4A0'); y += 1
        if rnd.random() < 0.35: x += rnd.choice((-1, 1))
def e_wind(g, rnd, hz, n=9, col='#D8DEDE'):
    for _ in range(n):
        x, y = rnd.uniform(-6, 40), rnd.uniform(2, g.h - 4)
        for k in range(rnd.randint(5, 9)): g.set(x + k, y + math.sin(k * 0.6) * 0.6, col)
def e_funnel(g, rnd, hz, x=30, col='#8A8E92'):
    for y in range(0, hz + 2):
        w = 0.6 + (hz - y) * 0.22; xc = x + math.sin(y * 0.4) * 1.5
        for xx in range(int(xc - w), int(xc + w) + 1): g.set(xx, y, col if (xx + y) % 3 else '#6A6E72')
def e_lava(g, rnd, hz, x=24, y=None, n=3):
    y = y if y is not None else hz - 18
    for d in ([-0.6, 0.5, 0.9][:n]):
        xx = x
        for yy in range(int(y), g.h):
            xx += d + (rnd.random() - 0.5) * 0.7
            if solid(g, xx, yy): g.set(xx, yy, '#F2A23A'); g.set(xx + 1, yy, '#D0663F')
def e_fountain(g, rnd, hz, x=24, y=None):
    y = y if y is not None else hz - 18
    for _ in range(50):
        yy = rnd.uniform(y - 9, y); g.set(x + rnd.gauss(0, (y - yy) * 0.3 + 0.4), yy, '#FFE08A' if rnd.random() < 0.4 else '#F2A23A')
def e_cracks(g, rnd, hz, n=4, col='#140F0C'):
    for _ in range(n):
        x, y = rnd.uniform(4, 44), rnd.uniform(hz + 2, g.h - 2)
        for k in range(rnd.randint(5, 10)):
            g.set(x, y, col); x += rnd.choice((-1, 0, 1)); y += rnd.choice((0, 1)) if rnd.random() < 0.5 else 0
            g.set(x + 1, y, '#D0663F' if rnd.random() < 0.15 else col)
def e_boulders(g, rnd, hz, n=5):
    for _ in range(n):
        x, y = rnd.uniform(2, 46), rnd.uniform(2, g.h - 3); r = rnd.uniform(0.9, 1.8)
        disc(g, x, y, r, '#5A4A3C'); g.set(x - 0.5, y - 0.5, '#7A6650')
def e_rocks(g, rnd, hz, n=6, col='#4A4E4C'):
    for _ in range(n):
        x, y = rnd.uniform(2, 46), rnd.uniform(hz + 3, g.h - 1)
        g.set(x, y, col); g.set(x + 1, y, col); g.set(x, y - 1, '#6A6E6C')
def e_reeds(g, rnd, hz, n=10, y0=None):
    for _ in range(n):
        x = rnd.uniform(1, 47); base = (y0 if y0 is not None else g.h - 2) - rnd.uniform(0, 4)
        for k in range(rnd.randint(2, 4)): g.set(x, base - k, '#5E7A3E' if k < 2 else '#8A9A4E')
def e_cactus(g, rnd, hz, n=3):
    for _ in range(n):
        x = rnd.uniform(4, 44); base = rnd.uniform(hz + 5, g.h - 2)
        for k in range(5): g.set(x, base - k, '#4E6A3A')
        g.set(x - 1, base - 3, '#4E6A3A'); g.set(x - 1, base - 4, '#4E6A3A'); g.set(x + 1, base - 2, '#3A5230'); g.set(x + 1, base - 3, '#3A5230')
def e_ripples(g, rnd, hz, pts=((18, None), (30, None))):
    for (cx, cy) in pts:
        cy = cy if cy is not None else hz + (g.h - hz) * 0.55
        for a in range(0, 360, 30): g.set(cx + math.cos(math.radians(a)) * 3, cy + math.sin(math.radians(a)) * 1, '#C6E0E4')
def e_shimmer(g, rnd, hz, col='#E8D8B0'):
    for y in range(hz - 4, hz + 4, 2):
        for x in range(48):
            if (x + y * 3) % 7 < 3 and rnd.random() < 0.5: g.set(x, y + math.sin(x * 0.5), col)
def e_flames(g, rnd, hz, n=8):
    for _ in range(n):
        x = rnd.uniform(1, 47); base = rnd.uniform(hz + 1, g.h - 1); h = rnd.randint(3, 6)
        for k in range(h):
            for dx in range(-max(0, (h - k) // 2), max(0, (h - k) // 2) + 1):
                g.set(x + dx, base - k, '#FFE08A' if k < h / 3 and dx == 0 else ('#F2A23A' if abs(dx) < 1 else '#D0663F'))
def e_wave(g, rnd, hz, col=('#24506E', '#346A8A', '#E6F0F2')):
    for x in range(48):
        top = hz - 14 + 10 * math.exp(-((x - 30) / 10) ** 2) * -1 + 10
        top = hz - 4 - 12 * math.exp(-((x - 30) / 9) ** 2)
        for y in range(int(top), hz + 3): g.set(x, y, col[0] if y > top + 2 else col[1])
        g.set(x, int(top), col[2])
    for k in range(6): g.set(24 + k, hz - 15 + k * 0.3, col[2])
def e_glow(g, rnd, hz, col='#D0663F'):
    for y in range(max(0, hz - 6), min(g.h, hz + 1)):
        for x in range(48):
            if dith(0.25, x, y) and solid(g, x, y): g.set(x, y, col)
def e_icicles(g, rnd, hz, n=10):
    for _ in range(n):
        x = rnd.randrange(48)
        for k in range(rnd.randint(1, 4)): g.set(x, k, '#CCE0E8')
EXTRAS = dict(sun=e_sun, moon=e_moon, stars=e_stars, clouds=e_clouds, smoke=e_smoke, steam=e_steam, geyser=e_geyser, embers=e_embers,
              snow=e_snow, rain=e_rain, hail=e_hail, birds=e_birds, fog=e_fog, aurora=e_aurora, lightning=e_lightning, wind=e_wind,
              funnel=e_funnel, lava=e_lava, fountain=e_fountain, cracks=e_cracks, boulders=e_boulders, rocks=e_rocks, reeds=e_reeds,
              cactus=e_cactus, ripples=e_ripples, shimmer=e_shimmer, flames=e_flames, wave=e_wave, glow=e_glow, icicles=e_icicles)
SKY_LAYER = {'sun', 'moon', 'stars', 'clouds', 'aurora', 'lightning', 'birds'}

def ground(g, rnd, hz, kind, top=None):
    pal = GROUND[kind]; top = top if top is not None else hz
    for x in range(g.w):
        t = top + int(1.2 * math.sin(x * 0.4 + rnd.random()))
        for y in range(max(0, t), g.h):
            c = pal[1] if dith(min(1, (y - t) / max(1, g.h - t) * 1.4), x, y) else pal[2] if y == t else pal[0]
            if rnd.random() < 0.05: c = pal[2]
            g.set(x, y, c)

def render(spec, H, seed):
    """spec: sky, hz (horizon as a fraction), far ('ridges', 'hills', None), feats [(name, kwargs)], water [(name, kwargs)],
    ground (kind or None), gtop (ground top as a fraction), extras [(name, kwargs)]."""
    rnd = random.Random(seed); g = G(48, H)
    hz = int(H * spec.get('hz', 0.62))
    bands(g, 0, hz + 2, SKY[spec.get('sky', 'day')])
    for name, kw in spec.get('extras', []):
        if name in SKY_LAYER: EXTRAS[name](g, rnd, hz, **kw)
    far = spec.get('far')
    if far:
        col = spec.get('farcol', '#2A2F3C')
        for x in range(48):
            h = hz - 3 - int(2.2 * math.sin(x * 0.35 + seed) + 1.5 * math.sin(x * 0.9 + 1)) - (3 if far == 'mountains' else 0)
            for y in range(h, hz + 1): g.set(x, y, col)
    for name, kw in spec.get('water_far', []): WATERS[name](g, rnd, hz, **kw)
    for name, kw in spec.get('feats', []): FEATURES[name](g, rnd, hz, **kw)
    if spec.get('ground'): ground(g, rnd, hz, spec['ground'], int(H * spec['gtop']) if 'gtop' in spec else None)
    for name, kw in spec.get('water', []): WATERS[name](g, rnd, hz, **kw)
    for name, kw in spec.get('feats2', []): FEATURES[name](g, rnd, hz, **kw)
    for name, kw in spec.get('extras', []):
        if name not in SKY_LAYER: EXTRAS[name](g, rnd, hz, **kw)
    for y in range(H):  # anything left empty takes the sky colour behind it
        for x in range(48):
            if g.p[y][x] is None:
                g.p[y][x] = SKY[spec.get('sky', 'day')][min(3, int(y / max(1, hz + 2) * 4))] if y <= hz + 1 else GROUND['dark'][1 if dith(0.5, x, y) else 0]
    return g

def e_flowers(g, rnd, hz, n=24):
    for _ in range(n):
        x, y = rnd.uniform(1, 47), rnd.uniform(hz + 3, g.h - 1)
        g.set(x, y, rnd.choice(('#D8C46A', '#C07A9A', '#E0E0D0', '#A87AC0')))
def e_core(g, rnd, hz):
    for r, col in ((30, '#3A1A12'), (24, '#7A2A18'), (17, '#B8431F'), (11, '#E07A2A'), (6, '#F2C45A'), (2.5, '#FFF0B0')):
        disc(g, 24, g.h * 0.62, r, col)
    e_embers(g, rnd, hz, n=40)
def e_equinox(g, rnd, hz):
    for y in range(0, hz + 2):
        for x in range(24, 48): g.set(x, y, SKY['night'][min(3, int(y / (hz + 2) * 4))])
    e_stars.__wrapped__ if False else None
    for _ in range(10): g.set(rnd.randrange(26, 48), rnd.randrange(max(1, hz - 4)), '#C9CFD6')
    disc(g, 24, hz, 4, '#F2D29A')
def e_rays(g, rnd, hz, x=24, y=4):
    for a in range(20, 170, 18):
        for k in range(4, 40):
            if k % 3: g.set(x + math.cos(math.radians(a)) * k, y + math.sin(math.radians(a)) * k, '#F4E2B0')
    disc(g, x, y, 4, '#FFF0C0')
def e_sound(g, rnd, hz, x=24, y=None):
    y = y if y is not None else hz - 8
    for r in (3, 6, 9, 12):
        for a in range(0, 360, 12): g.set(x + math.cos(math.radians(a)) * r, y + math.sin(math.radians(a)) * r * 0.6, '#C8C0D8')
EXTRAS.update(flowers=e_flowers, core=e_core, equinox=e_equinox, rays=e_rays, sound=e_sound)
SKY_LAYER.update({'equinox', 'rays'})
