#!/usr/bin/env python3
"""Third batch of overworld sketches, 65-96, tuned to Cam's notes on the second batch:
shapes in the spirit of 60 (broad, lopsided, moderately ragged coasts, two or three mountain chains),
more open sea and islands to sail between, no sprinkled ponds: every enclosed puddle is filled in and
each map gets only a handful of deliberate lakes, none of them huge."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import distance_transform_edt, map_coordinates, label
import gen_overworld as g
from gen_batch2 import lopsided

g.MEANDER = False
W, H, NX, NY = g.W, g.H, g.NX, g.NY
noise, ridge, meander, rough, blob = g.noise, g.ridge_line, g.meander, g.rough, g.blob
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 30)
YY, XX = np.mgrid[0:H, 0:W]


def shape(r, seed):
    kind = r.choices(["one", "two", "edge", "big_and_bits", "isles", "many"], [8, 4, 4, 5, 4, 2])[0]
    f = np.full((H, W), -1.0)
    if kind == "one":
        rot = r.choice([r.uniform(-0.5, 0.5), r.uniform(-0.5, 0.5), r.uniform(0, 3.1)])
        f = lopsided(r, r.uniform(0.38, 0.62), r.uniform(0.4, 0.6), r.uniform(0.34, 0.44), r.uniform(1.3, 2.0), rot)
        for _ in range(r.randint(1, 3)):
            f = np.maximum(f, lopsided(r, r.uniform(0.1, 0.9), r.uniform(0.1, 0.9), r.uniform(0.04, 0.1), r.uniform(1, 2.2), r.uniform(0, 3.1)) * 0.8)
        land = r.uniform(0.38, 0.52)
    elif kind == "two":
        for _ in range(2):
            f = np.maximum(f, lopsided(r, r.uniform(0.18, 0.82), r.uniform(0.25, 0.75), r.uniform(0.18, 0.3), r.uniform(1.1, 2.0), r.uniform(0, 3.1)))
        for _ in range(r.randint(1, 3)):
            f = np.maximum(f, lopsided(r, r.uniform(0.1, 0.9), r.uniform(0.1, 0.9), r.uniform(0.03, 0.08), 1.3, r.uniform(0, 3.1)) * 0.8)
        land = r.uniform(0.32, 0.46)
    elif kind == "edge":
        side = r.choice("lrtb"); off = r.uniform(0.0, 0.14)
        cx, cy = {"l": (off, r.uniform(0.3, 0.7)), "r": (1 - off, r.uniform(0.3, 0.7)), "t": (r.uniform(0.3, 0.7), off), "b": (r.uniform(0.3, 0.7), 1 - off)}[side]
        f = lopsided(r, cx, cy, r.uniform(0.45, 0.6), r.uniform(1.0, 1.6), r.uniform(0, 3.1))
        for _ in range(r.randint(2, 4)):
            f = np.maximum(f, lopsided(r, r.uniform(0.1, 0.9), r.uniform(0.1, 0.9), r.uniform(0.04, 0.11), r.uniform(1, 2), r.uniform(0, 3.1)) * 0.85)
        land = r.uniform(0.36, 0.5)
    elif kind == "big_and_bits":
        f = lopsided(r, r.uniform(0.32, 0.68), r.uniform(0.35, 0.65), r.uniform(0.26, 0.34), r.uniform(1.2, 1.9), r.uniform(-0.6, 0.6))
        for _ in range(r.randint(5, 9)):
            f = np.maximum(f, lopsided(r, r.uniform(0.05, 0.95), r.uniform(0.06, 0.94), r.uniform(0.03, 0.08), r.uniform(1, 2.4), r.uniform(0, 3.1)) * 0.9)
        land = r.uniform(0.34, 0.46)
    elif kind == "isles":
        pts = []
        while len(pts) < r.randint(5, 8):
            p = (r.uniform(0.1, 0.9), r.uniform(0.12, 0.88))
            if all(math.hypot(p[0] - a, (p[1] - b) * H / W) > 0.17 for a, b in pts):
                pts.append(p)
        for (x, y) in pts:
            f = np.maximum(f, lopsided(r, x, y, r.uniform(0.07, 0.15), r.uniform(1, 2), r.uniform(0, 3.1)))
        land = r.uniform(0.26, 0.36)
    else:
        for _ in range(r.randint(3, 4)):
            f = np.maximum(f, lopsided(r, r.uniform(0.12, 0.88), r.uniform(0.15, 0.85), r.uniform(0.12, 0.22), r.uniform(1, 2), r.uniform(0, 3.1)))
        land = r.uniform(0.34, 0.46)
    grain = r.uniform(0.8, 1.3)
    f = f + r.uniform(0.28, 0.45) * (noise(seed + 1, 130 * grain, 4) - 0.5) * 2 + r.uniform(0.13, 0.22) * (noise(seed + 2, 34 * grain, 3) - 0.5) * 2 + 0.05 * (noise(seed + 10, 14, 2) - 0.5) * 2
    amp = r.uniform(40, 90); a2 = r.uniform(8, 18)
    wx = (noise(seed + 3, 180, 3) - 0.5) * 2 * amp + (noise(seed + 8, 55, 3) - 0.5) * 2 * a2
    wy = (noise(seed + 4, 180, 3) - 0.5) * 2 * amp + (noise(seed + 9, 55, 3) - 0.5) * 2 * a2
    f = map_coordinates(f, [np.clip(YY + wy, 0, H - 1), np.clip(XX + wx, 0, W - 1)], order=1)
    return kind, f > np.quantile(f, 1 - land)


def tidy(land, r, seed, kind):
    # fill every enclosed puddle, then drop specks of island too small to sail to
    water_lab, n = label(~land)
    edge = set(np.unique(np.concatenate([water_lab[0], water_lab[-1], water_lab[:, 0], water_lab[:, -1]])))
    for k in range(1, n + 1):
        if k not in edge:
            land[water_lab == k] = True
    land_lab, n = label(land)
    sizes = np.bincount(land_lab.ravel())
    for k in range(1, n + 1):
        if sizes[k] < 60:
            land[land_lab == k] = False
    # a handful of deliberate lakes, well inland and apart, none huge
    want = r.choice([0, 1, 2]) if kind == "isles" else r.choice([2, 3, 3, 4, 4, 5])
    dist = distance_transform_edt(np.pad(land, 1))[1:-1, 1:-1]
    lakes = np.zeros_like(land); placed = []
    ys, xs = np.nonzero(dist > 45)
    order = list(range(len(xs))); r.shuffle(order)
    for i in order:
        if len(placed) >= want:
            break
        x, y = xs[i], ys[i]
        if any(math.hypot(x - a, y - b) < 110 for a, b in placed):
            continue
        rad = r.uniform(0.014, 0.03) if r.random() < 0.7 else r.uniform(0.032, 0.046)
        lk = rough(blob(x / W, y / H, rad, rad * r.uniform(0.35, 0.8), r.uniform(0, 3.1)), seed + 50 + len(placed), 0.5, 0.4, 28, 9) > 0
        if (lk & (dist < 14)).any():
            continue
        lakes |= lk; placed.append((x, y))
    return land & ~lakes


def finish(num, land, seed, r):
    rng = np.random.default_rng(seed)
    dist = distance_transform_edt(np.pad(land, 1))[1:-1, 1:-1]
    e = 0.42 * noise(seed + 3, 110) + 0.28 * np.clip(dist / 110, 0, 1)
    ys, xs = np.nonzero(dist > 30)
    chains = r.choice([2, 2, 3])
    starts = []
    for k in range(chains if len(xs) else 0):
        for _ in range(20):
            i = rng.integers(len(xs)); x0, y0 = xs[i] / W, ys[i] / H
            if all(math.hypot(x0 - a, (y0 - b) * H / W) > 0.22 for a, b in starts):
                break
        starts.append((x0, y0))
        ang = r.uniform(0, math.pi); L = r.uniform(0.16, 0.3)
        pts = [(x0 - math.cos(ang) * L, y0 - math.sin(ang) * L * W / H), (x0, y0),
               (x0 + math.cos(ang + r.uniform(-0.5, 0.5)) * L * 0.8, y0 + math.sin(ang + r.uniform(-0.5, 0.5)) * L * 0.8 * W / H)]
        e = e + 0.5 * ridge(meander(pts, seed + k, 0.02), 0.05) * (dist > 6)
    elev = np.clip(e, 0, 1)
    riv = []
    cand = list(zip(*np.nonzero((elev > 0.55) & (dist > 30)))); r.shuffle(cand)
    for (y, x) in cand[:24]:
        if len(riv) >= r.choice([1, 2, 3]):
            break
        if any(math.hypot(x - p[0][0] * W, y - p[0][1] * H) < 120 for p in riv):
            continue
        path = [(x, y)]; off_map = False
        for _ in range(400):
            best = None
            for dx, dy in ((6, 0), (-6, 0), (0, 6), (0, -6), (4, 4), (-4, 4), (4, -4), (-4, -4)):
                nx, ny = path[-1][0] + dx, path[-1][1] + dy
                if 0 <= nx < W and 0 <= ny < H:
                    sc = dist[ny, nx] + r.uniform(0, 2.5)
                    if best is None or sc < best[0]:
                        best = (sc, nx, ny)
            path.append((best[1], best[2]))
            if not land[best[2], best[1]]:
                break
            if best[1] < 4 or best[1] > W - 5 or best[2] < 4 or best[2] > H - 5:
                off_map = True; break
        if len(path) > 14 and not off_map:
            P = np.array(path, float); k = 7
            sm = np.array([P[max(0, i - k):i + k + 1].mean(0) for i in range(len(P))]); sm[0], sm[-1] = P[0], P[-1]
            riv.append([(px / W, py / H) for px, py in sm[::4]] + [(P[-1][0] / W, P[-1][1] / H)])
    name = f"d{num:02d}"
    g.render(name, np.where(land, 1.0, -1.0), elev, seed, 0, {}, riv)
    im = Image.open(g.OUT / f"ow_{name}.png").convert("RGB"); d = ImageDraw.Draw(im)
    d.ellipse((14, 14, 70, 70), fill=(241, 232, 210), outline=(58, 46, 34), width=3)
    t = str(num); bw = d.textlength(t, font=FONT)
    d.text((42 - bw / 2, 24), t, fill=(58, 46, 34), font=FONT)
    im.resize((636, 398), Image.LANCZOS).save(g.OUT / f"{name}.png")


if __name__ == "__main__":
    nums = list(range(65, 97))
    for n in nums:
        seed = 9000 + n * 37; r = random.Random(seed)
        kind, land = shape(r, seed)
        land = tidy(land, r, seed, kind)
        finish(n, land, seed, r)
    sheet = Image.new("RGB", (318 * 4 + 30, 199 * 8 + 70), (41, 34, 27))
    for i, n in enumerate(nums):
        sheet.paste(Image.open(g.OUT / f"d{n:02d}.png").resize((318, 199)), ((i % 4) * 328, (i // 4) * 209))
    sheet.save(g.OUT / "batch3_sheet.png")
