#!/usr/bin/env python3
from __future__ import annotations
import json, re, time, urllib.robotparser
from collections import deque
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
DATA.mkdir(exist_ok=True)
UA = 'HongshengCollectionResearchBot/1.0 (+https://yang79403-wq.github.io/coin-ai-news/)'
SESSION = requests.Session()
SESSION.headers.update({'User-Agent': UA, 'Accept-Language': 'zh-CN,zh;q=0.9'})
TIMEOUT = 15
DELAY = 1.0
MAX_PAGES = 60

MARKET_SEEDS = [
    ('一尘网', 'http://www.pm001.net/'),
    ('一尘网备用', 'http://www1.pm001.net/'),
    ('钱币天堂', 'https://www.yy11.com/c2c/forum/4.html'),
]
FUJIAN_SEEDS = [
    ('福建官局造光绪元宝十文','福建铜元','1901-1905','https://tcmb.culture.tw/zh-tw/detail?id=14000113139&indexCode=MOCCOLLECTIONS'),
    ('福建官局造光绪元宝库平三分六厘','福建银元','清代','https://tcmb.culture.tw/zh-tw/detail?id=14000128171&indexCode=MOCCOLLECTIONS'),
    ('福建官局造光绪元宝库平七分二厘','福建银元','清代','https://tcmb.culture.tw/zh-tw/detail?id=14000128030&indexCode=MOCCOLLECTIONS'),
    ('福建官局造光绪元宝库平一钱四分四厘','福建银元','清代','https://tcmb.culture.tw/zh-tw/detail?id=14000113490&indexCode=MOCCOLLECTIONS'),
    ('福建省造光绪元宝库平七分二厘','福建银元','清代','https://tcmb.culture.tw/zh-tw/detail?id=14000128036&indexCode=MOCCOLLECTIONS'),
]

def clean(s):
    return re.sub(r'\s+', ' ', s or '').strip()

def can_fetch(url, robots):
    p = urlparse(url)
    if not p.netloc: return False
    if p.netloc not in robots:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(f'{p.scheme}://{p.netloc}/robots.txt')
        try: rp.read(); robots[p.netloc] = rp
        except Exception: robots[p.netloc] = None
    rp = robots[p.netloc]
    return True if rp is None else rp.can_fetch(UA, url)

def fetch(url, robots):
    if not can_fetch(url, robots): raise RuntimeError('robots-disallowed')
    r = SESSION.get(url, timeout=TIMEOUT, allow_redirects=True)
    r.raise_for_status()
    return r

def category(text):
    rules = [('纸币','纸币'),('纪念钞','纪念钞'),('纪念币','纪念币'),('金银币','金银币'),('金币','金银币'),('银元','银元'),('银币','银元'),('古钱','古钱币'),('铜元','铜元'),('铜币','铜元'),('硬币','硬币'),('邮票','邮票')]
    for k,v in rules:
        if k in text: return v
    return '其他'

def price(text):
    patterns = [
        r'(?:成交价|求购价|成交|求购|买入价|售价|价格)\s*[:：]?\s*(?:¥|￥)?\s*([0-9][0-9,，]*(?:\.[0-9]+)?)\s*(?:元|人民币|RMB)',
        r'(?:¥|￥)\s*([0-9][0-9,，]*(?:\.[0-9]+)?)'
    ]
    for p in patterns:
        m = re.search(p, text, re.I)
        if m: return m.group(1).replace(',','').replace('，','') + '元'
    return ''

def status(text):
    if any(x in text for x in ('流拍','无人出价','未成交')): return '流拍'
    if any(x in text for x in ('竞价中','正在竞价','拍卖中')): return '竞价中'
    if price(text) and any(x in text for x in ('成交','已成交')): return '成交'
    if price(text) and any(x in text for x in ('求购','买入价')): return '求购'
    return ''

def market_source(source, seed):
    robots, seen, queue, rows = {}, set(), deque([(seed,0)]), []
    pages = 0
    while queue and pages < MAX_PAGES:
        url, depth = queue.popleft(); key = url.split('#')[0]
        if key in seen or depth > 2: continue
        seen.add(key); pages += 1
        try: r = fetch(url, robots)
        except Exception: continue
        soup = BeautifulSoup(r.text, 'html.parser')
        text = clean(soup.get_text(' ', strip=True))
        title = clean(soup.title.get_text(' ', strip=True)) if soup.title else '公开交易记录'
        st, pr = status(text), price(text)
        if st in ('成交','求购') and pr:
            rows.append({'category':category(title+' '+text[:1000]),'name':title,'status':st,'price':pr,'quantity':'','date':datetime.now().strftime('%Y-%m-%d'),'source':source,'source_url':r.url})
        for a in soup.find_all('a', href=True):
            href = urljoin(r.url, a['href']).split('#')[0]
            if urlparse(href).netloc != urlparse(r.url).netloc: continue
            signal = (clean(a.get_text(' ',strip=True))+' '+href).lower()
            if href not in seen and any(k in signal for k in ('成交','求购','交易','钱币','银元','铜元','纸币','纪念币','古钱','硬币')):
                queue.append((href, depth+1))
        time.sleep(DELAY)
    unique=[]; keys=set()
    for row in rows:
        k=(row['source_url'],row['status'],row['price'])
        if k not in keys: keys.add(k); unique.append(row)
    return unique, pages

def fujian_archive():
    robots={}; out=[]
    for name, cat, period, url in FUJIAN_SEEDS:
        rec={'name':name,'category':cat,'period':period,'source':'国家文化记忆库/公开馆藏资料','source_url':url,'description':'','features':'','image_url':'','image_license':'','status':'source-only'}
        try:
            r=fetch(url, robots); soup=BeautifulSoup(r.text,'html.parser'); text=clean(soup.get_text(' ',strip=True))
            pos=text.find(name)
            rec['description']=text[pos:pos+700] if pos>=0 else text[:700]
            rec['features']=text[pos:pos+1200] if pos>=0 else text[:1200]
            og=soup.find('meta',attrs={'property':'og:image'})
            if og and og.get('content'): rec['image_url']=urljoin(r.url,og['content'])
            rec['image_license']='CC BY 3.0 TW（来源页标示）' if ('CC BY 3.0' in text or '創用CC姓名標示 3.0' in text) else '未确认开放授权，仅保留来源链接'
            rec['status']='ok'
        except Exception as e:
            rec['status']='source-unavailable:'+type(e).__name__
        out.append(rec); time.sleep(DELAY)
    return out

def write(name, obj):
    (DATA/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')

def main():
    now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    market=[]; stats=[]
    for source, seed in MARKET_SEEDS:
        try:
            rows,pages=market_source(source,seed); market.extend(rows); stats.append({'source':source,'pages':pages,'records':len(rows),'status':'ok'})
        except Exception as e:
            stats.append({'source':source,'pages':0,'records':0,'status':'error:'+type(e).__name__})
    write('market.json', {'updated':now,'sources':['一尘网','钱币天堂'],'stats':stats,'records':market})
    write('fujian.json', {'updated':now,'status':'ok','notice':'福建钱币专题只做资料收集、实物图鉴、历史整理与分析研究，不采集成交价或求购价。','records':fujian_archive()})
    print(json.dumps({'market_records':len(market),'fujian_records':len(FUJIAN_SEEDS),'stats':stats},ensure_ascii=False))

if __name__ == '__main__': main()
