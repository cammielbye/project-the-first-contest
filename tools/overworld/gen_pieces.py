#!/usr/bin/env python3
"""Overworld pieces: continent shapes, bodies of water, and ways to divide regions.
Uses the renderer in gen_overworld.py (no place dots, no seats) and adds dashed region borders."""
import math
import numpy as np
from PIL import Image, ImageDraw
import gen_overworld as g

W, H, NX, NY = g.W, g.H, g.NX, g.NY
blob, rough, ridge, noise = g.blob, g.rough, g.ridge_line, g.noise


def go(name, land, elev, seed, rivers=(), lakes=None):
    g.render(name, land, elev, seed, 0, {}, rivers, lakes=lakes)
    return (land > 0) & (~lakes if lakes is not None else True)


def elev_of(seed, ridges=(), w=0.07):
    e = 0.55 * noise(seed, 110)
    for r in ridges:
        e = e + 0.55 * ridge(r, w)
    return np.clip(e, 0, 1)


# ---- continent shapes ----
def shapes():
    go("p_compact", rough(blob(0.5, 0.5, 0.3, 0.32), 101), elev_of(102, [[(0.42, 0.32), (0.56, 0.6)]]), 101,
       [[(0.5, 0.48), (0.62, 0.6), (0.72, 0.72)]])
    go("p_long", rough(blob(0.5, 0.52, 0.5, 0.12, 0.45), 111, 0.3, 0.2), elev_of(112, [[(0.1, 0.8), (0.5, 0.52), (0.9, 0.22)]], 0.05), 111)
    cres = np.minimum(rough(blob(0.48, 0.54, 0.44, 0.42), 121, 0.3, 0.2), -rough(blob(0.64, 0.4, 0.3, 0.26), 125, 0.25, 0.2, 90, 30))
    go("p_crescent", cres, elev_of(122, [[(0.18, 0.4), (0.3, 0.8), (0.6, 0.88)]]), 121)
    br = blob(0.42, 0.5, 0.2, 0.22)
    for k, pts in enumerate(([(0.45, 0.4), (0.62, 0.28), (0.8, 0.2), (0.9, 0.22)], [(0.5, 0.55), (0.66, 0.62), (0.78, 0.74), (0.86, 0.86)],
                              [(0.4, 0.6), (0.38, 0.78), (0.44, 0.95)], [(0.36, 0.42), (0.22, 0.26), (0.12, 0.12)], [(0.3, 0.55), (0.16, 0.66), (0.06, 0.62)])):
        w = 0.045 - 0.005 * k
        br = np.maximum(br, (w - (1 - ridge(g.meander(pts, 140 + k, 0.02), 1.0))) * 3.0)
    br = rough(br, 131, 0.06, 0.05, 60, 20)
    go("p_branching", br, elev_of(133, [[(0.38, 0.4), (0.46, 0.6)]]), 131)
    ring = np.minimum(rough(blob(0.5, 0.5, 0.44, 0.42), 141, 0.3, 0.2), -rough(blob(0.5, 0.5, 0.25, 0.22), 142, 0.2, 0.15))
    go("p_ring", ring, elev_of(143, [[(0.15, 0.3), (0.4, 0.1), (0.75, 0.15)]]), 141)
    brk = rough(blob(0.5, 0.5, 0.4, 0.36), 151, 0.3, 0.2)
    cuts = np.maximum.reduce([ridge(g.meander([(0.3, 0.0), (0.42, 0.45), (0.36, 1.0)], 155, 0.03), 0.06),
                              ridge(g.meander([(0.42, 0.45), (1.0, 0.36)], 156, 0.03), 0.06), ridge(g.meander([(0.62, 0.4), (0.72, 1.0)], 157, 0.03), 0.05)])
    brk = np.where(cuts * (0.6 + 0.9 * noise(152, 40, 3)) > 0.62, -0.3, brk)
    go("p_broken", brk, elev_of(153, [[(0.15, 0.4), (0.25, 0.7)], [(0.78, 0.2), (0.9, 0.3)]]), 151)


# ---- bodies of water ----
def waters():
    coast = 0.5 - (NX - 0.58 - 0.18 * (noise(201, 100, 4) - 0.5) - 0.06 * (noise(202, 25, 3) - 0.5))
    coast = np.maximum(coast, rough(blob(0.82, 0.3, 0.05, 0.06), 203, 0.35, 0.3, 30, 10) + 0.5)
    coast = np.maximum(coast, rough(blob(0.86, 0.7, 0.06, 0.045), 204, 0.35, 0.3, 30, 10) + 0.5)
    go("w_ocean", coast - 0.5, elev_of(205, [[(0.1, 0.2), (0.25, 0.8)]]), 201, [[(0.2, 0.45), (0.38, 0.55), (0.55, 0.6)]])
    land = 0.4 + 0 * NX
    sea = rough(blob(0.5, 0.52, 0.3, 0.24), 211, 0.28, 0.18) > 0
    go("w_inland_sea", np.where(sea, -1, land), elev_of(212, [[(0.1, 0.12), (0.5, 0.06), (0.9, 0.14)]]), 211,
       [[(0.4, 0.12), (0.42, 0.3)], [(0.1, 0.7), (0.22, 0.62)]])
    lakes = np.zeros((H, W), bool)
    for i, (cx, cy, rx, ry) in enumerate(((0.2, 0.3, 0.1, 0.06), (0.42, 0.5, 0.12, 0.07), (0.66, 0.4, 0.09, 0.08), (0.82, 0.66, 0.08, 0.05), (0.3, 0.76, 0.07, 0.05))):
        lakes |= rough(blob(cx, cy, rx, ry, i * 0.7), 221 + i, 0.3, 0.3, 40, 14) > 0
    go("w_great_lakes", land, elev_of(226), 221, [[(0.28, 0.33), (0.36, 0.45)], [(0.52, 0.48), (0.6, 0.43)], [(0.72, 0.48), (0.78, 0.6)], [(0.4, 0.56), (0.33, 0.72)]], lakes=lakes)
    go("w_great_river", np.where((NX + 0.2 * NY) > 1.08 + 0.1 * (noise(231, 60) - 0.5), -1, land), elev_of(232, [[(0.05, 0.1), (0.4, 0.05)]], 0.1), 231,
       [[(0.15, 0.1), (0.3, 0.3), (0.5, 0.45), (0.7, 0.62), (0.88, 0.8)], [(0.08, 0.55), (0.3, 0.5), (0.5, 0.45)], [(0.55, 0.12), (0.6, 0.35), (0.7, 0.62)]])
    fj = 0.5 - (NX - 0.6 - 0.12 * (noise(241, 80) - 0.5) - 0.05 * (noise(248, 25, 3) - 0.5))
    for i, (y, L) in enumerate(((0.1, 0.3), (0.28, 0.44), (0.47, 0.32), (0.66, 0.46), (0.86, 0.3))):
        pts = g.meander([(0.7, y), (0.7 - L * 0.5, y + 0.03 * math.sin(i * 2)), (0.7 - L, y - 0.03)], 243 + i, 0.025)
        fj = np.where(ridge(pts, 0.03) * (0.5 + noise(242 + i, 20, 3)) > 0.62, -1, fj)
    go("w_fjords", fj - 0.5, elev_of(247, [[(0.15, 0.1), (0.3, 0.9)], [(0.4, 0.05), (0.45, 0.95)]], 0.1), 241)
    dl = np.where((NY - 0.62 - 0.05 * (noise(251, 60) - 0.5)) > 0, -1, land)
    lobe = rough(blob(0.5, 0.7, 0.26, 0.16), 254, 0.25, 0.25, 60, 18) > 0
    dl = np.where(lobe, land, dl)
    marsh = lobe & (noise(252, 16, 3) > 0.62) & (NY > 0.6)
    chans = [[(0.5, 0.05), (0.48, 0.3), (0.5, 0.56)], [(0.5, 0.56), (0.34, 0.68), (0.27, 0.8)], [(0.5, 0.56), (0.46, 0.72), (0.44, 0.86)],
             [(0.5, 0.56), (0.58, 0.72), (0.6, 0.86)], [(0.5, 0.56), (0.68, 0.66), (0.74, 0.78)]]
    go("w_marsh_delta", dl, elev_of(253), 251, chans, lakes=marsh)


# ---- ways to divide regions ----
def borders(name, mask, seeds):
    im = Image.open(g.OUT / f"ow_{name}.png").convert("RGB"); a = np.asarray(im).copy()
    sx = np.array([p[0] * W for p in seeds]); sy = np.array([p[1] * H for p in seeds])
    d = (XX[..., None] - sx) ** 2 + (YY[..., None] - sy) ** 2
    lab = np.argmin(d, axis=2)
    b = np.zeros_like(mask)
    b[:, 1:] |= lab[:, 1:] != lab[:, :-1]; b[1:, :] |= lab[1:, :] != lab[:-1, :]
    b = b & mask
    b = np.asarray(Image.fromarray(b.astype(np.uint8) * 255).resize((W, H)), bool)
    from PIL import ImageFilter
    b = np.asarray(Image.fromarray(b.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(3)), bool)
    dash = ((XX + YY) // 9) % 2 == 0
    a[b & dash] = (124, 62, 38)
    Image.fromarray(a).save(g.OUT / f"ow_{name}.png")


XX, YY = g.XX, g.YY


def regions():
    m = go("r_one_continent", rough(blob(0.5, 0.52, 0.42, 0.36, 0.1), 301), elev_of(302, [[(0.3, 0.2), (0.45, 0.5), (0.4, 0.85)]]), 301,
           [[(0.45, 0.48), (0.6, 0.62), (0.72, 0.8)]])
    borders("r_one_continent", m, [(0.22, 0.35), (0.3, 0.7), (0.5, 0.25), (0.55, 0.55), (0.75, 0.35), (0.72, 0.72), (0.5, 0.85)])
    few = np.maximum.reduce([rough(blob(0.22, 0.4, 0.17, 0.26, 0.3), 311), rough(blob(0.7, 0.3, 0.2, 0.17, -0.2), 312), rough(blob(0.66, 0.78, 0.17, 0.12), 313)])
    m = go("r_few_continents", few, elev_of(314), 311)
    borders("r_few_continents", m, [(0.18, 0.28), (0.25, 0.6), (0.62, 0.25), (0.8, 0.35), (0.6, 0.8), (0.75, 0.78)])
    isl = np.full((H, W), -1.0)
    for i, (cx, cy, r) in enumerate(((0.16, 0.28, 0.09), (0.42, 0.2, 0.08), (0.74, 0.24, 0.1), (0.24, 0.72, 0.1), (0.52, 0.6, 0.09), (0.82, 0.72, 0.08))):
        isl = np.maximum(isl, rough(blob(cx, cy, r, r * 0.8, i), 321 + i, 0.35, 0.3, 40, 14))
    go("r_islands", isl, elev_of(330), 321)


if __name__ == "__main__":
    shapes(); waters(); regions()
    thumbs = ["p_compact", "p_long", "p_crescent", "p_branching", "p_ring", "p_broken",
              "w_ocean", "w_inland_sea", "w_great_lakes", "w_great_river", "w_fjords", "w_marsh_delta"]
    for t in thumbs:
        Image.open(g.OUT / f"ow_{t}.png").resize((420, 263), Image.LANCZOS).save(g.OUT / f"th_{t}.png")
    sheet = Image.new("RGB", (420 * 6 + 50, 263 * 2 + 10 + 267 + 10), (41, 34, 27))
    for i, t in enumerate(thumbs):
        sheet.paste(Image.open(g.OUT / f"th_{t}.png"), ((i % 6) * 430, (i // 6) * 273))
    for i, t in enumerate(["r_one_continent", "r_few_continents", "r_islands"]):
        sheet.paste(Image.open(g.OUT / f"ow_{t}.png").resize((426, 267)), (i * 436, 546))
    sheet.resize((sheet.width // 2, sheet.height // 2)).save(g.OUT / "pieces_sheet.png")
