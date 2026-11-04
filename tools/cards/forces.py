import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

# ---------- force-face art (288 x 192) ----------
def art_brushfire(i):
    return (L(['M70 70 C60 56 80 46 70 32', 'M150 58 C140 44 160 34 150 20', 'M232 80 C222 66 242 56 232 42'], MID, 1.4, shadow=False, op='0.7')
      + F(['M0 150 Q144 140 288 152 L288 192 L0 192 Z'])
      + L(['M0 150 Q144 140 288 152'], HI, 1.8)
      + EM(['M60 150 C52 132 70 124 62 104 C58 94 66 88 64 80', 'M96 150 C90 136 104 128 98 112',
            'M140 150 C130 128 152 116 142 94 C136 82 146 74 142 64', 'M186 150 C178 134 196 124 188 106',
            'M226 150 C218 132 238 122 230 100'], i, 2.2)
      + DOTS([(78, 96, 1.6), (120, 84, 1.4), (166, 70, 1.8), (206, 92, 1.4), (248, 84, 1.4)], EMB, i)
      + L(['M14 160 l4 -10 l4 10 M30 164 l3 -8 l3 8 M112 160 l4 -10 l4 10 M206 162 l4 -10 l4 10 M256 164 l3 -8 l3 8'], MID, 1.3)
      + L(['M8 178 H110 M150 178 H280'], LOW, 1.2, shadow=False))

def art_washout(i):
    return (L(['M60 10 l-6 18 M100 4 l-6 18 M150 12 l-6 18 M200 2 l-6 18 M250 10 l-6 18 M30 30 l-6 18 M226 32 l-6 18'], WAT, 1.2, shadow=False, op='0.6')
      + F(['M0 70 Q120 90 288 170 L288 192 L0 192 Z'])
      + L(['M0 70 Q120 90 288 170'], HI, 2)
      + L(['M10 96 Q110 116 220 174', 'M30 112 Q120 134 200 180', 'M60 130 Q130 148 176 184'], WAT, 1.6)
      + F(['M120 104 l10 -6 l10 6 l-4 8 h-12 Z', 'M168 128 l8 -5 l8 5 l-3 6 h-10 Z', 'M212 150 l6 -4 l6 4 l-2 5 h-8 Z'])
      + L(['M120 104 l10 -6 l10 6 l-4 8 h-12 Z', 'M168 128 l8 -5 l8 5 l-3 6 h-10 Z', 'M212 150 l6 -4 l6 4 l-2 5 h-8 Z'], HI, 1.5)
      + L(['M106 112 l-8 -2 M156 134 l-8 -2 M202 156 l-7 -2'], LOW, 1.2, shadow=False)
      + DOTS([(228, 172, 1.6), (238, 166, 1.2), (206, 182, 1.4)], WAT))

def art_gust(i):
    return (F(['M0 70 L90 70 L102 82 L86 100 L96 128 L78 192 L0 192 Z'])
      + L(['M0 70 L90 70 L102 82 L86 100 L96 128 L78 192'], HI, 2)
      + L(['M10 100 L76 100', 'M12 140 L74 136', 'M8 172 L70 170'], MID, 1.3)
      + L(['M84 46 q30 -10 60 0 t60 0 t60 0', 'M112 104 q24 -8 48 0 t48 0 t48 0',
           'M196 134 c22 -12 44 0 34 18 c-8 12 -26 4 -20 -6'], AIR, 1.7)
      + F(['M176 70 l10 -6 l10 6 l-4 9 h-12 Z'])
      + L(['M176 70 l10 -6 l10 6 l-4 9 h-12 Z'], HI, 1.6)
      + L(['M144 72 h20 M150 80 h16 M120 76 h16'], LOW, 1.3, shadow=False)
      + L(['M232 70 q6 -6 12 0 q-6 6 -12 0 Z', 'M254 104 q5 -5 10 0 q-5 5 -10 0 Z'], MID, 1.2))

def art_overgrowth(i):
    leaf = lambda x, y: 'M%d %d q8 -10 16 0 q-8 10 -16 0 Z' % (x, y)
    return (L(['M14 124 Q144 -4 274 124'], LOW, 1.4, shadow=False, dash='5 6')
      + F(['M24 192 Q144 76 264 192 Z'])
      + L(['M24 192 Q144 76 264 192'], HI, 2)
      + L(['M44 192 C62 154 92 162 102 134 C110 112 130 116 136 100',
           'M244 192 C228 158 202 162 192 136 C184 116 162 118 156 102',
           'M124 192 C128 172 150 172 152 152'], EARTHC, 1.8)
      + L([leaf(70, 160), leaf(96, 138), leaf(124, 108), leaf(198, 140), leaf(172, 116), leaf(140, 158), leaf(212, 168)], EARTHC, 1.4)
      + L(['M150 20 l4 -8 l4 8 M60 54 l3 -6 l3 6 M226 50 l3 -6 l3 6'], MID, 1.2, shadow=False))

def art_steamburst(i):
    return (L(['M100 40 a18 14 0 0 1 34 -6 a20 16 0 0 1 38 2 a16 12 0 0 1 22 14'], HI, 1.5)
      + L(['M144 152 C120 128 150 114 132 90 C116 68 150 56 136 44', 'M150 152 C176 126 146 110 166 86 C182 66 156 54 170 40',
           'M138 152 C106 138 96 118 108 100'], HI, 1.6)
      + F(['M0 150 Q144 140 288 150 L288 192 L0 192 Z'])
      + L(['M0 150 Q144 140 288 150'], HI, 1.8)
      + F(['M84 164 a60 12 0 1 0 120 0 a60 12 0 1 0 -120 0'], DEEP)
      + L(['M84 164 a60 12 0 1 0 120 0 a60 12 0 1 0 -120 0'], WAT, 1.6)
      + L(['M118 164 a26 5 0 1 0 52 0 a26 5 0 1 0 -52 0'], WAT, 1.1, shadow=False)
      + EM(['M60 172 L72 166 L80 174', 'M210 172 L220 166 L230 174'], i, 2)
      + DOTS([(96, 124, 1.4), (190, 118, 1.6), (176, 74, 1.2), (110, 70, 1.2), (74, 182, 1.4), (222, 184, 1.4)], EMB, i))

def art_gale(i):
    def bent(x, y, dx):
        return ['M%d %d C%d %d %d %d %d %d' % (x, y, x + 2, y - 20, x + 10, y - 34, x + dx, y - 44),
                'M%d %d l20 -4 M%d %d l22 4 M%d %d l18 2' % (x + dx, y - 44, x + dx, y - 44, x + dx - 6, y - 36)]
    return (L(['M0 40 q40 -12 80 0 t80 0 t80 0 t80 0', 'M0 76 q36 -10 72 0 t72 0 t72 0 t72 0', 'M20 108 q30 -8 60 0 t60 0 t60 0 t60 0'], AIR, 1.6)
      + F(['M0 160 Q144 150 288 162 L288 192 L0 192 Z'])
      + L(['M0 160 Q144 150 288 162'], HI, 1.8)
      + L(bent(60, 160, 26) + bent(150, 158, 30) + bent(222, 160, 24), HI, 1.6)
      + L(['M196 120 q5 -5 10 0 q-5 5 -10 0 Z', 'M250 96 q5 -5 10 0 q-5 5 -10 0 Z', 'M120 128 q4 -4 8 0 q-4 4 -8 0 Z'], MID, 1.2))

def art_fog(i):
    return (L(['M0 118 L60 78 L110 108 L170 62 L230 98 L288 74'], LOW, 1.4, shadow=False, op='0.6')
      + L(['M40 112 l6 -14 l6 14 M150 104 l6 -14 l6 14 M244 108 l6 -14 l6 14'], MID, 1.3, shadow=False, op='0.7')
      + L([wave(0, 104, 8, 48, 6), wave(20, 128, 10, 56, 5), wave(0, 150, 9, 44, 7)], AIR, 1.5, shadow=False, op='0.85')
      + F(['M0 174 Q144 166 288 174 L288 192 L0 192 Z'])
      + L(['M0 174 Q144 166 288 174'], HI, 1.6)
      + L([wave(10, 166, 6, 40, 7)], AIR, 1.3, shadow=False, op='0.7'))

def art_thaw(i):
    return (L(['M246 30 a16 16 0 1 0 32 0', 'M262 6 v8 M240 16 l6 5 M284 16 l-6 5'], LOW, 1.4, shadow=False)
      + F(['M60 40 L216 40 L228 118 L48 118 Z'], '#2E3437')
      + L(['M60 40 L216 40 L228 118 L48 118 Z'], HI, 1.8)
      + L(['M118 40 L110 70 L124 90 L116 118', 'M182 40 L190 64 L178 88'], WAT, 1.6)
      + L(['M84 118 v14', 'M140 118 v22', 'M198 118 v12'], WAT, 1.5)
      + DOTS([(84, 140, 2), (140, 148, 2.2), (198, 138, 2)], WAT)
      + F(['M36 170 a108 14 0 1 0 216 0 a108 14 0 1 0 -216 0'], DEEP)
      + L(['M36 170 a108 14 0 1 0 216 0 a108 14 0 1 0 -216 0'], WAT, 1.6)
      + L(['M118 170 a22 4 0 1 0 44 0 a22 4 0 1 0 -44 0'], WAT, 1.1, shadow=False))

def art_collapse(i):
    return (L(['M90 76 C80 60 100 50 92 36', 'M196 72 C186 56 206 46 198 32'], MID, 1.4, shadow=False, op='0.7')
      + F(['M0 150 L70 88 L108 110 L144 98 L180 110 L218 86 L288 150 L288 192 L0 192 Z'])
      + L(['M0 150 L70 88 L108 110 L144 98 L180 110 L218 86 L288 150'], HI, 2)
      + F(['M118 132 l12 -8 l14 6 l-6 10 h-16 Z', 'M156 142 l10 -6 l10 6 l-4 8 h-12 Z'], '#3A3F3A')
      + L(['M118 132 l12 -8 l14 6 l-6 10 h-16 Z', 'M156 142 l10 -6 l10 6 l-4 8 h-12 Z'], HI, 1.5)
      + L(['M128 106 v14 M166 116 v14 M100 120 l8 10 M196 118 l-8 10'], LOW, 1.3, shadow=False)
      + EM(['M100 178 L122 166 L144 178 L166 164 L190 176'], i, 2.2)
      + DOTS([(132, 160, 1.4), (176, 170, 1.4)], EMB, i))

def art_erosion(i):
    left = 'M22 192 L26 70 L110 66 L116 192 Z'; right = 'M152 192 L158 62 L262 66 L268 192 Z'
    return (L(['M170 34 q24 -8 48 0 t48 0', 'M10 40 q20 -8 40 0 t40 0'], AIR, 1.4)
      + F([left, right])
      + L([left[:-2], right[:-2]], HI, 2)
      + L(['M26 104 H112 M24 140 H114 M23 172 H115', 'M158 100 H264 M156 138 H266 M155 170 H267'], MID, 1.2, shadow=False)
      + L(['M134 66 L128 94 L138 122 L130 150 L136 192'], LOW, 1.4, shadow=False, dash='4 5')
      + L(['M84 116 q16 -6 32 0 t32 0 t32 0', 'M70 150 q18 -6 36 0 t36 0 t36 0'], AIR, 1.5, shadow=False, op='0.85')
      + DOTS([(132, 108, 1.2), (138, 132, 1.2), (128, 160, 1.2), (140, 178, 1.2)], MID))

def art_risingsea(i):
    isl = ['M30 112 Q60 82 90 112 Z', 'M118 112 Q150 56 182 112 Z', 'M206 112 Q236 90 264 112 Z']
    return (L(['M222 40 a18 18 0 1 0 36 0 a18 18 0 1 0 -36 0'], LOW, 1.4, shadow=False)
      + F(isl)
      + L([p[:-2] for p in isl], HI, 2)
      + F(['M0 112 H288 V192 H0 Z'], DEEP)
      + L(['M30 112 L10 186', 'M90 112 L108 186', 'M118 112 L98 186', 'M182 112 L204 186', 'M206 112 L188 186', 'M264 112 L284 186'], LOW, 1.3, shadow=False, dash='4 5')
      + L(['M0 112 H288'], WAT, 1.8)
      + L([wave(0, 132, 6, 40, 8), wave(0, 156, 7, 48, 6)], WAT, 1.4)
      + L(['M0 176 H288'], LOW, 1.2, shadow=False, dash='2 6'))

def art_deluge(i):
    crest = ('M0 120 C40 64 116 34 176 46 C228 58 248 96 226 110 C210 118 196 104 206 94 '
             'C188 86 170 100 176 120 C184 146 230 150 288 140')
    return (L(['M30 4 l-8 20 M80 2 l-8 20 M130 6 l-8 20 M220 4 l-8 20 M270 8 l-8 20 M250 40 l-8 20 M20 50 l-8 20'], WAT, 1.2, shadow=False, op='0.6')
      + L(['M20 192 Q100 150 180 192'], LOW, 1.3, shadow=False, dash='4 5')
      + F([crest + ' L288 192 L0 192 Z'], DEEP)
      + L([crest], WAT, 2.2)
      + L(['M40 150 C70 130 110 126 140 140', 'M150 168 C180 156 220 156 250 166'], WAT, 1.4)
      + DOTS([(212, 86, 1.6), (226, 96, 1.4), (196, 80, 1.2), (232, 108, 1.2), (180, 52, 1.2)], HI))

# ---------- force face ----------
FORCE_BG = '#2A2F32'
def force(i, name, num, rar, dur, rule, art):
    rc = '#C9973A' if rar == 'S' else '#C2C5B8'
    durtxt = 'FORCE · LASTS THE ROUND' if dur == 'round' else 'FORCE · ONCE, THEN TO THE VOID'
    return f'''<div style="position: relative; width: 320px; height: 448px; flex: none; border-radius: 14px; background: {FORCE_BG}; box-shadow: 0 14px 32px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.06), inset 0 -4px 10px rgba(0,0,0,0.5)">
<svg width="320" height="448" style="position: absolute; top: 0; left: 0" aria-hidden="true"><defs><filter id="grain{i}"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="3" stitchTiles="stitch" seed="{i}"></feTurbulence><feColorMatrix type="saturate" values="0"></feColorMatrix></filter><pattern id="hatch{i}" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)"><path d="M0 0 V9" stroke="#C2C5B8" stroke-width="1"></path></pattern></defs><rect width="320" height="448" rx="14" filter="url(#grain{i})" opacity="0.14"></rect><rect width="320" height="448" rx="14" fill="url(#hatch{i})" opacity="0.05"></rect><rect x="5.5" y="5.5" width="309" height="437" rx="10" fill="none" stroke="#7E8A90" stroke-width="1" stroke-dasharray="3 5" opacity="0.55"></rect></svg>
<div style="position: absolute; top: 10px; left: 16px; width: 288px; height: 38px; display: flex; align-items: center; justify-content: center; font-size: 26px; font-weight: 600; font-style: italic; color: #ECE6D6; text-shadow: 1px 1px 0 #0D0F0D">{name}</div>
<div style="position: absolute; top: 52px; left: 16px; width: 288px; bottom: 70px; display: flex; flex-direction: column; gap: 6px">
<div role="img" aria-label="{name}" style="position: relative; flex: 1 1 0; min-height: 0; border-radius: 10px; background: rgba(0,0,0,0.22); box-shadow: inset 0 4px 12px rgba(0,0,0,0.65), inset 0 -1px 0 rgba(255,255,255,0.06); overflow: hidden">
<svg style="position: absolute; inset: 0; width: 100%; height: 100%" viewBox="0 0 288 192" preserveAspectRatio="xMidYMid slice" fill="none" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><defs><filter id="ember{i}" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.2" result="b"></feGaussianBlur><feMerge><feMergeNode in="b"></feMergeNode><feMergeNode in="SourceGraphic"></feMergeNode></feMerge></filter></defs>{art(i)}</svg>
</div>
<div style="flex: none; height: 16px; display: flex; align-items: center; justify-content: center; font-family: 'IBM Plex Mono', monospace; font-size: 11px; letter-spacing: 0.1em; color: #A9B3B8">{durtxt}</div>
<div class="rules" style="flex: none; box-sizing: border-box; padding: 6px 10px; border-radius: 8px; background: rgba(13,15,13,0.55); border: 1px solid rgba(194,197,184,0.22); text-align: center; font-size: 42px; line-height: 1.04; color: #ECE6D6">{rule}</div>
</div>
<svg width="288" height="10" viewBox="0 0 288 10" style="position: absolute; top: 386px; left: 16px" aria-hidden="true"><path d="M32 5 H256" stroke="#0D0F0D" stroke-width="3" transform="translate(0 1)"></path><path d="M32 5 H256" stroke="#7E827A" stroke-width="1.4"></path><path d="M24 5 L32 1 L40 5 L32 9 Z M248 5 L256 1 L264 5 L256 9 Z" fill="#7E827A"></path></svg>
<div style="position: absolute; left: 22px; top: 404px; height: 32px; display: flex; align-items: center; font-family: 'IBM Plex Mono', monospace; font-size: 14px; letter-spacing: 0.04em; color: #B9BCB0">{num}/100</div>
<div role="img" aria-label="Rarity {rar}, {RARITY[rar]}" style="position: absolute; right: 18px; top: 402px; width: 36px; height: 36px">
<div style="position: absolute; top: 7px; left: 7px; width: 20px; height: 20px; transform: rotate(45deg); border: 1.6px solid {rc}; box-shadow: 1px 1px 0 #0D0F0D"></div>
<div style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-size: 19px; font-weight: 700; color: {rc}; text-shadow: 1px 1px 0 #0D0F0D">{rar}</div>
</div>
</div>'''

# (permanence face) , (force face)
PAIRS = [
 (('Cinder Field', 12, 'C', ['fire'], None, art_cinder),
  ('Brushfire', 'round', 'A one-affinity card doesn’t count.', art_brushfire)),
 (('Spring', 23, 'C', ['water'], None, art_spring),
  ('Washout', 'once', 'Return a one-affinity card to its binder.', art_washout)),
 (('Ledge', 41, 'C', ['air'], None, art_ledge),
  ('Gust', 'once', 'A one-affinity card becomes its own world.', art_gust)),
 (('Hill', 52, 'C', ['earth'], None, art_hill),
  ('Overgrowth', 'round', 'One of your worlds ignores common forces.', art_overgrowth)),
 (('Hot Spring', 63, 'B', ['water', 'fire'], None, art_hotspring),
  ('Steam Burst', 'round', 'A touching fire-water pair doesn’t count.', art_steamburst)),
 (('Sea Cliff', 71, 'B', ['earth', 'air'], None, art_seacliff),
  ('Gale', 'once', 'Swap two cards between one player’s worlds.', art_gale)),
 (('Cloud Forest', 78, 'B', ['air', 'water'], None, art_cloudforest),
  ('Fog', 'round', 'A world can’t grow.', art_fog)),
 (('Glacier', 66, 'B', ['water'], 'Play on earth permanence. It becomes water.', art_glacier),
  ('Thaw', 'once', 'Remove a card sitting on another.', art_thaw)),
 (('Caldera Lake', 88, 'A', ['fire', 'earth', 'water'], None, art_caldera),
  ('Collapse', 'once', 'Remove any card.', art_collapse)),
 (('Stone Towers', 91, 'A', ['air', 'air', 'earth'], None, art_pillars),
  ('Erosion', 'once', 'Split a world in two.', art_erosion)),
 (('Archipelago', 93, 'A', ['water', 'water', 'earth'], 'Win the round with 10 water affinities.', art_archipelago),
  ('Rising Sea', 'round', 'One-affinity cards in a world don’t count.', art_risingsea)),
 (('Ocean', 98, 'S', ['water', 'water', 'water', 'water'], None, art_ocean),
  ('Deluge', 'round', 'A world doesn’t count.', art_deluge)),
]

W, H = 2880, 1800

def build(outdir):
    rows = [[('COMMON · C · SUBTLE EFFECTS, REAL RESTRICTIONS · REACHES ONLY ONE-AFFINITY CARDS', PAIRS[0:4])],
            [('UNCOMMON · B · STRONGER EFFECTS, LIGHTER RESTRICTIONS', PAIRS[4:8])],
            [('RARE · A · STRONG EFFECTS, FEW RESTRICTIONS', PAIRS[8:11]),
             ('PINNACLE · S · A WHOLE WORLD', PAIRS[11:12])]]
    body = ''; idx = 200
    for groups in rows:
        ghtml = ''
        for label, row in groups:
            pairs = ''
            for perm, fz in row:
                idx += 1
                front = card(idx, *perm)
                idx += 1
                name, dur, rule, art = fz
                back_ = force(idx, name, perm[1], perm[2], dur, rule, art)
                pairs += f'''<div style="display: flex; flex-direction: column; gap: 10px">
<div style="display: flex; gap: 12px">{front}{back_}</div>
<div style="display: flex; gap: 12px; font-family: 'IBM Plex Mono', monospace; font-size: 11px; letter-spacing: 0.1em; color: #7E827A"><div style="width: 320px; text-align: center">PERMANENCE</div><div style="width: 320px; text-align: center">FORCE</div></div>
</div>'''
            ghtml += f'''<div style="display: flex; flex-direction: column; gap: 14px">
<div style="font-family: 'IBM Plex Mono', monospace; font-size: 12px; letter-spacing: 0.12em; color: #A9ADA2">{label}</div>
<div style="display: flex; gap: 56px">{pairs}</div>
</div>'''
        body += f'<div style="display: flex; gap: 56px">{ghtml}</div>\n'
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Force faces</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500;1,600&amp;family=IBM+Plex+Mono:wght@400;500;600&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0}}
a{{color:#D9A441}}a:hover{{color:#ECE6D6}}
</style>
</helmet>
<div style="width: {W}px; height: {H}px; box-sizing: border-box; padding: 48px; background: #191B1A; color: #ECE6D6; font-family: 'Cormorant Garamond', Georgia, serif; display: flex; flex-direction: column; gap: 32px">
<div style="display: flex; justify-content: space-between; align-items: flex-end; gap: 40px">
<div style="display: flex; flex-direction: column; gap: 6px">
<h1 style="margin: 0; font-size: 40px; font-weight: 600">Force faces for the card examples</h1>
<p style="margin: 0; font-family: 'IBM Plex Mono', monospace; font-size: 13px; color: #A9ADA2; max-width: 1500px">The other face of each of the twelve examples, revised Nov 1: rules text under 8 words; effects grow and restrictions shrink with rarity. A world is up to four of your cards in a 2×2 square, and it scores one world point per complete set of the four elements.</p>
</div>
<div style="display: flex; flex-direction: column; gap: 6px; align-items: flex-end; font-family: 'IBM Plex Mono', monospace; font-size: 13px; color: #A9ADA2; text-align: right">
<div>Forces are never part of a world: no affinity, and they don’t connect cards. They can target either player’s cards unless they say otherwise.</div>
<div><span style="color: #ECE6D6">LASTS THE ROUND</span>: played on the card it affects, or beside the world, until the round ends, then goes to the void.</div>
<div><span style="color: #ECE6D6">ONCE</span>: happens, then goes to the void.</div>
<div><span style="color: #ECE6D6">THE VOID</span>: each player’s one place for cards that leave play. “Remove” sends a card there.</div>
</div>
</div>
{body}</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{W},"height":{H}}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
'''
    open(os.path.join(outdir, 'Force-faces.dc.html'), 'w').write(html)
    print('ok', len(html))

if __name__ == '__main__':
    build(sys.argv[1])
