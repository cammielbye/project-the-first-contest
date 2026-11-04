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
from scipy.ndimage import distance_transform_edt as edt, map_coordinates, label, uniform_filter, gaussian_filter
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
# three round lobes in a chain: A and C each share a long border with B and touch each other
# only across a short stretch. Try shapes until the borders come out that way and every piece
# is roundish (no strips) and in one piece.
N1 = (g.noise(SEED + 1, 150, 4) - 0.5) * 2; N2 = (g.noise(SEED + 2, 40, 3) - 0.5) * 2
WX = (g.noise(SEED + 3, 180, 3) - 0.5) * 2 * 60 + (g.noise(SEED + 8, 55, 3) - 0.5) * 2 * 14
WY = (g.noise(SEED + 4, 180, 3) - 0.5) * 2 * 60 + (g.noise(SEED + 9, 55, 3) - 0.5) * 2 * 14
SN = [0.36 * (g.noise(SEED + 25 + i, 170, 3) - 0.5) * 2 + 0.05 * (g.noise(SEED + 28 + i, 35, 3) - 0.5) * 2 for i in range(3)]
edgeness = np.clip(np.minimum.reduce([NX, 1 - NX, NY * OH / OW, (1 - NY) * OH / OW]) / 0.16, 0, 1)


def borders(lobe, land):
    bnd = np.zeros_like(land); pairs = []
    for dy, dx in ((0, 1), (1, 0)):
        a_ = lobe[:OH - dy, :OW - dx]; b_ = lobe[dy:, dx:]
        m_ = (a_ != b_) & land[:OH - dy, :OW - dx] & land[dy:, dx:]
        bnd[:OH - dy, :OW - dx] |= m_
        yy_, xx_ = np.nonzero(m_)
        pairs += list(zip(xx_, yy_, a_[m_], b_[m_]))
    return bnd, pairs


def stretch(m):
    yy_, xx_ = np.nonzero(m)
    ev = np.linalg.eigvalsh(np.cov(np.stack([xx_, yy_])))
    return math.sqrt(ev[1] / max(ev[0], 1e-6))


for tries in range(400):
    spin = r.uniform(0, 2 * math.pi); spread = r.uniform(1.7, 2.6)
    sizes = [r.uniform(0.175, 0.205), r.uniform(0.13, 0.15), r.uniform(0.09, 0.11)]; r.shuffle(sizes)
    rA, rB, rC = sizes
    RA = (rA + rB) * r.uniform(0.56, 0.66); RC = (rC + rB) * r.uniform(0.56, 0.66)
    cB = (0.0, 0.0)
    cA = (RA * math.cos(spin), RA * math.sin(spin) * OW / OH)
    cC = (RC * math.cos(spin + spread), RC * math.sin(spin + spread) * OW / OH)
    wsum = rA ** 2 + rB ** 2 + rC ** 2
    mx0 = (cA[0] * rA ** 2 + cC[0] * rC ** 2) / wsum; my0 = (cA[1] * rA ** 2 + cC[1] * rC ** 2) / wsum
    sh = (0.5 - mx0 + r.uniform(-0.04, 0.04), 0.5 - my0 + r.uniform(-0.04, 0.04))
    cA, cB, cC = [(c[0] + sh[0], c[1] + sh[1]) for c in (cA, cB, cC)]
    lobes = [(cA, rA), (cB, rB), (cC, rC)]
    fs = [lopsided(r, c[0], c[1], rr, r.uniform(1.0, 1.15), r.uniform(0, 3.1)) for c, rr in lobes]
    f = np.log(sum(np.exp(6 * fi) for fi in fs)) / 6 + 0.3 * N1 + 0.08 * N2
    f = map_coordinates(f, [np.clip(YY + WY, 0, OH - 1), np.clip(XX + WX, 0, OW - 1)], order=1)
    f = f - (1 - edgeness) ** 2 * 1.2
    land_old = gaussian_filter((f > np.quantile(f, 1 - 0.37)).astype(np.float32), 4.5) > 0.5
    land_old = fill_holes(land_old, 160)
    lab, n = label(land_old); sz = np.bincount(lab.ravel()); sz[0] = 0
    land_old = lab == np.argmax(sz)
    score = np.stack([np.hypot(NX - c[0], (NY - c[1]) * OH / OW) / rr + SN[i] for i, (c, rr) in enumerate(lobes)])
    lobe = np.argmin(score, axis=0)
    bnd, bpairs = borders(lobe, land_old)
    L = {k: sum(1 for p in bpairs if {p[2], p[3]} == k) for k in ({0, 1}, {1, 2}, {0, 2}) for k in [frozenset(k)]}
    lab_, ab_, bc_, ac_ = None, L[frozenset({0, 1})], L[frozenset({1, 2})], L[frozenset({0, 2})]
    if not (8 <= ac_ <= 0.28 * min(ab_, bc_)):
        continue
    ok = True
    for i in range(3):
        m = land_old & (lobe == i); share = m.sum() / land_old.sum()
        cl, cn = label(m); cs = np.bincount(cl.ravel()); cs[0] = 0
        if share < 0.1 or cs.max() < 0.95 * m.sum() or stretch(m) > 1.6:
            ok = False; break
    if ok:
        shares = sorted((land_old & (lobe == i)).sum() / land_old.sum() for i in range(3))
        ok = shares[2] > 0.42 and 0.12 < shares[0] < 0.23 and shares[2] / shares[0] > 2.2
    if ok:
        break
print("supercontinent after", tries + 1, "tries; borders A-B", ab_, "B-C", bc_, "A-C", ac_, "| shares", [round(x, 2) for x in shares])
dist_old = edt(land_old)
ys, xs = np.nonzero(land_old)
cx_all, cy_all = xs.mean(), ys.mean()

# the pieces are the lobes; the rifts run along the borders between them
corridor = edt(~bnd) < 3.5
rifts = []
pieces_lab, npcs = label(land_old & ~corridor)
psz = np.bincount(pieces_lab.ravel()); psz[0] = 0
big = [k for k in range(1, npcs + 1) if psz[k] > 0.05 * land_old.sum()]
frags = [k for k in range(1, npcs + 1) if 0 < psz[k] <= 0.05 * land_old.sum() and psz[k] > 120]
near_rift = edt(~corridor) < 16
comp_of = {}
for k in big:
    vals = np.bincount(lobe[pieces_lab == k], minlength=3); comp_of[int(np.argmax(vals))] = k
ac = [(x, y) for x, y, a_, b_ in bpairs if {a_, b_} == {0, 2}]
if ac:
    jx, jy = np.mean([p[0] for p in ac]) / OW, np.mean([p[1] for p in ac]) / OH
else:
    jx, jy = (cA[0] + cC[0]) / 2, (cA[1] + cC[1]) / 2

# features on the old land: a range that crosses the main rift, two more, a few lakes, rivers
e = 0.42 * g.noise(SEED + 30, 110) + 0.28 * np.clip(dist_old / 110, 0, 1)
ab = [(x, y) for x, y, a_, b_ in bpairs if {a_, b_} == {0, 1}]
mx_, my_ = (np.mean([p[0] for p in ab]) / OW, np.mean([p[1] for p in ab]) / OH) if ab else (cB[0], cB[1])
dx_, dy_ = cB[0] - cA[0], (cB[1] - cA[1]) * OH / OW; L_ = math.hypot(dx_, dy_) + 1e-6; dx_, dy_ = dx_ / L_, dy_ / L_
ranges = [[(mx_ - dx_ * 0.17, my_ - dy_ * 0.17 * OW / OH + 0.02), (mx_ - dx_ * 0.05, my_ - dy_ * 0.05 * OW / OH), (mx_ + dx_ * 0.07, my_ + dy_ * 0.07 * OW / OH - 0.01), (mx_ + dx_ * 0.18, my_ + dy_ * 0.18 * OW / OH + 0.02)]]
for k in [comp_of.get(2, big[-1]), r.choice(big)]:   # the far piece always gets a range of its own
    yy_, xx_ = np.nonzero((pieces_lab == k) & (dist_old > 40) & ~near_rift)
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
    if len(placed) >= 2:
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
from scipy.ndimage import binary_dilation
pts_of = {}
for k in big:
    yy_, xx_ = np.nonzero(pieces_lab == k); sel = slice(None, None, 7)
    pts_of[k] = (xx_[sel].astype(float), yy_[sel].astype(float))
placed_ok = False; attempt = 0
for S in (1.75, 1.62, 1.5, 1.4, 1.3):
    for attempt in range(150):
        grids = {}; ok = True
        for k in big:
            c = plates[k]["c"]; u = np.array([c[0] - cx_all, c[1] - cy_all]); u = u / (np.linalg.norm(u) + 1e-6)
            D = r.uniform(50, 170)
            d = (MW / 2 + S * (c[0] - cx_all) + u[0] * D + r.uniform(-30, 30), MH / 2 + S * (c[1] - cy_all) + u[1] * D * 0.7 + r.uniform(-30, 30))
            th = math.radians(r.uniform(8, 30)) * r.choice([1, -1])
            plates[k].update(d=d, th=th)
            nx_, ny_ = to_new(th, c, d, *pts_of[k])
            if nx_.min() < 36 or ny_.min() < 36 or nx_.max() > MW - 36 or ny_.max() > MH - 36:
                ok = False; break
            gk = np.zeros((MH // 8 + 1, MW // 8 + 1), bool); gk[(ny_ // 8).astype(int), (nx_ // 8).astype(int)] = True
            grids[k] = gk
        if not ok:
            continue
        grown = {k: binary_dilation(gk, iterations=8) for k, gk in grids.items()}
        if any((grown[a] & grids[b]).any() for a in big for b in big if a < b):
            continue
        placed_ok = True; break
    if placed_ok:
        break
masks = {k: sample(pieces_lab == k, to_old(plates[k]["th"], plates[k]["c"], plates[k]["d"])) > 0.5 for k in big}
print("placed:", placed_ok, "scale", S, "after", attempt + 1, "tries;", len(big), "continents,", len(frags), "fragments")

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
    sd = din - edt(~ck)
    nz = g.noise(SEED + 70 + idx, 220, 3)
    fine = (g.noise(SEED + 75 + idx, 70, 3) - 0.5) * 2
    mid = (g.noise(SEED + 77 + idx, 130, 3) - 0.5) * 2
    boost = np.zeros_like(din)
    if erode_at is None and (rs > 0.3).any():
        ey, ex = np.nonzero((rs > 0.3) & (din < 6)); j = r.randrange(len(ex)); erode_at = (ex[j], ey[j], k)
        boost = np.exp(-((MX - ex[j]) ** 2 + (MY - ey[j]) ** 2) / (2 * 80 ** 2)) * 1.8
    shape_t = (1 + 1.1 * np.clip(rs * 2, 0, 1)) * (0.65 + 0.7 * nz) * (1 + boost)
    wxk = (g.noise(SEED + 80 + idx, 90, 3) - 0.5) * 2 * 9; wyk = (g.noise(SEED + 85 + idx, 90, 3) - 0.5) * 2 * 9
    warp = lambda a: gaussian_filter(map_coordinates(a, [np.clip(MY + wyk, 0, MH - 1), np.clip(MX + wxk, 0, MW - 1)], order=1), 4)
    rag = gaussian_filter((g.noise(SEED + 79 + idx, 40, 3) - 0.5) * 2 * 19.0 + (g.noise(SEED + 82 + idx, 15, 2) - 0.5) * 2 * 5.5, 1.0)
    Gs, Gt, Gf = gaussian_filter(warp(sd), 17), warp(shape_t), warp(fine * 13.0 + mid * 18.0) + rag   # the wide blur wears the corners round
    lo, hi = 0.0, 60.0
    for _ in range(30):
        t0 = (lo + hi) / 2
        land_k = ck & ((Gs - t0 * Gt + Gf) > 0)
        if land_k.sum() / ck.sum() > DRY:
            lo = t0
        else:
            hi = t0
    land_k = ck & ((Gs - lo * Gt + Gf) > 0)
    plates[k]["dry_share"] = land_k.sum() / ck.sum()
    plates[k]["dry_mask"] = land_k
    crust |= ck; dry |= land_k; elev = np.maximum(elev, ek); lakes |= lk & land_k; rift_side = np.maximum(rift_side, rs)
dry = fill_holes(dry.copy(), 40)
lab_l, nl = label(lakes)                 # a lake the sea has reached is a bay now, so drop it
for j in range(1, nl + 1):
    if (edt(dry)[lab_l == j] < 12).any():
        lakes[lab_l == j] = False
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
for (bx, by, la, lb) in r.sample(bpairs, min(400, len(bpairs))):
    ka, kb = comp_of.get(int(la)), comp_of.get(int(lb))
    if ka in plates and kb in plates and ka != kb:
        pa = to_new(plates[ka]["th"], plates[ka]["c"], plates[ka]["d"], float(bx), float(by))
        pb = to_new(plates[kb]["th"], plates[kb]["c"], plates[kb]["d"], float(bx), float(by))
        t_ = r.uniform(0.28, 0.72)
        ridge_isles.append((pa[0] + (pb[0] - pa[0]) * t_ + r.uniform(-35, 35), pa[1] + (pb[1] - pa[1]) * t_ + r.uniform(-35, 35)))
r.shuffle(ridge_isles)
near_crust = edt(~crust) < 30
kept = []
for (x, y) in ridge_isles:
    if 40 < x < MW - 40 and 40 < y < MH - 40 and all(math.hypot(x - a, y - b) > 170 for a, b in kept) and not near_crust[int(y), int(x)] and len(kept) < 3:
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
fa = np.asarray(fim).copy(); dash = ((oy // 6 + ox // 6) % 2 == 0)
fa[(edt(~bnd) < 1.6) & dash] = (156, 74, 47); fim = Image.fromarray(fa); d = ImageDraw.Draw(fim)
d.rectangle((0, 0, OW - 1, OH - 1), outline=(58, 46, 34), width=3)
fim.save(g.OUT / f"ow_pg_fit_{SEED}.png")

print("dry share per continent:", [round(plates[k]["dry_share"], 3) for k in big])
print("shelf share of all crust:", round(float((crust & ~dry).sum() / crust.sum()), 3), "| ridge isles", len(kept), "| delta", delta is not None, "| eroding coast", erode_at is not None)
