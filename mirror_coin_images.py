#!/usr/bin/env python3
"""Mirror public coin reference images into this repository for GitHub Pages.

The source files are public Wikimedia Commons media. The script keeps source URLs
and attribution metadata beside the mirrored files and never bypasses login,
CAPTCHA, robots controls, or other access restrictions.
"""
from pathlib import Path
import json
import time
import requests

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "assets" / "coins"
OUT.mkdir(parents=True, exist_ok=True)

COINS = [
    {"id":"yuan-3-obverse","filename":"yuan-3-obverse.jpg","source":"https://commons.wikimedia.org/wiki/Special:Redirect/file/Yuan_Shikai_Dollar_Year_3_Obverse.jpg","title":"Yuan Shikai Dollar, Year 3, obverse","label":"袁大头"},
    {"id":"cash-coins","filename":"cash-coins-a.jpg","source":"https://commons.wikimedia.org/wiki/Special:Redirect/file/Chinese_cash_coins_a.jpg","title":"Chinese cash coins","label":"古钱币"},
    {"id":"rmb1-100","filename":"rmb1-100-1b.jpg","source":"https://commons.wikimedia.org/wiki/Special:Redirect/file/RMB1-100-1B.jpg","title":"RMB 1st series, 100 yuan specimen","label":"老纸币"},
    {"id":"panda-2016","filename":"panda-2016-reverse.png","source":"https://commons.wikimedia.org/wiki/Special:Redirect/file/China_Panda_Goldmünze_2016_Rückseite.png","title":"China Panda Gold Coin 2016 reverse","label":"熊猫金币"},
    {"id":"founding-commemorative","filename":"founding-commemorative.jpg","source":"https://commons.wikimedia.org/wiki/Special:Redirect/file/中华民国开国纪念币一圆硬币 正面.jpg","title":"Republic of China Founding Commemorative Dollar","label":"开国纪念币"},
    {"id":"yuan-1921","filename":"yuan-1921-iii.png","source":"https://commons.wikimedia.org/wiki/Special:FilePath/1_dollar_Yuan_Shikai_1921_-_III.png","title":"Yuan Shikai Dollar 1921","label":"机制银币"},
]

HEADERS = {"User-Agent":"CoinAI-News/1.0 (GitHub Actions; public image mirror)"}
session = requests.Session()
session.headers.update(HEADERS)
results = []

for item in COINS:
    target = OUT / item["filename"]
    ok = False
    error = None
    for attempt in range(3):
        try:
            response = session.get(item["source"], timeout=30, allow_redirects=True)
            response.raise_for_status()
            if len(response.content) < 1000:
                raise RuntimeError(f"response too small: {len(response.content)} bytes")
            target.write_bytes(response.content)
            ok = True
            break
        except Exception as exc:  # noqa: BLE001
            error = str(exc)
            time.sleep(2 * (attempt + 1))
    results.append({**item,"local":f"assets/coins/{item['filename']}","mirrored":ok,"error":error})
    print(f"{'OK' if ok else 'FAIL'} {item['label']}: {target}")

metadata = {
    "updated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "notice": "Public Wikimedia Commons reference images mirrored for GitHub Pages. Check each original file page for current license/attribution requirements before reuse outside this site.",
    "images": results,
}
(ROOT / "assets" / "coins" / "sources.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

failed = [x for x in results if not x["mirrored"]]
if failed:
    print(f"ERROR: {len(failed)} image(s) failed to mirror.")
    raise SystemExit(1)
print(f"Mirrored {len(results)} coin images successfully.")
