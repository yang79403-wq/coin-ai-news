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

# 只采集公开页面，不登录、不提交表单、不绕过验证码/访问控制。
SOURCES = [
    {"provider_id":"yichen","source_name":"一尘网","url":"https://www.pm001.net/index.asp",
     "seeds":["https://www.pm001.net/index.asp","https://www1.pm001.net/index.asp","https://www2.pm001.net/index.asp"]},
    {"provider_id":"yy11","source_name":"钱币天堂","url":"https://www.yy11.com/htm/shop.cgi",
     "seeds":["https://www.yy11.com/htm/shop.cgi","http://www.yy11.com/htm/shop.cgi","https://www.yy11.com/"]},
    {"provider_id":"huaxia","source_name":"华夏古泉","url":"https://www.hxguquan.com/",
     "seeds":["https://www.hxguquan.com/","https://wwwn.hxguquan.com/","https://www.hxguquan.com/goods-list.html?gid=76167"]},
]
CATEGORIES=[
    ("古钱",["古钱","通宝","重宝","元宝","五铢","半两","方孔","刀币","布币","钱范"]),
    ("银元",["银元","袁大头","袁世凯","大洋","龙洋","银币","七钱二分"]),
    ("纸币",["纸币","人民币","老钞","钞票","纸钞"]),
    ("纪念币",["纪念币","生肖币","流通纪念币"]),
    ("纪念钞",["纪念钞","纪念钞票"]),
    ("金银币",["金币","金银币","金条","银条","贵金属币"]),
]
TRANSACTION=["成交价","成交价格","成交金额","已成交","成交","成交了","落槌价","落槌","中标价","中标","得标价","得标","拍得","结拍","结标","已结标","最终成交","竞价成功","竞买成功","已售","售出","已卖","交易成功","交易完成"]
ACTIVE=["拍卖中","竞拍中","竞价中","正在拍","待拍","尚未结拍","尚未结标","出价中","进行中"]
HEADERS={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8","Accept-Language":"zh-CN,zh;q=0.9,en;q=0.5","Cache-Control":"no-cache"}
TIMEOUT=25
MAX_LIST=20
MAX_DETAIL=120
MAX_ROWS=300

def clean(x): return " ".join(unescape(str(x or "")).replace("\xa0"," ").split())

def session():
    s=requests.Session(); s.headers.update(HEADERS)
    r=Retry(total=5,connect=5,read=5,status=4,backoff_factor=1.5,status_forcelist=(429,500,502,503,504),allowed_methods=frozenset(["GET","HEAD"]),raise_on_status=False)
    a=HTTPAdapter(max_retries=r,pool_connections=8,pool_maxsize=8); s.mount("http://",a); s.mount("https://",a); return s

def fetch(s,url,referer=None):
    h={"Referer":referer} if referer else {}
    last=None
    for attempt in range(3):
        try:
            r=s.get(url,timeout=TIMEOUT,allow_redirects=True,headers=h)
            if r.status_code in (403,429):
                time.sleep(2.5*(attempt+1)); continue
            r.raise_for_status(); r.encoding=r.apparent_encoding or r.encoding
            return r
        except Exception as e:
            last=e; time.sleep(1.5*(attempt+1))
    raise last or RuntimeError("request failed")

def confirmed(text, provider_id=None):
    text=clean(text)
    strong=[x for x in TRANSACTION if x in text]
    if not strong:return False
    if any(x in text for x in ACTIVE) and not any(x in text for x in ["已成交","成交价","成交价格","成交金额","落槌","中标","得标","拍得","结拍","结标","已结标","竞价成功","竞买成功","已售","售出","已卖","交易成功","交易完成"]): return False
    if provider_id=="yichen" and not any(x in text for x in ["已成交","成交","已售","售出","已卖","交易成功","交易完成"]): return False
    return True

def price(text):
    text=clean(text).replace(",","")
    pats=[
      r"(?:成交金额|成交价格|成交价|结标价|落槌价|中标价|得标价|最终成交|最终价|拍得|成交|落槌|中标|得标|已售|售出|已卖)\s*[:：=]?\s*[¥￥]?\s*(\d+(?:\.\d+)?)\s*(?:元|RMB|人民币)?",
      r"(?:结标|结标价|中标|得标|最终价|成交)\s*[：:]?\s*(?:RMB|￥|¥)?\s*(\d+(?:\.\d+)?)",
    ]
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
        src=img.get("src") or img.get("data-src") or img.get("data-original")
        if not src: continue
        x=urljoin(url,src); low=x.lower()
        if not x.startswith(("http://","https://")) or any(k in low for k in ("logo","icon","avatar","blank","spacer","qrcode","advert")): continue
        w=int(re.sub(r"\D","",str(img.get("width") or "0")) or 0); h=int(re.sub(r"\D","",str(img.get("height") or "0")) or 0)
        score=w*h
        if score==0:
            alt=clean(img.get("alt") or img.get("title")); score=len(alt)*100
        if best is None or score>best[0]: best=(score,x)
    return best[1] if best else None

def title(soup,text):
    m=soup.find("meta",property="og:title") or soup.find("meta",attrs={"name":"twitter:title"})
    if m and m.get("content"): return clean(m["content"])[:180]
    for tag in ("h1","h2","h3","title"):
        n=soup.find(tag)
        if n and clean(n.get_text(" ",strip=True)): return clean(n.get_text(" ",strip=True))[:180]
    return clean(text[:160])

def script_text(soup): return " ".join(clean(x.get_text(" ",strip=True)) for x in soup.find_all("script"))

def detail(s,item_url,src):
    try:r=fetch(s,item_url,src["url"])
    except Exception:return None
    sp=BeautifulSoup(r.text,"html.parser"); txt=clean(sp.get_text(" ",strip=True)); raw=txt+" "+script_text(sp)
    if not confirmed(raw,src["provider_id"]): return None
    p=price(raw)
    if p is None and src["provider_id"]=="huaxia" and ("已结标" in raw or "竞价成功" in raw or "结标" in raw): p=price(re.sub(r"[{}\[\]", " ", raw))
    im=image(sp,r.url)
    if p is None or im is None:return None
    name=title(sp,txt).strip(" -|：:")
    if len(name)<2:return None
    return {"name":name,"price":p,"currency":"CNY","date":datetime.now().astimezone().strftime("%Y-%m-%d"),"provider_id":src["provider_id"],"source_name":src["source_name"],"source_page_url":r.url,"item_url":r.url,"image_url":im,"category":category(name),"transaction_confirmed":True,"type":"公开原帖已确认成交"}

def links(soup,page,src):
    out=[]; seen=set(); host=urlparse(page).netloc.lower()
    keys=("成交","结拍","结标","已结标","拍品","拍卖","竞价","交易","商品","详情","历史","中标","得标","已售","售出","auction","lot","item","goods-detail","goods-list","shop.cgi","topic.cgi","dispbbs.asp")
    for a in soup.find_all("a",href=True):
        u=urljoin(page,a["href"]).split("#",1)[0]; q=urlparse(u); label=clean(a.get_text(" ",strip=True)).lower()
        if q.scheme not in ("http","https") or q.netloc.lower()!=host or u in seen:continue
        low=label+" "+u.lower()
        if any(k in low for k in keys): seen.add(u); out.append(u)
        if len(out)>=MAX_DETAIL:break
    return out

def direct_nodes(soup,r,src):
    rows=[]
    for node in soup.find_all(["tr","li","article","section","div"],limit=15000):
        txt=clean(node.get_text(" ",strip=True))
        if len(txt)<12 or len(txt)>1600 or not confirmed(txt,src["provider_id"]):continue
        p=price(txt); a=node.find("a",href=True); im=node.find("img",src=True) or node.find("img",attrs={"data-src":True}) or node.find("img",attrs={"data-original":True})
        if p is None or not a or not im:continue
        item=urljoin(r.url,a.get("href")); ims=im.get("src") or im.get("data-src") or im.get("data-original"); iu=urljoin(r.url,ims)
        if not same_host(item,r.url) or not iu.startswith(("http://","https://")):continue
        name=clean(a.get_text(" ",strip=True)) or txt[:160]
        if len(name)<2:continue
        rows.append({"name":name[:160],"price":p,"currency":"CNY","date":datetime.now().astimezone().strftime("%Y-%m-%d"),"provider_id":src["provider_id"],"source_name":src["source_name"],"source_page_url":r.url,"item_url":item,"image_url":iu,"category":category(name),"transaction_confirmed":True,"type":"公开原帖已确认成交"})
    return rows

def crawl(src):
    s=session(); queue=list(src.get("seeds",[src["url"]])); visited=set(); detail_q=[]; detail_seen=set(); rows=[]; errors=[]; pages=0; used_seed=None
    while queue and pages<MAX_LIST and len(rows)<MAX_ROWS:
        u=queue.pop(0)
        if u in visited:continue
        visited.add(u)
        try:
            r=fetch(s,u,src["url"]); used_seed=used_seed or r.url; pages+=1
            sp=BeautifulSoup(r.text,"html.parser"); rows.extend(direct_nodes(sp,r,src))
            for x in links(sp,r.url,src):
                if x not in detail_seen:detail_seen.add(x);detail_q.append(x)
            while detail_q and len(detail_seen)<=MAX_DETAIL and len(rows)<MAX_ROWS:
                x=detail_q.pop(0); z=detail(s,x,src)
                if z:rows.append(z)
                time.sleep(.12)
        except Exception as e:
            errors.append(f"{type(e).__name__}: {str(e)[:180]}"); time.sleep(1.5)
    unique={}
    for row in rows:
        if row.get("item_url") and row.get("image_url") and row.get("price") is not None:unique[(row["provider_id"],row["item_url"])]=row
    rows=list(unique.values())[:MAX_ROWS]
    return rows,{"provider_id":src["provider_id"],"source_name":src["source_name"],"source_url":src["url"],"used_seed":used_seed,"ok":pages>0,"pages":pages,"rows":len(rows),"errors":errors[:8]}

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
payload={"updated_at":datetime.now(timezone.utc).astimezone().isoformat(),"scope":"一尘网、钱币天堂、华夏古泉公开成交页面","data_policy":"仅收录能够同时关联到原始商品/拍品链接、该条目原始实物图片和明确成交价格的公开记录；不把挂牌价、求购价或进行中的竞价当作成交价。","sources":SOURCES,"rows":all_rows,"summary":summary,"status":status,"verification":{"policy":"只有打开原始商品/拍品页面后再次确认成交状态、成交价格，并从同一页面取得实物图片的记录才进入价格表。","verified_count":len(all_rows),"verified_at":datetime.now(timezone.utc).astimezone().isoformat()}}
Path("market-data.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
print("source-linked transaction model complete:",len(all_rows))
for x in status:print(x["source_name"],x["ok"],"pages=",x["pages"],"rows=",x["rows"],"seed=",x["used_seed"],"errors=",x["errors"])
