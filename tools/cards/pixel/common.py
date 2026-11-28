# Shared pieces for the card-style canvas: card data, pip tokens, the face layout.
import math, random
GLYPH = {'fire': ('M12 3.5 L20.5 19 H3.5 Z', '#D0663F'), 'water': ('M3.5 5 H20.5 L12 20.5 Z', '#7FA7B5'),
         'air': ('M12 3.5 L20.5 19 H3.5 Z M3 12.5 H21', '#D5D8CC'), 'earth': ('M3.5 5 H20.5 L12 20.5 Z M3 11.5 H21', '#A88F6B'),
         'any': ('M4.5 4.5 H19.5 V19.5 H4.5 Z', '#FFFFFF')}
ORDER = ['water', 'earth', 'fire', 'air', 'any']
CARDS = [
    {'key': 'volcano', 'name': 'Volcano', 'no': 23, 'rar': 'B', 'front': ['earth', 'fire'],
     'force': 'Lava Bomb', 'back': ['fire'], 'text': 'Remove an uncommon permanence.'},
    {'key': 'tidepool', 'name': 'Tide Pool', 'no': 5, 'rar': 'C', 'front': ['water'],
     'force': 'Drizzle', 'back': [], 'text': 'Return a card from your void. Next turn, flip this back.'},
]
RW = {'C': 'common', 'B': 'uncommon', 'A': 'rare', 'S': 'pinnacle'}

def pip(el, size=30, disc='#161816', ring='#E6E1D3'):
    d, c = GLYPH[el]
    sc = 0.78
    t = 'translate(%.2f %.2f) scale(%.3f)' % (16 - 12 * sc, 16.4 - 12 * sc, sc)
    own = ' fill="#000000" stroke-width="0.6"' if el == 'any' else ''
    return ('<svg width="%d" height="%d" viewBox="0 0 32 32" fill="none" stroke-width="1.9" stroke-linejoin="miter" stroke-linecap="butt" role="img" aria-label="%s pip">'
            '<circle cx="16" cy="16" r="15" fill="%s"></circle><circle cx="16" cy="16" r="14.3" stroke="%s" stroke-width="1.2"></circle>'
            '<g transform="%s" stroke="%s"><path d="%s"%s></path></g></svg>') % (size, size, el, disc, ring, t, c, d, own)

def pips(els, size=30, **kw):
    return ''.join(pip(e, size, **kw) for e in sorted(els, key=ORDER.index))

class Grid:
    def __init__(s, w, h, bg):
        s.w, s.h = w, h; s.p = [[bg] * w for _ in range(h)]
    def set(s, x, y, c):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < s.w and 0 <= y < s.h: s.p[y][x] = c
    def get(s, x, y):
        return s.p[y][x] if 0 <= x < s.w and 0 <= y < s.h else None
    def rect(s, x0, y0, x1, y1, c):
        for y in range(y0, y1):
            for x in range(x0, x1): s.set(x, y, c)
    def svg(s, W, H):
        paths = {}
        for y, row in enumerate(s.p):
            x = 0
            while x < s.w:
                c = row[x]; x2 = x
                while x2 < s.w and row[x2] == c: x2 += 1
                paths.setdefault(c, []).append('M%d %dh%dv1h-%dz' % (x, y, x2 - x, x2 - x)); x = x2
        body = ''.join('<path fill="%s" d="%s"></path>' % (c, ''.join(d)) for c, d in paths.items() if c)
        return ('<svg width="%d" height="%d" viewBox="0 0 %d %d" shape-rendering="crispEdges" preserveAspectRatio="none" aria-hidden="true">%s</svg>'
                % (W, H, s.w, s.h, body))

BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
def dither(t, x, y):  # True if the second colour wins at this pixel, t in 0..1
    return t * 16 > BAYER[y % 4][x % 4] + 0.5

def bands(g, y0, y1, cols):  # dithered vertical gradient through a list of colours
    n = len(cols) - 1
    for y in range(y0, y1):
        f = (y - y0) / max(1, (y1 - y0 - 1)) * n
        i = min(int(f), n - 1); t = f - i
        for x in range(g.w):
            g.set(x, y, cols[i + 1] if dither(t, x, y) else cols[i])
