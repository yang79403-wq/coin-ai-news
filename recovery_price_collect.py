#!/usr/bin/env python3
"""洪盛集藏：一尘网/钱币公开回收报价整理器。
只发布公开页面中明确标注“收购价/回收价”的记录；报价保留原文日期和来源，不把挂牌/成交/求购混为一谈。
"""
import json,re,time
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'data/recovery-prices.json'
UA='HongshengCollectionResearchBot/1.0 (+https://yang79403-wq.github.io/coin-ai-news/)'
SOURCES=[
 {'name':'一尘网','url':'http://www.pm001.net/','kind':'yichen'},
 {'name':'钱币天堂','url':'https://www.yy11.com/c2c/forum/4.html','kind':'coinsky'},
]

def fetch(url):
 r=requests.get(url,headers={'User-Agent':UA},timeout=25); r.raise_for_status(); return r.text

def clean(x): return re.sub(r'\s+',' ',x or '').strip()

def parse_page(url,source):
 html=fetch(url); soup=BeautifulSoup(html,'html.parser'); text=clean(soup.get_text(' ',strip=True)); rows=[]
 # 只识别明确的收购/回收报价表达，避免把普通销售价当回收价
 pats=[r'([^。；\n]{2,80}?)\s*(?:收购价|回收价|收价)\s*[:：]?\s*([¥￥]?\s*[0-9][0-9,.]*(?:\s*[-~至]\s*[¥￥]?[0-9][0-9,.]*)?\s*元?)']
 for pat in pats:
  for m in re.finditer(pat,text,re.I):
   name=clean(m.group(1)); price=clean(m.group(2))
   if len(name)>80 or any(k in name for k in ['电话','微信','地址','账号']): continue
   rows.append({'name':name,'price':price,'type':'回收报价','source':source['name'],'source_url':url,'date':time.strftime('%Y-%m-%d'),'verification':'source-text'})
 # 去重
 seen=set(); out=[]
 for r in rows:
  key=(r['name'],r['price'],r['source_url'])
  if key not in seen: seen.add(key); out.append(r)
 return out

def main():
 records=[]; statuses=[]
 for s in SOURCES:
  try:
   records.extend(parse_page(s['url'],s)); statuses.append({'name':s['name'],'url':s['url'],'status':'checked'})
  except Exception as e:
   statuses.append({'name':s['name'],'url':s['url'],'status':'unavailable','error':type(e).__name__})
  time.sleep(2)
 data={'updated_at':time.strftime('%Y-%m-%d %H:%M:%S'),'status':'ok' if records else 'waiting_for_verified_sources','records':records[:1000],'sources':statuses,'notice':'回收报价为来源页面公开报价整理，不代表洪盛集藏自身报价；受品相、版别、数量、号码、包装等影响，实际价格以双方当时确认结果为准。'}
 OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
 print('recovery records=',len(records))
if __name__=='__main__': main()
