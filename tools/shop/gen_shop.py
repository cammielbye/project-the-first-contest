# Pixel art for the sample shop: a scene (360x200) and the cabinet close-up (360x230), both drawn
# in flat colours, lit, then squeezed into a small palette with ordered dithering, and scaled x4.
import math, random, sys
from PIL import Image
OUT = sys.argv[1]
random.seed(4)

PAL = ["#0f0c0a", "#1a1410", "#241a14", "#2e2119", "#3b2a1e", "#4a3424", "#5b402b", "#6e4e33", "#85613f", "#a07a4c",
       "#c99a55", "#e3bf7a", "#f4dca0", "#1c2620", "#25332b", "#314237", "#3f5345", "#56685a", "#3a3a38", "#55534e",
       "#77736a", "#9e988b", "#c9c2b0", "#e8dfc8", "#4a1c1a", "#6e2a24", "#93392d", "#2b3a44", "#445866", "#6f8794",
       "#a9bcc4", "#c9a07c", "#a97f5e", "#e0bc98", "#7a5a44"]
hexrgb = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
P = [hexrgb(h) for h in PAL]
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]

class Canvas:
    def __init__(s, w, h, bg):
        s.w, s.h = w, h
        s.px = [[hexrgb(bg) for _ in range(w)] for _ in range(h)]
        s.lit = [[True] * w for _ in range(h)]   # False: drawn after lighting (no light falloff)
    def put(s, x, y, c):
        if 0 <= x < s.w and 0 <= y < s.h: s.px[y][x] = hexrgb(c) if isinstance(c, str) else c
    def rect(s, x0, y0, x1, y1, c):
        for y in range(max(0, y0), min(s.h, y1)):
            for x in range(max(0, x0), min(s.w, x1)): s.put(x, y, c)
    def hline(s, x0, x1, y, c): s.rect(x0, y, x1, y + 1, c)
    def vline(s, x, y0, y1, c): s.rect(x, y0, x + 1, y1, c)
    def checker(s, x0, y0, x1, y1, a, b):
        for y in range(y0, y1):
            for x in range(x0, x1): s.put(x, y, a if (x + y) % 2 else b)
    def sprite(s, x0, y0, rows, key):
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch in key: s.put(x0 + i, y0 + j, key[ch])

def light(cv, lamps, ambient=0.42, vx=0.28, vy=0.18):
    for y in range(cv.h):
        for x in range(cv.w):
            r, g, b = cv.px[y][x]
            k_r = k_g = k_b = ambient
            for (lx, ly, rad, strength, tint) in lamps:
                d = math.hypot(x - lx, (y - ly) * 1.15) / rad
                f = max(0.0, 1 - d) ** 1.6 * strength
                k_r += f * tint[0]; k_g += f * tint[1]; k_b += f * tint[2]
            vig = 1 - vx * (((x / cv.w - .5) * 2) ** 2) - vy * (((y / cv.h - .45) * 2) ** 2)
            cv.px[y][x] = (min(255, r * k_r * vig), min(255, g * k_g * vig), min(255, b * k_b * vig))

def quantize(cv, spread=26):
    img = Image.new("RGB", (cv.w, cv.h))
    for y in range(cv.h):
        for x in range(cv.w):
            r, g, b = cv.px[y][x]
            t = (BAYER[y % 4][x % 4] / 16 - 0.5) * spread
            r, g, b = r + t, g + t, b + t
            best = min(P, key=lambda p: (p[0] - r) ** 2 * .9 + (p[1] - g) ** 2 * 1.2 + (p[2] - b) ** 2 * .7)
            img.putpixel((x, y), best)
    return img

# a 3x5 font for painted signs
FONT = {
    "H": ["101", "101", "111", "101", "101"], "O": ["111", "101", "101", "101", "111"], "L": ["100", "100", "100", "100", "111"],
    "I": ["111", "010", "010", "010", "111"], "S": ["111", "100", "111", "001", "111"], "G": ["011", "100", "101", "101", "011"],
    "A": ["010", "101", "111", "101", "101"], "M": ["101", "111", "111", "101", "101"], "E": ["111", "100", "110", "100", "111"],
    "C": ["111", "100", "100", "100", "111"], "U": ["101", "101", "101", "101", "111"], "R": ["110", "101", "110", "101", "101"],
    "&": ["010", "101", "010", "101", "011"], " ": ["000", "000", "000", "000", "000"], "N": ["101", "111", "111", "111", "101"],
    "P": ["110", "101", "110", "100", "100"], "D": ["110", "101", "101", "101", "110"], "W": ["101", "101", "111", "111", "101"],
}
def text(cv, x, y, s, c):
    for ch in s:
        g = FONT[ch]
        for j in range(5):
            for i in range(3):
                if g[j][i] == "1": cv.put(x + i, y + j, c)
        x += 4

ELEMENT = ["#d0663f", "#7fa7b5", "#d5d8cc", "#a88f6b"]
def tiny_card(cv, x, y, el):  # an 8x11 card standing on a shelf, face out
    cv.rect(x, y, x + 8, y + 11, "#c9c2b0")
    cv.rect(x + 1, y + 1, x + 7, y + 10, "#3a3a38")
    cv.rect(x + 1, y + 1, x + 7, y + 6, "#25332b")
    cv.put(x + 3, y + 3, ELEMENT[el]); cv.put(x + 4, y + 3, ELEMENT[el]); cv.put(x + 4, y + 2, ELEMENT[el])
    cv.hline(x + 2, x + 6, y + 7, "#77736a"); cv.hline(x + 2, x + 5, y + 8, "#55534e")
    cv.rect(x, y + 11, x + 8, y + 12, "#1a1410")

def wood_panel(cv, x0, y0, x1, y1, base="#4a3424", dark="#3b2a1e", hi="#5b402b"):
    cv.rect(x0, y0, x1, y1, base)
    cv.hline(x0, x1, y0, hi); cv.hline(x0, x1, y1 - 1, dark)
    for y in range(y0 + 2, y1 - 1, 3):
        for x in range(x0, x1):
            if random.random() < 0.18: cv.put(x, y, dark)


def disc(cv, cx, cy, r, c):
    for y in range(int(cy - r), int(cy + r) + 1):
        for x in range(int(cx - r), int(cx + r) + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r: cv.put(x, y, c)
def poly(cv, pts, c):
    ys = [p[1] for p in pts]
    for y in range(int(min(ys)), int(max(ys)) + 1):
        xs = []
        for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for a, b in zip(xs[::2], xs[1::2]):
            for x in range(int(round(a)), int(round(b))): cv.put(x, y, c)
SMUDGE = {"f": ("#d0663f", "#93392d"), "w": ("#7fa7b5", "#445866"), "a": ("#d5d8cc", "#9e988b"), "e": ("#a88f6b", "#6e4e33")}
def smudge_card(cv, x, y, els):  # a card on the table: a 4x5 blur of its affinity colours
    cv.rect(x, y, x + 4, y + 5, "#55534e")
    for i, e in enumerate(els):
        hi, lo = SMUDGE[e]
        for (dx, dy) in ((1, 1 + i), (2, 1 + i), (1, 2 + i), (2, 3)):
            cv.put(x + dx, y + dy, hi if (dx + dy) % 2 else lo)
    cv.hline(x, x + 4, y + 5, "#1a1410")


# ---- figures: drawn on a layer, then stamped with a dark outline so the silhouette reads
class Layer:
    def __init__(s): s.px = {}
    def put(s, x, y, c): s.px[(int(x), int(y))] = c
    def ellipse(s, cx, cy, rx, ry, c, keep=None):
        for y in range(int(cy - ry - 1), int(cy + ry + 2)):
            for x in range(int(cx - rx - 1), int(cx + rx + 2)):
                if ((x + .5 - cx) / rx) ** 2 + ((y + .5 - cy) / ry) ** 2 <= 1 and (keep is None or keep(x, y)): s.put(x, y, c)
    def poly(s, pts, c, keep=None):
        ys = [p[1] for p in pts]
        for y in range(int(min(ys)), int(max(ys)) + 1):
            yc = y + .5; xs = []
            for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
                if (y0 <= yc < y1) or (y1 <= yc < y0): xs.append(x0 + (yc - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for a, b in zip(xs[::2], xs[1::2]):
                for x in range(int(round(a)), int(round(b))):
                    if keep is None or keep(x, y): s.put(x, y, c)
    def rect(s, x0, y0, x1, y1, c):
        for y in range(int(y0), int(y1)):
            for x in range(int(x0), int(x1)): s.put(x, y, c)
    def limb(s, x0, y0, x1, y1, w, c, edge=None):
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 3) + 1
        for pass_ in ((edge, w / 2 + .9), (c, w / 2)) if edge else ((c, w / 2),):
            col, r = pass_
            for i in range(n + 1):
                tx = x0 + (x1 - x0) * i / n; ty = y0 + (y1 - y0) * i / n
                s.ellipse(tx, ty, r, r, col)
    def shade(s, pred, frm, to):
        for k, c in list(s.px.items()):
            if c == frm and pred(*k): s.px[k] = to
    def flipped(s, ax):
        L = Layer(); L.px = {(int(2 * ax - x), y): c for (x, y), c in s.px.items()}; return L
    def stamp(s, cv, outline="#1a1410"):
        for (x, y) in s.px:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (x + dx, y + dy) not in s.px: cv.put(x + dx, y + dy, outline)
        for (x, y), c in s.px.items(): cv.put(x, y, c)

def chair(cv, hx, hy, back_left=True):
    bx = hx - 11 if back_left else hx + 9
    cv.rect(bx, hy - 22, bx + 2, hy + 20, "#3b2a1e"); cv.vline(bx, hy - 22, hy + 20, "#5b402b"); cv.rect(bx - 1, hy - 23, bx + 3, hy - 21, "#5b402b")
    sx0, sx1 = (hx - 11, hx + 9) if back_left else (hx - 9, hx + 11)
    cv.rect(sx0, hy, sx1, hy + 2, "#5b402b"); cv.hline(sx0, sx1, hy, "#85613f")
    fx = sx1 - 2 if back_left else sx0
    cv.rect(fx, hy + 2, fx + 2, hy + 20, "#3b2a1e")

def dunstan(hx, hy):
    """Seated, facing right: a broad old fisherman hunched toward the table."""
    L = Layer()
    T, Tt = "#3a3a38", "#241a14"
    L.poly([(hx - 7, hy - 3), (hx + 12, hy - 4), (hx + 14, hy + 3), (hx - 7, hy + 3)], T)          # thigh
    L.poly([(hx + 9, hy + 1), (hx + 14, hy + 1), (hx + 15, hy + 19), (hx + 10, hy + 19)], T)       # shin
    L.rect(hx + 8, hy + 18, hx + 18, hy + 22, "#1a1410"); L.rect(hx + 9, hy + 18, hx + 17, hy + 19, "#3b2a1e")  # boot
    L.shade(lambda x, y: y >= hy + 1 and x < hx + 11, T, Tt)
    C, Cs, Ch = "#2b3a44", "#1c2620", "#445866"
    L.poly([(hx - 8, hy), (hx - 10, hy - 8), (hx - 9, hy - 15), (hx - 6, hy - 20), (hx - 1, hy - 23), (hx + 4, hy - 22),
            (hx + 8, hy - 16), (hx + 10, hy - 8), (hx + 9, hy)], C)                                  # peacoat
    L.shade(lambda x, y: x < hx - 5, C, Cs); L.shade(lambda x, y: y < hy - 20 and x > hx - 5, C, Ch)
    L.poly([(hx + 2, hy - 21), (hx + 7, hy - 18), (hx + 4, hy - 14)], "#445866")                    # lapel
    for y in (hy - 13, hy - 9, hy - 5): L.put(hx + 8, y, "#c99a55")
    L.rect(hx - 8, hy - 2, hx + 9, hy, Cs)                                                            # coat hem shadow
    L.limb(hx + 1, hy - 18, hx + 4, hy - 9, 5.5, C, Cs)                                              # upper arm
    L.limb(hx + 4, hy - 9, hx + 15, hy - 14, 4.5, C, Cs)                                             # forearm on the table
    L.ellipse(hx + 17.5, hy - 14.5, 2.3, 2, "#c9a07c"); L.put(hx + 18, hy - 13, "#a97f5e")         # hand
    S, Ss = "#c9a07c", "#a97f5e"
    L.ellipse(hx + 5.5, hy - 28.5, 5.2, 5.8, S)                                                      # head
    L.shade(lambda x, y: x < hx + 3, S, Ss)
    L.ellipse(hx + 5, hy - 31.5, 5.7, 3.6, "#2b3a44", keep=lambda x, y: y <= hy - 31)                # watch cap
    L.rect(hx, hy - 32, hx + 11, hy - 31, "#445866")                                                 # its turned-up band
    L.ellipse(hx + 6.5, hy - 24, 4.6, 3.6, "#9e988b", keep=lambda x, y: x > hx + 1)                  # beard
    L.ellipse(hx + 7.5, hy - 25.5, 3, 1.6, "#c9c2b0", keep=lambda x, y: x > hx + 5)                  # moustache, lighter
    for (x, y, c) in ((hx + 8, hy - 29, "#1a1410"), (hx + 7, hy - 30, "#77736a"), (hx + 8, hy - 30, "#77736a"),
                      (hx + 11, hy - 28, S), (hx + 11, hy - 27, Ss), (hx + 2, hy - 28, Ss), (hx + 1, hy - 29, "#9e988b"), (hx + 1, hy - 28, "#9e988b")):
        L.put(x, y, c)
    return L

def vanessa(hx, hy):
    """Seated, drawn facing right and flipped to face left: slim, upright, a long grey coat, a dark bob, cards held up."""
    L = Layer()
    G, Gs, Gh = "#77736a", "#55534e", "#9e988b"
    L.poly([(hx + 9, hy + 2), (hx + 12, hy + 2), (hx + 13, hy + 19), (hx + 10, hy + 19)], "#3a3a38")  # shin
    L.rect(hx + 9, hy + 18, hx + 16, hy + 21, "#1a1410")                                                 # shoe
    L.poly([(hx - 6, hy - 3), (hx + 12, hy - 3), (hx + 13, hy + 4), (hx - 6, hy + 4)], G)                 # coat over the thigh
    L.shade(lambda x, y: y >= hy + 2, G, Gs)
    L.poly([(hx - 6, hy), (hx - 7, hy - 9), (hx - 6, hy - 17), (hx - 3, hy - 21), (hx + 2, hy - 22), (hx + 5, hy - 18),
            (hx + 6, hy - 9), (hx + 6, hy)], G)                                                           # torso
    L.shade(lambda x, y: x < hx - 3, G, Gs); L.shade(lambda x, y: y < hy - 19 and x > hx - 2, G, Gh)
    L.poly([(hx - 5, hy - 24), (hx, hy - 24), (hx, hy - 19), (hx - 6, hy - 20)], Gh)                     # collar turned up
    L.vline = None
    L.limb(hx + 1, hy - 18, hx + 7, hy - 13, 4, G, Gs)                                                   # upper arm, elbow on the table
    L.limb(hx + 7, hy - 13, hx + 11, hy - 17, 3.6, G, Gs)                                                # forearm, raised a little
    L.ellipse(hx + 12, hy - 17.5, 1.9, 1.8, "#e0bc98")                                                  # hand
    D = "#241a14"
    L.ellipse(hx + 1, hy - 29, 5.6, 6.2, D)                                                              # the bob, behind
    L.ellipse(hx + 2.8, hy - 28.6, 4.4, 5.2, "#e0bc98", keep=lambda x, y: x >= hx + 2)                   # face
    L.ellipse(hx + 1.5, hy - 31.5, 5.2, 3, D, keep=lambda x, y: y <= hy - 31)                           # fringe
    for (x, y, c) in ((hx + 5, hy - 29, "#1a1410"), (hx + 7, hy - 28, "#e0bc98"), (hx + 5, hy - 26, "#93392d"),
                      (hx + 3, hy - 27, "#c9a07c"), (hx + 2, hy - 23, "#c9a07c"), (hx + 3, hy - 23, "#c9a07c")):
        L.put(x, y, c)
    return L

def kid(kx, top):
    """Standing behind the table, front view, leaning on it: about twelve, an oversized mustard sweater, a satchel."""
    L = Layer()
    Y, Ys = "#a07a4c", "#85613f"
    L.poly([(kx - 5, top + 14), (kx + 5, top + 14), (kx + 7, top + 19), (kx + 7, top + 34), (kx - 7, top + 34), (kx - 7, top + 19)], Y)
    L.shade(lambda x, y: x < kx - 3, Y, Ys)
    L.limb(kx - 6, top + 17, kx - 8, top + 31, 3.6, Y, Ys); L.limb(kx + 6, top + 17, kx + 8, top + 31, 3.6, Y, Ys)    # sleeves
    L.ellipse(kx - 8, top + 33, 1.8, 1.5, "#c9a07c"); L.ellipse(kx + 8, top + 33, 1.8, 1.5, "#c9a07c")             # hands on the table's edge
    for i in range(12): L.put(kx - 5 + i, top + 15 + i, "#3b2a1e")                                                # satchel strap
    L.rect(kx - 2, top + 11, kx + 2, top + 14, "#a97f5e")                                                         # neck
    L.ellipse(kx, top + 6.5, 5, 5.6, "#c9a07c")                                                                   # head
    L.ellipse(kx, top + 3, 5.4, 3.6, "#5b402b", keep=lambda x, y: y <= top + 3)                                # hair
    for (x, y, c) in ((kx + 1, top, "#5b402b"), (kx + 2, top - 1, "#5b402b"), (kx - 5, top + 4, "#5b402b"), (kx + 5, top + 4, "#5b402b"), (kx - 5, top + 5, "#5b402b"),
                      (kx - 2, top + 7, "#1a1410"), (kx + 2, top + 7, "#1a1410"), (kx, top + 9, "#a97f5e"), (kx - 1, top + 10, "#93392d"), (kx, top + 10, "#93392d"),
                      (kx - 3, top + 9, "#d8a890"), (kx + 3, top + 9, "#d8a890")):
        L.put(x, y, c)
    return L

def side_table(cv):
    """A small table in front of the bookshelf: Dunstan and Vanessa playing, a kid watching."""
    hy = 190; top = hy - 14
    chair(cv, 16, hy, back_left=True); chair(cv, 71, hy, back_left=False)
    kid(44, 141).stamp(cv)
    # the table: a small round top on one pedestal
    cv.rect(26, top, 63, top + 3, "#6e4e33"); cv.hline(26, 63, top, "#a07a4c"); cv.hline(26, 63, top + 3, "#1a1410")
    cv.rect(42, top + 4, 47, 205, "#3b2a1e"); cv.vline(42, top + 4, 205, "#5b402b"); cv.rect(35, 204, 54, 207, "#2e2119")
    for (x, els) in ((30, "w"), (35, "fa")):
        smudge_card(cv, x, top - 5, els)
    for (x, els) in ((50, "e"), (55, "wf")):
        smudge_card(cv, x, top - 5, els)
    cv.rect(43, top - 4, 46, top, "#e8dfc8"); cv.put(44, top - 5, "#f4dca0"); cv.put(44, top - 6, "#d0663f")   # a candle stub
    dunstan(16, hy).stamp(cv)
    smudge_card(cv, 32, top - 11, "w")                                    # the card he's about to put down
    v = vanessa(71, hy).flipped(71)
    v.stamp(cv)
    for i, el in enumerate("fwa"):                                         # her fan of cards, held low over the table
        smudge_card(cv, 54 + i * 3, top - 10 - (i % 2), el)

def pipe_smoke(cv):
    """Wendell's pipe, and its smoke drifting up toward the lamp."""
    cv.hline(250, 254, 88, "#3b2a1e"); cv.put(251, 89, "#3b2a1e")
    cv.rect(254, 85, 258, 90, "#5b402b"); cv.hline(254, 258, 85, "#85613f"); cv.put(255, 85, "#d0663f"); cv.put(256, 85, "#e3bf7a")
    rng = random.Random(9)
    path = lambda tt: (256 - 13 * tt + 2.6 * math.sin(tt * 10.5), 83 - 47 * tt)
    for tt in (0.04, 0.15, 0.28, 0.42, 0.57, 0.72, 0.87):               # puffs, growing and thinning as they rise
        cx, cy = path(tt); r = 1.1 + 2.4 * tt; dens = 0.75 - 0.55 * tt
        for yy in range(int(cy - r), int(cy + r) + 1):
            for xx in range(int(cx - r), int(cx + r) + 1):
                d = math.hypot(xx - cx, yy - cy)
                if d <= r and (xx + yy) % 2 == 0 and rng.random() < dens * (1 - 0.5 * d / (r + .01)):
                    cv.put(xx, yy, "#9e988b" if rng.random() < 0.6 else "#77736a")
    for i in range(70):                                                   # a thin wisp joining them
        tt = i / 70; x, y = path(tt)
        if rng.random() < 0.55 - 0.4 * tt: cv.put(round(x + rng.uniform(-.6, .6)), round(y), "#9e988b")

# ------------------------------------------------------------------ the scene
def scene(table=False):
    W, H = 360, (220 if table else 200)
    cv = Canvas(W, H, "#314237")
    # wallpaper: stripes and a small figure
    for x in range(0, W, 12):
        cv.rect(x, 6, x + 2, 112, "#2a382f")
        for y in range(14, 108, 12): cv.put(x + 7, y, "#3f5345"); cv.put(x + 6, y + 1, "#3f5345"); cv.put(x + 8, y + 1, "#3f5345")
    # ceiling trim
    cv.rect(0, 0, W, 6, "#241a14"); cv.hline(0, W, 6, "#4a3424"); cv.hline(0, W, 7, "#1a1410")
    # wainscot and chair rail
    cv.rect(0, 112, W, 150, "#4a3424")
    cv.rect(0, 110, W, 113, "#6e4e33"); cv.hline(0, W, 113, "#2e2119")
    for x in range(4, W, 30):
        cv.rect(x, 118, x + 24, 146, "#3b2a1e"); cv.rect(x + 1, 119, x + 23, 145, "#4a3424"); cv.hline(x + 1, x + 23, 119, "#5b402b")
    # floor planks
    cv.rect(0, 150, W, H, "#3b2a1e")
    for y in range(150, H, 7):
        cv.hline(0, W, y, "#2e2119")
        off = random.randint(0, 40)
        for x in range(off, W, 48 + random.randint(-6, 6)): cv.vline(x, y, y + 7, "#2e2119")
    for _ in range(9):
        y = 151 + 7 * random.randint(0, 6); x = random.randint(0, W - 40)
        cv.rect(x, y, x + random.randint(20, 46), y + 6, "#4a3424")
    cv.hline(0, W, 150, "#1a1410")
    # a worn rug in front of the counter
    if True:
        cv.rect(206, 176, 340, 196, "#4a1c1a")
        cv.rect(208, 178, 338, 194, "#6e2a24")
        for x in range(212, 336, 6): cv.put(x, 186, "#a07a4c"); cv.put(x + 3, 182, "#93392d"); cv.put(x + 3, 190, "#93392d")
        cv.hline(208, 338, 179, "#a07a4c"); cv.hline(208, 338, 193, "#a07a4c")
    # left shelving with board games, jars and books
    cv.rect(6, 20, 80, 152, "#2e2119"); cv.rect(8, 22, 78, 150, "#3b2a1e")
    for sy in (48, 78, 108, 138):
        cv.rect(8, sy, 78, sy + 3, "#6e4e33"); cv.hline(8, 78, sy, "#85613f"); cv.hline(8, 78, sy + 3, "#1a1410")
    boxes = [("#6e2a24", "#93392d"), ("#3f5345", "#56685a"), ("#c9c2b0", "#e8dfc8"), ("#445866", "#6f8794"), ("#a07a4c", "#c99a55"), ("#55534e", "#77736a")]
    # top shelf: stacked flat boxes and a globe
    y = 48
    for i, (a, b) in enumerate(boxes[:3]):
        cv.rect(12, y - 5 * (i + 1), 40 - i * 2, y - 5 * i - 1, a); cv.hline(12, 40 - i * 2, y - 5 * (i + 1), b)
    cv.rect(52, 34, 64, 46, "#445866"); cv.rect(54, 36, 62, 44, "#6f8794"); cv.put(56, 38, "#a9bcc4"); cv.rect(57, 46, 59, 48, "#85613f")
    cv.put(60, 40, "#3f5345"); cv.put(58, 41, "#3f5345"); cv.put(57, 39, "#3f5345")
    # second shelf: upright spines
    x = 11
    for i in range(14):
        a, b = boxes[i % 6]; w = random.choice([3, 4, 5]); h = random.randint(16, 25)
        cv.rect(x, 78 - h, x + w, 78, a); cv.vline(x, 78 - h, 78, b); x += w + (1 if i % 4 else 2)
        if x > 74: break
    # third shelf: jars and a chess board
    for jx, c in ((12, "#6f8794"), (24, "#56685a"), (36, "#a97f5e")):
        cv.rect(jx, 94, jx + 9, 108, c); cv.rect(jx + 1, 92, jx + 8, 94, "#85613f"); cv.vline(jx + 2, 96, 106, "#a9bcc4")
    cv.rect(50, 98, 74, 108, "#2e2119")
    for i in range(6):
        for j in range(2): cv.rect(50 + i * 4, 98 + j * 5, 52 + i * 4, 100 + j * 5, "#c9c2b0")
    # bottom shelf: puzzle boxes
    cv.rect(12, 124, 44, 138, "#6e2a24"); cv.rect(14, 126, 42, 136, "#93392d"); cv.hline(16, 40, 130, "#c99a55")
    cv.rect(48, 128, 74, 138, "#3f5345"); cv.hline(50, 72, 131, "#e3bf7a")

    # the display cabinet: a tall glass curio case, lit from inside
    X0, X1, Y0, Y1 = 92, 196, 30, 152
    cv.rect(X0 - 3, Y0 - 8, X1 + 3, Y0, "#5b402b"); cv.hline(X0 - 3, X1 + 3, Y0 - 8, "#85613f"); cv.hline(X0 - 1, X1 + 1, Y0 - 5, "#3b2a1e")
    cv.rect(X0, Y0, X1, Y1, "#4a3424")
    cv.rect(X0 + 5, Y0 + 4, X1 - 5, Y1 - 10, "#1c2620")
    cv.checker(X0 + 5, Y0 + 4, X1 - 5, Y1 - 10, "#1c2620", "#25332b")
    for sy in (Y0 + 34, Y0 + 66, Y0 + 98):
        cv.hline(X0 + 5, X1 - 5, sy, "#a9bcc4"); cv.hline(X0 + 5, X1 - 5, sy + 1, "#6f8794")
    els = [0, 1, 2, 3, 1, 0, 3, 2, 0, 1, 2, 3, 3, 1, 0, 2, 1, 0]
    k = 0
    for r, sy in enumerate((Y0 + 34, Y0 + 66, Y0 + 98)):
        for c in range(6):
            if r == 2 and c == 5: continue  # the empty stand
            tiny_card(cv, X0 + 9 + c * 15, sy - 12, els[k] % 4); k += 1
        cv.rect(X0 + 9 + 5 * 15 + 2, Y0 + 98 - 3, X0 + 9 + 5 * 15 + 6, Y0 + 98, "#6e4e33") if r == 2 else None
    cv.vline((X0 + X1) // 2, Y0 + 4, Y1 - 10, "#5b402b")   # the doors' meeting stiles
    cv.vline((X0 + X1) // 2 + 1, Y0 + 4, Y1 - 10, "#3b2a1e")
    cv.rect((X0 + X1) // 2 - 3, Y0 + 60, (X0 + X1) // 2 - 1, Y0 + 66, "#c99a55"); cv.rect((X0 + X1) // 2 + 2, Y0 + 60, (X0 + X1) // 2 + 4, Y0 + 66, "#c99a55")
    for gx in range(X0 + 10, X1 - 10, 22):   # glass highlights
        for t in range(22):
            cv.put(gx + t, Y0 + 8 + t * 4, "#56685a") if Y0 + 8 + t * 4 < Y1 - 12 else None
    cv.rect(X0, Y1 - 10, X1, Y1, "#5b402b"); cv.hline(X0, X1, Y1 - 10, "#85613f")
    cv.rect(X0 + 40, Y1 - 7, X1 - 40, Y1 - 3, "#c99a55")  # a brass plate
    cv.rect(X0 + 2, Y1, X0 + 6, Y1 + 2, "#2e2119"); cv.rect(X1 - 6, Y1, X1 - 2, Y1 + 2, "#2e2119")

    # a painted sign over the counter
    cv.rect(212, 12, 296, 24, "#241a14"); cv.rect(213, 13, 295, 23, "#3b2a1e")
    text(cv, 218, 16, "HOLLIS GAMES", "#e3bf7a")
    cv.vline(222, 8, 12, "#1a1410"); cv.vline(286, 8, 12, "#1a1410")

    # a high little window, dusk outside
    cv.rect(318, 12, 352, 38, "#2e2119"); cv.rect(320, 14, 350, 36, "#2b3a44"); cv.rect(320, 26, 350, 36, "#445866")
    cv.rect(322, 28, 330, 36, "#1c2620"); cv.rect(332, 24, 340, 36, "#1c2620"); cv.rect(342, 30, 350, 36, "#1c2620")
    cv.put(335, 27, "#e3bf7a"); cv.put(325, 31, "#c99a55"); cv.vline(335, 14, 36, "#2e2119"); cv.hline(320, 350, 25, "#2e2119")
    # the back-room doorway with a curtain, June just visible
    cv.rect(306, 44, 348, 122, "#1a1410"); cv.rect(308, 46, 346, 122, "#e3bf7a"); cv.checker(308, 46, 346, 122, "#c99a55", "#e3bf7a")
    for x in range(308, 346):
        fold = (x - 308) % 6
        if x < 318 or x > 336:
            cv.vline(x, 46, 122, "#6e2a24" if fold < 4 else "#4a1c1a")
    JUNE = [
        "...HHHH...",
        "..HHhhHH..",
        ".HHssssHH.",
        ".HsksskSH.",
        ".HssssssH.",
        "..sSmmSs..",
        "...ssss...",
        "..BBccBB..",
        ".BBBccBBB.",
        "BBBBccBBBB",
        "BBBBBBBBBB",
    ]
    cv.sprite(322, 82, JUNE, {"H": "#77736a", "h": "#9e988b", "s": "#c9a07c", "S": "#a97f5e", "k": "#241a14", "m": "#93392d", "B": "#3f5345", "c": "#e8dfc8"})
    for y in range(93, 122): cv.put(321, y, "#4a1c1a"); cv.put(333, y, "#4a1c1a")

    # the lamp over the counter
    cv.vline(243, 0, 26, "#1a1410")  # through the gap between the sign's two words
    cv.rect(233, 26, 253, 30, "#2e2119"); cv.rect(231, 30, 255, 33, "#3b2a1e"); cv.hline(233, 253, 26, "#85613f"); cv.hline(231, 255, 32, "#c99a55")
    cv.rect(239, 33, 247, 35, "#f4dca0")

    # Wendell, behind the counter
    WENDELL = [
        "......ssssss......",
        "....ssssssssss....",
        "...sssssssssSss...",
        "..hssssssssssSsh..",
        "..hhHHssssssHHhh..",
        "..hsggggssggggsh..",
        "..hsgkwggggkwgsh..",
        "..hsggggssggggsh..",
        "...ssssssssssSs...",
        "...ssSmmmmmmSss...",
        "...sSmmmmmmmmSs...",
        "....ssSskkSssS....",
        ".....SssssssS.....",
        "......SSSSSS......",
        "....bbbbKKbbbb....",
        "..cccbbbKKbbbccc..",
        ".cccccbbbbbbccccc.",
        "cccccCcbbbbcCcccccc",
        "ccccCCcbbbbcCCcccc",
        "cccCCccbbbbccCCccc",
        "ccccccccbbcccccccc",
        "cccccccccccccccccc",
    ]
    cv.sprite(240, 76, WENDELL, {"s": "#c9a07c", "S": "#a97f5e", "h": "#c9c2b0", "H": "#e8dfc8", "g": "#4a3424", "w": "#e8dfc8", "k": "#1a1410",
                                 "m": "#9e988b", "b": "#e8dfc8", "K": "#4a1c1a", "c": "#6e2a24", "C": "#4a1c1a"})
    cv.rect(240, 98, 258, 118, "#6e2a24")                       # the rest of him, down to the counter
    cv.rect(241, 98, 244, 118, "#4a1c1a"); cv.rect(254, 98, 257, 118, "#4a1c1a")
    cv.rect(247, 98, 251, 118, "#e8dfc8"); cv.vline(249, 98, 118, "#c9c2b0")
    for y in (101, 106, 111): cv.put(246, y, "#c99a55"); cv.put(252, y, "#c99a55")

    # the counter
    cv.rect(204, 118, 354, 124, "#85613f"); cv.hline(204, 354, 118, "#a07a4c"); cv.hline(204, 354, 124, "#2e2119")
    wood_panel(cv, 206, 125, 352, 176)
    for x in range(210, 350, 36):
        cv.rect(x, 130, x + 30, 170, "#3b2a1e"); cv.rect(x + 1, 131, x + 29, 169, "#4a3424"); cv.hline(x + 1, x + 29, 131, "#5b402b")
    cv.rect(206, 172, 352, 176, "#2e2119")
    # on the counter: a bell, a ledger, a teacup and the register
    cv.rect(212, 114, 220, 118, "#c99a55"); cv.rect(215, 112, 217, 114, "#e3bf7a"); cv.put(214, 115, "#f4dca0")
    cv.rect(262, 114, 284, 118, "#4a1c1a"); cv.rect(263, 113, 283, 115, "#e8dfc8"); cv.hline(264, 282, 114, "#c9c2b0")
    cv.rect(288, 113, 294, 118, "#e8dfc8"); cv.put(294, 114, "#e8dfc8"); cv.put(295, 115, "#e8dfc8"); cv.rect(286, 117, 296, 118, "#c9c2b0")
    cv.rect(298, 96, 330, 118, "#5b402b"); cv.rect(300, 98, 328, 104, "#2e2119"); cv.rect(302, 99, 312, 103, "#93392d")
    for i in range(4):
        for j in range(3): cv.rect(301 + i * 7, 106 + j * 4, 305 + i * 7, 109 + j * 4, "#c99a55")
    cv.rect(296, 116, 332, 118, "#3b2a1e")

    pipe_smoke(cv)
    if table: side_table(cv)
    lamps = [(243, 40, 200, 0.85, (1.0, 0.82, 0.55)), (144, 96, 90, 0.6, (1.0, 0.86, 0.6)), (327, 84, 50, 0.6, (1.0, 0.8, 0.5)), (335, 24, 40, 0.25, (0.55, 0.7, 0.9)), (270, 170, 120, 0.35, (1.0, 0.85, 0.65))]
    if table: lamps += [(45, 165, 70, 0.75, (1.0, 0.8, 0.5))]
    light(cv, lamps, ambient=0.66, vx=0.18, vy=0.1)
    return quantize(cv)

# ------------------------------------------------------------------ the cabinet close-up
def cabinet():
    W, H = 360, 230
    cv = Canvas(W, H, "#1c2620")
    cv.checker(12, 12, W - 12, H - 12, "#1c2620", "#25332b")
    for y in range(12, H - 12, 6):   # the felt's weave
        for x in range(12 + (y // 6) % 2 * 3, W - 12, 6): cv.put(x, y, "#314237")
    # the frame
    cv.rect(0, 0, W, 12, "#5b402b"); cv.rect(0, H - 12, W, H, "#5b402b"); cv.rect(0, 0, 12, H, "#5b402b"); cv.rect(W - 12, 0, W, H, "#5b402b")
    cv.hline(0, W, 0, "#85613f"); cv.hline(12, W - 12, 11, "#2e2119"); cv.vline(11, 12, H - 12, "#2e2119"); cv.vline(W - 12, 12, H - 12, "#3b2a1e")
    cv.hline(12, W - 12, H - 12, "#85613f")
    for y in range(2, 10, 3):
        for x in range(0, W):
            if random.random() < 0.2: cv.put(x, y, "#4a3424"); 
    # three glass shelves (card bottoms sit at y = 71, 137, 203 in base pixels)
    for sy in (72, 138, 204):
        cv.hline(12, W - 12, sy, "#c9d6dc" if False else "#a9bcc4"); cv.hline(12, W - 12, sy + 1, "#6f8794"); cv.hline(12, W - 12, sy + 2, "#2b3a44")
        for x in range(12, W - 12, 4): cv.put(x, sy + 3, "#1a1410")
        # little wooden stands behind each card
        for c in range(6):
            x = (111 + c * 213) // 4
            cv.rect(x + 10, sy - 4, x + 28, sy, "#3b2a1e"); cv.hline(x + 10, x + 28, sy - 4, "#5b402b")
    # a brass corner bracket on each corner
    for (x, y) in ((12, 12), (W - 20, 12), (12, H - 20), (W - 20, H - 20)):
        cv.rect(x, y, x + 8, y + 2, "#c99a55"); cv.rect(x if x < 100 else x + 6, y, (x if x < 100 else x + 6) + 2, y + 8, "#c99a55")
    light(cv, [(180, 10, 300, 0.7, (1.0, 0.85, 0.6)), (180, 230, 260, 0.25, (1.0, 0.86, 0.65))], ambient=0.8, vx=0.12, vy=0.06)
    return quantize(cv, spread=20)

# ---- the case, second pass: cards in holders, casting shadows on the felt ----
SLOTS = [((111 + c * 213) / 4, 19 + r * 66) for r in range(3) for c in range(6)]   # card top-left in base px (37.5 x 52.5)
SHELVES = (72, 138, 204)
LAMP = (180, 10)

def cabinet2():
    W, H = 360, 230
    cv = Canvas(W, H, "#1c2620")
    cv.checker(12, 12, W - 12, H - 12, "#1c2620", "#25332b")
    for y in range(12, H - 12, 6):
        for x in range(12 + (y // 6) % 2 * 3, W - 12, 6): cv.put(x, y, "#314237")
    # cast shadows on the felt: each card's outline pushed down and away from the lamp, soft at the edge
    def darken(x, y, k):
        if 12 <= x < W - 12 and 12 <= y < H - 12:
            r, g, b = cv.px[y][x]; cv.px[y][x] = (r * k, g * k, b * k)
    for (x0, y0) in SLOTS[:17]:
        cx = x0 + 18.75; dx = (cx - LAMP[0]) * 0.07; dy = 5
        sx0, sy0 = int(round(x0 + dx)), int(round(y0 + dy))
        sy_shelf = min(s for s in SHELVES if s > y0)
        for y in range(sy0, min(sy0 + 53, sy_shelf - 6)):
            for x in range(sx0, sx0 + 38):
                edge = min(x - sx0, sx0 + 37 - x, y - sy0)
                if edge >= 3: darken(x, y, 0.66)
                elif edge >= 1 or (x + y) % 2 == 0: darken(x, y, 0.8)
    # glass shelves: a pale top face (the shelf's depth), a bright back edge, then the front lip
    for sy in SHELVES:
        for y in range(sy - 6, sy):
            for x in range(12, W - 12): cv.put(x, y, "#3f5345" if (x + y) % 2 else "#445866")
        cv.hline(12, W - 12, sy - 6, "#6f8794")
        cv.hline(12, W - 12, sy, "#a9bcc4"); cv.hline(12, W - 12, sy + 1, "#6f8794"); cv.hline(12, W - 12, sy + 2, "#2b3a44")
        for x in range(12, W - 12, 4): cv.put(x, sy + 3, "#1a1410")
    # contact shadows on the glass behind and beside each holder
    for (x0, y0) in SLOTS:
        sy = min(s for s in SHELVES if s > y0); cx = int(x0 + 18.75)
        for y in range(sy - 6, sy - 1):
            for x in range(cx - 20, cx + 22):
                if abs(x - cx) < 17 or (x + y) % 2 == 0: darken(x, y, 0.55)
    # the frame
    cv.rect(0, 0, W, 12, "#5b402b"); cv.rect(0, H - 12, W, H, "#5b402b"); cv.rect(0, 0, 12, H, "#5b402b"); cv.rect(W - 12, 0, W, H, "#5b402b")
    cv.hline(0, W, 0, "#85613f"); cv.hline(12, W - 12, 11, "#2e2119"); cv.vline(11, 12, H - 12, "#2e2119"); cv.vline(W - 12, 12, H - 12, "#3b2a1e")
    cv.hline(12, W - 12, H - 12, "#85613f")
    for y in range(2, 10, 3):
        for x in range(0, W):
            if random.random() < 0.2: cv.put(x, y, "#4a3424")
    for (x, y) in ((12, 12), (W - 20, 12), (12, H - 20), (W - 20, H - 20)):
        cv.rect(x, y, x + 8, y + 2, "#c99a55"); cv.rect(x if x < 100 else x + 6, y, (x if x < 100 else x + 6) + 2, y + 8, "#c99a55")
    light(cv, [(180, 10, 300, 0.7, (1.0, 0.85, 0.6)), (180, 230, 260, 0.25, (1.0, 0.86, 0.65))], ambient=0.8, vx=0.12, vy=0.06)
    return quantize(cv, spread=20)

def holders():
    """the wooden card holders, drawn on their own layer so they sit in front of the cards"""
    W, H = 360, 230; KEY = "#ff00ff"
    cv = Canvas(W, H, KEY)
    for i, (x0, y0) in enumerate(SLOTS):
        sy = min(s for s in SHELVES if s > y0); cx = int(x0 + 18.75); x1, x2 = cx - 14, cx + 14
        cv.rect(x1, sy - 8, x2, sy - 7, "#6e4e33")                 # top edge, catching the lamp
        cv.rect(x1, sy - 7, x2, sy - 1, "#4a3424")                 # front face
        cv.rect(x1, sy - 1, x2, sy, "#2e2119")                     # underside shade
        cv.vline(x1, sy - 7, sy, "#5b402b"); cv.vline(x2 - 1, sy - 7, sy, "#3b2a1e")
        for k in range(x1 + 3, x2 - 3, 6): cv.put(k, sy - 4, "#3b2a1e"); cv.put(k + 1, sy - 4, "#3b2a1e")   # grain
        if i == 17:                                                # the empty one: its slot shows
            cv.rect(cx - 10, sy - 8, cx + 10, sy - 7, "#1a1410")
    key = hexrgb(KEY)
    drawn = [[cv.px[y][x] != key for x in range(W)] for y in range(H)]
    light(cv, [(180, 10, 300, 0.7, (1.0, 0.85, 0.6)), (180, 230, 260, 0.25, (1.0, 0.86, 0.65))], ambient=0.8, vx=0.12, vy=0.06)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for y in range(H):
        for x in range(W):
            r, g, b = cv.px[y][x]
            if not drawn[y][x]:
                continue
            t = (BAYER[y % 4][x % 4] / 16 - 0.5) * 20
            best = min(P, key=lambda p: (p[0] - r - t) ** 2 * .9 + (p[1] - g - t) ** 2 * 1.2 + (p[2] - b - t) ** 2 * .7)
            img.putpixel((x, y), best + (255,))
    return img

if "case2" in sys.argv:
    for name, img in (("shop_cabinet2", cabinet2()), ("shop_holders", holders())):
        img.save(f"{OUT}/{name}_1x.png")
        img.resize((img.width * 4, img.height * 4), Image.NEAREST).save(f"{OUT}/{name}.png")
        print(name, img.size)
    sys.exit(0)

for name, img in (("shop_scene", scene()), ("shop_cabinet", cabinet()), ("shop_rivals", scene(table=True))):
    img.save(f"{OUT}/{name}_1x.png")
    img.resize((img.width * 4, img.height * 4), Image.NEAREST).save(f"{OUT}/{name}.png")
    print(name, img.size)
