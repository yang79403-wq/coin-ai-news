#!/usr/bin/env python3
"""Mirror public coin reference images into this repository for GitHub Pages."""
from pathlib import Path
import json
import time
from urllib.parse import quote
import requests
from PIL import Image

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "assets" / "coins"
OUT.mkdir(parents=True, exist_ok=True)

COINS = [
    {"id":"yuan-3-obverse","filename":"yuan-3-obverse.jpg","source":"https://commons.wikimedia.org/wiki/Special:Redirect/file/Yuan_Shikai_Dollar_Year_3_Obverse.jpg","wikimedia_file":"Yuan Shikai Dollar Year 3 Obverse.jpg","title":"Yuan Shikai Dollar, Year 3, obverse","label":"袁大头"},
    {"id":"cash-coins","filename":"cash-coins-a.jpg","source":"https://commons.wikimedia.org/wiki/Special:Redirect/file/Chinese_cash_coins_a.jpg","wikimedia_file":"Chinese cash coins a.jpg","title":"Chinese cash coins","label":"古钱币"},
    {"id":"rmb1-100","filename":"rmb1-100-1b.jpg","source":"https://commons.wikimedia.org/wiki/Special:Redirect/file/RMB1-100-1B.jpg","wikimedia_file":"RMB1-100-1B.jpg","title":"RMB 1st series, 100 yuan specimen","label":"老纸币"},
    {"id":"panda-2016","filename":"panda-2016-reverse.png","source":"https://commons.wikimedia.org/wiki/Special:Redirect/file/China_Panda_Goldmünze_2016_Rückseite.png","wikimedia_file":"China Panda Goldmünze 2016 Rückseite.png","title":"China Panda Gold Coin 2016 reverse","label":"熊猫金币"},
    {"id":"founding-commemorative","filename":"founding-commemorative.jpg","source":"https://commons.wikimedia.org/wiki/Special:Redirect/file/中华民国开国纪念币一圆硬币 正面.jpg","wikimedia_file":"中华民国开国纪念币一圆硬币 正面.jpg","title":"Republic of China Founding Commemorative Dollar","label":"开国纪念币"},
    {"id":"yuan-mechanism-reference","filename":"yuan-1921-iii.png","source":"https://commons.wikimedia.org/wiki/Special:Redirect/file/Yuan_Shikai_Dollar_Year_3_Obverse.png","wikimedia_file":"Yuan Shikai Dollar Year 3 Obverse.png","title":"Yuan Shikai silver dollar reference","label":"机制银币"},
]

HEADERS = {"User-Agent":"CoinAI-News/1.0 (GitHub Actions; public image mirror)"}
session = requests.Session()
session.headers.update(HEADERS)

def resolve_wikimedia_url(filename: str) -> str:
    api = "https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url&format=json&titles=" + quote("File:" + filename)
    data = session.get(api, timeout=30).json()
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        info = page.get("imageinfo")
        if info and info[0].get("url"):
            return info[0]["url"]
    raise RuntimeError(f"Wikimedia API could not resolve File:{filename}")

results = []
for item in COINS:
    target = OUT / item["filename"]
    ok = False
    fallback_used = False
    error = None
    urls = [item["source"]]
    try:
        urls.append(resolve_wikimedia_url(item["wikimedia_file"]))
    except Exception as exc:
        print(f"API fallback unavailable for {item['label']}: {exc}")

    for url in urls:
        for attempt in range(3):
            try:
                response = session.get(url, timeout=30, allow_redirects=True)
                response.raise_for_status()
                if len(response.content) < 1000:
                    raise RuntimeError(f"response too small: {len(response.content)} bytes")
                target.write_bytes(response.content)
                ok = True
                break
            except Exception as exc:  # noqa: BLE001
                error = str(exc)
                time.sleep(2 * (attempt + 1))
        if ok:
            break

    # Wikimedia may occasionally reject one large historical file. Keep the site
    # fully local by using a real mirrored silver-dollar image as a valid PNG fallback.
    if not ok and item["id"] == "yuan-mechanism-reference":
        fallback = OUT / "yuan-3-obverse.jpg"
        if fallback.exists():
            Image.open(fallback).convert("RGB").save(target, "PNG")
            ok = True
            fallback_used = True
            error = f"source unavailable; generated local PNG copy from {fallback.name}"

    results.append({**item,"local":f"assets/coins/{item['filename']}","mirrored":ok,"fallback_used":fallback_used,"error":error})
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
