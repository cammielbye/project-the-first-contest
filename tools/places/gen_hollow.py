#!/usr/bin/env python3
"""The hollow mountain (Nov 4): Cam's middle island, a tall hollow mountain with a hole in its roof.

Two pixel-art scenes in the Hollis Games style (360x200, flat colours, lit, squeezed into a small palette
with ordered dithering, scaled x4):
  hollow_outside.png  the mountain from the sea: sheer cliffs all round, a dense canopy on top that hides
                      the hole, and the sea gate at the waterline with a ship heading in
  hollow_inside.png   the port inside: the harbour under the hole's shaft of light, shops and taverns
                      cut into the cavern walls in tiers, stairs, lanterns, ships at the quays

Run: python3 gen_hollow.py <out folder>"""
import math, random, sys, pathlib
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter

OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
W, H = 360, 200
# the Hollis Games palette, plus a few sea teals and canopy greens
PAL = ["#0f0c0a", "#1a1410", "#241a14", "#2e2119", "#3b2a1e", "#4a3424", "#5b402b", "#6e4e33", "#85613f", "#a07a4c",
       "#c99a55", "#e3bf7a", "#f4dca0", "#1c2620", "#25332b", "#314237", "#3f5345", "#56685a", "#3a3a38", "#55534e",
       "#77736a", "#9e988b", "#c9c2b0", "#e8dfc8", "#4a1c1a", "#6e2a24", "#93392d", "#2b3a44", "#445866", "#6f8794",
       "#a9bcc4", "#c9a07c", "#a97f5e", "#e0bc98", "#7a5a44",
       "#15262a", "#1f3a3e", "#2d5250", "#4a7270", "#3e5530", "#5a7344"]
hexrgb = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
P = np.array([hexrgb(h) for h in PAL], float)
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 - 0.5
YY, XX = np.mgrid[0:H, 0:W]


def quantize(arr, spread=24):
    t = BAYER[YY % 4, XX % 4] * spread
    a = arr + t[..., None]
    d = (((a[:, :, None, :] - P[None, None]) ** 2) * np.array([.9, 1.2, .7])).sum(-1)
    return P[d.argmin(-1)].astype(np.uint8)


def finish(arr, name, spread=24):
    q = Image.fromarray(quantize(np.clip(arr, 0, 255), spread))
    q.save(OUT / f"{name}_1x.png")
    q.resize((W * 4, H * 4), Image.NEAREST).save(OUT / f"{name}.png")


def C(h):
    return hexrgb(h)


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(img, y0, y1, top, bot, x0=0, x1=W):
    d = ImageDraw.Draw(img)
    for y in range(y0, y1):
        d.line([(x0, y), (x1 - 1, y)], fill=mix(C(top), C(bot), (y - y0) / max(1, y1 - y0 - 1)))


def vignette(arr, vx=0.22, vy=0.16):
    v = 1 - vx * (((XX / W - .5) * 2) ** 2) - vy * (((YY / H - .45) * 2) ** 2)
    return arr * v[..., None]


# ----------------------------------------------------------------------------------------- outside
def outside():
    r = random.Random(11)
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    HOR = 128
    vgrad(img, 0, HOR, "#445866", "#c9c2b0")
    for _ in range(14):                      # long, thin cloud streaks, brighter to the left where the sun is
        y = r.randint(8, 70); x = r.randint(-40, 330); L = r.randint(40, 130)
        d.line([(x, y), (x + L, y)], fill=C("#c9c2b0") if x < 160 else C("#9e988b"), width=r.choice([1, 1, 2]))
    vgrad(img, HOR, H, "#445866", "#15262a")
    d.line([(0, HOR), (W, HOR)], fill=C("#77736a"))
    d.polygon([(318, HOR), (332, HOR - 4), (346, HOR - 3), (360, HOR - 6), (360, HOR)], fill=C("#77736a"))   # the far shore across the strait
    for _ in range(170):                     # wave glints, thinning toward us
        y = r.randint(HOR + 2, H - 2); x = r.randint(0, W)
        L = max(2, int(9 - (y - HOR) / 11)) + r.randint(0, 3)
        d.line([(x, y), (x + L, y)], fill=C("#6f8794") if y < 160 else C("#2d5250"))

    # the mountain: tall and sheer, built from buttresses of different heights so the rim steps and nothing
    # reads as made; the walls flare a little toward the foot
    top, base = 30, 151
    cols = []
    x = 112
    while x < 262:
        w_ = r.randint(7, 16); cols.append((x, x + w_, top + r.randint(0, 9))); x += w_
    left_x = lambda y: 112 - 6 * ((y - top) / (base - top)) ** 2 + 3 * math.sin(y / 11)
    right_x = lambda y: 262 + 9 * ((y - top) / (base - top)) ** 2 + 3 * math.sin(y / 13 + 1)
    wall = [(left_x(y) + r.choice([0, 0, -1, 1]), y) for y in range(base, top + 6, -2)]
    for (x0, x1, t) in cols:
        wall += [(x0, t + r.randint(0, 2)), (x1, t + r.randint(0, 2))]
    wall += [(right_x(y) + r.choice([0, 0, -1, 1]), y) for y in range(top + 6, base + 1, 2)]
    mask = Image.new("L", (W, H)); ImageDraw.Draw(mask).polygon(wall, fill=255)
    m = np.asarray(mask) > 0
    arr = np.asarray(img).astype(float)
    # organ-pipe fluting: columns of rock lighter and darker, lit from the left
    flute = np.zeros(W); xx = 100; rr_ = random.Random(21)
    while xx < W:
        w_ = rr_.randint(2, 6); flute[xx:xx + w_] = rr_.uniform(-1, 1); xx += w_
    shade = np.clip((XX - 104) / 170, 0, 1)
    lightc, midc, darkc = np.array(C("#9e988b"), float), np.array(C("#77736a"), float), np.array(C("#3a3a38"), float)
    cliff = np.where(shade[..., None] < 0.5, lightc + (midc - lightc) * (shade[..., None] * 2), midc + (darkc - midc) * ((shade[..., None] - .5) * 2))
    cliff *= (1 + 0.1 * flute[None, :, None]) * (0.95 + 0.08 * np.random.default_rng(3).random((H, W))[..., None])
    arr[m] = cliff[m]
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(img)
    for _ in range(46):                       # long vertical fissures, uneven
        x = r.randint(116, 260); y0 = r.randint(top + 8, base - 30); L = r.randint(10, 70)
        pts = [(x + int(1.2 * math.sin(k / 5 + x)), y0 + k) for k in range(0, L, 2) if y0 + k < base]
        if len(pts) > 1: d.line(pts, fill=C("#2e2119") if x > 190 else C("#55534e"))
    for _ in range(9):                        # broken ledges, short and uneven, with moss and streaks below
        x = r.randint(114, 238); y = r.randint(top + 14, base - 22); L = r.randint(8, 26)
        d.line([(x, y), (x + L, y + r.choice([-1, 0, 1]))], fill=C("#3a3a38"))
        d.line([(x + 1, y - 1), (x + L - 2, y - 1)], fill=C("#3f5345"))
        for k in range(x + 1, x + L, 3):
            d.line([(k, y + 1), (k, y + 1 + r.randint(2, 9))], fill=C("#55534e") if k < 190 else C("#2e2119"))
    # the waterfall that drains the top, with its mist
    for y in range(top - 2, base):
        x = 232 + int(1.2 * math.sin(y / 9))
        if r.random() < 0.9:
            d.point((x, y), fill=C("#c9c2b0")); d.point((x + 1, y), fill=C("#e8dfc8") if y % 3 else C("#a9bcc4"))
    for _ in range(18):
        x, y = 232 + r.randint(-8, 9), base - r.randint(0, 9)
        d.ellipse((x - 2, y - 2, x + 2, y + 1), fill=C("#c9c2b0"))
    # talus and surf along the foot
    for _ in range(40):
        x = r.randint(102, 274); y = base - r.randint(0, 5); s = r.randint(2, 5)
        d.polygon([(x - s, base + 1), (x, y - s // 2), (x + s, base + 1)], fill=C("#3a3a38") if x > 200 else C("#55534e"))
    for x in range(100, 276):
        if r.random() < 0.8:
            d.point((x, base + 1 + r.choice([0, 0, 1])), fill=C("#c9c2b0"))
    # the sea gate: a ragged sea-cave mouth at the waterline, dark inside, lanterns far within
    gx = 160
    mouth = [(gx - 13, base), (gx - 12, base - 9), (gx - 10, base - 14), (gx - 8, base - 19), (gx - 4, base - 22), (gx - 1, base - 25),
             (gx + 3, base - 23), (gx + 6, base - 24), (gx + 9, base - 19), (gx + 11, base - 15), (gx + 12, base - 8), (gx + 14, base)]
    d.polygon(mouth, fill=C("#0f0c0a"))
    d.line(mouth[1:-1], fill=C("#3a3a38"))
    for (x, y) in [(gx - 4, base - 9), (gx + 2, base - 11), (gx + 7, base - 8)]:
        d.point((x, y), fill=C("#e3bf7a")); d.point((x, y + 1), fill=C("#c99a55"))
    for y in range(base + 2, base + 14, 2):
        d.point((gx + 1 + r.choice([-1, 0, 1]), y), fill=C("#85613f"))
    # the canopy: a dome of crowns over the rim, overhanging the walls, with vines hanging down
    crowns = []
    for cx in range(117, 259, 5):
        dome = 9 * (1 - ((cx - 187) / 86) ** 2)
        rr = r.randint(5, 9)
        crowns.append((cx + r.randint(-2, 2), int(top - 2 - dome - rr * 0.3 + r.randint(-2, 2)), rr))
    for cx, cy, rr in crowns:   # each crown's foliage drapes over the rim by its own amount
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=C("#1c2620"))
        d.rectangle((cx - rr + 2, cy, cx + rr - 2, top + 4 + r.randint(0, 9)), fill=C("#1c2620"))
        dy_ = top + 2 + r.randint(0, 9)
        d.ellipse((cx - 3, dy_, cx + 3, dy_ + r.randint(4, 8)), fill=C("#1c2620"))
    for cx, cy, rr in crowns:
        d.ellipse((cx - rr + 1, cy - rr, cx + rr - 3, cy + rr - 4), fill=C("#25332b"))
        d.arc((cx - rr + 2, cy - rr + 1, cx + rr - 3, cy + rr - 5), 190, 300, fill=C("#5a7344") if cx < 200 else C("#3e5530"))
    for _ in range(70):
        x = r.randint(106, 268); L = r.randint(4, 40) if r.random() < 0.6 else r.randint(2, 6)
        y0 = top + 9
        d.line([(x, y0), (x + r.choice([-1, 0, 1]), y0 + L)], fill=C("#25332b") if r.random() < .6 else C("#314237"))
    # a sea stack to the left, and a ship heading for the gate
    stack = [(14, 158), (16, 132), (21, 118), (27, 114), (34, 120), (37, 138), (41, 158)]
    d.polygon(stack, fill=C("#3a3a38")); d.line(stack[:4], fill=C("#77736a"))
    d.ellipse((20, 109, 33, 118), fill=C("#25332b"))
    for x in range(10, 46):
        if r.random() < 0.7: d.point((x, 158 + r.choice([0, 1])), fill=C("#c9c2b0"))
    sx, sy = 206, 150                           # bow points left, toward the gate
    d.polygon([(sx - 9, sy - 3), (sx + 8, sy - 3), (sx + 9, sy - 6), (sx + 7, sy + 1), (sx - 7, sy + 1)], fill=C("#2e2119"))
    d.line([(sx - 8, sy - 3), (sx + 7, sy - 3)], fill=C("#6e4e33"))
    for mx, h_, sw in ((sx - 3, 15, 4), (sx + 4, 12, 3)):
        d.line([(mx, sy - 3), (mx, sy - 4 - h_)], fill=C("#241a14"))
        d.polygon([(mx - sw, sy - 2 - h_), (mx + sw, sy - 2 - h_), (mx + sw + 1, sy - 6), (mx - sw + 1, sy - 6)], fill=C("#c9c2b0"))
        d.line([(mx + sw, sy - 2 - h_), (mx + sw + 1, sy - 6)], fill=C("#9e988b"))
    d.point((sx - 3, sy - 20), fill=C("#93392d")); d.point((sx - 2, sy - 20), fill=C("#93392d"))
    for k in range(4):
        d.line([(sx + 9 + k * 4, sy + k), (sx + 12 + k * 5, sy + k)], fill=C("#a9bcc4"))
    for (bx, by) in ((138, 14), (146, 10), (226, 18), (290, 30)):   # birds
        d.point((bx - 1, by - 1), fill=C("#241a14")); d.point((bx, by), fill=C("#241a14")); d.point((bx + 1, by - 1), fill=C("#241a14"))

    arr = np.asarray(img).astype(float)
    # a band of cloud wrapped round the cliffs, as on a tepui
    cy_ = 92 + 5 * np.sin(XX / 23) + 3 * np.sin(XX / 9 + 1)
    patch = gaussian_filter(np.random.default_rng(5).random((H, W)), (2, 9))
    patch = (patch - patch.min()) / (patch.max() - patch.min())
    band = np.exp(-((YY - cy_) / 5.5) ** 2) * (0.15 + 0.85 * patch)
    band *= np.clip((XX - 95) / 30, 0, 1) * np.clip((300 - XX) / 30, 0, 1)
    band = np.clip(band, 0, 0.7)
    arr = arr * (1 - band[..., None]) + np.array(C("#c9c2b0"), float) * band[..., None]
    arr = vignette(arr, 0.16, 0.1)
    finish(arr, "hollow_outside", 22)


# ----------------------------------------------------------------------------------------- inside
def inside():
    r = random.Random(7)
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    emit = Image.new("RGBA", (W, H), (0, 0, 0, 0)); e = ImageDraw.Draw(emit)
    lamps = []                                 # (x, y, radius, strength)

    vgrad(img, 0, 150, "#1a1410", "#3b2a1e")
    rng = np.random.default_rng(2)
    arr = np.asarray(img).astype(float)
    tex = gaussian_filter(rng.random((H, W)), 1.2)
    arr *= (0.85 + 0.35 * (tex - tex.mean()) / tex.std() * 0.25)[..., None]
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(img)

    def arcy(base, x, dip=10):
        return int(base + dip * ((x - 180) / 180) ** 2)

    # the sea gate, low on the back wall at the left: daylight from outside
    gx, gw, gy = 52, 15, 128
    gate = [(gx - 16, 148), (gx - 15, 138), (gx - 13, 131), (gx - 10, 124), (gx - 6, 119), (gx - 2, 116), (gx + 2, 117),
            (gx + 5, 114), (gx + 9, 118), (gx + 12, 124), (gx + 14, 131), (gx + 15, 140), (gx + 16, 148)]
    e.polygon(gate, fill=C("#a9bcc4") + (255,))
    e.polygon([(x, max(y, 134)) for x, y in gate], fill=C("#6f8794") + (255,))
    e.line([(gx - 12, 140), (gx + 12, 140)], fill=C("#c9c2b0") + (255,))
    d.line(gate[1:-1], fill=C("#55534e"), width=2)
    lamps.append((gx, 136, 50, 0.6))

    # tiers of shops and taverns cut into the back wall
    levels = [128, 106, 86, 66]
    signs = ["mug", "card", "fish", "mug", "card", "bolt", "fish", "mug"]
    si = 0
    for li, base in enumerate(levels):
        x = 12 + li * 9
        while x < 345:
            w = r.randint(16, 26)
            if gx - gw - 8 < x + w and x < gx + gw + 8 and li == 0:
                x += 8; continue
            yb = arcy(base, x + w / 2)
            h_ = r.randint(13, 18)
            facade = C("#4a3424") if r.random() < 0.6 else C("#3b2a1e")
            d.rectangle((x, yb - h_, x + w, yb), fill=facade)
            d.line([(x, yb - h_), (x + w, yb - h_)], fill=C("#5b402b"))
            dx = x + r.randint(3, w - 7)
            d.rectangle((dx, yb - 7, dx + 3, yb), fill=C("#0f0c0a")); d.point((dx + 1, yb - 8), fill=C("#0f0c0a")); d.point((dx + 2, yb - 8), fill=C("#0f0c0a"))
            for wx in range(x + 2, x + w - 3, 6):
                if abs(wx - dx) < 5 or r.random() < 0.25:
                    continue
                wy = yb - h_ + 4
                lit = r.random() < 0.8
                col = C("#e3bf7a") if lit else C("#1a1410")
                e.rectangle((wx, wy, wx + 2, wy + 3), fill=col + (255,))
                if lit:
                    lamps.append((wx + 1, wy + 2, 16, 0.32))
            if r.random() < 0.45:                       # an awning
                cc = r.choice(["#6e2a24", "#93392d", "#314237", "#6e4e33"])
                d.polygon([(x + 2, yb - h_ + 1), (x + w - 2, yb - h_ + 1), (x + w, yb - h_ + 5), (x, yb - h_ + 5)], fill=C(cc))
                for k in range(x + 1, x + w, 3):
                    d.point((k, yb - h_ + 5), fill=C("#241a14"))
            if r.random() < 0.55:                       # a hanging sign
                sx = x + w - 2; sy = yb - h_ + 6
                d.line([(sx, sy), (sx + 5, sy)], fill=C("#241a14"))
                d.rectangle((sx + 1, sy + 1, sx + 6, sy + 6), fill=C("#85613f"))
                kind = signs[si % len(signs)]; si += 1
                if kind == "mug":
                    d.rectangle((sx + 2, sy + 2, sx + 4, sy + 5), fill=C("#e8dfc8")); d.point((sx + 5, sy + 3), fill=C("#e8dfc8"))
                elif kind == "card":
                    d.rectangle((sx + 2, sy + 2, sx + 5, sy + 5), fill=C("#e8dfc8")); d.point((sx + 3, sy + 3), fill=C("#93392d"))
                elif kind == "fish":
                    d.line([(sx + 2, sy + 3), (sx + 5, sy + 3)], fill=C("#a9bcc4")); d.point((sx + 2, sy + 2), fill=C("#a9bcc4")); d.point((sx + 2, sy + 4), fill=C("#a9bcc4"))
                else:
                    d.line([(sx + 2, sy + 5), (sx + 5, sy + 2)], fill=C("#c99a55"))
            x += w + r.randint(2, 6)
        # the ledge walkway in front of this tier
        pts = [(x_, arcy(base, x_)) for x_ in range(0, W, 3)]
        d.line([(x_, y_ + 1) for x_, y_ in pts], fill=C("#77736a"))
        d.line([(x_, y_ + 2) for x_, y_ in pts], fill=C("#3a3a38"))
    # stairs between the tiers
    for (x0, lo, hi, dirn) in ((96, 0, 1, 1), (250, 0, 1, -1), (150, 1, 2, -1), (300, 1, 2, 1), (60, 2, 3, 1), (214, 2, 3, 1)):
        y0 = arcy(levels[lo], x0) + 1; y1 = arcy(levels[hi], x0 + dirn * (levels[lo] - levels[hi])) + 1
        n = (y0 - y1) // 2
        for k in range(n):
            xs = x0 + dirn * k * 2; ys = y0 - k * 2
            d.line([(xs, ys), (xs + dirn * 2, ys)], fill=C("#9e988b")); d.point((xs, ys + 1), fill=C("#3a3a38"))
    # strings of lanterns across the cavern
    for (x0, y0, x1, y1, sag) in ((20, 58, 150, 70, 14), (210, 66, 340, 56, 14), (40, 96, 330, 104, 22), (120, 40, 260, 44, 10)):
        prev = None
        for i in range(41):
            t = i / 40; x = x0 + (x1 - x0) * t; y = y0 + (y1 - y0) * t + sag * 4 * t * (1 - t)
            if prev: d.line([prev, (x, y)], fill=C("#241a14"))
            prev = (x, y)
            if i % 4 == 2:
                e.point((int(x), int(y) + 1), fill=C("#f4dca0") + (255,)); e.point((int(x), int(y) + 2), fill=C("#c99a55") + (255,))
                lamps.append((x, y + 2, 14, 0.25))

    # the harbour water
    vgrad(img, 148, H, "#1f3a3e", "#15262a")
    for _ in range(220):
        y = r.randint(150, H - 1); x = r.randint(0, W); L = r.randint(2, 7)
        d.line([(x, y), (x + L, y)], fill=C("#2d5250") if r.random() < 0.7 else C("#15262a"))
    # the quay along the back wall
    d.rectangle((0, 140, W, 148), fill=C("#3b2a1e"))
    d.line([(0, 140), (W, 140)], fill=C("#77736a"))
    for x in range(4, W, 22):
        if abs(x - gx) > gw + 3:
            d.rectangle((x, 137, x + 2, 140), fill=C("#241a14"))
    e.rectangle((gx - gw, 140, gx + gw, 148), fill=C("#6f8794") + (255,))   # the gate's water runs through the quay
    for (x, c) in ((80, "#6e4e33"), (86, "#85613f"), (120, "#5b402b"), (226, "#6e4e33"), (233, "#5b402b"), (318, "#85613f")):
        d.rectangle((x, 134, x + 5, 139), fill=C(c)); d.line([(x, 134), (x + 5, 134)], fill=C("#a07a4c"))
    people = [(100, "#6e2a24"), (108, "#314237"), (140, "#2b3a44"), (196, "#85613f"), (205, "#6e2a24"), (270, "#3f5345"), (290, "#2b3a44"), (330, "#93392d")]
    for x, c in people:
        d.rectangle((x, 135, x + 1, 139), fill=C(c)); d.point((x, 134), fill=C("#e0bc98")); d.point((x + 1, 134), fill=C("#c9a07c"))
    # a wooden crane on the quay
    d.line([(132, 139), (132, 112)], fill=C("#5b402b")); d.line([(132, 113), (156, 118)], fill=C("#5b402b"))
    d.line([(155, 118), (155, 128)], fill=C("#241a14")); d.rectangle((152, 128, 158, 132), fill=C("#6e4e33"))

    # the big ship at the right, sails furled, and a smaller one cut by the left edge
    hx0, hx1, hy = 244, 340, 168
    d.polygon([(hx0, hy - 9), (hx1 - 8, hy - 9), (hx1, hy - 18), (hx1 + 2, hy - 18), (hx1 - 2, hy + 4), (hx0 + 8, hy + 4)], fill=C("#4a3424"))
    lamps += [(hx0 + 14, hy - 12, 34, 0.6), (288, 112, 46, 0.4), (hx1 - 6, hy - 8, 34, 0.55)]
    d.line([(hx0 + 2, hy - 8), (hx1 - 9, hy - 8)], fill=C("#a07a4c"))
    d.line([(hx0 + 1, hy - 6), (hx1 - 3, hy - 6)], fill=C("#5b402b"))
    d.line([(hx0 + 4, hy - 1), (hx1 - 4, hy - 1)], fill=C("#241a14"))
    for k in range(hx0 + 14, hx1 - 10, 9):
        d.point((k, hy - 3), fill=C("#0f0c0a"))
    d.line([(hx0 - 14, hy - 16), (hx0 + 2, hy - 9)], fill=C("#3b2a1e"))       # bowsprit
    for mx, mt in ((270, 50), (306, 64)):
        d.line([(mx, hy - 9), (mx, mt)], fill=C("#1a1410"), width=2)
        d.line([(mx + 1, hy - 9), (mx + 1, mt + 2)], fill=C("#6e4e33"))
        for yy, half in ((mt + 8, 15), (mt + 24, 18), (mt + 42, 20)):
            d.line([(mx - half, yy), (mx + half, yy)], fill=C("#1a1410"))
            d.rectangle((mx - half + 2, yy + 1, mx + half - 2, yy + 2), fill=C("#c9c2b0"))
            d.line([(mx - half + 3, yy + 3), (mx + half - 3, yy + 3)], fill=C("#77736a"))
        d.line([(mx, mt), (hx0 - 12, hy - 15)], fill=C("#241a14"))
        d.line([(mx, mt), (hx1 - 4, hy - 17)], fill=C("#241a14"))
    e.point((hx1 - 1, hy - 21), fill=C("#f4dca0") + (255,)); e.point((hx1 - 1, hy - 20), fill=C("#c99a55") + (255,))
    e.point((hx0 + 14, hy - 12), fill=C("#f4dca0") + (255,))
    d.polygon([(0, 158), (34, 158), (40, 151), (42, 151), (36, 166), (0, 166)], fill=C("#241a14"))
    d.line([(20, 158), (20, 92)], fill=C("#1a1410"))
    d.line([(6, 104), (34, 104)], fill=C("#3b2a1e")); d.line([(7, 105), (33, 105)], fill=C("#77736a"))
    # a rowing boat in the light
    d.polygon([(166, 167), (190, 167), (187, 171), (169, 171)], fill=C("#3b2a1e")); d.line([(167, 167), (189, 167)], fill=C("#6e4e33"))
    d.point((178, 165), fill=C("#e0bc98")); d.rectangle((177, 166, 179, 167), fill=C("#2b3a44"))
    d.line([(172, 168), (166, 173)], fill=C("#5b402b"))

    # foreground quays with crates and barrels, and the near rock framing the view
    d.polygon([(0, 186), (96, 186), (104, 200), (0, 200)], fill=C("#3b2a1e")); d.line([(0, 186), (96, 186)], fill=C("#77736a"))
    d.polygon([(292, 181), (360, 181), (360, 200), (282, 200)], fill=C("#3b2a1e")); d.line([(292, 181), (360, 181)], fill=C("#77736a"))
    for (x, y, w_, c) in ((14, 176, 10, "#6e4e33"), (26, 179, 7, "#85613f"), (60, 178, 8, "#5b402b"), (306, 172, 9, "#6e4e33"), (318, 175, 6, "#85613f")):
        d.rectangle((x, y, x + w_, 186 if x < 200 else 181), fill=C(c)); d.line([(x, y), (x + w_, y)], fill=C("#a07a4c"))
    for (x, c) in ((40, "#2b3a44"), (336, "#6e2a24"), (345, "#3f5345")):
        yb = 186 if x < 200 else 181
        d.rectangle((x, yb - 7, x + 2, yb - 1), fill=C(c)); d.point((x + 1, yb - 8), fill=C("#e0bc98")); d.point((x, yb - 8), fill=C("#c9a07c"))
    for (lx, ly) in ((64, 175), (322, 170)):
        d.line([(lx, ly + 1), (lx, ly + 10)], fill=C("#241a14"))
        e.rectangle((lx - 1, ly - 1, lx + 1, ly + 1), fill=C("#f4dca0") + (255,))
        lamps.append((lx, ly, 40, 0.75))

    # the near rock: the vault of the roof, with stalactites, and the walls that close in at the edges
    near = Image.new("L", (W, H)); nd = ImageDraw.Draw(near)
    roof = [(0, 0), (W, 0)]
    for x in range(W, -1, -3):
        u = (x - 180) / 180
        roof.append((x, int(38 + 30 * u * u + r.randint(-2, 2))))
    nd.polygon(roof, fill=255)
    for _ in range(46):                          # stalactites hanging from the vault's edge
        x = r.randint(4, W - 4); u = (x - 180) / 180; y = int(38 + 30 * u * u)
        if abs(x - 181) < 40: continue
        L = r.randint(3, 14); w_ = r.randint(1, 3)
        nd.polygon([(x - w_, y - 1), (x + w_, y - 1), (x, y + L)], fill=255)
    nd.polygon([(0, 0), (20, 40), (13, 84), (24, 120), (10, 158), (0, 186)], fill=255)
    nd.polygon([(W, 0), (W - 18, 46), (W - 11, 92), (W - 24, 128), (W - 12, 168), (W, 181)], fill=255)
    hole = Image.new("L", (W, H)); hd = ImageDraw.Draw(hole)
    hd.ellipse((148, -3, 214, 21), fill=255)
    nm = (np.asarray(near) > 0) & ~(np.asarray(hole) > 0)
    arr = np.asarray(img).astype(float)
    rtex = gaussian_filter(rng.random((H, W)), 1.4); rtex = (rtex - rtex.mean()) / rtex.std()
    strata = np.sin(YY / 3.0 + 2.5 * np.sin(XX / 17.0)) * 0.5
    rock = np.array(C("#3b2a1e"), float)
    arr[nm] = rock * np.clip(0.85 + 0.12 * rtex[nm] + 0.1 * strata[nm], 0.5, 1.3)[:, None]
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(img)
    e.ellipse((148, -3, 214, 21), fill=C("#e8dfc8") + (255,))
    e.ellipse((160, -3, 202, 13), fill=C("#f4dca0") + (255,))
    for _ in range(64):                          # leaves over the rim
        ang = r.uniform(0, math.pi); x = int(181 + math.cos(ang) * r.uniform(28, 36)); y = int(9 + math.sin(ang) * r.uniform(9, 14) - r.randint(0, 6))
        rr = r.randint(1, 3)
        e.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(C("#1c2620") if r.random() < .6 else C("#25332b")) + (255,))
    for _ in range(30):                          # vines hanging into the cavern
        x = r.randint(150, 212); L = r.randint(8, 56)
        sway = r.uniform(-0.15, 0.15); y0 = 14 + int(6 * math.sin((x - 148) / 66 * math.pi))
        for k in range(L):
            e.point((int(x + sway * k + math.sin(k / 6) * 0.8), y0 + k), fill=(C("#1c2620") if k % 5 else C("#314237")) + (255,))

    arr = np.asarray(img).astype(float)
    # light: low ambient, warm lamps, and the shaft from the hole
    k = np.full((H, W), 0.4)
    warm = np.zeros((H, W))
    for (lx, ly, rad, s) in lamps:
        dd = np.hypot(XX - lx, (YY - ly) * 1.15) / rad
        warm += np.clip(1 - dd, 0, 1) ** 1.6 * s
    shaft = Image.new("L", (W, H)); sd = ImageDraw.Draw(shaft)
    sd.polygon([(154, 12), (208, 12), (262, 174), (110, 174)], fill=255)
    sh = gaussian_filter(np.asarray(shaft).astype(float) / 255, 5)
    sh *= np.clip(1 - (YY - 6) / 260, 0.35, 1) * (1 - 0.35 * np.abs((XX - 181 - (YY - 6) * 0.03) / (40 + YY * 0.55)))
    pool = np.exp(-(((XX - 186) / 52) ** 2 + ((YY - 168) / 9) ** 2))   # where the shaft lands on the water
    glow = gaussian_filter(np.asarray(shaft).astype(float) / 255, 34) * 0.55 + np.exp(-(((XX - 181) / 90) ** 2 + ((YY - 20) / 45) ** 2)) * 0.45
    cool = np.clip(sh * 1.05 + pool * 0.9 + glow, 0, 2)
    lit = arr * (k + warm * 0.0)[..., None]
    lit = lit + arr * warm[..., None] * np.array([1.25, 0.95, 0.6])
    lit = lit + arr * cool[..., None] * np.array([0.95, 1.0, 1.05]) + cool[..., None] * np.array([46, 48, 44])
    lit = vignette(lit, 0.18, 0.12)
    # reflections of the lights on the water, and motes in the shaft
    em = np.asarray(emit).astype(float)
    ea = em[..., 3] > 0
    lit[ea] = em[ea][:, :3]
    refl = Image.fromarray(np.clip(lit, 0, 255).astype(np.uint8)); rd = ImageDraw.Draw(refl)
    ys, xs = np.nonzero(ea & (YY < 136) & (YY > 96) & (em[..., 0] > 200))
    for i in r.sample(range(len(xs)), min(24, len(xs))):
        x = xs[i]; c = mix(C("#c99a55"), C("#1f3a3e"), 0.35)
        for y in range(152 + r.randint(0, 3), 186, 3):
            px_ = lit[min(H - 1, y), min(W - 1, x)]
            if r.random() < 0.7 and px_[2] > px_[0]: rd.line([(x, y), (x + 1, y)], fill=c)   # on open water only
    for _ in range(90):
        y = r.randint(14, 165); half = 29 + (y - 6) * 0.45; x = int(181 + (y - 6) * 0.03 + r.uniform(-half, half) * 0.8)
        if not nm[y, x]:
            rd.point((x, y), fill=C("#e8dfc8"))
    for _ in range(40):
        x = int(186 + r.gauss(0, 34)); y = int(168 + r.gauss(0, 4))
        if 150 < y < 199: rd.line([(x, y), (x + r.randint(1, 4), y)], fill=C("#c9c2b0"))
    finish(np.asarray(refl).astype(float), "hollow_inside", 24)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    outside()
    inside()
    print("wrote", OUT / "hollow_outside.png", OUT / "hollow_inside.png")
