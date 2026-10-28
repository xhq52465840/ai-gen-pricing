"""Check every internal link in the built site: python3 tools/check_links.py
Resolves each href/src/meta-refresh/JSON "src"/"page" against the page URL and confirms the target file exists.
The site is served under BASE (GitHub Pages project path); every internal URL must be root-relative and start with BASE."""
import os, re, sys, json
from urllib.parse import urljoin, urlsplit, unquote
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.environ.get('BASE_PATH', '/ai-gen-pricing/')
SKIP_DIRS = {'.git', 'src', 'tools', 'node_modules'}
PAT = re.compile(r'''\b(?:href|src|action)="([^"]*)"|url=([^"'>;\s]+)|"(?:page|model_url)":\s*"([^"]+)"''')
EXT = ('http:', 'https:', 'mailto:', 'tel:', 'data:', 'javascript:', '//')
OWN = ('https://xhq52465840.github.io',)

def exists(p):
    if not p.startswith(BASE): return False
    f = os.path.join(ROOT, unquote(p[len(BASE):]))
    if p.endswith('/') or os.path.isdir(f): return os.path.isfile(os.path.join(f, 'index.html'))
    return os.path.isfile(f)

broken, relative, outside, n, pages = [], [], [], 0, 0
for d, dirs, files in os.walk(ROOT):
    dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
    for fn in files:
        if not fn.endswith(('.html', '.xml', '.txt')): continue
        pages += 1
        fp = os.path.join(d, fn); rp = os.path.relpath(fp, ROOT).replace(os.sep, '/')
        url = BASE + (rp[:-len('index.html')] if fn == 'index.html' else rp)
        txt = open(fp, encoding='utf-8').read()
        found = [next(g for g in m.groups() if g is not None) for m in PAT.finditer(txt)]
        if fn.endswith(('.xml', '.txt')):
            found = re.findall(r'https://xhq52465840\.github\.io[^\s<"]*', txt)
        for u in found:
            if not u or u.startswith('#') or '{' in u: continue
            for o in OWN:
                if u.startswith(o): u = u[len(o):] or '/'
            if u.startswith(EXT): continue
            n += 1
            if not u.startswith('/'): relative.append((url, u)); continue
            path = urlsplit(urljoin(url, u)).path
            if not path.startswith(BASE): outside.append((url, u)); continue
            if path.endswith('/') and path == BASE + 'models/' and '"model_url"' in txt: pass
            if not exists(path): broken.append((url, u, path))
print(f'{pages} files, {n} internal URLs checked')
for x in relative: print('RELATIVE', *x)
for x in outside: print('OUTSIDE-BASE', *x)
for x in broken: print('BROKEN  ', *x)
print(f'broken={len(broken)} relative={len(relative)} outside_base={len(outside)}')
sys.exit(1 if broken or relative or outside else 0)
