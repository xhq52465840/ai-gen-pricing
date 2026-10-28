"""Verified price data. Every number here was read on the linked official page on CHECKED.
Rule: never invent a price. If a platform does not publish a per-model cost, it is not listed for that model."""
CHECKED = '2026-10-28'

# ---------------------------------------------------------------- platforms
# kind: 'api' (pay as you go) | 'app' (credit subscription) | 'both'
# plans: list of dicts {id, name, monthly (USD/mo billed monthly or None), annual (USD/mo billed annually or None), credits (per month), note}
PLATFORMS = {
 'higgsfield': dict(name='Higgsfield', kind='app', color='#111111', fg='#D7FF3E', mono='H', url='https://higgsfield.ai',
    pricing='https://higgsfield.ai/pricing', credit='credits',
    plans=[dict(id='starter', name='Starter', monthly=19, annual=19, credits=270, limited=True),
           dict(id='plus', name='Plus', monthly=59, annual=47, credits=1200),
           dict(id='ultra', name='Ultra', monthly=129, annual=99, credits=3000)],
    facts=['hf_rollover', 'hf_failed', 'hf_unlimited', 'hf_starter'],
    api=dict(url='https://open.higgsfield.ai/pricing')),
 'pollo': dict(name='Pollo AI', kind='app', color='#7C3AED', fg='#fff', mono='P', url='https://pollo.ai',
    pricing='https://pollo.ai/pricing', credit='credits',
    plans=[dict(id='lite', name='Lite', monthly=None, annual=15, credits=400),
           dict(id='pro', name='Pro', monthly=None, annual=29, credits=800),
           dict(id='ultra', name='Ultra', monthly=None, annual=129, credits=5000)],
    facts=['po_rollover', 'po_refund', 'po_addon', 'po_permodel']),
 'krea': dict(name='Krea', kind='app', color='#0B0B0B', fg='#fff', mono='K', url='https://www.krea.ai',
    pricing='https://www.krea.ai/pricing', credit='compute units',
    plans=[dict(id='basic', name='Basic', monthly=9, annual=5.25, credits=5000),
           dict(id='pro', name='Pro', monthly=35, annual=21, credits=20000),
           dict(id='max', name='Max', monthly=105, annual=63, credits=60000)],
    facts=['kr_packs', 'kr_relaxed', 'kr_counts']),
 'freepik': dict(name='Freepik (Magnific)', kind='app', color='#1273EB', fg='#fff', mono='F', url='https://www.magnific.com',
    pricing='https://www.magnific.com/pricing', credit='credits',
    plans=[dict(id='premium', name='Premium', monthly=None, annual=14.50, credits=20000, yearly=240000),
           dict(id='premiumplus', name='Premium+', monthly=None, annual=33.75, credits=50000, yearly=600000),
           dict(id='prostarter', name='Pro Starter', monthly=None, annual=82.50, credits=125000, yearly=1500000)],
    facts=['fp_rename', 'fp_yearly', 'fp_unlimited']),
 'openart': dict(name='OpenArt', kind='app', color='#F43F5E', fg='#fff', mono='O', url='https://openart.ai',
    pricing='https://openart.ai/pricing', credit='credits',
    plans=[dict(id='starter', name='Starter', monthly=14, annual=13, credits=4000),
           dict(id='plus', name='Plus', monthly=34, annual=27, credits=12000),
           dict(id='pro', name='Pro', monthly=56, annual=44, credits=24000),
           dict(id='wonder', name='Wonder', monthly=240, annual=175, credits=106000)],
    facts=['oa_counts', 'oa_permodel', 'oa_promo']),
 'fal': dict(name='fal', kind='api', color='#5B21B6', fg='#fff', mono='fal', url='https://fal.ai',
    pricing='https://fal.ai/pricing', credit=None, plans=[], facts=['fal_payg', 'fal_models']),
 'replicate': dict(name='Replicate', kind='api', color='#EA2805', fg='#fff', mono='R', url='https://replicate.com',
    pricing='https://replicate.com/pricing', credit=None, plans=[], facts=['rep_payg', 'rep_models']),
 'runway': dict(name='Runway', kind='both', color='#000000', fg='#fff', mono='Rw', url='https://runwayml.com',
    pricing='https://runwayml.com/pricing', credit='credits',
    plans=[dict(id='standard', name='Standard', monthly=15, annual=12, credits=625),
           dict(id='pro', name='Pro', monthly=35, annual=28, credits=2250),
           dict(id='max', name='Max', monthly=95, annual=76, credits=9500)],
    facts=['rw_api', 'rw_rollover', 'rw_topup'],
    api=dict(url='https://docs.dev.runwayml.com/guides/pricing/')),
 'luma': dict(name='Luma AI', kind='both', color='#1E1B4B', fg='#fff', mono='L', url='https://lumalabs.ai',
    pricing='https://lumalabs.ai/pricing', credit='credits',
    plans=[dict(id='plus', name='Plus', monthly=30, annual=None, credits=10000),
           dict(id='pro', name='Pro', monthly=90, annual=None, credits=40000),
           dict(id='ultra', name='Ultra', monthly=300, annual=None, credits=150000)],
    facts=['lu_api', 'lu_hdr'], api=dict(url='https://lumalabs.ai/api/pricing')),
 'kling': dict(name='Kling AI', kind='both', color='#0A0A0A', fg='#00E5A8', mono='Kl', url='https://kling.ai',
    pricing='https://kling.ai/document-api/pricing/base/video', credit='units',
    plans=[], facts=['kl_api', 'kl_preview', 'kl_app'], api=dict(url='https://kling.ai/document-api/pricing/base/video')),
 'google': dict(name='Google (Gemini API)', kind='api', color='#1A73E8', fg='#fff', mono='G', url='https://ai.google.dev',
    pricing='https://ai.google.dev/gemini-api/docs/pricing', credit=None, plans=[], facts=['gg_veo', 'gg_omni', 'gg_tokens']),
 'byteplus': dict(name='BytePlus ModelArk (Seedance)', kind='api', color='#3C8CE7', fg='#fff', mono='B', url='https://www.byteplus.com',
    pricing='https://docs.byteplus.com/en/docs/ModelArk/1544106', credit=None, plans=[], facts=['bp_tokens', 'bp_packs']),
 'alibaba': dict(name='Alibaba Cloud Model Studio (Wan)', kind='api', color='#FF6A00', fg='#fff', mono='A', url='https://www.alibabacloud.com',
    pricing='https://www.alibabacloud.com/help/en/model-studio/wan3-0-video', credit=None, plans=[], facts=['al_region', 'al_prime']),
 'midjourney': dict(name='Midjourney', kind='app', color='#0B0B0B', fg='#fff', mono='MJ', url='https://www.midjourney.com',
    pricing='https://docs.midjourney.com/hc/en-us/articles/27870484040333-Comparing-Midjourney-Plans', credit='GPU hours',
    plans=[dict(id='basic', name='Basic', monthly=10, annual=8, credits=3.3),
           dict(id='standard', name='Standard', monthly=30, annual=24, credits=15),
           dict(id='pro', name='Pro', monthly=60, annual=48, credits=30),
           dict(id='mega', name='Mega', monthly=120, annual=96, credits=60)],
    facts=['mj_gpu', 'mj_relax', 'mj_noapi']),
}
ORDER = ['higgsfield', 'pollo', 'krea', 'freepik', 'openart', 'fal', 'replicate', 'runway', 'luma', 'kling', 'google', 'byteplus', 'alibaba', 'midjourney']

# ---------------------------------------------------------------- jobs (model + setting)
# type 'video' priced per second of output (sec default 5) or 'image' per image.
JOBS = {
 'kling-4-720p':      dict(type='video', model='Kling 4.0', maker='Kuaishou', setting='720p, text/image input', sec=5),
 'kling-4-1080p':     dict(type='video', model='Kling 4.0', maker='Kuaishou', setting='1080p, text/image input', sec=5),
 'kling-3-1080p':     dict(type='video', model='Kling 3.0', maker='Kuaishou', setting='1080p, no native audio', sec=5),
 'seedance-2-5-720p': dict(type='video', model='Seedance 2.5', maker='ByteDance', setting='720p, no video input', sec=5),
 'seedance-2-5-1080p':dict(type='video', model='Seedance 2.5', maker='ByteDance', setting='1080p, no video input', sec=5),
 'seedance-2-720p':   dict(type='video', model='Seedance 2.0', maker='ByteDance', setting='720p, no video input', sec=5),
 'seedance-2-1080p':  dict(type='video', model='Seedance 2.0', maker='ByteDance', setting='1080p, no video input', sec=5),
 'veo-3-1-1080p':     dict(type='video', model='Veo 3.1', maker='Google', setting='1080p, with audio', sec=8),
 'veo-3-1-fast-1080p':dict(type='video', model='Veo 3.1 Fast', maker='Google', setting='1080p, with audio', sec=8),
 'gemini-omni-flash-720p': dict(type='video', model='Gemini Omni Flash 1.1', maker='Google', setting='720p', sec=5),
 'wan-3-720p':        dict(type='video', model='Wan 3.0', maker='Alibaba', setting='720p', sec=5),
 'wan-3-1080p':       dict(type='video', model='Wan 3.0', maker='Alibaba', setting='1080p', sec=5),
 'runway-gen-4-5':    dict(type='video', model='Runway Gen-4.5', maker='Runway', setting='default resolution', sec=5),
 'luma-ray-3-2-720p': dict(type='video', model='Luma Ray3.2', maker='Luma AI', setting='720p SDR, image-to-video', sec=5),
 'luma-ray-3-2-1080p':dict(type='video', model='Luma Ray3.2', maker='Luma AI', setting='1080p SDR, image-to-video', sec=5),
 'nano-banana-2-1k':  dict(type='image', model='Nano Banana 2', maker='Google', setting='1K (1024px)'),
 'nano-banana-2-2k':  dict(type='image', model='Nano Banana 2', maker='Google', setting='2K (2048px)'),
 'nano-banana-pro-2k':dict(type='image', model='Nano Banana Pro', maker='Google', setting='1K or 2K'),
 'gpt-image-2-high':  dict(type='image', model='GPT Image 2', maker='OpenAI', setting='high quality, 1K square'),
 'flux-2-pro-1mp':    dict(type='image', model='FLUX.2 [pro]', maker='Black Forest Labs', setting='1 megapixel, no input image'),
}
JOB_ORDER = list(JOBS)

# ---------------------------------------------------------------- offers
# unit: 'usd_s' ($ per second) | 'usd_clip' ($ per clip of `per` seconds) | 'usd_img' ($ per image)
#       'cr_s' (credits per second) | 'cr_clip' (credits per clip of `per` seconds) | 'cr_img' (credits per image)
# approx=True when the platform itself shows "~"; derived=True when we compute from the platform's own published numbers (explained in `calc`).
# promo: temporary price note. src: the exact official page the number was read on.
F = 'https://fal.ai/models/'
R = 'https://replicate.com/'
RWAPI = 'https://docs.dev.runwayml.com/guides/pricing/'
KL = 'https://kling.ai/document-api/pricing/base/video'
HF = 'https://higgsfield.ai/pricing'
FP = 'https://www.magnific.com/pricing'
BP = 'https://docs.byteplus.com/en/docs/ModelArk/1544106'
AL = 'https://www.alibabacloud.com/help/en/model-studio/wan3-0-video'
GG = 'https://ai.google.dev/gemini-api/docs/pricing'
O = lambda job, plat, unit, v, src, **k: dict(job=job, plat=plat, unit=unit, v=v, src=src, **k)
OFFERS = [
 # Kling 4.0 720p
 O('kling-4-720p', 'kling', 'usd_s', 0.157, KL, channel='api', note='kl_preview_n'),
 O('kling-4-720p', 'fal', 'usd_s', 0.157, F + 'kling/v4/text-to-video'),
 O('kling-4-720p', 'replicate', 'usd_s', 0.157, R + 'kwaivgi/kling-v4.0'),
 O('kling-4-720p', 'runway', 'usd_s', 0.157, RWAPI, channel='api', promo='rw_kling_promo'),
 # Kling 4.0 1080p
 O('kling-4-1080p', 'kling', 'usd_s', 0.235, KL, channel='api', note='kl_preview_n'),
 O('kling-4-1080p', 'fal', 'usd_s', 0.235, F + 'kling/v4/text-to-video'),
 O('kling-4-1080p', 'replicate', 'usd_s', 0.235, R + 'kwaivgi/kling-v4.0'),
 O('kling-4-1080p', 'runway', 'usd_s', 0.235, RWAPI, channel='api', promo='rw_kling_promo'),
 O('kling-4-1080p', 'runway', 'cr_clip', 118, 'https://runwayml.com/pricing', per=5, channel='app', promo='rw_kling_promo'),
 O('kling-4-1080p', 'freepik', 'cr_clip', 840, FP, per=3),
 # Kling 3.0 1080p
 O('kling-3-1080p', 'kling', 'usd_s', 0.112, KL, channel='api'),
 O('kling-3-1080p', 'fal', 'usd_s', 0.112, F + 'fal-ai/kling-video/v3/pro/text-to-video'),
 O('kling-3-1080p', 'runway', 'usd_s', 0.12, RWAPI, channel='api'),
 O('kling-3-1080p', 'higgsfield', 'cr_clip', 8, HF, per=5, approx=True, note='hf_audio_n'),
 O('kling-3-1080p', 'freepik', 'cr_clip', 450, FP, per=5, note='fp_k3_n'),
 # Seedance 2.5
 O('seedance-2-5-720p', 'byteplus', 'usd_s', 0.231, BP, note='bp_example_n'),
 O('seedance-2-5-720p', 'replicate', 'usd_s', 0.2312, R + 'bytedance/seedance-2.5'),
 O('seedance-2-5-720p', 'fal', 'usd_s', 0.4730, F + 'bytedance/seedance-2.5/text-to-video', approx=True),
 O('seedance-2-5-720p', 'runway', 'usd_s', 0.30, RWAPI, channel='api', note='rw_min_n', min_usd=0.80),
 O('seedance-2-5-720p', 'freepik', 'cr_clip', 1760, FP, per=4),
 O('seedance-2-5-1080p', 'byteplus', 'usd_s', 0.569, BP, note='bp_example_n'),
 O('seedance-2-5-1080p', 'fal', 'usd_s', 1.164, F + 'bytedance/seedance-2.5/text-to-video', approx=True),
 O('seedance-2-5-1080p', 'runway', 'usd_s', 0.68, RWAPI, channel='api', note='rw_min_n', min_usd=0.80),
 O('seedance-2-5-1080p', 'freepik', 'cr_clip', 4400, FP, per=4),
 # Seedance 2.0
 O('seedance-2-720p', 'byteplus', 'usd_s', 0.15, BP, note='bp_example_n'),
 O('seedance-2-720p', 'replicate', 'usd_s', 0.18, R + 'bytedance/seedance-2.0'),
 O('seedance-2-720p', 'fal', 'usd_s', 0.3034, F + 'bytedance/seedance-2.0/text-to-video'),
 O('seedance-2-720p', 'runway', 'usd_s', 0.30, RWAPI, channel='api', note='rw_min56_n', min_usd=0.56),
 O('seedance-2-720p', 'higgsfield', 'cr_clip', 22, HF, per=5, approx=True),
 O('seedance-2-720p', 'freepik', 'cr_clip', 1120, FP, per=4, note='fp_s2pro_n'),
 O('seedance-2-1080p', 'byteplus', 'usd_s', 0.37, BP, note='bp_example_n'),
 O('seedance-2-1080p', 'replicate', 'usd_s', 0.45, R + 'bytedance/seedance-2.0'),
 O('seedance-2-1080p', 'fal', 'usd_s', 0.682, F + 'bytedance/seedance-2.0/text-to-video'),
 O('seedance-2-1080p', 'runway', 'usd_s', 0.40, RWAPI, channel='api', note='rw_min56_n', min_usd=0.56),
 O('seedance-2-1080p', 'runway', 'cr_clip', 160, 'https://runwayml.com/pricing', per=4, channel='app'),
 O('seedance-2-1080p', 'higgsfield', 'cr_clip', 60, HF, per=5, approx=True),
 # Veo 3.1
 O('veo-3-1-1080p', 'fal', 'usd_s', 0.40, F + 'fal-ai/veo3.1'),
 O('veo-3-1-1080p', 'replicate', 'usd_s', 0.40, R + 'google/veo-3.1'),
 O('veo-3-1-1080p', 'runway', 'usd_s', 0.40, RWAPI, channel='api'),
 O('veo-3-1-1080p', 'higgsfield', 'cr_clip', 40, HF, per=4, approx=True, note='hf_audio_n'),
 O('veo-3-1-fast-1080p', 'replicate', 'usd_s', 0.15, R + 'google/veo-3.1-fast'),
 O('veo-3-1-fast-1080p', 'runway', 'usd_s', 0.15, RWAPI, channel='api'),
 O('veo-3-1-fast-1080p', 'higgsfield', 'cr_clip', 16, HF, per=4, approx=True, note='hf_audio_n'),
 # Gemini Omni Flash 1.1
 O('gemini-omni-flash-720p', 'google', 'usd_s', 0.10, GG, approx=True, note='gg_omni_n'),
 O('gemini-omni-flash-720p', 'fal', 'usd_s', 0.10, F + 'google/gemini-omni-flash/v1.1/text-to-video'),
 O('gemini-omni-flash-720p', 'runway', 'usd_s', 0.10, RWAPI, channel='api'),
 # Wan 3.0
 O('wan-3-720p', 'alibaba', 'usd_s', 0.10, AL, note='al_region_n'),
 O('wan-3-720p', 'fal', 'usd_s', 0.10, F + 'alibaba/wan-3.0/text-to-video'),
 O('wan-3-720p', 'runway', 'usd_s', 0.10, RWAPI, channel='api'),
 O('wan-3-720p', 'higgsfield', 'cr_clip', 8.75, HF, per=5),
 O('wan-3-1080p', 'alibaba', 'usd_s', 0.20, AL, note='al_region_n'),
 O('wan-3-1080p', 'fal', 'usd_s', 0.20, F + 'alibaba/wan-3.0/text-to-video'),
 O('wan-3-1080p', 'runway', 'usd_s', 0.20, RWAPI, channel='api'),
 O('wan-3-1080p', 'higgsfield', 'cr_clip', 17.5, HF, per=5),
 # Runway Gen-4.5
 O('runway-gen-4-5', 'runway', 'usd_s', 0.12, RWAPI, channel='api'),
 O('runway-gen-4-5', 'runway', 'cr_s', 12, 'https://runwayml.com/pricing', channel='app'),
 O('runway-gen-4-5', 'replicate', 'usd_s', 0.12, R + 'runwayml/gen-4.5'),
 # Luma Ray3.2 (5 s clips)
 O('luma-ray-3-2-720p', 'luma', 'usd_clip', 0.30, 'https://lumalabs.ai/api/pricing', per=5, channel='api'),
 O('luma-ray-3-2-720p', 'luma', 'cr_clip', 100, 'https://lumalabs.ai/pricing', per=5, channel='app'),
 O('luma-ray-3-2-720p', 'fal', 'usd_clip', 0.30, F + 'luma/agent/ray/v3.2/image-to-video', per=5),
 O('luma-ray-3-2-720p', 'replicate', 'usd_clip', 0.30, R + 'luma/ray-3.2', per=5),
 O('luma-ray-3-2-1080p', 'luma', 'usd_clip', 1.20, 'https://lumalabs.ai/api/pricing', per=5, channel='api'),
 O('luma-ray-3-2-1080p', 'luma', 'cr_clip', 400, 'https://lumalabs.ai/pricing', per=5, channel='app'),
 O('luma-ray-3-2-1080p', 'fal', 'usd_clip', 1.20, F + 'luma/agent/ray/v3.2/image-to-video', per=5),
 O('luma-ray-3-2-1080p', 'replicate', 'usd_clip', 1.20, R + 'luma/ray-3.2', per=5),
 # Nano Banana 2
 O('nano-banana-2-1k', 'google', 'usd_img', 0.067, GG),
 O('nano-banana-2-1k', 'replicate', 'usd_img', 0.067, R + 'google/nano-banana-2'),
 O('nano-banana-2-1k', 'fal', 'usd_img', 0.08, F + 'fal-ai/nano-banana-2'),
 O('nano-banana-2-1k', 'runway', 'usd_img', 0.07, RWAPI, channel='api'),
 O('nano-banana-2-1k', 'higgsfield', 'cr_img', 2, HF, note='hf_res_n'),
 O('nano-banana-2-1k', 'freepik', 'cr_img', 75, FP, note='fp_unl_n'),
 O('nano-banana-2-1k', 'krea', 'cr_img', 44.44, 'https://www.krea.ai/pricing', derived=True, calc='kr_calc_nb2'),
 O('nano-banana-2-2k', 'google', 'usd_img', 0.101, GG),
 O('nano-banana-2-2k', 'replicate', 'usd_img', 0.101, R + 'google/nano-banana-2'),
 O('nano-banana-2-2k', 'fal', 'usd_img', 0.12, F + 'fal-ai/nano-banana-2', derived=True, calc='fal_calc_nb2'),
 O('nano-banana-2-2k', 'runway', 'usd_img', 0.11, RWAPI, channel='api'),
 O('nano-banana-2-2k', 'freepik', 'cr_img', 75, FP, note='fp_unl_n'),
 # Nano Banana Pro
 O('nano-banana-pro-2k', 'google', 'usd_img', 0.134, GG),
 O('nano-banana-pro-2k', 'replicate', 'usd_img', 0.15, R + 'google/nano-banana-pro'),
 O('nano-banana-pro-2k', 'fal', 'usd_img', 0.15, F + 'fal-ai/nano-banana-pro'),
 O('nano-banana-pro-2k', 'runway', 'usd_img', 0.20, RWAPI, channel='api'),
 O('nano-banana-pro-2k', 'runway', 'cr_img', 20, 'https://runwayml.com/pricing', channel='app'),
 O('nano-banana-pro-2k', 'higgsfield', 'cr_img', 2, HF),
 O('nano-banana-pro-2k', 'freepik', 'cr_img', 75, FP, note='fp_unl_n'),
 # GPT Image 2
 O('gpt-image-2-high', 'replicate', 'usd_img', 0.128, R + 'openai/gpt-image-2'),
 O('gpt-image-2-high', 'runway', 'usd_img', 0.20, RWAPI, channel='api'),
 # FLUX.2 pro
 O('flux-2-pro-1mp', 'fal', 'usd_img', 0.03, F + 'fal-ai/flux-2-pro'),
 O('flux-2-pro-1mp', 'replicate', 'usd_img', 0.03, R + 'black-forest-labs/flux-2-pro', derived=True, calc='rep_calc_flux'),
 O('flux-2-pro-1mp', 'higgsfield', 'cr_img', 1, HF),
]

# Platforms that publish plans but no per-model price for the models above (shown with plan data only).
PLAN_ONLY = ['pollo', 'openart', 'midjourney']
