#!/usr/bin/env python3
"""A larger batch of overworld sketches for inspiration: 24 natural shapes and 8 that look made.
Same parchment-and-ink renderer; mountains, rivers (traced downhill to the sea) and lakes; a number in each corner."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import distance_transform_edt
import gen_overworld as g
g.MEANDER = False

W, H, NX, NY = g.W, g.H, g.NX, g.NY
blob, rough, ridge, noise, meander = g.blob, g.rough, g.ridge_line, g.noise, g.meander
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 30)


def rect(cx, cy, rx, ry, rot=0.0, p=4.0):
    c, s = math.cos(rot), math.sin(rot)
    dx, dy = (NX - cx), (NY - cy) * H / W
    u = np.abs((dx * c + dy * s) / rx); v = np.abs((-dx * s + dy * c) / ry)
    return 1 - (u ** p + v ** p) ** (1 / p)


def U(*fields):
    return np.maximum.reduce(fields)


def finish(num, sh, seed, ridges=1, rivers=2, lakes=None, rim=None):
    rng = np.random.default_rng(seed); r2 = random.Random(seed)
    land = sh > 0
    dist = distance_transform_edt(land)
    e = 0.42 * noise(seed + 3, 110) + 0.28 * np.clip(dist / 110, 0, 1)
    ys, xs = np.nonzero(dist > 28)
    for _ in range(ridges if len(xs) else 0):
        k = rng.integers(len(xs)); x0, y0 = xs[k] / W, ys[k] / H
        ang = r2.uniform(0, math.pi); L = r2.uniform(0.12, 0.3)
        pts = [(x0 - math.cos(ang) * L, y0 - math.sin(ang) * L * W / H), (x0, y0), (x0 + math.cos(ang) * L, y0 + math.sin(ang) * L * W / H)]
        e = e + 0.5 * ridge(meander(pts, seed + _, 0.02), 0.05)
    if rim is not None:
        e = e + 0.55 * rim
    elev = np.clip(e, 0, 1)
    lk = None
    if lakes:
        lk = (noise(seed + 7, 34, 3) > lakes) & (dist > 18)
    riv = []
    cand = list(zip(*np.nonzero((elev > 0.55) & (dist > 30))))
    r2.shuffle(cand)
    for (y, x) in cand[: rivers * 6]:
        if len(riv) >= rivers:
            break
        if any(math.hypot(x - p[0][0] * W, y - p[0][1] * H) < 120 for p in riv):
            continue
        path = [(x, y)]
        for _ in range(400):
            best = None
            for dx, dy in ((6, 0), (-6, 0), (0, 6), (0, -6), (4, 4), (-4, 4), (4, -4), (-4, -4)):
                nx, ny = path[-1][0] + dx, path[-1][1] + dy
                if not (0 <= nx < W and 0 <= ny < H):
                    continue
                score = dist[ny, nx] + r2.uniform(0, 2.5)
                if best is None or score < best[0]:
                    best = (score, nx, ny)
            path.append((best[1], best[2]))
            if not land[best[2], best[1]] or (lk is not None and lk[best[2], best[1]]):
                break
        if len(path) > 14:
            P = np.array(path, float); k = 7
            sm = np.array([P[max(0, i - k):i + k + 1].mean(0) for i in range(len(P))])
            sm[0], sm[-1] = P[0], P[-1]
            riv.append([(px / W, py / H) for px, py in sm[::4]] + [(P[-1][0] / W, P[-1][1] / H)])
    name = f"b{num:02d}"
    g.render(name, sh, elev, seed, 0, {}, riv, lakes=lk)
    im = Image.open(g.OUT / f"ow_{name}.png").convert("RGB"); d = ImageDraw.Draw(im)
    d.ellipse((14, 14, 70, 70), fill=(241, 232, 210), outline=(58, 46, 34), width=3)
    t = str(num); bw = d.textlength(t, font=FONT)
    d.text((42 - bw / 2, 24), t, fill=(58, 46, 34), font=FONT)
    im.resize((636, 398), Image.LANCZOS).save(g.OUT / f"{name}.png")


MAPS = []


def m(f):
    MAPS.append(f); return f


# ---- grown ----
@m
def _(s): return rough(blob(0.5, 0.5, 0.34, 0.32), s), dict(ridges=2, rivers=3)
@m
def _(s): return np.minimum(rough(blob(0.48, 0.5, 0.4, 0.36), s), -rough(blob(0.72, 0.62, 0.15, 0.12), s + 1, 0.3, 0.25, 60, 20)), dict(ridges=2, rivers=3)
@m
def _(s):
    ch = ridge(meander([(0.5, 0.0), (0.46, 0.4), (0.54, 0.7), (0.5, 1.0)], s, 0.03), 0.07) > 0.05
    return np.where(ch, -0.4, U(rough(blob(0.25, 0.5, 0.2, 0.36, 0.2), s), rough(blob(0.76, 0.5, 0.2, 0.34, -0.2), s + 1))), dict(ridges=2, rivers=3)
@m
def _(s): return U(rough(blob(0.3, 0.34, 0.24, 0.2, 0.4), s), rough(blob(0.72, 0.68, 0.22, 0.2, -0.3), s + 1)), dict(ridges=2, rivers=2)
@m
def _(s): return U(rough(blob(0.22, 0.32, 0.16, 0.18), s), rough(blob(0.72, 0.28, 0.2, 0.14), s + 1), rough(blob(0.5, 0.76, 0.22, 0.14, 0.2), s + 2)), dict(ridges=3, rivers=3)
@m
def _(s): return (noise(s, 70, 5) - 0.56) * 3 + 0.3 * blob(0.5, 0.5, 0.6, 0.55) + 0.2 * (noise(s + 1, 28, 3) - 0.5), dict(ridges=2, rivers=1)
@m
def _(s): return (noise(s, 55, 5) - 0.64) * 3 + 0.25 * blob(0.5, 0.5, 0.6, 0.55) + 0.25 * (noise(s + 1, 22, 3) - 0.5), dict(ridges=1, rivers=0)
@m
def _(s):
    f = np.full((H, W), -1.0)
    for i in range(9):
        t = i / 8; x = 0.1 + 0.8 * t; y = 0.25 + 0.5 * math.sin(t * math.pi) ** 0.8
        r = 0.05 + 0.04 * math.sin(t * math.pi)
        f = np.maximum(f, rough(blob(x, 1 - y + 0.15, r, r * 0.8, t), s + i, 0.35, 0.3, 50, 16))
    return f, dict(ridges=2, rivers=1)
@m
def _(s):
    f = rough(blob(0.45, 0.5, 0.26, 0.3, 0.3), s)
    for i, (x, y, r) in enumerate(((0.82, 0.22, 0.05), (0.85, 0.6, 0.06), (0.12, 0.82, 0.05), (0.15, 0.15, 0.04), (0.7, 0.88, 0.04))):
        f = U(f, rough(blob(x, y, r, r * 0.8), s + 10 + i, 0.35, 0.3, 40, 14))
    return f, dict(ridges=2, rivers=3)
@m
def _(s):
    return U(rough(blob(0.28, 0.42, 0.2, 0.26), s), rough(blob(0.74, 0.58, 0.19, 0.24), s + 1),
             (0.035 - (1 - ridge(meander([(0.4, 0.5), (0.5, 0.52), (0.62, 0.54)], s, 0.02), 1.0))) * 4), dict(ridges=2, rivers=2)
@m
def _(s): return np.minimum(rough(blob(0.5, 0.5, 0.45, 0.42), s, 0.3, 0.2), -rough(blob(0.5, 0.52, 0.25, 0.21, 0.4), s + 1, 0.3, 0.2)), dict(ridges=2, rivers=3)
@m
def _(s):
    f = np.minimum(rough(blob(0.5, 0.5, 0.45, 0.42), s, 0.3, 0.2), -rough(blob(0.48, 0.5, 0.24, 0.2, -0.3), s + 1, 0.3, 0.2))
    st = (ridge(meander([(0.6, 0.62), (0.76, 0.78), (0.92, 0.96)], s, 0.03), 0.05) + 0.4 * (noise(s + 2, 30, 3) - 0.5)) > 0.3
    return np.where(st, -0.3, f), dict(ridges=2, rivers=2)
@m
def _(s): return np.minimum(rough(blob(0.46, 0.54, 0.44, 0.42), s, 0.3, 0.2), -rough(blob(0.66, 0.38, 0.32, 0.27), s + 1, 0.25, 0.2, 90, 30)), dict(ridges=2, rivers=2)
@m
def _(s):
    f = blob(0.45, 0.5, 0.2, 0.22)
    for k, pts in enumerate(([(0.48, 0.4), (0.66, 0.26), (0.86, 0.18)], [(0.52, 0.56), (0.7, 0.68), (0.84, 0.88)], [(0.4, 0.62), (0.34, 0.8), (0.3, 0.96)],
                              [(0.38, 0.42), (0.24, 0.26), (0.1, 0.18)], [(0.32, 0.56), (0.16, 0.62), (0.04, 0.7)], [(0.5, 0.36), (0.52, 0.16), (0.5, 0.04)])):
        f = U(f, (0.04 - (1 - ridge(meander(pts, s + k, 0.02), 1.0))) * 3)
    return rough(f, s, 0.07, 0.06, 60, 20), dict(ridges=1, rivers=2)
@m
def _(s):
    f = rough(blob(0.5, 0.5, 0.42, 0.38), s, 0.3, 0.2)
    cuts = U(ridge(meander([(0.34, 0.0), (0.44, 0.5), (0.38, 1.0)], s, 0.03), 0.05), ridge(meander([(0.44, 0.5), (1.0, 0.4)], s + 1, 0.03), 0.05),
             ridge(meander([(0.0, 0.62), (0.44, 0.5)], s + 2, 0.03), 0.04))
    return np.where(cuts * (0.6 + 0.9 * noise(s + 3, 40, 3)) > 0.62, -0.3, f), dict(ridges=3, rivers=3)
@m
def _(s):
    f = rough(blob(0.5, 0.5, 0.46, 0.24, 0.3), s)
    return f, dict(ridges=0, rivers=4, rim=ridge(meander([(0.1, 0.72), (0.5, 0.5), (0.9, 0.26)], s, 0.02), 0.06))
@m
def _(s): return rough(blob(0.5, 0.5, 0.52, 0.1, 0.55), s, 0.25, 0.18), dict(ridges=1, rivers=2)
@m
def _(s): return rough(blob(0.5, 0.5, 0.42, 0.38), s), dict(ridges=2, rivers=3, lakes=0.66)
@m
def _(s):
    f = rough(blob(0.42, 0.5, 0.4, 0.4), s, 0.3, 0.2)
    for i in range(7):
        y = 0.12 + i * 0.12
        pts = meander([(0.9, y), (0.72, y + 0.02), (0.55, y - 0.02)], s + i, 0.025)
        f = np.where(ridge(pts, 0.03) * (0.5 + noise(s + 20 + i, 20, 3)) > 0.62, -1, f)
    return f, dict(ridges=2, rivers=2)
@m
def _(s):
    f = rough(blob(0.5, 0.5, 0.46, 0.42), s, 0.3, 0.2)
    rift = ridge(meander([(0.92, 0.12), (0.68, 0.38), (0.5, 0.56), (0.36, 0.7)], s, 0.02), 0.06)
    return np.where(rift * (0.6 + 0.8 * noise(s + 1, 30, 3)) > 0.5, -0.4, f), dict(ridges=2, rivers=3)
@m
def _(s): return 0.5 - (NX - 0.6 - 0.2 * (noise(s, 70, 4) - 0.5) - 0.12 * (noise(s + 1, 18, 3) - 0.5)) - 0.5, dict(ridges=2, rivers=3)
@m
def _(s):
    f = 0.4 - 0 * NX
    return np.where((NX + 0.3 * NY) > 1.05 + 0.3 * (noise(s, 80, 4) - 0.5), -0.4, f), dict(ridges=2, rivers=4, lakes=0.7)
@m
def _(s):
    return U(rough(blob(0.36, 0.42, 0.3, 0.3), s), (0.05 - (1 - ridge(meander([(0.5, 0.55), (0.66, 0.72), (0.76, 0.92)], s, 0.03), 1.0))) * 3), dict(ridges=2, rivers=2)
@m
def _(s):
    f = np.full((H, W), -1.0)
    for i in range(14):
        a = i / 14 * 2 * math.pi; r = 0.06 if i % 3 == 0 else 0.035
        f = U(f, rough(blob(0.5 + 0.36 * math.cos(a), 0.5 + 0.36 * math.sin(a) * W / H * 0.62, r, r * 0.8, a), s + i, 0.35, 0.3, 40, 14))
    return f, dict(ridges=1, rivers=0)


# ---- made: as if laid down by the two players ----
@m
def _(s):
    half = rough(blob(0.26, 0.5, 0.2, 0.36), s)
    f = np.where(NX < 0.5, half, half[:, ::-1])
    return np.where(np.abs(NX - 0.5) < 0.025, -0.4, f), dict(ridges=2, rivers=2)
@m
def _(s):
    f = np.minimum(rough(blob(0.5, 0.5, 0.46, 0.43), s, 0.25, 0.18), -blob(0.5, 0.5, 0.3, 0.27))
    f = U(f, rough(blob(0.5, 0.5, 0.06, 0.06), s + 1, 0.3, 0.25, 40, 14))
    for i, (x, y) in enumerate(((0.5, 0.22), (0.72, 0.5), (0.5, 0.78), (0.28, 0.5))):
        f = U(f, rough(blob(x, y, 0.035, 0.035), s + 2 + i, 0.3, 0.25, 30, 10))
    return f, dict(ridges=0, rivers=2)
@m
def _(s):
    f = np.minimum(rough(blob(0.5, 0.5, 0.44, 0.4), s), -rough(blob(0.5, 0.5, 0.2, 0.2), s + 1, 0.12, 0.12, 60, 20))
    rim = np.clip(1 - np.abs(np.hypot(NX - 0.5, (NY - 0.5) * H / W) - 0.24) / 0.05, 0, 1)
    return f, dict(ridges=0, rivers=3, rim=rim)
@m
def _(s):
    f = rough(blob(0.5, 0.5, 0.46, 0.44), s, 0.25, 0.2)
    cross = U(ridge(meander([(0.5, 0.0), (0.5, 1.0)], s, 0.02), 0.045), ridge(meander([(0.0, 0.5), (1.0, 0.5)], s + 1, 0.02), 0.045))
    return np.where(cross > 0.05, -0.4, f), dict(ridges=4, rivers=2)
@m
def _(s):
    r2 = random.Random(s); cells = {(0, 0)}
    while len(cells) < 22:
        cx, cy = r2.choice(sorted(cells)); dx, dy = r2.choice(((1, 0), (-1, 0), (0, 1), (0, -1)))
        if abs(cx + dx) <= 4 and abs(cy + dy) <= 2:
            cells.add((cx + dx, cy + dy))
    f = np.full((H, W), -1.0)
    for cx, cy in cells:
        f = U(f, rect(0.5 + cx * 0.1, 0.5 + cy * 0.16, 0.048, 0.048, 0.0, 6))
    return rough(f, s, 0.08, 0.1, 40, 12), dict(ridges=2, rivers=2)
@m
def _(s):
    f = np.full((H, W), -1.0)
    for i in range(20):
        t = 1.2 + i * 0.55; r = 0.03 * t
        x = 0.5 + r * math.cos(t); y = 0.5 + r * math.sin(t) * W / H * 0.62
        rr = 0.018 + 0.0022 * i
        f = U(f, rough(blob(x, y, rr, rr * 0.8, t), s + i, 0.3, 0.3, 40, 14))
    return f, dict(ridges=1, rivers=0)
@m
def _(s):
    ring1 = np.minimum(rough(blob(0.5, 0.5, 0.45, 0.42), s, 0.22, 0.18), -rough(blob(0.5, 0.5, 0.32, 0.29), s + 1, 0.18, 0.15))
    ring2 = np.minimum(rough(blob(0.5, 0.5, 0.2, 0.18), s + 2, 0.2, 0.18), -rough(blob(0.5, 0.5, 0.12, 0.11), s + 3, 0.18, 0.15))
    core = rough(blob(0.5, 0.5, 0.045, 0.045), s + 4, 0.3, 0.25, 40, 14)
    return U(ring1, ring2, core), dict(ridges=1, rivers=1)
@m
def _(s):
    r2 = random.Random(s); f = np.full((H, W), -1.0); placed = []
    while len(placed) < 12:
        x, y = r2.uniform(0.12, 0.88), r2.uniform(0.15, 0.85)
        if all(math.hypot(x - a, (y - b) * H / W) > 0.13 for a, b in placed):
            placed.append((x, y))
            f = U(f, rect(x, y, 0.055, 0.038, r2.uniform(-0.9, 0.9), 5))
    return rough(f, s, 0.1, 0.12, 40, 12), dict(ridges=2, rivers=0)


if __name__ == "__main__":
    for i, fn in enumerate(MAPS, 1):
        sh, kw = fn(1000 + i * 17)
        finish(i, sh, 1000 + i * 17, **kw)
    sheet = Image.new("RGB", (318 * 4 + 30, 199 * 8 + 70), (41, 34, 27))
    for i in range(len(MAPS)):
        sheet.paste(Image.open(g.OUT / f"b{i + 1:02d}.png").resize((318, 199)), ((i % 4) * 328, (i // 4) * 209))
    sheet.save(g.OUT / "batch_sheet.png")
    print(len(MAPS), "maps")
