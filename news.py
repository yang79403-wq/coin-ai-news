from datetime import datetime, timezone
from html import escape
from urllib.parse import quote

import feedparser


FEEDS = [
    ("收藏热点", "钱币 收藏"),
    ("古钱币", "古钱币"),
    ("银元银币", "银元 银币"),
    ("纸币", "纸币 收藏"),
    ("纪念币", "纪念币 金银币"),
    ("拍卖行情", "钱币 拍卖"),
]

MAX_PER_FEED = 10
MAX_ARTICLES = 40


def clean_text(value):
    return " ".join(str(value or "").split())


def parse_date(item):
    parsed = item.get("published_parsed") or item.get("updated_parsed")
    if parsed:
        try:
            return datetime(*parsed[:6], tzinfo=timezone.utc)
        except Exception:
            pass
    return datetime.min.replace(tzinfo=timezone.utc)


def feed_url(query):
    return (
        "https://news.google.com/rss/search?q="
        + quote(query)
        + "&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    )


articles = []

for category, query in FEEDS:
    try:
        feed = feedparser.parse(feed_url(query))
        for item in feed.entries[:MAX_PER_FEED]:
            title = clean_text(item.get("title"))
            link = item.get("link", "")
            summary = clean_text(item.get("summary", ""))
            source = clean_text(item.get("source", {}).get("title", ""))
            if title and link:
                articles.append({
                    "category": category,
                    "title": title,
                    "link": link,
                    "summary": summary or "暂无摘要",
                    "source": source,
                    "published": parse_date(item),
                })
    except Exception as exc:
        print("RSS错误:", query, exc)

# 标题去重，并优先保留较新的文章
seen = set()
clean_articles = []
for article in sorted(articles, key=lambda x: x["published"], reverse=True):
    key = article["title"].lower()
    if key in seen:
        continue
    seen.add(key)
    clean_articles.append(article)

clean_articles = clean_articles[:MAX_ARTICLES]
today = datetime.now().strftime("%Y-%m-%d")
updated = datetime.now().strftime("%Y-%m-%d %H:%M")

category_counts = {}
for article in clean_articles:
    category_counts[article["category"]] = category_counts.get(article["category"], 0) + 1

cards = []
for article in clean_articles:
    source = article["source"] or "资讯来源"
    published = article["published"].astimezone().strftime("%m-%d %H:%M") if article["published"] != datetime.min.replace(tzinfo=timezone.utc) else ""
    cards.append(f"""
    <article class="card" data-category="{escape(article['category'])}">
      <div class="meta">
        <span class="tag">{escape(article['category'])}</span>
        <span>{escape(source)}</span>
        <span>{published}</span>
      </div>
      <h2>{escape(article['title'])}</h2>
      <p>{escape(article['summary'][:260])}</p>
      <a class="read" href="{escape(article['link'], quote=True)}" target="_blank" rel="noopener noreferrer">查看原文 <span>→</span></a>
    </article>
    """)

cards_html = "\n".join(cards)

category_buttons = ['<button class="filter active" data-filter="全部">全部</button>']
for category, _ in FEEDS:
    if category_counts.get(category, 0):
        category_buttons.append(f'<button class="filter" data-filter="{escape(category)}">{escape(category)}</button>')
filters_html = "".join(category_buttons)

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="币智通AI钱币收藏资讯，自动汇总古钱币、银元、纸币、纪念币与拍卖行情。">
<title>币智通 AI · 钱币资讯</title>
<style>
:root {{ --red:#650000; --gold:#b8860b; --ink:#231f20; --muted:#777; --paper:#f7f3ed; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--paper); color:var(--ink); font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif; }}
header {{ background:linear-gradient(135deg,#4d0000 0%,#7b0505 48%,#b8860b 100%); color:#fff; padding:42px 18px 34px; text-align:center; box-shadow:0 5px 25px rgba(50,0,0,.18); }}
.logo {{ font-size:14px; letter-spacing:3px; opacity:.85; margin-bottom:8px; }}
header h1 {{ margin:0; font-size:34px; letter-spacing:2px; }}
header p {{ margin:12px 0 0; opacity:.9; font-size:15px; }}
.container {{ max-width:980px; margin:0 auto; padding:24px 16px 50px; }}
.dashboard {{ display:grid; grid-template-columns:1fr auto; gap:18px; align-items:center; margin-bottom:18px; }}
.panel {{ background:#fff; border-radius:16px; padding:18px 20px; box-shadow:0 4px 18px rgba(80,50,20,.07); }}
.date {{ font-size:14px; color:var(--muted); }}
.stats {{ display:flex; gap:22px; align-items:center; }}
.stat b {{ display:block; font-size:25px; color:var(--red); }}
.stat span {{ font-size:12px; color:var(--muted); }}
.filters {{ display:flex; gap:8px; overflow:auto; padding-bottom:3px; margin-bottom:18px; }}
.filter {{ border:1px solid #ddd; background:#fff; color:#555; border-radius:999px; padding:9px 14px; cursor:pointer; white-space:nowrap; }}
.filter.active {{ background:var(--red); color:#fff; border-color:var(--red); }}
.card {{ background:#fff; margin-bottom:15px; padding:21px 22px; border-radius:16px; box-shadow:0 3px 14px rgba(80,50,20,.06); transition:transform .15s,box-shadow .15s; }}
.card:hover {{ transform:translateY(-2px); box-shadow:0 7px 22px rgba(80,50,20,.1); }}
.meta {{ display:flex; flex-wrap:wrap; gap:10px; color:#999; font-size:12px; align-items:center; }}
.tag {{ color:var(--red); background:#fff2f0; border-radius:999px; padding:4px 9px; }}
.card h2 {{ margin:10px 0 9px; font-size:19px; line-height:1.5; }}
.card p {{ margin:0 0 15px; color:#666; line-height:1.75; font-size:14px; }}
.read {{ color:var(--red); text-decoration:none; font-weight:600; font-size:14px; }}
.read span {{ margin-left:5px; }}
.empty {{ text-align:center; padding:55px 20px; color:#888; background:#fff; border-radius:16px; }}
footer {{ text-align:center; color:#999; font-size:12px; padding:10px 20px 35px; }}
@media (max-width:700px) {{ header h1{{font-size:28px}} .dashboard{{grid-template-columns:1fr}} .stats{{justify-content:space-between}} .card{{padding:18px}} .card h2{{font-size:17px}} }}
</style>
</head>
<body>
<header>
  <div class="logo">COIN AI NEWS</div>
  <h1>🪙 币智通 AI</h1>
  <p>钱币收藏 · 行情 · 拍卖 · 藏品资讯</p>
</header>
<main class="container">
  <section class="dashboard">
    <div class="panel">
      <div class="date">📅 今日更新：{today}</div>
      <div class="date" style="margin-top:6px">最后生成：{updated} · 每日自动采集</div>
    </div>
    <div class="panel stats">
      <div class="stat"><b>{len(clean_articles)}</b><span>今日资讯</span></div>
      <div class="stat"><b>{len(category_counts)}</b><span>资讯分类</span></div>
    </div>
  </section>
  <nav class="filters" aria-label="资讯分类">{filters_html}</nav>
  <section id="news-list">
    {cards_html if cards_html else '<div class="empty">今天暂时没有抓取到资讯，系统下一次运行会自动重试。</div>'}
  </section>
</main>
<footer>币智通 AI 钱币资讯自动化平台 · 数据来自公开 RSS 资讯源 · 仅供收藏信息参考</footer>
<script>
document.querySelectorAll('.filter').forEach(function(button) {{
  button.addEventListener('click', function() {{
    document.querySelectorAll('.filter').forEach(function(b) {{ b.classList.remove('active'); }});
    button.classList.add('active');
    const filter = button.dataset.filter;
    document.querySelectorAll('.card').forEach(function(card) {{
      card.style.display = (filter === '全部' || card.dataset.category === filter) ? '' : 'none';
    }});
  }});
}});
</script>
</body>
</html>
'''

with open("index.html", "w", encoding="utf-8") as file:
    file.write(html)

print("成功生成资讯：", len(clean_articles))
