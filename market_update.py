import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

SOURCES = [
    {"provider_id":"yichen","source_name":"一尘网","url":"https://www.pm001.net/index.asp"},
    {"provider_id":"yy11","source_name":"钱币天堂","url":"https://www.yy11.com/htm/shop.cgi"},
    {"provider_id":"huaxia","source_name":"华夏古泉","url":"https://www.hxguquan.com/"},
]
CATEGORIES = [
    ("古钱", ["古钱","通宝","重宝","元宝","五铢","半两","方孔","刀币","布币"]),
    ("银元", ["银元","袁大头","袁世凯","大洋","龙洋","银币"]),
    ("纸币", ["纸币","人民币","老钞","钞票","纸钞"]),
    ("纪念币", ["纪念币","生肖币","流通纪念币"]),
    ("纪念钞", ["纪念钞","纪念钞票"]),
    ("金银币", ["金币","金银币","金条","银条","贵金属币"]),
]
TRANSACTION_WORDS = ["成交价","成交价格","已成交","成交","落槌价","落槌","中标价","中标","得标价","得标","拍得","结拍"]
ACTIVE_WORDS = ["拍卖中","竞拍中","竞价中","正在拍","待拍","尚未结拍","出价"]
HEADERS = {"User-Agent":"Mozilla/5.0 (compatible; HongshengCollectionMarket/2.0)"}
TIMEOUT = 20
MAX_PAGES = 30
MAX_ROWS = 240


def clean(s):
    return " ".join(unescape(str(s or "")).replace("\xa0", " ").split())


def extract_price(text):
    text = clean(text).replace(",", "")
    patterns = [
        r"(?:成交价格|成交价|落槌价|中标价|得标价|最终价|拍得|成交|落槌|中标|得标)\s*[:：]?\s*[¥￥]?\s*(\d+(?:\.\d+)?)\s*元?",
        r"[¥￥]\s*(\d+(?:\.\d+)?)",
    ]
    for pattern in patterns:
        m = re.search(pattern, text, re.I)
        if m:
            try:
                value = float(m.group(1))
            except ValueError:
                continue
            if 0 < value < 100000000:
                return value
    return None


def classify(name):
    for category, keys in CATEGORIES:
        if any(k in name for k in keys):
            return category
    return "其他"


def looks_like_transaction(text):
    if any(k in text for k in ACTIVE_WORDS) and not any(k in text for k in ["已成交", "成交价", "成交价格", "落槌", "中标", "得标", "拍得", "结拍"]):
        return False
    return any(k in text for k in TRANSACTION_WORDS)


def extract_item(node, page_url, source):
    text = clean(node.get_text(" ", strip=True))
    if len(text) < 8 or len(text) > 900:
        return None
    if not looks_like_transaction(text):
        return None
    price = extract_price(text)
    if price is None:
        return None

    # Prefer the item's own anchor. This is the original post/listing URL, not the source homepage.
    anchor = node.find("a", href=True)
    if not anchor:
        return None
    item_url = urljoin(page_url, anchor.get("href"))
    if not item_url.startswith(("http://", "https://")):
        return None

    title_node = node.find(["h1","h2","h3","h4","strong","b"])
    title = clean(title_node.get_text(" ", strip=True) if title_node else anchor.get_text(" ", strip=True))
    if len(title) < 2:
        title = text[:120]
    title = re.sub(r"(?:成交价格|成交价|落槌价|中标价|得标价|最终价|拍得|成交|落槌|中标|得标)\s*[:：]?\s*[¥￥]?\s*\d[\d,]*(?:\.\d+)?\s*元?", "", title).strip(" -|：:")

    # Use the image attached to this exact item node. Do not substitute a generic coin image.
    img = node.find("img", src=True)
    image_url = urljoin(page_url, img.get("src")) if img else None
    if image_url and not image_url.startswith(("http://", "https://")):
        image_url = None
    if not image_url:
        # If the item itself has no image, reject it so price/image pairing stays truthful.
        return None

    return {
        "name": title[:160],
        "price": price,
        "currency": "CNY",
        "date": datetime.now().astimezone().strftime("%Y-%m-%d"),
        "provider_id": source["provider_id"],
        "source_name": source["source_name"],
        "source_page_url": page_url,
        "item_url": item_url,
        "image_url": image_url,
        "category": classify(title),
        "transaction_confirmed": True,
        "type": "公开页面已确认成交",
    }


def discover_links(html, page_url):
    soup = BeautifulSoup(html, "html.parser")
    host = urlparse(page_url).netloc
    links = []
    seen = set()
    for a in soup.find_all("a", href=True):
        url = urljoin(page_url, a["href"]).split("#",1)[0]
        if urlparse(url).netloc != host or url in seen:
            continue
        label = clean(a.get_text(" ", strip=True)).lower()
        if any(k in label for k in ["成交","结拍","拍卖","竞价","交易","历史","商品","拍品","专场","下一页","next"]):
            seen.add(url)
            links.append(url)
    return links[:MAX_PAGES]


def crawl(source):
    session = requests.Session()
    session.headers.update(HEADERS)
    queue = [source["url"]]
    visited = set()
    rows = []
    errors = []
    pages = 0

    while queue and pages < MAX_PAGES and len(rows) < MAX_ROWS:
        page_url = queue.pop(0)
        if page_url in visited:
            continue
        visited.add(page_url)
        try:
            response = session.get(page_url, timeout=TIMEOUT, allow_redirects=True)
            response.raise_for_status()
            response.encoding = response.apparent_encoding or response.encoding
            pages += 1
            soup = BeautifulSoup(response.text, "html.parser")
            for node in soup.find_all(["tr","li","article","div"], limit=7000):
                item = extract_item(node, response.url, source)
                if item:
                    rows.append(item)
                    if len(rows) >= MAX_ROWS:
                        break
            if len(rows) < MAX_ROWS:
                queue.extend([u for u in discover_links(response.text, response.url) if u not in visited and u not in queue])
        except Exception as exc:
            errors.append(str(exc)[:200])

    # Exact transaction identity: source + original item URL. This prevents mixing prices/images from different listings.
    unique = {}
    for row in rows:
        unique[(row["provider_id"], row["item_url"])] = row
    rows = list(unique.values())[:MAX_ROWS]
    return rows, {"provider_id":source["provider_id"],"source_name":source["source_name"],"source_url":source["url"],"ok":pages > 0,"pages":pages,"rows":len(rows),"errors":errors[:3]}


all_rows = []
status = []
for source in SOURCES:
    rows, info = crawl(source)
    all_rows.extend(rows)
    status.append(info)

# Keep only records with all four key fields: exact item link, exact item image, confirmed price, confirmed transaction.
all_rows = [r for r in all_rows if r.get("item_url") and r.get("image_url") and r.get("price") is not None and r.get("transaction_confirmed")]
all_rows.sort(key=lambda r: (r["category"], r["date"], r["name"]))

# Summary is computed only from confirmed, source-linked transactions.
summary = []
groups = defaultdict(list)
for row in all_rows:
    groups[(row["category"], row["name"])].append(row["price"])
for (category, name), prices in groups.items():
    values = sorted(prices)
    mid = values[len(values)//2] if len(values) % 2 else (values[len(values)//2-1] + values[len(values)//2]) / 2
    summary.append({"category":category,"name":name,"min":min(values),"median":mid,"max":max(values),"samples":len(values)})
summary.sort(key=lambda x:(-x["samples"],x["category"],x["name"]))

payload = {
    "updated_at": datetime.now(timezone.utc).astimezone().isoformat(),
    "scope": "一尘网、钱币天堂、华夏古泉公开成交页面",
    "data_policy": "仅收录能够同时关联到原始商品/拍品链接、该条目原始实物图片和明确成交价格的公开记录；不把挂牌价或进行中的竞价当作成交价。",
    "sources": SOURCES,
    "rows": all_rows,
    "summary": summary,
    "status": status,
}
Path("market-data.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

# The front-end is updated so every row uses the exact image and exact original item link.
index = Path("index.html")
if index.exists():
    html = index.read_text(encoding="utf-8")
    script = r'''<script id="coin-ai-market-script">(function(){function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}function money(n){return Number(n||0).toLocaleString('zh-CN',{maximumFractionDigits:2})}var cats=['古钱','银元','纸币','纪念币','纪念钞','金银币'];function render(d){var rows=d.rows||[];var cards=cats.map(function(cat){var rr=rows.filter(function(r){return r.category===cat}).slice(0,15);var body=rr.length?rr.map(function(r){return '<article class="market-row"><a class="market-item-link" href="'+esc(r.item_url)+'" target="_blank" rel="noopener noreferrer"><img class="market-item-image" src="'+esc(r.image_url)+'" alt="'+esc(r.name)+' 成交实物图" loading="lazy"><div class="market-item-info"><h4>'+esc(r.name)+'</h4><strong>¥'+money(r.price)+'</strong><small>'+esc(r.date)+' · '+esc(r.source_name)+'</small><em>查看原始成交帖 ↗</em></div></a></article>'}).join(''):'<div class="empty">暂无符合“实物图 + 原帖 + 明确成交价”三项条件的成交记录</div>';return '<div class="market"><h3>'+cat+' · 真实成交</h3><div class="market-item-list">'+body+'</div></div>'}).join('');var html='<section class="market-live section"><h2 class="title">📊 洪盛集藏 · 真实成交实物价格表</h2><p class="desc">每条记录均绑定原始商品/拍品链接与该条记录对应的实物图片；正在竞拍、挂牌价和无法核验的记录不进入成交表。</p><div class="market-category-grid">'+cards+'</div><div class="notice">更新时间：'+esc(d.updated_at||'')+'。价格仅作收藏研究参考。点击实物图或“查看原始成交帖”可回到原始页面核验。</div></section>';var old=document.querySelector('.market-live');if(old)old.outerHTML=html;else{var a=document.getElementById('market')||document.getElementById('coins');if(a)a.insertAdjacentHTML('afterend',html)}}fetch('market-data.json?'+Date.now(),{cache:'no-store'}).then(function(r){return r.json()}).then(render).catch(function(){render({rows:[],updated_at:'暂未更新'})});})();</script>'''
    style = r'''<style id="hongsheng-real-transaction-style">.market-live .market-category-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.market-live .market-item-list{display:grid;gap:12px}.market-live .market-row{background:#fffdf8;border:1px solid #ead9b9;border-radius:14px;overflow:hidden}.market-live .market-item-link{display:grid;grid-template-columns:120px 1fr;gap:12px;align-items:center;color:inherit;text-decoration:none;padding:10px}.market-live .market-item-image{width:120px;height:120px;object-fit:contain;background:#f5f1e8;border-radius:10px}.market-live .market-item-info h4{margin:0 0 7px;font-family:"STKaiti","KaiTi","Songti SC",serif;color:#680904;font-size:17px}.market-live .market-item-info strong{display:block;color:#7b3f0a;font-size:19px}.market-live .market-item-info small{display:block;color:#8a7b6d;margin-top:5px}.market-live .market-item-info em{display:inline-block;margin-top:7px;color:#7a4a13;font-style:normal;font-size:12px}.market-live .empty{padding:18px;color:#8a7b6d;text-align:center}.market-live .market-row:hover{box-shadow:0 5px 18px rgba(80,45,10,.1)}@media(max-width:700px){.market-live .market-category-grid{grid-template-columns:1fr}.market-live .market-item-link{grid-template-columns:96px 1fr}.market-live .market-item-image{width:96px;height:96px}}</style>'''
    html = re.sub(r'<script id="coin-ai-market-script">.*?</script>', '', html, flags=re.S)
    html = re.sub(r'<style id="hongsheng-real-transaction-style">.*?</style>', '', html, flags=re.S)
    html = html.replace('</head>', style + '\n</head>', 1) if '</head>' in html else style + html
    html = html.replace('</body>', script + '\n</body>', 1) if '</body>' in html else html + script
    index.write_text(html, encoding='utf-8')

print('source-linked transaction model complete:', len(all_rows))
for info in status:
    print(info['source_name'], info['ok'], 'pages=', info['pages'], 'rows=', info['rows'])
