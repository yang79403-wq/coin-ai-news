import json, re, time
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HongshengCoinBot/5.0; +https://yang79403-wq.github.io/coin-ai-news/)"}
TIMEOUT = 20
MAX_PAGES_PER_SOURCE = 80
MAX_ITEMS_PER_SOURCE = 800

SOURCES = [
    {"id":"yichen", "name":"一尘网", "seeds":["http://www.pm001.net/index.asp","http://www1.pm001.net/index.asp","http://www2.pm001.net/index.asp","http://www3.pm001.net/index.asp"]},
    {"id":"yy11", "name":"钱币天堂", "seeds":["https://www.yy11.com/c2c/forum/4.html"]},
]

CATEGORIES = {
    "纸币":["纸币","钞","人民币","连体钞"],
    "纪念钞":["纪念钞","纪念券"],
    "纪念币":["纪念币","流通纪念"],
    "金银币":["金币","银币","金银币","熊猫币"],
    "银元":["银元","袁大头","孙小头","船洋","龙洋","大洋","七钱二分"],
    "古钱币":["古钱","通宝","重宝","元宝","五铢","半两","刀币","布币"],
    "铜元":["铜元","铜板","大清铜币","光绪元宝"],
    "硬币":["硬币","流通币","分币","角币"],
    "福建钱币":["福建","闽","福州","厦门","泉州","漳州"],
}

TRANSACTION = ["成交价","成交价格","物品成交价","成交金额","成交于","已成交","结标价","已结标","结标","中标价","中标","得标价","得标","拍得","落槌价","落槌","售出","已售","交易成功","交易完成","确认成交","确认售出","竞价成功"]
WANTED = ["求购","收购","买入","求","出价","报价","求一个","高价求"]
ACTIVE = ["拍卖中","竞拍中","竞价中","进行中","尚未结拍","尚未结标"]

def clean(s): return " ".join(str(s or "").replace("\xa0"," ").split())

def fetch(session, url, referer=None):
    r=session.get(url, timeout=TIMEOUT, headers={**HEADERS, **({"Referer":referer} if referer else {})}, allow_redirects=True)
    r.raise_for_status(); r.encoding=r.apparent_encoding or r.encoding; return r

def classify(text):
    hits=[]
    for c, keys in CATEGORIES.items():
        if any(k in text for k in keys): hits.append(c)
    if "福建钱币" in hits and len(hits)>1: hits.remove("福建钱币")
    return hits[:2] or ["其他"]

def price_values(text):
    t=clean(text).replace(",","")
    pats=[r"(?:成交价|成交价格|物品成交价|成交金额|结标价|中标价|得标价|落槌价)\s*[:：=]?\s*(?:人民币|RMB|￥|¥)?\s*(\d+(?:\.\d+)?)",
          r"(?:成交于|成交|中标|得标|落槌|拍得|售出)\s*[:：=]?\s*(?:人民币|RMB|￥|¥)?\s*(\d+(?:\.\d+)?)"]
    vals=[]
    for p in pats:
        for m in re.finditer(p,t,re.I):
            try:
                v=float(m.group(1))
                if 0<v<100000000: vals.append(v)
            except: pass
    return vals

def image_url(soup, page):
    for m in soup.find_all("meta"):
        if (m.get("property") or "").lower()=="og:image" and m.get("content"): return urljoin(page,m["content"])
    for img in soup.find_all("img"):
        u=img.get("src") or img.get("data-src") or img.get("data-original")
        if u:
            u=urljoin(page,u)
            if u.startswith("http") and not any(x in u.lower() for x in ["logo","icon","avatar","qrcode","spacer"]): return u
    return ""

def title(soup):
    for tag in ["h1","h2","title"]:
        n=soup.find(tag)
        if n:
            x=clean(n.get_text(" ",strip=True))
            if x: return x[:180]
    return ""

def relevant_links(soup,page,host):
    out=[]
    for a in soup.find_all("a",href=True):
        u=urljoin(page,a["href"]).split("#",1)[0]
        if urlparse(u).netloc.lower()!=host: continue
        text=clean(a.get_text(" ",strip=True))
        low=(text+" "+u).lower()
        if any(k in low for k in ["forum","topic","dispbbs","list","detail","c2c","goods","auction","page="]): out.append(u)
    return list(dict.fromkeys(out))

def crawl(source):
    s=requests.Session(); queue=list(source["seeds"]); seen=set(); rows=[]; pages=0
    while queue and pages<MAX_PAGES_PER_SOURCE and len(rows)<MAX_ITEMS_PER_SOURCE:
        u=queue.pop(0)
        if u in seen: continue
        seen.add(u)
        try:
            r=fetch(s,u); pages+=1
            soup=BeautifulSoup(r.text,"html.parser")
            text=clean(soup.get_text(" ",strip=True))
            vals=price_values(text)
            has_tx=any(x in text for x in TRANSACTION)
            has_wanted=any(x in text for x in WANTED)
            active=any(x in text for x in ACTIVE)
            if (has_tx or has_wanted) and not active:
                nm=title(soup)
                if nm and vals:
                    img=image_url(soup,r.url)
                    cats=classify(nm+" "+text[:1200])
                    state="成交" if has_tx else "求购"
                    for v in vals[:3]:
                        rows.append({"name":nm,"category":cats[0],"state":state,"price":v,"currency":"CNY","date":datetime.now().strftime("%Y-%m-%d"),"source_name":source["name"],"source_url":r.url,"item_url":r.url,"image_url":img,"transaction_confirmed":has_tx,"verification":"公开页面文字规则核验"})
            for x in relevant_links(soup,r.url,urlparse(r.url).netloc.lower()):
                if x not in seen and len(queue)<300: queue.append(x)
        except Exception as e:
            pass
    uniq={}
    for x in rows: uniq[(x["source_name"],x["item_url"],x["state"],x["price"])]=x
    return list(uniq.values()), {"source":source["name"],"pages":pages,"rows":len(uniq)}

all_rows=[]; status=[]
for src in SOURCES:
    r,st=crawl(src); all_rows.extend(r); status.append(st)

# Generate category tables. Never invent a price: an empty category remains empty.
tables={}
for r in all_rows:
    tables.setdefault(r["category"],[]).append(r)
for c in list(tables):
    tables[c]=sorted(tables[c],key=lambda x:(x["name"],x["state"],-x["price"]))[:500]

payload={"updated_at":datetime.now().isoformat(),"sources":[x["name"] for x in SOURCES],"rows":all_rows,"tables":tables,"status":status,"policy":"成交与求购分离；不把挂牌价、进行中竞价当作成交价；保留原始页面链接。"}
Path("price-tables.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
# Keep the existing verified market feed intact; this file is the broader price-table feed.
print("price-table rows:",len(all_rows))
for x in status: print(x)
