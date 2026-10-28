#!/usr/bin/env python3
"""i18n + calculator checker for the built GenCost site.

For every language folder it checks:
  * parity     - the same set of pages exists in every language as in /en/
  * html lang  - <html lang> matches the folder (en, zh-CN, es, de, ja, pt-BR)
  * hreflang   - all 6 languages + x-default, targets exist and link back (reciprocity), canonical = self, x-default = en
  * switcher   - header and footer language menus point to the same page in each language
  * sitemap    - every indexable page is listed with the same alternates as the page
  * leftover English (non-English pages) - visible text, <title>, meta description, OG tags, aria-label/title/alt attributes,
                 and JS-rendered calculator text after exercising every model, both billing modes and edge inputs (headless Chrome).
                 zh/ja: any Latin word not in the allowlist (brand, model, plan and unit names); es/de/pt: English function words.
  * math       - window.GC_compute in every language against the Python mirror (src/build.py) on random scenarios.
Usage: python3 tools/check_i18n.py --base http://127.0.0.1:8090/ai-gen-pricing [--math 40] [--no-browser] [-v]
"""
import argparse, glob, html as H, json, os, random, re, sys
from collections import defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))
import data as D, i18n as I
import build as B
LANG_HTML = I.HTML_LANG
SITE = B.ORIGIN + B.BASE
AL = json.load(open(os.path.join(ROOT, 'tools', 'i18n_allowlist.json')))

def pages(lang):
    out = set()
    for f in glob.glob(os.path.join(ROOT, lang, '**', 'index.html'), recursive=True):
        out.add(os.path.relpath(f, os.path.join(ROOT, lang)).replace(os.sep, '/').replace('index.html', ''))
    return out

def brand_words():
    w = set()
    for P in D.PLATFORMS.values():
        w |= set(re.findall(r'[A-Za-z]+', P['name'] + ' ' + P['mono']))
        for pl in P['plans']: w |= set(re.findall(r'[A-Za-z]+', pl['name']))
    for J in D.JOBS.values(): w |= set(re.findall(r'[A-Za-z]+', J['model'] + ' ' + J['maker']))
    return w

class English:
    def __init__(self):
        self.words = (set(AL['latin_ok']) | brand_words()) - {'Units', 'Credits'}
        self.cjk_extra = {'Units', 'Credits'}
        self.stop = set(AL['english_markers'])
    def find(self, lang, s):
        s = H.unescape(s)
        s = re.sub(r'https?://\S+|[\w.+-]+@[\w-]+\.[\w.]+|[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.(?:ai|com|io|dev|app|org)(?![A-Za-z])', ' ', s)
        for ph in AL['phrases']: s = s.replace(ph, ' ')
        words = re.findall(r"[A-Za-z][A-Za-z'’]*", s)
        if lang in ('zh', 'ja'):
            return [x for x in words if x not in self.words and not re.fullmatch(r'\d*[KkMps]|[A-Z]\d*', x)]
        ok = set(AL['not_english_in'].get(lang, []))
        return [x for x in words if x.lower() in self.stop and x not in self.words and x not in ok]

def static_checks(report):
    en = pages('en'); per = {l: pages(l) for l in LANG_HTML}
    for l in LANG_HTML:
        if l == 'en': continue
        for suf in sorted(en - per[l]): report['parity'].append(f'missing {l}/{suf}')
        for suf in sorted(per[l] - en): report['parity'].append(f'extra {l}/{suf}')
    sm = open(os.path.join(ROOT, 'sitemap.xml'), encoding='utf-8').read()
    sm_urls = dict(re.findall(r'<url><loc>([^<]+)</loc>(.*?)</url>', sm.replace('\n', ''), re.S))
    n_sm = 0
    for l in LANG_HTML:
        for suf in sorted(per[l]):
            s = open(os.path.join(ROOT, l, suf, 'index.html'), encoding='utf-8').read(); me = SITE + l + '/' + suf; page = f'{l}/{suf}'
            m = re.search(r'<html lang="([^"]+)"', s)
            if not m or m.group(1) != LANG_HTML[l]: report['html_lang'].append(f'{page}: lang={m.group(1) if m else None}')
            if 'name="robots" content="noindex' in s: continue
            alts = dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)">', s))
            can = re.search(r'<link rel="canonical" href="([^"]+)">', s)
            if not can or can.group(1) != me: report['hreflang'].append(f'{page}: canonical {can.group(1) if can else None}')
            for h in list(LANG_HTML.values()) + ['x-default']:
                if h not in alts: report['hreflang'].append(f'{page}: no hreflang {h}')
            if alts.get(LANG_HTML[l]) != me: report['hreflang'].append(f'{page}: self hreflang {alts.get(LANG_HTML[l])}')
            if alts.get('x-default') != alts.get('en'): report['hreflang'].append(f'{page}: x-default != en')
            for h, u in alts.items():
                if h == 'x-default': continue
                p2 = u.replace(SITE, '')
                f2 = os.path.join(ROOT, p2, 'index.html')
                if not os.path.isfile(f2): report['hreflang'].append(f'{page}: hreflang {h} -> missing {p2}'); continue
                back = dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)">', open(f2, encoding='utf-8').read()))
                if back.get(LANG_HTML[l]) != me: report['hreflang'].append(f'{page}: not reciprocal from {p2}')
            exp = {k: v.replace(B.ORIGIN, '') for k, v in alts.items() if k != 'x-default'}
            hm = re.search(r'<details class="dd">(.*?)</details>', s, re.S)
            fm = re.findall(r'<nav aria-label="[^"]+">(.*?)</nav>', s.split('<footer>')[-1], re.S)
            blocks = [('header', hm.group(1) if hm else ''), ('footer', fm[-1] if fm else '')]
            for name, blk in blocks:
                got = dict((b, a) for a, b in re.findall(r'<a href="([^"]+)" hreflang="([^"]+)"', blk))
                if set(got) != set(exp): report['switcher'].append(f'{page}: {name} switcher languages {sorted(got)}')
                for h, u in got.items():
                    if exp.get(h) != u: report['switcher'].append(f'{page}: {name} switcher {h} -> {u} (expected {exp.get(h)})')
            if me not in sm_urls: report['sitemap'].append(f'{page}: not in sitemap')
            else:
                n_sm += 1
                smalt = dict(re.findall(r'hreflang="([^"]+)" href="([^"]+)"', sm_urls[me]))
                if smalt != alts: report['sitemap'].append(f'{page}: sitemap alternates differ')
    if n_sm != len(sm_urls): report['sitemap'].append(f'sitemap has {len(sm_urls)} URLs but {n_sm} indexable pages')
    return per

JS_COLLECT = r"""() => {
  const lang = document.documentElement.lang; const out = [];
  const foreign = el => { const c = el.closest('[lang]'); return c && c.getAttribute('lang') !== lang; };
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n; while ((n = w.nextNode())) {
    const p = n.parentElement; if (!p || ['SCRIPT','STYLE'].includes(p.tagName)) continue;
    const t = n.nodeValue.trim(); if (!t || foreign(p) || p.closest('[aria-hidden="true"]')) continue; out.push(['text', t, p.tagName.toLowerCase()]);
  }
  document.querySelectorAll('[title],[alt],[aria-label],[placeholder]').forEach(e => {
    if (foreign(e)) return;
    for (const a of ['title','alt','aria-label','placeholder']) if (e.hasAttribute(a) && e.getAttribute(a).trim()) out.push(['@' + a, e.getAttribute(a), e.tagName.toLowerCase()]);
  });
  document.querySelectorAll('optgroup').forEach(e => out.push(['@label', e.label, 'optgroup']));
  out.push(['title', document.title, 'head']);
  const m = document.querySelector('meta[name=description]'); if (m) out.push(['meta', m.content, 'description']);
  for (const k of ['og:title','og:description']) { const x = document.querySelector('meta[property="' + k + '"]'); if (x) out.push(['meta', x.content, k]); }
  return out;
}"""
JS_EXERCISE = r"""async () => {
  const sel = document.getElementById('c-job'); if (!sel) return [];
  const got = []; const fire = (e, t) => e.dispatchEvent(new Event(t || 'change', {bubbles: true}));
  const grab = w => { got.push(['js-rendered', document.getElementById('o-rows').innerText, w]); got.push(['js-rendered', document.getElementById('o-best').innerText, w]); };
  const bills = [...document.querySelectorAll('input[name=bill]')];
  for (const o of sel.options) {
    sel.value = o.value; fire(sel);
    for (const b of bills) { b.checked = true; fire(b);
      for (const [s, q, k] of [['3', '1', '100'], ['12', '5000', '20']]) {
        const S = document.getElementById('c-secs'), Q = document.getElementById('c-qty'), K = document.getElementById('c-keep');
        S.value = s; Q.value = q; K.value = k; fire(S, 'input'); fire(Q, 'input'); fire(K, 'input'); grab(o.value);
      }
    }
  }
  return got;
}"""

def py_compute(job, sec, qty, keep, bill):
    vid = D.JOBS[job]['type'] == 'video'
    if not vid: sec = 1
    import math
    gen = math.ceil(qty * 100 / keep - 1e-9)
    rows = []
    for o in D.OFFERS:
        if o['job'] != job: continue
        if B.is_credit(o):
            cpo = B.credits_out(o, sec); need = cpo * gen
            ps = sorted(B.plans_of(o['plat']), key=lambda p: p['credits'])
            pick = next((p for p in ps if p['credits'] >= need - 1e-9), None)
            pl = pick or ps[-1]; price = B.plan_price(pl, bill)
            rows.append((o['plat'], o['unit'], cpo * price / pl['credits'], price if pick else None))
        else:
            per = B.payg_out(o, sec); rows.append((o['plat'], o['unit'], per, per * gen))
    return sorted(rows, key=lambda r: (r[3] is None, r[3] if r[3] is not None else 0, r[2]))

def browser_checks(report, base, per, math_n, verbose):
    from playwright.sync_api import sync_playwright
    E = English()
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True)
        pg = b.new_page()
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        for l in LANG_HTML:
            for suf in sorted(per[l]):
                page = f'{l}/{suf}'; errs.clear()
                pg.goto(f'{base}/{page}', wait_until='load')
                calc = pg.query_selector('#c-job')
                if calc:
                    try: pg.wait_for_function('window.GC_ready===true', timeout=15000)
                    except Exception: report['js'].append(f'{page}: calculator did not initialise')
                if l == 'en':
                    if errs: report['js'].append(f'{page}: JS error {errs[0][:120]}')
                    continue
                items = pg.evaluate(JS_COLLECT)
                if calc and (suf == '' or suf.startswith('models/kling-4-1080p')): items += pg.evaluate(JS_EXERCISE)
                elif calc: items += [['js-rendered', pg.inner_text('#o-rows'), 'default']]
                if errs: report['js'].append(f'{page}: JS error {errs[0][:120]}')
                seen = set()
                for kind, txt, where in items:
                    for line in (txt or '').split('\n'):
                        bad = E.find(l, line)
                        if bad:
                            k = line.strip()[:160]
                            if k in seen: continue
                            seen.add(k); report['english'].append(f'{page} [{kind} {where}] {" ".join(dict.fromkeys(bad))} :: {k}')
        # root 404 + chooser
        for f in ('404.html', ''):
            errs.clear(); pg.goto(f'{base}/{f}' if f else f'{base}/', wait_until='load')
            if errs: report['js'].append(f'root {f or "index"}: JS error {errs[0][:120]}')
        if math_n:
            rnd = random.Random(7)
            for l in LANG_HTML:
                pg.goto(f'{base}/{l}/'); pg.wait_for_function('window.GC_ready===true', timeout=15000)
                cases = []
                for i in range(math_n):
                    j = rnd.choice(D.JOB_ORDER)
                    cases.append([j, rnd.randint(1, 20), rnd.choice([1, 3, 10, 30, 100, 400, 2000]), rnd.choice([10, 25, 33, 50, 80, 100]), rnd.choice(['monthly', 'annual'])])
                res = pg.evaluate('cs=>cs.map(c=>GC_compute(c[0],c[1],c[2],c[3],c[4]))', cases)
                for c, js in zip(cases, res):
                    py = py_compute(*c)
                    ok = len(py) == len(js) and all(a[0] == x[0] and abs(a[2] - x[2]) < 1e-6 and ((a[3] is None and x[3] is None) or (a[3] is not None and x[3] is not None and abs(a[3] - x[3]) < 1e-6)) for a, x in zip(py, js))
                    report['math_cases'] += 1
                    if not ok: report['math'].append(f'{l}: {c} python={py[:3]} js={js[:3]}')
        b.close()

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--base', default='http://127.0.0.1:8090/ai-gen-pricing'); ap.add_argument('--math', type=int, default=40)
    ap.add_argument('--no-browser', action='store_true'); ap.add_argument('--json', default='/tmp/gencost_i18n.json'); ap.add_argument('-v', action='store_true')
    a = ap.parse_args()
    report = defaultdict(list); report['math_cases'] = 0
    per = static_checks(report)
    if not a.no_browser: browser_checks(report, a.base, per, a.math, a.v)
    counts = {l: len(per[l]) for l in LANG_HTML}
    keys = ['parity', 'html_lang', 'hreflang', 'switcher', 'sitemap', 'english', 'js', 'math']
    json.dump({k: report[k] for k in keys} | {'pages': counts, 'math_cases': report['math_cases']}, open(a.json, 'w'), ensure_ascii=False, indent=1)
    print('pages per locale:', counts)
    total = 0
    for k in keys:
        n = len(report[k]); total += n
        print(f'{k:10s} {n}')
        for x in report[k][: (10**6 if a.v else 8)]: print('   ', x)
    print(f'math scenarios checked: {report["math_cases"]}')
    print('TOTAL ISSUES', total)
    sys.exit(1 if total else 0)
