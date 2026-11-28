# Pixel art for the framework set (Nov 28). `python3 build.py` renders every card's art into branch-b/img/pixel/;
# `python3 page.py out.html` makes the Framework Set page. Placeholder art; the scene specs are in specs.py.
# Render every card's art to small PNGs (48 cells wide), plus a contact sheet to review them.
import json, sys, collections
HERE = __file__.rsplit('/', 1)[0]; sys.path.insert(0, HERE); ROOT = HERE.rsplit('/', 3)[0]
import engine, specs, art_pixel
from PIL import Image
POOL = json.load(open(ROOT + '/data/cards-branch-b.json'))['cards']
def save_grid(p, path):
    h, w = len(p), len(p[0]); im = Image.new('RGB', (w, h))
    im.putdata([tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for row in p for c in row]); im.save(path, optimize=True)
SPECIAL = {'Volcano': (art_pixel.volcano_front, art_pixel.volcano_back), 'Tide Pool': (art_pixel.tidepool_front, art_pixel.tidepool_back)}
def dominant(pips):
    c = collections.Counter(p.split('|')[0] for p in pips if p != 'any')
    return c.most_common(1)[0][0] if c else None
kinds = {}
for c in POOL:
    n, no = c['name'], c['no']
    if c.get('meta'):
        engine.render(specs.META[n], 31, no).png(ROOT + '/branch-b/img/pixel/%03d-meta.png' % no); continue
    if n in SPECIAL:
        save_grid(SPECIAL[n][0]().p, ROOT + '/branch-b/img/pixel/%03d-front.png' % no); save_grid(SPECIAL[n][1]().p, ROOT + '/branch-b/img/pixel/%03d-back.png' % no); kinds[n] = 'hand-made'; continue
    sp = specs.L[n]
    engine.render(sp, 46, no).png(ROOT + '/branch-b/img/pixel/%03d-front.png' % no)
    bs, kind = specs.back_spec(sp, c['back']['name'], dominant(c['front']['pips']))
    engine.render(bs, 31, no + 1000).png(ROOT + '/branch-b/img/pixel/%03d-back.png' % no); kinds[n] = kind
json.dump(kinds, open(ROOT + '/branch-b/img/pixel/back-kinds.json', 'w'), indent=0)
print('ok', len(POOL))
