#!/usr/bin/env python3
"""Writes the plates board ("Plates") for the Card Anatomy canvas: each card's two faces beside its plate.
Plate images are the PNGs from plates.py, uploaded to the canvas as assets; their blob urls go in BLOBS.
  python3 tools/cards/plates_board.py <project folder> <blobs.json>"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pass3_cards as P3, pass3
from plates import CARDS, card

W, H = 1480, 2470
MONO = P3.MONO
RAR = {'C': 'COMMON', 'B': 'UNCOMMON', 'A': 'RARE', 'S': 'PINNACLE'}


def img(src, alt):
    return (f'<img src="{src}" alt="{alt}" style="display: block; width: 320px; height: 448px; flex: none; border-radius: 14px; '
            f'box-shadow: 0 14px 32px rgba(0,0,0,0.55)">')


def pair(left, right, cap):
    return (f'<div style="display: flex; flex-direction: column; gap: 10px"><div style="display: flex; gap: 12px">{left}{right}</div>'
            f'<div style="{P3.CAP}; text-align: center">{cap}</div></div>')


def board(blobs):
    body = f'''<div style="display: flex; flex-direction: column; gap: 6px">
<h1 style="margin: 0; font-size: 40px; font-weight: 600">Plates</h1>
<p style="margin: 0; {MONO}; font-size: 13px; color: #A9ADA2; max-width: 1900px">Nov 5, 2026. Cam's idea (LORE-02): the originals are metal plates that press the cards, with the art and text mirrored. Each card is shown beside its plate, one card per rarity, both faces, with the drawing raised as on a stamp (Cam's pick over engraved). Clean bronze is the current best (Cam, after drafts in matte brushed steel and weathered bronze). Placeholders until an artist does the art.</p>
</div>
'''
    i = 5000
    for n in CARDS:
        c = card(n); slug = n.lower().replace(' ', '-'); i += 2
        row = pair(P3.perm_face(i, c), P3.force_face(i + 1, c), 'CARD · PERMANENCE AND FORCE')
        for m, cap in (('bronze', 'PLATE · BRONZE (CURRENT BEST)'),):
            row += pair(img(blobs[f'{slug}-perm-plate-{m}.png'], f'{n} plate in {m}, permanence face, mirrored'),
                        img(blobs[f'{slug}-force-plate-{m}.png'], f'{n} plate in {m}, force face, mirrored'), cap)
        body += (f'<div style="display: flex; flex-direction: column; gap: 14px">{P3.label(RAR[c[2]] + " · " + n.upper())}'
                 f'<div style="display: flex; gap: 56px">{row}</div></div>\n')
    return P3.HEAD.format(title='Plates', W=W, H=H, local='') + body + P3.TAIL.format(W=W, H=H)


if __name__ == '__main__':
    blobs = json.load(open(sys.argv[2]))
    open(os.path.join(sys.argv[1], 'Plates.dc.html'), 'w').write(board(blobs))
    print('wrote Plates.dc.html', W, H)
