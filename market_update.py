from datetime import datetime
import json
from pathlib import Path
import requests

path = Path('market-data.json')
data = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {"records": []}

# 只访问公开网页，不绕过登录、验证码或反爬机制。
checks = [
    ('一尘网公开行情入口', 'http://www.pm001.net/index.asp?boardid=148'),
    ('闲鱼公开搜索入口', 'https://www.goofish.com/'),
]
access = []
for name, url in checks:
    try:
        r = requests.get(url, timeout=12, headers={'User-Agent':'Mozilla/5.0 (compatible; CoinAI-News/1.0)'})
        access.append({'name': name, 'url': url, 'status_code': r.status_code, 'accessible': r.ok})
    except Exception as exc:
        access.append({'name': name, 'url': url, 'accessible': False, 'error': str(exc)[:160]})

data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
data['access_check'] = access
data['notice'] = '仅采集公开网页；一尘/闲鱼若要求登录、动态渲染或触发反爬，则不强行绕过。未直接核验的成交价标记为公开报道参考。'
path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
print('行情数据更新时间：', data['updated_at'])
for item in access:
    print(item)
