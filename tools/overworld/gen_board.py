#!/usr/bin/env python3
"""Writes worldsketch-out/project/Overworld.dc.html: six overworld options and the choices behind them."""
import html, pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "worldsketch-out/project/Overworld.dc.html"
FELL = "'IM Fell English', Georgia, serif"
SC = "'IM Fell English SC', Georgia, serif"
BODY = "'Cormorant Garamond', Georgia, serif"
H_BOARD = 2380

CHOICES = [
    ("Landmass", ["One continent", "Two or three continents", "Many islands"]),
    ("Water", ["Ocean and coastlines", "One inland sea", "Rivers and lakes"]),
    ("Regions", ["Provinces inside one landmass", "A landmass for each region", "A blend of both"]),
    ("Scale", ["Compact: 4 regions, about 30 places", "Large: 8 regions, 70–90 places (your lean)", "Huge: 12 or more regions"]),
]

OPTIONS = [
    ("/_blob/7115e3d7bc26cc80ca0f4fc232787339", "One great continent",
     "One landmass with ragged coasts, an inland lake and long rivers.",
     [("Water", "Ocean all the way round, a lake in the middle, rivers out to the coast."),
      ("Travel", "Roads, with rivers and mountain ranges as the borders between regions."),
      ("Regions", "About 8 provinces and 80 places."),
      ("For the hunt", "The far side really is far, and mountain passes keep the harder regions for later."),
      ("Watch for", "The middle can blur together unless every province has a look of its own.")]),
    ("/_blob/5391d54fa76c5292ff2746dd612e1d2b", "Two continents and a strait",
     "Two landmasses facing each other across a sea, with an island between.",
     [("Water", "A strait down the middle and open ocean beyond."),
      ("Travel", "Overland on each side. Crossing takes a ship, and the captain only sails for someone who’s beaten them."),
      ("Regions", "3 or 4 on each continent, about 70 places. The island in the strait could host the great tournament."),
      ("For the hunt", "The crossing is a milestone: a second half of the game with new shops and collectors."),
      ("Watch for", "The second continent can feel like a sequel. Both sides need reasons to go back and forth.")]),
    ("/_blob/eb6010e4a3714474f6cc1d79ee045660", "An archipelago",
     "Dozens of islands, where the sea is the road.",
     [("Water", "Open sea everywhere, with long coastlines, coves and straits."),
      ("Travel", "By boat from harbor to harbor; some islands are reached only by certain routes."),
      ("Regions", "Island groups, about 60 places, many of them small."),
      ("For the hunt", "Every island is a closed box to open, and hidden coves suit hidden gems."),
      ("Watch for", "Sailing can turn into filler, and the land is thin for big mountain and volcano places.")]),
    ("/_blob/995e27a1047c10842b610a7e564d3274", "An inland sea",
     "Land wrapped around one great sea, like the Mediterranean.",
     [("Water", "A central sea, a strait out to the ocean, and rivers running down to the shore."),
      ("Travel", "Roads around the shore, or boats straight across."),
      ("Regions", "About 6 around the shore, 75 places. The island in the middle holds the water seat."),
      ("For the hunt", "Every region faces the same sea, so the world stays easy to read, and crossing it is the shortcut."),
      ("Watch for", "It can feel smaller than it is, since everything looks toward the middle.")]),
    ("/_blob/bbb5f1fae24047843ab518e9637579cd", "River country",
     "Hills and lakes inland, and one great river down to the sea.",
     [("Water", "A long river with tributaries, many lakes, and one coast at the delta."),
      ("Travel", "Up and down the river by boat, and roads along the tributaries."),
      ("Regions", "Strung along the river and its branches, about 80 places."),
      ("For the hunt", "Going upriver gets harder, a natural difficulty curve, and each tributary is a side path to take in any order."),
      ("Watch for", "The main river pulls you down one line, so the tributaries have to matter.")]),
    ("/_blob/e470dfe9571891dd96f3a16d7c81592d", "A spine between two coasts",
     "A long continent split by one mountain range.",
     [("Water", "A wet coast on one side, a drier coast on the other, and rivers running off the range."),
      ("Travel", "Along either side, crossing only at the passes."),
      ("Regions", "About 6 on each side of the range, 75 places."),
      ("For the hunt", "The elements sit on the land: water on the wet coast, fire on the dry side, earth and air up in the range."),
      ("Watch for", "Two halves can feel like only two choices.")]),
]

SEAT_SVG = {
    "fire": '<svg width="22" height="22" viewBox="0 0 22 22" aria-hidden="true"><circle cx="11" cy="11" r="10" fill="#F1E8D2" stroke="#3A2E22" stroke-width="1.5"></circle><path d="M11 4 L17 15.5 L5 15.5 Z" fill="#B04A2E"></path></svg>',
    "water": '<svg width="22" height="22" viewBox="0 0 22 22" aria-hidden="true"><circle cx="11" cy="11" r="10" fill="#F1E8D2" stroke="#3A2E22" stroke-width="1.5"></circle><circle cx="11" cy="11" r="6" fill="#34688C"></circle></svg>',
    "earth": '<svg width="22" height="22" viewBox="0 0 22 22" aria-hidden="true"><circle cx="11" cy="11" r="10" fill="#F1E8D2" stroke="#3A2E22" stroke-width="1.5"></circle><rect x="6" y="6" width="10" height="10" fill="#5C7034"></rect></svg>',
    "air": '<svg width="22" height="22" viewBox="0 0 22 22" aria-hidden="true"><circle cx="11" cy="11" r="10" fill="#F1E8D2" stroke="#3A2E22" stroke-width="1.5"></circle><path d="M11 4 L18 11 L11 18 L4 11 Z" fill="#807696"></path></svg>',
}


def e(s):
    return html.escape(s, quote=False)


def choice(label, vals):
    items = "".join(f'<li style="font-size: 18px; line-height: 1.35; color: #EDE3CC">{e(v)}</li>' for v in vals)
    return (f'<div style="flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 6px; padding: 16px 18px; border: 1px solid #4A3C2D; border-radius: 6px; background: #30281F">'
            f'<span style="font-family: {SC}; font-size: 16px; letter-spacing: 0.06em; color: #C9BCA2">{e(label)}</span>'
            f'<ul style="margin: 0; padding-left: 18px; display: flex; flex-direction: column; gap: 2px">{items}</ul></div>')


def option(img, name, pitch, rows):
    rr = "".join(f'<div style="display: flex; flex-direction: column; gap: 1px"><span style="font-family: {SC}; font-size: 15px; letter-spacing: 0.06em; color: #7A5E3E">{e(a)}</span>'
                 f'<span style="font-size: 18px; line-height: 1.3; color: #2C2219">{e(b)}</span></div>' for a, b in rows)
    return (f'<section aria-label="{e(name)}" style="width: 432px; box-sizing: border-box; display: flex; flex-direction: column; background: #F1E8D2; border: 2px solid #3A2E22; box-shadow: 0 14px 30px rgba(0,0,0,0.5)">'
            f'<img src="{img}" alt="Sketch map: {e(name.lower())}" style="display: block; width: 428px; height: 268px; border-bottom: 2px solid #3A2E22">'
            f'<div style="display: flex; flex-direction: column; gap: 12px; padding: 16px 20px 22px">'
            f'<div style="display: flex; flex-direction: column; gap: 2px"><h2 style="margin: 0; font-family: {FELL}; font-weight: 400; font-size: 28px; color: #2C2219">{e(name)}</h2>'
            f'<p style="margin: 0; font-size: 18px; line-height: 1.3; font-style: italic; color: #5E4E3C">{e(pitch)}</p></div>'
            f'{rr}</div></section>')


legend = "".join(f'<span style="display: inline-flex; align-items: center; gap: 6px">{SEAT_SVG[k]}<span>{e(t)}</span></span>' for k, t in
                 (("fire", "fire seat (Core)"), ("water", "water seat (Ocean)"), ("earth", "earth seat (Pangaea)"), ("air", "air seat (Trade Winds)")))

doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Overworld options</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link href="https://fonts.googleapis.com/css2?family=IM+Fell+English:ital@0;1&amp;family=IM+Fell+English+SC&amp;family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0}}
</style>
</helmet>
<div style="position: relative; width: 1440px; height: {H_BOARD}px; box-sizing: border-box; padding: 40px 48px; background: #29221B; color: #EDE3CC; font-family: {BODY}; font-weight: 500; overflow: hidden; display: flex; flex-direction: column; gap: 28px">

<div style="display: flex; flex-direction: column; gap: 6px; max-width: 1100px">
<h1 style="margin: 0; font-family: {FELL}; font-weight: 400; font-size: 46px; color: #EDE3CC">Overworld options</h1>
<p style="margin: 0; font-size: 20px; line-height: 1.4; color: #C9BCA2">The overworld is the region and world map; towns get maps of their own. Six first shapes to react to, drawn at the larger scale you’re leaning toward. Each dot is a place worth visiting, and the four marked seats are where the elemental pinnacles always wait, behind the hardest contests.</p>
</div>

<div style="display: flex; flex-direction: column; gap: 12px">
<span style="font-family: {SC}; font-size: 18px; letter-spacing: 0.06em; color: #C9BCA2">The choices behind every option</span>
<div style="display: flex; gap: 16px; align-items: stretch">
{"".join(choice(a, b) for a, b in CHOICES)}
</div>
<div style="display: flex; flex-wrap: wrap; gap: 22px; align-items: center; font-size: 18px; color: #EDE3CC">{legend}<span style="display: inline-flex; align-items: center; gap: 6px"><svg width="22" height="22" viewBox="0 0 22 22" aria-hidden="true"><circle cx="11" cy="11" r="3" fill="#EDE3CC"></circle></svg><span>a place</span></span></div>
</div>

<div style="display: grid; grid-template-columns: repeat(3, 432px); gap: 32px 24px; align-items: start">
{"".join(option(*o) for o in OPTIONS)}
</div>

<p style="margin: 0; font-size: 19px; line-height: 1.4; font-style: italic; color: #C9BCA2; max-width: 1100px">These mix. A real overworld is usually a blend, such as a great continent with river country inland and an archipelago off one coast. Nothing here is adopted; first sketches for WORLD-01 and WORLD-12, with the seats from WORLD-04.</p>

</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":1440,"height":{H_BOARD}}}}}'>
class Component extends DCLogic {{
renderVals() {{ return {{}}; }}
}}
</script>
</body>
</html>
'''
OUT.write_text(doc)
print(OUT, len(doc))
