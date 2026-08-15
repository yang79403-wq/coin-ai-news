#!/usr/bin/env python3
"""洪盛集藏唯一主采集器
仅处理公开可访问页面；无法核验的数据直接跳过，不编造价格。
"""
import json,re,time
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

OUT=Path('data/price-tables.json')
UA='HongshengCollectionResearchBot/1.0'
SOURCES=[
 ('一尘网','http://www.pm001.net/'),
 ('钱币天堂','https://www.yy11.com/c2c/forum/4.html#1'),
]

def fetch(url):
    try:
        r=requests.get(url,headers={'User-Agent':UA},timeout=20)
        if r.ok and r.text: return r.text
    except Exception: pass
    return ''

def parse(source,url,html):
    soup=BeautifulSoup(html,'html.parser')
    text=re.sub(r'\s+',' ',soup.get_text(' ',strip=True))
    rows=[]
    # 只抓明确包含成交/求购及价格的短文本，避免把普通参考价当成交价
    patterns=[
      r'(.{0,80})(成交价|成交价格|成交)(.{0,80})(?:￥|¥|人民币)?\s*([0-9][0-9,.]*(?:\.[0-9]+)?)\s*元',
      r'(.{0,80})(求购价|求购)(.{0,80})(?:￥|¥|人民币)?\s*([0-9][0-9,.]*(?:\.[0-9]+)?)\s*元'
    ]
    for pat in patterns:
        for m in re.finditer(pat,text,re.I):
            context=re.sub(r'\s+',' ',m.group(0)).strip()
            price=m.group(4)
            kind='成交' if '成交' in m.group(2) else '求购'
            rows.append({'name':context[:80],'variant':'','condition':'','deal_price':price+'元' if kind=='成交' else '','buy_price':price+'元' if kind=='求购' else '','date':time.strftime('%Y-%m-%d'),'source':source,'source_url':url,'status':kind})
    return rows

def main():
    all_rows=[]
    sources_ok=[]
    for source,url in SOURCES:
        html=fetch(url)
        if html:
            sources_ok.append(source)
            all_rows.extend(parse(source,url,html))
        time.sleep(1)
    # 去重
    seen=set(); clean=[]
    for x in all_rows:
        k=(x['name'],x['deal_price'],x['buy_price'],x['source_url'])
        if k not in seen: seen.add(k); clean.append(x)
    by={}
    for x in clean:
        key='其他行情'
        s=x['name']
        if any(k in s for k in ['银元','袁大头','船洋','龙洋','鹰洋','大清']): key='银元'
        elif any(k in s for k in ['纸币','人民币','纪念钞']): key='纸币/纪念钞'
        elif any(k in s for k in ['铜元','铜币']): key='铜元'
        elif any(k in s for k in ['古钱','通宝','元宝']): key='古钱币'
        by.setdefault(key,[]).append(x)
    tables=[{'category':k,'title':k+'｜今日成交/求购','rows':v} for k,v in by.items()]
    OUT.write_text(json.dumps({'updated_at':time.strftime('%Y-%m-%d %H:%M:%S'),'status':'ok' if sources_ok else 'sources_unavailable','sources_checked':sources_ok,'tables':tables,'notice':'仅显示可从公开来源核验的成交/求购记录；没有真实数据时不编造价格。'},ensure_ascii=False,indent=2),encoding='utf-8')
    print('sources_ok=',sources_ok,'rows=',len(clean))

if __name__=='__main__': main()
