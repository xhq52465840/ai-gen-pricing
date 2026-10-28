# -*- coding: utf-8 -*-
"""Static site generator for GenCost. Usage: python3 src/build.py   (BASE_PATH env overrides the URL base, default /ai-gen-pricing/)"""
import os, sys, json, math, shutil, html as H
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data as D, i18n as I, facts as FX
from i18n import LANGS, tr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.environ.get('BASE_PATH', '/ai-gen-pricing/')
ORIGIN = os.environ.get('SITE_ORIGIN', 'https://xhq52465840.github.io')
REPO = 'https://github.com/xhq52465840/ai-gen-pricing'
CSSV = '3'
LI = {l: i for i, l in enumerate(LANGS)}
e = lambda s: H.escape(str(s), quote=True)

def U(lang, path=''):
    return BASE + (lang + '/' if lang else '') + path

# ------------------------------------------------------------------ formatting
def num(lang, x, dec):
    s = f'{x + (5e-9 if x >= 0 else -5e-9):,.{dec}f}'
    if lang in ('es', 'de', 'pt'):
        s = s.replace(',', '\x00').replace('.', ',').replace('\x00', '.')
    return s
def usd_dec(x):
    if x >= 100: return 0
    if x >= 1: return 2
    if x >= 0.1: return 3
    if x >= 0.01: return 4
    return 5
def trim(lang, s):
    d = ',' if lang in ('es', 'de', 'pt') else '.'
    if d not in s: return s
    a, b = s.split(d)
    b = b.rstrip('0')
    b = b + '0' * max(0, 2 - len(b))
    return a + d + b
def usd(lang, x, dec=None):
    dec = usd_dec(x) if dec is None else dec
    s = trim(lang, num(lang, x, dec)) if dec > 2 else num(lang, x, dec)
    if lang in ('es', 'de'): return s + '\u00a0$'
    if lang == 'pt': return 'US$\u00a0' + s
    return '$' + s
def n_fmt(lang, x):
    if abs(x - round(x)) < 1e-9: return num(lang, x, 0)
    t = num(lang, x, 2); d = ',' if lang in ('es', 'de', 'pt') else '.'
    return t.rstrip('0').rstrip(d)

# ------------------------------------------------------------------ pricing maths (mirrored in app.js)
def plans_of(p): return [pl for pl in D.PLATFORMS[p]['plans'] if not pl.get('limited')]
def plan_price(pl, billing):
    if billing == 'annual': return pl['annual'] if pl['annual'] is not None else pl['monthly']
    return pl['monthly'] if pl['monthly'] is not None else pl['annual']
def best_plan(p):
    return min(plans_of(p), key=lambda pl: plan_price(pl, 'annual') / pl['credits'])
def small_plan(p):
    return min(plans_of(p), key=lambda pl: plan_price(pl, 'monthly'))
def is_credit(o): return o['unit'].startswith('cr_')
def credits_out(o, sec):
    u, v = o['unit'], o['v']
    return v * sec if u == 'cr_s' else v * sec / o['per'] if u == 'cr_clip' else v
def payg_out(o, sec):
    u, v = o['unit'], o['v']
    x = v * sec if u == 'usd_s' else v * sec / o['per'] if u == 'usd_clip' else v
    return max(x, o.get('min_usd', 0))
def eff(o, sec, mode='best'):
    """$ per output. mode best|small"""
    if not is_credit(o): return payg_out(o, sec)
    pl = best_plan(o['plat']) if mode == 'best' else small_plan(o['plat'])
    price = plan_price(pl, 'annual' if mode == 'best' else 'monthly')
    return credits_out(o, sec) * price / pl['credits']
def job_sec(j): return D.JOBS[j].get('sec', 1) if D.JOBS[j]['type'] == 'video' else 1
def offers(job): return sorted([o for o in D.OFFERS if o['job'] == job], key=lambda o: eff(o, job_sec(job)))
def best_by_plat(job):
    out = {}
    for o in offers(job):
        out.setdefault(o['plat'], o)
    return out
def rate(o, job, mode='best'):
    return eff(o, job_sec(job), mode) / job_sec(job)

# ------------------------------------------------------------------ text helpers
def jname(lang, j): return D.JOBS[j]['model']
def jset(lang, j): return I.setting(lang, D.JOBS[j]['setting'])
def unit_word(lang, j): return tr(lang, 'u_second' if D.JOBS[j]['type'] == 'video' else 'u_image')
def per_unit(lang, j): return tr(lang, 'per_s' if D.JOBS[j]['type'] == 'video' else 'per_img')
def rate_txt(lang, o, j, mode='best'): return usd(lang, rate(o, j, mode)) + per_unit(lang, j)
def pname(p): return D.PLATFORMS[p]['name']
def cw(lang, p): return I.cword(lang, D.PLATFORMS[p]['credit'])
def listed(lang, o):
    u, v, j = o['unit'], o['v'], o['job']
    pre = '~' if o.get('approx') else ''
    if u == 'usd_s': return pre + usd(lang, v) + tr(lang, 'per_s')
    if u == 'usd_img': return pre + usd(lang, v) + tr(lang, 'per_img')
    if u == 'usd_clip': return pre + usd(lang, v) + ' · ' + tr(lang, 'n_sec_clip', n=o['per'])
    uu = tr(lang, 'u_second') if u == 'cr_s' else tr(lang, 'u_image') if u == 'cr_img' else tr(lang, 'n_sec_clip', n=o['per'])
    return pre + tr(lang, 'credits_per', v=n_fmt(lang, v), c=cw(lang, o['plat']), u=uu)
def how(lang, o):
    p = D.PLATFORMS[o['plat']]
    if not is_credit(o): return tr(lang, 'payg_api') if p['kind'] != 'app' else tr(lang, 'payg')
    return tr(lang, 'channel_app')
def note(lang, k): return FX.NOTES[k][LI[lang]]
def notes(lang, o, sec=None):
    out = []
    if o.get('note'): out.append(e(note(lang, o['note'])))
    if o.get('calc'): out.append(e(tr(lang, 'derived') + ': ' + note(lang, o['calc'])))
    if o.get('approx'): out.append(e(tr(lang, 'approx')))
    if o['unit'].endswith('_clip') and sec is not None and sec != o['per']: out.append(e(tr(lang, 'scaled')))
    if o.get('promo'): out.append('<span class="badge promo">' + e(note(lang, o['promo'])) + '</span>')
    return out
def tile(p, sm=False):
    P = D.PLATFORMS[p]
    return f'<span class="tile{" sm" if sm else ""}" style="background:{P["color"]};color:{P["fg"]}" aria-hidden="true">{e(P["mono"])}</span>'
def src_link(lang, url):
    return f'<a class="lnk small" href="{e(url)}" rel="nofollow noopener" target="_blank">{e(tr(lang, "source"))}</a> <span class="muted small">· {e(I.DATE[lang])}</span>'
def fact_li(lang, k):
    url, t = FX.FACTS[k]
    return f'<li>{e(t[LI[lang]])} <a href="{e(url)}" rel="nofollow noopener" target="_blank">{e(tr(lang, "source"))}</a></li>'

# ------------------------------------------------------------------ layout
NAV = [('nav_calc', ''), ('nav_models', 'models/'), ('nav_platforms', 'platforms/'), ('nav_failed', 'failed-generations/'), ('nav_about', 'about/')]
def head(lang, path, title, desc, noindex=False):
    alts = ''.join(f'<link rel="alternate" hreflang="{I.HTML_LANG[l]}" href="{ORIGIN}{U(l, path)}">' for l in LANGS)
    alts += f'<link rel="alternate" hreflang="x-default" href="{ORIGIN}{U("en", path)}">'
    rob = '<meta name="robots" content="noindex">' if noindex else ''
    return f'''<!doctype html>
<html lang="{I.HTML_LANG[lang]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{rob}<link rel="canonical" href="{ORIGIN}{U(lang, path)}">
{alts}
<meta property="og:type" content="website">
<meta property="og:site_name" content="GenCost">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{ORIGIN}{U(lang, path)}">
<meta property="og:locale" content="{I.OG_LOCALE[lang]}">
<meta name="twitter:card" content="summary">
<link rel="icon" href="{BASE}favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{BASE}assets/style.css?v={CSSV}">
</head>
<body>
<a class="skip" href="#main">{e(tr(lang, "skip"))}</a>
'''
def header(lang, path):
    items = ''.join(f'<a href="{U(lang, p)}"{" aria-current=\"page\"" if p == path else ""}>{e(tr(lang, k))}</a>' for k, p in NAV)
    langs = ''.join(f'<a href="{U(l, path)}" hreflang="{I.HTML_LANG[l]}" lang="{I.HTML_LANG[l]}"{" aria-current=\"true\"" if l == lang else ""}>{e(I.LNAME[l])}</a>' for l in LANGS)
    return f'''<header class="nav"><div class="wrap">
<a class="logo" href="{U(lang)}"><span class="mark" aria-hidden="true">$</span>GenCost</a>
<nav class="menu" aria-label="{e(tr(lang, "menu"))}">{items}</nav>
<details class="dd"><summary aria-label="{e(tr(lang, "language"))}">{e(I.LNAME[lang])} ▾</summary><div class="ddm">{langs}</div></details>
</div></header>
<main id="main">
'''
def footer(lang, path):
    items = ''.join(f'<a href="{U(lang, p)}">{e(tr(lang, k))}</a>' for k, p in NAV) + f'<a href="{U(lang, "privacy/")}">{e(tr(lang, "privacy"))}</a>'
    langs = ''.join(f'<a href="{U(l, path)}" hreflang="{I.HTML_LANG[l]}" lang="{I.HTML_LANG[l]}">{e(I.LNAME[l])}</a>' for l in LANGS)
    return f'''</main>
<footer><div class="wrap"><div class="cols">
<div><a class="logo" href="{U(lang)}"><span class="mark" aria-hidden="true">$</span>GenCost</a>
<p>{e(tr(lang, "footer_note"))}</p>
<p>{e(tr(lang, "checked"))}: {e(I.DATE[lang])} · <a class="lnk" href="{REPO}" rel="noopener">{e(tr(lang, "repo"))}</a></p></div>
<div><nav aria-label="{e(tr(lang, "menu"))}">{items}</nav>
<nav aria-label="{e(tr(lang, "language"))}">{langs}</nav></div>
</div></div></footer>
</body>
</html>
'''
PAGES = []  # (lang, path)
def write(lang, path, title, desc, body, noindex=False, extra=''):
    fn = os.path.join(ROOT, lang, path, 'index.html')
    os.makedirs(os.path.dirname(fn), exist_ok=True)
    with open(fn, 'w', encoding='utf-8') as f:
        f.write(head(lang, path, title, desc, noindex) + header(lang, path) + body + footer(lang, path).replace('</body>', extra + '</body>'))
    if not noindex and lang == 'en': PAGES.append(path)
def crumbs(lang, *pairs):
    out = [f'<a href="{U(lang)}">{e(tr(lang, "home"))}</a>']
    for label, p in pairs:
        out.append(f'<a href="{U(lang, p)}">{e(label)}</a>' if p is not None else e(label))
    return '<div class="crumbs">' + ' / '.join(out) + '</div>'

# ------------------------------------------------------------------ calculator
def calc_data(lang):
    jobs = {j: dict(m=jname(lang, j), s=jset(lang, j), t=D.JOBS[j]['type'], sec=D.JOBS[j].get('sec', 1)) for j in D.JOB_ORDER}
    offs = []
    for o in D.OFFERS:
        P = D.PLATFORMS[o['plat']]
        d = dict(j=o['job'], p=o['plat'], n=P['name'], u=o['unit'], v=o['v'], per=o.get('per'), min=o.get('min_usd', 0),
                 src=o['src'], how=how(lang, o), ap=bool(o.get('approx')), c=cw(lang, o['plat']) if is_credit(o) else '',
                 nt=' · '.join(H.unescape(x) for x in notes(lang, o) if not x.startswith('<')),
                 pr=note(lang, o['promo']) if o.get('promo') else '', page=U(lang, o['plat'] + '/pricing/'))
        if is_credit(o):
            d['plans'] = [dict(n=pl['name'], m=pl['monthly'], a=pl['annual'], cr=pl['credits']) for pl in plans_of(o['plat'])]
        offs.append(d)
    keys = ['per_s', 'per_img', 'payg', 'exceeds', 'scaled', 'approx', 'generated', 'cheapest_now', 'minimum', 'annual_only', 'monthly_only',
            'you_pay_plan', 'leftover', 'source', 'plan_word', 'clip_cost', 'see_pricing']
    S = {k: tr(lang, k) for k in keys}
    S['fmt'] = lang
    return dict(jobs=jobs, offers=offs, S=S, model_url=U(lang, 'models/'))

def calc_html(lang, job='kling-4-1080p'):
    vid = ''.join(f'<option value="{j}"{" selected" if j == job else ""}>{e(jname(lang, j))} · {e(jset(lang, j))}</option>' for j in D.JOB_ORDER if D.JOBS[j]['type'] == 'video')
    img = ''.join(f'<option value="{j}"{" selected" if j == job else ""}>{e(jname(lang, j))} · {e(jset(lang, j))}</option>' for j in D.JOB_ORDER if D.JOBS[j]['type'] == 'image')
    sec = D.JOBS[job].get('sec', 5)
    return f'''<div class="calc" id="calc">
<form class="card cs" onsubmit="return false" aria-label="{e(tr(lang, "calc_h"))}">
<div class="field"><label class="label" for="c-job">{e(tr(lang, "f_model"))}</label>
<div class="input"><select id="c-job"><optgroup label="{e(tr(lang, "f_video"))}">{vid}</optgroup><optgroup label="{e(tr(lang, "f_image"))}">{img}</optgroup></select></div></div>
<div class="field" id="f-secs"><label class="label" for="c-secs">{e(tr(lang, "f_secs"))}</label>
<div class="input"><input id="c-secs" type="number" min="1" max="60" step="1" value="{sec}" inputmode="numeric"><span class="suf">s</span></div></div>
<div class="field"><label class="label" for="c-qty"><span id="l-clips">{e(tr(lang, "f_clips"))}</span><span id="l-imgs" hidden>{e(tr(lang, "f_images"))}</span></label>
<div class="input"><input id="c-qty" type="number" min="1" max="100000" step="1" value="30" inputmode="numeric"></div></div>
<div class="field"><label class="label" for="c-keep">{e(tr(lang, "f_keep"))}</label>
<div class="input"><input id="c-keep" type="number" min="5" max="100" step="5" value="50" inputmode="numeric"><span class="suf">%</span></div></div>
<div class="field"><span class="label" id="l-bill">{e(tr(lang, "f_billing"))}</span>
<div class="seg" role="radiogroup" aria-labelledby="l-bill"><label><input type="radio" name="bill" value="monthly" checked><span>{e(tr(lang, "monthly"))}</span></label><label><input type="radio" name="bill" value="annual"><span>{e(tr(lang, "annual"))}</span></label></div></div>
<a class="lnk small" id="c-model" href="{U(lang, "models/" + job + "/")}">{e(tr(lang, "try_calc"))}</a>
</form>
<div class="card res" aria-live="polite">
<div class="sum"><div><span>{e(tr(lang, "generated"))}</span><b class="num" id="o-gen">–</b></div><div><span>{e(tr(lang, "cheapest_now"))}</span><b id="o-best">–</b></div></div>
<div class="tablewrap"><table><thead><tr><th>{e(tr(lang, "th_platform"))}</th><th>{e(tr(lang, "th_how"))}</th><th class="n">{e(tr(lang, "th_rate"))}</th><th class="n">{e(tr(lang, "th_unit"))}</th><th class="n">{e(tr(lang, "th_month"))}</th><th>{e(tr(lang, "th_src"))}</th></tr></thead>
<tbody id="o-rows"><tr><td colspan="6"><noscript>{e(tr(lang, "no_js"))}</noscript></td></tr></tbody></table></div>
<p class="note">{e(tr(lang, "calc_note"))}</p>
</div></div>
<script id="gc-data" type="application/json">{json.dumps(calc_data(lang), ensure_ascii=False).replace("</", "<\\/")}</script>
'''
CALC_JS = f'<script src="{BASE}assets/app.js?v={CSSV}" defer></script>'

# ------------------------------------------------------------------ pages
def offer_table(lang, job, highlight=None):
    sec = job_sec(job); vid = D.JOBS[job]['type'] == 'video'
    rows = ''
    offs = offers(job)
    for i, o in enumerate(offs):
        cls = ' class="top"' if i == 0 else (' class="hl"' if o['plat'] == highlight else '')
        small = ''
        if is_credit(o):
            bp = best_plan(o['plat']); sp = small_plan(o['plat'])
            small = f'<small>{e(bp["name"])}</small>'
            if sp is not bp: small += f'<small>{e(sp["name"])}, {e(tr(lang, "monthly"))}: {rate_txt(lang, o, job, "small")}</small>'
        badge = f' <span class="badge best">{e(tr(lang, "is_cheapest"))}</span>' if i == 0 else ''
        per = f'<td class="n num">{usd(lang, eff(o, sec))}</td>' if vid else ''
        nt = notes(lang, o, sec)
        rows += f'<tr{cls}><td>{tile(o["plat"], True)}<a href="{U(lang, o["plat"] + "/pricing/")}"><b>{e(pname(o["plat"]))}</b></a>{badge}</td><td>{e(how(lang, o))}</td><td class="num">{e(listed(lang, o))}</td><td class="n num"><b>{rate_txt(lang, o, job)}</b>{small}</td>{per}<td class="small">{"<br>".join(nt)}{"<br>" if nt else ""}{src_link(lang, o["src"])}</td></tr>'
    perh = f'<th class="n">{e(tr(lang, "clip_cost", n=sec))}</th>' if vid else ''
    return f'<div class="tablewrap"><table><thead><tr><th>{e(tr(lang, "th_platform"))}</th><th>{e(tr(lang, "th_how"))}</th><th>{e(tr(lang, "th_listed"))}</th><th class="n">{e(tr(lang, "th_rate"))}</th>{perh}<th>{e(tr(lang, "th_note"))}</th></tr></thead><tbody>{rows}</tbody></table></div><p class="meta">{e(tr(lang, "eff_note"))}</p>'

def page_model(lang, job):
    J = D.JOBS[job]; offs = offers(job); sec = job_sec(job)
    m, s = jname(lang, job), jset(lang, job)
    cheap, dear = offs[0], offs[-1]
    plats = {o['plat'] for o in offs}
    title = tr(lang, 'model_title', m=m, s=s, u=unit_word(lang, job), n=len(plats))
    lead = tr(lang, 'model_lead', m=m, k=J['maker'], s=s, n=len(plats), c=rate_txt(lang, cheap, job), p=pname(cheap['plat']), x=rate_txt(lang, dear, job))
    others = [j for j in D.JOB_ORDER if D.JOBS[j]['model'] == J['model'] and j != job]
    oth = ''
    if others:
        oth = f'<h3>{e(tr(lang, "other_settings"))}</h3><ul>' + ''.join(f'<li><a href="{U(lang, "models/" + j + "/")}">{e(jname(lang, j))} · {e(jset(lang, j))}</a></li>' for j in others) + '</ul>'
    path = f'models/{job}/'
    body = f'''<section class="hero"><div class="wrap">{crumbs(lang, (tr(lang, "nav_models"), "models/"), (m + " · " + s, None))}
<h1>{e(tr(lang, "model_h1", m=m))}</h1><p class="lead">{e(lead)}</p><p class="meta">{e(s)} · {e(tr(lang, "checked"))}: {e(I.DATE[lang])}</p></div></section>
<section class="blk"><div class="wrap"><h2>{e(tr(lang, "table_h"))}</h2>{offer_table(lang, job)}</div></section>
<section class="blk"><div class="wrap"><h2>{e(tr(lang, "try_calc"))}</h2>{calc_html(lang, job)}</div></section>
<section class="blk"><div class="wrap prose">{oth}<p><a href="{U(lang, "failed-generations/")}">{e(tr(lang, "failed_teaser_h"))}</a></p></div></section>
'''
    write(lang, path, title, lead, body, extra=CALC_JS)

def page_models(lang):
    def tbl(kind):
        rows = ''
        for j in D.JOB_ORDER:
            if D.JOBS[j]['type'] != kind: continue
            offs = offers(j); c = offs[0]
            rows += f'<tr><td><a href="{U(lang, "models/" + j + "/")}"><b>{e(jname(lang, j))}</b></a></td><td>{e(jset(lang, j))}</td><td class="num">{e(tr(lang, "from_price", c=rate_txt(lang, c, j)))}</td><td>{tile(c["plat"], True)}{e(pname(c["plat"]))}</td><td class="n">{e(tr(lang, "n_platforms", n=len({o["plat"] for o in offs})))}</td></tr>'
        return f'<div class="tablewrap"><table><thead><tr><th>{e(tr(lang, "th_model"))}</th><th>{e(tr(lang, "th_setting"))}</th><th>{e(tr(lang, "th_rate"))}</th><th>{e(tr(lang, "th_cheapest"))}</th><th class="n">{e(tr(lang, "th_platform"))}</th></tr></thead><tbody>{rows}</tbody></table></div>'
    body = f'''<section class="hero"><div class="wrap">{crumbs(lang, (tr(lang, "nav_models"), None))}<h1>{e(tr(lang, "all_models_h"))}</h1><p class="lead">{e(tr(lang, "all_models_p"))}</p></div></section>
<section class="blk"><div class="wrap"><h2>{e(tr(lang, "video_models"))}</h2>{tbl("video")}</div></section>
<section class="blk"><div class="wrap"><h2>{e(tr(lang, "image_models"))}</h2>{tbl("image")}<p class="meta">{e(tr(lang, "eff_note"))}</p></div></section>'''
    write(lang, 'models/', tr(lang, 'all_models_h') + ' · GenCost', tr(lang, 'all_models_p'), body)

def plans_table(lang, p):
    P = D.PLATFORMS[p]
    if not P['plans']: return ''
    gpu = P['credit'] == 'GPU hours'
    rows = ''
    for pl in P['plans']:
        incl = tr(lang, 'gpu_hours', v=n_fmt(lang, pl['credits'])) if gpu else f'{n_fmt(lang, pl["credits"])} {cw(lang, p)}'
        if pl.get('yearly'): incl += f'<small>{n_fmt(lang, pl["yearly"])} / {e(tr(lang, "annual"))}</small>'
        if pl.get('limited'): incl += f'<small>{e(note_fact(lang, "hf_starter_short"))}</small>'
        pa = plan_price(pl, 'annual')
        per = pa / pl['credits'] * (1 if gpu else 1000)
        rows += f'<tr><td><b>{e(pl["name"])}</b></td><td class="n num">{usd(lang, pl["monthly"], 2) if pl["monthly"] is not None else e(tr(lang, "not_offered"))}</td><td class="n num">{usd(lang, pl["annual"], 2) if pl["annual"] is not None else e(tr(lang, "not_offered"))}</td><td class="n num">{incl}</td><td class="n num">{usd(lang, per)}</td></tr>'
    hper = tr(lang, 'per_gpu_h') if gpu else tr(lang, 'th_percredit', c=cw(lang, p))
    return f'<h2>{e(tr(lang, "plans_h"))}</h2><div class="tablewrap"><table><thead><tr><th>{e(tr(lang, "th_plan"))}</th><th class="n">{e(tr(lang, "th_monthly"))}</th><th class="n">{e(tr(lang, "th_annual"))}</th><th class="n">{e(tr(lang, "th_credits"))}</th><th class="n">{e(hper)}</th></tr></thead><tbody>{rows}</tbody></table></div><p class="meta">{src_link(lang, P["pricing"])}</p>'
def note_fact(lang, k): return tr(lang, 'limited_plan')

def plat_jobs(p): return [j for j in D.JOB_ORDER if any(o['plat'] == p and o['job'] == j for o in D.OFFERS)]

def page_pricing(lang, p):
    P = D.PLATFORMS[p]; name = P['name']
    kind = P['kind']
    lead = tr(lang, 'pp_lead_' + kind, p=name, c=cw(lang, p) if P['credit'] else '')
    rows = ''
    for j in plat_jobs(p):
        mine = [o for o in offers(j) if o['plat'] == p]
        best = offers(j)[0]
        for o in mine:
            r, rb = rate(o, j), rate(best, j)
            if best['plat'] == p or abs(r - rb) < 1e-9: vs = f'<span class="badge best">{e(tr(lang, "is_cheapest"))}</span>'
            else: vs = f'{tile(best["plat"], True)}{e(pname(best["plat"]))} {rate_txt(lang, best, j)}<small>{e(tr(lang, "pricier_by", pct=round((r / rb - 1) * 100)))}</small>'
            rows += f'<tr><td><a href="{U(lang, "models/" + j + "/")}"><b>{e(jname(lang, j))}</b></a><small>{e(jset(lang, j))}</small></td><td>{e(how(lang, o))}</td><td class="num">{e(listed(lang, o))}</td><td class="n num"><b>{rate_txt(lang, o, j)}</b></td><td>{vs}</td><td class="small">{"<br>".join(notes(lang, o, job_sec(j)))}{"<br>" if notes(lang, o, job_sec(j)) else ""}{src_link(lang, o["src"])}</td></tr>'
    if rows:
        models = f'<h2>{e(tr(lang, "models_on_h", p=name))}</h2><div class="tablewrap"><table><thead><tr><th>{e(tr(lang, "th_model"))}</th><th>{e(tr(lang, "th_how"))}</th><th>{e(tr(lang, "th_listed"))}</th><th class="n">{e(tr(lang, "th_rate"))}</th><th>{e(tr(lang, "th_vs"))}</th><th>{e(tr(lang, "th_note"))}</th></tr></thead><tbody>{rows}</tbody></table></div><p class="meta">{e(tr(lang, "eff_note"))}</p>'
    else:
        models = f'<div class="callout">{e(tr(lang, "no_permodel", p=name))}</div>'
    links = f'<a class="cta" href="{U(lang, p + "/alternatives/")}">{e(tr(lang, "see_alt", p=name))}</a><a class="cta sec" href="{e(P["pricing"])}" rel="nofollow noopener" target="_blank">{e(tr(lang, "official_page"))}</a>'
    if P.get('api'): links += f'<a class="cta sec" href="{e(P["api"]["url"])}" rel="nofollow noopener" target="_blank">{e(tr(lang, "api_page"))}</a>'
    facts = '<ul class="facts">' + ''.join(fact_li(lang, k) for k in P['facts']) + '</ul>'
    body = f'''<section class="hero"><div class="wrap">{crumbs(lang, (tr(lang, "nav_platforms"), "platforms/"), (name, None))}
<div style="display:flex;gap:14px;align-items:center">{tile(p)}<span class="eyebrow">{e(tr(lang, "kind_" + kind))}</span></div>
<h1>{e(tr(lang, "pp_h1", p=name))}</h1><p class="lead">{e(lead)}</p><p class="meta">{e(tr(lang, "checked"))}: {e(I.DATE[lang])}</p><div class="row">{links}</div></div></section>
<section class="blk"><div class="wrap">{models}</div></section>
{f'<section class="blk"><div class="wrap">{plans_table(lang, p)}</div></section>' if P['plans'] else ''}
<section class="blk"><div class="wrap prose"><h2>{e(tr(lang, "facts_h"))}</h2>{facts}</div></section>'''
    write(lang, p + '/pricing/', tr(lang, 'pp_title', p=name), lead, body)

def page_alt(lang, p):
    P = D.PLATFORMS[p]; name = P['name']
    jobs = plat_jobs(p)
    secs = ''
    if jobs:
        lead = tr(lang, 'alt_lead', p=name)
        for j in jobs:
            bb = best_by_plat(j); mine = bb[p]; r0 = rate(mine, j)
            rows = ''
            for q, o in sorted(bb.items(), key=lambda kv: rate(kv[1], j)):
                r = rate(o, j)
                if q == p: vs = '–'
                elif abs(r - r0) < 1e-9: vs = e(tr(lang, 'same_price'))
                elif r < r0: vs = f'<span class="pos">{e(tr(lang, "cheaper_by", pct=round((1 - r / r0) * 100)))}</span>'
                else: vs = e(tr(lang, 'pricier_by', pct=round((r / r0 - 1) * 100)))
                rows += f'<tr{" class=\"hl\"" if q == p else ""}><td>{tile(q, True)}<a href="{U(lang, q + "/pricing/")}"><b>{e(pname(q))}</b></a></td><td>{e(how(lang, o))}</td><td class="n num"><b>{rate_txt(lang, o, j)}</b></td><td class="n">{vs}</td><td class="small">{src_link(lang, o["src"])}</td></tr>'
            secs += f'<h3 style="margin-top:22px"><a href="{U(lang, "models/" + j + "/")}">{e(jname(lang, j))}</a> <span class="muted small">{e(jset(lang, j))}</span></h3><div class="tablewrap"><table><thead><tr><th>{e(tr(lang, "th_platform"))}</th><th>{e(tr(lang, "th_how"))}</th><th class="n">{e(tr(lang, "th_rate"))}</th><th class="n">{e(tr(lang, "on_p", p=name))}</th><th>{e(tr(lang, "th_src"))}</th></tr></thead><tbody>{rows}</tbody></table></div>'
        secs += f'<p class="meta">{e(tr(lang, "eff_note"))}</p>'
    else:
        lead = tr(lang, 'alt_lead_plan', p=name)
        cards = ''
        for q in D.ORDER:
            if q == p or not plat_jobs(q): continue
            cards += f'<a class="card pcard" href="{U(lang, q + "/pricing/")}">{tile(q)}<div><b>{e(pname(q))}</b><span>{e(tr(lang, "kind_" + D.PLATFORMS[q]["kind"]))} · {e(tr(lang, "plat_models"))}: {len(plat_jobs(q))}</span></div></a>'
        secs = f'<div class="grid">{cards}</div>'
    body = f'''<section class="hero"><div class="wrap">{crumbs(lang, (tr(lang, "nav_platforms"), "platforms/"), (name, p + "/pricing/"), (tr(lang, "alt_h1", p=name), None))}
<h1>{e(tr(lang, "alt_h1", p=name))}</h1><p class="lead">{e(lead)}</p><p class="meta">{e(tr(lang, "checked"))}: {e(I.DATE[lang])}</p>
<div class="row"><a class="cta sec" href="{U(lang, p + "/pricing/")}">{e(tr(lang, "see_pricing", p=name))}</a></div></div></section>
<section class="blk"><div class="wrap">{secs}</div></section>
<section class="blk"><div class="wrap prose"><h2>{e(tr(lang, "alt_why_h"))}</h2><p>{e(tr(lang, "alt_why"))}</p><p><a href="{U(lang, "failed-generations/")}">{e(tr(lang, "nav_failed"))}</a></p></div></section>'''
    write(lang, p + '/alternatives/', tr(lang, 'alt_title', p=name), lead, body)

def plat_cards(lang):
    out = ''
    for q in D.ORDER:
        n = len(plat_jobs(q))
        out += f'<div class="card pcard">{tile(q)}<div><a href="{U(lang, q + "/pricing/")}"><b>{e(pname(q))}</b></a><span>{e(tr(lang, "kind_" + D.PLATFORMS[q]["kind"]))}{" · " + e(tr(lang, "plat_models")) + ": " + str(n) if n else ""}</span><span><a class="lnk" href="{U(lang, q + "/pricing/")}">{e(tr(lang, "see_pricing", p=pname(q)))}</a> · <a class="lnk" href="{U(lang, q + "/alternatives/")}">{e(tr(lang, "see_alt", p=pname(q)))}</a></span></div></div>'
    return f'<div class="grid">{out}</div>'

def page_platforms(lang):
    body = f'''<section class="hero"><div class="wrap">{crumbs(lang, (tr(lang, "nav_platforms"), None))}<h1>{e(tr(lang, "plat_index_h"))}</h1><p class="lead">{e(tr(lang, "plat_index_p"))}</p></div></section>
<section class="blk"><div class="wrap">{plat_cards(lang)}</div></section>'''
    write(lang, 'platforms/', tr(lang, 'plat_index_h') + ' · GenCost', tr(lang, 'plat_index_p'), body)

def page_home(lang):
    rows = ''
    for j in D.JOB_ORDER:
        offs = offers(j); c = offs[0]
        rows += f'<tr><td><a href="{U(lang, "models/" + j + "/")}"><b>{e(jname(lang, j))}</b></a><small>{e(jset(lang, j))}</small></td><td>{tile(c["plat"], True)}{e(pname(c["plat"]))}</td><td class="n num"><b>{rate_txt(lang, c, j)}</b></td><td class="n">{e(tr(lang, "n_platforms", n=len({o["plat"] for o in offs})))}</td></tr>'
    nplat = len({o['plat'] for o in D.OFFERS}) + len(D.PLAN_ONLY)
    body = f'''<section class="hero"><div class="wrap"><span class="eyebrow">{e(tr(lang, "tagline"))}</span>
<h1>{e(tr(lang, "h1_home"))}</h1><p class="lead">{e(tr(lang, "home_lead"))}</p>
<div class="stats"><div><b class="num">{len(D.OFFERS)}</b><span>{e(tr(lang, "stat_offers"))}</span></div><div><b class="num">{nplat}</b><span>{e(tr(lang, "stat_platforms"))}</span></div><div><b class="num">{len(D.JOBS)}</b><span>{e(tr(lang, "stat_models"))}</span></div><div><b>{e(I.DATE[lang])}</b><span>{e(tr(lang, "checked"))}</span></div></div></div></section>
<section class="blk"><div class="wrap"><h2>{e(tr(lang, "calc_h"))}</h2>{calc_html(lang)}</div></section>
<section class="blk"><div class="wrap"><h2>{e(tr(lang, "cheapest_h"))}</h2><p class="muted" style="margin-bottom:14px">{e(tr(lang, "cheapest_p"))}</p>
<div class="tablewrap"><table><thead><tr><th>{e(tr(lang, "th_model"))}</th><th>{e(tr(lang, "th_cheapest"))}</th><th class="n">{e(tr(lang, "th_rate"))}</th><th class="n">{e(tr(lang, "th_platform"))}</th></tr></thead><tbody>{rows}</tbody></table></div></div></section>
<section class="blk"><div class="wrap"><h2>{e(tr(lang, "platforms_h"))}</h2>{plat_cards(lang)}</div></section>
<section class="blk"><div class="wrap"><div class="callout"><h3>{e(tr(lang, "failed_teaser_h"))}</h3><p>{e(tr(lang, "failed_teaser_p"))}</p><p style="margin-top:8px"><a class="lnk" href="{U(lang, "failed-generations/")}">{e(tr(lang, "read_more"))}</a></p></div></div></section>'''
    write(lang, '', tr(lang, 'site') + ': ' + tr(lang, 'h1_home'), tr(lang, 'home_lead'), body, extra=CALC_JS)

def page_failed(lang):
    j = 'kling-4-1080p'; o = [x for x in offers(j) if x['plat'] == 'kling'][0]; clip = eff(o, 5)
    rows = ''.join(f'<tr><td class="n">{k}%</td><td class="n num">{usd(lang, clip, 2)}</td><td class="n num"><b>{usd(lang, clip * 100 / k, 2)}</b></td></tr>' for k in (100, 50, 33, 25))
    tbl = f'<div class="tablewrap" style="max-width:520px;margin:6px 0 16px"><table><thead><tr><th class="n">{e(tr(lang, "f_keep"))}</th><th class="n">{e(tr(lang, "th_listed"))}</th><th class="n">{e(tr(lang, "th_unit"))}</th></tr></thead><tbody>{rows}</tbody></table></div>'
    say = '<ul class="facts">' + ''.join(fact_li(lang, k) for k in ['hf_failed', 'po_refund', 'po_addon', 'kr_packs', 'bp_packs', 'rw_rollover', 'fp_unlimited']) + \
          f'<li>{e(pname("runway"))}: {e(note(lang, "rw_min_n"))} (Seedance 2.5), {e(note(lang, "rw_min56_n"))} (Seedance 2.0). <a href="{D.RWAPI}" rel="nofollow noopener" target="_blank">{e(tr(lang, "source"))}</a></li></ul>'
    tips = '<ul>' + ''.join(f'<li>{e(tr(lang, k))}</li>' for k in ('fg_tip1', 'fg_tip2', 'fg_tip3', 'fg_tip4')) + '</ul>'
    body = f'''<section class="hero"><div class="wrap narrow">{crumbs(lang, (tr(lang, "nav_failed"), None))}<h1>{e(tr(lang, "fg_h1"))}</h1><p class="lead">{e(tr(lang, "fg_p1"))}</p></div></section>
<section class="blk"><div class="wrap narrow prose"><h2>{e(tr(lang, "fg_h2a"))}</h2><p>{e(tr(lang, "fg_p2"))}</p><div class="callout">{e(tr(lang, "fg_example"))}</div>{tbl}
<h2>{e(tr(lang, "fg_h2b"))}</h2>{say}<h2>{e(tr(lang, "fg_h2c"))}</h2>{tips}
<p><a class="cta" style="color:#fff;text-decoration:none" href="{U(lang)}#calc">{e(tr(lang, "try_calc"))}</a></p></div></section>'''
    write(lang, 'failed-generations/', tr(lang, 'fg_title'), tr(lang, 'fg_p1'), body)

def page_about(lang):
    srcs = '<ul>' + ''.join(f'<li><a href="{e(D.PLATFORMS[q]["pricing"])}" rel="nofollow noopener" target="_blank">{e(pname(q))}</a>{(" · <a href=\"" + e(D.PLATFORMS[q]["api"]["url"]) + "\" rel=\"nofollow noopener\" target=\"_blank\">" + e(tr(lang, "api_page")) + "</a>") if D.PLATFORMS[q].get("api") else ""}</li>' for q in D.ORDER) + '</ul>'
    rules = '<ul>' + ''.join(f'<li>{e(tr(lang, k, d=I.DATE[lang]) if k == "about_r2" else tr(lang, k))}</li>' for k in ('about_r1', 'about_r2', 'about_r3', 'about_r4', 'about_r5')) + '</ul>'
    body = f'''<section class="hero"><div class="wrap narrow">{crumbs(lang, (tr(lang, "nav_about"), None))}<h1>{e(tr(lang, "about_title"))}</h1><p class="lead">{e(tr(lang, "about_p1"))}</p></div></section>
<section class="blk"><div class="wrap narrow prose"><h2>{e(tr(lang, "about_h_rules"))}</h2>{rules}<h2>{e(tr(lang, "sources"))}</h2>{srcs}
<h2>{e(tr(lang, "about_h_fix"))}</h2><p>{e(tr(lang, "about_fix"))}</p><p><a href="{REPO}/issues" rel="noopener">{e(tr(lang, "about_open"))}</a></p></div></section>'''
    write(lang, 'about/', tr(lang, 'about_title'), tr(lang, 'about_p1'), body)

def page_privacy(lang):
    ps = ''.join(f'<p>{e(tr(lang, k))}</p>' for k in ('privacy_p1', 'privacy_p2', 'privacy_p3', 'privacy_p4'))
    body = f'''<section class="hero"><div class="wrap narrow">{crumbs(lang, (tr(lang, "privacy"), None))}<h1>{e(tr(lang, "privacy_title"))}</h1><p class="meta">{e(tr(lang, "updated"))}: {e(I.DATE[lang])}</p></div></section>
<section class="blk"><div class="wrap narrow prose">{ps}<p lang="en"><a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement" rel="nofollow noopener" target="_blank">GitHub Privacy Statement</a></p></div></section>'''
    write(lang, 'privacy/', tr(lang, 'privacy_title') + ' · GenCost', tr(lang, 'privacy_p1'), body)

# ------------------------------------------------------------------ root files
def root_files():
    links = ''.join(f'<li><a href="{U(l)}" hreflang="{I.HTML_LANG[l]}" lang="{I.HTML_LANG[l]}">{e(I.LNAME[l])}</a></li>' for l in LANGS)
    alts = ''.join(f'<link rel="alternate" hreflang="{I.HTML_LANG[l]}" href="{ORIGIN}{U(l)}">' for l in LANGS) + f'<link rel="alternate" hreflang="x-default" href="{ORIGIN}{U("en")}">'
    js = "var L=(navigator.languages||[navigator.language||'en']),M={zh:'zh',es:'es',de:'de',ja:'ja',pt:'pt',en:'en'},t='en';for(var i=0;i<L.length;i++){var k=(L[i]||'').slice(0,2).toLowerCase();if(M[k]){t=M[k];break}}location.replace('" + BASE + "'+t+'/');"
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GenCost: AI image and video generation prices compared</title>
<meta name="description" content="Compare what AI image and video generation costs on Higgsfield, Freepik, Krea, fal, Replicate, Runway, Kling, Google and more.">
<link rel="canonical" href="{ORIGIN}{U("en")}">{alts}<link rel="stylesheet" href="{BASE}assets/style.css?v={CSSV}"><link rel="icon" href="{BASE}favicon.svg" type="image/svg+xml"><script>{js}</script></head>
<body><main class="wrap narrow" style="padding:60px 28px"><a class="logo" href="{U("en")}"><span class="mark" aria-hidden="true">$</span>GenCost</a><h1>Choose your language</h1><ul class="prose">{links}</ul></main></body></html>'''
    open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(page)
    nf = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Page not found · GenCost</title><meta name="robots" content="noindex">
<link rel="stylesheet" href="{BASE}assets/style.css?v={CSSV}"><link rel="icon" href="{BASE}favicon.svg" type="image/svg+xml"></head>
<body><main class="wrap narrow" style="padding:60px 28px"><a class="logo" href="{U("en")}"><span class="mark" aria-hidden="true">$</span>GenCost</a>
''' + ''.join(f'<section lang="{I.HTML_LANG[l]}" style="margin-top:28px"><h2>{e(tr(l, "not_found_t"))}</h2><p>{e(tr(l, "not_found_p"))}</p><p><a class="lnk" href="{U(l)}">{e(tr(l, "nav_calc"))}</a> · <a class="lnk" href="{U(l, "models/")}">{e(tr(l, "nav_models"))}</a></p></section>' for l in LANGS) + '</main></body></html>'
    open(os.path.join(ROOT, '404.html'), 'w', encoding='utf-8').write(nf)
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for p in PAGES:
        alt = ''.join(f'<xhtml:link rel="alternate" hreflang="{I.HTML_LANG[l]}" href="{ORIGIN}{U(l, p)}"/>' for l in LANGS) + f'<xhtml:link rel="alternate" hreflang="x-default" href="{ORIGIN}{U("en", p)}"/>'
        for l in LANGS:
            sm.append(f'<url><loc>{ORIGIN}{U(l, p)}</loc><lastmod>{D.CHECKED}</lastmod>{alt}</url>')
    sm.append('</urlset>')
    open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write('\n'.join(sm) + '\n')
    open(os.path.join(ROOT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {ORIGIN}{BASE}sitemap.xml\n')
    open(os.path.join(ROOT, 'favicon.svg'), 'w').write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7C3AED"/><stop offset="1" stop-color="#2450E6"/></linearGradient></defs><rect width="32" height="32" rx="8" fill="url(#g)"/><text x="16" y="22" font-family="Arial" font-size="17" font-weight="700" text-anchor="middle" fill="#fff">$</text></svg>')
    open(os.path.join(ROOT, '.nojekyll'), 'w').write('')

def main():
    for l in LANGS:
        d = os.path.join(ROOT, l)
        if os.path.isdir(d): shutil.rmtree(d)
    for l in LANGS:
        page_home(l); page_models(l); page_platforms(l); page_failed(l); page_about(l); page_privacy(l)
        for j in D.JOB_ORDER: page_model(l, j)
        for p in D.ORDER: page_pricing(l, p); page_alt(l, p)
    root_files()
    print('pages per language:', len(PAGES), 'total:', len(PAGES) * len(LANGS))
if __name__ == '__main__': main()
