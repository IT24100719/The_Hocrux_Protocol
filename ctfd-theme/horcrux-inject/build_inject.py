#!/usr/bin/env python3
"""Assemble the Horcrux theme-header (CSS) and theme-footer (scenes+sigils+engine)
and push them into CTFd's theme_header / theme_footer config via the admin API.
Edit horcrux.css / horcrux.engine.js / ../horcrux-preview/scenes.json /
../horcrux-preview/sigils/*.svg, then re-run this to redeploy."""
import base64, json, os, re, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PREVIEW = os.path.normpath(os.path.join(HERE, '..', 'horcrux-preview'))
BASE = os.environ.get('CTFD_URL', 'http://127.0.0.1:8000')
TOKEN = os.environ.get('CTFD_TOKEN', '')
if not TOKEN:
    print('Set CTFD_TOKEN env var to the admin API token.'); sys.exit(1)
H = {'Authorization': 'Token ' + TOKEN, 'Content-Type': 'application/json'}

def api(method, path, data=None):
    req = urllib.request.Request(BASE + path,
        data=json.dumps(data).encode() if data is not None else None, headers=H, method=method)
    try:
        with urllib.request.urlopen(req) as r: return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]

def sanitize_sig(svg):
    svg = re.sub(r'<path d="M0 0h[\d.]+v[\d.]+H0z"[^>]*/>', '', svg)   # drop bg rect
    svg = svg.replace('fill="#fff"', 'fill="currentColor"')
    svg = re.sub(r'\s(width|height)="[^"]*"', '', svg)
    svg = re.sub(r'<svg ', '<svg class="hx-sig" fill="currentColor" ', svg, count=1)
    return re.sub(r'>\s+<', '><', svg).strip()

# sigils -> {HX-0N: svg}
SIG = {}
for n in range(1, 7):
    p = os.path.join(PREVIEW, 'sigils', 'hx0%d.svg' % n)
    SIG['HX-0%d' % n] = sanitize_sig(open(p, encoding='utf-8').read())

SCENES = json.load(open(os.path.join(PREVIEW, 'scenes.json'), encoding='utf-8'))
CSS = open(os.path.join(HERE, 'horcrux.css'), encoding='utf-8').read()
ENGINE = open(os.path.join(HERE, 'horcrux.engine.js'), encoding='utf-8').read()
# Seal shown on locked ("sealed") cards. Swap it by dropping your OWN (or
# licensed) image in here as seal.svg / seal.png / seal.jpg / seal.webp — see
# SEAL.md. SVG is inlined; a raster is base64 data-URI'd into an <img>.
def load_seal():
    for ext in ('svg', 'png', 'jpg', 'jpeg', 'webp', 'gif'):
        p = os.path.join(HERE, 'seal.' + ext)
        if not os.path.exists(p):
            continue
        if ext == 'svg':
            return open(p, encoding='utf-8').read().strip()
        mime = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png',
                'webp': 'image/webp', 'gif': 'image/gif'}[ext]
        b64 = base64.b64encode(open(p, 'rb').read()).decode()
        return '<img class="hxc-seal-svg" alt="" src="data:%s;base64,%s">' % (mime, b64)
    return ''

SEAL = load_seal()

header = '<style>\n' + CSS + '\n</style>'
footer = ('<script>\nwindow.HX_SCENES=' + json.dumps(SCENES, ensure_ascii=False) +
          ';\nwindow.HX_SIG=' + json.dumps(SIG, ensure_ascii=False) +
          ';\nwindow.HX_SEAL=' + json.dumps(SEAL) + ';\n' + ENGINE + '\n</script>')

print('header %d bytes | footer %d bytes | sigils %d' % (len(header), len(footer), len(SIG)))

st, r = api('PATCH', '/api/v1/configs', {'theme_header': header, 'theme_footer': footer})
print('set configs:', st, (r.get('success') if isinstance(r, dict) else r))
# verify
for k in ('theme_header', 'theme_footer'):
    st, g = api('GET', '/api/v1/configs/' + k)
    v = g['data']['value'] if isinstance(g, dict) and g.get('success') and g.get('data') else ''
    print('  %s stored: %d bytes' % (k, len(v or '')))
