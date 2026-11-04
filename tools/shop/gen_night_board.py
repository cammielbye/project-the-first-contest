#!/usr/bin/env python3
"""Writes worldsketch-out/project/Night.dc.html: a night at Hollis Games, three collectors."""
import html, json, pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "worldsketch-out/project/Night.dc.html"
SCENE = "/_blob/fc3803f9c4bc2086a7ca4d0cc480f362"
FELL = "'IM Fell English', Georgia, serif"
MONO = "'IBM Plex Mono', monospace"

P = [
    dict(k="dunstan", name="Dunstan Rook", img="/_blob/b07869808b20b3b162107f3281e4bb00",
         tag="Sixties. A fisherman out of the Greywater Reach.",
         facts=[
             ("First played", "Fogbound three days off the Teeth, with a deckhand’s binder that had been in the bilge. “Cards never dried properly. Neither did I.”"),
             ("Favorite card", "Cloud Sea, Hurricane on its other face. Never owned one. “The storm that took the Margery took my brother with her. I came home on a hatch cover. Poor trade. I’ve been trying to improve on it ever since.”"),
             ("Wants", "The original Cloud Sea, or any copy drier than the ones he’s seen. Trades generously for anything with a storm in it."),
             ("Plays", "Water and air. Slow, passes early, and never chases a round he can’t see the end of."),
             ("Would trade", "Spare tide cards he’s picked up over forty years: two Shoals, a Lagoon, and a Tide Pool with a thumbprint on it that isn’t his."),
         ],
         lines=[
             ("Meeting you", "“You’ve a binder on you. Sit down, then. Tide’s not for hours.”"),
             ("Banter", "“I’ve been shipwrecked twice and married once. The marriage was worse.”"),
             ("You beat him", "“Fair. The sea’s beaten me worse, and I still go out.”"),
             ("He beats you", "“Don’t look so drowned. Nobody died. This time.”"),
             ("You hold Cloud Sea", "“You’ve got it. You’ve actually got it.” A long pause. “What would you take for it? Don’t answer quick.”"),
         ]),
    dict(k="milo", name="Milo Finch", img="/_blob/63f5ca8c6667d2535c1692c3a2681642",
         tag="Twelve. A paper round, a satchel, and opinions.",
         facts=[
             ("First played", "His big sister’s binder, while she was at work. “She said I’d ruin them. I’ve only ruined two.”"),
             ("Favorite card", "Smoking Hills, for Eruption on its other face. He’s never seen one, only heard Wendell describe it. “It’s the only card that’s loud.”"),
             ("Wants", "Anything with fire in it, and Eruption most of all. He’s saving his paper-round money and won’t say for what."),
             ("Plays", "All fire, all the time. Plays every card the turn he gets it and has never passed. Loses a lot, and enjoys it more than anyone at the table."),
             ("Would trade", "His sister’s doubles, which she may not know are gone. And what he’s seen in other people’s hands, for a Spark."),
         ],
         lines=[
             ("Meeting you", "“Are you any good? Dunstan’s good but he’s slow. You look fast.”"),
             ("Banter", "“Mum says I’ll grow out of it. Wendell’s about a hundred and he hasn’t.”"),
             ("You beat him", "“Again. Best of five. Best of however many it takes.”"),
             ("He beats you", "“I’m telling everyone. Not in a mean way. In a loud way.”"),
             ("You hold Smoking Hills", "“Is that real? Can I hold it? I’ll wash my hands. I’ll wash them twice.”"),
         ]),
    dict(k="vanessa", name="Vanessa Marlowe", img="/_blob/c2e7abe9bd0587ace1aaf932d271c1ed",
         tag="Late twenties. A grey coat, and a ledger she never closes.",
         facts=[
             ("First played", "Her gran’s kitchen in a blackout, by candle. “She cheated. I’ve never forgiven her, and I’ve never lost that way twice.”"),
             ("Favorite card", "Spring. She owns a copy, won off her gran that night. “The only thing she left me that wasn’t a debt.”"),
             ("Wants", "The original Spring, though she’d never be the first to say so."),
             ("Plays", "Even across the elements. Fast, plays her best card early, and dares you to answer it."),
             ("Would trade", "Almost anything in her binder for the right card. She’ll show you the page of her ledger where she wrote down what each one is worth to her, which is never what it’s worth to you."),
         ],
         lines=[
             ("Meeting you", "“Mind if I see your binder? I won’t take anything. I’ll just write it down.”"),
             ("Banter", "“I write down every card I see. It’s not obsessive if it’s organized.”"),
             ("You beat her", "“Write that down. Actually, don’t. I’ll remember.”"),
             ("She beats you", "“Chin up. I only take the good ones.”"),
             ("You hold the original Spring", "“Name a price. Not gold. Gold’s for people who don’t know what things are worth.”"),
         ]),
]

H = {
    "table": ("The table", "A little round table by the books, one candle, two small worlds each and a void pile between them. Dunstan has passed once already. Vanessa hasn’t passed all night.", ""),
    "dunstan": ("Dunstan Rook", "Holding a water card he’s kept all round. “Tide’s not for hours,” he says, to nobody.", ""),
    "milo": ("Milo Finch", "Standing, because Wendell says chairs are for players. He’s watched every card tonight. “I know what she’s holding. I’ll tell you for a Spark.”", ""),
    "vanessa": ("Vanessa Marlowe", "Fanning her cards like she’s already won, and writing down every card Dunstan plays.", ""),
    "cabinet": ("The cabinet", "Nothing in front of it tonight. Seventeen cards on their easels, lit from inside, and the one empty stand.", "flex"),
    "wendell": ("Wendell, keeping score", "Pipe going behind the counter, the smoke climbing straight into the lamp. “No betting at my table. Except on cards. Cards are fine. Cards are the point.”", ""),
}

# hotspot positions on the 1440x880 scene (circle top-left)
SPOTS = [("milo", "Milo Finch", 152, 498), ("vanessa", "Vanessa Marlowe", 322, 628),
         ("dunstan", "Dunstan Rook", 16, 838), ("table", "The table", 200, 838),
         ("cabinet", "The cabinet", 600, 520), ("wendell", "Wendell", 1046, 316)]


def e(s):
    return html.escape(s, quote=False)


def spot(k, label, x, y):
    return (f'<button aria-label="{e(label)}" onClick="{{{{ pick.{k} }}}}" onFocus="{{{{ pick.{k} }}}}" style="position: absolute; left: {x}px; top: {y}px; padding: 0; border: 0; background: none; cursor: pointer; display: flex; align-items: center; gap: 8px">\n'
            f'<span style="width: 40px; height: 40px; border-radius: 50%; border: 2px solid {{{{ ring.{k} }}}}; background: {{{{ fill.{k} }}}}; display: flex; align-items: center; justify-content: center"><span style="width: 10px; height: 10px; border-radius: 50%; background: #F1D9A0"></span></span>\n'
            f'<span style="padding: 4px 10px; border-radius: 4px; background: rgba(20,14,10,0.78); font-family: {FELL}; font-style: italic; font-size: 17px; color: #F1E3C6">{e(label)}</span>\n'
            f'</button>')


def label(t):
    return f'<span style="font-family: {MONO}; font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase; color: #B9A587">{e(t)}</span>'


def profile(p):
    facts = "".join(f'<div style="display: flex; flex-direction: column; gap: 3px">{label(a)}<span style="font-size: 18px; line-height: 1.3; color: #EDE2CB">{e(b)}</span></div>' for a, b in p["facts"])
    lines = "".join(f'<div style="display: flex; flex-direction: column; gap: 2px">{label(a)}<span style="font-family: {FELL}; font-style: italic; font-size: 18px; line-height: 1.3; color: #F6EAD0">{e(b)}</span></div>' for a, b in p["lines"])
    return (f'<section aria-label="{e(p["name"])}" style="width: 432px; box-sizing: border-box; padding: 22px 24px 26px; background: #201913; border: 1px solid #3A2E22; border-radius: 10px; box-shadow: 0 14px 30px rgba(0,0,0,0.5); display: flex; flex-direction: column; gap: 16px">\n'
            f'<div style="display: flex; gap: 16px; align-items: center">\n'
            f'<img src="{p["img"]}" alt="Portrait of {e(p["name"])}" style="width: 136px; height: 136px; flex: none; image-rendering: pixelated; border-radius: 6px; border: 2px solid #3A2E22">\n'
            f'<div style="display: flex; flex-direction: column; gap: 4px"><h3 style="margin: 0; font-family: {FELL}; font-weight: 400; font-size: 30px; color: #F6EAD0">{e(p["name"])}</h3><p style="margin: 0; font-size: 18px; line-height: 1.25; color: #CDB892; font-style: italic">{e(p["tag"])}</p></div>\n'
            f'</div>\n{facts}\n<div style="height: 1px; background: #3A2E22"></div>\n'
            f'<span style="font-family: {FELL}; font-size: 22px; color: #F6EAD0">What they say</span>\n{lines}\n</section>')


H_JS = ",\n".join(f"{k}: {{ name: {json.dumps(n, ensure_ascii=False)}, text: {json.dumps(t, ensure_ascii=False)}, link: {json.dumps(l or 'none')} }}" for k, (n, t, l) in H.items())

doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>A night at Hollis Games</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link href="https://fonts.googleapis.com/css2?family=IM+Fell+English:ital@0;1&amp;family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&amp;family=IBM+Plex+Mono:wght@400;500&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0}}
a{{color:#F1E3C6}}a:hover{{color:#FFFFFF}}
</style>
</helmet>
<div style="position: relative; width: 1440px; height: 2430px; background: #15110E; color: #F1E3C6; font-family: 'Cormorant Garamond', Georgia, serif; overflow: hidden">

<img src="{SCENE}" alt="Hollis Games at night: Dunstan Rook and Vanessa Marlowe play at a small candlelit table in front of the bookshelf while Milo Finch stands beside it watching; the card cabinet stands clear in the middle, and Wendell watches from behind the counter, his pipe smoke rising into the lamp" style="position: absolute; left: 0; top: 0; width: 1440px; height: 880px; image-rendering: pixelated">

<div style="position: absolute; left: 40px; top: 30px; display: flex; flex-direction: column; gap: 2px; max-width: 760px">
<h1 style="margin: 0; font-family: {FELL}; font-weight: 400; font-size: 42px; color: #F6EAD0; text-shadow: 0 2px 8px rgba(0,0,0,0.85)">Tuesday night at Hollis Games</h1>
<p style="margin: 0; font-family: {FELL}; font-style: italic; font-size: 19px; color: #E2D2B2; text-shadow: 0 2px 8px rgba(0,0,0,0.85)">Dunstan is playing Vanessa at the little table by the books. Milo is watching every card.</p>
</div>

<a href="Shop.dc.html" style="position: absolute; right: 40px; top: 40px; display: inline-flex; align-items: center; gap: 8px; padding: 10px 16px; border: 1.5px solid #C9B48A; border-radius: 6px; background: rgba(20,14,10,0.7); font-family: {FELL}; font-size: 18px; color: #F1E3C6; text-decoration: none"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#F1E3C6" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 5 L8 12 L15 19"></path></svg>The shop by day</a>

{chr(10).join(spot(*s) for s in SPOTS)}

<div style="position: absolute; left: 440px; top: 690px; width: 380px; box-sizing: border-box; padding: 16px 20px; background: #F1E8D2; border: 2px solid #3A2E22; box-shadow: 0 14px 30px rgba(0,0,0,0.6); color: #2C2219; display: flex; flex-direction: column; gap: 5px">
<h2 style="margin: 0; font-family: {FELL}; font-weight: 400; font-size: 25px">{{{{ cur.name }}}}</h2>
<p style="margin: 0; font-size: 18px; line-height: 1.3">{{{{ cur.text }}}}</p>
<a href="Shop.dc.html" style="display: {{{{ cur.link }}}}; align-items: center; gap: 6px; margin-top: 4px; font-family: {FELL}; font-style: italic; font-size: 18px; color: #6B3A1E">Take a closer look<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6B3A1E" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 5 L16 12 L9 19"></path></svg></a>
</div>

<div style="position: absolute; left: 48px; top: 920px; right: 48px; display: flex; align-items: baseline; justify-content: space-between; gap: 24px">
<h2 style="margin: 0; font-family: {FELL}; font-weight: 400; font-size: 34px; color: #F6EAD0">Three collectors</h2>
<p style="margin: 0; font-family: {FELL}; font-style: italic; font-size: 19px; color: #CDB892">Whoever happens to be in tonight. Each has a story, a want and something to trade.</p>
</div>

<div style="position: absolute; left: 48px; top: 990px; display: flex; gap: 24px; align-items: flex-start">
{"".join(profile(p) for p in P)}
</div>

</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":1440,"height":2430}}}}'>
class Component extends DCLogic {{
constructor(props) {{
super(props);
this.state = {{ sel: 'table' }};
}}
renderVals() {{
var H = {{
{H_JS}
}};
var self = this;
var s = this.state || {{}};
var sel = H[s.sel] ? s.sel : 'table';
var pick = {{}}, ring = {{}}, fill = {{}};
Object.keys(H).forEach(function (k) {{
pick[k] = function () {{ self.setState({{ sel: k }}); }};
ring[k] = sel === k ? '#E0B252' : 'rgba(241,227,198,0.85)';
fill[k] = sel === k ? 'rgba(224,178,82,0.45)' : 'rgba(20,14,10,0.45)';
}});
return {{ pick: pick, ring: ring, fill: fill, cur: H[sel] }};
}}
}}
</script>
</body>
</html>
'''
OUT.write_text(doc)
print(OUT, len(doc))
