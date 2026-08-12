import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime

feeds = [
    "https://news.google.com/rss/search?q=%E9%92%B1%E5%B8%81+%E6%94%B6%E8%97%8F&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
    "https://news.google.com/rss/search?q=%E5%8F%A4%E9%92%B1%E5%B8%81&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
    "https://news.google.com/rss/search?q=%E9%93%B6%E5%85%83&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
    "https://news.google.com/rss/search?q=%E7%BA%B8%E5%B8%81+%E6%94%B6%E8%97%8F&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
]

articles = []

for feed_url in feeds:
    try:
        feed = feedparser.parse(feed_url)

        for item in feed.entries[:10]:
            title = item.get("title", "")
            link = item.get("link", "")
            summary = item.get("summary", "")

            soup = BeautifulSoup(summary, "html.parser")
            summary = soup.get_text(" ", strip=True)

            articles.append({
                "title": title,
                "link": link,
                "summary": summary
            })

    except Exception as e:
        print("RSS错误:", e)

# 去重
seen = set()
clean_articles = []

for article in articles:
    title = article["title"]

    if title not in seen:
        seen.add(title)
        clean_articles.append(article)

clean_articles = clean_articles[:30]

today = datetime.now().strftime("%Y-%m-%d")

html = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>币智通 AI 钱币资讯</title>

<style>

body{
    margin:0;
    background:#f5f5f5;
    font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;
    color:#222;
}

header{
    background:linear-gradient(135deg,#650000,#b8860b);
    color:white;
    padding:35px 20px;
    text-align:center;
}

header h1{
    margin:0;
    font-size:32px;
}

header p{
    margin-top:10px;
    opacity:.9;
}

.container{
    max-width:900px;
    margin:30px auto;
    padding:0 15px;
}

.date{
    margin-bottom:20px;
    color:#777;
}

.card{
    background:white;
    margin-bottom:18px;
    padding:22px;
    border-radius:12px;
    box-shadow:0 3px 12px rgba(0,0,0,.06);
}

.card h2{
    margin-top:0;
    font-size:20px;
}

.card p{
    line-height:1.8;
    color:#555;
}

.card a{
    color:#9b0000;
    text-decoration:none;
}

footer{
    text-align:center;
    color:#888;
    padding:40px;
}

</style>
</head>

<body>

<header>
    <h1>🪙 币智通 AI</h1>
    <p>钱币收藏 · 行情 · 拍卖 · 收藏资讯</p>
</header>

<div class="container">

<div class="date">
    📅 自动更新：TODAY
</div>

NEWS

</div>

<footer>
    币智通 AI 钱币资讯自动化平台
    <br>
    每日自动采集更新
</footer>

</body>
</html>
"""

cards = ""

for article in clean_articles:

    cards += f"""
    <div class="card">

        <h2>🪙 {article['title']}</h2>

        <p>
        {article['summary']}
        </p>

        <a href="{article['link']}" target="_blank">
        查看原文 →
        </a>

    </div>
    """

html = html.replace("TODAY", today)
html = html.replace("NEWS", cards)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("成功生成资讯：", len(clean_articles))

