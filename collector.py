#!/usr/bin/env python3
import json,re,time
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

UA='HongshengCollectionResearchBot/1.0'; TIMEOUT=20
MARKET_SOURCES=[
 {'name':'一尘网','url':'http://www.pm001.net/','category':'未分类'},
 {'name':'钱币天堂','url':'https://www.yy11.com/c2c/forum/4.html#1','category':'钱币交易'},
]
FUJIAN_SOURCES=[
 {'name':'中国国家博物馆','url':'https://www.chnmuseum.cn/zp/zpml/hb/202106/t20210610_250327.shtml'},
 {'name':'国家文化记忆库·国立历史博物馆','url':'https://tcmb.culture.tw/zh-tw/detail?id=14000113139&indexCode=MOCCOLLECTIONS'},
 {'name':'国家文化记忆库·国立历史博物馆','url':'https://tcmb.culture.tw/zh-tw/detail?id=14000128171&indexCode=MOCCOLLECTIONS'},
 {'name':'国家文化记忆库·国立历史博物馆','url':'https://tcmb.culture.tw/zh-tw/detail?id=14000113490&indexCode=MOCCOLLECTIONS'},
]
def get(url):
 r=requests.get(url,headers={'User-Agent':UA},timeout=TIMEOUT); r.raise_for_status(); return r
def clean(s): return re.sub(r'\s+',' ',s or '').strip()
def collect_market():
 records=[]; sources=[]
 for src in MARKET_SOURCES:
  try:
   r=get(src['url']); soup=BeautifulSoup(r.text,'html.parser')
   sources.append({'name':src['name'],'url':src['url'],'status':'reachable'})
   for line in soup.stripped_strings:
    line=clean(line)
    if re.search(r'(成交|求购)',line) and re.search(r'(¥|￥|元)',line):
     price=re.search(r'(?:¥|￥)?\s*([0-9]+(?:\.[0-9]+)?)\s*元?',line)
     if price:
      status='成交' if '成交' in line else '求购'
      records.append({'category':src['category'],'name':line[:80],'status':status,'price':price.group(1)+'元','date':time.strftime('%Y-%m-%d'),'source':src['name'],'source_url':src['url']})
   time.sleep(1)
  except Exception as e:
   sources.append({'name':src['name'],'url':src['url'],'status':'unreachable','error':type(e).__name__})
 return records,sources
def collect_fujian():
 records=[]
 for src in FUJIAN_SOURCES:
  try:
   r=get(src['url']); soup=BeautifulSoup(r.text,'html.parser'); text=clean(soup.get_text(' ',strip=True))
   title=clean(soup.title.get_text()) if soup.title else '福建钱币资料'
   img=''; og=soup.find('meta',attrs={'property':'og:image'})
   if og and og.get('content'): img=urljoin(src['url'],og['content'])
   records.append({'name':title[:120],'category':'福建钱币资料','features':text[:700],'source':src['name'],'source_url':src['url'],'source_image_url':img,'image_status':'来源页图片，授权确认后再镜像','updated':time.strftime('%Y-%m-%d')})
   time.sleep(1)
  except Exception as e:
   records.append({'name':'资料来源暂时无法访问','category':'福建钱币资料','source':src['name'],'source_url':src['url'],'image_status':'source-only','error':type(e).__name__})
 return records
def main():
 m,s=collect_market(); f=collect_fujian()
 Path('data/price-tables.json').write_text(json.dumps({'updated_at':time.strftime('%Y-%m-%d %H:%M:%S'),'status':'ok' if m else 'waiting_for_verified_sources','records':m,'sources':s,'notice':'仅显示明确可核验的公开成交/求购记录；没有真实数据不编造价格。'},ensure_ascii=False,indent=2),encoding='utf-8')
 Path('data/fujian-coins.json').write_text(json.dumps({'updated':time.strftime('%Y-%m-%d'),'title':'洪盛集藏·福建钱币资料库','notice':'只做资料收集、实物图鉴、历史整理与学习研究，不采集成交价或求购价。','records':f},ensure_ascii=False,indent=2),encoding='utf-8')
 print('market records:',len(m),'fujian records:',len(f))
if __name__=='__main__': main()
