from datetime import datetime, timezone
from html import escape
from urllib.parse import quote
import json
import feedparser

FEEDS = [("收藏热点", "钱币 收藏"),("古钱币", "古钱币"),("银元银币", "银元 银币"),("纸币", "纸币 收藏"),("纪念币", "纪念币 金银币"),("拍卖行情", "钱币 拍卖")]
MAX_PER_FEED = 8
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
    return "https://news.google.com/rss/search?q=" + quote(query) + "&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"

articles = []
for category, query in FEEDS:
    try:
        feed = feedparser.parse(feed_url(query))
        for item in feed.entries[:MAX_PER_FEED]:
            title = clean_text(item.get("title")); link = item.get("link", "")
            summary = clean_text(item.get("summary", "")); source = clean_text(item.get("source", {}).get("title", ""))
            if title and link:
                articles.append({"category":category,"title":title,"link":link,"summary":summary or "暂无摘要","source":source or "公开资讯源","published":parse_date(item)})
    except Exception as exc:
        print("RSS错误:", query, exc)

seen=set(); clean_articles=[]
for article in sorted(articles,key=lambda x:x["published"],reverse=True):
    key=article["title"].lower()
    if key in seen: continue
    seen.add(key)
    article["published_text"]=article["published"].astimezone().strftime("%m-%d %H:%M") if article["published"] != datetime.min.replace(tzinfo=timezone.utc) else ""
    clean_articles.append(article)
clean_articles=clean_articles[:MAX_ARTICLES]
now=datetime.now().astimezone()

if clean_articles:
    headline=clean_articles[0]["title"]
    ai_summary=f"AI自动编排：今日首先关注「{headline}」。系统持续从收藏热点、古钱币、银元、纸币、纪念币及拍卖行情中筛选公开资讯，供藏友研究参考。"
else:
    headline="今日钱币资讯正在采集"
    ai_summary="AI自动采集任务暂未取得新资讯，系统会在下一次任务中自动重试。"

payload={"updated_at":now.strftime("%Y-%m-%d %H:%M:%S"),"headline":headline,"ai_summary":ai_summary,"count":len(clean_articles),"articles":[{k:(v.isoformat() if k=="published" else v) for k,v in a.items()} for a in clean_articles]}
with open("news-data.json","w",encoding="utf-8") as f: json.dump(payload,f,ensure_ascii=False,indent=2)

cards=[]
for a in clean_articles:
    cards.append(f'<article class="ncard"><div class="nmeta"><span>{escape(a["category"])}</span><span>{escape(a["source"])}</span><span>{escape(a["published_text"])}</span></div><h3>{escape(a["title"])}</h3><p>{escape(a["summary"][:220])}</p><a href="{escape(a["link"],quote=True)}" target="_blank" rel="noopener noreferrer">查看原文 →</a></article>')

news_html=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>币智通 AI · 每日钱币资讯</title><style>body{{margin:0;background:#f7f1e7;color:#2b211c;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}}header{{padding:34px 18px;background:linear-gradient(135deg,#320000,#850707,#b8860b);color:#fff}}main{{max-width:1000px;margin:auto;padding:20px}}.hero,.ncard{{background:#fff;border-radius:16px;padding:20px;margin-bottom:14px;box-shadow:0 5px 20px #4a160012}}.hero h1{{margin:0 0 10px;color:#6b0000}}.nmeta{{display:flex;gap:10px;flex-wrap:wrap;font-size:12px;color:#999}}.ncard h3{{font-size:18px;line-height:1.5;margin:9px 0}}.ncard p{{color:#666;line-height:1.7}}.ncard a{{color:#760000;font-weight:800;text-decoration:none}}</style></head><body><header><div>COIN AI NEWS</div><h1>🪙 币智通 AI 每日钱币资讯</h1><div>自动采集时间：{now.strftime("%Y-%m-%d %H:%M:%S")}</div></header><main><section class="hero"><h1>🔥 今日钱币头条</h1><h2>{escape(headline)}</h2><p>{escape(ai_summary)}</p></section>{''.join(cards) if cards else '<div class="hero">暂无新资讯，下一次任务自动重试。</div>'}</main></body></html>'''
with open("news.html","w",encoding="utf-8") as f: f.write(news_html)
print("每日资讯已生成：",len(clean_articles))
