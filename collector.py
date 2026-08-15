#!/usr/bin/env python3
from __future__ import annotations
import json,re,time
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

DATA=Path(__file__).resolve().parent/'data'; DATA.mkdir(exist_ok=True)
S=requests.Session(); S.headers.update({'User-Agent':'HongshengCollectionBot/6.2 (+https://yang79403-wq.github.io/coin-ai-news/)','Accept-Language':'zh-CN,zh;q=0.9'})
TIMEOUT=6
PM001=['http://www.pm001.net/','http://www1.pm001.net/','http://www2.pm001.net/']
YY11=['https://www.yy11.com/c2c/forum/4.html','https://yy11.com/c2c/forum/4.html']
PRICE_RE=re.compile(r'(?:¥|￥|RMB|人民币)?\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?)\s*(?:元|块|RMB)',re.I)

def get(url):
    r=S.get(url,timeout=TIMEOUT,allow_redirects=True); r.raise_for_status(); return r

def clean(x): return re.sub(r'\s+',' ',x or '').strip()
def nums(text):
    out=[]
    for m in PRICE_RE.finditer(text):
        try:
            v=float(m.group(1).replace(',',''))
            if 1<=v<=10000000: out.append(v)
        except: pass
    return out

def cat(text):
    t=text.lower(); rules=[('纸币',['纸币','人民币','冠号','纪念钞']),('银元',['银元','袁大头','孙小头','船洋','龙洋','光绪元宝']),('古钱币',['古钱','通宝','重宝','元宝','咸丰','乾隆','顺治','康熙']),('铜元',['铜元','铜币','大清铜币']),('金银币',['金币','金银币','熊猫币']),('纪念币',['纪念币']),('邮票',['邮票','邮品'])]
    for c,ks in rules:
        if any(k in t for k in ks): return c
    return '钱币综合'

def scan_market(base,name):
    health={'name':name,'url':base,'status':'error'}; rows=[]
    try: soup=BeautifulSoup(get(base).text,'html.parser'); health['status']='reachable'
    except Exception as e: health['error']=type(e).__name__; return rows,health
    candidates=[]
    for a in soup.find_all('a',href=True):
        title=clean(a.get_text(' ',strip=True)); href=a.get('href','')
        if not title: continue
        if name=='一尘网' and ('dispbbs.asp' in href.lower() or 'boardid=' in href.lower()): candidates.append((urljoin(base,href),title))
        if name=='钱币天堂' and '/c2c/topic/' in href: candidates.append((urljoin(base,href),title))
    seen=set()
    for url,title in candidates[:10]:
        if url in seen: continue
        seen.add(url)
        try:
            text=clean(BeautifulSoup(get(url).text,'html.parser').get_text(' ',strip=True))
            if name=='钱币天堂':
                m=re.search(r'物品成交价[^0-9]{0,50}([0-9][0-9,]*(?:\.[0-9]+)?)\s*元?',text)
                if not (m and '成交于' in text and '流拍' not in text): continue
                p=float(m.group(1).replace(',','')); status='成交'
            else:
                ps=[]
                for s in re.split(r'[。；\n]',text):
                    if re.search(r'(收购|回收|求购|成交|价格|报价)',s): ps+=nums(s)
                if not ps: continue
                p=ps[0]; status='求购' if '求购' in text else ('回收/收购' if re.search(r'(收购|回收)',text) else '成交/报价')
            rows.append({'category':cat(title+' '+text[:900]),'name':title[:100],'status':status,'price':f'{p:g}元','date':time.strftime('%Y-%m-%d'),'source':name,'source_url':url})
        except Exception: continue
    return rows,health

def fujian():
    seeds=[
    ('福建官局造光绪元宝当十铜元','福建铜元','1900-1905','中国国家博物馆','https://www.chnmuseum.cn/zp/zpml/hb/202106/t20210610_250327.shtml'),
    ('福建官局造光緒元寶十文','福建铜元','1901-1905','国家文化记忆库·国立历史博物馆','https://tcmb.culture.tw/zh-tw/detail?id=14000113139&indexCode=MOCCOLLECTIONS'),
    ('福建官局造光緒元寶庫平三分六厘','福建银元','约1900-1908','国家文化记忆库·国立历史博物馆','https://tcmb.culture.tw/zh-tw/detail?id=14000128171&indexCode=MOCCOLLECTIONS'),
    ('福建官局造光緒元寶庫平七分二厘','福建银元','约1900-1908','国家文化记忆库·国立历史博物馆','https://tcmb.culture.tw/zh-tw/detail?id=14000128030&indexCode=MOCCOLLECTIONS'),
    ('福建官局造光緒元寶庫平一錢四分四厘','福建银元','约1900-1908','国家文化记忆库·国立历史博物馆','https://tcmb.culture.tw/zh-tw/detail?id=14000113490&indexCode=MOCCOLLECTIONS'),
    ('福建省造光緒元寶庫平七分二厘','福建银元','约1890-1908','国家文化记忆库·国立历史博物馆','https://tcmb.culture.tw/zh-tw/detail?id=14000128036&indexCode=MOCCOLLECTIONS')]
    out=[]
    for name,category,period,source,url in seeds:
        r={'name':name,'category':category,'period':period,'source':source,'source_url':url,'image_status':'source-page-only'}
        try:
            soup=BeautifulSoup(get(url).text,'html.parser'); text=clean(soup.get_text(' ',strip=True)); r['features']=text[:850]
            if 'CC BY 3.0 TW' in text or '創用CC姓名標示 3.0 台灣' in text: r['image_status']='open-license-source'
            og=soup.find('meta',attrs={'property':'og:image'}); r['source_image_url']=urljoin(url,og.get('content')) if og and og.get('content') else ''
        except Exception as e: r['error']=type(e).__name__; r['features']='来源页暂时无法访问，保留原始链接等待下一次自动重试。'
        out.append(r)
    return out

def main():
    market=[]; sources=[]
    for u in PM001:
        r,h=scan_market(u,'一尘网'); sources.append(h); market+=r
        if h['status']=='reachable': break
    for u in YY11:
        r,h=scan_market(u,'钱币天堂'); sources.append(h); market+=r
        if h['status']=='reachable': break
    unique={x['source_url']:x for x in market}; market=sorted(unique.values(),key=lambda x:(x['category'],x['name']))
    now=time.strftime('%Y-%m-%d %H:%M:%S')
    (DATA/'market.json').write_text(json.dumps({'updated_at':now,'status':'ok' if market else 'waiting_for_verified_sources','records':market,'sources':sources,'notice':'只展示公开、可核验记录；无真实记录时不编造价格。'},ensure_ascii=False,indent=2),encoding='utf-8')
    fj=fujian()
    (DATA/'fujian.json').write_text(json.dumps({'updated_at':now,'title':'洪盛集藏·福建钱币资料库','notice':'只做资料收集、实物图片资料、历史整理、版别分析与学习研究，不采集成交价或求购价。','records':fj},ensure_ascii=False,indent=2),encoding='utf-8')
    print('market=',len(market),'fujian=',len(fj))
if __name__=='__main__': main()
