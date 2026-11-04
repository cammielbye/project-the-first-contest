import os
FD = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fonts'))
def local_fonts():
    css = ''
    for w in (500, 600, 700):
        for st in ('normal', 'italic'):
            css += "@font-face{font-family:'Cormorant Garamond';font-style:%s;font-weight:%d;src:url('file://%s/package/files/cormorant-garamond-latin-%d-%s.woff2') format('woff2')}\n" % (st, w, FD, w, st)
    for w in (400, 500, 600):
        css += "@font-face{font-family:'IBM Plex Mono';font-style:normal;font-weight:%d;src:url('file://%s/plex/package/files/ibm-plex-mono-latin-%d-normal.woff2') format('woff2')}\n" % (w, FD, w)
    return '<style>' + css + '</style>'
