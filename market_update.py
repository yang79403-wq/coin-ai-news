import json
import re
import time
from collections import defaultdict
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

SOURCES = [
    {"provider_id":"yichen","source_name":"一尘网","url":"https://www.pm001.net/index.asp"},
    {"provider_id":"yy11","source_name":"钱币天堂","url":"https://www.yy11.com/htm/shop.cgi"},
    {"provider_id":"huaxia","source_name":"华夏古泉","url":"https://www.hxguquan.com/"},
]
CATEGORIES=[("古钱",["古钱","通宝","重宝","元宝","五铢","半两","方孔","刀币","布币"]),("银元",["银元","袁大头","袁世凯","大洋","龙洋","银币"]),("纸币",["纸币","人民币","老钞","钞票","纸钞"]),("纪念币",["纪念币","生肖币","流通纪念币"]),("纪念钞",["纪念钞","纪念钞票"]),("金银币",["金币","金银币","金条","银条","贵金属币"])]
TRANSACTION=["成交价","成交价格","成交金额","已成交","成交","落槌价","落槌","中标价","中标","得标价","得标","拍得","结拍","最终成交"]
ACTIVE=["拍卖中","竞拍中","竞价中","正在拍","待拍","尚未结拍","出价中","当前出价"]
HEADERS={"User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Version/17.0 Mobile/15E148 Safari/604.1","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language":"zh-CN,zh;q=0.9,en;q=0.5","Cache-Control":"no-cache"}
TIMEOUT=20
MAX_LIST=12
MAX_DETAIL=80
MAX_ROWS=240

def clean(x): return " ".join(unescape(str(x or "")).replace("\xa0"," ").split())

def session():
    s=requests.Session(); s.headers.update(HEADERS)
    r=Retry(total=4,connect=4,read=4,status=3,backoff_factor=1.2,status_forcelist=(429,500,502,503,504),allowed_methods=frozenset(["GET","HEAD"]),raise_on_status=False)
    a=HTTPAdapter(max_retries=r,pool_connections=8,pool_maxsize=8); s.mount("http://",a); s.mount("https://",a); return s

def confirmed(text):
    text=clean(text)
    if not any(x in text for x in TRANSACTION): return False
    if any(x in text for x in ACTIVE) and not any(x in text for x in ["已成交","成交价","成交价格","成交金额","落槌","中标","得标","拍得","结拍","最终成交"]): return False
    return True

def price(text):
    text=clean(text).replace(",","")
    pats=[r"(?:成交金额|成交价格|成交价|落槌价|中标价|得标价|最终成交|最终价|拍得|成交|落槌|中标|得标)\s*[:：]?\s*[¥￥]?\s*(\d+(?:\.\d+)?)\s*元?",r"[¥￥]\s*(\d+(?:\.\d+)?)"]
    for p in pats:
        for m in re.finditer(p,text,re.I):
            v=float(m.group(1))
            if 0<v<100000000:return v
    return None

def category(name):
    for c,ks in CATEGORIES:
        if any(k in name for k in ks): return c
    return "其他"

def same_host(a,b): return urlparse(a).netloc.lower()==urlparse(b).netloc.lower()

def image(soup,url):
    for m in soup.find_all("meta"):
        key=(m.get("property") or m.get("name") or "").lower()
        if key in ("og:image","twitter:image") and m.get("content"):
            x=urljoin(url,m["content"])
            if x.startswith(("http://","https://")): return x
    best=None
    for img in soup.find_all("img"):
        src=img.get("src") or img.get("data-src")
        if not src: continue
        x=urljoin(url,src); low=x.lower()
        if not x.startswith(("http://","https://")) or any(k in low for k in ("logo","icon","avatar","blank","spacer")): continue
        w=int(re.sub(r"\D","",str(img.get("width") or "0")) or 0); h=int(re.sub(r"\D","",str(img.get("height") or "0")) or 0)
        score=w*h
        if best is None or score>best[0]: best=(score,x)
    return best[1] if best else None

def title(soup,text):
    m=soup.find("meta",property="og:title") or soup.find("meta",attrs={"name":"twitter:title"})
    if m and m.get("content"): return clean(m["content"])[:180]
    for tag in ("h1","h2","h3","title"):
        n=soup.find(tag)
        if n and clean(n.get_text(" ",strip=True)): return clean(n.get_text(" ",strip=True))[:180]
    return clean(text[:160])

def detail(s,item_url,src):
    try:
        r=s.get(item_url,timeout=TIMEOUT,allow_redirects=True,headers={"Referer":src["url"]}); r.raise_for_status(); r.encoding=r.apparent_encoding or r.encoding
    except Exception: return None
    sp=BeautifulSoup(r.text,"html.parser"); txt=clean(sp.get_text(" ",strip=True))
    if not confirmed(txt): return None
    p=price(txt); im=image(sp,r.url)
    if p is None or im is None:return None
    name=title(sp,txt).strip(" -|：:")
    if len(name)<2:return None
    return {"name":name,"price":p,"currency":"CNY","date":datetime.now().astimezone().strftime("%Y-%m-%d"),"provider_id":src["provider_id"],"source_name":src["source_name"],"source_page_url":src["url"],"item_url":r.url,"image_url":im,"category":category(name),"transaction_confirmed":True,"type":"公开原帖已确认成交"}

def links(soup,page,src):
    out=[]; seen=set(); host=urlparse(src["url"]).netloc.lower()
    keys=("成交","结拍","拍品","拍卖","竞价","交易","商品","详情","历史","result","auction","lot","item","shop","page","next")
    for a in soup.find_all("a",href=True):
        u=urljoin(page,a["href"]).split("#",1)[0]; q=urlparse(u); label=clean(a.get_text(" ",strip=True)).lower()
        if q.scheme not in ("http","https") or q.netloc.lower()!=host or u in seen or u.rstrip("/")==src["url"].rstrip("/"):continue
        if any(k in (label+" "+u.lower()) for k in keys): seen.add(u); out.append(u)
        if len(out)>=MAX_DETAIL:break
    return out

def crawl(src):
    s=session(); queue=[src["url"]]; visited=set(); detail_q=[]; detail_seen=set(); rows=[]; errors=[]; pages=0
    while queue and pages<MAX_LIST and len(rows)<MAX_ROWS:
        u=queue.pop(0)
        if u in visited:continue
        visited.add(u)
        try:
            r=s.get(u,timeout=TIMEOUT,allow_redirects=True,headers={"Referer":src["url"]}); r.raise_for_status(); r.encoding=r.apparent_encoding or r.encoding
            pages+=1; sp=BeautifulSoup(r.text,"html.parser")
            # Direct row/card verification: price, image and item link must belong to the same node.
            for node in sp.find_all(["tr","li","article","section","div"],limit=10000):
                txt=clean(node.get_text(" ",strip=True))
                if len(txt)<12 or len(txt)>1200 or not confirmed(txt):continue
                p=price(txt); a=node.find("a",href=True); im=node.find("img",src=True) or node.find("img",attrs={"data-src":True})
                if p is None or not a or not im:continue
                item=urljoin(r.url,a.get("href")); ims=im.get("src") or im.get("data-src"); iu=urljoin(r.url,ims)
                if not same_host(item,src["url"]) or not iu.startswith(("http://","https://")):continue
                name=clean(a.get_text(" ",strip=True)) or txt[:160]
                rows.append({"name":name[:160],"price":p,"currency":"CNY","date":datetime.now().astimezone().strftime("%Y-%m-%d"),"provider_id":src["provider_id"],"source_name":src["source_name"],"source_page_url":src["url"],"item_url":item,"image_url":iu,"category":category(name),"transaction_confirmed":True,"type":"公开原帖已确认成交"})
                if len(rows)>=MAX_ROWS:break
            for x in links(sp,r.url,src):
                if x not in detail_seen:detail_seen.add(x);detail_q.append(x)
            while detail_q and len(detail_seen)<=MAX_DETAIL and len(rows)<MAX_ROWS:
                x=detail_q.pop(0); z=detail(s,x,src)
                if z:rows.append(z)
                time.sleep(.15)
        except Exception as e:
            errors.append(f"{type(e).__name__}: {str(e)[:180]}"); time.sleep(2)
    unique={}
    for row in rows:
        if row.get("item_url") and row.get("image_url") and row.get("price") is not None:unique[(row["provider_id"],row["item_url"])]=row
    rows=list(unique.values())[:MAX_ROWS]
    return rows,{"provider_id":src["provider_id"],"source_name":src["source_name"],"source_url":src["url"],"ok":pages>0,"pages":pages,"rows":len(rows),"errors":errors[:5]}

all_rows=[]; status=[]
for src in SOURCES:
    r,info=crawl(src); all_rows.extend(r); status.append(info)
all_rows=[r for r in all_rows if r.get("item_url") and r.get("image_url") and r.get("price") is not None and r.get("transaction_confirmed")]
groups=defaultdict(list)
for r in all_rows:groups[(r["category"],r["name"])].append(r["price"])
summary=[]
for (c,n),vals in groups.items():
    vals=sorted(vals); med=vals[len(vals)//2] if len(vals)%2 else (vals[len(vals)//2-1]+vals[len(vals)//2])/2
    summary.append({"category":c,"name":n,"min":min(vals),"median":med,"max":max(vals),"samples":len(vals)})
summary.sort(key=lambda x:(-x["samples"],x["category"],x["name"]))
payload={"updated_at":datetime.now(timezone.utc).astimezone().isoformat(),"scope":"一尘网、钱币天堂、华夏古泉公开成交页面","data_policy":"仅收录能够同时关联到原始商品/拍品链接、该条目原始实物图片和明确成交价格的公开记录；不把挂牌价或进行中的竞价当作成交价。","sources":SOURCES,"rows":all_rows,"summary":summary,"status":status,"verification":{"policy":"只有打开原始商品/拍品页面后再次确认成交状态、成交价格，并从同一页面取得实物图片的记录才进入价格表。","verified_count":len(all_rows),"verified_at":datetime.now(timezone.utc).astimezone().isoformat()}}
Path("market-data.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
print("source-linked transaction model complete:",len(all_rows))
for x in status:print(x["source_name"],x["ok"],"pages=",x["pages"],"rows=",x["rows"],"errors=",x["errors"])
