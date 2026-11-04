#!/usr/bin/env python3
"""Six overworld option sketches in the parchment-and-ink style of the Greywater Reach board.
Each map is 852x534 (shown at 426x267). Land, sea, coast ink, mountains, forests, rivers,
lakes, place dots for scale, and the four fixed pinnacle seats."""
import math, pathlib, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = pathlib.Path(__file__).resolve().parent
W, H = 852, 534
MEANDER = True

SEA = (185, 195, 178)      # #B9C3B2, as on the Greywater Reach
SEA_DEEP = (160, 174, 160)
LAND = (230, 218, 192)     # #E6DAC0
LAND_HI = (218, 203, 172)
INK = (58, 46, 34)         # #3A2E22
WAVE = (94, 112, 102)      # #5E7066
RIVER = (88, 112, 112)
FOREST = (112, 122, 88)
SEATS = {"fire": (176, 74, 46), "water": (52, 104, 140), "earth": (92, 112, 52), "air": (128, 118, 150)}


def noise(seed, scale, octaves=5):
    rng = np.random.default_rng(seed)
    acc = np.zeros((H, W)); amp = 1.0; tot = 0.0
    for o in range(octaves):
        gw = max(2, int(W / scale * 2 ** o)); gh = max(2, int(H / scale * 2 ** o))
        g = rng.random((gh, gw)).astype(np.float32)
        im = Image.fromarray((g * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
        acc += amp * (np.asarray(im, np.float32) / 255.0); tot += amp; amp *= 0.5
    return acc / tot


YY, XX = np.mgrid[0:H, 0:W]
NX, NY = XX / W, YY / H


def blob(cx, cy, rx, ry, rot=0.0):
    c, s = math.cos(rot), math.sin(rot)
    dx, dy = (NX - cx), (NY - cy) * H / W
    u = (dx * c + dy * s) / rx; v = (-dx * s + dy * c) / ry
    return 1 - np.sqrt(u * u + v * v)


def ridge_line(pts, width):
    """distance falloff from a polyline given in 0..1 coords"""
    d = np.full((H, W), 9.0)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        ax, ay, bx, by = x0, y0 * H / W, x1, y1 * H / W
        px, py = NX, NY * H / W
        vx, vy = bx - ax, by - ay
        t = np.clip(((px - ax) * vx + (py - ay) * vy) / (vx * vx + vy * vy), 0, 1)
        d = np.minimum(d, np.hypot(px - (ax + t * vx), py - (ay + t * vy)))
    return np.clip(1 - d / width, 0, 1)


def rough(sh, seed, a=0.42, b=0.22, s1=120, s2=38):
    """add coarse and fine noise so coastlines read as real coasts"""
    return sh + a * (noise(seed + 101, s1, 4) - 0.5) * 2 + b * (noise(seed + 202, s2, 3) - 0.5) * 2


def meander(pts, seed, amp=0.012):
    r = random.Random(seed); out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy) or 1; px, py = -dy / L, dx / L
        ph = r.random() * 6.28
        for k in range(10):
            t = k / 10; w = amp * math.sin(ph + t * 6.28 * 1.5)
            out.append((x0 + dx * t + px * w, y0 + dy * t + py * w))
    out.append(pts[-1]); return out


def render(name, land, elev, seed, n_places, seats, rivers=(), lakes=None, label=None):
    rng = random.Random(seed)
    land_m = land > 0
    if lakes is not None:
        land_m &= ~lakes
    # base
    img = np.zeros((H, W, 3), np.float32)
    deep = noise(seed + 9, 90, 3)
    sea = np.array(SEA)[None, None, :] * (1 - 0.25 * deep[..., None]) + np.array(SEA_DEEP)[None, None, :] * 0.25 * deep[..., None]
    img[:] = sea
    lt = np.clip((elev - 0.45) * 2.2, 0, 1)[..., None]
    lnd = np.array(LAND)[None, None, :] * (1 - 0.5 * lt) + np.array(LAND_HI)[None, None, :] * 0.5 * lt
    img[land_m] = lnd[land_m]
    im = Image.fromarray(img.astype(np.uint8))
    # paper grain
    grain = (np.random.default_rng(seed).random((H, W)) * 18 - 9)
    arr = np.clip(np.asarray(im, np.float32) + grain[..., None], 0, 255).astype(np.uint8)
    im = Image.fromarray(arr)
    d = ImageDraw.Draw(im)
    # coast ink: edge of the land mask
    lm = Image.fromarray((land_m * 255).astype(np.uint8))
    edge = np.asarray(lm.filter(ImageFilter.MaxFilter(3)), bool) & ~np.asarray(lm.filter(ImageFilter.MinFilter(3)), bool)
    ink = np.asarray(im).copy(); ink[edge] = INK; im = Image.fromarray(ink); d = ImageDraw.Draw(im)
    # shallow-water hatch: a second faint ring offshore
    ring = np.asarray(lm.filter(ImageFilter.MaxFilter(13)), bool) & ~np.asarray(lm.filter(ImageFilter.MaxFilter(9)), bool)
    a = np.asarray(im).copy(); a[ring] = (a[ring] * 0.6 + np.array(WAVE) * 0.4).astype(np.uint8); im = Image.fromarray(a); d = ImageDraw.Draw(im)
    # waves in open sea
    for _ in range(int(W * H / 9000)):
        x, y = rng.randrange(10, W - 30), rng.randrange(10, H - 10)
        if not land_m[y, x] and not land_m[min(H - 1, y + 8), min(W - 1, x + 20)] and not land_m[max(0, y - 8), x]:
            d.arc((x, y - 3, x + 10, y + 3), 200, 340, fill=WAVE, width=1)
            d.arc((x + 9, y - 3, x + 19, y + 3), 200, 340, fill=WAVE, width=1)
    # rivers
    for k, pts in enumerate(rivers):
        pp = [(x * W, y * H) for x, y in (meander(pts, seed * 10 + k) if MEANDER and len(pts) < 12 else pts)]
        d.line(pp, fill=RIVER, width=3, joint="curve")
    # lakes ink
    if lakes is not None:
        lk = Image.fromarray((lakes & (land > 0)).astype(np.uint8) * 255)
        e2 = np.asarray(lk.filter(ImageFilter.MaxFilter(3)), bool) & ~np.asarray(lk.filter(ImageFilter.MinFilter(3)), bool)
        a = np.asarray(im).copy(); a[e2] = INK; im = Image.fromarray(a); d = ImageDraw.Draw(im)
    # mountains: carets on high ground; forests: stipple on mid ground
    for _ in range(int(6000 * W * H / (852 * 534))):
        x, y = rng.randrange(6, W - 12), rng.randrange(10, H - 6)
        if not land_m[y, x]:
            continue
        e = elev[y, x]
        if e > 0.64 and rng.random() < 0.5:
            s = 6 + int((e - 0.64) * 22)
            if land_m[max(0, y - s), x] and land_m[y, min(W - 1, x + s)]:
                d.line([(x - s, y), (x, y - s), (x + s, y)], fill=INK, width=2)
                d.line([(x, y - s), (x + s // 2, y - s // 3)], fill=INK, width=1)
        elif 0.5 < e < 0.6 and rng.random() < 0.18:
            d.ellipse((x - 3, y - 3, x + 3, y + 3), outline=FOREST, width=1)
    # place dots, spread across the land
    placed = []
    tries = 0
    while len(placed) < n_places and tries < 40000:
        tries += 1
        x, y = rng.randrange(14, W - 14), rng.randrange(14, H - 14)
        if not land_m[y, x] or elev[y, x] > 0.74:
            continue
        if any((x - px) ** 2 + (y - py) ** 2 < 26 ** 2 for px, py in placed):
            continue
        placed.append((x, y))
    for x, y in placed:
        d.ellipse((x - 2.5, y - 2.5, x + 2.5, y + 2.5), fill=INK)
    # pinnacle seats: fire triangle, water circle, earth square, air diamond
    for kind, (sx, sy) in seats.items():
        x, y = sx * W, sy * H; c = SEATS[kind]; r = 11
        d.ellipse((x - r - 5, y - r - 5, x + r + 5, y + r + 5), fill=(241, 232, 210), outline=INK, width=2)
        if kind == "fire":
            d.polygon([(x, y - r), (x + r, y + r * 0.8), (x - r, y + r * 0.8)], fill=c)
        elif kind == "water":
            d.ellipse((x - r, y - r, x + r, y + r), fill=c)
        elif kind == "earth":
            d.rectangle((x - r * 0.8, y - r * 0.8, x + r * 0.8, y + r * 0.8), fill=c)
        else:
            d.polygon([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], fill=c)
    # frame
    d.rectangle((0, 0, W - 1, H - 1), outline=INK, width=3)
    im.save(OUT / f"ow_{name}.png")
    land_share = land_m.mean()
    print(name, "land", round(float(land_share), 2), "places", len(placed))


def continent():
    n = noise(11, 160); e = noise(12, 120)
    sh = rough(blob(0.5, 0.52, 0.36, 0.3, 0.15), 11)
    sh = np.maximum(sh, rough(blob(0.2, 0.28, 0.1, 0.08), 13, 0.3, 0.2))
    inland = rough(blob(0.6, 0.47, 0.07, 0.05, 0.6), 14, 0.2, 0.25) > 0
    elev = np.clip(0.5 * e + 0.5 * ridge_line([(0.3, 0.2), (0.45, 0.4), (0.4, 0.75)], 0.08) + 0.15 * (n - 0.5), 0, 1)
    rivers = [[(0.44, 0.42), (0.5, 0.52), (0.56, 0.62), (0.62, 0.72), (0.66, 0.84)],
              [(0.38, 0.62), (0.3, 0.7), (0.22, 0.78)], [(0.42, 0.3), (0.5, 0.22), (0.58, 0.14)]]
    seats = {"fire": (0.78, 0.66), "water": (0.93, 0.18), "earth": (0.42, 0.52), "air": (0.33, 0.22)}
    render("continent", sh, elev, 1, 80, seats, rivers, lakes=inland)


def two_continents():
    n = noise(21, 150); e = noise(22, 110)
    a = rough(blob(0.24, 0.5, 0.18, 0.32, 0.3), 21)
    b = rough(blob(0.75, 0.5, 0.17, 0.3, -0.2), 23)
    ch = ridge_line([(0.5, 0.0), (0.47, 0.35), (0.53, 0.65), (0.49, 1.0)], 0.06) > 0.05
    sh = np.where(ch, -0.3, np.maximum(a, b))
    sh = np.maximum(sh, rough(blob(0.5, 0.5, 0.045, 0.06), 24, 0.18, 0.22))
    elev = np.clip(0.55 * e + 0.45 * np.maximum(ridge_line([(0.18, 0.2), (0.28, 0.75)], 0.06), ridge_line([(0.8, 0.25), (0.7, 0.8)], 0.06)), 0, 1)
    rivers = [[(0.26, 0.45), (0.33, 0.55), (0.4, 0.62)], [(0.72, 0.48), (0.64, 0.4), (0.57, 0.33)]]
    seats = {"fire": (0.83, 0.74), "water": (0.5, 0.86), "earth": (0.24, 0.5), "air": (0.79, 0.27)}
    render("two_continents", sh, elev, 2, 70, seats, rivers)


def archipelago():
    n = noise(31, 70, 5); e = noise(32, 60)
    base = 0.3 * blob(0.5, 0.5, 0.6, 0.55)
    sh = (n - 0.6) * 3 + base + 0.25 * (noise(33, 30, 3) - 0.5)
    elev = np.clip(0.4 + (n - 0.5) * 2.2 + 0.2 * (e - 0.5), 0, 1)
    seats = {"fire": (0.82, 0.78), "water": (0.08, 0.86), "earth": (0.5, 0.48), "air": (0.2, 0.16)}
    render("archipelago", sh, elev, 3, 60, seats)


def inland_sea():
    n = noise(41, 140); e = noise(42, 110)
    outer = rough(blob(0.5, 0.5, 0.43, 0.4), 41)
    inner = rough(blob(0.52, 0.5, 0.24, 0.19, 0.3), 43, 0.3, 0.18)
    sh = np.minimum(outer, -inner)
    strait = (ridge_line([(0.8, 0.58), (0.86, 0.66), (0.92, 0.62), (1.0, 0.7)], 0.04) + 0.5 * (noise(45, 30, 3) - 0.5)) > 0.25
    sh = np.where(strait, -0.2, sh)
    sh = np.maximum(sh, rough(blob(0.54, 0.5, 0.05, 0.065), 44, 0.18, 0.22))
    elev = np.clip(0.5 * e + 0.5 * ridge_line([(0.12, 0.3), (0.3, 0.12), (0.6, 0.1), (0.85, 0.22)], 0.07), 0, 1)
    rivers = [[(0.3, 0.14), (0.33, 0.22), (0.36, 0.3)], [(0.15, 0.6), (0.24, 0.58), (0.3, 0.55)]]
    seats = {"fire": (0.74, 0.82), "water": (0.54, 0.5), "earth": (0.12, 0.45), "air": (0.55, 0.1)}
    render("inland_sea", sh, elev, 4, 75, seats, rivers)


def river_country():
    n = noise(51, 150); e = noise(52, 100)
    sh = 0.4 + 0.25 * (n - 0.5)
    coast = (NX + 0.25 * NY) > 1.02 + 0.35 * (noise(54, 90, 4) - 0.5) + 0.12 * (noise(55, 30, 3) - 0.5)
    sh = np.where(coast, -0.3, sh)
    lakes = (noise(53, 40, 4) > 0.69) & (NX < 0.8)
    mtn = np.maximum(ridge_line([(0.05, 0.1), (0.3, 0.05), (0.5, 0.12)], 0.14), ridge_line([(0.02, 0.45), (0.08, 0.85)], 0.1))
    elev = np.clip(0.35 * e + 0.6 * mtn + 0.15, 0, 1)
    main = [(0.22, 0.12), (0.26, 0.24), (0.34, 0.33), (0.42, 0.42), (0.5, 0.5), (0.6, 0.58), (0.7, 0.66), (0.8, 0.74), (0.86, 0.8)]
    tribs = [[(0.08, 0.5), (0.2, 0.46), (0.34, 0.44), (0.42, 0.42)], [(0.48, 0.14), (0.47, 0.28), (0.5, 0.5)],
             [(0.2, 0.82), (0.36, 0.72), (0.52, 0.64), (0.6, 0.58)], [(0.62, 0.16), (0.66, 0.34), (0.7, 0.5), (0.7, 0.66)]]
    seats = {"fire": (0.6, 0.86), "water": (0.92, 0.88), "earth": (0.08, 0.66), "air": (0.3, 0.07)}
    render("river_country", sh, elev, 5, 80, seats, [main] + tribs, lakes=lakes)


def spine():
    n = noise(61, 150); e = noise(62, 110)
    sh = rough(blob(0.5, 0.5, 0.44, 0.26, 0.35), 61)
    sp = ridge_line([(0.1, 0.78), (0.3, 0.6), (0.52, 0.48), (0.72, 0.34), (0.9, 0.2)], 0.07)
    elev = np.clip(0.4 * e + 0.75 * sp, 0, 1)
    rivers = [[(0.32, 0.58), (0.26, 0.44), (0.2, 0.32)], [(0.63, 0.39), (0.55, 0.28), (0.48, 0.17)],
              [(0.5, 0.5), (0.6, 0.62), (0.68, 0.72)]]
    seats = {"fire": (0.7, 0.62), "water": (0.18, 0.2), "earth": (0.52, 0.46), "air": (0.86, 0.22)}
    render("spine", sh, elev, 6, 75, seats, rivers)


if __name__ == "__main__":
    continent(); two_continents(); archipelago(); inland_sea(); river_country(); spine()
    ims = [Image.open(OUT / f"ow_{k}.png") for k in ("continent", "two_continents", "archipelago", "inland_sea", "river_country", "spine")]
    sheet = Image.new("RGB", (W * 3 + 40, H * 2 + 20), (41, 34, 27))
    for i, m in enumerate(ims):
        sheet.paste(m, ((i % 3) * (W + 20), (i // 3) * (H + 20)))
    sheet.resize((sheet.width // 2, sheet.height // 2)).save(OUT / "ow_sheet.png")
