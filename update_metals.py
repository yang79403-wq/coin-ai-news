import json, urllib.request, urllib.parse, datetime

symbols = {"gold":"GC=F", "silver":"SI=F"}
out = {"updated_at": datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC'), "source_type":"自动行情接口参考"}
for key, symbol in symbols.items():
    url = 'https://query1.finance.yahoo.com/v8/finance/chart/' + urllib.parse.quote(symbol, safe='') + '?range=1d&interval=1m'
    try:
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
        data = json.load(urllib.request.urlopen(req, timeout=20))
        result = data['chart']['result'][0]
        meta = result['meta']
        price = meta.get('regularMarketPrice') or meta.get('previousClose')
        out[key] = {'symbol': symbol, 'price': float(price), 'label':'自动更新国际现货/期货参考'}
    except Exception:
        out[key] = {'symbol': symbol, 'price': None, 'label':'暂不可用'}
with open('metals.json','w',encoding='utf-8') as f:
    json.dump(out,f,ensure_ascii=False,indent=2)
print(json.dumps(out,ensure_ascii=False))
