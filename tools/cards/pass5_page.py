# The fifth-pass card pool as one page (the "Card Pool" artifact on claude.ai; the fourth pass's page before Nov 11).
# Usage: python3 pass5_page.py <out.html>
# The styles are the fourth-pass page's (read from pass4_page.py), plus tags for new and changed cards.
import collections, html, re, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import pass3, pass4, pass5, lib

esc = html.escape
ORDER = pass4.ORDER
RWORD = {'C': 'common', 'B': 'uncommon', 'A': 'rare', 'S': 'pinnacle'}
_src = open(__file__.rsplit('/', 1)[0] + '/pass4_page.py').read()
STYLE = _src[_src.index('<style>'):_src.index('</style>') + len('</style>')].replace('{{', '{').replace('}}', '}')
STYLE = STYLE.replace('</style>', '''  .tag-new { background: var(--draft); color: var(--draft-ink); }
  .tag-changed { background: transparent; border: 1px solid var(--rule-strong); color: var(--muted); }
  .format { background: var(--panel); border: 1px solid var(--rule-strong); border-radius: 10px; padding: 12px 16px; display: flex; flex-direction: column; gap: 6px; font-size: 14px; max-width: 75ch; }
  .format p { margin: 0; }
  .format b { font-weight: 500; }
</style>''')

def aff_sort(a):
    if a == 'any': return (9, a)
    return (ORDER.index(a.split('|')[0]), a)

def rings(affs, size=24):
    if not affs:
        return '<span class="plate plate-none" role="img" aria-label="No affinity">none</span>'
    marks = ''.join(lib.ringed(a, size) for a in sorted(affs, key=aff_sort))
    return '<span class="plate" role="img" aria-label="%s">%s</span>' % (esc(pass4.aff_cell(affs)), marks)

def rarity(r):
    if not r: return '<span class="rar rar-none" aria-label="No rarity">meta</span>'
    return '<span class="rar rar-%s" role="img" aria-label="%s"><i></i><b>%s</b></span>' % (r, RWORD[r], r)

def tags(c):
    out = []
    if c.get('how') == 'new': out.append('<span class="tag tag-new" title="New in the fifth pass: Claude\'s draft">new</span>')
    elif c['name'] in pass5.CHANGED: out.append('<span class="tag tag-changed" title="%s">changed</span>' % esc('; '.join(pass5.CHANGED[c['name']])))
    return ''.join(out)

def card_row(c):
    dur = 'lasts the round' if c['duration'] == pass3.R else 'once'
    text = esc(c['text']) if c['text'] else '<span class="vanilla">No text</span>'
    force = f'<em>{esc(c["force"])}</em> <span class="dur">{dur}</span> {esc(c["force_text"])}'
    return f'''<li class="card">
  <span class="no">{c['no']:02d}<small>/100</small></span>
  <span class="name"><b>{esc(c['name'])}</b>{tags(c)}</span>
  {rings(c['affinities'])}
  {rarity(c['rarity'])}
  <span class="text"><span class="perm">{text}</span><span class="force">{force}</span></span>
</li>'''

NEW_META = {n for _no, n, _t, _w in pass5.NEW_META}
def meta_row(name, text, no):
    tag = '<span class="tag tag-new" title="New in the fifth pass: Claude\'s draft">new</span>' if name in NEW_META else ''
    return f'''<li class="card card-meta">
  <span class="no">{no:02d}<small>/100</small></span>
  <span class="name"><b>{esc(name)}</b>{tag}</span>
  <span class="plate plate-none" role="img" aria-label="No affinity, meta card">meta</span>
  {rarity(None)}
  <span class="text"><span class="perm">{esc(text)}</span><span class="force">One face, usable by either player.</span></span>
</li>'''

def sub(title, note, rows, n):
    note_html = f'<span class="sub-note">{esc(note)}</span>' if note else ''
    return f'''<div class="sub">
  <h3><span>{esc(title)}</span><span class="count">{n}</span>{note_html}</h3>
  <ol class="cards">{''.join(rows)}</ol>
</div>'''

G = {k: (t, b, cs) for k, t, b, cs in pass5.GROUPS}
def g(key, label, note=''):
    t, b, cs = G[key]
    return sub(label, note, [card_row(c) for c in sorted(cs, key=lambda c: c['no'])], len(cs))

SECTIONS = [
 ('One pip', [g('c-still', "Common · can't be moved"), g('c-ignore', 'Common · unaffected by forces'),
              g('c-played', 'Common · when played'), g('c-either', 'Common · either-or, no text'), g('c-any', 'Common · any'),
              g('c-point', 'Common · +1 of its element with a world point', '8 words, one over the under-8 rule.'),
              g('a-blank', 'Rare · blanks the opposite element', "Ice Sheet's cycle.")]),
 ('Unique to one element', [g('u-pos', 'Common · positional', 'Idea 11 (Cam, Nov 11). In a 2×2 world each card has one card beside it, one above or below, and one across the diagonal; each element gets its own direction.'),
                            g('u-twist', "The element's effect, twisted", "Cam (Nov 11): lean into the effect and element relationship and double down, with a twist left unique to that element.")]),
 ('Two pips', [g('b-two', 'Uncommon · two different elements, no text'), g('b-two-text', 'Uncommon · two different elements, no text since Nov 10'),
               g('b-score', 'Uncommon · scoring', 'A point per four of its element.'),
               g('b-any', 'Uncommon · any'), g('b-same', 'Uncommon · two of one element')]),
 ('Three pips', [g('a-three', 'Rare · three different elements', 'Play only on a new world (fifth pass).'), g('a-two-one', 'Rare · two of one element, one of another'),
                 g('a-triple', 'Rare · three of one element', 'Play only on your first turn (fifth pass).')]),
 ('Four pips', [g('s', 'Pinnacle')]),
 ('No pips', [g('b-none', 'Uncommon'), g('b-none-open', 'Uncommon · one pip fewer', 'Its +1 world point did nothing once a world scores one point at most (Nov 10).'),
              sub('Meta cards · no rarity', 'One face, usable by either player. Six are new in the fifth pass.', [meta_row(m[0], m[1], pass5.META_NO[m[0]]) for m in sorted(pass5.META, key=lambda m: pass5.META_NO[m[0]])], len(pass5.META))]),
]

def section(title, subs):
    n = sum(s.count('<li class="card') for s in subs)
    sid = title.lower().replace(' ', '-')
    return f'''<section class="group" aria-labelledby="{sid}">
  <h2 id="{sid}"><span>{esc(title)}</span><span class="count">{n} cards</span></h2>
  {''.join(subs)}
</section>'''

rc = collections.Counter(c['rarity'] for c in pass5.ALL)
t = collections.Counter()
for c in pass5.ALL:
    for a in c['affinities']:
        if '|' in a:
            for x in a.split('|'): t[x + ' (either-or)'] += 1
        else: t[a] += 1
legend_marks = ''.join(f'<span class="key">{lib.ringed(e, 20)}{e}</span>' for e in ORDER)
legend_marks += f'<span class="key">{lib.ringed("water|fire", 20)}either-or</span><span class="key">{lib.ringed("any", 20)}any</span>'
legend_rar = ''.join(f'<span class="key">{rarity(r)}{RWORD[r]}</span>' for r in 'CBAS')
n_new = sum(1 for c in pass5.ALL if c.get('how') == 'new') + len(NEW_META)
n_changed = sum(1 for c in pass5.ALL if c['name'] in pass5.CHANGED and c.get('how') != 'new')

page = f'''<title>Fifth Pass Card Pool</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:wght@500;600;700&family=IBM+Plex+Sans:ital,wght@0,400;0,500;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
{STYLE}

<div class="wrap">
  <header>
    <h1>Fifth Pass Card Pool</h1>
    <p class="lede">The pool made playable again (Nov 11, 2026): <b>{len(pass5.ALL) + len(pass5.META)}</b> cards, no placeholders, and every permanence has a force. <b>{rc['C']}</b> commons, <b>{rc['B']}</b> uncommons, <b>{rc['A']}</b> rares, <b>{rc['S']}</b> pinnacles and <b>{len(pass5.META)}</b> meta cards; <b>{n_new}</b> new and <b>{n_changed}</b> changed, all Claude's drafts against Cam's brief. Pips across the pool: water <b>{t['water']}</b>, earth <b>{t['earth']}</b>, fire <b>{t['fire']}</b>, air <b>{t['air']}</b>, plus <b>{t['water (either-or)']}</b> either-or of each and <b>{t['any']}</b> any.</p>
    <div class="legend" aria-label="Key">{legend_marks}<span class="sep" aria-hidden="true"></span>{legend_rar}<span class="sep" aria-hidden="true"></span><span class="key"><span class="tag tag-new">new</span></span><span class="key"><span class="tag tag-changed">changed</span>hover for why</span></div>
  </header>

  <div class="format">
    <p><b>The format for test games (Cam, Nov 11).</b> Best of three rounds, no cap on cards a round. Before the contest, each player may reveal a permanence from their binder; whoever reveals the most pips goes second, and a tie is a coin flip. A world scores one world point at most, for one of each element or four of one element; worlds go up to 2×2.</p>
    <p>A ◯ in a force's text means a permanence with one pip.</p>
  </div>

  <main class="pool">
    {''.join(section(title, subs) for title, subs in SECTIONS)}
  </main>

  <div class="notes">
    <p><b>New</b>: a card or meta card new in the fifth pass. <b>Changed</b>: a fourth-pass card whose force or text changed; the reason is on the tag. Everything new or changed is Claude's draft, not adopted.</p>
    <p>Source: the fifth pass in design/card-pool.md. The fourth pass as it ended is saved in the playtest repo (data/versions/card-pool-2026-11-11-fourth-pass-final.md, branch saved/card-pool-2026-11-11-fourth-pass-final).</p>
  </div>
</div>
'''
open(sys.argv[1], 'w').write(page)
print(len(page), 'bytes')
