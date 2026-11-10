# The fourth-pass card pool as one page (the "Fourth Pass Card Pool" artifact on claude.ai).
# Usage: python3 pass4_page.py <out.html>
import collections, html, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import pass3, pass4, lib

esc = html.escape
ORDER = pass4.ORDER
RWORD = {'C': 'common', 'B': 'uncommon', 'A': 'rare', 'S': 'pinnacle'}

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
    if c.get('how') == 'reused': out.append('<span class="tag" title="A cut third-pass card\'s name, art and force, given a new permanence">reused name</span>')
    if 'draft text' in c.get('note', ''): out.append('<span class="tag tag-draft" title="Claude\'s draft; earth had no when-played card">draft text</span>')
    return ''.join(out)

def card_row(c):
    dur = 'lasts the round' if c['duration'] == pass3.R else 'once'
    text = esc(c['text']) if c['text'] else '<span class="vanilla">No text</span>'
    force = (f'<em>{esc(c["force"])}</em> <span class="dur">{dur}</span> {esc(c["force_text"])}' if c['force']
             else '<span class="vanilla">No force for the moment</span>')
    return f'''<li class="card">
  <span class="no">{c['no']:02d}<small>/100</small></span>
  <span class="name"><b>{esc(c['name'])}</b>{tags(c)}</span>
  {rings(c['affinities'])}
  {rarity(c['rarity'])}
  <span class="text"><span class="perm">{text}</span><span class="force">{force}</span></span>
</li>'''

def meta_row(name, text, no):
    return f'''<li class="card card-meta">
  <span class="no">{no:02d}<small>/100</small></span>
  <span class="name"><b>{esc(name)}</b></span>
  <span class="plate plate-none" role="img" aria-label="No affinity, meta card">meta</span>
  {rarity(None)}
  <span class="text"><span class="perm">{esc(text)}</span><span class="force">One face, usable by either player.</span></span>
</li>'''

def meta_ph_row(no, k, was, ab):
    return f'''<li class="card card-meta card-ph">
  <span class="no">{no:02d}<small>/100</small></span>
  <span class="name"><b>Meta {k}</b><span class="tag tag-ph">placeholder</span></span>
  <span class="plate plate-none" role="img" aria-label="No affinity, meta card">meta</span>
  {rarity(None)}
  <span class="text"><span class="perm">Effect and name to come.</span><span class="force">Was {esc(was)} (either-or {ab[0]} or {ab[1]}, force {esc(pass3_force(was))}).</span></span>
</li>'''
def pass3_force(n): return pass4.P3[n][5]

def sub(title, note, rows, n):
    note_html = f'<span class="sub-note">{esc(note)}</span>' if note else ''
    return f'''<div class="sub">
  <h3><span>{esc(title)}</span><span class="count">{n}</span>{note_html}</h3>
  <ol class="cards">{''.join(rows)}</ol>
</div>'''

G = {k: (t, b, cs) for k, t, b, cs in pass4.GROUPS}
def g(key, label, note=None):
    t, b, cs = G[key]
    return sub(label, b if note is None else note, [card_row(c) for c in cs], len(cs))

SECTIONS = [
 ('One pip', [g('c-still', "Common · can't be moved"), g('c-ignore', 'Common · unaffected by forces', 'Cam (Nov 10): to make some single-pip cards strong enough to play late. Until Nov 10 they ignored the opposite element\'s forces.'),
               g('c-played', 'Common · when played'), g('c-either', 'Common · either-or, no text'), g('c-any', 'Common · any'),
               g('c-point', 'Common · +1 of its element with a world point', 'Cam (Nov 9): one of each element\'s placeholders. They sit in the slots for cards unique to one element, numbered with them; 8 words, one over the under-8 rule.'),
               g('a-blank', 'Rare · blanks the opposite element', 'Ice Sheet\'s cycle.')]),
 ('Two pips', [g('b-two', 'Uncommon · two different elements, no text'), g('b-two-text', 'Uncommon · two different elements, no text since Nov 10', 'Cam (Nov 10): their texts moved to the idea pool; the scoring cycle keeps its text.'),
                g('b-score', 'Uncommon · scoring', 'A point per four of its element. Sky Isle is also the any cycle\'s air card.'),
                g('b-any', 'Uncommon · any', 'One element and any; Hidden Valley has two any.'), g('b-same', 'Uncommon · two of one element')]),
 ('Three pips', [g('a-three', 'Rare · three different elements'), g('a-two-one', 'Rare · two of one element, one of another'), g('a-triple', 'Rare · three of one element')]),
 ('Four pips', [g('s', 'Pinnacle')]),
 ('No pips', [g('b-none', 'Uncommon', 'No pip of its own; kept at uncommon.'),
               g('b-none-open', 'Uncommon · +1 world point', 'Cam (Nov 9): in the last open slot. The four elements in its text are ringed. Claude gave it the one free name and kept it at uncommon like Mirage; 8 words, with the four symbols counted as one (Cam, Nov 9), so one over the under-8 rule.'),
               sub('Meta cards · no rarity', 'Equinox was Cradle\'s force face.', [meta_row(m[0], m[1], pass4.META_NO[m[0]]) for m in pass4.META], len(pass4.META)),
               sub('Meta cards · placeholders', 'Cam (Nov 9): one of each either-or pair becomes a meta card, since one-sided cards are fewer to balance and design. Claude took the second of each pair; their names and force faces are free again.', [meta_ph_row(no, k + 1, n, ab) for k, (no, n, ab) in enumerate(pass4.META_PH)], len(pass4.META_PH))]),
]

def section(title, subs):
    n = sum(s.count('<li class="card') for s in subs)
    sid = title.lower().replace(' ', '-')
    return f'''<section class="group" aria-labelledby="{sid}">
  <h2 id="{sid}"><span>{esc(title)}</span><span class="count">{n} cards</span></h2>
  {''.join(subs)}
</section>'''

rc = collections.Counter(c['rarity'] for c in pass4.ALL)
t = pass4.tally()
legend_marks = ''.join(f'<span class="key">{lib.ringed(e, 20)}{e}</span>' for e in ORDER)
legend_marks += f'<span class="key">{lib.ringed("water|fire", 20)}either-or</span><span class="key">{lib.ringed("any", 20)}any</span>'
legend_rar = ''.join(f'<span class="key">{rarity(r)}{RWORD[r]}</span>' for r in 'CBAS')
open_slots = ''.join(f'<li>{n}</li>' for n in pass4.OPEN)
def ph_row(no, e, k, nm):
    note = pass4.UNIQUE_NOTE if nm else pass4.UNNAMED_NOTE
    return f'''<li class="card card-ph">
  <span class="no">{no:02d}<small>/100</small></span>
  <span class="name"><b>{esc(nm or f'Unique {e} {k}')}</b><span class="tag tag-ph">placeholder</span>{'<span class="tag" title="The name of a cut third-pass card">reused name</span>' if nm else ''}</span>
  <span class="plate" role="img" aria-label="At least one {e} ring">{lib.ringed(e, 24)}<span class="more">+?</span></span>
  <span class="rar rar-none" aria-label="Rarity to come">tbd</span>
  <span class="text"><span class="perm">{esc(note)}</span></span>
</li>'''
_ph = {e: [ph_row(no, ee, pass4.PH_NAMES[ee].index(nm) + 1, nm) for no, ee, nm in pass4.PLACEHOLDERS if ee == e] for e in ORDER}
ph_subs = ''.join(sub(f'{e.capitalize()}', '', _ph[e], len(_ph[e])) for e in ORDER)

OPEN_SECTION = (f'''<section class="group open" aria-labelledby="open-slots">
      <h2 id="open-slots"><span>{'Open slot' if len(pass4.OPEN) == 1 else 'Open slots'}</span><span class="count">{len(pass4.OPEN)}</span></h2>
      <ol>{open_slots}</ol>
      <p>For more multi-affinity cards (Cam, Nov 8). Name still free from a cut card: {esc(', '.join(pass4.FREE_NAMES))}.</p>
    </section>''') if pass4.OPEN else ''

page = f'''<title>Fourth Pass Card Pool</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:wght@500;600;700&family=IBM+Plex+Sans:ital,wght@0,400;0,500;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
  /* Layout: one stone panel holding the whole pool, grouped by pip count, each card one row: number, name, pips in rings on a dark plate as on the faces, rarity diamond, text. */
  :root {{
    --bg: #E9EBE4; --panel: #F7F8F3; --ink: #1D211D; --muted: #5D635B; --rule: #D3D7CC; --rule-strong: #B9BEB1;
    --plate: #2B2F2B; --plate-edge: #0D0F0D; --bronze: #9A6E1F; --tag: #E5E2D2; --tag-ink: #4C4A3C; --draft: #F3E0C4; --draft-ink: #6B4512;
    --display: "Barlow Semi Condensed", "Arial Narrow", "Helvetica Neue", Arial, sans-serif;
    --body: "IBM Plex Sans", "Helvetica Neue", Arial, sans-serif;
    --mono: "IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
  }}
  @media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
    --bg: #161916; --panel: #1E221E; --ink: #E7E4D9; --muted: #A3A89C; --rule: #2F342F; --rule-strong: #424842;
    --plate: #2B2F2B; --plate-edge: #0D0F0D; --bronze: #D2A24A; --tag: #2E3229; --tag-ink: #C9C6B5; --draft: #3D3020; --draft-ink: #E8C38D; color-scheme: dark; }} }}
  :root[data-theme="dark"] {{
    --bg: #161916; --panel: #1E221E; --ink: #E7E4D9; --muted: #A3A89C; --rule: #2F342F; --rule-strong: #424842;
    --plate: #2B2F2B; --plate-edge: #0D0F0D; --bronze: #D2A24A; --tag: #2E3229; --tag-ink: #C9C6B5; --draft: #3D3020; --draft-ink: #E8C38D; color-scheme: dark; }}
  body {{ background: var(--bg); color: var(--ink); font-family: var(--body); font-size: 15px; line-height: 1.45; }}
  .wrap {{ max-width: 72rem; margin: 0 auto; padding-block: 28px 40px; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); display: flex; flex-direction: column; gap: 18px; }}
  header {{ display: flex; flex-direction: column; gap: 8px; }}
  h1 {{ margin: 0; font-family: var(--display); font-weight: 700; font-size: clamp(1.9rem, 4vw, 2.6rem); letter-spacing: 0.01em; line-height: 1.05; text-wrap: balance; }}
  .lede {{ margin: 0; color: var(--muted); max-width: 62ch; }}
  .lede b {{ color: var(--ink); font-weight: 500; font-variant-numeric: tabular-nums; }}
  .legend {{ display: flex; flex-wrap: wrap; gap: 6px 16px; font-size: 13px; color: var(--muted); align-items: center; }}
  .legend .key {{ display: inline-flex; align-items: center; gap: 6px; }}
  .legend .key svg {{ background: var(--plate); border-radius: 50%; }}
  .legend .key svg[viewBox="0 0 60 32"] {{ border-radius: 10px; }}
  .legend .sep {{ width: 1px; height: 18px; background: var(--rule-strong); }}
  .pool {{ background: var(--panel); border: 1px solid var(--rule-strong); border-radius: 10px; padding: 6px 0 4px; }}
  .group {{ padding: 14px 20px 6px; }}
  .group + .group {{ border-top: 2px solid var(--rule-strong); }}
  h2 {{ margin: 0 0 4px; display: flex; align-items: baseline; gap: 12px; font-family: var(--display); font-weight: 700; font-size: 1.45rem; letter-spacing: 0.02em; text-transform: uppercase; }}
  h2 .count, h3 .count {{ font-family: var(--mono); font-weight: 400; font-size: 12px; letter-spacing: 0.04em; color: var(--muted); text-transform: none; }}
  .sub {{ padding: 10px 0 6px; }}
  h3 {{ margin: 0 0 4px; display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 10px; font-family: var(--display); font-weight: 600; font-size: 1.05rem; letter-spacing: 0.03em; color: var(--bronze); }}
  .sub-note {{ font-family: var(--body); font-weight: 400; font-size: 13px; letter-spacing: 0; color: var(--muted); }}
  ol.cards {{ list-style: none; margin: 0; padding: 0; }}
  .card {{ display: grid; grid-template-columns: 3.6rem minmax(8rem, 11rem) 9.5rem 2.6rem minmax(0, 1fr); gap: 4px 14px; align-items: center; padding: 7px 0; border-top: 1px solid var(--rule); }}
  .card:first-child {{ border-top-color: transparent; }}
  .no {{ font-family: var(--mono); font-size: 13px; font-variant-numeric: tabular-nums; color: var(--muted); }}
  .no small {{ font-size: 10px; opacity: 0.7; }}
  .name {{ display: flex; flex-wrap: wrap; align-items: center; gap: 4px 8px; min-width: 0; }}
  .name b {{ font-family: var(--display); font-weight: 600; font-size: 1.12rem; letter-spacing: 0.01em; }}
  .tag {{ font-size: 11px; line-height: 1; padding: 3px 6px; border-radius: 4px; background: var(--tag); color: var(--tag-ink); white-space: nowrap; }}
  .tag-draft {{ background: var(--draft); color: var(--draft-ink); }}
  .plate {{ justify-self: start; display: inline-flex; align-items: center; gap: 4px; padding: 4px 7px; border-radius: 7px; background: var(--plate); box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), inset 0 -2px 4px rgba(0,0,0,0.4); }}
  .plate svg {{ display: block; }}
  .plate-none {{ font-family: var(--mono); font-size: 11px; letter-spacing: 0.06em; color: #B9BCB0; padding: 7px 9px; text-transform: uppercase; }}
  .rar {{ position: relative; width: 26px; height: 26px; display: inline-flex; align-items: center; justify-content: center; }}
  .rar i {{ position: absolute; inset: 5px; transform: rotate(45deg); border: 1.5px solid var(--muted); border-radius: 2px; }}
  .rar b {{ position: relative; font-family: var(--display); font-weight: 700; font-size: 13px; color: var(--ink); }}
  .rar-S i {{ border-color: var(--bronze); }} .rar-S b {{ color: var(--bronze); }}
  .rar-none {{ font-family: var(--mono); font-size: 10px; letter-spacing: 0.06em; color: var(--muted); text-transform: uppercase; width: auto; }}
  .text {{ display: flex; flex-direction: column; gap: 2px; min-width: 0; }}
  .perm {{ font-size: 14.5px; }}
  .vanilla {{ color: var(--muted); font-style: italic; }}
  .force {{ font-size: 12.5px; color: var(--muted); }}
  .force em {{ font-style: normal; font-weight: 500; color: var(--ink); }}
  .dur {{ font-family: var(--mono); font-size: 10.5px; letter-spacing: 0.04em; text-transform: uppercase; padding: 1px 5px; border: 1px solid var(--rule-strong); border-radius: 3px; margin: 0 3px; white-space: nowrap; }}
  .group-note {{ margin: 0 0 2px; color: var(--muted); font-size: 13.5px; max-width: 70ch; }}
  .tag-ph {{ background: transparent; border: 1px dashed var(--rule-strong); color: var(--muted); }}
  .card-ph .name b {{ color: var(--muted); }}
  .card-ph .plate {{ opacity: 0.9; }}
  .plate .more {{ font-family: var(--mono); font-size: 12px; color: #B9BCB0; padding: 0 2px 0 3px; }}
  .open {{ display: flex; flex-direction: column; gap: 8px; padding-bottom: 12px; }}
  .open ol {{ list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: 6px; }}
  .open li {{ font-family: var(--mono); font-size: 13px; font-variant-numeric: tabular-nums; color: var(--muted); border: 1.5px dashed var(--rule-strong); border-radius: 6px; padding: 6px 10px; }}
  .open p {{ margin: 0; color: var(--muted); font-size: 13px; max-width: 70ch; }}
  .notes {{ margin: 0; color: var(--muted); font-size: 13px; max-width: 75ch; display: flex; flex-direction: column; gap: 6px; }}
  .notes p {{ margin: 0; }}
  @media (max-width: 760px) {{
    .group {{ padding: 12px 14px 4px; }}
    .card {{ grid-template-columns: 3rem minmax(0, 1fr) auto; grid-template-areas: "no name rar" ". plate plate" ". text text"; gap: 6px 10px; align-items: start; }}
    .no {{ grid-area: no; padding-top: 3px; }} .name {{ grid-area: name; }} .plate {{ grid-area: plate; }} .rar {{ grid-area: rar; }} .text {{ grid-area: text; }}
  }}
</style>

<div class="wrap">
  <header>
    <h1>Fourth Pass Card Pool</h1>
    <p class="lede">The third pass restructured by pip count (Nov 8, 2026): <b>{len(pass4.ALL) + len(pass4.META)}</b> cards, <b>{len(pass4.META_PH) + len(pass4.PLACEHOLDERS)}</b> placeholders ({len(pass4.META_PH)} meta, {len(pass4.PLACEHOLDERS)} unique to one element) and {('<b>%d</b> open %s' % (len(pass4.OPEN), 'slot' if len(pass4.OPEN) == 1 else 'slots')) if pass4.OPEN else 'no open slots'}. <b>{rc['C']}</b> commons, <b>{rc['B']}</b> uncommons, <b>{rc['A']}</b> rares, <b>{rc['S']}</b> pinnacles and <b>{len(pass4.META)}</b> meta cards. Rings across the pool: water <b>{t['water']}</b>, earth <b>{t['earth']}</b>, fire <b>{t['fire']}</b>, air <b>{t['air']}</b>, plus <b>{t['water (either-or)']}</b> either-or of each and <b>{t['any']}</b> any.</p>
    <div class="legend" aria-label="Key">{legend_marks}<span class="sep" aria-hidden="true"></span>{legend_rar}</div>
  </header>

  <main class="pool">
    {''.join(section(title, subs) for title, subs in SECTIONS)}
    <section class="group" aria-labelledby="placeholders">
      <h2 id="placeholders"><span>Placeholders</span><span class="count">{len(pass4.PLACEHOLDERS)} slots</span></h2>
      <p class="group-note">Cam (Nov 8): some cards shouldn't be part of a cycle. Ironically, a cycle of at least 3 cards in each element whose effects have no equivalent in other elements.</p>
      {ph_subs}
    </section>
    {OPEN_SECTION}
  </main>

  <div class="notes">
    <p><b>Reused name</b>: a cut third-pass card's name, art and force face, given a new permanence; Claude matched names to cards by landform. <b>Draft text</b>: Claude's draft. Forces are carried over from the third pass, so they aren't tuned to the new rarities yet; Cam has changed some since (listed in the card pool), and the cards marked "No force for the moment" lost theirs to other cards.</p>
    <p>Source: the fourth pass in design/card-pool.md. The third pass before this is saved in the playtest repo (data/versions/, branch saved/card-pool-2026-11-08-third-pass), and the playtest table still plays it until binders are rebuilt.</p>
  </div>
</div>
'''
open(sys.argv[1], 'w').write(page)
print(len(page), 'bytes')
