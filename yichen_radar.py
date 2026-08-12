"""一尘交易雷达 V1

用途：从公开可访问的一尘交易帖子中提取公开的品种、报价、时间等信息，
生成可供首页使用的静态 JSON。当前版本只做公开页面采集与报价/确认文本识别，
不会绕过登录、验证码或反爬限制，也不把单纯的挂牌价冒充真实成交价。
"""
from datetime import datetime, timezone
from html import escape
from urllib.parse import urljoin
import json
import re
import requests
from bs4 import BeautifulSoup

BASES = ["https://www1.pm001.net/", "https://www3.pm001.net/", "https://www4.pm001.net/"]
# 公开搜索入口的关键词。实际页面结构可能变化，因此解析采用宽松规则。
KEYWORDS = ["钱币", "银元", "古钱", "纸币", "纪念币", "金银币", "机制币", "评级币", "纪念钞"]
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CoinAI-News/1.0)"}
TIMEOUT = 12

PRICE_RE = re.compile(r"(?<!\d)(?:¥|￥)?\s*([0-9]{1,7}(?:\.[0-9]{1,2})?)\s*(?:元|/枚|/张|/套|/卷|/盒)?")
CONFIRM_WORDS = ["确认", "成交", "已成交", "要了", "收了", "付款", "中介"]
CANCEL_WORDS = ["不成交", "取消", "不要了", "撤单", "未成交"]


def get(url):
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    r.encoding = r.apparent_encoding or r.encoding
    return r.text


def parse_post(url, html):
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    text = soup.get_text(" ", strip=True)
    if not any(k in text or k in title for k in KEYWORDS):
        return None
    # 页面通常包含标题、正文和时间。只截取交易相关文字，避免保存个人联系方式。
    date_match = re.search(r"(20\d{2}/\d{1,2}/\d{1,2}\s+\d{1,2}:\d{2}:\d{2})", text)
    published = date_match.group(1) if date_match else ""
    prices = []
    for m in PRICE_RE.finditer(text[:12000]):
        try:
            p = float(m.group(1))
            if 1 <= p <= 9999999:
                prices.append(p)
        except ValueError:
            pass
    confirmed = any(w in text for w in CONFIRM_WORDS)
    cancelled = any(w in text for w in CANCEL_WORDS)
    if cancelled:
        status = "取消/未成交"
    elif confirmed:
        status = "疑似确认/成交"
    else:
        status = "挂牌/待确认"
    return {
        "title": re.sub(r"\[.*?\]", "", title).strip(),
        "url": url,
        "published": published,
        "prices": prices[:20],
        "status": status,
        "is_confirmed": confirmed and not cancelled,
    }


def collect():
    # 先用公开站点的可索引页面作为种子；不执行绕过验证的操作。
    results = []
    for base in BASES:
        try:
            html = get(base)
        except Exception as e:
            print("一尘访问失败", base, e)
            continue
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = urljoin(base, a["href"])
            label = a.get_text(" ", strip=True)
            if "dispbbs" in href and any(k in label for k in KEYWORDS):
                links.append(href)
        for url in list(dict.fromkeys(links))[:30]:
            try:
                post = parse_post(url, get(url))
                if post:
                    results.append(post)
            except Exception as e:
                print("帖子解析失败", url, e)
    unique = {}
    for x in results:
        unique[x["url"]] = x
    return list(unique.values())


posts = collect()
confirmed = [p for p in posts if p["is_confirmed"] and p["prices"]]
for p in posts:
    p["price_min"] = min(p["prices"]) if p["prices"] else None
    p["price_max"] = max(p["prices"]) if p["prices"] else None

out = {
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "source": "公开可访问的一尘交易帖子",
    "notice": "挂牌价不等于成交价；仅在帖子文本出现确认/成交等公开表述时标记为疑似确认，最终成交需人工复核。",
    "total_posts": len(posts),
    "confirmed_posts": len(confirmed),
    "posts": posts[:100],
}
with open("yichen_data.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

rows = []
for p in confirmed[:30]:
    price = f"¥{p['price_min']:g}" if p['price_min'] == p['price_max'] else f"¥{p['price_min']:g}–¥{p['price_max']:g}"
    rows.append(f"<tr><td>{escape(p['title'][:80])}</td><td>{price}</td><td>疑似确认/成交</td><td>{escape(p['published'])}</td><td><a href=\"{escape(p['url'], quote=True)}\" target=\"_blank\" rel=\"noopener\">原帖</a></td></tr>")

html = '''<section id="yichen" class="yichen-radar"><div class="yr-head"><div><span class="yr-kicker">MARKET RADAR</span><h2>🔥 一尘交易成交雷达</h2><p>公开交易帖子 · 报价追踪 · 确认/成交文本识别</p></div><div class="yr-stat"><b>''' + str(len(confirmed)) + '''</b><span>疑似确认/成交帖</span></div></div><div class="yr-note">⚠️ 一尘帖子中的挂牌价格不等于实际成交价格。只有帖子出现“确认/成交”等公开文字时才标记为“疑似确认/成交”，数据仅供行情研究，建议打开原帖人工核实。</div><div class="yr-table-wrap"><table><thead><tr><th>品种/帖子</th><th>价格</th><th>状态</th><th>时间</th><th>来源</th></tr></thead><tbody>''' + (''.join(rows) if rows else '<tr><td colspan="5">本次运行未发现可确认的公开成交记录，系统将在下一次任务继续采集。</td></tr>') + '''</tbody></table></div><p class="yr-source">数据源：公开可访问的一尘交易帖子。系统不绕过登录、验证码或访问控制。</p></section>'''
with open("yichen_radar.html", "w", encoding="utf-8") as f:
    f.write(html)
print("一尘雷达完成：", len(posts), "帖子，", len(confirmed), "疑似确认/成交")
