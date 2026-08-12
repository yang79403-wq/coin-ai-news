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
    return "https://news.google.com/rss/search?q=" + quote(query) + "&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"

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
                articles.append({"category": category, "title": title, "link": link, "summary": summary or "暂无摘要", "source": source, "published": parse_date(item)})
    except Exception as exc:
        print("RSS错误:", query, exc)

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
    cards.append(f'''<article class="card" data-category="{escape(article['category'])}"><div class="meta"><span class="tag">{escape(article['category'])}</span><span>{escape(source)}</span><span>{published}</span></div><h2>{escape(article['title'])}</h2><p>{escape(article['summary'][:260])}</p><a class="read" href="{escape(article['link'], quote=True)}" target="_blank" rel="noopener noreferrer">查看原文 <span>→</span></a></article>''')
cards_html = "\n".join(cards)

category_buttons = ['<button class="filter active" data-filter="全部">全部</button>']
for category, _ in FEEDS:
    if category_counts.get(category, 0):
        category_buttons.append(f'<button class="filter" data-filter="{escape(category)}">{escape(category)}</button>')
filters_html = "".join(category_buttons)

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="币智通AI钱币收藏资讯，自动汇总古钱币、银元、纸币、纪念币、拍卖行情与收藏知识。">
<title>币智通 AI · 钱币资讯</title>
<style>
:root{{--red:#650000;--gold:#b8860b;--ink:#231f20;--muted:#777;--paper:#f7f3ed}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}}
header{{background:linear-gradient(135deg,#4d0000,#7b0505 48%,#b8860b);color:#fff;padding:42px 18px 34px;text-align:center;box-shadow:0 5px 25px rgba(50,0,0,.18)}}
.logo{{font-size:14px;letter-spacing:3px;opacity:.85;margin-bottom:8px}} header h1{{margin:0;font-size:34px;letter-spacing:2px}} header p{{margin:12px 0 0;opacity:.9;font-size:15px}}
.container,.service-wrap{{max-width:980px;margin:0 auto;padding:24px 16px}} .dashboard{{display:grid;grid-template-columns:1fr auto;gap:18px;align-items:center;margin-bottom:18px}}
.panel,.card,.service-card,.price-card{{background:#fff;border-radius:16px;box-shadow:0 4px 18px rgba(80,50,20,.07)}} .panel{{padding:18px 20px}} .date{{font-size:14px;color:var(--muted)} .stats{{display:flex;gap:22px;align-items:center}} .stat b{{display:block;font-size:25px;color:var(--red)}} .stat span{{font-size:12px;color:var(--muted)}}
.filters{{display:flex;gap:8px;overflow:auto;padding-bottom:3px;margin-bottom:18px}} .filter{{border:1px solid #ddd;background:#fff;color:#555;border-radius:999px;padding:9px 14px;cursor:pointer;white-space:nowrap}} .filter.active{{background:var(--red);color:#fff;border-color:var(--red)}}
.card{{margin-bottom:15px;padding:21px 22px}} .meta{{display:flex;flex-wrap:wrap;gap:10px;color:#999;font-size:12px;align-items:center}} .tag{{color:var(--red);background:#fff2f0;border-radius:999px;padding:4px 9px}} .card h2{{margin:10px 0 9px;font-size:19px;line-height:1.5}} .card p{{margin:0 0 15px;color:#666;line-height:1.75;font-size:14px}} .read{{color:var(--red);text-decoration:none;font-weight:600;font-size:14px}}
.section-title{{font-size:24px;color:#650000;margin:30px 0 14px}} .hero{{background:linear-gradient(135deg,#fff8e8,#fff);border-left:5px solid #b8860b;border-radius:16px;padding:20px;margin-bottom:16px}} .hero h2{{margin:0 0 8px;color:#650000}} .hero p{{line-height:1.8;color:#555;margin:5px 0}}
.service-wrap{{padding-top:0}} .service-hero{{background:linear-gradient(135deg,#4d0000,#8a0505 55%,#b8860b);color:#fff;border-radius:18px;padding:24px 22px;margin-bottom:16px}} .service-hero h2{{margin:0 0 10px;font-size:24px}} .service-hero p{{margin:7px 0;line-height:1.8}} .phone{{display:inline-block;margin-top:10px;background:#fff;color:#7b0000;text-decoration:none;font-weight:800;padding:10px 18px;border-radius:999px;font-size:19px}}
.service-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-bottom:16px}} .service-card{{padding:18px 20px}} .service-card h3{{margin:0 0 10px;color:#7b0000;font-size:19px}} .service-card p{{line-height:1.75;color:#555;margin:7px 0}} .service-list{{margin:0;padding-left:20px;line-height:2;color:#444}}
.price-card{{padding:20px;overflow:auto}} .price-card h3{{margin:0 0 14px;color:#7b0000;font-size:20px}} .price-table{{width:100%;min-width:650px;border-collapse:collapse}} .price-table th,.price-table td{{border-bottom:1px solid #eee;padding:12px 10px;text-align:left;line-height:1.55}} .price-table th{{background:#faf5e8;color:#6f0000}} .free{{color:#16803c;font-weight:800}} .notice{{font-size:12px;color:#888;line-height:1.7;margin:12px 0 0}}
footer{{text-align:center;color:#999;font-size:12px;padding:10px 20px 35px}} @media(max-width:700px){{header h1{{font-size:28px}}.dashboard{{grid-template-columns:1fr}}.stats{{justify-content:space-between}}.service-grid{{grid-template-columns:1fr}}.card{{padding:18px}}.card h2{{font-size:17px}}.service-hero h2{{font-size:22px}}}}
</style>
</head><body>
<header><div class="logo">COIN AI NEWS</div><h1>🪙 币智通 AI</h1><p>全球钱币资讯 · AI鉴定评估 · 收藏知识</p></header>

<section class="container">
<div class="hero"><h2>📚 钱币收藏资讯中心</h2><p>以资讯、行情、拍卖、收藏知识和鉴定评估为核心，帮助藏友更快了解市场变化、学习钱币知识。</p><p><strong>资讯为主｜鉴定评估为核心服务｜回收寄卖仅作为平台服务入口</strong></p></div>

<h2 class="section-title">🔥 今日钱币资讯</h2>
<section class="dashboard"><div class="panel"><div class="date">📅 今日更新：{today}</div><div class="date" style="margin-top:6px">最后生成：{updated} · 每日自动采集</div></div><div class="panel stats"><div class="stat"><b>{len(clean_articles)}</b><span>今日资讯</span></div><div class="stat"><b>{len(category_counts)}</b><span>资讯分类</span></div></div></section>
<nav class="filters" aria-label="资讯分类">{filters_html}</nav>
<section id="news-list">{cards_html if cards_html else '<div class="panel" style="text-align:center;padding:50px">今天暂时没有抓取到资讯，系统下一次运行会自动重试。</div>'}</section>

<h2 class="section-title">📈 钱币行情 · 市场分析</h2>
<div class="service-card"><h3>💰 关注市场变化</h3><p>后续自动增加银元、古钱、纸币、纪念币、金银币、评级币和拍卖成交数据分析。</p><p>价格判断应综合真伪、版别、品相、评级、来源及近期实际成交情况，网站价格仅作收藏研究参考。</p></div>

<h2 class="section-title">📚 钱币知识</h2>
<div class="service-grid">
<div class="service-card"><h3>🔍 钱币鉴定</h3><p>真伪识别、版别辨识、包浆与品相分析、常见造假方式。</p></div>
<div class="service-card"><h3>🏆 评级知识</h3><p>PCGS、NGC、PMG评级知识、送评注意事项和评级价值分析。</p></div>
<div class="service-card"><h3>🔨 拍卖研究</h3><p>关注国内外钱币拍卖资讯、精品成交和市场热点。</p></div>
<div class="service-card"><h3>📊 行情分析</h3><p>结合公开资讯和成交数据，观察热门品种与市场趋势。</p></div>
</div>
</section>

<section class="service-wrap" id="services">
<div class="service-hero"><h2>🔎 免费鉴定 · 咨询 · 线上估价</h2><p>📞 服务电话：<strong>13799875350</strong></p><p>覆盖全国主要城市｜免费评估｜无交易不收费｜照片 / 视频在线咨询｜24小时响应</p><a class="phone" href="tel:13799875350">📞 立即咨询 13799875350</a></div>
<div class="service-grid">
<div class="service-card"><h3>🔎 免费鉴定评估</h3><ul class="service-list"><li>免费鉴定、咨询、线上估价</li><li>提供照片 / 视频即可在线咨询</li><li>免费评估，无交易不收费</li><li>24小时响应</li></ul></div>
<div class="service-card"><h3>🚗 上门服务</h3><ul class="service-list"><li>覆盖全国主要城市</li><li>同城当面交流</li><li>安全保障，隐私全程保密</li><li>提前联系预约</li></ul></div>
<div class="service-card"><h3>💰 回收｜寄卖｜鉴定｜评估</h3><ul class="service-list"><li>钱币回收、寄卖</li><li>藏品鉴定、价值评估</li><li>全方位收藏品应急变现服务</li><li>贵金属、黄铂金相关服务咨询</li></ul></div>
<div class="service-card"><h3>🏆 评级与收藏服务</h3><ul class="service-list"><li>PCGS｜NGC｜PMG评级咨询</li><li>评级送评服务</li><li>收藏交流</li><li>实时行情资讯</li></ul></div>
</div>
<div class="service-card" style="margin-bottom:16px"><h3>🏮 长期专注</h3><p><strong>老银元｜机制币｜铜钱古币</strong></p><p><strong>老纸币｜纪念币｜评级币</strong></p><p><strong>PCGS｜NGC｜PMG评级咨询</strong></p></div>
<div class="price-card"><h3>💰 币智通 AI 服务价格表</h3><table class="price-table"><thead><tr><th>服务项目</th><th>价格</th><th>服务说明</th></tr></thead><tbody>
<tr><td>免费鉴定</td><td class="free">免费</td><td>照片 / 视频提交，24小时响应</td></tr>
<tr><td>收藏咨询</td><td class="free">免费</td><td>古钱、银币、金币、纪念币等收藏咨询</td></tr>
<tr><td>线上估价 / 评估</td><td class="free">免费</td><td>根据品种、版别、品相等信息综合评估</td></tr>
<tr><td>同城当面交流</td><td class="free">免费</td><td>提前电话预约</td></tr>
<tr><td>上门服务</td><td class="free">免费咨询</td><td>覆盖全国主要城市，需提前预约</td></tr>
<tr><td>钱币回收</td><td>实时询价</td><td>根据真伪、版别、品相及市场行情核价</td></tr>
<tr><td>钱币寄卖</td><td>具体议价</td><td>根据藏品情况确认服务条件</td></tr>
<tr><td>PCGS / NGC / PMG评级咨询</td><td class="free">免费咨询</td><td>评级机构实际费用、快递等费用另计</td></tr>
<tr><td>评级送评服务</td><td>咨询后报价</td><td>根据评级机构、数量及实际服务内容确定</td></tr>
<tr><td>贵金属 / 黄铂金回收</td><td>实时询价</td><td>按当日行情、成色、重量等实际情况核价</td></tr>
</tbody></table><p class="notice">※ “免费”仅指对应咨询、鉴定或评估服务本身不收费。实际回收、寄卖、评级、快递等产生的费用或成交价格，以双方最终确认内容为准。藏品价值会因真伪、版别、品相、评级及市场行情变化而变化。</p></div>
</section>
<footer>币智通 AI 钱币资讯自动化平台 · 资讯为主 · 鉴定评估服务为辅 · 回收寄卖作为服务入口 · 数据来自公开资讯源，仅供收藏研究参考</footer>
<script>document.querySelectorAll('.filter').forEach(function(button){button.addEventListener('click',function(){document.querySelectorAll('.filter').forEach(function(b){b.classList.remove('active')});button.classList.add('active');const filter=button.dataset.filter;document.querySelectorAll('.card').forEach(function(card){card.style.display=(filter==='全部'||card.dataset.category===filter)?'':'none'})})});</script>
</body></html>'''

with open("index.html", "w", encoding="utf-8") as file:
    file.write(html)
print("成功生成资讯：", len(clean_articles))
