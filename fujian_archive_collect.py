#!/usr/bin/env python3
"""洪盛集藏：福建钱币公益资料采集器，仅允许中国大陆来源。"""
from __future__ import annotations
import json, time
from pathlib import Path
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data/fujian-coins.json'
IMG_DIR=ROOT/'assets/fujian'; IMG_DIR.mkdir(parents=True,exist_ok=True)
UA='HongshengCollectionResearchBot/1.1'
ALLOWED=( '.gov.cn','.edu.cn','.ac.cn','.org.cn','.cnmuseum.cn','.chnmuseum.cn','.fjdsfzw.org.cn','.fujian.gov.cn' )
SEEDS=[
('福建官局造光绪元宝当十铜元','福建铜元','1900-1905','中国国家博物馆','https://www.chnmuseum.cn/zp/zpml/hb/202106/t20210610_250327.shtml'),
('福建铸币历史','福建铸币历史','清末民国','福建省地方志编纂委员会','https://data.fjdsfzw.org.cn/upload/Annals/2011/%E9%87%91%E8%9E%8D%E5%BF%97/epub/ops/14.htm'),
]

def mainland(url):
    h=urlparse(url).hostname or ''
    return h.endswith(ALLOWED)

def fetch(url):
    if not mainland(url): raise ValueError('非中国大陆来源')
    r=requests.get(url,headers={'User-Agent':UA},timeout=25); r.raise_for_status(); return r

def main():
    old=json.loads(DATA.read_text(encoding='utf-8')) if DATA.exists() else {}
    records=[]
    for name,cat,period,source,url in SEEDS:
        if not mainland(url): continue
        try:
            soup=BeautifulSoup(fetch(url).text,'html.parser')
            text=' '.join(soup.stripped_strings)
            records.append({'name':name,'category':cat,'period':period,'features':text[:900],'source':source,'source_url':url,'image_status':'source-only','image_policy':'仅使用中国大陆来源；图片必须有明确开放授权、自有或获授权后才本地保存。'})
            time.sleep(1)
        except Exception as e:
            print(name,type(e).__name__)
    old.update({'updated':time.strftime('%Y-%m-%d'),'title':'洪盛集藏·福建钱币资料库','notice':'仅收录中国大陆来源；本专题只做资料收集、实物图鉴、历史整理与研究，不采集成交价或求购价。','source_policy':'仅允许 .cn / .gov.cn / .edu.cn / .ac.cn / .org.cn 及明确列入的中国大陆文化机构域名。非中国大陆链接自动删除。','records':records})
    DATA.write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding='utf-8')
    print('mainland_records=',len(records))
if __name__=='__main__': main()
