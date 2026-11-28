# The Branch B card pool as one page, front and back (the "Branch B Card Pool" artifact on claude.ai).
# Usage: python3 branchb_page.py <out.html>
# The look is the sixth-pass list view's (pass6_page.py, which takes its styles from pass4_page.py), with a back column.
import collections, html, re, sys
HERE = __file__.rsplit('/', 1)[0]
sys.path.insert(0, HERE)
import lib, branchb_pool as B

esc = html.escape
ORDER = B.E
RWORD = {'C': 'common', 'B': 'uncommon', 'A': 'rare', 'S': 'pinnacle'}
_src4 = open(HERE + '/pass4_page.py').read()
STYLE = _src4[_src4.index('<style>'):_src4.index('</style>') + len('</style>')].replace('{{', '{').replace('}}', '}')
_src6 = open(HERE + '/pass6_page.py').read()
_a = _src6.index("STYLE = STYLE.replace('</style>', '''") + len("STYLE = STYLE.replace('</style>', '''")
STYLE = STYLE.replace('</style>', _src6[_a:_src6.index("''')", _a)])
STYLE = STYLE.replace('</style>', '''  /* front and back */
  .card { grid-template-columns: 3.4rem minmax(7.5rem, 10.5rem) 2.4rem minmax(8.5rem, 0.8fr) minmax(0, 1.6fr); align-items: start; }
  .card > .no, .card > .rar { padding-top: 5px; }
  .card > .name { padding-top: 3px; }
  .face { display: flex; flex-direction: column; gap: 5px; min-width: 0; }
  .face .ftxt { font-size: 13.5px; }
  .face > .plate, .back-head > .plate { align-self: flex-start; justify-self: start; }
  .back-head { display: flex; flex-wrap: wrap; align-items: center; gap: 4px 8px; }
  .back-head em { font-style: normal; font-weight: 600; font-family: var(--display); font-size: 1.02rem; letter-spacing: 0.01em; }
  .btxt { font-size: 14.5px; }
  .plate-sm { padding: 3px 6px; gap: 3px; }
  .plate-sm.plate-none { padding: 5px 8px; font-size: 10px; }
  .cols { display: grid; grid-template-columns: 3.4rem minmax(7.5rem, 10.5rem) 2.4rem minmax(8.5rem, 0.8fr) minmax(0, 1.6fr); gap: 4px 14px;
          font-family: var(--mono); font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted);
          position: sticky; top: 0; z-index: 2; background: var(--bg, Canvas); padding: 8px 20px 6px; border-bottom: 1px solid var(--rule-strong); }
  .cols span:nth-child(4) { grid-column: 4; } .cols span:nth-child(5) { grid-column: 5; }
  .tag-flip { background: transparent; border: 1px dashed currentColor; color: #4F7FA8; }
  .tag-block { background: transparent; border: 1px solid currentColor; color: #8A5A9E; }
  .tag-back { background: transparent; border: 1px solid currentColor; color: #5D8A4A; }
  .changes { grid-column: 2 / -1; display: none; margin: 2px 0 0; padding: 0 0 0 14px; font-size: 12.5px; color: var(--muted); }
  .changes li { margin: 1px 0; }
  .show-changes .changes { display: block; }
  .was { color: var(--muted); font-size: 12.5px; }
  .toggle { display: inline-flex; align-items: center; gap: 8px; font-size: 14px; cursor: pointer; user-select: none; }
  .toggle input { width: 16px; height: 16px; accent-color: #8466CC; }
  .ideas { list-style: none; margin: 0; padding: 0; display: grid; gap: 6px; }
  .ideas li { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 4px 14px; padding: 6px 0; border-top: 1px solid var(--rule); font-size: 14.5px; }
  .ideas li:first-child { border-top-color: transparent; }
  .ideas .who { color: var(--muted); font-size: 13px; text-align: right; }
  @media (max-width: 760px) {
    .cols { display: none; }
    .card { grid-template-columns: 3rem minmax(0, 1fr) auto; grid-template-areas: "no name rar" ". front front" ". back back" ". ch ch"; }
    .card > .face-front { grid-area: front; } .card > .face-back { grid-area: back; } .changes { grid-area: ch; }
    .face-front::before { content: "Front"; } .face-back::before { content: "Back"; }
    .face::before { font-family: var(--mono); font-size: 10px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); }
    .ideas li { grid-template-columns: 1fr; } .ideas .who { text-align: left; }
  }
</style>''')

def aff_sort(a):
    a0 = a.split('|')[0]
    return (ORDER.index(a0) if a0 in ORDER else 9, a)

def plate(affs, size=24, small=False):
    cls = 'plate plate-sm' if small else 'plate'
    if not affs:
        return '<span class="%s plate-none" role="img" aria-label="No pips">none</span>' % cls
    marks = ''.join(lib.ringed(a, size) for a in sorted(affs, key=aff_sort))
    return '<span class="%s" role="img" aria-label="%s">%s</span>' % (cls, esc(B.pips_md(affs)), marks)

def rarity(r):
    if not r: return '<span class="rar rar-none" aria-label="No rarity">meta</span>'
    return '<span class="rar rar-%s" role="img" aria-label="%s"><i></i><b>%s</b></span>' % (r, RWORD[r], r)

RLET = {'common': 'C', 'uncommon': 'B', 'rare': 'A', 'pinnacle': 'S'}
def ftext(t):  # a rarity named in a rule is shown as its letter, as on the cards
    t = esc(t)
    t = re.sub(r'\ban (uncommon)(?= (permanence|force))', r'a \1', t)
    return re.sub(r'\b(common|uncommon|rare|pinnacle)(?= (permanences?|forces?)\b)', lambda m: '<span class="rtext rtext-%s" title="%s">%s</span>' % (RLET[m.group(1)], m.group(1), RLET[m.group(1)]), t)

ROLE_LABEL = {'removal': 'removal', 'move': 'moves theirs', 'negate': 'stops forces'}
def tags(c):
    out = []
    if c.get('blocker'): out.append('<span class="tag tag-block" title="Can be played on an opponent\'s world">blocker</span>')
    if c.get('role') in ROLE_LABEL: out.append('<span class="tag tag-role role-%s" title="Reaches the other player">%s</span>' % (c['role'], ROLE_LABEL[c['role']]))
    if any(x.startswith('extra play back') for x in c['changes']): out.append('<span class="tag tag-back" title="Back from the idea pool">extra play</span>')
    if c.get('role') == 'open': out.append('<span class="tag tag-role role-open" title="No force for the moment">open</span>')
    return ''.join(out)

def changes(c):
    if not c['changes']: return ''
    return '<ul class="changes">%s</ul>' % ''.join('<li>%s</li>' % esc(x[0].upper() + x[1:]) for x in c['changes'])

def card_row(c):
    f, b = c['front'], c['back']
    if not b['text']:
        back_html = f'<span class="back-head">{plate(b["pips"], 20, True)}<span class="vanilla">Open: no force for the moment. Extra plays go on 1- and 2-pip cards (Cam, Nov 23).</span></span>'
    else:
        back_html = None
    ftxt = f'<span class="ftxt">{esc(f["text"])}</span>' if f['text'] else ''
    text = b['text'].replace(' Next turn, flip this back.', '')
    flip = ' Next turn, flip this back.' if b['flipsBack'] else ''
    chip_flip = '<span class="tag tag-flip" title="Flips back at the start of your next turn">flips back</span>' if b['flipsBack'] else ''
    return f'''<li class="card">
  <span class="no">{c['no']:02d}<small>/100</small></span>
  <span class="name"><b>{esc(c['name'])}</b>{tags(c)}</span>
  {rarity(c['rarity'])}
  <span class="face face-front">{plate(f['pips'])}{ftxt}</span>
  <span class="face face-back">{back_html or f'<span class="back-head">{plate(b["pips"], 20, True)}<em>{esc(b["name"])}</em><span class="dur">{esc(b["duration"].lower())}</span>{chip_flip}</span><span class="btxt">{ftext(text)}{esc(flip)}</span>'}</span>
  {changes(c)}
</li>'''

def meta_row(m):
    was = f'<span class="was">In the idea pool since Nov 28: {esc(m["was"])}</span>' if m['was'] else ''
    return f'''<li class="card card-meta">
  <span class="no">{m['no']:02d}<small>/100</small></span>
  <span class="name"><b>{esc(m['name'])}</b></span>
  {rarity(None)}
  <span class="face face-front"><span class="plate plate-none" role="img" aria-label="Meta card">meta</span></span>
  <span class="face face-back"><span class="vanilla">Blank: no ability yet.</span>{was}</span>
  {changes(m)}
</li>'''

def sub(title, note, rows):
    note_html = f'<span class="sub-note">{esc(note)}</span>' if note else ''
    return f'''<div class="sub">
  <h3><span>{esc(title)}</span><span class="count">{len(rows)}</span>{note_html}</h3>
  <ol class="cards">{''.join(rows)}</ol>
</div>'''

L = B.LAND
def pick(fn): return [card_row(c) for c in L if fn(c)]
def n(c): return len(c['front']['pips'])
def kinds(c): return set(c['front']['pips'])
one_el = lambda c: n(c) == 1 and c['rarity'] == 'C' and c['front']['pips'][0] in ORDER

SECTIONS = [
 ('One pip', [sub('Common · blockers', "Cam, Nov 23: a cycle of eight, two per element. Played on an opponent's world, a blocker stays its owner's: it counts toward that world, its owner can use its force, and it returns to its owner's binder.", pick(lambda c: c['blocker'])),
              sub('Common · one element', '', pick(lambda c: one_el(c) and not c['blocker'])),
              sub('Common · either-or', 'One pip that counts as either element.', pick(lambda c: n(c) == 1 and '|' in c['front']['pips'][0])),
              sub('Common · any', '', pick(lambda c: c['rarity'] == 'C' and c['front']['pips'] == ['any'])),
              sub('Rare · one pip', 'Cam, Nov 23: "I\'d like to have some 1 pip rares and just because I think it\'s interesting. we\'ll figure out what their effects have to be to qualify them as rares." Their backs are the sixth pass\'s for now; their old front text is in the idea pool.', pick(lambda c: n(c) == 1 and c['rarity'] == 'A'))]),
 ('Two pips', [sub('Uncommon · two elements', '', pick(lambda c: n(c) == 2 and len(kinds(c)) == 2 and 'any' not in kinds(c))),
               sub('Uncommon · with any', '', pick(lambda c: n(c) == 2 and 'any' in kinds(c))),
               sub('Uncommon · two of one element', '', pick(lambda c: n(c) == 2 and len(kinds(c)) == 1 and 'any' not in kinds(c)))]),
 ('Three pips', [sub('Rare · three elements', '', pick(lambda c: n(c) == 3 and len(kinds(c)) == 3)),
                 sub('Rare · two of one, one of another', '', pick(lambda c: n(c) == 3 and len(kinds(c)) == 2)),
                 sub('Rare · three of one element', '', pick(lambda c: n(c) == 3 and len(kinds(c)) == 1))]),
 ('Four pips', [sub('Pinnacle', '', pick(lambda c: n(c) == 4))]),
 ('No pips', [sub('Uncommon', 'Mirage and Hanging Valley were uncommon for their front text, which is in the idea pool now.', pick(lambda c: n(c) == 0)),
              sub('Meta cards · no rarity', "One face, shown in the back column. Played in place of the turn's landscape. Abilities blank since Nov 28 (Cam: \"blank the meta card abilities to be clear, leave the names and art and layout\"); what they said is in the idea pool.", [meta_row(m) for m in B.META])]),
]
assert sum(s.count('<li class="card') for _t, subs in SECTIONS for s in subs) == 100

def section(title, subs):
    k = sum(s.count('<li class="card') for s in subs)
    sid = title.lower().replace(' ', '-')
    return f'''<section class="group" aria-labelledby="{sid}">
  <h2 id="{sid}"><span>{esc(title)}</span><span class="count">{k} cards</span></h2>
  {''.join(subs)}
</section>'''

st = B.stats()
rc = collections.Counter(c['rarity'] for c in L)
roles = collections.Counter(c['role'] for c in L)
legend_marks = ''.join(f'<span class="key">{lib.ringed(e, 20)}{e}</span>' for e in ORDER)
legend_marks += f'<span class="key">{lib.ringed("water|fire", 20)}either-or</span><span class="key">{lib.ringed("any", 20)}any</span>'
legend_rar = ''.join(f'<span class="key">{rarity(r)}{RWORD[r]}</span>' for r in 'CBAS')
ideas = ''.join(f'<li><span>{esc(t)}</span><span class="who">{esc(", ".join(ns))}</span></li>' for t, ns in B.IDEA.items())
n_idea = sum(len(v) for v in B.IDEA.values())

page = f'''<title>Branch B Card Pool</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:wght@500;600;700&family=IBM+Plex+Sans:ital,wght@0,400;0,500;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
{STYLE}

<div class="wrap">
  <header>
    <h1>Branch B Card Pool</h1>
    <p class="lede">The last 100-card pool (the sixth pass) under Branch B's rules, first draft (Nov 23, 2026). Cam: "let's get the card pool back into a 100 card playable state like it once was." Fronts are vanilla: the <b>{n_idea}</b> front abilities are in the idea pool, listed at the bottom. The only front text left is the <b>8</b> blockers'. Every landscape's back has its own pips: <b>{st['loses every pip']}</b> lose every pip when flipped, <b>{st['loses some']}</b> lose some, <b>{st['keeps every pip']}</b> keep them all, and <b>{st['changes element']}</b> change element. <b>{st['flips back']}</b> flip back on their own. <b>{st['extra plays']}</b> give one extra play, all on 1- or 2-pip cards, and <b>{roles['open']}</b> rares are open. <b>{roles['removal']}</b> forces are hard removal, <b>{roles['move']}</b> move or swap the other player's cards and <b>{roles['negate']}</b> stop the other player's forces. <b>{rc['C']}</b> commons, <b>{rc['B']}</b> uncommons, <b>{rc['A']}</b> rares, <b>{rc['S']}</b> pinnacles and <b>{len(B.META)}</b> meta cards. Everything beyond Cam's three answers is Claude's draft.</p>
    <div class="legend" aria-label="Key">{legend_marks}<span class="sep" aria-hidden="true"></span>{legend_rar}<span class="sep" aria-hidden="true"></span><span class="key"><span class="tag tag-block">blocker</span></span><span class="key"><span class="tag tag-flip">flips back</span></span><span class="key"><span class="tag tag-back">extra play</span>back from the idea pool</span><span class="key"><span class="tag tag-role role-open">open</span>no force yet</span><span class="key"><span class="tag tag-role role-removal">removal</span></span><span class="key"><span class="tag tag-role role-move">moves theirs</span></span><span class="key"><span class="tag tag-role role-negate">stops forces</span></span></div>
  </header>

  <div class="format">
    <p><b>Branch B's rules.</b> A binder of 24, best of one. Nine whole turns each, then a shared 10th where both players lock in a landscape and a force and reveal together. Each turn, up to one landscape played and one force used. Using a force flips its card: its front pips stop counting and its back pips count. Worlds go up to 2×2. A world point is one of each element or four of one, uncapped per world, each pip counted once. A 2×2 world worth 3 points is a perfect world and wins at once; otherwise most world points after the 10th turn wins. Removed cards go to their owner's void; returned cards go to their owner's binder.</p>
    <p><b>What the rules changed on the cards.</b> "Lasts the round" is <b>while flipped</b>: the effect lives on the flipped card and ends if it's flipped back or leaves play. The forces on the table are flipped cards, so "remove a force" is "flip back". The extra plays are back: they left on Nov 12 because "with uncapped turns, playing extra cards in a row doesnt do anything" (Cam), and a Branch B turn has one landscape. Cam (Nov 23): "'play two more' is definitely too strong. 'Play one more' and moving it to a 1 or 2 pip card instead of a 3 pip card." So every extra play is one more, and the five 3-pip cards that had one are open. A rarity letter in a force's text is the rarity it reaches: <span class="rtext rtext-C">C</span> common, <span class="rtext rtext-B">B</span> uncommon, <span class="rtext rtext-A">A</span> rare.</p>
    <label class="toggle"><input type="checkbox" id="show-changes"> Show what changed on each card since the sixth pass</label>
  </div>

  <main class="pool" id="pool">
    <div class="cols" aria-hidden="true"><span>No.</span><span>Card</span><span></span><span>Front</span><span>Back</span></div>
    {''.join(section(title, subs) for title, subs in SECTIONS)}
    <section class="group" aria-labelledby="idea-pool">
      <h2 id="idea-pool"><span>Abilities now in the idea pool</span><span class="count">{n_idea + len(B.META_IDEA)} cards</span></h2>
      <div class="sub"><h3><span>Cam, Nov 23: "return the abilities to the idea pool so we don't forget about them"</span><span class="count">{len(B.IDEA)}</span></h3>
      <ol class="ideas">{ideas}</ol></div>
      <div class="sub"><h3><span>Meta card abilities, Nov 28: "lets just blank all the meta cards, move the current abilities to the idea pool"</span><span class="count">{len(B.META_IDEA)}</span></h3>
      <ol class="ideas">{''.join(f'<li><span>{esc(t)}</span><span class="who">{esc(n)}</span></li>' for n, t in B.META_IDEA)}</ol></div>
    </section>
  </main>

  <div class="notes">
    <p><b>Back pips</b> follow Cam's "the back side maybe has the same but almost always fewer or even no element affinities", losing an element where it feels thematic. Every one-pip card but Bedrock loses its pip. The elements that change: Mud Pots (water and fire make mud: earth), Obsidian (lava cools to glass: earth), Lava Coast (lava meets the sea and makes land).</p>
    <p><b>Flips back</b> marks the natural cycles: tides (Tide Pool, Tidal Flat, Spring's Low Tide), seasons (Snowfield), regrowth (Grove, Savanna), bubbling mud (Mud Pots) and a mirage that comes and goes. None of them removes, moves or stops the other player's cards, so none can lock a player out turn after turn.</p>
    <p>Source: the sixth pass in design/card-pool.md. Data: data/cards-branch-b.json in the playtest repo, made by tools/cards/branchb_pool.py. The sixth pass itself is unchanged.</p>
  </div>
</div>
<script>
  (function () {{
    var box = document.getElementById('show-changes'), pool = document.getElementById('pool');
    function set(on) {{ pool.classList.toggle('show-changes', on); box.checked = on; }}
    try {{ set(localStorage.getItem('bbpool:changes') === '1'); }} catch (e) {{}}
    box.addEventListener('change', function () {{ set(box.checked); try {{ localStorage.setItem('bbpool:changes', box.checked ? '1' : '0'); }} catch (e) {{}} }});
  }})();
</script>
'''
open(sys.argv[1], 'w').write(page)
