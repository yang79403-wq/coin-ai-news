import json
import re
from datetime import datetime, timezone
from html import unescape
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# 仅允许这三个公开来源。前台不显示来源名称。
SOURCES = [
    {"provider_id":"source_a","url":"https://www.xx007.com/","keywords":["钱币","银元","纸币","纪念币","金银币"]},
    {"provider_id":"source_b","url":"https://www.coinsky.com/","keywords":["钱币","银元","纸币","纪念币","金币"]},
    {"provider_id":"source_c","url":"https://www.chcoin.com/","keywords":["钱币","古钱","银元","机制币","评级币"]},
]
HEADERS={"User-Agent":"Mozilla/5.0 (compatible; CoinAI-News/1.0)"}
TIMEOUT=20

def clean(s):
    return " ".join(unescape(str(s or "")).split())

def extract_price(text):
    text=clean(text).replace(",","")
    for p in [r"(?:¥|￥)\s*(\d+(?:\.\d+)?)",r"(?:成交|价格|价|售价|落槌)\s*[:：]?\s*(\d+(?:\.\d+)?)\s*元?"]:
        m=re.search(p,text,re.I)
        if m:
            v=float(m.group(1))
            if 0<v<100000000:return v
    return None

def parse(html, source):
    soup=BeautifulSoup(html,"html.parser")
    out=[];seen=set()
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
        out.append({"name":title[:100],"price":price,"date":datetime.now().astimezone().strftime("%Y-%m-%d"),"provider_id":source["provider_id"],"type":"公开成交/报价线索"})
        if len(out)>=30: break
    return out

rows=[];status=[]
for source in SOURCES:
    try:
        r=requests.get(source["url"],headers=HEADERS,timeout=TIMEOUT,allow_redirects=True)
        r.raise_for_status()
        got=parse(r.text,source);rows.extend(got)
        status.append({"provider_id":source["provider_id"],"ok":True,"rows":len(got),"http":r.status_code})
    except Exception as exc:
        status.append({"provider_id":source["provider_id"],"ok":False,"rows":0,"error":str(exc)[:160]})

unique={(r["name"],r["price"]):r for r in rows}
rows=list(unique.values())[:80]
payload={"updated_at":datetime.now(timezone.utc).astimezone().isoformat(),"scope":"公开市场成交/报价线索，仅作收藏研究参考","rows":rows,"status":status}
Path("market-data.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")

# 在首页注入数据渲染器：只显示统一的“公开成交/报价线索”，不显示来源网站名称。
index=Path("index.html")
if index.exists():
    html=index.read_text(encoding="utf-8")
    # 固定首页品牌口号与福建服务信息，保证每日自动更新时不会被旧版文案覆盖。
    html=html.replace("币智通 <em>AI</em>","币智通 <em>AI</em>")
    if "新时代人工智能 AI，让收藏畅通无阻" not in html:
        html=html.replace('<div class="sub">钱币资讯 · 市场行情 · 鉴定评估 · 收藏研究</div>', '<div class="sub">新时代人工智能 AI，让收藏畅通无阻</div><div class="sub" style="margin-top:6px;font-size:12px;letter-spacing:2px">钱币资讯 · 市场行情 · 鉴定评估 · 收藏研究</div>')
    html=html.replace("福建泉州 · 当天服务", "福建泉州 · 当天上门评估鉴定")
    html=html.replace("福建厦门 · 当天服务", "福建厦门 · 当天上门评估鉴定")
    html=html.replace("福建福州 · 当天服务", "福建福州 · 当天上门评估鉴定")
    if "13799875350" in html and "微信同号" not in html:
        html=html.replace("📞 电话 / 微信（手机同号）", "📞 电话 / 微信同号")
    script=r'''<script id="coin-ai-market-script">(function(){function e(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}function render(d){var rows=d.rows||[],body=rows.length?rows.slice(0,40).map(function(r){return '<tr><td>'+e(r.name)+'</td><td><strong>¥'+Number(r.price).toLocaleString('zh-CN')+'</strong></td><td>'+e(r.date||'')+'</td><td>公开成交/报价线索</td></tr>'}).join(''):'<tr><td colspan="4" style="text-align:center;color:#999">今日暂未采集到可确认的公开价格线索，下一次任务自动重试。</td></tr>';var box='<section class="market-live"><div class="table-box"><h3>📊 今日成交价格参考</h3><div style="color:#8b8179;font-size:12px;margin-bottom:10px">AI自动整理公开市场线索 · 更新时间 '+e(d.updated_at||'')+'</div><table class="price-table"><thead><tr><th>钱币品种</th><th>价格</th><th>日期</th><th>数据性质</th></tr></thead><tbody>'+body+'</tbody></table><div style="font-size:11px;color:#8b8179;line-height:1.7;margin-top:10px">价格受真伪、版别、品相、评级、交易条件等影响；本表仅作市场研究参考，不构成报价或交易承诺。</div></div></section>';var m=document.getElementById('market');if(m)m.innerHTML=box;else{var a=document.getElementById('coins')||document.querySelector('main');if(a)a.insertAdjacentHTML('afterend',box)}}fetch('market-data.json?'+Date.now(),{cache:'no-store'}).then(function(r){return r.json()}).then(render).catch(function(){render({rows:[],updated_at:'暂未更新'})});document.querySelectorAll('.nmeta').forEach(function(m){var s=m.querySelectorAll('span');for(var i=1;i<s.length;i++)s[i].remove()})})();</script>'''
    html=re.sub(r'<script id="coin-ai-market-script">.*?</script>','',html,flags=re.S)
    if '</body>' in html: html=html.replace('</body>',script+'\n</body>',1)
    index.write_text(html,encoding='utf-8')

print('市场数据更新完成：',len(rows))
