#!/usr/bin/env python3
"""Writes worldsketch-out/project/Pieces.dc.html: the overworld broken into its separate choices."""
import html, pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "worldsketch-out/project/Pieces.dc.html"
FELL = "'IM Fell English', Georgia, serif"
SC = "'IM Fell English SC', Georgia, serif"
BODY = "'Cormorant Garamond', Georgia, serif"
H_BOARD = 1780

SHAPES = [
    ("/_blob/94bf68431b37a3f6a607876e7ed18600", "Compact", "Short trips and a strong middle. The far edge is never very far."),
    ("/_blob/4a94a5af4d54d73296bd61441f8ef1ae", "Long", "One line from end to end, so progress reads as distance travelled."),
    ("/_blob/65becde3195e9fcef60cc0aa9aed7670", "Crescent", "Wrapped around a great bay: the ends are far apart by land, close by sea."),
    ("/_blob/7b55b2980084661366b5e7a66b2fce0e", "Branching", "Peninsulas: long coasts and dead ends, each one a region you finish."),
    ("/_blob/9c0a9d1777224e8d5119332d4123eff3", "Ring", "Land around a sea, so every region shares one shore."),
    ("/_blob/085053dcf56766855b14cc5ba194bc7f", "Broken", "One continent split by narrow straits, each crossing a small gate."),
]
WATERS = [
    ("/_blob/5f48c11d3db636c333ade17ae574cf6e", "Ocean and coastlines", "Ports, ships, storms, islands offshore. The water seat can sit out at sea."),
    ("/_blob/fe78c1ffac0cf8017bc18b50adbc1684", "One inland sea", "A hub in the middle that every region touches."),
    ("/_blob/d12c01103e64eb9aa6f74d5bb6490719", "Great lakes", "Lakes as inland hubs, joined by short rivers. Lake towns, fishing villages."),
    ("/_blob/c81a6f1383e6d380dc836b6fa1b81808", "A great river", "A road with a direction: upstream is harder, tributaries branch off."),
    ("/_blob/afb542c9585e926ba518deb55a9a881c", "Fjords", "Deep, narrow inlets between mountains. Hard to reach, good for hiding things."),
    ("/_blob/5a77cf252ccd2e7aa6ebc1e6abc6296f", "Marsh and delta", "Where the river meets the sea: wetlands, channels, a maze of small places."),
]
REGIONS = [
    ("/_blob/7704aaae672bf90cdf31ab72ee8137d0", "One continent, many regions", "Mountains and rivers are the borders. You can walk anywhere, so the land itself does the gating."),
    ("/_blob/56910510ceb07efe21a9a0822b5a34fd", "A few continents, a few regions each", "Sea crossings are the big gates, and the borders inside each continent are the small ones."),
    ("/_blob/98c1a6bc1ec77e4fbe0fbb38f5130570", "Islands, one region each", "Every region is its own island. The edges are clear, but travel is always by boat."),
]
COMPARE = [
    ("Travel", "Boats up and down, roads along the banks.", "Harbors and ships; a crossing is a milestone."),
    ("Feel", "Inland and quiet, towns strung along the water.", "Open and wide, with storms and far shores."),
    ("Getting harder", "Upstream is harder: a difficulty curve for free.", "Farther shores and islands are harder."),
    ("Elements", "Water everywhere but small; fire and earth get room.", "Water dominates; the land is coastal and thinner."),
    ("Water seat", "At a source, a great lake, or the delta.", "Out at sea, reached only by ship."),
]


def e(s):
    return html.escape(s, quote=False)


def small(img, name, text):
    return (f'<section aria-label="{e(name)}" style="width: 210px; box-sizing: border-box; display: flex; flex-direction: column; background: #F1E8D2; border: 2px solid #3A2E22">'
            f'<img src="{img}" alt="Sketch: {e(name.lower())}" style="display: block; width: 206px; height: 129px; border-bottom: 2px solid #3A2E22">'
            f'<div style="display: flex; flex-direction: column; gap: 4px; padding: 10px 12px 14px">'
            f'<h3 style="margin: 0; font-family: {FELL}; font-weight: 400; font-size: 22px; color: #2C2219">{e(name)}</h3>'
            f'<p style="margin: 0; font-size: 17px; line-height: 1.28; color: #2C2219">{e(text)}</p></div></section>')


def big(img, name, text):
    return (f'<section aria-label="{e(name)}" style="width: 432px; box-sizing: border-box; display: flex; flex-direction: column; background: #F1E8D2; border: 2px solid #3A2E22">'
            f'<img src="{img}" alt="Sketch: {e(name.lower())}, with region borders dashed" style="display: block; width: 428px; height: 268px; border-bottom: 2px solid #3A2E22">'
            f'<div style="display: flex; flex-direction: column; gap: 4px; padding: 14px 18px 18px">'
            f'<h3 style="margin: 0; font-family: {FELL}; font-weight: 400; font-size: 26px; color: #2C2219">{e(name)}</h3>'
            f'<p style="margin: 0; font-size: 18px; line-height: 1.3; color: #2C2219">{e(text)}</p></div></section>')


def row_label(t, sub):
    return (f'<div style="display: flex; align-items: baseline; gap: 14px"><span style="font-family: {SC}; font-size: 22px; letter-spacing: 0.05em; color: #EDE3CC">{e(t)}</span>'
            f'<span style="font-size: 18px; font-style: italic; color: #C9BCA2">{e(sub)}</span></div>')


def compare():
    head = (f'<tr><th style="width: 18%; padding: 0 12px 10px 0; text-align: left; font-family: {SC}; font-weight: 400; font-size: 16px; letter-spacing: 0.05em; color: #7A5E3E"></th>'
            f'<th style="width: 41%; padding: 0 16px 10px 0; text-align: left; font-family: {FELL}; font-weight: 400; font-size: 26px; color: #2C2219">Rivers and lakes</th>'
            f'<th style="width: 41%; padding: 0 0 10px 0; text-align: left; font-family: {FELL}; font-weight: 400; font-size: 26px; color: #2C2219">Oceans and coastlines</th></tr>')
    rows = "".join(f'<tr><td style="padding: 9px 12px 9px 0; border-top: 1px solid #CDBF9F; font-family: {SC}; font-size: 16px; letter-spacing: 0.05em; color: #7A5E3E; vertical-align: top">{e(a)}</td>'
                   f'<td style="padding: 9px 16px 9px 0; border-top: 1px solid #CDBF9F; font-size: 18px; line-height: 1.3; color: #2C2219; vertical-align: top">{e(b)}</td>'
                   f'<td style="padding: 9px 0; border-top: 1px solid #CDBF9F; font-size: 18px; line-height: 1.3; color: #2C2219; vertical-align: top">{e(c)}</td></tr>' for a, b, c in COMPARE)
    return (f'<div style="box-sizing: border-box; padding: 22px 28px 18px; background: #F1E8D2; border: 2px solid #3A2E22">'
            f'<table style="width: 100%; border-collapse: collapse">{head}{rows}</table>'
            f'<p style="margin: 12px 0 0; font-size: 18px; font-style: italic; color: #5E4E3C">Most worlds use both: coasts on the outside, rivers and lakes inside.</p></div>')


doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Overworld pieces</title>
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
<div style="position: relative; width: 1440px; height: {H_BOARD}px; box-sizing: border-box; padding: 40px 48px; background: #29221B; color: #EDE3CC; font-family: {BODY}; font-weight: 500; overflow: hidden; display: flex; flex-direction: column; gap: 30px">

<div style="display: flex; flex-direction: column; gap: 6px; max-width: 1100px">
<h1 style="margin: 0; font-family: {FELL}; font-weight: 400; font-size: 46px; color: #EDE3CC">Overworld pieces</h1>
<p style="margin: 0; font-size: 20px; line-height: 1.4; color: #C9BCA2">The same choices, one at a time. Take one from each row and you have an overworld; the six options next door are mixes of these.</p>
</div>

<div style="display: flex; flex-direction: column; gap: 12px">
{row_label("Continent shapes", "how the land is laid out")}
<div style="display: flex; gap: 16px; align-items: flex-start">{"".join(small(*s) for s in SHAPES)}</div>
</div>

<div style="display: flex; flex-direction: column; gap: 12px">
{row_label("Bodies of water", "what the water does")}
<div style="display: flex; gap: 16px; align-items: flex-start">{"".join(small(*s) for s in WATERS)}</div>
</div>

<div style="display: flex; flex-direction: column; gap: 12px">
{row_label("Continents or regions", "how the world divides; dashed lines are region borders")}
<div style="display: flex; gap: 24px; align-items: flex-start">{"".join(big(*s) for s in REGIONS)}</div>
</div>

<div style="display: flex; flex-direction: column; gap: 12px">
{row_label("Rivers and lakes, or oceans and coastlines", "what each gives the hunt")}
{compare()}
</div>

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
