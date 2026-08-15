#!/usr/bin/env python3
from __future__ import annotations
import json,re,time,urllib.robotparser
from collections import deque
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urljoin,urlparse
import requests
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'
DATA.mkdir(exist_ok=True)
UA='HongshengCollectionResearchBot/1.0 (+https://yang79403-wq.github.io/coin-ai-news/)'
HEAD={'User-Agent':UA,'Accept-Language':'zh-CN,zh;q=0.9'}
S=requests.Session();S.headers.update(HEAD)
TIMEOUT=25
MAX_PAGES=180
DELAY=0.8

MARKET_SEEDS=[
 ('一尘网','http://www.pm001.net/'),
 ('一尘网备用','http://www1.pm001.net/'),
 ('钱币天堂','https://www.yy11.com/c2c/forum/4.html'),
]
FUJIAN_SEEDS=[
 ('福建官局造光绪元宝十文','福建铜元','1901-1905','https://tcmb.culture.tw/zh-tw/detail?id=14000113139&indexCode=MOCCOLLECTIONS'),
 ('福建官局造光绪元宝库平三分六厘','福建银元','清代','https://tcmb.culture.tw/zh-tw/detail?id=14000128171&indexCode=MOCCOLLECTIONS'),
 ('福建官局造光绪元宝库平七分二厘','福建银元','清代','https://tcmb.culture.tw/zh-tw/detail?id=14000128030&indexCode=MOCCOLLECTIONS'),
 ('福建官局造光绪元宝库平一钱四分四厘','福建银元','清代','https://tcmb.culture.tw/zh-tw/detail?id=14000113490&indexCode=MOCCOLLECTIONS'),
 ('福建省造光绪元宝库平七分二厘','福建银元','清代','https://tcmb.culture.tw/zh-tw/detail?id=14000128036&indexCode=MOCCOLLECTIONS'),
]

def clean(s:str)->str:
    return re.sub(r'\s+',' ',s or '').strip()

def allowed(url:str, cache:dict)->bool:
    p=urlparse(url); host=p.netloc
    if not host:return False
    if host not in cache:
        rp=urllib.robotparser.RobotFileParser();rp.set_url(f'{p.scheme}://{host}/robots.txt')
        try:rp.read()
        except Exception: cache[host]=None
        else: cache[host]=rp
    rp=cache.get(host)
    return True if rp is None else rp.can_fetch(UA,url)

def get(url:str, robots:dict):
    if not allowed(url,robots): raise RuntimeError('robots-disallowed')
    r=S.get(url,timeout=TIMEOUT,allow_redirects=True)
    r.raise_for_status()
    return r

def category(text:str)->str:
    t=text.lower()
    rules=[('第一套人民币','第一套人民币'),('第二套人民币','第二套人民币'),('第三套人民币','第三套人民币'),('第四套人民币','第四套人民币'),('第五套人民币','第五套人民币'),('纪念钞','纪念钞'),('连体钞','连体钞'),('纪念币','纪念币'),('金银币','金银币'),('金币','金银币'),('银元','银元'),('银币','银元'),('古钱','古钱币'),('铜元','铜元'),('铜币','铜元'),('硬币','硬币'),('邮票','邮票')]
    for k,v in rules:
        if k in t:return v
    return '其他'

def price_from_text(text:str)->str:
    # 只接受紧邻人民币单位或明确价格字段的数字，避免把年份/编号当价格。
    pats=[r'(?:成交价|成交|求购价|求购|买入价|售价|价格)\s*[:：]?\s*(?:¥|￥)?\s*([0-9][0-9,，]*(?:\.[0-9]+)?)\s*(?:元|人民币|RMB)',r'(?:¥|￥)\s*([0-9][0-9,，]*(?:\.[0-9]+)?)']
    for pat in pats:
        m=re.search(pat,text,re.I)
        if m:return m.group(1).replace(',','').replace('，','')+'元'
    return ''

def status_from_text(text:str):
    t=text.lower()
    if any(k in t for k in ['流拍','无人出价','未成交']):return '流拍'
    if any(k in t for k in ['竞价中','正在竞价','拍卖中']):return '竞价中'
    if any(k in t for k in ['已成交','成交价','成交']) and price_from_text(text):return '成交'
    if any(k in t for k in ['求购价','求购','买入价']) and price_from_text(text):return '求购'
    return ''

def market_source(source,seed):
    robots={};q=deque([(seed,0)]);seen=set();rows=[];pages=0
    while q and pages<MAX_PAGES:
        url,depth=q.popleft();key=url.split('#')[0]
        if key in seen or depth>3:continue
        seen.add(key);pages+=1
        try:r=get(url,robots)
        except Exception:continue
        base=r.url;soup=BeautifulSoup(r.text,'html.parser')
        page_text=clean(soup.get_text(' ',strip=True))
        # 页面本身有明确交易字段时记录一条页面级行情。
        st=status_from_text(page_text);pr=price_from_text(page_text)
        title=clean(soup.title.get_text(' ',strip=True)) if soup.title else ''
        if st and pr:
            rows.append({'category':category(title+' '+page_text[:1200]),'name':title or '公开交易记录','status':st,'price':pr,'quantity':'','date':datetime.now().strftime('%Y-%m-%d'),'source':source,'source_url':base})
        for a in soup.find_all('a',href=True):
            href=urljoin(base,a['href']).split('#')[0];txt=clean(a.get_text(' ',strip=True))
            if not href.startswith(('http://','https://')):continue
            if urlparse(href).netloc!=urlparse(base).netloc:continue
            if href in seen:continue
            signal=(txt+' '+href).lower()
            if any(k in signal for k in ['成交','求购','出售','拍卖','交易','钱币','银元','铜元','纸币','纪念币','古钱','硬币']):
                q.append((href,depth+1))
        time.sleep(DELAY)
    # 去重，保留来源最具体的页面
    out=[];keys=set()
    for x in rows:
        k=(x['source_url'],x['status'],x['price'])
        if k not in keys:keys.add(k);out.append(x)
    return out,pages

def fujian_archive():
    robots={};out=[]
    for name,cat,period,url in FUJIAN_SEEDS:
        rec={'name':name,'category':cat,'period':period,'source':'国家文化记忆库/公开馆藏资料','source_url':url,'description':'','features':'','image_url':'','image_license':'','status':'ok'}
        try:
            r=get(url,robots);soup=BeautifulSoup(r.text,'html.parser');text=clean(soup.get_text(' ',strip=True))
            rec['description']=text[:700]
            # 截取与品种名称相关的正文，避免整页导航噪声。
            pos=text.find(name)
            rec['features']=text[pos:pos+1400] if pos>=0 else text[:1400]
            og=soup.find('meta',attrs={'property':'og:image'})
            if og and og.get('content'):rec['image_url']=urljoin(r.url,og['content'])
            if 'CC BY 3.0' in text or '創用CC姓名標示 3.0' in text:rec['image_license']='CC BY 3.0 TW（来源页标示）'
            elif 'CC BY' in text:rec['image_license']='CC BY（来源页标示）'
            else:rec['image_license']='未确认开放授权，仅保留来源链接'
        except Exception as e:
            rec['status']='error:'+type(e).__name__
        out.append(rec);time.sleep(DELAY)
    return out

def write(path,obj):
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')

def main():
    now=datetime.now(timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S')
    market=[];stats=[]
    for source,url in MARKET_SEEDS:
        try:
            rows,pages=market_source(source,url);market.extend(rows);stats.append({'source':source,'pages':pages,'records':len(rows),'status':'ok'})
        except Exception as e:stats.append({'source':source,'pages':0,'records':0,'status':'error:'+type(e).__name__})
    # 只有明确成交/求购状态且有价格的记录进入价格表。
    write(DATA/'market.json',{'updated':now,'sources':['一尘网','钱币天堂'],'stats':stats,'records':market})
    fj=fujian_archive();write(DATA/'fujian.json',{'updated':now,'status':'ok','notice':'福建钱币专题只做资料收集、实物图鉴、历史整理与分析研究，不采集成交价或求购价。','records':fj})
    print(json.dumps({'market_records':len(market),'fujian_records':len(fj),'stats':stats},ensure_ascii=False))

if __name__=='__main__':main()
