#!/usr/bin/env python3
"""Second batch of overworld sketches, 33-64: grown, lopsided shapes only.
Lopsided blobs (radius varies with angle), off-centre placement, land running off the frame,
domain-warped coasts and a sea level picked per map to hit a random share of land."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import distance_transform_edt, map_coordinates
import gen_overworld as g

g.MEANDER = False
W, H, NX, NY = g.W, g.H, g.NX, g.NY
noise, ridge, meander = g.noise, g.ridge_line, g.meander
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 30)
YY, XX = np.mgrid[0:H, 0:W]


def lopsided(r, cx, cy, r0, elong, rot):
    """a blob whose radius wobbles with angle, so no two sides match"""
    dx, dy = (NX - cx), (NY - cy) * H / W
    c, s = math.cos(rot), math.sin(rot)
    u = (dx * c + dy * s); v = (-dx * s + dy * c) * elong
    th = np.arctan2(v, u); d = np.hypot(u, v)
    rad = r0 * (1 + r.uniform(0.1, 0.35) * np.cos(th - r.uniform(0, 6.3)) + r.uniform(0.05, 0.25) * np.cos(2 * th - r.uniform(0, 6.3))
                + r.uniform(0.0, 0.15) * np.cos(3 * th - r.uniform(0, 6.3)) + r.uniform(0.0, 0.1) * np.cos(4 * th - r.uniform(0, 6.3))
                + r.uniform(0.0, 0.07) * np.cos(5 * th - r.uniform(0, 6.3)))
    return (1 - d / rad) / math.sqrt(elong)  # soften the steep long sides so noise can still bend them


def make(seed):
    r = random.Random(seed)
    kind = r.choices(["one", "two", "many", "edge", "scatter", "big_and_bits"], [5, 4, 3, 4, 2, 3])[0]
    f = np.full((H, W), -1.0)
    if kind == "one":
        f = lopsided(r, r.uniform(0.35, 0.65), r.uniform(0.35, 0.65), r.uniform(0.28, 0.4), r.uniform(1.0, 1.7), r.uniform(0, 3.1))
        for _ in range(r.randint(1, 3)):
            f = np.maximum(f, lopsided(r, r.uniform(0.1, 0.9), r.uniform(0.1, 0.9), r.uniform(0.08, 0.2), r.uniform(1, 3), r.uniform(0, 3.1)) * r.uniform(0.6, 1))
        land = r.uniform(0.42, 0.62)
    elif kind == "two":
        for _ in range(2):
            f = np.maximum(f, lopsided(r, r.uniform(0.15, 0.85), r.uniform(0.2, 0.8), r.uniform(0.16, 0.32), r.uniform(1, 2.5), r.uniform(0, 3.1)))
        f = np.maximum(f, lopsided(r, r.uniform(0.1, 0.9), r.uniform(0.1, 0.9), r.uniform(0.05, 0.1), 1.2, 0) * 0.8)
        land = r.uniform(0.35, 0.55)
    elif kind == "many":
        for _ in range(r.randint(3, 5)):
            f = np.maximum(f, lopsided(r, r.uniform(0.08, 0.92), r.uniform(0.1, 0.9), r.uniform(0.1, 0.24), r.uniform(1, 2.5), r.uniform(0, 3.1)))
        land = r.uniform(0.35, 0.5)
    elif kind == "edge":
        side = r.choice("lrtb"); off = r.uniform(-0.05, 0.12)
        cx, cy = {"l": (off, r.uniform(0.3, 0.7)), "r": (1 - off, r.uniform(0.3, 0.7)), "t": (r.uniform(0.3, 0.7), off), "b": (r.uniform(0.3, 0.7), 1 - off)}[side]
        f = lopsided(r, cx, cy, r.uniform(0.45, 0.65), r.uniform(0.8, 1.6), r.uniform(0, 3.1))
        for _ in range(r.randint(1, 3)):
            f = np.maximum(f, lopsided(r, r.uniform(0.1, 0.9), r.uniform(0.1, 0.9), r.uniform(0.05, 0.14), r.uniform(1, 2), r.uniform(0, 3.1)) * 0.85)
        land = r.uniform(0.4, 0.6)
    elif kind == "scatter":
        f = 0.25 * lopsided(r, r.uniform(0.4, 0.6), r.uniform(0.4, 0.6), 0.55, 1.2, r.uniform(0, 3.1))
        land = r.uniform(0.22, 0.36)
    else:
        f = lopsided(r, r.uniform(0.3, 0.7), r.uniform(0.3, 0.7), r.uniform(0.24, 0.34), r.uniform(1, 2), r.uniform(0, 3.1))
        for _ in range(r.randint(4, 8)):
            f = np.maximum(f, lopsided(r, r.uniform(0.05, 0.95), r.uniform(0.05, 0.95), r.uniform(0.03, 0.08), r.uniform(1, 2.5), r.uniform(0, 3.1)) * 0.9)
        land = r.uniform(0.35, 0.5)
    # noise on top, at a strength and grain that varies per map
    grain = r.uniform(0.6, 1.4)
    f = f + r.uniform(0.25, 0.55) * (noise(seed + 1, 130 * grain, 4) - 0.5) * 2 + r.uniform(0.1, 0.3) * (noise(seed + 2, 34 * grain, 3) - 0.5) * 2
    if kind == "scatter":
        f = f + 0.6 * (noise(seed + 5, 60, 4) - 0.5) * 2
    # domain warp: drag the whole field sideways along noise, which bends coasts and breaks symmetry
    amp = r.uniform(45, 110)
    wx = (noise(seed + 3, 180, 3) - 0.5) * 2 * amp; wy = (noise(seed + 4, 180, 3) - 0.5) * 2 * amp
    a2 = r.uniform(12, 28)
    wx = wx + (noise(seed + 8, 55, 3) - 0.5) * 2 * a2; wy = wy + (noise(seed + 9, 55, 3) - 0.5) * 2 * a2
    f = map_coordinates(f, [np.clip(YY + wy, 0, H - 1), np.clip(XX + wx, 0, W - 1)], order=1)
    # sometimes cut a rift or a long bay into it
    if False:
        x0, y0 = r.uniform(0.25, 0.75), r.uniform(0.25, 0.75); a = r.uniform(0, 6.3); L = r.uniform(0.12, 0.25); b = a + r.uniform(-1.0, 1.0)
        x1, y1 = x0 + math.cos(a) * L, y0 + math.sin(a) * L * W / H
        pts = meander([(x0, y0), (x1, y1), (x1 + math.cos(b) * L * 0.8, y1 + math.sin(b) * L * 0.8 * W / H)], seed + 6, 0.04)
        f = np.where(ridge(pts, r.uniform(0.015, 0.028)) * (0.5 + noise(seed + 7, 24, 3)) > 0.6, f.min(), f)
    thr = np.quantile(f, 1 - land)
    return f - thr, dict(ridges=r.randint(1, 3), rivers=r.randint(1, 4), lakes=(r.uniform(0.66, 0.72) if r.random() < 0.3 else None))


def finish(num, sh, seed, ridges=1, rivers=2, lakes=None):
    rng = np.random.default_rng(seed); r2 = random.Random(seed)
    land = sh > 0
    dist = distance_transform_edt(np.pad(land, 1))[1:-1, 1:-1]  # the frame counts as sea, so rivers can run off the map
    e = 0.42 * noise(seed + 3, 110) + 0.28 * np.clip(dist / 110, 0, 1)
    ys, xs = np.nonzero(dist > 28)
    for k in range(ridges if len(xs) else 0):
        i = rng.integers(len(xs)); x0, y0 = xs[i] / W, ys[i] / H
        ang = r2.uniform(0, math.pi); L = r2.uniform(0.12, 0.3)
        pts = [(x0 - math.cos(ang) * L, y0 - math.sin(ang) * L * W / H), (x0, y0), (x0 + math.cos(ang) * L * 0.7, y0 + math.sin(ang) * L * 0.7 * W / H)]
        e = e + 0.5 * ridge(meander(pts, seed + k, 0.02), 0.05)
    elev = np.clip(e, 0, 1)
    lk = (noise(seed + 7, 34, 3) > lakes) & (dist > 18) if lakes else None
    riv = []
    cand = list(zip(*np.nonzero((elev > 0.55) & (dist > 30)))); r2.shuffle(cand)
    for (y, x) in cand[: rivers * 6]:
        if len(riv) >= rivers:
            break
        if any(math.hypot(x - p[0][0] * W, y - p[0][1] * H) < 120 for p in riv):
            continue
        path = [(x, y)]; off_map = False
        for _ in range(400):
            best = None
            for dx, dy in ((6, 0), (-6, 0), (0, 6), (0, -6), (4, 4), (-4, 4), (4, -4), (-4, -4)):
                nx, ny = path[-1][0] + dx, path[-1][1] + dy
                if 0 <= nx < W and 0 <= ny < H:
                    sc = dist[ny, nx] + r2.uniform(0, 2.5)
                    if best is None or sc < best[0]:
                        best = (sc, nx, ny)
            path.append((best[1], best[2]))
            if not land[best[2], best[1]] or (lk is not None and lk[best[2], best[1]]):
                break
            if best[1] < 4 or best[1] > W - 5 or best[2] < 4 or best[2] > H - 5:
                off_map = True
                break
        if len(path) > 14 and not off_map:
            P = np.array(path, float); k = 7
            sm = np.array([P[max(0, i - k):i + k + 1].mean(0) for i in range(len(P))]); sm[0], sm[-1] = P[0], P[-1]
            riv.append([(px / W, py / H) for px, py in sm[::4]] + [(P[-1][0] / W, P[-1][1] / H)])
    name = f"c{num:02d}"
    g.render(name, sh, elev, seed, 0, {}, riv, lakes=lk)
    im = Image.open(g.OUT / f"ow_{name}.png").convert("RGB"); d = ImageDraw.Draw(im)
    d.ellipse((14, 14, 70, 70), fill=(241, 232, 210), outline=(58, 46, 34), width=3)
    t = str(num); bw = d.textlength(t, font=FONT)
    d.text((42 - bw / 2, 24), t, fill=(58, 46, 34), font=FONT)
    im.resize((636, 398), Image.LANCZOS).save(g.OUT / f"{name}.png")


if __name__ == "__main__":
    nums = list(range(33, 65))
    for n in nums:
        sh, kw = make(5000 + n * 31)
        finish(n, sh, 5000 + n * 31, **kw)
    sheet = Image.new("RGB", (318 * 4 + 30, 199 * 8 + 70), (41, 34, 27))
    for i, n in enumerate(nums):
        sheet.paste(Image.open(g.OUT / f"c{n:02d}.png").resize((318, 199)), ((i % 4) * 328, (i // 4) * 209))
    sheet.save(g.OUT / "batch2_sheet.png")
