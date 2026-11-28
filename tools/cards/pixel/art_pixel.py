# Pixel style: low-resolution scenes in a restrained palette (after He Is Coming and Probably Stolen).
import math, random
from common import Grid, bands, dither

def cone(g, cx, top, bottom, crater_w, lit, mid, shade, rnd, spread=0.78):
    for y in range(top, bottom):
        d = y - top
        hw = crater_w / 2 + spread * (0.35 * d + 0.034 * d * d) + (rnd.random() - 0.5) * 0.9
        for x in range(int(cx - hw), int(cx + hw) + 1):
            rel = (x - cx) / max(hw, 1)
            c = lit if rel < -0.25 else (mid if rel < 0.35 else shade)
            if rel > 0.1 and rel < 0.35 and dither(0.5, x, y): c = shade
            if rel < -0.25 and rel > -0.45 and dither(0.4, x, y): c = mid
            g.set(x, y, c)
    return lambda y: crater_w / 2 + (y - top) * spread

def volcano_front():
    rnd = random.Random(23); g = Grid(48, 46, '#1A2230')
    bands(g, 0, 33, ['#161C28', '#232A3A', '#3A3346', '#6A4448', '#8E5A48'])
    for _ in range(14):
        x, y = rnd.randrange(48), rnd.randrange(14); g.set(x, y, '#C9CFD6' if rnd.random() < 0.5 else '#7E8796')
    # far ridges
    for x in range(48):
        h = 27 + int(2.2 * math.sin(x * 0.35) + 1.5 * math.sin(x * 0.9 + 1))
        for y in range(h, 34): g.set(x, y, '#2A2F3C')
        h2 = 31 + int(1.5 * math.sin(x * 0.5 + 2))
        for y in range(h2, 36): g.set(x, y, '#222633')
    cone(g, 24, 12, 41, 6, '#7E6048', '#5A4434', '#352A23', rnd, spread=1.15)
    for x in range(21, 28): g.set(x, 12, '#2A201C')
    for x in (21, 27): g.set(x, 11, '#4A3A30')
    g.set(23, 12, '#D0663F'); g.set(25, 12, '#E08A4A'); g.set(24, 12, '#F2B25A')
    for y in (20, 27, 34):  # strata
        for x in range(48):
            if g.get(x, y) in ('#7E6048', '#5A4434') and (x + y) % 4 == 0: g.set(x, y, '#46362C')
    # smoke drifting right
    for i in range(11):
        y = 10 - i; cx = 24 + i * 0.9 + math.sin(i * 0.8) * 1.2; r = 1 + i * 0.28
        for dy in range(-2, 3):
            for dx in range(-3, 4):
                if dx * dx / (r * r + 0.5) + dy * dy / (r * 0.7 + 0.6) ** 2 <= 1:
                    g.set(cx + dx, y + dy * 0.6, '#6E6A70' if dy < 0 else '#55525A')
    # ground
    for y in range(40, 46):
        for x in range(48): g.set(x, y, '#1C221E' if dither((y - 40) / 6, x, y) else '#26302A')
    for x in range(48):
        if rnd.random() < 0.35: g.set(x, 40, '#3A4A3A')
        if rnd.random() < 0.12: g.set(x, 41, '#4A5A44')
    for _ in range(5):
        x = rnd.randrange(2, 46); g.set(x, 42, '#3C403C'); g.set(x + 1, 42, '#4A4E48'); g.set(x, 43, '#2E322E')
    return g

def volcano_back():
    rnd = random.Random(5); g = Grid(48, 31, '#170C0C')
    bands(g, 0, 31, ['#140A0A', '#2A1010', '#4A1A14', '#7A2A18'])
    # ash cloud
    for i in range(40):
        cx = 24 + rnd.gauss(0, 7); cy = 5 + rnd.gauss(0, 2.2); r = rnd.uniform(1.5, 3.2)
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                if dx * dx + dy * dy <= r * r:
                    c = '#3A3234' if dy < 0 else '#2A2426'
                    if dy >= r - 1.5: c = '#6A3A2A'
                    g.set(cx + dx, cy + dy, c)
    hw = cone(g, 24, 13, 31, 6, '#3A2C24', '#2B211D', '#1E1714', rnd, spread=1.6)
    for x in range(21, 28): g.set(x, 13, '#F2A23A')
    # lava streams
    for start, drift in ((22, -0.55), (25, 0.5), (27, 0.9)):
        x = start
        for y in range(13, 31):
            x += drift + (rnd.random() - 0.5) * 0.8
            g.set(x, y, '#F2A23A'); g.set(x + 1, y, '#D0663F')
            if y < 18: g.set(x, y, '#FFE08A')
    # fountain
    for _ in range(60):
        y = rnd.randrange(5, 13); x = 24 + rnd.gauss(0, (13 - y) * 0.35 + 0.4)
        g.set(x, y, '#FFE08A' if rnd.random() < 0.4 else '#F2A23A')
    # bombs with trails
    for (x0, y0, vx, vy, n) in ((23, 9, -1.4, -0.9, 9), (26, 8, 1.6, -0.8, 10), (24, 6, 0.5, -1.1, 6)):
        x, y = x0, y0
        for i in range(n):
            x += vx; vy += 0.22; y += vy
            g.set(x, y, '#D0663F' if i > n - 4 else '#7A2A18')
        g.set(x, y, '#FFE08A'); g.set(x + 1, y, '#F2A23A'); g.set(x, y + 1, '#F2A23A'); g.set(x + 1, y + 1, '#D0663F')
    return g

def pool_basin(g, cx, cy, rx, ry, rnd, water, deep, hi):
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            v = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if v <= 1: g.set(x, y, deep if v < 0.45 and dither(0.6, x, y) else water)
            elif v <= 1.35: g.set(x, y, '#1F2628')

def rocks(g, y0, rnd, cols):
    for y in range(y0, g.h):
        for x in range(g.w):
            n = math.sin(x * 0.7 + y * 0.3) + math.sin(x * 0.23 - y * 0.9) + rnd.random() * 0.6
            g.set(x, y, cols[0] if n > 1.1 else (cols[1] if n > -0.4 else cols[2]))

def tidepool_front():
    rnd = random.Random(7); g = Grid(48, 46, '#2E3B4A')
    bands(g, 0, 16, ['#24303E', '#3E5262', '#7A8E98', '#C9B8A0'])
    for y in range(16, 24):
        for x in range(48): g.set(x, y, '#3E6A7A' if dither((y - 16) / 10, x, y) else '#4F7E8C')
    for x in range(48): g.set(x, 16, '#A9C4CC')
    for _ in range(18): g.set(rnd.randrange(48), rnd.randrange(17, 23), '#7FA7B5')
    for x in range(34, 41): g.set(x, 15, '#2A3236')
    for x in range(36, 39): g.set(x, 14, '#2A3236')
    # shore rocks with a ragged top edge
    for x in range(48):
        top = 23 + int(1.6 * math.sin(x * 0.5) + rnd.random() * 1.5)
        for y in range(top, 46): g.set(x, y, '#3A4244')
    rocks(g, 26, rnd, ('#5A6466', '#3A4244', '#2C3335'))
    for x in range(48):
        top = 23 + int(1.6 * math.sin(x * 0.5))
        g.set(x, top, '#6E7A7C')
    pool_basin(g, 24, 34, 15, 6.2, rnd, '#3F8A96', '#2F6A78', '#A9D2D8')
    for (x, y) in ((18, 32), (19, 32), (27, 31), (28, 31), (31, 35), (22, 37)): g.set(x, y, '#A9D2D8')
    # starfish, anemone, weed, barnacles
    for (dx, dy) in ((0, 0), (-1, 0), (1, 0), (0, -1), (-1, 1), (1, 1)): g.set(16 + dx, 35 + dy, '#D0663F')
    g.set(16, 35, '#E08A4A')
    for (dx, dy) in ((0, 0), (1, 0), (0, -1), (1, -1)): g.set(31 + dx, 37 + dy, '#C06A8A')
    g.set(31, 35, '#E08AA8')
    for x in (10, 11, 37, 38, 39):
        g.set(x, 33, '#4A7A4A'); g.set(x, 32 + (x % 2), '#5E9A5A')
    for _ in range(26):
        x, y = rnd.randrange(48), rnd.randrange(27, 46)
        if g.get(x, y) in ('#3A4244', '#2C3335', '#5A6466'): g.set(x, y, '#8A9496')
    return g

def tidepool_back():
    rnd = random.Random(9); g = Grid(48, 31, '#3A4248')
    bands(g, 0, 12, ['#2E363C', '#3E484E', '#5A646A'])
    for y in range(12, 16):
        for x in range(48): g.set(x, y, '#3A5A64')
    for x in range(48): g.set(x, 12, '#7A949C')
    for x in range(48):
        top = 15 + int(1.3 * math.sin(x * 0.5) + rnd.random())
        for y in range(top, 31): g.set(x, y, '#323A3C')
    rocks(g, 17, rnd, ('#4E585A', '#323A3C', '#262C2E'))
    pool_basin(g, 24, 23, 16, 5.2, rnd, '#3A7480', '#2C5C66', '#A9D2D8')
    for (cx, cy, r) in ((19, 23, 2.2), (28, 22, 3.0), (25, 25, 1.4)):
        for a in range(0, 360, 30):
            x = cx + math.cos(math.radians(a)) * r * 1.6; y = cy + math.sin(math.radians(a)) * r * 0.6
            if g.get(int(round(x)), int(round(y))) in ('#3A7480', '#2C5C66'): g.set(x, y, '#A9D2D8')
    for i in range(34):
        x, y = rnd.randrange(-4, 48), rnd.randrange(0, 29)
        g.set(x, y, '#8C9AA2'); g.set(x - 1, y + 1, '#6E7C84')
    return g

ART = {('volcano', 'front'): volcano_front, ('volcano', 'back'): volcano_back,
       ('tidepool', 'front'): tidepool_front, ('tidepool', 'back'): tidepool_back}
def art(key, side, W, H):
    return ART[(key, side)]().svg(W, H)
