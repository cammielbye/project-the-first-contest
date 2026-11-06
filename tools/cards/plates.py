#!/usr/bin/env python3
"""Plates, first draft (Nov 5): the metal stamp plates that press the cards (LORE-02).

A plate carries its card's faces mirrored, the way a stamp does, and in metal relief (Cam chose raised; steel
added after the bronze looked too shiny, Nov 5). This renders a few
third-pass faces with Playwright, mirrors them, and turns them into lit metal: the art lines, lettering,
rings and footer stand up from the plate (RAISED, the way a stamp or printing block is cut), or are cut
into it (ENGRAVED, the way an intaglio plate is), with a raised rim and a sunken art panel.

  python3 tools/cards/plates.py <out folder>        # writes <name>-<perm|force>-plate-<metal>.png

Needs the local fonts in tools/fonts/ (see tools/README.md, "cards/")."""
import os, sys, json
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, distance_transform_edt as edt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pass3_cards as P3
import pass3
from fontcss import local_fonts

CARDS = ['Grove', 'Volcano', 'Cloud Sea', 'Ocean']        # one per rarity: common, uncommon, rare, pinnacle
ENGRAVED_TOO = []                                         # cards also drawn cut-in (Cam chose raised, Nov 5)
DRAW_METALS = ['steel', 'bronze']
S = 2                                                      # render scale
W, H = 320 * S, 448 * S
METAL = {  # a ramp from shadow to highlight, and how the surface is finished
    'bronze': dict(ramp=[(28, 18, 10), (66, 44, 24), (112, 78, 42), (158, 114, 62), (198, 152, 88), (232, 196, 132), (252, 234, 188)],
                   spec=(255, 236, 196), spec_amt=1.0, spec_pow=38, brushed=0.035, brush_len=5, hammer=0.06, sheen=0.08, polish=0.1, patina=(-16, -4, 6)),
    # matte brushed steel (Cam, Nov 5: the bronze was too shiny): a soft, broad highlight, long fine brushing, no hammering
    'steel': dict(ramp=[(20, 22, 25), (44, 48, 53), (76, 81, 87), (110, 115, 121), (142, 147, 152), (172, 176, 180), (200, 203, 206)],
                  spec=(226, 230, 234), spec_amt=0.22, spec_pow=10, brushed=0.06, brush_len=14, hammer=0.0, sheen=0.04, polish=0.04, patina=(-6, -4, -2)),
}


def card(name):
    return next(c for c in pass3.ALL if c[1] == name)


def render_faces(names, tmp):
    from playwright.sync_api import sync_playwright
    faces = ''
    for k, n in enumerate(names):
        c = card(n)
        faces += f'<div id="p{k}" style="display:inline-block;margin:8px">{P3.perm_face(3000 + 2 * k, c)}</div>'
        faces += f'<div id="f{k}" style="display:inline-block;margin:8px">{P3.force_face(3001 + 2 * k, c)}</div>'
    page = ('<!doctype html><html><head><meta charset="utf-8">' + local_fonts() +
            '<style>body{margin:0;background:#191B1A;color:#ECE6D6;font-family:"Cormorant Garamond",Georgia,serif}</style></head>'
            f'<body><div style="width:{(320 + 16) * 2}px">{faces}</div></body></html>')
    path = os.path.join(tmp, 'plates_src.html')
    open(path, 'w').write(page)
    out = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(device_scale_factor=S, viewport={'width': 800, 'height': 1000})
        pg.goto('file://' + path); pg.wait_for_timeout(600)
        pg.evaluate('document.fonts.ready')
        for k, n in enumerate(names):
            for side, sel in (('perm', f'#p{k} .face'), ('force', f'#f{k} .face')):
                f = os.path.join(tmp, f'src-{n}-{side}.png')
                pg.locator(sel).screenshot(path=f)
                out[(n, side)] = f
        b.close()
    return out


def rounded_mask(w, h, r):
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    cx = np.clip(xx, r, w - 1 - r); cy = np.clip(yy, r, h - 1 - r)
    return np.hypot(xx - cx, yy - cy) <= r


def rrect(w, h, x0, y0, x1, y1, r):
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    cx = np.clip(xx, x0 + r, x1 - r); cy = np.clip(yy, y0 + r, y1 - r)
    return np.hypot(xx - cx, yy - cy) <= r


def ramp(v, stops):
    v = np.clip(v, 0, 1) * (len(stops) - 1)
    i = np.clip(v.astype(int), 0, len(stops) - 2); t = (v - i)[..., None]
    st = np.array(stops, float)
    return st[i] * (1 - t) + st[i + 1] * t


def make_plate(src, side, mode='raised', metal='bronze', seed=0):
    a = np.asarray(Image.open(src).convert('RGB')).astype(float)
    a = a[:H, :W]
    a = a[:, ::-1]                                                     # a plate is the mirror of its card
    V = a.max(-1)
    card = rounded_mask(W, H, 14 * S)
    rng = np.random.default_rng(seed)
    # what stands up: anything drawn lighter than the face's ground (lines, lettering, rings, footer)
    lines = np.clip((V - 88) / 90, 0, 1)
    lines = gaussian_filter(lines, 0.6)
    lines = 1 / (1 + np.exp(-(lines - 0.35) * 14))                    # flat tops, steep shoulders
    lines = gaussian_filter(lines, 0.9) * card
    # the plate's own shape: a bevelled edge, a raised frame line inset from it, a sunken art panel
    d_edge = edt(card)
    frame = rrect(W, H, 6 * S, 6 * S, W - 1 - 6 * S, H - 1 - 6 * S, 9 * S) & ~rrect(W, H, 9 * S, 9 * S, W - 1 - 9 * S, H - 1 - 9 * S, 6 * S)
    frame = gaussian_filter(frame.astype(float), 0.8)
    ph = P3.PH if side == 'perm' else P3.FH
    panel = rrect(W, H, W - (16 + 288) * S, 50 * S, W - 16 * S, (50 + ph) * S, 10 * S)   # mirrored position
    panel = gaussian_filter(panel.astype(float), 1.2 * S)
    bevel = np.clip(d_edge / (3.5 * S), 0, 1) ** 0.7
    field = 0.35 * bevel + 0.75 * frame - 0.5 * panel
    # worked surface: fine hammering on the field, a fine brushed grain over everything
    hammer = gaussian_filter(rng.standard_normal((H, W)), 1.6 * S)
    hammer = hammer / (np.abs(hammer).max() + 1e-6)
    M = METAL[metal]
    brushed = gaussian_filter(rng.standard_normal((H, W)), (0.35, M['brush_len'] * S)) + 0.5 * gaussian_filter(rng.standard_normal((H, W)), (0.3, 1.5 * S))
    brushed = brushed / (np.abs(brushed).max() + 1e-6)
    if mode == 'raised':
        Hm = field + 1.05 * lines + M['hammer'] * hammer * (1 - lines)
    else:                                                              # engraved: the drawing is cut into the plate
        Hm = field - 0.95 * lines + M['hammer'] * hammer * (1 - lines)
    Hm = Hm * card
    # light from the upper left; normals from the height map
    k = 9.0
    gy, gx = np.gradient(gaussian_filter(Hm, 0.7))
    nx, ny, nz = -gx * k, -gy * k, np.ones_like(Hm)
    nl = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2); nx, ny, nz = nx / nl, ny / nl, nz / nl
    L = np.array([-0.55, -0.62, 0.56]); L /= np.linalg.norm(L)
    diff = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    Hv = L + np.array([0, 0, 1.0]); Hv /= np.linalg.norm(Hv)
    spec = np.clip(nx * Hv[0] + ny * Hv[1] + nz * Hv[2], 0, 1) ** METAL[metal]['spec_pow']
    # cavities hold dark patina; tops are polished
    occl = gaussian_filter(Hm, 4 * S) - Hm
    ao = np.clip(1 - 2.4 * np.clip(occl, 0, None), 0.3, 1)
    top = np.clip(Hm - gaussian_filter(Hm, 3 * S), 0, None)
    polish = np.clip(top * 3.0, 0, 1) if mode == 'raised' else np.clip(frame * 0.7, 0, 1)
    # cast shadows, the trick that sells the depth: raised work throws a shadow down and right onto the
    # field; a cut line is shadowed along its upper-left wall and lit along its lower-right lip
    def shift(m, dx, dy):
        o = np.zeros_like(m); o[max(0, dy):, max(0, dx):] = m[:H - max(0, dy), :W - max(0, dx)]; return o
    if mode == 'raised':
        cast = gaussian_filter(shift(lines, int(1.6 * S), int(2.2 * S)), 1.4 * S) * (1 - lines)
        shade = 1 - 0.55 * np.clip(cast, 0, 1)
        lip = 0
    else:
        inner = lines * (1 - gaussian_filter(shift(lines, int(1.4 * S), int(1.8 * S)), 0.8 * S))
        shade = 1 - 0.6 * np.clip(inner, 0, 1)
        lip = np.clip(shift(lines, int(1.2 * S), int(1.6 * S)) - lines, 0, 1)
    # a broad sheen across the plate, brighter toward the light, as on polished metal
    YY, XX = np.mgrid[0:H, 0:W]
    sheen = 0.5 + 0.5 * np.cos((XX / W * 0.9 + YY / H * 1.1) * np.pi * 1.1)
    v = (0.1 + 0.7 * diff * ao + M['brushed'] * brushed + M['polish'] * polish + M['sheen'] * sheen) * shade + 0.25 * lip
    col = ramp(v, M['ramp'])
    col += spec[..., None] * np.array(M['spec']) * M['spec_amt'] * (0.45 + 0.55 * polish[..., None])
    patina = np.clip(occl * 3, 0, 1)[..., None] * np.array(M['patina'])
    col = np.clip(col + patina, 0, 255)
    alpha = (gaussian_filter(card.astype(float), 0.6) * 255).astype(np.uint8)
    return Image.fromarray(np.dstack([col.astype(np.uint8), alpha]), 'RGBA')


def main(out):
    os.makedirs(out, exist_ok=True)
    tmp = os.path.join(out, 'src'); os.makedirs(tmp, exist_ok=True)
    srcs = render_faces(CARDS, tmp)
    made = []
    for (n, side), f in srcs.items():
        slug = n.lower().replace(' ', '-')
        for m in DRAW_METALS:
            make_plate(f, side, 'raised', metal=m, seed=hash(n) % 1000).save(os.path.join(out, f'{slug}-{side}-plate-{m}.png'))
            made.append(f'{slug}-{side}-plate-{m}.png')
        if n in ENGRAVED_TOO:
            make_plate(f, side, 'engraved', seed=hash(n) % 1000).save(os.path.join(out, f'{slug}-{side}-plate-engraved.png'))
            made.append(f'{slug}-{side}-plate-engraved.png')
    print('\n'.join(made))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '.')
