#!/usr/bin/env python3
"""The supercontinent and the continents it broke into.

Old map (852x534): one supercontinent with its ranges, lakes and rivers.
Modern map (1704x1068, same scale, so the oceans opened around the pieces): the land is cut along
meandering rifts, each piece drifts and turns, and its coasts wear back so only ~72% of each
piece's crust is still dry. That is the real ratio: dry land is ~29% of Earth's surface and
continental crust ~40%, so ~28% of continental crust lies under the sea as shelf and slope.
The shelves are drawn, and the pieces fit at the shelf edge rather than at the shore
(Bullard, Everett and Smith 1965 fitted the Atlantic at ~900 m). Rift-facing coasts get wider
shelves, one coast erodes far faster than the rest, a delta has grown out past the old edge,
and a chain of volcanic islands marks where the rift opened (the earth seat sits on one).
Fit view (852x534): for us, not the player: each piece's crust on the old map, with what is
still dry today shaded darker."""
import math, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import distance_transform_edt as edt, map_coordinates, label, uniform_filter
import gen_overworld as g
from gen_batch2 import lopsided

g.MEANDER = False
OW, OH, MW, MH = 852, 534, 1704, 1068
SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 7
DRY = 0.72
S = 1.75            # the modern map is drawn closer in than the old one


def set_size(w, h):
    g.W, g.H = w, h
    g.YY, g.XX = np.mgrid[0:h, 0:w]
    g.NX, g.NY = g.XX / w, g.YY / h


def fill_holes(land, min_island=0):
    lab, n = label(~land)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
    for k in range(1, n + 1):
        if k not in edge:
            land[lab == k] = True
    if min_island:
        lab, n = label(land); sz = np.bincount(lab.ravel())
        for k in range(1, n + 1):
            if sz[k] < min_island:
                land[lab == k] = False
    return land


def rivers_for(land, elev, r, n, W, H):
    dist = edt(np.pad(land, 1))[1:-1, 1:-1]
    out = []
    cand = list(zip(*np.nonzero((elev > 0.55) & (dist > 30)))); r.shuffle(cand)
    for (y, x) in cand[:n * 12]:
        if len(out) >= n:
            break
        if any(math.hypot(x - p[0][0] * W, y - p[0][1] * H) < 140 for p in out):
            continue
        path = [(x, y)]; off = False
        for _ in range(500):
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
                off = True; break
        if len(path) > 16 and not off:
            P = np.array(path, float); k = 7
            sm = np.array([P[max(0, i - k):i + k + 1].mean(0) for i in range(len(P))]); sm[0], sm[-1] = P[0], P[-1]
            out.append([(px / W, py / H) for px, py in sm[::4]] + [(P[-1][0] / W, P[-1][1] / H)])
    return out


def age(path, tint=(200, 168, 118), k=0.22, seed=0):
    """make a rendered map look older: sepia, darker edges, a few faint stains"""
    im = Image.open(path).convert("RGB"); a = np.asarray(im, np.float32)
    a = a * (1 - k) + np.array(tint) * k
    H, W = a.shape[:2]; yy, xx = np.mgrid[0:H, 0:W]
    v = 1 - 0.16 * (((xx / W - .5) * 2) ** 2 + ((yy / H - .5) * 2) ** 2) ** 1.6
    a *= np.clip(v, 0.72, 1)[..., None]
    rng = np.random.default_rng(seed)
    for _ in range(5):
        cx, cy, rr = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(40, 120)
        m = np.clip(1 - np.hypot(xx - cx, yy - cy) / rr, 0, 1) ** 2 * rng.uniform(0.04, 0.09)
        a *= (1 - m)[..., None]
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)); dd = ImageDraw.Draw(out)
    dd.rectangle((9, 9, W - 10, H - 10), outline=(58, 46, 34), width=1)
    out.save(path)


r = random.Random(SEED)

# ------------------------------------------------------------------ the supercontinent
set_size(OW, OH)
YY, XX, NX, NY = g.YY, g.XX, g.NX, g.NY
f = lopsided(r, 0.5, 0.52, 0.33, 1.4, r.uniform(-0.25, 0.25))
for _ in range(3):
    f = np.maximum(f, lopsided(r, r.uniform(0.25, 0.75), r.uniform(0.28, 0.72), r.uniform(0.12, 0.2), r.uniform(1, 1.8), r.uniform(0, 3.1)) * 0.85)
f = f + 0.38 * (g.noise(SEED + 1, 130, 4) - 0.5) * 2 + 0.17 * (g.noise(SEED + 2, 34, 3) - 0.5) * 2
wx = (g.noise(SEED + 3, 180, 3) - 0.5) * 2 * 60 + (g.noise(SEED + 8, 55, 3) - 0.5) * 2 * 14
wy = (g.noise(SEED + 4, 180, 3) - 0.5) * 2 * 60 + (g.noise(SEED + 9, 55, 3) - 0.5) * 2 * 14
f = map_coordinates(f, [np.clip(YY + wy, 0, OH - 1), np.clip(XX + wx, 0, OW - 1)], order=1)
edgeness = np.clip(np.minimum.reduce([NX, 1 - NX, NY * OH / OW, (1 - NY) * OH / OW]) / 0.16, 0, 1)
f = f - (1 - edgeness) ** 2 * 1.2
land_old = fill_holes(f > np.quantile(f, 1 - 0.34), 160)
lab, n = label(land_old); sz = np.bincount(lab.ravel()); sz[0] = 0
land_old = lab == np.argmax(sz)          # one landmass
dist_old = edt(land_old)
ys, xs = np.nonzero(land_old)
cx_all, cy_all = xs.mean(), ys.mean()

# rifts: one long one across the land, one or two branching off it
xa = r.uniform(0.42, 0.58)
riftA = [(xa + r.uniform(-.05, .05), -0.05)] + [(xa + r.uniform(-.08, .08), t) for t in (0.2, 0.36, 0.52, 0.68, 0.84)] + [(xa + r.uniform(-.05, .05), 1.05)]
jy = r.uniform(0.42, 0.6)
jx = np.interp(jy, [p[1] for p in riftA], [p[0] for p in riftA])
side = r.choice([1, -1])
riftB = [(jx, jy)] + [(jx + side * t, jy + r.uniform(-.09, .09)) for t in (0.1, 0.2, 0.3, 0.4)] + [(0.5 + side * 0.6, jy + r.uniform(-.2, .2))]
rifts = [g.meander(riftA, SEED + 20, 0.022), g.meander(riftB, SEED + 21, 0.022)]
if r.random() < 0.6:
    ky = r.uniform(0.25, 0.4) if jy > 0.5 else r.uniform(0.62, 0.75)
    kx = np.interp(ky, [p[1] for p in riftA], [p[0] for p in riftA])
    riftC = [(kx, ky)] + [(kx - side * t, ky + r.uniform(-.08, .08)) for t in (0.12, 0.24, 0.36)] + [(0.5 - side * 0.6, ky + r.uniform(-.2, .2))]
    rifts.append(g.meander(riftC, SEED + 22, 0.022))
corridor = np.zeros_like(land_old)
for pts in rifts:
    corridor |= g.ridge_line(pts, 0.005) > 0
pieces_lab, npcs = label(land_old & ~corridor)
psz = np.bincount(pieces_lab.ravel()); psz[0] = 0
big = [k for k in range(1, npcs + 1) if psz[k] > 0.05 * land_old.sum()]
frags = [k for k in range(1, npcs + 1) if 0 < psz[k] <= 0.05 * land_old.sum() and psz[k] > 120]
near_rift = edt(~corridor) < 16

# features on the old land: a range that crosses the main rift, two more, a few lakes, rivers
e = 0.42 * g.noise(SEED + 30, 110) + 0.28 * np.clip(dist_old / 110, 0, 1)
y0 = r.uniform(0.3, 0.7)
x0 = np.interp(y0, [p[1] for p in riftA], [p[0] for p in riftA])
ranges = [[(x0 - 0.2, y0 - 0.06), (x0 - 0.05, y0), (x0 + 0.08, y0 + 0.03), (x0 + 0.2, y0 + 0.1)]]
for _ in range(2):
    k = r.choice(big); yy_, xx_ = np.nonzero((pieces_lab == k) & (dist_old > 40) & ~near_rift)
    if len(xx_):
        i = r.randrange(len(xx_)); px, py = xx_[i] / OW, yy_[i] / OH; a = r.uniform(0, math.pi); L = r.uniform(0.12, 0.22)
        ranges.append([(px - math.cos(a) * L, py - math.sin(a) * L * OW / OH), (px, py), (px + math.cos(a) * L, py + math.sin(a) * L * OW / OH)])
for k, pts in enumerate(ranges):
    e = e + (0.42 if k == 0 else 0.5) * g.ridge_line(g.meander(pts, SEED + 40 + k, 0.015), 0.035 if k == 0 else 0.045) * (dist_old > 6)
elev_old = np.clip(e, 0, 1)
lakes_old = np.zeros_like(land_old); placed = []
yl, xl = np.nonzero((dist_old > 40) & ~near_rift & (elev_old < 0.6))
order = list(range(len(xl))); r.shuffle(order)
for i in order:
    if len(placed) >= 3:
        break
    x, y = xl[i], yl[i]
    if any(math.hypot(x - a, y - b) < 130 for a, b in placed):
        continue
    rad = r.uniform(0.016, 0.03) if placed else r.uniform(0.03, 0.042)
    lk = g.rough(g.blob(x / OW, y / OH, rad, rad * r.uniform(0.4, 0.8), r.uniform(0, 3.1)), SEED + 50 + len(placed), 0.5, 0.4, 28, 9) > 0
    if (lk & (dist_old < 14)).any():
        continue
    lakes_old |= lk; placed.append((x, y))
dry_old = land_old & ~lakes_old
riv_old = rivers_for(dry_old, elev_old, r, 4, OW, OH)
g.render(f"pg_old_{SEED}", np.where(dry_old, 1.0, -1.0), elev_old, SEED, 0, {}, riv_old)
age(g.OUT / f"ow_pg_old_{SEED}.png", seed=SEED)

# ------------------------------------------------------------------ drift
set_size(MW, MH)
MY, MX = g.YY, g.XX


def to_old(theta, c, d):
    ct, st = math.cos(-theta), math.sin(-theta)
    ox = (ct * (MX - d[0]) - st * (MY - d[1])) / S + c[0]
    oy = (st * (MX - d[0]) + ct * (MY - d[1])) / S + c[1]
    return oy, ox


def to_new(theta, c, d, ox, oy):
    ct, st = math.cos(theta), math.sin(theta)
    return S * (ct * (ox - c[0]) - st * (oy - c[1])) + d[0], S * (st * (ox - c[0]) + ct * (oy - c[1])) + d[1]


def sample(arr, coords, order=1):
    return map_coordinates(arr.astype(np.float32), coords, order=order, cval=0.0)


plates = {}
for k in big:
    yy_, xx_ = np.nonzero(pieces_lab == k)
    plates[k] = dict(c=(xx_.mean(), yy_.mean()))
for attempt in range(60):
    ok = True; masks = {}
    for k in big:
        c = plates[k]["c"]; u = np.array([c[0] - cx_all, c[1] - cy_all]); u = u / (np.linalg.norm(u) + 1e-6)
        D = r.uniform(60, 190)
        d = (MW / 2 + S * (c[0] - cx_all) + u[0] * D + r.uniform(-30, 30), MH / 2 + S * (c[1] - cy_all) + u[1] * D * 0.7 + r.uniform(-30, 30))
        th = math.radians(r.uniform(8, 30)) * r.choice([1, -1])
        plates[k].update(d=d, th=th)
        m = sample(pieces_lab == k, to_old(th, c, d)) > 0.5
        if m[:30].any() or m[-30:].any() or m[:, :30].any() or m[:, -30:].any():
            ok = False; break
        masks[k] = m
    if not ok:
        continue
    grown = {k: edt(~m) < 70 for k, m in masks.items()}
    if any((grown[a] & masks[b]).any() for a in big for b in big if a < b):
        continue
    break
print("placed after", attempt + 1, "tries;", len(big), "continents,", len(frags), "fragments")

crust = np.zeros((MH, MW), bool); dry = np.zeros((MH, MW), bool); elev = np.zeros((MH, MW), np.float32)
lakes = np.zeros((MH, MW), bool); rift_side = np.zeros((MH, MW), np.float32)
erode_at = None
for idx, k in enumerate(big):
    P = plates[k]; co = to_old(P["th"], P["c"], P["d"])
    ck = masks[k]
    ek = sample(elev_old * (pieces_lab == k), co)
    lk = sample(lakes_old & (pieces_lab == k), co) > 0.5
    rs = sample(near_rift & (pieces_lab == k), co)
    rs = uniform_filter(rs, 40)
    din = edt(ck)
    nz = g.noise(SEED + 70 + idx, 70, 3)
    boost = np.zeros_like(din)
    if erode_at is None and (rs > 0.3).any():
        ey, ex = np.nonzero((rs > 0.3) & (din < 6)); j = r.randrange(len(ex)); erode_at = (ex[j], ey[j], k)
        boost = np.exp(-((MX - ex[j]) ** 2 + (MY - ey[j]) ** 2) / (2 * 80 ** 2)) * 1.8
    shape_t = (1 + 1.1 * np.clip(rs * 2, 0, 1)) * (0.5 + 0.9 * nz) * (1 + boost)
    lo, hi = 0.0, 60.0
    for _ in range(30):
        t0 = (lo + hi) / 2
        land_k = ck & (din > t0 * shape_t)
        if land_k.sum() / ck.sum() > DRY:
            lo = t0
        else:
            hi = t0
    land_k = ck & (din > lo * shape_t)
    plates[k]["dry_share"] = land_k.sum() / ck.sum()
    plates[k]["dry_mask"] = land_k
    crust |= ck; dry |= land_k; elev = np.maximum(elev, ek); lakes |= lk & land_k; rift_side = np.maximum(rift_side, rs)
dry = fill_holes(dry.copy(), 40)
dry &= ~lakes

# fragments ride with the nearest continent but less eroded
for k in frags:
    yy_, xx_ = np.nonzero(pieces_lab == k); c = (xx_.mean(), yy_.mean())
    near = min(big, key=lambda b: math.hypot(plates[b]["c"][0] - c[0], plates[b]["c"][1] - c[1]))
    P = plates[near]; co = to_old(P["th"], P["c"], P["d"])
    m = sample(pieces_lab == k, co) > 0.5
    din = edt(m); crust |= m; dry |= m & (din > 3)

# the ridge: volcanic islands halfway between matching rift coasts
ridge_isles = []; seat = None
for pts in rifts:
    P0 = np.array([(x * OW, y * OH) for x, y in pts])
    for i in range(0, len(P0) - 1):
        q = P0[i]; t = P0[i + 1] - P0[i]; nrm = np.array([-t[1], t[0]]) / (np.linalg.norm(t) + 1e-6)
        a = (q + nrm * 14).astype(int); b = (q - nrm * 14).astype(int)
        if not (0 <= a[0] < OW and 0 <= a[1] < OH and 0 <= b[0] < OW and 0 <= b[1] < OH):
            continue
        ka, kb = pieces_lab[a[1], a[0]], pieces_lab[b[1], b[0]]
        if ka in plates and kb in plates and ka != kb:
            pa = to_new(plates[ka]["th"], plates[ka]["c"], plates[ka]["d"], q[0], q[1])
            pb = to_new(plates[kb]["th"], plates[kb]["c"], plates[kb]["d"], q[0], q[1])
            ridge_isles.append(((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2))
r.shuffle(ridge_isles)
kept = []
for (x, y) in ridge_isles:
    if all(math.hypot(x - a, y - b) > 70 for a, b in kept) and not crust[int(y), int(x)] and len(kept) < 7:
        kept.append((x, y))
for i, (x, y) in enumerate(kept):
    rad = r.uniform(5, 13) / MW if i else 15 / MW
    isl = g.rough(g.blob(x / MW, y / MH, rad, rad * 0.8, r.uniform(0, 3)), SEED + 90 + i, 0.4, 0.35, 20, 7) > 0
    dry |= isl
    elev = np.where(isl, np.maximum(elev, 0.7), elev)
if kept:
    jn = np.array([jx * OW, jy * OH])
    seat = min(kept, key=lambda p: min(math.hypot(p[0] - to_new(P["th"], P["c"], P["d"], *jn)[0], p[1] - to_new(P["th"], P["c"], P["d"], *jn)[1]) for P in plates.values()))

# rivers on today's land, and a delta grown out past the old edge at one rift-facing mouth
riv = rivers_for(dry, elev, r, 6, MW, MH)
delta = None
for pts in sorted(riv, key=len, reverse=True):
    ex, ey = pts[-1][0] * MW, pts[-1][1] * MH
    if rift_side[min(MH - 1, int(ey)), min(MW - 1, int(ex))] > 0.05 or pts is sorted(riv, key=len)[-1]:
        px, py = pts[-4][0] * MW, pts[-4][1] * MH
        dx, dy = ex - px, ey - py; L = math.hypot(dx, dy) + 1e-6
        cxd, cyd = ex + dx / L * 22, ey + dy / L * 22
        fan = g.rough(g.blob(cxd / MW, cyd / MH, 30 / MW, 24 / MW, math.atan2(dy, dx)), SEED + 99, 0.25, 0.3, 16, 6) > 0
        dry |= fan; delta = (cxd, cyd); break

seats = {"earth": (seat[0] / MW, seat[1] / MH)} if seat else {}
g.render(f"pg_now_{SEED}", np.where(dry, 1.0, -1.0), elev, SEED, 0, seats, riv)

# shelves: today's sea over old crust, lighter, with a dotted edge; sea stacks off the eroding coast
im = Image.open(g.OUT / f"ow_pg_now_{SEED}.png").convert("RGB"); a = np.asarray(im).copy()
shelf = crust & ~dry
a[shelf] = (a[shelf] * 0.55 + np.array([214, 220, 204]) * 0.45).astype(np.uint8)
outer = crust & ~(edt(crust) > 1.5)
dots = ((MX // 3 + MY // 3) % 3 == 0)
a[outer & ~dry & dots] = (94, 112, 102)
im = Image.fromarray(a); d = ImageDraw.Draw(im)
if erode_at:
    ex, ey, k = erode_at
    zone = shelf & (((MX - ex) ** 2 + (MY - ey) ** 2) < 70 ** 2) & (edt(~dry) < 26)
    zy, zx = np.nonzero(zone)
    for j in r.sample(range(len(zx)), min(26, len(zx))):
        x, y = zx[j], zy[j]; s = r.choice([2, 2, 3])
        d.ellipse((x - s, y - s, x + s, y + s), fill=(58, 46, 34))
im.save(g.OUT / f"ow_pg_now_{SEED}.png")

# ------------------------------------------------------------------ fit view (for us)
TINTS = [(214, 190, 150), (186, 200, 160), (210, 172, 160), (176, 192, 204), (200, 186, 210)]
fv = np.zeros((OH, OW, 3), np.float32); fv[:] = (185, 195, 178)
oy, ox = np.mgrid[0:OH, 0:OW]
for i, k in enumerate(big):
    P = plates[k]; nx_, ny_ = to_new(P["th"], P["c"], P["d"], ox, oy)
    still = map_coordinates(P["dry_mask"].astype(np.float32), [ny_, nx_], order=0, cval=0) > 0.5
    pk = pieces_lab == k
    tint = np.array(TINTS[i % len(TINTS)])
    fv[pk] = tint * 1.08
    fv[pk & still] = tint * 0.8
fv[land_old & ~np.isin(pieces_lab, big)] = (150, 140, 120)
fv = np.clip(fv, 0, 255).astype(np.uint8)
fim = Image.fromarray(fv); d = ImageDraw.Draw(fim)
lm = Image.fromarray((land_old * 255).astype(np.uint8))
edge = np.asarray(lm.filter(ImageFilter.MaxFilter(3)), bool) & ~np.asarray(lm.filter(ImageFilter.MinFilter(3)), bool)
fa = np.asarray(fim).copy(); fa[edge] = (58, 46, 34); fim = Image.fromarray(fa); d = ImageDraw.Draw(fim)
for pts in rifts:
    pp = [(x * OW, y * OH) for x, y in pts]
    for i in range(0, len(pp) - 1, 2):
        d.line([pp[i], pp[i + 1]], fill=(156, 74, 47), width=3)
d.rectangle((0, 0, OW - 1, OH - 1), outline=(58, 46, 34), width=3)
fim.save(g.OUT / f"ow_pg_fit_{SEED}.png")

print("dry share per continent:", [round(plates[k]["dry_share"], 3) for k in big])
print("shelf share of all crust:", round(float((crust & ~dry).sum() / crust.sum()), 3), "| ridge isles", len(kept), "| delta", delta is not None, "| eroding coast", erode_at is not None)
