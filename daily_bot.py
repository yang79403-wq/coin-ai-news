#!/usr/bin/env python3
import json,re,time
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin,urlparse
import requests
from bs4 import BeautifulSoup

ROOT=Path(__file__).parent
DATA=ROOT/'data'
UA='HongshengCollectionBot/2.0 (+https://yang79403-wq.github.io/coin-ai-news/)'
HEAD={'User-Agent':UA,'Accept-Language':'zh-CN,zh;q=0.9'}
S=requests.Session();S.headers.update(HEAD)

MARKET_SEEDS=[
 ('一尘网','http://www.pm001.net/'),
 ('钱币天堂','https://www.yy11.com/c2c/forum/4.html#1'),
]
FUJIAN_SEEDS=[
 ('福建官局造光绪元宝十文','福建铜元','https://tcmb.culture.tw/zh-tw/detail?id=14000113139&indexCode=MOCCOLLECTIONS'),
 ('福建官局造光绪元宝库平三分六厘','福建银元','https://tcmb.culture.tw/zh-tw/detail?id=14000128171&indexCode=MOCCOLLECTIONS'),
 ('福建官局造光绪元宝库平七分二厘','福建银元','https://tcmb.culture.tw/zh-tw/detail?id=14000128030&indexCode=MOCCOLLECTIONS'),
 ('福建官局造光绪元宝库平一钱四分四厘','福建银元','https://tcmb.culture.tw/zh-tw/detail?id=14000113490&indexCode=MOCCOLLECTIONS'),
 ('福建省造光绪元宝库平七分二厘','福建银元','https://tcmb.culture.tw/zh-tw/detail?id=14000128036&indexCode=MOCCOLLECTIONS'),
]

def get(url):
    r=S.get(url,timeout=25);r.raise_for_status();return r

def category(t):
    t=t.lower()
    for k,v in [('纸币','纸币'),('纪念钞','纪念钞'),('纪念币','纪念币'),('银元','银元'),('银币','金银币'),('金币','金银币'),('铜元','铜元'),('铜币','铜元'),('古钱','古钱币'),('硬币','硬币')]:
        if k in t:return v
    return '其他'

def parse_market(source,seed):
    found=[];seen=set();queue=[seed];depth=0
    while queue and depth<2 and len(seen)<80:
        nextq=[]
        for u in queue:
            try:r=get(u)
            except Exception:continue
            soup=BeautifulSoup(r.text,'html.parser');base=r.url
            for a in soup.find_all('a',href=True):
                href=urljoin(base,a['href']);txt=' '.join(a.stripped_strings)
                if not href.startswith(('http://','https://')):continue
                if urlparse(href).netloc!=urlparse(base).netloc:continue
                key=href.split('#')[0]
                if key in seen:continue
                seen.add(key)
                low=txt.lower()
                # 交易主题/成交/求购页面才进入数据层
                if any(k in low for k in ['成交','求购','出售','拍卖','钱币','银元','铜元','纸币','古钱','纪念币']):
                    queue.append(key)
                if any(k in low for k in ['成交','已成交','成交价','求购价','求购','买入价']):
                    m=re.search(r'(?:¥|￥|人民币)?\s*([0-9]{1,3}(?:[,，][0-9]{3})*(?:\.[0-9]+)?)\s*(?:元|rmb)?',txt,re.I)
                    price=m.group(1).replace(',','').replace('，','')+'元' if m else ''
                    status='成交' if any(k in low for k in ['已成交','成交价','成交']) else '求购'
                    found.append({'category':category(txt),'name':txt[:100] or '未命名记录','status':status,'price':price,'quantity':'','date':datetime.now().strftime('%Y-%m-%d'),'source':source,'source_url':key})
            depth+=1
            time.sleep(.7)
        queue=nextq if nextq else queue[80:]
        if depth>=2:break
    # 去重
    out=[];keys=set()
    for x in found:
        k=(x['source_url'],x['status'],x['price'],x['name'])
        if k not in keys:keys.add(k);out.append(x)
    return out[:500]

def fujian():
    out=[]
    for name,cat,url in FUJIAN_SEEDS:
        try:
            r=get(url);soup=BeautifulSoup(r.text,'html.parser');text=' '.join(soup.stripped_strings)
            og=soup.find('meta',attrs={'property':'og:image'})
            img=urljoin(r.url,og.get('content')) if og and og.get('content') else ''
            out.append({'name':name,'category':cat,'period':'','description':text[:500],'features':text[:900],'source':'国家文化记忆库/公开馆藏资料','source_url':url,'image_url':img,'image_note':'图片授权以来源页为准；授权不明确时仅展示来源链接'})
        except Exception: pass
        time.sleep(.8)
    return out

def main():
    now=datetime.now().strftime('%Y-%m-%d %H:%M')
    market=[]
    for source,url in MARKET_SEEDS:
        try:market += parse_market(source,url)
        except Exception as e: print(source,e)
    # 不伪造数据：没有识别到可靠价格就保持空记录
    (DATA/'market.json').write_text(json.dumps({'updated':now,'sources':[x[0] for x in MARKET_SEEDS],'records':market},ensure_ascii=False,indent=2),encoding='utf-8')
    fj=fujian()
    (DATA/'fujian.json').write_text(json.dumps({'updated':now,'records':fj},ensure_ascii=False,indent=2),encoding='utf-8')
    print('market=',len(market),'fujian=',len(fj))
if __name__=='__main__':main()
