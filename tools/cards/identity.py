# Element identity check, step 1 (Nov 11, Cam: elements should have an identity through what their forces do; with so many
# hybrid cards, an algorithm should flag permanences or forces whose effect fits poorly with the elements on the card).
# This step only describes the pool: it tags every force and permanence text with its effect category (the numbering of
# design/effect-categories.md), its target element and the element it turns things into, then counts categories by element.
# The judging step needs Cam's element pie (which categories each element gets) and his rule for hybrid cards.
# Usage: python3 tools/cards/identity.py [--md out.md]
import json, re, sys, collections
ROOT = __file__.rsplit('/', 3)[0]
EL = ['water', 'earth', 'fire', 'air']
CATS = {1: 'positional', 2: 'adding pips', 3: 'taking pips away', 4: 'changing pips', 5: 'copying', 7: 'removing',
        8: 'returning', 9: 'moving and rearranging', 10: 'protection', 11: 'growth and shape', 12: 'scoring rules',
        15: 'timing', 16: 'turn order and tempo', 18: 'forces on forces'}

def tag(text):
    t = text.rstrip('.')
    out = {'cat': None, 'target': [], 'into': None, 'own': bool(re.search(r"\b(your|one of your)\b", t, re.I))}
    out['target'] = [e for e in EL if re.search(r"\b%s\b" % e, t.split(' become')[0].split(' if ')[0], re.I)]
    m = re.search(r"becomes? (water|earth|fire|air)\b", t)
    if re.search(r"\bforces?\b", t) and re.match(r"(Remove|When played, remove)", t): out['cat'] = 18
    elif re.search(r"can't be (moved|removed)|ignores .*forces|Unaffected", t, re.I): out['cat'] = 10
    elif re.search(r"can't grow", t): out['cat'] = 11
    elif re.search(r"^Score a point|world point if this world", t): out['cat'] = 12
    elif re.match(r"\+1 (water|earth|fire|air)", t): out['cat'] = 2; out['into'] = t.split()[1]
    elif re.search(r"[Cc]opies", t): out['cat'] = 5
    elif re.search(r"lose(s)? (its|their) affinities|loses it\b", t): out['cat'] = 3
    elif m: out['cat'] = 4; out['into'] = m.group(1)
    elif re.search(r"own world|separate worlds|^(Move|Swap|Split|Rearrange)|When played, move", t): out['cat'] = 9
    elif re.search(r"^Return|When played, return", t): out['cat'] = 8
    elif re.match(r"Remove", t): out['cat'] = 7
    elif re.search(r"play another", t): out['cat'] = 16
    if out['target'] and out['cat'] in (10, 12, 2): out['target'] = [] if out['cat'] != 10 else out['target']
    return out

def card_elements(affs):
    els = set()
    for a in affs:
        if a == 'any': els.add('any')
        else: els.update(a.split('|'))
    return els

rows = []
for c in json.load(open(ROOT + '/data/cards.json'))['cards']:
    if c.get('meta'): continue
    p = c['permanence']; els = card_elements(p['affinities'])
    for face, name, text in ([('force', c['force']['name'], c['force']['text'])] if c.get('force') else []) + ([('permanence', p['name'], p['text'])] if p.get('text') else []):
        tg = tag(text)
        rows.append(dict(no=c['no'], rarity=c['rarity'], card=p['name'], pips=p['affinities'], els=sorted(els), face=face, name=name, text=text, **tg))

unknown = [r for r in rows if r['cat'] is None]
if unknown: print('untagged:', [(r['name'], r['text']) for r in unknown], file=sys.stderr)

def matrix(face, mono):
    m = collections.defaultdict(collections.Counter)
    for r in rows:
        if r['face'] != face: continue
        els = r['els'] or ['none']
        if mono and len(els) != 1: continue
        for e in els: m[r['cat']][e] += 1
    return m

if __name__ == '__main__':
    md = '# Element identity: the pool as it stands (step 1, generated)\n\n'
    for face in ('force', 'permanence'):
        for mono in (True, False):
            m = matrix(face, mono)
            cols = EL + ['any', 'none']
            md += '\n### %s texts, %s\n\n| Category | %s |\n|---|%s\n' % (face.capitalize(), 'cards of one element only' if mono else 'every card, counted once for each element it shows', ' | '.join(cols), '---|' * len(cols))
            for cat in sorted(m, key=lambda k: (k is None, k or 0)):
                md += '| %s | %s |\n' % (CATS.get(cat, '?'), ' | '.join(str(m[cat][e] or '') for e in cols))
    rel = collections.Counter()
    md += '\n### Which element a force aims at, against the elements on its card\n\n| Card | Card elements | Category | Aims at | Turns into |\n|---|---|---|---|---|\n'
    for r in rows:
        if r['face'] == 'force' and (r['target'] or r['into']):
            md += '| %s (%s) | %s | %s | %s | %s |\n' % (r['card'], r['name'], ', '.join(r['els']), CATS[r['cat']], ', '.join(r['target']) or '—', r['into'] or '—')
    if '--md' in sys.argv: open(sys.argv[sys.argv.index('--md') + 1], 'w').write(md)
    else: print(md)
