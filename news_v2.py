import json
import re
from datetime import datetime, timezone
from html import unescape
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# 资讯也只允许来自这三个公开站点。前台不显示站点名称。
SOURCES=[
 {"provider_id":"source_a","url":"https://www.xx007.com/","keywords":["钱币","银元","纸币","纪念币","金银币","行情"]},
 {"provider_id":"source_b","url":"https://www.coinsky.com/","keywords":["钱币","银元","纸币","纪念币","金币","竞价"]},
 {"provider_id":"source_c","url":"https://www.chcoin.com/","keywords":["钱币","古钱","银元","机制币","评级币","拍卖"]},
]
HEADERS={"User-Agent":"Mozilla/5.0 (compatible; CoinAI-News/1.0)"}

def clean(s): return " ".join(unescape(str(s or "")).split())

def parse(html, source):
    soup=BeautifulSoup(html,"html.parser")
    items=[];seen=set()
    for node in soup.find_all(["a","h1","h2","h3","h4","li"],limit=5000):
        title=clean(node.get_text(" ",strip=True))
        if len(title)<6 or len(title)>180: continue
        if not any(k in title for k in source["keywords"]): continue
        if re.search(r"登录|注册|客服热线|版权|版权所有|立即参拍|免费注册",title): continue
        link=node.get("href","") if node.name=="a" else ""
        if link and link.startswith("/"):
            from urllib.parse import urljoin
            link=urljoin(source["url"],link)
        if not link: link=source["url"]
        key=title.lower()
        if key in seen: continue
        seen.add(key)
        items.append({"category":"钱币市场资讯","title":title,"link":link,"summary":"AI从公开钱币资讯页面整理的市场线索，供收藏研究参考。","provider_id":source["provider_id"],"published":datetime.now(timezone.utc).isoformat()})
        if len(items)>=20: break
    return items

articles=[];status=[]
for source in SOURCES:
    try:
        r=requests.get(source["url"],headers=HEADERS,timeout=20,allow_redirects=True)
        r.raise_for_status();got=parse(r.text,source);articles.extend(got)
        status.append({"provider_id":source["provider_id"],"ok":True,"count":len(got),"http":r.status_code})
    except Exception as exc:
        status.append({"provider_id":source["provider_id"],"ok":False,"count":0,"error":str(exc)[:160]})

unique={a["title"].lower():a for a in articles}
clean_articles=list(unique.values())[:40]
now=datetime.now().astimezone()
headline=clean_articles[0]["title"] if clean_articles else "今日钱币市场资讯正在自动采集"
ai_summary=(f"AI自动整理：{headline}。系统每日从公开钱币市场页面筛选收藏、行情、交易与拍卖线索，供藏友研究参考。" if clean_articles else "今日暂未取得新的公开资讯，系统将在下一次任务自动重试。")
payload={"updated_at":now.isoformat(),"headline":headline,"ai_summary":ai_summary,"count":len(clean_articles),"articles":clean_articles,"status":status}
Path("news-data.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")

cards=[]
for a in clean_articles:
    cards.append(f'<article class="ncard"><div class="nmeta"><span>{clean(a["category"])}</span><span>{now.strftime("%m-%d %H:%M")}</span></div><h3>{clean(a["title"])}</h3><p>{clean(a["summary"])}</p><a href="{a["link"]}" target="_blank" rel="noopener noreferrer">查看详情 →</a></article>')

html=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>币智通 AI · 每日钱币资讯</title><style>body{{margin:0;background:#f7f1e7;color:#2b211c;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}}header{{padding:34px 18px;background:linear-gradient(135deg,#320000,#850707,#b8860b);color:#fff}}main{{max-width:1000px;margin:auto;padding:20px}}.hero,.ncard{{background:#fff;border-radius:16px;padding:20px;margin-bottom:14px;box-shadow:0 5px 20px #4a160012}}.hero h1{{margin:0 0 10px;color:#6b0000}}.nmeta{{display:flex;gap:10px;flex-wrap:wrap;font-size:12px;color:#999}}.ncard h3{{font-size:18px;line-height:1.5;margin:9px 0}}.ncard p{{color:#666;line-height:1.7}}.ncard a{{color:#760000;font-weight:800;text-decoration:none}}</style></head><body><header><div>COIN AI NEWS</div><h1>🪙 币智通 AI 每日钱币资讯</h1><div>自动更新：{now.strftime("%Y-%m-%d %H:%M:%S")}</div></header><main><section class="hero"><h1>🔥 今日钱币头条</h1><h2>{clean(headline)}</h2><p>{clean(ai_summary)}</p></section>{''.join(cards) if cards else '<div class="hero">暂无新资讯，下一次任务自动重试。</div>'}</main></body></html>'''
Path("news.html").write_text(html,encoding="utf-8")
print("每日资讯已生成：",len(clean_articles))
print("采集状态：",status)