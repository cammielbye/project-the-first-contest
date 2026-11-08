# Measure line counts of every third-pass text at a range of sizes, with the real font.
import sys, os, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pass3
from fontcss import local_fonts
def fmt(t): return html.escape(t).replace("'", '’').replace('◯', '<span style="display:inline-block;width:.72em;height:.72em;border:2px solid #E6E1D3;border-radius:50%;vertical-align:-0.05em;box-sizing:border-box"></span>')
items = []
for c in pass3.ALL:
    if c[4]: items.append(('p', c[1], c[4]))
    items.append(('f', c[5], c[7]))
for m in pass3.META: items.append(('m', m[1], m[3]))
W = int(sys.argv[1]) if len(sys.argv) > 1 else 280
body = ''
for k, (kind, name, t) in enumerate(items):
    for s in range(18, 37):
        st = 'italic' if kind == 'p' else 'normal'
        body += '<div class="m" data-k="%d" data-s="%d" style="width:%dpx;font:%s 500 %dpx/1.08 \'Cormorant Garamond\';text-align:center">%s</div>' % (k, s, W, st, s, fmt(t))
open(os.path.join(os.path.dirname(__file__), '..', 'm3.html'), 'w').write('<!doctype html><html><head><meta charset="utf-8">' + local_fonts() + '</head><body>' + body + '</body></html>')
json.dump(items, open(os.path.join(os.path.dirname(__file__), '..', 'm3items.json'), 'w'))
