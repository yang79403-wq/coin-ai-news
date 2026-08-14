import json
import re
import time
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.5",
}
TIMEOUT = 25
MAX_LIST = 12
MAX_DETAILS = 160
MAX_ROWS = 300
JINA = "https://r.jina.ai/http://"

SOURCES = [
    {
        "provider_id": "yichen",
        "source_name": "一尘网",
        "url": "https://www.pm001.net/index.asp",
        "seeds": [
            "https://www.pm001.net/index.asp",
            "https://www1.pm001.net/index.asp",
            "https://www2.pm001.net/index.asp",
            "https://www3.pm001.net/index.asp",
        ],
        "proxy": True,
    },
    {
        "provider_id": "yy11",
        "source_name": "钱币天堂",
        "url": "https://www.yy11.com/c2c/forum/4.html",
        "seeds": ["https://www.yy11.com/c2c/forum/4.html"],
        "proxy": False,
    },
    {
        "provider_id": "huaxia",
        "source_name": "华夏古泉",
        "url": "https://www.hxguquan.com/",
        "seeds": [
            "https://www.hxguquan.com/",
            "https://www.hxguquan.com/goods-list.html?gid=76167",
        ],
        "proxy": False,
    },
]

CATEGORY_KEYS = {
    "古钱": ["古钱", "通宝", "重宝", "元宝", "五铢", "半两", "方孔", "刀币", "布币"],
    "银元": ["银元", "袁大头", "袁世凯", "大洋", "龙洋", "银币", "七钱二分"],
    "纸币": ["纸币", "人民币", "老钞", "钞票", "纸钞"],
    "纪念币": ["纪念币", "生肖币", "流通纪念币"],
    "纪念钞": ["纪念钞", "纪念钞票"],
    "金银币": ["金币", "金银币", "金条", "银条", "贵金属币"],
}

NEGATIVE = ["已流拍", "流标", "无人出价", "拍卖中", "竞拍中", "竞价中", "预展中", "待拍", "待处理", "出价中"]
CONFIRM = ["物品成交价", "成交金额", "成交价格", "成交价", "已成交", "成交于", "落槌价", "落槌", "中标价", "中标", "得标价", "得标", "拍得", "结拍", "结标", "已结标", "竞价成功", "竞买成功", "已售", "售出", "已卖", "交易成功", "交易完成", "确认成交", "确认售出"]


def clean(x):
    return " ".join(unescape(str(x or "")).replace("\xa0", " ").split())


def category(name):
    for c, keys in CATEGORY_KEYS.items():
        if any(k in name for k in keys):
            return c
    return "其他"


def fetch(session, url, referer=None, use_proxy=False):
    headers = dict(HEADERS)
    if referer:
        headers["Referer"] = referer
    try:
        r = session.get(url, timeout=TIMEOUT, allow_redirects=True, headers=headers)
        r.raise_for_status()
        r.encoding = r.apparent_encoding or r.encoding
        return r, False
    except Exception:
        if not use_proxy:
            raise
        proxy_url = JINA + url.replace("https://", "").replace("http://", "")
        r = session.get(proxy_url, timeout=TIMEOUT, allow_redirects=True, headers={"User-Agent": HEADERS["User-Agent"]})
        r.raise_for_status()
        r.encoding = "utf-8"
        return r, True


def extract_price(raw):
    t = clean(raw).replace(",", "")
    # First prefer explicit transaction labels. This avoids confusing start/current bids with sale prices.
    patterns = [
        r"(?:物品成交价|成交金额|成交价格|成交价|结标价|落槌价|中标价|得标价|最终成交价|最终成交|最终价)\s*(?:</?[^>]+>\s*)*[:：=]?\s*(?:RMB|人民币|￥|¥)?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:元|RMB|人民币)?",
        r"(?:price|dealPrice|deal_price|finalPrice|final_price|soldPrice|sold_price|成交金额|成交价格|成交价)\s*[\"']?\s*[:=]\s*[\"']?\s*(?:RMB|人民币|￥|¥)?\s*([0-9]+(?:\.[0-9]+)?)",
        r"(?:成交于|中标|得标|拍得|落槌|结标|结拍)\s*(?:[:：=]|为)?\s*(?:RMB|人民币|￥|¥)?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:元|RMB|人民币)?",
    ]
    for p in patterns:
        m = re.search(p, t, re.I)
        if m:
            v = float(m.group(1))
            if 0 < v < 100000000:
                return v
    # Search JSON/HTML data attributes near transaction keys.
    for key in ["dealPrice", "deal_price", "soldPrice", "sold_price", "finalPrice", "final_price", "成交价", "成交金额"]:
        m = re.search(rf"{re.escape(key)}\s*[\"']?\s*[:=]\s*[\"']?\s*([0-9]+(?:\.[0-9]+)?)", raw, re.I)
        if m:
            v = float(m.group(1))
            if 0 < v < 100000000:
                return v
    return None


def confirmed(raw, provider):
    t = clean(raw)
    if provider == "yy11":
        if "已流拍" in t or "无人出价" in t or "流标" in t:
            return False
        return any(k in t for k in ["物品成交价", "成交于", "已成交", "竞价成功"]) and extract_price(raw) is not None
    if provider == "huaxia":
        if any(k in t for k in ["流拍", "未成交", "无人出价"]):
            return False
        return any(k in t for k in ["已结标", "竞价成功", "成交价", "成交价格", "结标价", "历史价格"]) and extract_price(raw) is not None
    # Yichen is a forum/trading site. Only explicit completed-sale language qualifies.
    if any(k in t for k in ["求购", "收购", "出售", "出价", "报价", "参考价", "行情价"]):
        # These alone are not transaction evidence.
        if not any(k in t for k in ["已成交", "成交确认", "确认成交", "交易成功", "交易完成", "确认售出"]):
            return False
    return any(k in t for k in ["已成交", "成交确认", "确认成交", "交易成功", "交易完成", "确认售出"]) and extract_price(raw) is not None


def image_from(soup, base):
    candidates = []
    for meta in soup.find_all("meta"):
        key = (meta.get("property") or meta.get("name") or "").lower()
        if key in ("og:image", "twitter:image") and meta.get("content"):
            u = urljoin(base, meta["content"])
            if u.startswith(("http://", "https://")):
                return u
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or img.get("data-original") or img.get("data-lazy-src")
        if not src:
            continue
        u = urljoin(base, src)
        if not u.startswith(("http://", "https://")):
            continue
        low = u.lower()
        alt = clean(img.get("alt") or img.get("title"))
        if any(k in low or k in alt.lower() for k in ["logo", "icon", "avatar", "qrcode", "favicon", "广告"]):
            continue
        try:
            area = int(re.sub(r"\D", "", str(img.get("width") or "0"))) * int(re.sub(r"\D", "", str(img.get("height") or "0")))
        except Exception:
            area = 0
        candidates.append((area, len(alt), u))
    if candidates:
        candidates.sort(reverse=True)
        return candidates[0][2]
    return None


def title(soup):
    n = soup.find("meta", attrs={"property": "og:title"})
    if n and n.get("content"):
        return clean(n["content"])[:180]
    for tag in ["h1", "h2", "title"]:
        n = soup.find(tag)
        if n and clean(n.get_text(" ", strip=True)):
            return clean(n.get_text(" ", strip=True))[:180]
    return ""


def detail_links(soup, base, provider):
    out, seen = [], set()
    host = urlparse(base).netloc.lower()
    for a in soup.find_all("a", href=True):
        u = urljoin(base, a["href"]).split("#", 1)[0]
        if urlparse(u).netloc.lower() != host or u in seen:
            continue
        low = u.lower()
        text = clean(a.get_text(" ", strip=True))
        if provider == "yy11":
            ok = "/c2c/topic/" in low
        elif provider == "yichen":
            ok = "dispbbs.asp" in low
        else:
            ok = "goods-detail.html" in low
        if ok:
            seen.add(u)
            out.append(u)
        if len(out) >= MAX_DETAILS:
            break
    return out


def crawl(source):
    s = requests.Session()
    s.headers.update(HEADERS)
    queue = list(source["seeds"])
    visited = set()
    candidates = []
    seen = set()
    pages = 0
    errors = []
    proxy_used = False
    while queue and pages < MAX_LIST:
        u = queue.pop(0)
        if u in visited:
            continue
        visited.add(u)
        try:
            r, proxied = fetch(s, u, source["url"], source.get("proxy", False))
            proxy_used = proxy_used or proxied
            pages += 1
            soup = BeautifulSoup(r.text, "html.parser")
            for x in detail_links(soup, r.url, source["provider_id"]):
                if x not in seen:
                    seen.add(x)
                    candidates.append(x)
            for a in soup.find_all("a", href=True):
                x = urljoin(r.url, a["href"]).split("#", 1)[0]
                if urlparse(x).netloc.lower() != urlparse(r.url).netloc.lower() or x in visited:
                    continue
                low = x.lower()
                if source["provider_id"] == "yy11" and ("/c2c/forum/4.html" in low or "/c2c/forum/" in low):
                    queue.append(x)
                elif source["provider_id"] == "yichen" and "index.asp" in low:
                    queue.append(x)
                elif source["provider_id"] == "huaxia" and "goods-list.html" in low:
                    queue.append(x)
        except Exception as e:
            errors.append(f"{type(e).__name__}: {str(e)[:180]}")
    rows = []
    rejected = []
    for u in candidates[:MAX_DETAILS]:
        try:
            r, proxied = fetch(s, u, source["url"], source.get("proxy", False))
            proxy_used = proxy_used or proxied
            soup = BeautifulSoup(r.text, "html.parser")
            visible = clean(soup.get_text(" ", strip=True))
            scripts = " ".join(clean(x.get_text(" ", strip=True)) for x in soup.find_all("script"))
            raw = visible + " " + scripts + " " + r.text
            if not confirmed(raw, source["provider_id"]):
                rejected.append({"url": r.url, "reason": "not_confirmed_or_price_missing"})
                continue
            p = extract_price(raw)
            img = image_from(soup, r.url)
            if not img:
                rejected.append({"url": r.url, "reason": "image_missing"})
                continue
            name = title(soup).strip(" -|：:")
            if len(name) < 2:
                rejected.append({"url": r.url, "reason": "title_missing"})
                continue
            rows.append({
                "name": name,
                "price": p,
                "currency": "CNY",
                "date": datetime.now().astimezone().strftime("%Y-%m-%d"),
                "provider_id": source["provider_id"],
                "source_name": source["source_name"],
                "source_page_url": r.url,
                "item_url": r.url,
                "image_url": img,
                "category": category(name),
                "transaction_confirmed": True,
                "verification": "原始成交/结标页面核验",
            })
        except Exception as e:
            rejected.append({"url": u, "reason": f"{type(e).__name__}: {str(e)[:140]}"})
        time.sleep(0.1)
    unique = {(x["provider_id"], x["item_url"]): x for x in rows}
    return list(unique.values())[:MAX_ROWS], {
        "provider_id": source["provider_id"],
        "source_name": source["source_name"],
        "source_url": source["url"],
        "pages": pages,
        "candidate_detail_pages": len(candidates),
        "rows": len(unique),
        "proxy_used": proxy_used,
        "rejected": rejected[:100],
        "errors": errors[:20],
        "ok": pages > 0,
    }


all_rows, statuses = [], []
for source in SOURCES:
    rows, status = crawl(source)
    all_rows.extend(rows)
    statuses.append(status)

payload = {
    "updated_at": datetime.now(timezone.utc).astimezone().isoformat(),
    "scope": "一尘网、钱币天堂、华夏古泉公开成交/结标页面",
    "data_policy": "只接受原始商品/拍品页面明确成交/结标、明确成交价格、同页实物图和原帖链接；挂牌价、当前竞价、流拍、求购、收购价均排除。",
    "sources": SOURCES,
    "rows": all_rows,
    "status": statuses,
    "verification": {
        "verified_count": len(all_rows),
        "policy": "原帖链接 + 同页实物图片 + 明确成交/结标状态 + 成交价格",
        "verified_at": datetime.now(timezone.utc).astimezone().isoformat(),
    },
}
Path("market-data.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print("V4 verified source-linked rows:", len(all_rows))
for x in statuses:
    print(x["source_name"], "pages=", x["pages"], "candidate=", x["candidate_detail_pages"], "rows=", x["rows"], "proxy=", x["proxy_used"], "errors=", x["errors"])
