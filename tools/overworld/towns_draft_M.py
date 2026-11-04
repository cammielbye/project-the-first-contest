#!/usr/bin/env python3
"""Towns on Draft M (Nov 4): a first pass at where towns sit on today's continents.

Draws numbered town marks over drafts/draftM_today.png and writes ow_towns_M.png next to this script.
Ports are snapped to the nearest coast; inland towns are kept off the coast and off high ground.
The middle island's mark is the hollow mountain's port (see "The hollow mountain" board)."""
import pathlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import distance_transform_edt as edt, binary_fill_holes

HERE = pathlib.Path(__file__).resolve().parent
INK, PAPER, SEA_INK = (58, 46, 34), (241, 232, 210), (52, 104, 140)
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 21)

# (number, kind, rough x, rough y, what it is) on the 1704x1068 map
TOWNS = [
    (1, "port", 528, 300, "North port, in the bay under the lake country"),
    (2, "town", 418, 512, "Lake town, on the lake's south shore where the river leaves it"),
    (3, "port", 196, 520, "West port, the far side of the world from the strait"),
    (4, "town", 300, 640, "Crossroads town between the west coast and the southern hills"),
    (5, "town", 560, 712, "Highland town in the valley between the great range and the cut-off range"),
    (6, "port", 548, 818, "South port, near the sea stacks at the foot of the cliffs"),
    (7, "hollow", 1012, 648, "The hollow mountain's port, inside the island's high ground"),
    (8, "port", 1176, 700, "Strait port across the narrow strait from the hollow mountain"),
    (9, "port", 1262, 300, "North point, at the right continent's northern tip"),
    (10, "town", 1440, 560, "Lowland town in the open east"),
    (11, "port", 1546, 498, "East port, on the outer coast"),
    (12, "port", 1386, 668, "Southeast port, on the long south shore"),
]


def main():
    im = Image.open(HERE / "drafts" / "draftM_today.png").convert("RGB")
    a = np.asarray(im).astype(int)
    land = (a[..., 0] > 195) & (a[..., 1] > 180) & (a[..., 2] > 145) & (a[..., 0] - a[..., 2] > 25)
    land = binary_fill_holes(land)
    dark = (a.sum(-1) < 330)                       # ink: coast lines, mountains, rivers
    d_sea = edt(land)
    d = ImageDraw.Draw(im)
    placed = []
    for n, kind, x, y, _ in TOWNS:
        if kind == "hollow":  # sits right on the island's high ground
            placed.append((n, kind, x, y)); continue
        if kind == "port":   # nearest land pixel 5-9 px in from the shore
            ring = land & (d_sea > 5) & (d_sea < 9)
            ys, xs = np.nonzero(ring)
        else:                # inland: off the coast and off inked high ground
            ok = land & (d_sea > 30)
            ys, xs = np.nonzero(ok)
            keep = []
            for i in np.argsort((xs - x) ** 2 + (ys - y) ** 2)[:4000]:
                yy, xx = ys[i], xs[i]
                if dark[max(0, yy - 9):yy + 10, max(0, xx - 9):xx + 10].mean() < 0.04:
                    keep.append(i); break
            ys, xs = ys[keep], xs[keep]
        j = int(np.argmin((xs - x) ** 2 + (ys - y) ** 2))
        px, py = int(xs[j]), int(ys[j])
        placed.append((n, kind, px, py))
        print(n, kind, "->", px, py, "moved", round(float(np.hypot(px - x, py - y)), 1))
    for n, kind, x, y in placed:
        if kind == "hollow":
            r = 13
            d.ellipse((x - r - 5, y - r - 5, x + r + 5, y + r + 5), fill=PAPER, outline=INK, width=2)
            d.ellipse((x - r + 1, y - r + 1, x + r - 1, y + r - 1), outline=INK, width=3)
            d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=INK)
        elif kind == "port":   # an anchor in a ring
            d.ellipse((x - 11, y - 11, x + 11, y + 11), fill=PAPER, outline=INK, width=2)
            d.line([(x, y - 5), (x, y + 6)], fill=INK, width=2)
            d.ellipse((x - 2, y - 8, x + 2, y - 4), outline=INK, width=1)
            d.line([(x - 4, y - 2), (x + 4, y - 2)], fill=INK, width=2)
            d.arc((x - 6, y - 1, x + 6, y + 7), 10, 170, fill=INK, width=2)
        else:
            d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=PAPER, outline=INK, width=2)
            d.rectangle((x - 4, y - 4, x + 4, y + 4), fill=INK)
        tx, ty = x + 15, y - 14
        if n in (3,):
            tx = x + 14
        if n in (11,):
            tx = x - 40
        d.text((tx, ty), str(n), font=FONT, fill=INK, stroke_width=3, stroke_fill=PAPER)
    im.save(HERE / "ow_towns_M.png")


if __name__ == "__main__":
    main()
