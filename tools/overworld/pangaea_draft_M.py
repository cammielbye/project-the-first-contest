#!/usr/bin/env python3
"""Draft M (Nov 4), the working map: Draft L with the left continent a bit rounder, its cliff side curved and its
corners softened so the old fit is less obvious. Revised the same day for the hollow mountain (WORLD-13): see HOLLOW.

Draft L: Draft K with Cam's Nov 4 edits (the right continent turned back 30°, the middle island and the
right continent close with the left continent farther off, and ranges laid out to mislead; see "Draft L").

The supercontinent and the continents it broke into.

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
# ---- Draft L knobs (Cam, Nov 4: turn the right continent back ~30°; two pieces close, the third a little farther;
# ranges as misleading as possible)
TURN_R = 60         # the right continent's extra turn, clockwise, in degrees (K had 90)
GAP_MR = 40         # coast gap between the middle island and the right continent, today's px (close)
GAP_LM = 190        # coast gap between the left continent and the middle island (farther)
DROP_R = 0          # nudge the right continent down (+) or up (-)
X_LM = 0.55                # where the great range crosses the L-M rift, as a fraction along it
HIGH_TURN = 0              # the high half's heading across the middle piece, turned from "toward its centre" (degrees)
BEND_IN, BEND_DEG = 34, 40  # the bend: how far short of the M-R rift (old px), and how sharply it turns (degrees, + = clockwise)
LEN_L, LEN_R = 150, 115      # how far the great range runs into the left and right pieces (old px)
DECOY2_PICK, DECOY2_TURN, DECOY2_LEN = 0, -25, 105   # decoy 2: which coast candidate, its turn off 'inland', its length
Y1_IN, Y1_TURN, Y1_LEN = 55, 40, 210   # young range: straight run on the old line, then its turn and length
# ---- Draft M knobs (Cam, Nov 4: the left continent a bit rounder, its flat side lessened a bit)
CURVE = 55          # how far the cliffs curve back at the ends of the old rift (today's px); 0 = Draft L's straight run
SOFT = 22           # how round the corners are where the cliffs meet the rest of the coast (Draft L: 13)
REACH = 1.6         # how far along the coast the cliffs' shape holds, in half-lengths of the old rift (Draft L: 1.25)
# ---- The hollow mountain (WORLD-13, Cam, Nov 4): the whole middle island is one tall hollow mountain. Today's map draws it
# as a plateau ringed by cliffs with forest on top; the lake Cam moved there in Draft K is hidden inside as the harbour, so
# only the old map shows it; a sea cave on the coast nearest that lake, facing the narrow strait, lets ships in. Everything
# off the island is drawn exactly as before. False gives Draft M as first drawn.
HOLLOW = True


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
            seg = np.hypot(*np.diff(sm, axis=0).T); sl_ = np.concatenate([[0], np.cumsum(seg)]); Ltot = sl_[-1]
            ss = np.arange(0, Ltot, 3.0); qx = np.interp(ss, sl_, sm[:, 0]); qy = np.interp(ss, sl_, sm[:, 1])
            tx, ty = np.gradient(qx), np.gradient(qy); tn = np.hypot(tx, ty) + 1e-6; nx_, ny_ = -ty / tn, tx / tn
            lr = random.Random(int(x) * 7919 + int(y) * 104729 + W)
            l1, l2 = lr.uniform(0.06, 0.09) * W, lr.uniform(0.025, 0.035) * W; p1, p2 = lr.uniform(0, 6.3), lr.uniform(0, 6.3)
            amp = 0.009 * W * np.sin(np.pi * np.clip(ss / Ltot, 0, 1)) ** 0.6
            off_ = amp * (np.sin(2 * np.pi * ss / l1 + p1) + 0.45 * np.sin(2 * np.pi * ss / l2 + p2))
            wx_, wy_ = qx + nx_ * off_, qy + ny_ * off_
            okp = land[np.clip(wy_.astype(int), 0, H - 1), np.clip(wx_.astype(int), 0, W - 1)]
            okp[-3:] = True
            wx_, wy_ = np.where(okp, wx_, qx), np.where(okp, wy_, qy)
            out.append([(px / W, py / H) for px, py in zip(wx_[::2], wy_[::2])] + [(P[-1][0] / W, P[-1][1] / H)])
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
# ---- Cam's edits to Draft J (Nov 3), as revised for Draft L (Nov 4)
kL, kM, kR = sorted(big, key=lambda k: plates[k]["d"][0])     # left, middle and right on today's map
th0_R = plates[kR]["th"]
plates[kR]["th"] = th0_R + math.radians(TURN_R)               # K turned the right continent 90° clockwise; L turns it back 30°
# the left continent takes a slice off the middle piece's round west side, so their border runs straight there;
# today the left continent's cliffs follow that line, and the old horns either side of it have worn away to shelf
iL = int(np.bincount(lobe[pieces_lab == kL]).argmax()); iM = int(np.bincount(lobe[pieces_lab == kM]).argmax())
iR = 3 - iL - iM
area0 = int((land_old & (lobe == iM)).sum())
bLM = np.zeros_like(land_old)
for x, y, a_, b_ in bpairs:
    if {int(a_), int(b_)} == {iL, iM}: bLM[y, x] = True
bl_, bn_ = label(bLM, structure=np.ones((3, 3))); bLM = bl_ == np.bincount(bl_.ravel())[1:].argmax() + 1
yy_, xx_ = np.nonzero(bLM); bp = np.stack([xx_, yy_], 1).astype(float)
m0 = bp.mean(0); ev, evec = np.linalg.eigh(np.cov((bp - m0).T)); uu = evec[:, 1]
tb = (bp - m0) @ uu; pa, pb = bp[np.argmin(tb)], bp[np.argmax(tb)]
uu = (pb - pa) / np.linalg.norm(pb - pa); nn = np.array([-uu[1], uu[0]])
if np.median((bp - pa) @ nn) > 0: nn = -nn                 # nn points away from the left piece's side of the border
dmax = -float(((bp - pa) @ nn).min()); cut = 0.45 * dmax
set_size(OW, OH); wob = 3.0 * (g.noise(SEED + 61, 50, 2) - 0.5) * 2; set_size(MW, MH)
sline = (XX - pa[0]) * nn[0] + (YY - pa[1]) * nn[1] + cut + wob
lobe = np.where(land_old & (lobe == iM) & (sline < 0), iL, lobe)
LINE = dict(p=tuple(pa - nn * cut), u=uu, n=nn, L=float(np.linalg.norm(pb - pa)))
want = (area0 - int((land_old & (lobe == iM)).sum())) // 2
bp2 = np.array([(x, y) for x, y, a_, b_ in borders(lobe, land_old)[1] if {int(a_), int(b_)} == {iM, iR}], float)
m2 = bp2.mean(0); ev2, evec2 = np.linalg.eigh(np.cov((bp2 - m2).T)); u2 = evec2[:, 1]
t2 = (XX - m2[0]) * u2[0] + (YY - m2[1]) * u2[1]; tb2 = (bp2 - m2) @ u2; tc2, T2 = (tb2.max() + tb2.min()) / 2, (tb2.max() - tb2.min()) / 2
dR = edt(lobe != iM); prof = np.clip(1 - ((t2 - tc2) / T2) ** 2, 0, None)
lo_, hi_ = 0.0, 80.0
for _ in range(25):
    dl = (lo_ + hi_) / 2
    if (land_old & (lobe == iR) & (dR < dl * prof)).sum() < want: lo_ = dl
    else: hi_ = dl
lobe = np.where(land_old & (lobe == iR) & (dR < lo_ * prof), iM, lobe)
bnd, bpairs = borders(lobe, land_old)
corridor = edt(~bnd) < 3.5
kmap = np.zeros(3, int); kmap[iL], kmap[iM], kmap[iR] = kL, kM, kR
pieces_lab = np.where(land_old & ~corridor, kmap[lobe], 0)
near_rift = edt(~corridor) < 16
print("cap depth", round(dmax), "px, cut", round(cut), "| middle piece", area0, "->", int((land_old & (lobe == iM)).sum()),
      "| shares now", [round((pieces_lab == k).sum() / land_old.sum(), 2) for k in (kL, kM, kR)])
lab_lo, nlo = label(lakes_old)                                 # its lake goes...
for j in range(1, nlo + 1):
    if np.bincount(pieces_lab[lab_lo == j]).argmax() == kR:
        lakes_old[lab_lo == j] = False
inl = edt(pieces_lab == kM)                                    # ...to the bottom of the middle island
yy_, xx_ = np.nonzero(inl > 40)
P = plates[kM]; ny_ = to_new(P["th"], P["c"], P["d"], xx_.astype(float), yy_.astype(float))[1]
jb = int(np.argmax(ny_)); lx, ly = xx_[jb], yy_[jb]
set_size(OW, OH)
new_lake = g.rough(g.blob(lx / OW, ly / OH, 0.021, 0.021 * 0.62, P["th"] * -1 + 0.4), SEED + 57, 0.5, 0.4, 28, 9) > 0
set_size(MW, MH)
lakes_old |= new_lake & (pieces_lab == kM)
print("edits: new lake at", lx, ly)

# ---- Draft L spacing. Each piece keeps the exact coast it had in Draft K: its coast is worn by noise carried along
# with the piece, so moving or turning a piece moves its coast with it instead of wearing a new one. The coasts are
# then placed: the middle island and the right continent close, the left continent farther off.
from scipy.spatial import cKDTree
K_PLACE = {k: (plates[k]["th"], plates[k]["d"]) for k in big}
K_PLACE[kR] = (th0_R + math.pi / 2, plates[kR]["d"])
K_PLACE[kM] = (plates[kM]["th"], (plates[kM]["d"][0] - 38, plates[kM]["d"][1] + 6))
NOISE = {}


def erode(k, idx, th, d):
    """crust and dry land of piece k placed at (th, d), worn exactly as Draft K wore it"""
    c = plates[k]["c"]; thK, dK = K_PLACE[k]
    co = to_old(th, c, d); ck = sample(pieces_lab == k, co) > 0.5
    oy_, ox_ = co; xK, yK = to_new(thK, c, dK, ox_, oy_)
    rem = lambda a: map_coordinates(a, [yK, xK], order=1, mode="nearest")
    if idx not in NOISE:
        NOISE[idx] = dict(nz=g.noise(SEED + 70 + idx, 220, 3), fine=(g.noise(SEED + 75 + idx, 70, 3) - 0.5) * 2,
                          mid=(g.noise(SEED + 77 + idx, 130, 3) - 0.5) * 2,
                          wx=(g.noise(SEED + 80 + idx, 90, 3) - 0.5) * 2 * 9, wy=(g.noise(SEED + 85 + idx, 90, 3) - 0.5) * 2 * 9,
                          rag=gaussian_filter((g.noise(SEED + 79 + idx, 40, 3) - 0.5) * 2 * 19.0 + (g.noise(SEED + 82 + idx, 15, 2) - 0.5) * 2 * 5.5, 1.0),
                          bow=11.0 * (g.noise(SEED + 91, 150, 3) - 0.5) * 2 + 4.0 * (g.noise(SEED + 92, 45, 2) - 0.5) * 2)
    N = NOISE[idx]
    rs = uniform_filter(sample(near_rift & (pieces_lab == k), co), 40)
    din = edt(ck); sd = din - edt(~ck)
    nz, fine, mid, rag = rem(N["nz"]), rem(N["fine"]), rem(N["mid"]), rem(N["rag"])
    dt = th - thK; wx0, wy0 = rem(N["wx"]), rem(N["wy"])
    wxk = math.cos(dt) * wx0 - math.sin(dt) * wy0; wyk = math.sin(dt) * wx0 + math.cos(dt) * wy0
    shape_t = (1 + 1.1 * np.clip(rs * 2, 0, 1)) * (0.65 + 0.7 * nz)
    warp = lambda a: gaussian_filter(map_coordinates(a, [np.clip(MY + wyk, 0, MH - 1), np.clip(MX + wxk, 0, MW - 1)], order=1), 4)
    Gs, Gt, Gf = gaussian_filter(warp(sd), 17), warp(shape_t), warp(fine * 13.0 + mid * 18.0) + rag   # the wide blur wears the corners round
    W_ = np.zeros_like(din); C_ = np.zeros_like(din); cl = None
    if k == kL:   # the side that faced the middle piece wears back to a straight run of cliffs along the cut line
        ct_, st_ = math.cos(th), math.sin(th)
        p0 = np.array(to_new(th, c, d, *LINE["p"]))
        uu = np.array([ct_ * LINE["u"][0] - st_ * LINE["u"][1], st_ * LINE["u"][0] + ct_ * LINE["u"][1]])
        nn = np.array([ct_ * LINE["n"][0] - st_ * LINE["n"][1], st_ * LINE["n"][0] + ct_ * LINE["n"][1]])
        sl = (MX - p0[0]) * nn[0] + (MY - p0[1]) * nn[1]; tl = (MX - p0[0]) * uu[0] + (MY - p0[1]) * uu[1]
        tc, T = LINE["L"] * S / 2, LINE["L"] * S / 2
        W_ = np.clip((T * REACH - np.abs(tl - tc)) / (0.35 * T), 0, 1); W_ = W_ * W_ * (3 - 2 * W_)   # Draft M: the cliffs' reach runs on past the old horns (Draft L: 1.25)
        W_ = W_ * np.clip((sl + 170) / 60, 0, 1) * np.clip((150 - sl) / 40, 0, 1)
        # Draft M: the cliffs curve back toward their ends, so the side is a long gentle arc, not a straight cut,
        # and they meet the rest of the coast on wider rounded corners
        arc = CURVE * np.clip((tl - tc) / T, -1.8, 1.8) ** 2
        a_ = -13.0 - sl - arc + rem(N["bow"]) + 0.35 * rag; b_ = gaussian_filter(sd, 14) - 5.0 + 0.5 * rag
        C_ = -SOFT * np.logaddexp(-a_ / SOFT, -b_ / SOFT)
        cl = dict(W=W_ * (edt(~ck) < 70), n=nn, u=uu, m=p0)
    lo, hi = 0.0, 60.0
    for _ in range(30):
        t0 = (lo + hi) / 2
        land_k = ck & (((1 - W_) * (Gs - t0 * Gt + Gf) + W_ * C_) > 0)
        if land_k.sum() / ck.sum() > DRY:
            lo = t0
        else:
            hi = t0
    land_k = ck & (((1 - W_) * (Gs - lo * Gt + Gf) + W_ * C_) > 0)
    return dict(co=co, ck=ck, land=land_k, rs=rs, cliff=cl)


# pass 1: wear each piece where Draft K had it, and keep its coast and crust as shapes that ride with the piece
shape = {}
for idx, k in enumerate(big):
    thK, dK = K_PLACE[k]; E = erode(k, idx, thK, dK)
    ct, st = math.cos(-thK), math.sin(-thK)
    def back(m):
        yy_, xx_ = np.nonzero(m & ~(edt(m) > 1.5)); xx_, yy_ = xx_.astype(float), yy_.astype(float)
        return np.stack([(ct * (xx_ - dK[0]) - st * (yy_ - dK[1])) / S + plates[k]["c"][0],
                         (st * (xx_ - dK[0]) + ct * (yy_ - dK[1])) / S + plates[k]["c"][1]], 1)
    shape[k] = dict(coast=back(E["land"]), crust=back(E["ck"]))


def cloud(k, what="coast"):
    P = plates[k]; o = shape[k][what]; return np.stack(to_new(P["th"], P["c"], P["d"], o[:, 0], o[:, 1]), 1)


def gap(a, b, what="coast"):
    return float(cKDTree(cloud(a, what)).query(cloud(b, what), k=1)[0].min())


def slide_to(k, other, want, sign):
    """move piece k sideways (sign +1 = east) until its coast is `want` px from `other`'s"""
    x0, y0 = plates[k]["d"]; lo, hi = -600.0, 600.0
    for _ in range(30):
        mid = (lo + hi) / 2; plates[k]["d"] = (x0 + sign * mid, y0)
        if gap(k, other) < want: lo = mid
        else: hi = mid
    plates[k]["d"] = (x0 + sign * lo, y0)


for k in big:
    plates[k]["d"] = K_PLACE[k][1]
saved = {k: plates[k]["th"] for k in big}
for k in big: plates[k]["th"] = K_PLACE[k][0]
print("Draft K coast gaps: L-M", round(gap(kL, kM)), "M-R", round(gap(kM, kR)))
for k in big: plates[k]["th"] = saved[k]
plates[kR]["d"] = (plates[kR]["d"][0], plates[kR]["d"][1] + DROP_R)
slide_to(kR, kM, GAP_MR, +1)
slide_to(kL, kM, GAP_LM, -1)
allp = np.concatenate([cloud(k, "crust") for k in big])
sx = MW / 2 - (allp[:, 0].min() + allp[:, 0].max()) / 2; sy = MH / 2 - (allp[:, 1].min() + allp[:, 1].max()) / 2
for k in big:
    plates[k]["d"] = (plates[k]["d"][0] + sx, plates[k]["d"][1] + sy)
allp = np.concatenate([cloud(k, "crust") for k in big])
print("Draft L coast gaps: L-M", round(gap(kL, kM)), "M-R", round(gap(kM, kR)), "| crust gaps", round(gap(kL, kM, "crust")), round(gap(kM, kR, "crust")),
      "| crust margins x", round(allp[:, 0].min()), round(MW - allp[:, 0].max()), "y", round(allp[:, 1].min()), round(MH - allp[:, 1].max()))

# ---- Draft L ranges, built to mislead (on the old map, x/y in old pixels)
# One great range crosses the whole supercontinent: west through the left piece, over the L-M rift, across the
# middle piece to a bend near its east side, then south-east over the M-R rift into the right piece.
#  - true clue 1: its western half is still high on the left continent and the middle island, but the left
#    continent's cliffs have eaten its end, so it stops short of the strait;
#  - true clue 2: the half past the bend was already old and is worn down to low hills today;
#  - decoy 1: a young range rose on the right continent after the break, exactly where the high half's line
#    would land across the narrow strait. It is not on the old map;
#  - decoy 2: a second old range on the left continent runs straight into an outer coast, so it looks cut by a
#    rift, but that coast was always a coast.
set_size(OW, OH)
rr = random.Random(SEED + 700)
iL = int(np.bincount(lobe[pieces_lab == kL]).argmax()); iM = int(np.bincount(lobe[pieces_lab == kM]).argmax()); iR = 3 - iL - iM


def border_pts(i, j):
    return np.array([(x, y) for x, y, a_, b_ in bpairs if {int(a_), int(b_)} == {i, j}], float)


def axis_sorted(bp):
    m = bp.mean(0); ev, evec = np.linalg.eigh(np.cov((bp - m).T)); u = evec[:, 1]
    return bp[np.argsort((bp - m) @ u)]


cen = {i: np.array(np.nonzero(land_old & (lobe == i))[::-1], float).mean(1) for i in (iL, iM, iR)}
bLM_s = axis_sorted(border_pts(iL, iM)); bMR_s = axis_sorted(border_pts(iM, iR))
cross1 = bLM_s[int(len(bLM_s) * X_LM)]
toL = (cen[iL] - cross1) / np.linalg.norm(cen[iL] - cross1)
startL = cross1 + toL * LEN_L


def turn(v, deg):
    a = math.radians(deg); return np.array([v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a)])


# the high half heads across the middle piece and stops BEND_IN px short of the M-R rift; there it bends
# BEND_DEG (positive turns clockwise) and the worn half runs on over the rift into the right piece
mMR = np.zeros_like(land_old); bmr = border_pts(iM, iR).astype(int); mMR[bmr[:, 1], bmr[:, 0]] = True
dMR = edt(~mMR)
v_hi = turn((cen[iM] - cross1) / np.linalg.norm(cen[iM] - cross1), HIGH_TURN)
p_ = cross1.copy()
for _ in range(600):
    p_ = p_ + v_hi
    if lobe[int(p_[1]), int(p_[0])] == iM and dMR[int(p_[1]), int(p_[0])] < BEND_IN:
        break
bend = p_.copy(); v_wo = turn(v_hi, BEND_DEG)
for _ in range(600):
    p_ = p_ + v_wo
    if lobe[int(p_[1]), int(p_[0])] == iR or not land_old[int(p_[1]), int(p_[0])]:
        break
cross2 = p_.copy(); endR = cross2 + v_wo * LEN_R
great = [tuple(startL), tuple((startL + cross1) / 2 + np.array([0, -8])), tuple(cross1), tuple(bend), tuple((bend + cross2) / 2), tuple(endR)]
great_n = [(x / OW, y / OH) for x, y in great]
gm = g.meander(great_n, SEED + 41, 0.012)
split = 30                                                      # g.meander gives 10 points per leg; the bend is point 3
high_pts, worn_pts = gm[:split + 1], gm[split:]
# decoy 2: an old range on the left piece that runs to an outer coast (one facing north or south today)
dB = edt(~bnd); coast_old = land_old & ~(edt(land_old) > 1.5)
cand = np.argwhere(coast_old & (lobe == iL) & (dB > 110)); dLk = edt(~lakes_old)
P = plates[kL]
ok_c = []
for (y, x) in cand[::3]:
    tx, ty = to_new(P["th"], P["c"], P["d"], float(x), float(y)); cxL, cyL = to_new(P["th"], P["c"], P["d"], *cen[iL])
    v = np.array([tx - cxL, ty - cyL]); v /= np.linalg.norm(v)
    if abs(v[1]) < 0.6:
        continue
    inw = turn((cen[iL] - np.array([x, y])) / np.linalg.norm(cen[iL] - np.array([x, y])), DECOY2_TURN)
    d2 = [(x - inw[0] * 6, y - inw[1] * 6), (x + inw[0] * DECOY2_LEN * 0.45, y + inw[1] * DECOY2_LEN * 0.45 + 5), (x + inw[0] * DECOY2_LEN, y + inw[1] * DECOY2_LEN)]
    along = [(x + inw[0] * t, y + inw[1] * t) for t in range(0, DECOY2_LEN + 1, 10)]
    far_lakes = min(dLk[int(b), int(a)] for a, b in along) > 35
    far_great = min(math.hypot(a - px * OW, b - py * OH) for a, b in along for px, py in gm[::2]) > 80
    if far_lakes and far_great:
        ok_c.append((abs(v[1]), x, y, d2))
print("decoy 2 candidates:", len(ok_c)); ok_c.sort(key=lambda t: -t[0]); _, x3, y3, d2 = ok_c[min(DECOY2_PICK, len(ok_c) - 1)]
decoy2_pts = g.meander([(x / OW, y / OH) for x, y in d2], SEED + 43, 0.01)
base = 0.42 * g.noise(SEED + 30, 110) + 0.28 * np.clip(dist_old / 110, 0, 1)
r_high = g.ridge_line(high_pts, 0.035); r_worn = g.ridge_line(worn_pts, 0.035); r_d2 = g.ridge_line(decoy2_pts, 0.04)
inl_ = dist_old > 6
elev_old = np.clip(base + (0.44 * np.maximum(r_high, r_worn) + 0.5 * r_d2) * inl_, 0, 1)       # the old map: all of it high
elev_src = np.clip(base + (0.44 * r_high + 0.5 * r_d2) * inl_, 0, 1)                             # what is still high today
worn_old = (r_worn > 0.22) & inl_ & (r_high < 0.3)
set_size(MW, MH)
print("ranges: crossing L-M", cross1.round(), "bend", bend.round(), "crossing M-R", cross2.round(), "| decoy 2 at", x3, y3)
print("placed:", placed_ok, "scale", S, "after", attempt + 1, "tries;", len(big), "continents,", len(frags), "fragments")

crust = np.zeros((MH, MW), bool); dry = np.zeros((MH, MW), bool); elev = np.zeros((MH, MW), np.float32)
lakes = np.zeros((MH, MW), bool); rift_side = np.zeros((MH, MW), np.float32); worn = np.zeros((MH, MW), bool)
erode_at = None
for idx, k in enumerate(big):
    P = plates[k]; E = erode(k, idx, P["th"], P["d"])
    co, ck, land_k, rs = E["co"], E["ck"], E["land"], E["rs"]
    if E["cliff"] is not None:
        cliff = E["cliff"]
    ek = sample(elev_src * (pieces_lab == k), co)
    worn |= sample(worn_old & (pieces_lab == k), co) > 0.5
    lk = sample(lakes_old & (pieces_lab == k), co) > 0.5
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
ridge_isles = []; seat = None; isle_pair = {}
for (bx, by, la, lb) in r.sample(bpairs, min(400, len(bpairs))):
    ka, kb = comp_of.get(int(la)), comp_of.get(int(lb))
    if ka in plates and kb in plates and ka != kb:
        pa = to_new(plates[ka]["th"], plates[ka]["c"], plates[ka]["d"], float(bx), float(by))
        pb = to_new(plates[kb]["th"], plates[kb]["c"], plates[kb]["d"], float(bx), float(by))
        t_ = r.uniform(0.28, 0.72)
        ridge_isles.append((pa[0] + (pb[0] - pa[0]) * t_ + r.uniform(-35, 35), pa[1] + (pb[1] - pa[1]) * t_ + r.uniform(-35, 35)))
        isle_pair[ridge_isles[-1]] = frozenset((ka, kb))
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
lm_isles = [p for p in kept if isle_pair.get(p) == frozenset((kL, kM))]
if lm_isles:                     # Draft L: the earth seat stays where K had it, off the middle of the left continent's cliffs
    cm = cliff["m"] + cliff["u"] * LINE["L"] * S / 2
    seat = min(lm_isles, key=lambda p: math.hypot(p[0] - cm[0], p[1] - cm[1]))
elif kept:
    jn = np.array([jx * OW, jy * OH])
    seat = min(kept, key=lambda p: min(math.hypot(p[0] - to_new(P["th"], P["c"], P["d"], *jn)[0], p[1] - to_new(P["th"], P["c"], P["d"], *jn)[1]) for P in plates.values()))

# decoy 1: the young range. Follow the high half's line off the middle island, across the strait, to where it
# lands on the right continent, and raise a range there that carries on the same line and then turns along the coast.
P = plates[kM]
e1 = np.array(to_new(P["th"], P["c"], P["d"], high_pts[-1][0] * OW, high_pts[-1][1] * OH))
e0 = np.array(to_new(P["th"], P["c"], P["d"], high_pts[-8][0] * OW, high_pts[-8][1] * OH))
v = (e1 - e0) / np.linalg.norm(e1 - e0)
dR_ = plates[kR]["dry_mask"] & dry
hit = None
for t in range(0, 700, 2):
    x, y = (e1 + v * t).astype(int)
    if not (0 <= x < MW and 0 <= y < MH):
        break
    if dR_[y, x]:
        hit = e1 + v * t; break
young_pts = []
if hit is None:
    print("WARNING: the high range's line misses the right continent")
else:
    best = None
    for sgn in (1, -1):
        a = math.radians(Y1_TURN) * sgn; w = np.array([v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a)])
        knee = hit + v * Y1_IN
        pts = [hit - v * 6, hit + v * Y1_IN * 0.5, knee, knee + (v + w) / np.linalg.norm(v + w) * Y1_LEN * 0.4, knee + w * Y1_LEN]
        inside = sum(dR_[int(min(MH - 1, max(0, py))), int(min(MW - 1, max(0, px)))] for px, py in
                     [tuple(pts[2] + (pts[4] - pts[2]) * f) for f in np.linspace(0, 1, 20)])
        if best is None or inside > best[0]:
            best = (inside, pts)
    young_pts = best[1]
    yr = g.ridge_line(g.meander([(x / MW, y / MH) for x, y in young_pts], SEED + 45, 0.006), 0.019)
    elev = np.clip(np.maximum(elev, elev + 0.46 * yr * (edt(dR_) > 5)), 0, 1)
    print("young range lands at", hit.round(), "| turn", Y1_TURN, "| on land", best[0], "of 20")

# rivers on today's land, and a delta grown out past the old edge at one rift-facing mouth
riv = rivers_for(dry, elev, r, 6, MW, MH)
delta = None
rs_wide = uniform_filter(rift_side, 60)      # Draft L: the delta goes to the river mouth that faces a rift the most
mouths = [p for p in riv if cliff['W'][min(MH - 1, int(p[-1][1] * MH)), min(MW - 1, int(p[-1][0] * MW))] <= 0.05]
for pts in sorted(mouths, key=lambda p: -rs_wide[min(MH - 1, int(p[-1][1] * MH)), min(MW - 1, int(p[-1][0] * MW))])[:1]:
    ex, ey = pts[-1][0] * MW, pts[-1][1] * MH
    if rs_wide[min(MH - 1, int(ey)), min(MW - 1, int(ex))] > 0.02:     # only a delta on a rift-facing coast is a clue
        px, py = pts[-4][0] * MW, pts[-4][1] * MH
        dx, dy = ex - px, ey - py; L = math.hypot(dx, dy) + 1e-6
        cxd, cyd = ex + dx / L * 22, ey + dy / L * 22
        fan = g.rough(g.blob(cxd / MW, cyd / MH, 30 / MW, 24 / MW, math.atan2(dy, dx)), SEED + 99, 0.25, 0.3, 16, 6) > 0
        dry |= fan; delta = (cxd, cyd); print("delta at", round(cxd), round(cyd), "| rift-facing", round(float(rs_wide[int(ey), int(ex)]), 3)); break

seats = {"earth": (seat[0] / MW, seat[1] / MH)} if seat else {}
g.render(f"pg_now_{SEED}", np.where(dry, 1.0, -1.0), elev, SEED, 0, seats, riv)
dry_r = dry
if HOLLOW:   # draw the island a second time as the hollow mountain and paste it in, so nothing else on the map moves
    from scipy.ndimage import binary_dilation as _dil
    kMask = plates[kM]["dry_mask"]
    hidden = lakes & kMask                                       # the old lake, now the harbour inside
    lab_i, _n = label(dry | hidden)
    keep_i = [j for j in np.unique(lab_i[kMask & (lab_i > 0)]) if (kMask[lab_i == j]).mean() > 0.5]
    I = np.isin(lab_i, keep_i)
    dry_r = dry | hidden
    elev_r = elev.copy(); elev_r[I] = 0.5                        # a flat top: no peaks, no river springs
    riv_r = [p for p in riv if not I[min(MH - 1, int(p[0][1] * MH)), min(MW - 1, int(p[0][0] * MW))]]
    g.render(f"pg_hollow_{SEED}", np.where(dry_r, 1.0, -1.0), elev_r, SEED, 0, seats, riv_r)
    base_ = np.asarray(Image.open(g.OUT / f"ow_pg_now_{SEED}.png").convert("RGB")).copy()
    hol_ = np.asarray(Image.open(g.OUT / f"ow_pg_hollow_{SEED}.png").convert("RGB"))
    region = _dil(I, iterations=12)
    base_[region] = hol_[region]
    Image.fromarray(base_).save(g.OUT / f"ow_pg_now_{SEED}.png")
    hy_, hx_ = np.nonzero(hidden)
    harbour = (float(hx_.mean()), float(hy_.mean())) if len(hx_) else None
    print("hollow mountain: island", int(I.sum()), "px | harbour (hidden lake) at", [round(v) for v in harbour] if harbour else None,
          "| rivers dropped", len(riv) - len(riv_r))

# shelves: today's sea over old crust, lighter, with a dotted edge; sea stacks off the eroding coast
im = Image.open(g.OUT / f"ow_pg_now_{SEED}.png").convert("RGB"); a = np.asarray(im).copy()
shelf = crust & ~dry_r
a[shelf] = (a[shelf] * 0.55 + np.array([214, 220, 204]) * 0.45).astype(np.uint8)
outer = crust & ~(edt(crust) > 1.5)
dots = ((MX // 3 + MY // 3) % 3 == 0)
a[outer & ~dry_r & dots] = (94, 112, 102)
im = Image.fromarray(a); d = ImageDraw.Draw(im)
if True:
    Wc, nn = cliff["W"], cliff["n"]
    coast = dry & ~(edt(dry) > 1.5) & (Wc > 0.55)
    cy_, cx_ = np.nonzero(coast); tt = (cx_ - cliff["m"][0]) * cliff["u"][0] + (cy_ - cliff["m"][1]) * cliff["u"][1]
    last = -1e9
    for j in np.argsort(tt):
        if tt[j] - last >= 9:
            x, y = cx_[j], cy_[j]; L_ = 9 if (int(tt[j]) // 9) % 2 else 6
            d.line([(x, y), (x - nn[0] * L_, y - nn[1] * L_)], fill=(58, 46, 34), width=2); last = tt[j]
    zone = ~dry & (Wc > 0.5) & (edt(~dry) < 28) & (edt(~dry) > 6)
    zy, zx = np.nonzero(zone)
    for j in r.sample(range(len(zx)), min(32, len(zx))):
        x, y = zx[j], zy[j]; s = r.choice([2, 2, 3])
        d.ellipse((x - s, y - s, x + s, y + s), fill=(58, 46, 34))
# the worn half of the great range: low hills, drawn as small humps
hy, hx = np.nonzero(worn & dry & (edt(dry) > 7) & ~lakes)
hr = random.Random(SEED + 710); kept_h = []
for j in hr.sample(range(len(hx)), len(hx)):
    x, y = int(hx[j]), int(hy[j])
    if all((x - a) ** 2 + (y - b) ** 2 > 13 ** 2 for a, b in kept_h):
        kept_h.append((x, y))
for x, y in kept_h:
    w_ = hr.choice([5, 6, 7])
    if HOLLOW and I[y, x]:
        continue                                                 # no hills on the hollow mountain's flat top
    d.arc((x - w_, y - 4, x + w_, y + 5), 190, 350, fill=(58, 46, 34), width=2)
print("worn hills drawn:", len(kept_h))
if HOLLOW:
    hr2 = random.Random(SEED + 720)
    di = edt(I)
    # forest on top: crowns packed on a jittered grid, clear of the rim
    ys_, xs_ = np.nonzero(I)
    for row, gy in enumerate(range(int(ys_.min()), int(ys_.max()) + 1, 9)):
        for gx in range(int(xs_.min()) + (5 if row % 2 else 0), int(xs_.max()) + 1, 10):
            x, y = gx + hr2.randint(-2, 2), gy + hr2.randint(-2, 2)
            if 0 <= x < MW and 0 <= y < MH and di[y, x] > 13:
                s_ = hr2.choice([3, 3, 4])
                d.ellipse((x - s_, y - s_, x + s_, y + s_), outline=g.FOREST, width=1)
                d.arc((x - s_ + 1, y - s_ + 1, x + s_ - 1, y + s_ - 1), 200, 300, fill=(92, 102, 70), width=1)
    # the sea cave: on the coast nearest the hidden harbour, facing the narrow strait (east)
    gsm = gaussian_filter(di.astype(float), 3); gyy, gxx = np.gradient(gsm)
    cst = I & ~(di > 1.5)
    cy_, cx_ = np.nonzero(cst)
    nrm = np.hypot(gxx[cy_, cx_], gyy[cy_, cx_]) + 1e-6
    inx, iny = gxx[cy_, cx_] / nrm, gyy[cy_, cx_] / nrm
    cave = None
    if harbour:
        cand = np.nonzero(-inx > 0.45)[0]
        j = cand[np.argmin((cx_[cand] - harbour[0]) ** 2 + (cy_[cand] - harbour[1]) ** 2)]
        cave = (int(cx_[j]), int(cy_[j]), float(inx[j]), float(iny[j]))
    # the cliffs: hachures all round the rim, pointing in, broken where the cave opens
    kept_t = []
    for j in hr2.sample(range(len(cx_)), len(cx_)):
        x, y = int(cx_[j]), int(cy_[j])
        if cave and (x - cave[0]) ** 2 + (y - cave[1]) ** 2 < 10 ** 2:
            continue
        if all((x - a) ** 2 + (y - b) ** 2 > 8 ** 2 for a, b in kept_t):
            kept_t.append((x, y))
            L_ = hr2.choice([6, 8, 9])
            d.line([(x, y), (x + inx[j] * L_, y + iny[j] * L_)], fill=(58, 46, 34), width=2)
    if cave:
        x, y, nx_, ny_ = cave
        cx0, cy0 = x + nx_ * 2.5, y + ny_ * 2.5
        d.ellipse((cx0 - 5, cy0 - 5, cx0 + 5, cy0 + 5), fill=(58, 46, 34))
        d.ellipse((cx0 - 2, cy0 - 2, cx0 + 2, cy0 + 2), fill=(26, 20, 16))
    print("hollow mountain drawn: cliff hachures", len(kept_t), "| sea cave at", cave[:2] if cave else None)
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
# the ranges, for us: the great range (solid where still high, dashed where worn to hills), decoy 2 in rust,
# and the young range (decoy 1) carried back onto the old map in rust dashes, where it did not yet exist
def pline(pts, fill, width, dash=None):
    pp = [(x * OW, y * OH) for x, y in pts]
    if dash is None:
        d.line(pp, fill=fill, width=width, joint="curve"); return
    seg = []; acc = 0.0; on = True
    for (x0, y0), (x1, y1) in zip(pp, pp[1:]):
        L = math.hypot(x1 - x0, y1 - y0); n = max(1, int(L / 2))
        for i in range(n):
            ax, ay = x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n; bx, by = x0 + (x1 - x0) * (i + 1) / n, y0 + (y1 - y0) * (i + 1) / n
            if on: d.line([(ax, ay), (bx, by)], fill=fill, width=width)
            acc += L / n
            if acc >= dash: acc = 0.0; on = not on
pline(high_pts, (58, 46, 34), 4)
pline(worn_pts, (58, 46, 34), 4, dash=7)
pline(decoy2_pts, (156, 74, 47), 4)
if young_pts:
    P = plates[kR]; ct, st = math.cos(-P["th"]), math.sin(-P["th"])
    back = [((ct * (x - P["d"][0]) - st * (y - P["d"][1])) / S + P["c"][0], (st * (x - P["d"][0]) + ct * (y - P["d"][1])) / S + P["c"][1]) for x, y in young_pts]
    pline([(x / OW, y / OH) for x, y in back], (156, 74, 47), 4, dash=7)
d.rectangle((0, 0, OW - 1, OH - 1), outline=(58, 46, 34), width=3)
fim.save(g.OUT / f"ow_pg_fit_{SEED}.png")

set_size(OW, OH)
dry_old = land_old & ~lakes_old
riv_old = rivers_for(dry_old, elev_old, random.Random(SEED + 500), 4, OW, OH)
g.render(f"pg_old_{SEED}", np.where(dry_old, 1.0, -1.0), elev_old, SEED, 0, {}, riv_old)
age(g.OUT / f"ow_pg_old_{SEED}.png", seed=SEED)
print("dry share per continent:", [round(plates[k]["dry_share"], 3) for k in big])
print("shelf share of all crust:", round(float((crust & ~dry).sum() / crust.sum()), 3), "| ridge isles", len(kept), "| delta", delta is not None, "| eroding coast", erode_at is not None)
