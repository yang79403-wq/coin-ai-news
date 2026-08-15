#!/usr/bin/env python3
from __future__ import annotations
import json,re,time
from pathlib import Path
from urllib.parse import urljoin,urlparse
import requests
from bs4 import BeautifulSoup

UA='HongshengCollectionResearchBot/2.0 (+https://yang79403-wq.github.io/coin-ai-news/)'
TIMEOUT=18
ROOT=Path(__file__).resolve().parent
SESSION=requests.Session(); SESSION.headers.update({'User-Agent':UA,'Accept-Language':'zh-CN,zh;q=0.9'})
PM001=['http://www.pm001.net/','http://www1.pm001.net/','http://www2.pm001.net/','http://www3.pm001.net/']
YY11=['https://www.yy11.com/c2c/forum/4.html','https://yy11.com/c2c/forum/4.html']
PRICE_RE=re.compile(r'(?:¥|￥|RMB|人民币)?\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?)\s*(?:元|块|RMB)?',re.I)

def fetch(url):
    r=SESSION.get(url,timeout=TIMEOUT,allow_redirects=True)
    r.raise_for_status()
    return r

def clean(s): return re.sub(r'\s+',' ',s or '').strip()

def price_values(text):
    vals=[]
    for m in PRICE_RE.finditer(text):
        try:
            v=float(m.group(1).replace(',',''))
            if 0 < v < 100000000: vals.append(v)
        except: pass
    return vals

def classify(text):
    t=text.lower()
    rules=[('纸币',['纸币','人民币','冠号','连体钞','纪念钞']),('银元',['银元','袁大头','孙小头','船洋','龙洋','大清银币','光绪元宝']),('古钱币',['古钱','通宝','重宝','元宝','咸丰','乾隆','顺治','康熙','崇宁']),('铜元',['铜元','铜币','大清铜币','机制币']),('金银币',['金币','金银币','银币','熊猫币']),('纪念币',['纪念币','流通纪念币']),('邮票',['邮票','邮品']),('硬币',['硬币','分币','长城币'])]
    for c,ks in rules:
        if any(k.lower() in t for k in ks): return c
    return '钱币综合'

def parse_pm001(base):
    records=[]; sources=[]; seen=set(); boards=[]
    try:
        r=fetch(base); soup=BeautifulSoup(r.text,'html.parser')
        sources.append({'name':'一尘网','url':base,'status':'reachable'})
        for a in soup.find_all('a',href=True):
            h=a['href']; title=clean(a.get_text(' ',strip=True))
            if 'boardID=' in h or 'BoardID=' in h:
                u=urljoin(base,h); boards.append((u,title))
    except Exception as e:
        sources.append({'name':'一尘网','url':base,'status':'unreachable','error':type(e).__name__})
        return records,sources
    unique=[]
    for u,t in boards:
        key=(u.split('&')[0],t)
        if key not in unique: unique.append(key)
    for board_url,board_title in unique[:80]:
        for page in range(1,11):
            u=board_url if page==1 else re.sub(r'([?&])page=\d+','\\1page='+str(page),board_url)
            if page>1 and 'page=' not in u: u += ('&' if '?' in u else '?')+'page='+str(page)
            try:
                s=BeautifulSoup(fetch(u).text,'html.parser')
                links=[]
                for a in s.find_all('a',href=True):
                    h=a['href']; title=clean(a.get_text(' ',strip=True))
                    if 'dispbbs.asp' in h and ('ID=' in h or 'id=' in h) and title:
                        links.append((urljoin(u,h),title))
                if not links: break
                for topic_url,title in links[:80]:
                    k=topic_url.lower().split('&page=')[0]
                    if k in seen: continue
                    seen.add(k)
                    try:
                        ts=BeautifulSoup(fetch(topic_url).text,'html.parser'); text=clean(ts.get_text(' ',strip=True))
                        if not re.search(r'(收购|回收|求购|成交|价格|报价)',text): continue
                        vals=price_values(text)
                        if not vals: continue
                        status='回收/收购' if re.search(r'(收购|回收)',text) else ('求购' if '求购' in text else '成交/报价')
                        # 只取页面中最接近价格语句的数字，避免把电话/日期等混入
                        candidates=[]
                        for sentence in re.split(r'[。；\n]',text):
                            if re.search(r'(收购|回收|求购|成交|价格|报价)',sentence) and price_values(sentence): candidates += price_values(sentence)
                        v=candidates[0] if candidates else vals[0]
                        records.append({'category':classify(title+' '+text[:1500]),'name':title[:100],'status':status,'price':f'{v:g}元','date':time.strftime('%Y-%m-%d'),'source':'一尘网','source_url':topic_url,'board':board_title[:80]})
                    except Exception: pass
                    time.sleep(.25)
            except Exception: break
    return records,sources

def parse_yy11(base):
    records=[]; sources=[]; seen=set(); topics=[]
    try:
        s=BeautifulSoup(fetch(base).text,'html.parser'); sources.append({'name':'钱币天堂','url':base,'status':'reachable'})
        for a in s.find_all('a',href=True):
            h=a['href']; title=clean(a.get_text(' ',strip=True))
            if '/c2c/topic/' in h and title: topics.append((urljoin(base,h),title))
    except Exception as e:
        sources.append({'name':'钱币天堂','url':base,'status':'unreachable','error':type(e).__name__}); return records,sources
    for topic_url,title in topics[:120]:
        k=topic_url.split('?')[0]
        if k in seen: continue
        seen.add(k)
        try:
            s=BeautifulSoup(fetch(topic_url).text,'html.parser'); text=clean(s.get_text(' ',strip=True))
            if '已流拍' in text or '流标' in text: continue
            # 钱币天堂明确的“物品成交价”优先
            m=re.search(r'物品成交价[^0-9]{0,40}(?:¥|￥)?\s*([0-9][0-9,]*(?:\.[0-9]+)?)\s*元?',text)
            if not m or '成交于' not in text: continue
            v=float(m.group(1).replace(',',''))
            records.append({'category':classify(title+' '+text[:1200]),'name':title[:100],'status':'成交','price':f'{v:g}元','date':time.strftime('%Y-%m-%d'),'source':'钱币天堂','source_url':topic_url})
        except Exception: pass
        time.sleep(.35)
    return records,sources

def fujian_sources():
    return [
      ('中国国家博物馆','https://www.chnmuseum.cn/zp/zpml/hb/202106/t20210610_250327.shtml'),
      ('国家文化记忆库·国立历史博物馆','https://tcmb.culture.tw/zh-tw/detail?id=14000113139&indexCode=MOCCOLLECTIONS'),
      ('国家文化记忆库·国立历史博物馆','https://tcmb.culture.tw/zh-tw/detail?id=14000128171&indexCode=MOCCOLLECTIONS'),
      ('国家文化记忆库·国立历史博物馆','https://tcmb.culture.tw/zh-tw/detail?id=14000113490&indexCode=MOCCOLLECTIONS'),
      ('国家文化记忆库·国立历史博物馆','https://tcmb.culture.tw/zh-tw/detail?id=14000128030&indexCode=MOCCOLLECTIONS'),
      ('国家文化记忆库·国立历史博物馆','https://tcmb.culture.tw/zh-tw/detail?id=14000128036&indexCode=MOCCOLLECTIONS')]

def parse_fujian():
    records=[]
    for source,url in fujian_sources():
        try:
            s=BeautifulSoup(fetch(url).text,'html.parser'); text=clean(s.get_text(' ',strip=True)); title=clean(s.title.get_text()) if s.title else '福建钱币资料'
            og=s.find('meta',attrs={'property':'og:image'}); img=urljoin(url,og.get('content')) if og and og.get('content') else ''
            records.append({'name':title[:120],'category':'福建钱币资料','features':text[:900],'source':source,'source_url':url,'source_image_url':img,'image_note':'图片展示与保存须以来源页授权条款为准；授权不明确时仅提供来源页。','updated':time.strftime('%Y-%m-%d')})
        except Exception as e:
            records.append({'name':'来源暂时无法访问','category':'福建钱币资料','source':source,'source_url':url,'image_note':'来源页暂时无法访问','error':type(e).__name__})
        time.sleep(.7)
    return records

def main():
    market=[]; sources=[]
    # 一尘网多入口容灾
    for base in PM001:
        m,s=parse_pm001(base); market += m; sources += s
        if m: break
    # 钱币天堂
    for base in YY11:
        m,s=parse_yy11(base); market += m; sources += s
        if m: break
    # 去重
    uniq={}
    for r in market: uniq[(r['source'],r['source_url'],r['status'],r['price'])]=r
    market=list(uniq.values())
    market.sort(key=lambda x:(x['category'],x['name']))
    fujian=parse_fujian()
    Path('data/market.json').write_text(json.dumps({'updated_at':time.strftime('%Y-%m-%d %H:%M:%S'),'status':'ok' if market else 'waiting_for_verified_sources','records':market,'sources':sources,'notice':'本站只整理公开可核验信息；没有真实记录时不编造价格。'},ensure_ascii=False,indent=2),encoding='utf-8')
    Path('data/fujian.json').write_text(json.dumps({'updated_at':time.strftime('%Y-%m-%d %H:%M:%S'),'title':'洪盛集藏·福建钱币资料库','notice':'只做资料收集、实物图片资料、历史整理、版别分析与学习研究，不采集成交价或求购价。','records':fujian},ensure_ascii=False,indent=2),encoding='utf-8')
    print('market=',len(market),'fujian=',len(fujian))
if __name__=='__main__': main()
