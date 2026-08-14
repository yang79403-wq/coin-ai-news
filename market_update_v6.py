import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib import robotparser

import requests
from bs4 import BeautifulSoup

BOT_NAME = "HongshengCoinBot/6.0"
HEADERS = {"User-Agent": f"Mozilla/5.0 (compatible; {BOT_NAME}; +https://yang79403-wq.github.io/coin-ai-news/)"}
TIMEOUT = 20
REQUEST_DELAY = 0.7
MAX_PAGES_PER_SOURCE = 900
MAX_ROWS_PER_SOURCE = 1200
MAX_QUEUE = 1200

SOURCES = [
    {
        "id": "yichen",
        "name": "一尘网",
        "seeds": [
            "http://www.pm001.net/index.asp",
            "http://www1.pm001.net/index.asp",
            "http://www2.pm001.net/index.asp",
            "http://www3.pm001.net/index.asp",
        ],
        "allowed_paths": ("/index", "/dispbbs.asp"),
        "topic_markers": ("dispbbs.asp",),
        "forum_markers": ("boardid=",),
    },
    {
        "id": "yy11",
        "name": "钱币天堂",
        "seeds": ["https://www.yy11.com/c2c/forum/4.html"],
        "allowed_paths": ("/c2c/forum/", "/c2c/topic/"),
        "topic_markers": ("/c2c/topic/",),
        "forum_markers": ("/c2c/forum/",),
    },
]

CATEGORIES = {
    "纸币": ["纸币", "钞票", "人民币", "连体钞", "钞"],
    "纪念钞": ["纪念钞", "纪念券"],
    "纪念币": ["纪念币", "流通纪念", "生肖纪念"],
    "金银币": ["金币", "银币", "金银币", "熊猫币", "贵金属"],
    "银元": ["银元", "袁大头", "孙小头", "船洋", "龙洋", "大洋", "七钱二分", "银圆"],
    "古钱币": ["古钱", "通宝", "重宝", "元宝", "五铢", "半两", "刀币", "布币", "咸丰", "嘉庆", "康熙"],
    "铜元": ["铜元", "铜板", "大清铜币", "光绪元宝", "铜圆"],
    "硬币": ["硬币", "流通币", "分币", "角币", "一分", "五分", "一角"],
    "福建钱币": ["福建", "闽省", "福州", "厦门", "泉州", "漳州", "闽"],
}

TRANSACTION_MARKERS = (
    "物品成交价", "成交价格", "成交价", "成交金额", "结标价", "中标价", "得标价",
    "落槌价", "落槌", "拍得", "已成交", "交易成功", "交易完成", "确认成交", "确认售出",
    "成交于", "已结标", "已售出"
)
WANTED_MARKERS = ("求购", "收购价", "收购", "买入价", "买入", "高价求", "求一个", "求购价")
ACTIVE_MARKERS = ("拍卖中", "竞拍中", "竞价中", "进行中", "预展中", "尚未结拍", "尚未结标")
NO_RESULT_MARKERS = ("已流拍", "无人出价", "暂无记录", "未成交", "流标")

PRICE_PATTERNS = [
    r"(?:物品成交价|成交价格|成交价|成交金额|结标价|中标价|得标价|落槌价|收购价|求购价|买入价)\s*[:：=]?\s*(?:人民币|RMB|CNY|￥|¥)?\s*([0-9]{1,3}(?:[,，][0-9]{3})*(?:\.\d+)?)",
    r"(?:成交于|成交|中标|得标|落槌|拍得|售出|收购|求购|买入)\s*[:：=]?\s*(?:人民币|RMB|CNY|￥|¥)?\s*([0-9]{1,3}(?:[,，][0-9]{3})*(?:\.\d+)?)",
]


def clean(text):
    return " ".join(str(text or "").replace("\xa0", " ").split())


def price_values(text):
    text = clean(text).replace("，", ",")
    values = []
    for pattern in PRICE_PATTERNS:
        for match in re.finditer(pattern, text, re.I):
            try:
                value = float(match.group(1).replace(",", ""))
            except ValueError:
                continue
            if 0 < value < 100_000_000:
                values.append(value)
    return list(dict.fromkeys(values))


def page_title(soup):
    for tag in ("h1", "h2", "title"):
        node = soup.find(tag)
        if node:
            value = clean(node.get_text(" ", strip=True))
            if value:
                return value[:200]
    return ""


def image_url(soup, page):
    meta = soup.find("meta", attrs={"property": re.compile("^og:image$", re.I)})
    if meta and meta.get("content"):
        return urljoin(page, meta["content"])
    for img in soup.find_all("img"):
        value = img.get("src") or img.get("data-src") or img.get("data-original")
        if not value:
            continue
        value = urljoin(page, value)
        low = value.lower()
        if value.startswith("http") and not any(x in low for x in ("logo", "icon", "avatar", "qrcode", "spacer")):
            return value
    return ""


def classify(text):
    hits = []
    for category, keys in CATEGORIES.items():
        if any(key in text for key in keys):
            hits.append(category)
    if "福建钱币" in hits and len(hits) > 1:
        hits.remove("福建钱币")
    return hits[0] if hits else "其他"


def transaction_state(text, values):
    has_wanted = any(marker in text for marker in WANTED_MARKERS)
    has_transaction = any(marker in text for marker in TRANSACTION_MARKERS)
    active = any(marker in text for marker in ACTIVE_MARKERS)
    no_result = any(marker in text for marker in NO_RESULT_MARKERS)

    if has_wanted and values:
        return "求购", True
    if has_transaction and values and not active and not no_result:
        return "成交", True
    return None, False


def allowed_link(source, page, href):
    absolute = urljoin(page, href).split("#", 1)[0]
    parsed = urlparse(absolute)
    host = urlparse(page).netloc.lower()
    if parsed.netloc.lower() != host:
        return None
    path = parsed.path.lower()
    if not any(marker in path or marker in absolute.lower() for marker in source["allowed_paths"]):
        return None
    return absolute


def discover_links(source, soup, page):
    links = []
    for anchor in soup.find_all("a", href=True):
        value = allowed_link(source, page, anchor["href"])
        if value:
            links.append(value)
    return list(dict.fromkeys(links))


def robots_allowed(url):
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    parser = robotparser.RobotFileParser()
    parser.set_url(robots_url)
    try:
        parser.read()
        return parser.can_fetch(HEADERS["User-Agent"], url)
    except Exception:
        return True


def crawl_source(source):
    session = requests.Session()
    queue = list(source["seeds"])
    seen = set()
    rows = []
    pages = 0
    errors = 0
    discovered_forums = set()
    discovered_topics = set()

    while queue and pages < MAX_PAGES_PER_SOURCE and len(rows) < MAX_ROWS_PER_SOURCE:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)

        if not robots_allowed(url):
            continue

        try:
            time.sleep(REQUEST_DELAY)
            response = session.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
            response.raise_for_status()
            response.encoding = response.apparent_encoding or response.encoding
            pages += 1
        except Exception:
            errors += 1
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        text = clean(soup.get_text(" ", strip=True))
        title = page_title(soup)
        combined = f"{title} {text[:8000]}"
        values = price_values(combined)
        state, confirmed = transaction_state(combined, values)

        if source["topic_markers"] and any(marker in response.url.lower() for marker in source["topic_markers"]):
            discovered_topics.add(response.url)
        if source["forum_markers"] and any(marker in response.url.lower() for marker in source["forum_markers"]):
            discovered_forums.add(response.url)

        if confirmed and title and values:
            image = image_url(soup, response.url)
            category = classify(combined)
            for value in values[:3]:
                rows.append({
                    "name": title,
                    "category": category,
                    "state": state,
                    "price": value,
                    "currency": "CNY",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "source_name": source["name"],
                    "source_url": response.url,
                    "item_url": response.url,
                    "image_url": image,
                    "transaction_confirmed": state == "成交",
                    "verification": "公开页面明确价格字段 + 状态规则核验",
                })

        for link in discover_links(source, soup, response.url):
            if link not in seen and len(queue) < MAX_QUEUE:
                queue.append(link)

    unique = {}
    for row in rows:
        key = (row["source_name"], row["item_url"], row["state"], row["price"], row["name"])
        unique[key] = row

    return list(unique.values()), {
        "source": source["name"],
        "pages_scanned": pages,
        "rows": len(unique),
        "forums_discovered": len(discovered_forums),
        "topics_discovered": len(discovered_topics),
        "errors": errors,
    }


def build_tables(rows):
    tables = {}
    for row in rows:
        tables.setdefault(row["category"], []).append(row)
    for category in tables:
        tables[category].sort(key=lambda x: (x["name"], x["state"], -x["price"]))
    return tables


all_rows = []
source_status = []
for source in SOURCES:
    rows, status = crawl_source(source)
    all_rows.extend(rows)
    source_status.append(status)

payload = {
    "version": "V6",
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "sources": [source["name"] for source in SOURCES],
    "rows": all_rows,
    "tables": build_tables(all_rows),
    "status": source_status,
    "policy": "成交与求购严格分离；只收录公开页面明确价格；不把挂牌价或进行中竞价当作成交价；保留来源页面；尊重robots规则并限速。",
}

Path("price-tables.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print("V6 price-table rows:", len(all_rows))
for status in source_status:
    print(status)
