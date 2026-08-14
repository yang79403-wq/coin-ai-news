import json, re
from pathlib import Path
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

p=Path('market-data.json')
data=json.loads(p.read_text(encoding='utf-8'))
verified=[]; rejected=[]
headers={'User-Agent':'Mozilla/5.0 (compatible; HongshengCollectionVerifier/1.0)'}
active=['拍卖中','竞拍中','竞价中','正在拍','待拍','尚未结拍','尚未结标','出价中','进行中']
strong=['成交价','成交价格','成交金额','已成交','成交','落槌价','落槌','中标价','中标','得标价','得标','拍得','结拍','结标','已结标','最终成交','竞价成功','竞买成功','已售','售出','已卖','交易成功','交易完成']
patterns=[r'(?:成交金额|成交价格|成交价|结标价|落槌价|中标价|得标价|最终成交|最终价|拍得|成交|落槌|中标|得标|已售|售出|已卖)\s*[:：=]?\s*[¥￥]?\s*([0-9][0-9,]*(?:\.\d+)?)',r'(?:结标|结标价|中标|得标|最终价|成交)\s*[：:]?\s*(?:RMB|￥|¥)?\s*([0-9][0-9,]*(?:\.\d+)?)']
s=requests.Session(); s.headers.update(headers)

def text(soup): return ' '.join(soup.get_text(' ',strip=True).split())
def price(t):
    t=t.replace(',','')
    for pat in patterns:
        for m in re.finditer(pat,t,re.I):
            v=float(m.group(1))
            if 0<v<100000000:return v
    return None
def image(soup,base):
    for m in soup.find_all('meta'):
        k=(m.get('property') or m.get('name') or '').lower()
        if k in ('og:image','twitter:image') and m.get('content'): return urljoin(base,m['content'])
    for img in soup.find_all('img'):
        src=img.get('src') or img.get('data-src') or img.get('data-original')
        if src:
            u=urljoin(base,src)
            if u.startswith(('http://','https://')) and not any(x in u.lower() for x in ('logo','icon','avatar','qrcode','advert')): return u
    return None
for row in data.get('rows',[]):
    u=row.get('item_url')
    if not u:
        rejected.append({'name':row.get('name'),'error':'missing_item_url'}); continue
    try:
        r=s.get(u,timeout=25,allow_redirects=True); r.raise_for_status(); sp=BeautifulSoup(r.text,'html.parser')
        t=text(sp)+' '+' '.join(x.get_text(' ',strip=True) for x in sp.find_all('script'))
        if any(a in t for a in active) and not any(x in t for x in strong): raise ValueError('still_active')
        if not any(x in t for x in strong): raise ValueError('no_confirmed_transaction')
        v=price(t); im=image(sp,r.url)
        if v is None: raise ValueError('price_missing')
        if im is None: raise ValueError('image_missing')
        row=dict(row); row['item_url']=r.url; row['image_url']=im; row['price']=v; row['transaction_confirmed']=True; row['verification']='原始商品/拍品页面二次核验'; row['verified_at']=datetime.now(timezone.utc).astimezone().isoformat(); verified.append(row)
    except Exception as e:
        rejected.append({'name':row.get('name'),'item_url':u,'error':str(e)[:160]})
data['rows']=verified
data['verification']={'policy':'原始商品/拍品页面确认成交状态、成交价格，并从同一页面取得实物图片后才入库。','verified_count':len(verified),'rejected_count':len(rejected),'rejected':rejected[:100],'verified_at':datetime.now(timezone.utc).astimezone().isoformat()}
data['updated_at']=datetime.now(timezone.utc).astimezone().isoformat()
p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('verified=',len(verified),'rejected=',len(rejected))
for x in data.get('status',[]): print(x.get('source_name'), 'OK' if x.get('ok') else 'FAILED', 'rows=',x.get('rows'), 'pages=',x.get('pages'), 'errors=',x.get('errors'))
