# The sixth-pass card pool as one page (the "Card Pool" artifact on claude.ai).
# Usage: python3 pass6_page.py <out.html>
# The styles are the fourth-pass page's (read from pass4_page.py), plus role tags, changed tags and the Nov 11 rarity marks.
import collections, html, re, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import pass3, pass4, pass5, pass6, lib

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
  /* rarity: a letter with no diamond, in shades of one violet that no element uses (Cam, Nov 11) */
  .rar { width: auto; min-width: 26px; height: 26px; }
  .rar i { display: none; }
  .rar b { font-size: 22px; line-height: 1; text-shadow: 1px 1px 0 rgba(0,0,0,.35); }
  :root { --rC: #8F86A6; --rB: #8466CC; --rA: #7240E0; --rS: #9A2BEB; }
  @media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --rC: #BDB6CF; --rB: #AC93E2; --rA: #9A6DF0; --rS: #B653FF; } }
  :root[data-theme="dark"] { --rC: #BDB6CF; --rB: #AC93E2; --rA: #9A6DF0; --rS: #B653FF; }
  .rar-C b, .rtext-C { color: var(--rC); } .rar-B b, .rtext-B { color: var(--rB); } .rar-A b, .rtext-A { color: var(--rA); } .rar-S b, .rtext-S { color: var(--rS); }
  .tag-role { background: transparent; border: 1px solid currentColor; }
  .role-removal { color: #B5502D; } .role-move { color: #3F7F95; } .role-negate { color: #7A6A3A; } .role-open { color: #8a8a8a; border-style: dashed; }
  .rtext { font-weight: 700; }
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

ROLE_LABEL = {pass6.REM: 'removal', pass6.MOV: 'moves theirs', pass6.NEG: 'stops forces', pass6.OPEN: 'open'}
def tags(c):
    out = []
    role = pass6.ROLE[c['name']]
    if role in ROLE_LABEL: out.append('<span class="tag tag-role role-%s" title="Reaches the other player">%s</span>' % (role, ROLE_LABEL[role]))
    if c['name'] in pass6.CHANGED: out.append('<span class="tag tag-changed" title="%s">changed</span>' % esc('; '.join(pass6.CHANGED[c['name']])))
    return ''.join(out)
RLET = {'common': 'C', 'uncommon': 'B', 'rare': 'A', 'pinnacle': 'S'}
def ftext(t):  # a rarity named in a rule is shown as its letter, as on the cards
    t = esc(t)
    t = re.sub(r'\ban (uncommon)(?= (permanence|force))', r'a \1', t)
    return re.sub(r'\b(common|uncommon|rare|pinnacle)(?= (permanences?|forces?)\b)', lambda m: '<span class="rtext rtext-%s" title="%s">%s</span>' % (RLET[m.group(1)], m.group(1), RLET[m.group(1)]), t)

def card_row(c):
    dur = pass6.dur_label(c).lower()
    text = ftext(c['text']) if c['text'] else '<span class="vanilla">No text</span>'
    force = f'<em>{esc(c["force"])}</em> <span class="dur">{dur}</span> {ftext(c["force_text"])}' if c['force'] else '<span class="vanilla">No force for the moment (its extra play went to the idea pool, Nov 12)</span>'
    return f'''<li class="card">
  <span class="no">{c['no']:02d}<small>/100</small></span>
  <span class="name"><b>{esc(c['name'])}</b>{tags(c)}</span>
  {rings(c['affinities'])}
  {rarity(c['rarity'])}
  <span class="text"><span class="perm">{text}</span><span class="force">{force}</span></span>
</li>'''

def meta_row(name, text, no):
    tag = ''
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

G = {k: (t, b, cs) for k, t, b, cs in pass6.GROUPS}
def g(key, label, note=''):
    t, b, cs = G[key]
    return sub(label, note, [card_row(c) for c in sorted(cs, key=lambda c: c['no'])], len(cs))

SECTIONS = [
 ('One pip', [g('c-still', "Common · can't be moved"), g('c-ignore', 'Common · unaffected by forces'),
              g('c-played', 'Common · when played'), g('c-either', 'Common · either-or, no text'), g('c-any', 'Common · any'),
              g('c-point', 'Common · +1 of its element with a world point', '8 words, one over the under-8 rule.'),
              g('a-blank', 'Rare · its whole world gains its element', "Ice Sheet's cycle; it blanked the opposite element until Nov 11.")]),
 ('Unique to one element', [g('u-pos', 'Common · positional', 'Idea 11 (Cam, Nov 11). In a 2×2 world each card has one card beside it, one above or below, and one across the diagonal; each element gets its own direction.'),
                            g('u-twist', "The element's effect, twisted", "Cam (Nov 11): lean into the effect and element relationship and double down, with a twist left unique to that element.")]),
 ('Two pips', [g('b-two', 'Uncommon · two different elements, no text'), g('b-two-text', 'Uncommon · two different elements, no text since Nov 10'),
               g('b-score', 'Uncommon · scoring', 'A point per four of its element.'),
               g('b-any', 'Uncommon · any'), g('b-same', 'Uncommon · two of one element')]),
 ('Three pips', [g('a-three', 'Rare · three different elements', 'Play only on a new world (fifth pass).'), g('a-two-one', 'Rare · two of one element, one of another'),
                 g('a-triple', 'Rare · three of one element', 'Play only on your first turn (fifth pass).')]),
 ('Four pips', [g('s', 'Pinnacle')]),
 ('No pips', [g('b-none', 'Uncommon'), g('b-none-open', 'Uncommon · +1 world point', 'Its +1 adds to the point its world\'s affinities score (Cam, Nov 11: the one world point per world is only from affinities). The four elements in its text are ringed; 8 words, with the four symbols counted as one, so one over the under-8 rule.'),
              sub('Meta cards · no rarity', 'One face, usable by either player. Unchanged in the sixth pass.', [meta_row(m[0], m[1], pass5.META_NO[m[0]]) for m in sorted(pass5.META, key=lambda m: pass5.META_NO[m[0]])], len(pass5.META))]),
]

def section(title, subs):
    n = sum(s.count('<li class="card') for s in subs)
    sid = title.lower().replace(' ', '-')
    return f'''<section class="group" aria-labelledby="{sid}">
  <h2 id="{sid}"><span>{esc(title)}</span><span class="count">{n} cards</span></h2>
  {''.join(subs)}
</section>'''

rc = collections.Counter(c['rarity'] for c in pass6.ALL)
t = collections.Counter()
for c in pass6.ALL:
    for a in c['affinities']:
        if '|' in a:
            for x in a.split('|'): t[x + ' (either-or)'] += 1
        else: t[a] += 1
legend_marks = ''.join(f'<span class="key">{lib.ringed(e, 20)}{e}</span>' for e in ORDER)
legend_marks += f'<span class="key">{lib.ringed("water|fire", 20)}either-or</span><span class="key">{lib.ringed("any", 20)}any</span>'
legend_rar = ''.join(f'<span class="key">{rarity(r)}{RWORD[r]}</span>' for r in 'CBAS')
roles = collections.Counter(pass6.ROLE.values())
n_changed = sum(1 for c in pass6.ALL if c['name'] in pass6.CHANGED)
n_lasting = sum(1 for c in pass6.ALL if c['duration'] in (pass6.R, pass6.UNTIL))

page = f'''<title>Sixth Pass Card Pool</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:wght@500;600;700&family=IBM+Plex+Sans:ital,wght@0,400;0,500;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
{STYLE}

<div class="wrap">
  <header>
    <h1>Sixth Pass Card Pool</h1>
    <p class="lede">Fewer answers, gated by rarity (Nov 11, 2026): <b>{len(pass6.ALL) + len(pass5.META)}</b> cards. Of the 86 force faces, <b>{roles[pass6.REM]}</b> are hard removal, <b>{roles[pass6.MOV]}</b> move or swap the other player's cards and <b>{roles[pass6.NEG]}</b> stop the other player's forces (Cam: about one in ten each); <b>{roles[pass6.SELF]}</b> help their owner, and <b>{roles[pass6.OPEN]}</b> are open since their extra plays went back to the idea pool (Nov 12). Protections now stop only the other player's cards. A force that reaches the other player reaches only permanences of its own rarity. No card loses its affinities any more, and <b>{n_lasting}</b> forces stay on the table. <b>{n_changed}</b> cards changed, all Claude's drafts against Cam's brief. <b>{rc['C']}</b> commons, <b>{rc['B']}</b> uncommons, <b>{rc['A']}</b> rares, <b>{rc['S']}</b> pinnacles and <b>{len(pass5.META)}</b> meta cards.</p>
    <div class="legend" aria-label="Key">{legend_marks}<span class="sep" aria-hidden="true"></span>{legend_rar}<span class="sep" aria-hidden="true"></span><span class="key"><span class="tag tag-role role-removal">removal</span></span><span class="key"><span class="tag tag-role role-move">moves theirs</span></span><span class="key"><span class="tag tag-role role-negate">stops forces</span></span><span class="key"><span class="tag tag-changed">changed</span>hover for why</span></div>
  </header>

  <div class="format">
    <p><b>The format for test games (Cam, Nov 11).</b> Best of three rounds, no cap on cards a round. Before the contest, each player may reveal a permanence from their binder; whoever reveals the most pips goes second, and a tie is a coin flip. A world's affinities score one world point at most, for one of each element or four of one element; card effects such as Hanging Valley's and the scoring cycle's add to it (Cam, Nov 11). Worlds go up to 2×2.</p>
    <p>A rarity letter in a force's text is the rarity it reaches: <span class="rtext rtext-C">C</span> common, <span class="rtext rtext-B">B</span> uncommon, <span class="rtext rtext-A">A</span> rare. Positional permanences give a pip in one direction each: water below, air above, earth beside, fire across. The pinnacles' forces act on whole worlds and aren't gated (Claude's reading).</p>
  </div>

  <main class="pool">
    {''.join(section(title, subs) for title, subs in SECTIONS)}
  </main>

  <div class="notes">
    <p><b>Removal</b>, <b>moves theirs</b> and <b>stops forces</b> mark the forces that reach the other player; every other force helps its owner. <b>Changed</b>: a fifth-pass card whose force or text changed, with what it was on hover. Everything changed is Claude's draft, not adopted.</p>
    <p>Source: the sixth pass in design/card-pool.md. The fifth pass as it ended is saved in the playtest repo (data/versions/card-pool-2026-11-11-fifth-pass-final.md, branch saved/card-pool-2026-11-11-fifth-pass-final).</p>
  </div>
</div>
'''
open(sys.argv[1], 'w').write(page)
print(len(page), 'bytes')
