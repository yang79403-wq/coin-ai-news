#!/usr/bin/env python3
from __future__ import annotations
import json,re,time
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'; DATA.mkdir(exist_ok=True)
UA='HongshengCollectionBot/6.0 (+https://yang79403-wq.github.io/coin-ai-news/)'
S=requests.Session(); S.headers.update({'User-Agent':UA,'Accept-Language':'zh-CN,zh;q=0.9'})
TIMEOUT=20
PM001=['http://www.pm001.net/','http://www1.pm001.net/','http://www2.pm001.net/','http://www3.pm001.net/']
YY11=['https://www.yy11.com/c2c/forum/4.html','https://yy11.com/c2c/forum/4.html']
PRICE_RE=re.compile(r'(?:¥|￥|RMB|人民币)?\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?)\s*(?:元|块|RMB)',re.I)

def fetch(url):
    r=S.get(url,timeout=TIMEOUT,allow_redirects=True); r.raise_for_status(); return r

def clean(x): return re.sub(r'\s+',' ',x or '').strip()
def prices(text):
    out=[]
    for m in PRICE_RE.finditer(text):
        try:
            v=float(m.group(1).replace(',',''))
            if 1<=v<=10000000: out.append(v)
        except: pass
    return out

def category(text):
    t=text.lower()
    for c,ks in [('纸币',['纸币','人民币','冠号','连体钞','纪念钞']),('银元',['银元','袁大头','孙小头','船洋','龙洋','大清银币','光绪元宝']),('古钱币',['古钱','通宝','重宝','元宝','咸丰','乾隆','顺治','康熙']),('铜元',['铜元','铜币','大清铜币','机制铜']),('金银币',['金币','金银币','熊猫币']),('纪念币',['纪念币','流通纪念币']),('邮票',['邮票','邮品']),('硬币',['硬币','分币','长城币'])]:
        if any(k.lower() in t for k in ks): return c
    return '钱币综合'

def parse_pm001(base):
    records=[]; health={'name':'一尘网','url':base,'status':'error'}
    try:
        home=fetch(base); health['status']='reachable'; soup=BeautifulSoup(home.text,'html.parser')
    except Exception as e:
        health['error']=type(e).__name__; return records,health
    boards=[]
    for a in soup.find_all('a',href=True):
        h=a['href']; title=clean(a.get_text(' ',strip=True))
        if title and ('boardid=' in h.lower()): boards.append((urljoin(base,h),title))
    seen=set()
    for board_url,board_title in boards[:120]:
        try: bs=BeautifulSoup(fetch(board_url).text,'html.parser')
        except: continue
        for a in bs.find_all('a',href=True):
            h=a['href']; title=clean(a.get_text(' ',strip=True))
            if not title or 'dispbbs.asp' not in h.lower(): continue
            topic=urljoin(board_url,h); key=topic.split('&page=')[0].lower()
            if key in seen: continue
            seen.add(key)
            try:
                ts=BeautifulSoup(fetch(topic).text,'html.parser'); text=clean(ts.get_text(' ',strip=True))
                if not re.search(r'(收购|回收|求购|成交|价格|报价)',text): continue
                candidates=[]
                for sentence in re.split(r'[。；\n]',text):
                    if re.search(r'(收购|回收|求购|成交|价格|报价)',sentence): candidates += prices(sentence)
                if not candidates: continue
                status='求购' if '求购' in text else ('回收/收购' if re.search(r'(收购|回收)',text) else '成交/报价')
                records.append({'category':category(title+' '+text[:1800]),'name':title[:120],'status':status,'price':f'{candidates[0]:g}元','date':time.strftime('%Y-%m-%d'),'source':'一尘网','source_url':topic,'board':board_title[:80]})
            except Exception: pass
            time.sleep(.15)
    return records,health

def parse_yy11(base):
    records=[]; health={'name':'钱币天堂','url':base,'status':'error'}
    try: soup=BeautifulSoup(fetch(base).text,'html.parser'); health['status']='reachable'
    except Exception as e: health['error']=type(e).__name__; return records,health
    for a in soup.find_all('a',href=True)[:1000]:
        h=a['href']; title=clean(a.get_text(' ',strip=True))
        if '/c2c/topic/' not in h or not title: continue
        topic=urljoin(base,h)
        try:
            ts=BeautifulSoup(fetch(topic).text,'html.parser'); text=clean(ts.get_text(' ',strip=True))
            m=re.search(r'物品成交价[^0-9]{0,60}(?:¥|￥)?\s*([0-9][0-9,]*(?:\.[0-9]+)?)\s*元?',text)
            if m and '成交于' in text and '流拍' not in text:
                records.append({'category':category(title+' '+text[:1600]),'name':title[:120],'status':'成交','price':f"{float(m.group(1).replace(',','')):g}元",'date':time.strftime('%Y-%m-%d'),'source':'钱币天堂','source_url':topic})
        except Exception: pass
        time.sleep(.15)
    return records,health

def fujian():
    seeds=[
      ('福建官局造光绪元宝当十铜元','福建铜元','1900-1905','中国国家博物馆','https://www.chnmuseum.cn/zp/zpml/hb/202106/t20210610_250327.shtml'),
      ('福建官局造光緒元寶十文','福建铜元','1901-1905','国家文化记忆库·国立历史博物馆','https://tcmb.culture.tw/zh-tw/detail?id=14000113139&indexCode=MOCCOLLECTIONS'),
      ('福建官局造光緒元寶庫平三分六厘','福建银元','约1900-1908','国家文化记忆库·国立历史博物馆','https://tcmb.culture.tw/zh-tw/detail?id=14000128171&indexCode=MOCCOLLECTIONS'),
      ('福建官局造光緒元寶庫平七分二厘','福建银元','约1900-1908','国家文化记忆库·国立历史博物馆','https://tcmb.culture.tw/zh-tw/detail?id=14000128030&indexCode=MOCCOLLECTIONS'),
      ('福建官局造光緒元寶庫平一錢四分四厘','福建银元','约1900-1908','国家文化记忆库·国立历史博物馆','https://tcmb.culture.tw/zh-tw/detail?id=14000113490&indexCode=MOCCOLLECTIONS'),
      ('福建省造光緒元寶庫平七分二厘','福建银元','约1890-1908','国家文化记忆库·国立历史博物馆','https://tcmb.culture.tw/zh-tw/detail?id=14000128036&indexCode=MOCCOLLECTIONS')]
    out=[]
    for name,cat,period,source,url in seeds:
        rec={'name':name,'category':cat,'period':period,'source':source,'source_url':url,'image_status':'source-page-only'}
        try:
            soup=BeautifulSoup(fetch(url).text,'html.parser'); text=clean(soup.get_text(' ',strip=True))
            rec['features']=text[:1100]
            if 'CC BY 3.0 TW' in text or '創用CC姓名標示 3.0 台灣' in text: rec['image_status']='open-license-source'
            og=soup.find('meta',attrs={'property':'og:image'}); rec['source_image_url']=urljoin(url,og.get('content')) if og and og.get('content') else ''
        except Exception as e: rec['error']=type(e).__name__; rec['features']='来源页暂时无法访问，保留原始链接等待下次自动重试。'
        out.append(rec); time.sleep(.4)
    return out

def main():
    market=[]; sources=[]
    for base in PM001:
        rows,h=parse_pm001(base); sources.append(h); market+=rows
        if rows: break
    for base in YY11:
        rows,h=parse_yy11(base); sources.append(h); market+=rows
        if rows: break
    uniq={}
    for r in market: uniq[(r['source'],r['source_url'])]=r
    market=sorted(uniq.values(),key=lambda x:(x['category'],x['name']))
    now=time.strftime('%Y-%m-%d %H:%M:%S')
    (DATA/'market.json').write_text(json.dumps({'updated_at':now,'status':'ok' if market else 'waiting_for_verified_sources','records':market,'sources':sources,'notice':'只展示公开、可核验记录；无真实记录时不编造价格。'},ensure_ascii=False,indent=2),encoding='utf-8')
    (DATA/'fujian.json').write_text(json.dumps({'updated_at':now,'title':'洪盛集藏·福建钱币资料库','notice':'只做资料收集、实物图片资料、历史整理、版别分析与学习研究，不采集成交价或求购价。','records':fujian()},ensure_ascii=False,indent=2),encoding='utf-8')
    print('market records:',len(market),'fujian records:',len(json.loads((DATA/'fujian.json').read_text())['records']))
if __name__=='__main__': main()
