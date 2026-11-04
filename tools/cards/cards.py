import sys
OUT = sys.argv[1]
SH='#0D0F0D'; HI='#C2C5B8'; MID='#9EA398'; LOW='#7E827A'; FILL='#2B2F2B'; EMB='#D0663F'; WAT='#7FA7B5'; AIR='#D5D8CC'; EARTHC='#A88F6B'; DEEP='#22292B'

def P(ds): return ''.join('<path d="%s"></path>' % d for d in ds)
def L(ds, color, w, shadow=True, op=None, dash=None):
    s=''
    if shadow: s+='<g transform="translate(1 1)" stroke="%s" stroke-width="%s">%s</g>' % (SH, w, P(ds))
    extra=(' stroke-opacity="%s"' % op if op else '')+(' stroke-dasharray="%s"' % dash if dash else '')
    s+='<g stroke="%s" stroke-width="%s"%s>%s</g>' % (color, w, extra, P(ds))
    return s
def F(ds, color=FILL): return ''.join('<path d="%s" fill="%s"></path>' % (d, color) for d in ds)
def EM(ds, i, w=2.4): return '<g filter="url(#ember%d)" stroke="%s" stroke-width="%s">%s</g>' % (i, EMB, w, P(ds))
def DOTS(pts, color, i=None):
    c=''.join('<circle cx="%s" cy="%s" r="%s"></circle>' % p for p in pts)
    f=(' filter="url(#ember%d)"' % i) if i is not None else ''
    return '<g fill="%s"%s>%s</g>' % (color, f, c)
def wave(x0, y, amp, half, n):
    d='M%d %d q%d %d %d 0' % (x0, y, half/2, -amp, half)
    d+=''.join(' t%d 0' % half for _ in range(n-1))
    return d

def art_cinder(i):
    return (F(['M0 160 Q144 148 288 162 L288 280 L0 280 Z'])
      + L(['M188 156 A34 34 0 0 1 256 152'], MID, 1.6)
      + L(['M0 160 Q144 148 288 162'], HI, 1.8)
      + L(['M82 170 C70 150 94 138 82 118 C72 102 90 92 84 76','M150 176 C140 158 160 148 150 130','M222 172 C212 152 234 142 224 124'], MID, 1.6)
      + EM(['M30 214 L58 200 L80 216 L110 204 L132 220','M150 240 L176 222 L200 236 L228 218 L262 230','M60 252 L88 244 L104 258'], i)
      + DOTS([(40,190,1.6),(120,186,1.4),(176,200,1.8),(250,196,1.4),(96,232,1.6),(210,256,1.4)], EMB, i)
      + L(['M8 266 H120 M160 266 H280','M24 274 H96 M180 274 H260'], LOW, 1.2, shadow=False))

def art_spring(i):
    return (L(['M0 150 Q60 110 120 140 Q190 100 288 146'], LOW, 1.4, shadow=False)
      + F(['M0 200 Q144 186 288 200 L288 280 L0 280 Z'])
      + L(['M0 200 Q144 186 288 200'], HI, 1.8)
      + F(['M28 214 Q44 186 84 198 Q96 214 74 226 Q44 232 28 214 Z','M204 206 Q236 182 266 204 Q270 222 244 228 Q214 230 204 206 Z'])
      + L(['M28 214 Q44 186 84 198 Q96 214 74 226 Q44 232 28 214 Z','M204 206 Q236 182 266 204 Q270 222 244 228 Q214 230 204 206 Z'], HI, 1.8)
      + L(['M74 214 a70 14 0 1 0 140 0 a70 14 0 1 0 -140 0','M100 214 a44 9 0 1 0 88 0 a44 9 0 1 0 -88 0'], WAT, 1.6)
      + L(['M126 214 a18 4 0 1 0 36 0 a18 4 0 1 0 -36 0'], WAT, 1.2, shadow=False)
      + L(['M144 208 C138 186 152 170 144 150','M132 206 C124 190 134 176 126 162','M156 206 C164 190 154 176 162 162'], WAT, 1.8)
      + DOTS([(144,138,2),(120,150,1.6),(168,150,1.6),(132,128,1.4),(156,126,1.4)], WAT)
      + L(['M20 250 l4 -10 l4 10 M232 248 l4 -10 l4 10 M262 256 l3 -8 l3 8 M54 262 l3 -8 l3 8'], MID, 1.4))

def art_ledge(i):
    return (L(['M150 270 L180 244 L206 262 L236 236 L288 268'], LOW, 1.4, shadow=False)
      + L(['M140 232 q20 -16 40 0 q20 -16 40 0 q20 -16 40 0 q16 -12 28 0'], LOW, 1.4, shadow=False)
      + F(['M0 96 L118 96 L132 108 L112 128 L124 156 L100 186 L110 222 L88 280 L0 280 Z'])
      + L(['M0 96 L118 96 L132 108 L112 128 L124 156 L100 186 L110 222 L88 280'], HI, 2)
      + L(['M10 130 L96 130','M14 170 L90 166','M8 214 L84 210','M20 250 L72 246'], MID, 1.3)
      + L(['M40 96 l6 -12 l6 12 M70 96 l5 -9 l5 9'], MID, 1.4)
      + L(['M150 70 q30 -10 60 0 t60 0','M168 108 q24 -8 48 0 t48 0','M146 146 q30 -10 60 0 t56 0'], AIR, 1.6)
      + L(['M214 40 q8 -7 16 0 q8 -7 16 0'], HI, 1.5))

def art_hill(i):
    return (L(['M30 70 q16 -12 32 0 q16 -12 32 0','M190 54 q14 -10 28 0 q14 -10 28 0'], LOW, 1.4, shadow=False)
      + F(['M0 236 Q90 118 170 170 Q226 140 288 196 L288 280 L0 280 Z'])
      + L(['M0 236 Q90 118 170 170 Q226 140 288 196'], HI, 2)
      + L(['M40 236 Q96 160 150 200','M90 252 Q120 216 150 232','M190 222 Q230 190 270 214'], MID, 1.4)
      + L(['M72 182 L76 156 L88 154 L92 180'], HI, 1.8)
      + L(['M150 280 Q140 250 160 234 Q176 220 168 204'], LOW, 1.4, shadow=False, dash='4 5')
      + L(['M10 262 l6 -8 M40 270 l6 -8 M230 258 l6 -8 M262 268 l6 -8'], LOW, 1.2, shadow=False))

def art_hotspring(i):
    return (L(['M0 120 L50 80 L90 106 L140 64 L200 110 L240 84 L288 116'], LOW, 1.4, shadow=False)
      + F(['M0 196 Q144 182 288 196 L288 280 L0 280 Z'])
      + L(['M0 196 Q144 182 288 196'], HI, 1.8)
      + F(['M50 222 a94 22 0 1 0 188 0 a94 22 0 1 0 -188 0'], DEEP)
      + L(['M50 222 a94 22 0 1 0 188 0 a94 22 0 1 0 -188 0'], WAT, 1.8)
      + L(['M96 222 a48 9 0 1 0 96 0 a48 9 0 1 0 -96 0'], WAT, 1.2, shadow=False)
      + F(['M36 216 Q44 198 64 204 Q70 216 58 224 Z','M222 210 Q242 196 258 210 Q256 224 236 224 Z'])
      + L(['M36 216 Q44 198 64 204 Q70 216 58 224 Z','M222 210 Q242 196 258 210 Q256 224 236 224 Z'], HI, 1.8)
      + L(['M108 200 C98 180 120 168 110 148 C102 132 118 120 112 104','M144 196 C134 174 156 162 146 140 C138 124 154 112 148 94','M180 200 C170 180 192 168 182 148 C174 132 190 120 184 104'], HI, 1.6)
      + EM(['M44 240 L56 234 L64 242','M224 240 L234 234 L244 242'], i, 2)
      + DOTS([(70,244,1.4),(212,246,1.4)], EMB, i))

def art_seacliff(i):
    return (L([wave(0,214,8,40,5), wave(0,238,9,48,4), wave(0,262,10,56,4)], WAT, 1.6)
      + F(['M288 34 L236 34 L222 62 L232 92 L210 128 L222 164 L200 206 L206 280 L288 280 Z'])
      + L(['M236 34 L222 62 L232 92 L210 128 L222 164 L200 206 L206 280'], HI, 2)
      + L(['M232 70 L284 70','M224 110 L284 108','M218 150 L284 150','M212 196 L284 192'], MID, 1.3)
      + L(['M240 34 l5 -10 l5 10 M262 34 l4 -8 l4 8'], MID, 1.4)
      + L(['M188 206 q6 -6 12 0 M180 222 q6 -6 12 0'], HI, 1.2, shadow=False)
      + L(['M20 70 q28 -10 56 0 t56 0','M40 110 q24 -8 48 0 t48 0','M10 150 q30 -10 60 0 t50 0'], AIR, 1.6)
      + L(['M110 44 q7 -6 14 0 q7 -6 14 0','M150 70 q5 -4 10 0 q5 -4 10 0'], HI, 1.4))

def tree(x, y, s=1.0):
    return 'M%g %g L%g %g L%g %g Z M%g %g v%g' % (x-12*s, y, x, y-30*s, x+12*s, y, x, y, 8*s)

def art_cloudforest(i):
    return (L(['M40 60 l-6 14 M70 46 l-6 14 M220 50 l-6 14 M250 66 l-6 14'], WAT, 1.2, shadow=False)
      + F(['M0 210 L70 108 L120 150 L186 80 L288 200 L288 280 L0 280 Z'])
      + L(['M0 210 L70 108 L120 150 L186 80 L288 200'], HI, 2)
      + L([wave(10,170,14,36,7)], AIR, 1.4, shadow=False, op='0.85')
      + L([tree(30,252), tree(58,246,1.1), tree(88,254,0.9), tree(196,250), tree(226,244,1.1), tree(256,252,0.9)], HI, 1.5)
      + L([wave(60,206,12,32,5)], AIR, 1.4, shadow=False, op='0.85')
      + L(['M0 264 H288'], LOW, 1.2, shadow=False))

def art_glacier(i):
    return (L(['M0 92 L50 52 L96 80 L150 36 L210 74 L250 50 L288 84'], LOW, 1.4, shadow=False)
      + F(['M0 108 L56 96 L120 110 L188 92 L288 106 L288 206 L0 206 Z'], '#2E3437')
      + L(['M0 108 L56 96 L120 110 L188 92 L288 106'], HI, 2)
      + L(['M44 112 L54 150 L46 176','M104 114 L98 160 L108 196','M178 104 L188 146 L180 188','M240 108 L232 150 L240 182'], WAT, 1.6)
      + L(['M10 130 H34 M66 140 H90 M120 132 H150 M200 126 H222 M252 136 H278'], MID, 1.2, shadow=False)
      + L(['M126 158 Q140 138 160 146 Q174 160 156 174 Q134 178 126 158 Z'], HI, 1.6, shadow=False, op='0.6', dash='4 4'))

def art_caldera(i):
    return (L(['M0 258 Q72 236 144 252 Q216 236 288 256'], LOW, 1.4, shadow=False)
      + F(['M14 240 L96 128 Q144 112 192 128 L274 240 Z'])
      + L(['M14 240 L96 128 Q144 112 192 128 L274 240'], HI, 2)
      + F(['M106 132 Q144 146 182 132 Q144 122 106 132 Z'], DEEP)
      + L(['M106 132 Q144 146 182 132 Q144 122 106 132 Z'], WAT, 1.6)
      + L(['M96 128 L76 180 L58 230','M192 128 L212 180 L230 230','M120 142 L112 200','M168 142 L176 200'], MID, 1.4)
      + EM(['M144 150 L136 176 L144 192 L134 222'], i, 2.2)
      + DOTS([(126,190,1.4),(156,206,1.6),(150,170,1.2)], EMB, i)
      + L(['M144 118 C136 100 154 90 144 72 C136 58 150 50 146 36'], HI, 1.4))

def art_pillars(i):
    pf=['M30 280 L34 96 L72 90 L76 280 Z','M112 280 L110 48 L156 44 L160 280 Z','M196 280 L200 112 L238 108 L244 280 Z']
    return (L(['M170 60 q24 -8 48 0 t48 0','M10 50 q20 -8 40 0 t40 0'], AIR, 1.4)
      + F(pf)
      + L([p[:-2] for p in pf], HI, 2)
      + L(['M34 130 H72 M33 170 H74 M32 214 H75','M111 90 H157 M111 140 H158 M112 190 H159','M201 150 H239 M200 196 H241'], MID, 1.2, shadow=False)
      + L(['M46 90 l5 -12 l5 12 M58 90 l4 -9 l4 9','M124 44 l6 -14 l6 14 M140 44 l5 -10 l5 10','M212 108 l5 -11 l5 11'], HI, 1.4)
      + L([wave(0,238,14,40,8), wave(14,262,12,36,8)], AIR, 1.4, shadow=False, op='0.85'))

def art_archipelago(i):
    isl=['M14 150 Q46 112 84 150 Z','M100 150 Q150 84 204 150 Z','M214 150 Q240 124 270 150 Z']
    return (L(['M218 62 a20 20 0 1 0 40 0 a20 20 0 1 0 -40 0'], LOW, 1.4, shadow=False)
      + F(isl)
      + L([p[:-2] for p in isl], HI, 2)
      + L(['M150 104 l-2 -16 M148 88 q-10 -2 -14 6 M148 88 q10 -2 14 6'], HI, 1.3)
      + L(['M0 150 H288'], HI, 1.6)
      + L(['M30 160 H70 M120 162 H186 M224 160 H262'], WAT, 1.2, shadow=False, op='0.6')
      + L([wave(0,174,8,40,8), wave(0,198,9,48,6)], WAT, 1.6))

def art_ocean(i):
    crest='M0 236 C40 236 70 214 96 196 C124 176 160 170 186 184 C206 196 204 220 186 222 C174 224 170 212 178 206 C164 200 150 212 156 230 C162 248 196 252 230 244 C256 238 274 230 288 226'
    return (L(['M206 54 a22 22 0 1 0 44 0 a22 22 0 1 0 -44 0'], HI, 1.6)
      + L(['M0 92 H288'], LOW, 1.2, shadow=False)
      + L(['M220 100 H236 M212 112 H244 M220 124 H236'], WAT, 1.2, shadow=False, op='0.7')
      + L([wave(0,124,6,36,8)], WAT, 1.2)
      + L([wave(0,152,8,48,6)], WAT, 1.5)
      + L([wave(0,186,11,64,5)], WAT, 1.8)
      + F([crest+' L288 280 L0 280 Z'], DEEP)
      + L([crest], WAT, 2.2)
      + L(['M120 200 C140 188 164 186 180 196'], HI, 1.4)
      + DOTS([(190,178,1.6),(200,190,1.4),(172,176,1.2),(206,204,1.2)], HI))

GLYPH={'fire':('M12 3.5 L20.5 19 H3.5 Z',EMB),'water':('M3.5 5 H20.5 L12 20.5 Z',WAT),
       'air':('M12 3.5 L20.5 19 H3.5 Z M3 12.5 H21',AIR),'earth':('M3.5 5 H20.5 L12 20.5 Z M3 11.5 H21',EARTHC)}
def glyph(el, size=28):
    d,c=GLYPH[el]
    return ('<svg width="%d" height="%d" viewBox="0 0 24 24" fill="none" stroke-width="1.9" stroke-linejoin="round" stroke-linecap="round" aria-hidden="true">'
            '<g transform="translate(0.8 0.8)" stroke="%s"><path d="%s"></path></g><g stroke="%s"><path d="%s"></path></g></svg>') % (size,size,SH,d,c,d)

def affinity_label(tags):
    order=['fire','water','air','earth']; parts=[]
    for e in order:
        n=tags.count(e)
        if n: parts.append('%d %s' % (n,e))
    return ', '.join(parts)

RARITY={'C':'common','B':'uncommon','A':'rare','S':'pinnacle'}
def card(i, name, num, rar, tags, rule, art):
    rc = '#C9973A' if rar=='S' else '#C2C5B8'
    plaque=''
    if rule:
        plaque=('<div style="position: absolute; left: 10px; right: 10px; bottom: 10px; box-sizing: border-box; padding: 8px 12px; border-radius: 6px; '
                'background: rgba(13,15,13,0.78); border: 1px solid rgba(194,197,184,0.28); font-size: 16px; font-style: italic; line-height: 1.2; color: #ECE6D6">%s</div>') % rule
    glyphs=''.join(glyph(t) for t in tags)
    return f'''<div style="position: relative; width: 320px; height: 448px; flex: none; border-radius: 14px; background: #353A35; box-shadow: 0 14px 32px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.08), inset 0 -4px 10px rgba(0,0,0,0.45)">
<svg width="320" height="448" style="position: absolute; top: 0; left: 0" aria-hidden="true"><filter id="grain{i}"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="3" stitchTiles="stitch" seed="{i}"></feTurbulence><feColorMatrix type="saturate" values="0"></feColorMatrix></filter><rect width="320" height="448" rx="14" filter="url(#grain{i})" opacity="0.16"></rect></svg>
<div style="position: absolute; top: 10px; left: 16px; width: 288px; height: 38px; display: flex; align-items: center; justify-content: center; font-size: 26px; font-weight: 600; color: #ECE6D6; text-shadow: 1px 1px 0 #0D0F0D">{name}</div>
<div role="img" aria-label="{name}" style="position: absolute; top: 52px; left: 16px; width: 288px; height: 280px; border-radius: 10px; background: rgba(0,0,0,0.2); box-shadow: inset 0 4px 12px rgba(0,0,0,0.65), inset 0 -1px 0 rgba(255,255,255,0.07); overflow: hidden">
<svg width="288" height="280" viewBox="0 0 288 280" fill="none" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><defs><filter id="ember{i}" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.2" result="b"></feGaussianBlur><feMerge><feMergeNode in="b"></feMergeNode><feMergeNode in="SourceGraphic"></feMergeNode></feMerge></filter></defs>{art(i)}</svg>
{plaque}
</div>
<div role="img" aria-label="Affinity: {affinity_label(tags)}" style="position: absolute; top: 342px; left: 16px; width: 288px; height: 36px; display: flex; align-items: center; justify-content: center; gap: 12px">{glyphs}</div>
<svg width="288" height="10" viewBox="0 0 288 10" style="position: absolute; top: 386px; left: 16px" aria-hidden="true"><path d="M32 5 H256" stroke="#0D0F0D" stroke-width="3" transform="translate(0 1)"></path><path d="M32 5 H256" stroke="#7E827A" stroke-width="1.4"></path><path d="M24 5 L32 1 L40 5 L32 9 Z M248 5 L256 1 L264 5 L256 9 Z" fill="#7E827A"></path></svg>
<div style="position: absolute; left: 22px; top: 404px; height: 32px; display: flex; align-items: center; font-family: 'IBM Plex Mono', monospace; font-size: 14px; letter-spacing: 0.04em; color: #B9BCB0">{num}/100</div>
<div role="img" aria-label="Rarity {rar}, {RARITY[rar]}" style="position: absolute; right: 18px; top: 402px; width: 36px; height: 36px">
<div style="position: absolute; top: 7px; left: 7px; width: 20px; height: 20px; transform: rotate(45deg); border: 1.6px solid {rc}; box-shadow: 1px 1px 0 #0D0F0D"></div>
<div style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-size: 19px; font-weight: 700; color: {rc}; text-shadow: 1px 1px 0 #0D0F0D">{rar}</div>
</div>
</div>'''

CARDS=[
 ('Cinder Field',12,'C',['fire'],None,art_cinder),
 ('Spring',23,'C',['water'],None,art_spring),
 ('Ledge',41,'C',['air'],None,art_ledge),
 ('Hill',7,'C',['earth'],None,art_hill),
 ('Hot Spring',63,'B',['water','fire'],None,art_hotspring),
 ('Sea Cliff',71,'B',['earth','air'],None,art_seacliff),
 ('Cloud Forest',78,'B',['air','water'],None,art_cloudforest),
 ('Glacier',66,'B',['water'],"Covers one permanence. Its tags don’t count while the Glacier stands.",art_glacier),
 ('Caldera Lake',88,'A',['fire','earth','water'],None,art_caldera),
 ('Stone Towers',91,'A',['air','air','earth'],None,art_pillars),
 ('Archipelago',93,'A',['water','water','earth'],"At the end of a round, if you control 10 water tags, you win the round.",art_archipelago),
 ('Ocean',98,'S',['water','water','water','water'],None,art_ocean),
]
rows=[('COMMON · C · ONE ELEMENT',CARDS[0:4]),('UNCOMMON · B · TWO ELEMENTS, OR ONE AND AN EFFECT',CARDS[4:8]),('RARE · A · THREE ELEMENTS, OR FEWER AND AN EFFECT    PINNACLE · S · FOUR OF ONE',CARDS[8:12])]
idx=0; body=''
for label, cs in rows:
    cards_html=''
    for c in cs:
        idx+=1; cards_html+=card(idx,*c)
    body+=f'''<div style="display: flex; flex-direction: column; gap: 14px">
<div style="font-family: 'IBM Plex Mono', monospace; font-size: 12px; letter-spacing: 0.12em; color: #A9ADA2">{label}</div>
<div style="display: flex; gap: 48px">{cards_html}</div>
</div>
'''
legend=''.join(f'<div style="display: flex; align-items: center; gap: 8px">{glyph(e,22)}<span style="font-family: \'IBM Plex Mono\', monospace; font-size: 13px; color: #ECE6D6">{e.capitalize()}</span></div>' for e in ['fire','water','air','earth'])
html=f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Card examples</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&amp;family=IBM+Plex+Mono:wght@400;500;600&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0}}
a{{color:#D9A441}}a:hover{{color:#ECE6D6}}
</style>
</helmet>
<div style="width: 1520px; height: 1800px; box-sizing: border-box; padding: 48px; background: #191B1A; color: #ECE6D6; font-family: 'Cormorant Garamond', Georgia, serif; display: flex; flex-direction: column; gap: 36px">
<div style="display: flex; justify-content: space-between; align-items: flex-end; gap: 32px">
<div style="display: flex; flex-direction: column; gap: 6px">
<h1 style="margin: 0; font-size: 40px; font-weight: 600">Card examples</h1>
<p style="margin: 0; font-family: 'IBM Plex Mono', monospace; font-size: 13px; color: #A9ADA2">Twelve permanence faces for the world-points loop. One of each element under your control makes a world point.</p>
</div>
<div style="display: flex; flex-direction: column; gap: 10px; align-items: flex-end">
<div style="display: flex; gap: 22px">{legend}</div>
<p style="margin: 0; font-family: 'IBM Plex Mono', monospace; font-size: 13px; color: #A9ADA2">Rarity: C common · B uncommon · A rare · S pinnacle</p>
</div>
</div>
{body}</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":1520,"height":1800}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
'''
open(OUT,'w').write(html)
print(len(html))
