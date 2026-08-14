#!/usr/bin/env python3
"""洪盛集藏：福建钱币公益资料采集器
仅采集公开资料；图片仅在来源页明确标注开放授权时镜像到本站。
"""
from __future__ import annotations
import json, re, time, hashlib
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data/fujian-coins.json"
IMG_DIR = ROOT / "assets/fujian"
IMG_DIR.mkdir(parents=True, exist_ok=True)
UA = "HongshengCollectionResearchBot/1.0 (+https://yang79403-wq.github.io/coin-ai-news/)"

SEEDS = [
 {"name":"福建官局造光绪元宝当十铜元","category":"福建铜元","period":"1900-1905","source":"中国国家博物馆","url":"https://www.chnmuseum.cn/zp/zpml/hb/202106/t20210610_250327.shtml","license":"来源页资料；图片使用前核验授权"},
 {"name":"福建官局造光绪元宝十文","category":"福建铜元","period":"1901-1905","source":"国家文化记忆库·国立历史博物馆","url":"https://tcmb.culture.tw/zh-tw/detail?id=14000113139&indexCode=MOCCOLLECTIONS","license":"CC BY 3.0 TW，保留署名与来源"},
 {"name":"福建官局造光绪元宝库平三分六厘","category":"福建银元","period":"1900-1908","source":"国家文化记忆库·国立历史博物馆","url":"https://tcmb.culture.tw/zh-tw/detail?id=14000128171&indexCode=MOCCOLLECTIONS","license":"CC BY 3.0 TW，保留署名与来源"},
 {"name":"福建官局造光绪元宝库平七分二厘","category":"福建银元","period":"1900-1908","source":"国家文化记忆库·国立历史博物馆","url":"https://tcmb.culture.tw/zh-tw/detail?id=14000128030&indexCode=MOCCOLLECTIONS","license":"CC BY 3.0 TW，保留署名与来源"},
 {"name":"福建官局造光绪元宝库平一钱四分四厘","category":"福建银元","period":"1900-1908","source":"国家文化记忆库·国立历史博物馆","url":"https://tcmb.culture.tw/zh-tw/detail?id=14000113490&indexCode=MOCCOLLECTIONS","license":"CC BY 3.0 TW，保留署名与来源"},
 {"name":"福建省造光绪元宝库平七分二厘","category":"福建银元","period":"1890-1908","source":"国家文化记忆库·国立历史博物馆","url":"https://tcmb.culture.tw/zh-tw/detail?id=14000128036&indexCode=MOCCOLLECTIONS","license":"CC BY 3.0 TW，保留署名与来源"},
 {"name":"福建闽海关纹龙铜元","category":"福建铜元","period":"1900-1905","source":"国家文化记忆库","url":"https://tcmb.culture.tw/zh-tw/detail?id=142000000075&indexCode=MOCCOLLECTIONS","license":"以来源页授权标示为准；未确认时只保留来源"},
]

def get(url):
    r=requests.get(url,headers={"User-Agent":UA},timeout=25)
    r.raise_for_status(); return r

def clean(s):
    return re.sub(r"\s+"," ",s or "").strip()

def parse(seed):
    out=dict(seed)
    try:
        html=get(seed["url"]).text
        soup=BeautifulSoup(html,"html.parser")
        text=clean(soup.get_text(" ",strip=True))
        # 尽量提取页面中的结构化描述
        for key,pat in [("diameter",r"直径(?:约)?\s*([0-9.]+\s*厘米)"),("weight",r"重(?:量)?(?:约)?\s*([0-9.]+\s*克)")]:
            m=re.search(pat,text,re.I)
            if m: out[key]=m.group(1)
        title=soup.find("title")
        out["page_title"]=clean(title.get_text()) if title else seed["name"]
        desc=soup.find("meta",attrs={"name":"description"}) or soup.find("meta",attrs={"property":"og:description"})
        if desc and desc.get("content"): out["features"]=clean(desc["content"])
        if "features" not in out:
            # 截取标题附近正文作为研究摘要，避免把整页复制进数据库
            idx=text.find(seed["name"].replace("｜",""))
            out["features"]=text[idx:idx+650] if idx>=0 else text[:650]
        # 图片只在明确 CC BY / 开放授权来源时下载
        og=soup.find("meta",attrs={"property":"og:image"})
        img=urljoin(seed["url"],og.get("content")) if og and og.get("content") else None
        out["source_image_url"]=img or ""
        cc = "CC BY" in text or "创用CC" in text or "授權標示" in text and "CC BY" in text
        out["image_license"]=seed.get("license","")
        if img and cc:
            try:
                rr=requests.get(img,headers={"User-Agent":UA},timeout=25)
                rr.raise_for_status()
                ext=".jpg"
                ct=rr.headers.get("content-type","").lower()
                if "png" in ct: ext=".png"
                elif "webp" in ct: ext=".webp"
                fn=hashlib.sha1(seed["url"].encode()).hexdigest()[:16]+ext
                path=IMG_DIR/fn; path.write_bytes(rr.content)
                out["image_local"]=f"assets/fujian/{fn}"
                out["image_status"]="mirrored-authorized"
            except Exception as e:
                out["image_status"]=f"source-only: {type(e).__name__}"
        else:
            out["image_status"]="source-only"
    except Exception as e:
        out["image_status"]=f"fetch-error: {type(e).__name__}"
    out["source_url"]=seed["url"]
    return out

def main():
    data=json.loads(DATA.read_text(encoding="utf-8")) if DATA.exists() else {}
    existing={x.get("source_url"):x for x in data.get("records",[])}
    for seed in SEEDS:
        rec=parse(seed); old=existing.get(seed["url"],{})
        old.update(rec); existing[seed["url"]]=old
        time.sleep(1.2)
    records=list(existing.values())
    data.update({"updated":time.strftime("%Y-%m-%d"),"title":"洪盛集藏·福建钱币资料库","notice":"仅供公益学习、收藏研究与交流；价格行情不属于本专题。图片优先使用明确开放授权馆藏或自有/获授权图片。","categories":["福建铜元","福建银元","福建纸币","福建地方货币","福建铸币历史"],"records":records})
    DATA.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"福建资料更新完成：{len(records)} 条")

if __name__=="__main__": main()
