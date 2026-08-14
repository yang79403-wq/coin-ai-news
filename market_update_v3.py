import json
import re
import time
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.5",
}
TIMEOUT = 25
MAX_LIST = 12
MAX_DETAIL = 180
MAX_ROWS = 300

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
    },
    {
        "provider_id": "yy11",
        "source_name": "钱币天堂",
        "url": "https://www.yy11.com/c2c/forum/4.html",
        "seeds": ["https://www.yy11.com/c2c/forum/4.html"],
    },
    {
        "provider_id": "huaxia",
        "source_name": "华夏古泉",
        "url": "https://www.hxguquan.com/",
        "seeds": [
            "https://www.hxguquan.com/",
            "https://wwwn.hxguquan.com/",
            "https://www.hxguquan.com/goods-list.html?gid=76167",
        ],
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

TRANSACTION_WORDS = [
    "成交价", "成交价格", "成交金额", "物品成交价", "已成交", "成交于", "成交", "落槌价", "落槌",
    "中标价", "中标", "得标价", "得标", "拍得", "结拍", "结标", "已结标", "竞价成功", "竞买成功",
    "已售", "售出", "已卖", "交易成功", "交易完成", "确认成交", "确认售出",
]
ACTIVE_WORDS = ["拍卖中", "竞拍中", "竞价中", "正在拍", "待拍", "尚未结拍", "尚未结标", "出价中", "进行中", "预展中"]


def clean(v):
    return " ".join(unescape(str(v or "")).replace("\xa0", " ").split())


def make_session():
    s = requests.Session()
    s.headers.update(HEADERS)
    retry = Retry(total=4, connect=4, read=4, status=4, backoff_factor=1.2,
                  status_forcelist=(429, 500, 502, 503, 504),
                  allowed_methods=frozenset(["GET", "HEAD"]))
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    return s


def get(s, url, referer=None):
    h = {"Referer": referer} if referer else {}
    r = s.get(url, timeout=TIMEOUT, allow_redirects=True, headers=h)
    r.raise_for_status()
    r.encoding = r.apparent_encoding or r.encoding
    return r


def category(name):
    for c, keys in CATEGORY_KEYS.items():
        if any(k in name for k in keys):
            return c
    return "其他"


def extract_price(text, provider):
    t = clean(text).replace(",", "")
    patterns = [
        r"(?:物品成交价|成交金额|成交价格|成交价|结标价|落槌价|中标价|得标价|最终成交|最终价|拍得|落槌|中标|得标)\s*[:：=]?\s*(?:RMB|人民币|￥|¥)?\s*(\d+(?:\.\d+)?)",
        r"(?:成交于|成交)\s*[:：]?\s*(?:RMB|人民币|￥|¥)?\s*(\d+(?:\.\d+)?)",
        r"(?:price|dealPrice|deal_price|finalPrice|final_price|soldPrice|sold_price)\"?\s*[:=]\s*\"?(\d+(?:\.\d+)?)",
    ]
    for p in patterns:
        for m in re.finditer(p, t, re.I):
            try:
                v = float(m.group(1))
            except ValueError:
                continue
            if 0 < v < 100000000:
                return v
    return None


def has_confirmed_transaction(text, provider):
    t = clean(text)
    if provider == "yy11":
        return "成交于" in t or "物品成交价" in t or "成交价" in t or "已成交" in t or "竞价成功" in t
    if provider == "huaxia":
        return any(x in t for x in ["已结标", "竞价成功", "历史价格", "成交价", "成交价格", "结标"])
    # 一尘网不是标准拍卖站，挂牌价不等于成交价。只接受明确交易完成语义。
    return any(x in t for x in ["已成交", "成交确认", "确认成交", "已售", "售出", "确认售出", "交易成功", "交易完成", "已卖"])


def choose_image(soup, page_url):
    for meta in soup.find_all("meta"):
        key = (meta.get("property") or meta.get("name") or "").lower()
        if key in ("og:image", "twitter:image") and meta.get("content"):
            u = urljoin(page_url, meta["content"])
            if u.startswith(("http://", "https://")):
                return u
    best = None
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or img.get("data-original")
        if not src:
            continue
        u = urljoin(page_url, src)
        low = u.lower()
        if not u.startswith(("http://", "https://")):
            continue
        if any(k in low for k in ["logo", "icon", "avatar", "qrcode", "favicon", "spacer"]):
            continue
        w = int(re.sub(r"\D", "", str(img.get("width") or "0")) or 0)
        h = int(re.sub(r"\D", "", str(img.get("height") or "0")) or 0)
        score = w * h
        if score == 0:
            score = len(clean(img.get("alt") or img.get("title"))) * 100
        if best is None or score > best[0]:
            best = (score, u)
    return best[1] if best else None


def page_title(soup):
    for selector in [("meta", {"property": "og:title"}), ("meta", {"name": "twitter:title"})]:
        n = soup.find(selector[0], attrs=selector[1])
        if n and n.get("content"):
            return clean(n["content"])[:180]
    for tag in ["h1", "h2", "title"]:
        n = soup.find(tag)
        if n and clean(n.get_text(" ", strip=True)):
            return clean(n.get_text(" ", strip=True))[:180]
    return ""


def links_from_page(soup, page_url, provider):
    out = []
    seen = set()
    host = urlparse(page_url).netloc.lower()
    for a in soup.find_all("a", href=True):
        u = urljoin(page_url, a["href"]).split("#", 1)[0]
        if urlparse(u).netloc.lower() != host or u in seen:
            continue
        low = (clean(a.get_text(" ", strip=True)) + " " + u).lower()
        if provider == "yy11":
            ok = "/c2c/topic/" in low or "/c2c/forum/4" in low
        elif provider == "yichen":
            ok = "dispbbs.asp" in low or "topicother.asp" in low or "list.asp" in low
        else:
            ok = "goods-detail.html" in low or "goods-list.html" in low or "history" in low
        if ok:
            seen.add(u)
            out.append(u)
        if len(out) >= MAX_DETAIL:
            break
    return out


def parse_detail(s, url, src):
    try:
        r = get(s, url, src["url"])
    except Exception:
        return None
    soup = BeautifulSoup(r.text, "html.parser")
    visible = clean(soup.get_text(" ", strip=True))
    scripts = " ".join(clean(x.get_text(" ", strip=True)) for x in soup.find_all("script"))
    raw = visible + " " + scripts + " " + r.text
    if not has_confirmed_transaction(raw, src["provider_id"]):
        return None
    p = extract_price(raw, src["provider_id"])
    if p is None:
        return None
    img = choose_image(soup, r.url)
    if not img:
        return None
    name = page_title(soup).strip(" -|：:")
    if len(name) < 2:
        return None
    return {
        "name": name,
        "price": p,
        "currency": "CNY",
        "date": datetime.now().astimezone().strftime("%Y-%m-%d"),
        "provider_id": src["provider_id"],
        "source_name": src["source_name"],
        "source_page_url": r.url,
        "item_url": r.url,
        "image_url": img,
        "category": category(name),
        "transaction_confirmed": True,
        "verification": "原始成交/结标页面核验",
    }


def crawl(src):
    s = make_session()
    queue = list(src["seeds"])
    visited = set()
    details = []
    seen_detail = set()
    rows = []
    errors = []
    pages = 0
    used = None
    while queue and pages < MAX_LIST and len(details) < MAX_DETAIL:
        u = queue.pop(0)
        if u in visited:
            continue
        visited.add(u)
        try:
            r = get(s, u, src["url"])
            used = used or r.url
            pages += 1
            soup = BeautifulSoup(r.text, "html.parser")
            for x in links_from_page(soup, r.url, src["provider_id"]):
                if x not in seen_detail:
                    seen_detail.add(x)
                    details.append(x)
            # 继续跟进分页/列表链接
            for a in soup.find_all("a", href=True):
                x = urljoin(r.url, a["href"]).split("#", 1)[0]
                low = x.lower()
                if urlparse(x).netloc.lower() == urlparse(r.url).netloc.lower() and x not in visited:
                    if src["provider_id"] == "yy11" and "/c2c/forum/4.html" in low:
                        queue.append(x)
                    elif src["provider_id"] == "yichen" and ("list.asp" in low or "index.asp" in low):
                        queue.append(x)
                    elif src["provider_id"] == "huaxia" and "goods-list.html" in low:
                        queue.append(x)
        except Exception as e:
            errors.append(f"{type(e).__name__}: {str(e)[:180]}")
    for u in details[:MAX_DETAIL]:
        row = parse_detail(s, u, src)
        if row:
            rows.append(row)
        time.sleep(0.1)
    unique = {}
    for row in rows:
        unique[(row["provider_id"], row["item_url"])] = row
    rows = list(unique.values())[:MAX_ROWS]
    return rows, {
        "provider_id": src["provider_id"],
        "source_name": src["source_name"],
        "source_url": src["url"],
        "used_seed": used,
        "pages": pages,
        "candidate_detail_pages": len(details),
        "rows": len(rows),
        "ok": pages > 0,
        "errors": errors[:10],
    }


all_rows = []
status = []
for source in SOURCES:
    rows, info = crawl(source)
    all_rows.extend(rows)
    status.append(info)

payload = {
    "updated_at": datetime.now(timezone.utc).astimezone().isoformat(),
    "scope": "一尘网、钱币天堂、华夏古泉公开成交/结标页面",
    "data_policy": "挂牌价、当前竞价、求购价、流标记录均不作为成交价；必须保存原始商品/拍品链接、同页实物图和明确成交语义。",
    "sources": SOURCES,
    "rows": all_rows,
    "status": status,
    "verification": {
        "verified_count": len(all_rows),
        "verified_at": datetime.now(timezone.utc).astimezone().isoformat(),
        "policy": "原帖链接 + 原帖实物图片 + 明确成交/结标状态 + 成交价格",
    },
}
Path("market-data.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print("V3 source-linked transaction rows:", len(all_rows))
for x in status:
    print(x["source_name"], "pages=", x["pages"], "candidate=", x["candidate_detail_pages"], "rows=", x["rows"], "errors=", x["errors"])
