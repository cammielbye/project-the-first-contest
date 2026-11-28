# Pixel art for the framework set (Nov 28). `python3 build.py` renders every card's art into branch-b/img/pixel/;
# `python3 page.py out.html` makes the Framework Set page. Placeholder art; the scene specs are in specs.py.
# The framework set page: all 100 cards in the chosen look. Sorted by number of pips, then rarity, both ascending. Click a landscape to flip it.
import json, base64, html, sys
HERE = __file__.rsplit('/', 1)[0]; sys.path.insert(0, HERE); ROOT = HERE.rsplit('/', 3)[0]
from common import GLYPH, ORDER
esc = html.escape
POOL = json.load(open(ROOT + '/data/cards-branch-b.json'))['cards']
RCOL = {'C': '#85837D', 'B': '#86A08C', 'A': '#A88FB0', 'S': '#C99C62'}
RWORD = {'C': 'common', 'B': 'uncommon', 'A': 'rare', 'S': 'pinnacle'}
def uri(path): return 'data:image/png;base64,' + base64.b64encode(open(path, 'rb').read()).decode()
def symbols():
    out = []
    for el in ORDER:
        d, c = GLYPH[el]; sc = 0.78; t = 'translate(%.2f %.2f) scale(%.3f)' % (16 - 12 * sc, 16.4 - 12 * sc, sc)
        own = ' fill="#000"' if el == 'any' else ''
        out.append('<symbol id="pip-%s" viewBox="0 0 32 32"><circle cx="16" cy="16" r="15" fill="#101211"/><circle cx="16" cy="16" r="14.3" fill="none" stroke="#C2C5B8" stroke-width="1.2"/>'
                   '<g transform="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linejoin="miter" stroke-linecap="butt"><path d="%s"%s/></g></symbol>' % (el, t, c, '1.1' if el == 'any' else '1.9', d, own))
    # an either-or pip: the two symbols side by side on one disc
    return '<svg width="0" height="0" style="position:absolute" aria-hidden="true">%s</svg>' % ''.join(out)
def pip_html(p, size):
    if '|' in p:
        a, b = p.split('|')
        return ('<span class="eo" style="--z:%dpx" role="img" aria-label="%s or %s pip"><svg viewBox="0 0 32 32"><use href="#pip-%s"/></svg><i>/</i><svg viewBox="0 0 32 32"><use href="#pip-%s"/></svg></span>' % (size, a, b, a, b))
    return '<svg class="pip" style="width:%dpx;height:%dpx" viewBox="0 0 32 32" role="img" aria-label="%s pip"><use href="#pip-%s"/></svg>' % (size, size, p, p)
def pips(ps, size):
    key = lambda p: ORDER.index(p.split('|')[0])
    return ''.join(pip_html(p, size) for p in sorted(ps, key=key))
def rmark(r, col):
    return '<span class="rar" style="--rc:%s" role="img" aria-label="Rarity: %s"><i></i><b>%s</b></span>' % (col, RWORD[r], r)
def frame(col, inner):
    return '<div class="face-body" style="--rc:%s"><div class="ring"></div><div class="plate"></div>%s</div>' % (col, inner)
def landscape(c):
    no, r = c['no'], c['rarity']; col = RCOL[r]; f, b = c['front'], c['back']
    front = frame(col, '<div class="nm">%s</div><img class="art" src="%s" alt="%s, pixel art placeholder">'
                       '<div class="pips">%s</div><div class="rule"></div><div class="no">%d/100</div>%s'
                       % (esc(c['name']), uri(ROOT + '/branch-b/img/pixel/%03d-front.png' % no), esc(c['name']), pips(f['pips'], 30), no, rmark(r, col)))
    ft = ('<div class="ftxt">%s</div>' % esc(f['text'])) if f['text'] else ''
    if ft: front = front.replace('<div class="rule"></div>', ft + '<div class="rule"></div>', 1)
    if b['text']:
        text = b['text'].replace(' Next turn, flip this back.', '')
        fb = '<span class="fb">flips back</span>' if b['flipsBack'] else ''
        btxt = '<div class="btxt"><span class="ph">placeholder</span>%s%s</div>' % (esc(text), fb)
        bname = esc(b['name'])
    else:
        btxt = '<div class="btxt open"><span class="ph">open</span>No force yet.</div>'; bname = '&nbsp;'
    bpips = pips(b['pips'], 26) if b['pips'] else '<span class="nopips">no pips</span>'
    back = frame(col, '<div class="nm">%s</div><img class="art art-b" src="%s" alt="%s back, pixel art placeholder">'
                      '<div class="pips pips-b">%s</div>%s<div class="rule"></div><div class="no">%d/100</div>%s'
                      % (bname, uri(ROOT + '/branch-b/img/pixel/%03d-back.png' % no), esc(c['name']), bpips, btxt, no, rmark(r, col)))
    els = sorted({p.split('|')[0] for p in f['pips']} | {p.split('|')[1] for p in f['pips'] if '|' in p})
    key = '%d-%d-%s-%03d' % (len(f['pips']), 'CBAS'.index(r), ''.join(str(ORDER.index(p.split('|')[0])) + ('9' if '|' in p else '') for p in sorted(f['pips'], key=lambda p: ORDER.index(p.split('|')[0]))), no)
    return ('<li class="slot" data-n="%d" data-k="%s" data-g="%d" data-r="%s" data-el="%s" data-q="%s"><button class="card" aria-label="%s, card %d. Click to flip." aria-pressed="false">'
            '<span class="flip"><span class="face front">%s</span><span class="face back">%s</span></span></button></li>'
            % (no, key, len(f['pips']), r, ' '.join(els), esc((c['name'] + ' ' + (b['name'] or '')).lower()), esc(c['name']), no, front, back))
def meta(c):
    no = c['no']
    body = frame('#0B0B0B', '<div class="nm">%s</div><img class="art art-b" src="%s" alt="%s, pixel art placeholder">'
                            '<div class="pips pips-b"><span class="nopips">meta card · one face</span></div>'
                            '<div class="btxt"><span class="ph">placeholder</span>%s</div><div class="rule"></div><div class="no">%d/100</div>'
                            % (esc(c['name']), uri(ROOT + '/branch-b/img/pixel/%03d-meta.png' % no), esc(c['name']), esc(c['text']), no))
    return ('<li class="slot" data-n="%d" data-k="9-9-%03d" data-g="9" data-r="M" data-el="" data-q="%s"><div class="card meta" role="group" aria-label="%s, meta card %d"><span class="flip"><span class="face front">%s</span></span></div></li>'
            % (no, no, esc(c['name'].lower()), esc(c['name']), no, body))
cards = ''.join(meta(c) if c.get('meta') else landscape(c) for c in POOL)
n = {k: sum(1 for c in POOL if (c.get('meta') and k == 'M') or c.get('rarity') == k and not c.get('meta')) for k in 'CBASM'}
CSS = '''
:root { color-scheme: dark; --bg: #1A1D1B; --ink: #E8E2CF; --muted: #9AA096; --s: 0.72; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font-family: 'IBM Plex Sans', system-ui, sans-serif; }
.wrap { max-width: 1480px; margin: 0 auto; padding: 32px 24px 64px; }
h1 { font-family: 'Silkscreen', monospace; font-weight: 400; font-size: 30px; letter-spacing: 0.04em; margin: 0 0 8px; }
.lede { max-width: 860px; color: #C8C4B4; font-size: 16px; line-height: 1.5; margin: 0 0 20px; }
.bar { position: sticky; top: 0; z-index: 5; display: flex; flex-wrap: wrap; gap: 10px 18px; align-items: center; padding: 12px 0; background: var(--bg); border-bottom: 1px solid #2E332F; margin-bottom: 22px; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip { font: 500 14px/1 'IBM Plex Sans', system-ui, sans-serif; color: var(--ink); background: #232724; border: 1px solid #3A403A; border-radius: 999px; padding: 9px 13px; cursor: pointer; display: inline-flex; gap: 7px; align-items: center; min-height: 36px; }
.chip i { width: 11px; height: 11px; border-radius: 3px; background: var(--rc); border: 1px solid #0B0B0B; }
.chip[aria-pressed="true"] { background: #E8E2CF; color: #1A1D1B; border-color: #E8E2CF; }
.chip small { color: inherit; opacity: 0.7; font-size: 12px; }
.tog { display: inline-flex; gap: 8px; align-items: center; font-size: 14px; cursor: pointer; }
.tog input { width: 18px; height: 18px; accent-color: #86A08C; }
.search { font: 14px 'IBM Plex Sans', system-ui; color: var(--ink); background: #232724; border: 1px solid #3A403A; border-radius: 8px; padding: 9px 12px; min-width: 200px; }
.size { display: inline-flex; gap: 8px; align-items: center; font-size: 14px; color: var(--muted); }
.grid { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fill, calc(320px * var(--s))); gap: 22px 18px; justify-content: center; }
.slot { width: calc(320px * var(--s)); height: calc(448px * var(--s)); perspective: 1400px; }
.slot[hidden], .sep[hidden] { display: none; }
.sep { grid-column: 1 / -1; display: flex; align-items: baseline; gap: 12px; margin: 14px 0 -4px; padding-bottom: 6px; border-bottom: 1px solid #2E332F; font-family: 'Silkscreen', monospace; font-size: 17px; letter-spacing: 0.04em; color: #E8E2CF; }
.sep:first-child { margin-top: 0; }
.sep small { font-family: 'IBM Plex Sans', system-ui, sans-serif; font-size: 13px; color: #9AA096; letter-spacing: 0; }
.sort { display: inline-flex; gap: 8px; align-items: center; font-size: 14px; color: var(--muted); }
.sort select { font: 14px 'IBM Plex Sans', system-ui; color: var(--ink); background: #232724; border: 1px solid #3A403A; border-radius: 8px; padding: 8px 10px; min-height: 36px; }
.card { all: unset; display: block; width: 320px; height: 448px; transform: scale(var(--s)); transform-origin: top left; cursor: pointer; border-radius: 10px; }
.card.meta { cursor: default; }
.card:focus-visible { outline: 3px solid #E8E2CF; outline-offset: 4px; }
.flip { display: block; position: relative; width: 320px; height: 448px; transform-style: preserve-3d; transition: transform 0.5s cubic-bezier(.3,.7,.3,1); }
.card[aria-pressed="true"] .flip { transform: rotateY(180deg); }
.face { position: absolute; inset: 0; backface-visibility: hidden; -webkit-backface-visibility: hidden; }
.face.back { transform: rotateY(180deg); }
.face-body { position: absolute; inset: 0; border-radius: 10px; background: var(--rc); box-shadow: 0 10px 22px rgba(0,0,0,0.45); }
.ring { position: absolute; inset: 8px; border-radius: 6px; background: #0B0B0B; }
.plate { position: absolute; inset: 11px; border-radius: 5px; background: #1E221F; }
.nm { position: absolute; top: 12px; left: 16px; width: 288px; height: 36px; display: flex; align-items: center; justify-content: center; font-family: 'Silkscreen', monospace; font-size: 19px; letter-spacing: 0.04em; text-transform: uppercase; color: #E8E2CF; white-space: nowrap; }
.art { position: absolute; top: 52px; left: 16px; width: 288px; height: 276px; image-rendering: pixelated; clip-path: polygon(8px 0, calc(100% - 8px) 0, calc(100% - 8px) 4px, calc(100% - 4px) 4px, calc(100% - 4px) 8px, 100% 8px, 100% calc(100% - 8px), calc(100% - 4px) calc(100% - 8px), calc(100% - 4px) calc(100% - 4px), calc(100% - 8px) calc(100% - 4px), calc(100% - 8px) 100%, 8px 100%, 8px calc(100% - 4px), 4px calc(100% - 4px), 4px calc(100% - 8px), 0 calc(100% - 8px), 0 8px, 4px 8px, 4px 4px, 8px 4px); }
.art-b { height: 186px; }
.pips { position: absolute; top: 336px; left: 16px; width: 288px; height: 38px; display: flex; align-items: center; justify-content: center; gap: 10px; }
.pips-b { top: 244px; height: 30px; gap: 8px; }
.pip { display: block; }
.eo { display: inline-flex; align-items: center; gap: 1px; }
.eo svg { width: calc(var(--z) * 0.86); height: calc(var(--z) * 0.86); }
.eo i { font-style: normal; font-family: 'VT323', monospace; font-size: 22px; color: #9AA096; }
.nopips { font-family: 'VT323', monospace; font-size: 18px; letter-spacing: 0.06em; text-transform: uppercase; color: #7E847A; }
.ftxt { position: absolute; top: 284px; left: 20px; width: 280px; text-align: center; font-family: 'VT323', monospace; font-size: 19px; color: #E8E2CF; background: rgba(16,18,17,0.88); padding: 2px 4px; }
.btxt { position: absolute; top: 280px; left: 22px; width: 276px; height: 96px; padding: 16px 10px 6px; display: flex; align-items: center; justify-content: center; text-align: center; font-family: 'VT323', monospace; font-size: 21px; line-height: 1.0; color: #B8B4A6; background: #2A2E2A; border-radius: 4px; flex-wrap: wrap; }
.btxt.open { color: #7E847A; }
.ph { position: absolute; top: 4px; right: 7px; font-size: 13px; letter-spacing: 0.08em; text-transform: uppercase; color: #7E847A; }
.fb { position: absolute; top: 4px; left: 7px; font-size: 13px; letter-spacing: 0.08em; text-transform: uppercase; color: #8FB0C0; }
.rule { position: absolute; top: 386px; left: 30px; width: 260px; border-top: 2px dashed #3A403A; }
.no { position: absolute; left: 24px; top: 396px; height: 36px; display: flex; align-items: center; font-family: 'VT323', monospace; font-size: 22px; letter-spacing: 0.04em; color: #9AA096; }
.rar { position: absolute; right: 20px; top: 396px; width: 36px; height: 36px; }
.rar i { position: absolute; top: 8px; left: 8px; width: 18px; height: 18px; transform: rotate(45deg); border: 1.6px solid var(--rc); }
.rar b { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-family: 'VT323', monospace; font-size: 20px; color: var(--rc); }
.notes { margin-top: 40px; max-width: 860px; color: #A8A496; font-size: 14px; line-height: 1.55; }
.notes b { color: var(--ink); }
@media (max-width: 640px) { :root { --s: 0.5; } .bar { position: static; } .wrap { padding: 20px 12px 48px; } .grid { gap: 14px 10px; } }
@media (prefers-reduced-motion: reduce) { .flip { transition: none; } }
'''
JS = '''
(function () {
  var grid = document.getElementById('grid'), slots = [].slice.call(grid.querySelectorAll('.slot')), state = { r: 'all', q: '', sort: 'pips' };
  var NAMES = { 0: 'No pips', 1: 'One pip', 2: 'Two pips', 3: 'Three pips', 4: 'Four pips', 9: 'Meta cards' };
  function order() {
    [].forEach.call(grid.querySelectorAll('.sep'), function (h) { h.remove(); });
    var list = slots.slice().sort(function (a, b) {
      return state.sort === 'pips' ? (a.dataset.k < b.dataset.k ? -1 : 1) : (+a.dataset.n - +b.dataset.n);
    });
    var last = null;
    list.forEach(function (s) {
      if (state.sort === 'pips' && s.dataset.g !== last) {
        last = s.dataset.g; var h = document.createElement('li'); h.className = 'sep'; h.dataset.g = last;
        h.setAttribute('role', 'presentation'); h.innerHTML = NAMES[last] + ' <small></small>'; grid.appendChild(h);
      }
      grid.appendChild(s);
    });
  }
  function apply() {
    var count = {};
    slots.forEach(function (s) {
      var ok = (state.r === 'all' || s.dataset.r === state.r) && (!state.q || s.dataset.q.indexOf(state.q) >= 0);
      s.hidden = !ok; if (ok) count[s.dataset.g] = (count[s.dataset.g] || 0) + 1;
    });
    [].forEach.call(grid.querySelectorAll('.sep'), function (h) {
      var n = count[h.dataset.g] || 0; h.hidden = !n; h.querySelector('small').textContent = n + (n === 1 ? ' card' : ' cards');
    });
  }
  document.getElementById('sort').addEventListener('change', function (e) { state.sort = e.target.value; order(); apply(); });
  order(); apply();
  grid.addEventListener('click', function (e) {
    var b = e.target.closest('button.card'); if (!b) return;
    b.setAttribute('aria-pressed', b.getAttribute('aria-pressed') === 'true' ? 'false' : 'true');
  });
  [].forEach.call(document.querySelectorAll('.chip'), function (c) {
    c.addEventListener('click', function () {
      [].forEach.call(document.querySelectorAll('.chip'), function (x) { x.setAttribute('aria-pressed', 'false'); });
      c.setAttribute('aria-pressed', 'true'); state.r = c.dataset.r; apply();
    });
  });
  document.getElementById('q').addEventListener('input', function (e) { state.q = e.target.value.trim().toLowerCase(); apply(); });
  document.getElementById('backs').addEventListener('change', function (e) {
    [].forEach.call(document.querySelectorAll('button.card'), function (b) { b.setAttribute('aria-pressed', e.target.checked ? 'true' : 'false'); });
  });
  document.getElementById('sz').addEventListener('input', function (e) { document.documentElement.style.setProperty('--s', e.target.value); });
})();
'''
chips = '<button class="chip" data-r="all" aria-pressed="true">All <small>100</small></button>' + ''.join(
    '<button class="chip" data-r="%s" aria-pressed="false" style="--rc:%s"><i></i>%s <small>%d</small></button>' % (k, RCOL.get(k, '#0B0B0B'), {'C': 'Common', 'B': 'Uncommon', 'A': 'Rare', 'S': 'Pinnacle', 'M': 'Meta'}[k], n[k]) for k in 'CBASM')
page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Framework Set</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Silkscreen&family=VT323&family=IBM+Plex+Sans:wght@400;500&display=swap">
<style>{CSS}</style>
</head>
<body>
{symbols()}
<div class="wrap">
<h1>Framework Set</h1>
<p class="lede">All 100 cards with their names, pixel art, layout and pips (Nov 28). Click a landscape to flip it. The abilities and effects on the backs are placeholders. Cam: "the abilities and effects should currently be considered messy." The art is quick template art, to be hand-tuned for the cards you care about.</p>
<div class="bar" role="toolbar" aria-label="Filters">
<div class="chips">{chips}</div>
<label class="sort">Sort <select id="sort" aria-label="Sort cards"><option value="pips" selected>By pips, then rarity</option><option value="no">By number</option></select></label>
<label class="tog"><input type="checkbox" id="backs"> Show backs</label>
<input class="search" id="q" type="search" placeholder="Find a card" aria-label="Find a card by name">
<label class="size">Size <input id="sz" type="range" min="0.45" max="1" step="0.05" value="0.72" aria-label="Card size"></label>
</div>
<ol class="grid" id="grid">{cards}</ol>
<div class="notes">
<p><b>The look.</b> Pixel art as the placeholder style, a 2 mm corner, and a matte rarity border with a thin black line inside it: common grey, uncommon green, rare purple, pinnacle gold with a hint of red. Meta cards keep a plain black border (not confirmed yet).</p>
<p><b>The backs</b> show the same place when its force is used: storms, fire, quakes, wind or fog, picked from the force's name. Five rares have no force yet, and their backs show a quiet night. Volcano and Tide Pool keep their hand-made art from the style canvas.</p>
<p>Data: data/cards-branch-b.json. Art: the pixel scene generator in the playtest repo.</p>
</div>
</div>
<script>{JS}</script>
</body>
</html>'''
open(sys.argv[1] if len(sys.argv) > 1 else 'framework-set.html', 'w').write(page)
print(len(page))
