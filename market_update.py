import json
import re
from datetime import datetime, timezone
from html import unescape
from pathlib import Path

import requests
from bs4 import BeautifulSoup

SOURCES = [
    {"provider_id":"source_a","url":"https://www.xx007.com/","keywords":["钱币","银元","纸币","纪念币","金银币"]},
    {"provider_id":"source_b","url":"https://www.coinsky.com/","keywords":["钱币","银元","纸币","纪念币","金币"]},
    {"provider_id":"source_c","url":"https://www.chcoin.com/","keywords":["钱币","古钱","银元","机制币","评级币"]},
]
CATEGORIES = [
    ("古钱", ["古钱","通宝","重宝","元宝","五铢","半两","方孔"]),
    ("银元", ["银元","袁大头","袁世凯","大洋","龙洋","银币"]),
    ("纸币", ["纸币","人民币","老钞","钞票","纸钞"]),
    ("纪念币", ["纪念币","生肖币","流通纪念币"]),
    ("纪念钞", ["纪念钞","纪念钞票"]),
    ("金银币", ["金币","金银币","银币","金条","银条","贵金属币"]),
]
HEADERS={"User-Agent":"Mozilla/5.0 (compatible; CoinAI-News/1.0)"}
TIMEOUT=20

def clean(s): return " ".join(unescape(str(s or "")).split())

def extract_price(text):
    text=clean(text).replace(",","")
    for p in [r"(?:¥|￥)\s*(\d+(?:\.\d+)?)",r"(?:成交|价格|价|售价|落槌)\s*[:：]?\s*(\d+(?:\.\d+)?)\s*元?"]:
        m=re.search(p,text,re.I)
        if m:
            v=float(m.group(1))
            if 0<v<100000000:return v
    return None

def classify(name):
    for cat, keys in CATEGORIES:
        if any(k in name for k in keys): return cat
    return "其他"

def parse(html, source):
    soup=BeautifulSoup(html,"html.parser"); out=[]; seen=set()
    for node in soup.find_all(["tr","li","article","div"],limit=4000):
        text=clean(node.get_text(" ",strip=True))
        if len(text)<5 or len(text)>500 or not any(k in text for k in source["keywords"]): continue
        price=extract_price(text)
        if price is None: continue
        heading=node.find(["a","h1","h2","h3","h4","strong"])
        title=clean(heading.get_text(" ",strip=True) if heading else text[:100])
        title=re.sub(r"(?:¥|￥)\s*\d+(?:\.\d+)?","",title).strip(" -|：:")
        key=(title,price)
        if len(title)<2 or key in seen: continue
        seen.add(key)
        out.append({"name":title[:100],"price":price,"date":datetime.now().astimezone().strftime("%Y-%m-%d"),"provider_id":source["provider_id"],"type":"公开成交/报价线索","category":classify(title)})
        if len(out)>=30: break
    return out

rows=[]; status=[]
for source in SOURCES:
    try:
        r=requests.get(source["url"],headers=HEADERS,timeout=TIMEOUT,allow_redirects=True); r.raise_for_status()
        got=parse(r.text,source); rows.extend(got)
        status.append({"provider_id":source["provider_id"],"ok":True,"rows":len(got),"http":r.status_code})
    except Exception as exc:
        status.append({"provider_id":source["provider_id"],"ok":False,"rows":0,"error":str(exc)[:160]})

unique={(r["name"],r["price"]):r for r in rows}; rows=list(unique.values())[:120]
payload={"updated_at":datetime.now(timezone.utc).astimezone().isoformat(),"scope":"公开市场成交/报价线索，仅作收藏研究参考","categories":[x[0] for x in CATEGORIES],"rows":rows,"status":status}
Path("market-data.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")

# 六大类价格表固定显示；没有可靠样本时明确显示“暂无可确认数据”，绝不虚构价格。
index=Path("index.html")
if index.exists():
    html=index.read_text(encoding="utf-8")
    script=r'''<script id="coin-ai-market-script">(function(){function e(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}var cats=['古钱','银元','纸币','纪念币','纪念钞','金银币'];function render(d){var rows=d.rows||[];var wrap='<section class="market-live section"><h2 class="title">📊 AI成交价格表 · Market Prices</h2><p class="desc">古钱 · 银元 · 纸币 · 纪念币 · 纪念钞 · 金银币　｜　AI自动整理公开市场成交/报价线索</p><div class="market-category-grid">'+cats.map(function(c){var rr=rows.filter(function(r){return r.category===c}).slice(0,15);var body=rr.length?rr.map(function(r){return '<tr class="market-row"><td>'+e(r.name)+'</td><td><strong>¥'+Number(r.price).toLocaleString('zh-CN')+'</strong></td><td>'+e(r.date||'')+'</td></tr>'}).join(''):'<tr><td colspan="3" class="empty">暂无可确认的公开价格数据<br><small>下一次自动采集后更新</small></td></tr>';return '<div class="market"><h3>'+c+' · Market</h3><table class="price-table" data-category="'+c+'"><thead><tr><th>钱币品种</th><th>价格</th><th>日期</th></tr></thead><tbody>'+body+'</tbody></table></div>'}).join('')+'</div><div class="notice">更新时间：'+e(d.updated_at||'')+'。价格受真伪、版别、品相、评级和交易条件影响，仅作收藏研究参考，不构成报价或交易承诺。</div></section>';var old=document.querySelector('.market-live');if(old)old.outerHTML=wrap;else{var a=document.getElementById('market')||document.getElementById('coins');if(a)a.insertAdjacentHTML('afterend',wrap)}}fetch('market-data.json?'+Date.now(),{cache:'no-store'}).then(function(r){return r.json()}).then(render).catch(function(){render({rows:[],updated_at:'暂未更新'})});})();</script>'''
    html=re.sub(r'<script id="coin-ai-market-script">.*?</script>','',html,flags=re.S)
    if '</body>' in html: html=html.replace('</body>',script+'\n</body>',1)
    index.write_text(html,encoding='utf-8')
print('六大类市场表已生成，样本数：',len(rows))
