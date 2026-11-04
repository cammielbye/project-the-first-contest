import sys, os, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fontcss import local_fonts
items = json.load(open(sys.argv[1]))  # [[kind, text]]
body = ''
for k, (kind, t) in enumerate(items):
    for s in range(18, 31):
        st = 'italic' if kind == 'p' else 'normal'
        body += '<div class="m" data-k="%d" data-s="%d" style="width:296px;font:%s 500 %dpx/1.08 \'Cormorant Garamond\';text-align:center">%s</div>' % (k, s, st, s, html.escape(t).replace("'", '’'))
open(sys.argv[2], 'w').write('<!doctype html><html><head><meta charset="utf-8">' + local_fonts() + '</head><body>' + body + '</body></html>')
