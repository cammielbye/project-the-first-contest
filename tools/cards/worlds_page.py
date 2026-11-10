# "Three-Point Worlds": every 2x2 world of four fourth-pass permanences that scores 3+ world points (Nov 9, for Cam).
# Usage: node scripts/three-point-worlds.mjs worlds.json && python3 tools/cards/worlds_page.py worlds.json <out.html>
import html, json, re, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import lib

esc = html.escape
ROOT = __file__.rsplit('/', 3)[0]
worlds = json.load(open(sys.argv[1]))
cards = {c['permanence']['name']: c for c in json.load(open(ROOT + '/data/cards.json'))['cards'] if not c.get('meta')}
PIN = ['Origin', 'Ocean', 'Pangaea', 'Core', 'Trade Winds']
ORDER = ['water', 'earth', 'fire', 'air']

def aff_sort(a):
    return (9, a) if a == 'any' else (ORDER.index(a.split('|')[0]), a)

# one <symbol> per kind of ring, reused by every chip
kinds = sorted({a for f in worlds for n in f['cards'] for a in cards[n]['permanence']['affinities']}, key=aff_sort)
def symbol(a):
    svg = lib.ringed(a, 32)
    vb = re.search(r'viewBox="([^"]+)"', svg).group(1)
    inner = svg[svg.index('>') + 1:svg.rindex('</svg>')]
    return '<symbol id="r-%s" viewBox="%s"><g fill="none" stroke-width="1.9" stroke-linejoin="round" stroke-linecap="round">%s</g></symbol>' % (a.replace('|', '-'), vb, inner)
symbols = '<svg width="0" height="0" style="position:absolute" aria-hidden="true">%s</svg>' % ''.join(symbol(a) for a in kinds)

used = sorted({n for f in worlds for n in f['cards']}, key=lambda n: cards[n]['no'])
CARD = {n: {'no': cards[n]['no'], 'r': cards[n]['rarity'], 'a': sorted(cards[n]['permanence']['affinities'], key=aff_sort),
            't': cards[n]['permanence'].get('text') or ''} for n in used}
idx = {n: i for i, n in enumerate(used)}

def family(cs):
    pins = [c for c in cs if c in PIN]
    if pins: return 'pin'
    m, h = 'Mirage' in cs, 'Hanging Valley' in cs
    return 'mh' if m and h else 'm' if m else 'h' if h else 'r'
rows = []
for f in worlds:
    cs = f['cards']
    key = sorted(cs, key=lambda n: (0 if n in PIN else 1 if n == 'Mirage' else 2 if n == 'Hanging Valley' else 3, cards[n]['no']))
    diag = sorted({a[3 - a.index('Mirage')] for a in f['arrangements']}, key=lambda n: cards[n]['no']) if f['arrangements'] else []
    pins = [c for c in cs if c in PIN]
    sub = pins[0] if len(pins) == 1 else ('Two or more pinnacles' if pins else '')
    rows.append({'c': [idx[n] for n in key], 'k': f['k'], 'f': family(cs), 's': sub, 'd': [idx[n] for n in diag]})
rows.sort(key=lambda r: ([PIN.index(r['s']) if r['s'] in PIN else 9 if r['s'] else 0], [CARD[used[i]]['no'] for i in r['c']]))
n_all, n4 = len(rows), sum(1 for r in rows if r['k'] >= 4)
fam_n = {k: sum(1 for r in rows if r['f'] == k) for k in ('r', 'h', 'm', 'mh', 'pin')}

page = f'''<title>Three-Point Worlds</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:wght@500;600;700&family=IBM+Plex+Sans:ital,wght@0,400;0,500;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
  /* Layout: the card pool page's stone panel; one row per world, four card chips with their pips on a dark plate; filters on top. */
  :root {{
    --bg: #E9EBE4; --panel: #F7F8F3; --ink: #1D211D; --muted: #5D635B; --rule: #D3D7CC; --rule-strong: #B9BEB1;
    --plate: #2B2F2B; --bronze: #9A6E1F; --chip: #EEF0E8; --on: #1D211D; --on-ink: #F7F8F3;
    --display: "Barlow Semi Condensed", "Arial Narrow", "Helvetica Neue", Arial, sans-serif;
    --body: "IBM Plex Sans", "Helvetica Neue", Arial, sans-serif;
    --mono: "IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
  }}
  @media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
    --bg: #161916; --panel: #1E221E; --ink: #E7E4D9; --muted: #A3A89C; --rule: #2F342F; --rule-strong: #424842;
    --plate: #2B2F2B; --bronze: #D2A24A; --chip: #252925; --on: #E7E4D9; --on-ink: #161916; color-scheme: dark; }} }}
  :root[data-theme="dark"] {{
    --bg: #161916; --panel: #1E221E; --ink: #E7E4D9; --muted: #A3A89C; --rule: #2F342F; --rule-strong: #424842;
    --plate: #2B2F2B; --bronze: #D2A24A; --chip: #252925; --on: #E7E4D9; --on-ink: #161916; color-scheme: dark; }}
  body {{ background: var(--bg); color: var(--ink); font-family: var(--body); font-size: 15px; line-height: 1.45; }}
  .wrap {{ max-width: 76rem; margin: 0 auto; padding-block: 28px 40px; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); display: flex; flex-direction: column; gap: 16px; }}
  h1 {{ margin: 0; font-family: var(--display); font-weight: 700; font-size: clamp(1.9rem, 4vw, 2.6rem); line-height: 1.05; text-wrap: balance; }}
  .lede {{ margin: 0; color: var(--muted); max-width: 70ch; }}
  .lede b {{ color: var(--ink); font-weight: 500; font-variant-numeric: tabular-nums; }}
  .notes {{ margin: 0; padding-left: 1.1em; color: var(--muted); font-size: 13.5px; max-width: 80ch; display: flex; flex-direction: column; gap: 4px; }}
  .controls {{ display: flex; flex-wrap: wrap; gap: 10px 18px; align-items: center; }}
  .controls label {{ display: inline-flex; align-items: center; gap: 6px; font-size: 14px; }}
  #q {{ font: inherit; padding: 6px 10px; border: 1px solid var(--rule-strong); border-radius: 6px; background: var(--panel); color: var(--ink); width: 16rem; max-width: 100%; }}
  #q:focus-visible, input[type=checkbox]:focus-visible {{ outline: 2px solid var(--bronze); outline-offset: 2px; }}
  .shown {{ font-family: var(--mono); font-size: 12.5px; color: var(--muted); font-variant-numeric: tabular-nums; }}
  .pool {{ background: var(--panel); border: 1px solid var(--rule-strong); border-radius: 10px; }}
  section {{ padding: 14px 20px 8px; }}
  section + section {{ border-top: 2px solid var(--rule-strong); }}
  h2 {{ margin: 0 0 2px; display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 12px; font-family: var(--display); font-weight: 700; font-size: 1.35rem; letter-spacing: 0.02em; text-transform: uppercase; }}
  h2 .count, h3 .count {{ font-family: var(--mono); font-weight: 400; font-size: 12px; letter-spacing: 0.04em; color: var(--muted); text-transform: none; }}
  h3 {{ margin: 10px 0 2px; font-family: var(--display); font-weight: 600; font-size: 1.05rem; letter-spacing: 0.03em; color: var(--bronze); display: flex; gap: 10px; align-items: baseline; }}
  .why {{ margin: 0 0 6px; color: var(--muted); font-size: 13.5px; max-width: 75ch; }}
  ol {{ list-style: none; margin: 0; padding: 0; }}
  li.w {{ display: flex; flex-wrap: wrap; align-items: center; gap: 6px 8px; padding: 7px 0; border-top: 1px solid var(--rule); }}
  li.w:first-child {{ border-top-color: transparent; }}
  .pts {{ font-family: var(--mono); font-size: 11px; letter-spacing: 0.04em; padding: 2px 6px; border-radius: 4px; border: 1px solid var(--rule-strong); color: var(--muted); font-variant-numeric: tabular-nums; }}
  .pts.four {{ background: var(--on); color: var(--on-ink); border-color: var(--on); }}
  .c {{ display: inline-flex; align-items: center; gap: 6px; padding: 3px 4px 3px 8px; border-radius: 7px; background: var(--chip); min-width: 0; }}
  .c b {{ font-family: var(--display); font-weight: 600; font-size: 1.02rem; letter-spacing: 0.01em; white-space: nowrap; }}
  .c .rr {{ font-family: var(--mono); font-size: 10.5px; color: var(--muted); }}
  .pl {{ display: inline-flex; gap: 3px; padding: 3px 5px; border-radius: 6px; background: var(--plate); }}
  .pl svg {{ display: block; height: 18px; }}
  .pl .none {{ font-family: var(--mono); font-size: 10px; letter-spacing: 0.06em; color: #B9BCB0; text-transform: uppercase; padding: 2px 2px; line-height: 14px; }}
  .plus {{ color: var(--muted); font-size: 13px; }}
  .diag {{ font-size: 12.5px; color: var(--muted); }}
  .empty {{ color: var(--muted); font-size: 13.5px; padding: 6px 0 10px; }}
  @media (max-width: 760px) {{ section {{ padding: 12px 14px 6px; }} .plus {{ display: none; }} }}
  @media (prefers-reduced-motion: reduce) {{ * {{ scroll-behavior: auto; }} }}
</style>
{symbols}
<div class="wrap">
  <header style="display:flex;flex-direction:column;gap:8px">
    <h1>Three-Point Worlds</h1>
    <p class="lede">Every 2×2 world of four fourth-pass permanences that scores 3 or more world points, worked out by the playtest engine: <b>{n_all:,}</b> sets of four cards, <b>{n4}</b> of them worth 4. A 2×2 world holds four cards, so there are no five-card worlds under this cap.</p>
    <ul class="notes">
      <li>A world point is one complete set of water, earth, fire and air. Either-or and any pips fill whichever element is missing.</li>
      <li>Mirage copies the two cards beside it. The card across the diagonal isn't beside it, so where it sits matters; each Mirage row names the card or cards that can go diagonal to it.</li>
      <li>Hanging Valley adds a point to a world that already scores, and that point counts toward the 3. Ice Floe, Hill, Dune and Ledge count their +1 once the player has a world point.</li>
      <li>Points from Spring, Mountain Range, Fumarole and Sky Isle aren't world points, so they don't count here. Forces aren't included.</li>
    </ul>
  </header>
  <div class="controls">
    <label for="q">Card <input id="q" type="search" placeholder="Search a card, e.g. Lagoon" autocomplete="off"></label>
    <label for="nopin"><input id="nopin" type="checkbox"> Hide pinnacles</label>
    <label for="nomir"><input id="nomir" type="checkbox"> Hide Mirage</label>
    <label for="nohv"><input id="nohv" type="checkbox"> Hide Hanging Valley</label>
    <span class="shown" id="shown"></span>
  </div>
  <div class="pool">
    <section data-f="r"><h2>Four rares <span class="count" data-c="r"></span></h2><p class="why">Twelve pips, exactly three of each element. Every one is four three-pip rares.</p><ol id="l-r"></ol></section>
    <section data-f="h"><h2>Hanging Valley <span class="count" data-c="h"></span></h2><p class="why">Three cards that make two sets (eight pips, two of each element), plus Hanging Valley's point.</p><ol id="l-h"></ol></section>
    <section data-f="m"><h2>Mirage <span class="count" data-c="m"></span></h2><p class="why">Mirage copies the two cards beside it, so three cards can carry twelve pips.</p><ol id="l-m"></ol></section>
    <section data-f="mh"><h2>Mirage and Hanging Valley <span class="count" data-c="mh"></span></h2><p class="why">Two sets from Mirage and one other card's copied pips, plus Hanging Valley's point.</p><ol id="l-mh"></ol></section>
    <section data-f="pin"><h2>With a pinnacle <span class="count" data-c="pin"></span></h2><p class="why">Pinnacles carry four pips each. Origin alone is a full set.</p><div id="l-pin"></div></section>
  </div>
</div>
<script>
const NAMES = {json.dumps(used)};
const CARD = {json.dumps([CARD[n] for n in used])};
const ROWS = {json.dumps(rows, separators=(',', ':'))};
const PIN = {json.dumps(PIN)};
const esc = (s) => s.replace(/[&<>"]/g, (c) => ({{"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}})[c]);
const ring = (a) => {{ const w = a.includes("|") ? 34 : 18; return `<svg width="${{w}}" height="18" aria-hidden="true"><use href="#r-${{a.replace("|", "-")}}"></use></svg>`; }};
const word = (a) => a === "any" ? "any" : a.replace("|", " or ");
function chip(i) {{
  const c = CARD[i], n = NAMES[i];
  const pl = c.a.length ? c.a.map(ring).join("") : '<span class="none">none</span>';
  const label = c.a.length ? c.a.map(word).join(", ") : "no affinity";
  return `<span class="c" title="#${{c.no}} ${{esc(n)}}${{c.t ? ": " + esc(c.t) : ""}}"><b>${{esc(n)}}</b><span class="pl" role="img" aria-label="${{esc(label)}}">${{pl}}</span><span class="rr">${{c.r}}</span></span>`;
}}
function row(r) {{
  const d = r.d.length ? `<span class="diag">Diagonal to Mirage: ${{r.d.map((i) => esc(NAMES[i])).join(" or ")}}</span>` : "";
  return `<li class="w"><span class="pts${{r.k >= 4 ? " four" : ""}}">${{r.k}} pts</span>${{r.c.map(chip).join('<span class="plus">+</span>')}}${{d}}</li>`;
}}
const q = document.getElementById("q"), nopin = document.getElementById("nopin"), nomir = document.getElementById("nomir"), nohv = document.getElementById("nohv");
function render() {{
  const t = q.value.trim().toLowerCase();
  const keep = (r) => (!t || r.c.some((i) => NAMES[i].toLowerCase().includes(t))) && !(nomir.checked && r.c.some((i) => NAMES[i] === "Mirage")) && !(nohv.checked && r.c.some((i) => NAMES[i] === "Hanging Valley"));
  let shown = 0;
  for (const f of ["r", "h", "m", "mh", "pin"]) {{
    const rs = ROWS.filter((r) => r.f === f && keep(r));
    const sec = document.querySelector(`section[data-f="${{f}}"]`);
    sec.hidden = (f === "pin" && nopin.checked) || ((f === "m" || f === "mh") && nomir.checked) || ((f === "h" || f === "mh") && nohv.checked);
    if (sec.hidden) continue;
    shown += rs.length;
    document.querySelector(`[data-c="${{f}}"]`).textContent = rs.length.toLocaleString();
    const el = document.getElementById("l-" + f);
    if (f === "pin") {{
      const subs = [...PIN, "Two or more pinnacles"];
      el.innerHTML = subs.map((s) => {{ const g = rs.filter((r) => r.s === s); return g.length ? `<h3>${{esc(s)}} <span class="count">${{g.length.toLocaleString()}}</span></h3><ol>${{g.map(row).join("")}}</ol>` : ""; }}).join("") || '<p class="empty">No worlds match.</p>';
    }} else el.innerHTML = rs.length ? rs.map(row).join("") : '<li class="empty">No worlds match.</li>';
  }}
  document.getElementById("shown").textContent = `${{shown.toLocaleString()}} of ${{ROWS.length.toLocaleString()}} shown`;
}}
q.addEventListener("input", render); nopin.addEventListener("change", render); nomir.addEventListener("change", render); nohv.addEventListener("change", render);
render();
</script>
'''
open(sys.argv[2], 'w').write(page)
print(len(page), 'bytes;', n_all, 'worlds;', fam_n)
