#!/usr/bin/env python3
from __future__ import annotations
import json,re,time,hashlib
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data/fujian-coins.json'
IMG_DIR=ROOT/'assets/fujian'; IMG_DIR.mkdir(parents=True,exist_ok=True)
UA='HongshengCollectionResearchBot/1.1 (+https://yang79403-wq.github.io/coin-ai-news/)'

SEEDS=[
 {'name':'福建省造光绪元宝七分二厘','category':'福建银元','source':'古泉园地图库','url':'https://tuku.chcoin.com/detail-743.html','image_mode':'source-index'},
 {'name':'福建闽关十文','category':'福建铜元','source':'古泉社区','url':'https://bbs.chcoin.com/show-17354241.html','image_mode':'source-index'},
 {'name':'美品福建小闽关','category':'福建铜元','source':'古泉社区','url':'https://bbs.chcoin.com/show-6091790.html','image_mode':'source-index'},
 {'name':'福建机制币/铜元资料','category':'福建铜元','source':'古泉园地图库','url':'https://tuku.chcoin.com/listing-748-0-0-5.html','image_mode':'source-index'},
 {'name':'华夏古泉古钱图库','category':'福建古钱币','source':'华夏古泉网','url':'https://wwwh.huaxiaguquan.com/hxgq/cn/','image_mode':'source-index'},
 {'name':'福建钱币公开资料检索入口','category':'福建钱币研究','source':'华夏古泉网','url':'https://wwwh.huaxiaguquan.com/hxgq/cn/index.jsp','image_mode':'source-index'},
]
KEYWORDS=['福建','闽','福州','厦门','泉州','漳州','宁德','福安','莆田','龙岩','福建官局','福建省造','闽关','福建通宝','福建银行','福建省银行']

def fetch(url):
 r=requests.get(url,headers={'User-Agent':UA},timeout=30); r.raise_for_status(); return r

def clean(s): return re.sub(r'\s+',' ',s or '').strip()

def parse(seed):
 out=dict(seed); out['source_url']=seed['url']; out['image_urls']=[]; out['image_policy']='仅在来源明确开放授权或自有/获授权时本地保存图片；否则只保存来源页和图片索引。'
 try:
  soup=BeautifulSoup(fetch(seed['url']).text,'html.parser'); text=clean(soup.get_text(' ',strip=True))
  title=soup.find('title'); out['page_title']=clean(title.get_text()) if title else seed['name']
  out['summary']=text[:900]
  imgs=[]
  for img in soup.find_all('img'):
   src=img.get('src') or img.get('data-src') or img.get('data-original')
   if src:
    u=urljoin(seed['url'],src)
    alt=clean(img.get('alt',''))
    if any(k in (alt+' '+text[:1500]) for k in KEYWORDS): imgs.append({'url':u,'alt':alt})
  # 去重并限制，防止把站点导航图片全部收走
  seen=set()
  for x in imgs:
   if x['url'] not in seen: seen.add(x['url']); out['image_urls'].append(x)
  out['image_count']=len(out['image_urls'])
  out['status']='collected'
 except Exception as e:
  out['status']='fetch-error:'+type(e).__name__
 return out

def main():
 old=json.loads(DATA.read_text(encoding='utf-8')) if DATA.exists() else {}
 byurl={x.get('source_url'):x for x in old.get('records',[])}
 for s in SEEDS:
  r=parse(s); prev=byurl.get(s['url'],{}); prev.update(r); byurl[s['url']]=prev; time.sleep(1.5)
 records=list(byurl.values())
 DATA.write_text(json.dumps({'updated':time.strftime('%Y-%m-%d'),'title':'洪盛集藏·福建钱币资料库','notice':'公益资料收集、实物图鉴、历史整理与研究；不采集成交/求购价格。','categories':['福建古钱币','福建铜元','福建银元','福建银角','福建纸币','福建地方货币','福建铸币历史','福建钱币研究'],'records':records},ensure_ascii=False,indent=2),encoding='utf-8')
 print('福建资料来源更新：',len(records),'条；图片索引：',sum(x.get('image_count',0) for x in records))
if __name__=='__main__': main()
