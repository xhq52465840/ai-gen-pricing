# GenCost: AI image and video generation prices compared

Static, multilingual (en, zh, es, de, ja, pt) price comparison for AI image and video generation:
Higgsfield, Pollo AI, Krea, Freepik (Magnific), OpenArt, fal, Replicate, Runway, Luma AI, Kling AI,
Google Gemini API, BytePlus ModelArk (Seedance), Alibaba Cloud Model Studio (Wan) and Midjourney.

Every price in `src/data.py` was read on the linked official page on the date in `CHECKED`.
If a platform does not publish a per-model price, it is left out for that model.

Live site: https://xhq52465840.github.io/ai-gen-pricing/

## Build and check
```
python3 src/build.py                     # writes /en/ /zh/ /es/ /de/ /ja/ /pt/, sitemap.xml, robots.txt, 404.html
python3 tools/check_links.py             # every internal URL resolves under BASE_PATH
mkdir -p /tmp/srv && ln -sfn "$PWD" /tmp/srv/ai-gen-pricing && (cd /tmp/srv && python3 -m http.server 8090 &)
python3 tools/check_i18n.py --math 60    # parity, hreflang, sitemap, leftover English, JS vs Python maths
```
`BASE_PATH` (default `/ai-gen-pricing/`) and `SITE_ORIGIN` env vars change the URL base, e.g. for a custom domain use `BASE_PATH=/`.

Found a wrong price? Open an issue with the link to the official page.
