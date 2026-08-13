from pathlib import Path
import requests

OUT = Path('assets/coins')
OUT.mkdir(parents=True, exist_ok=True)

IMAGES = {
    'rmb1-200yuan.jpg': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Renminbi1ban_200yuan.jpg',
    'yuan-3-reverse.jpg': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Yuan_Shikai_Dollar_Year_3_Reverse.jpg',
    'kangxi-tongbao.jpg': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Kangxi_Tongbao._Baoquan_01.png',
    'qianlong-tongbao.jpg': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Coin._Qing_Dynasty._Qianlong_Tongbao._Bao_Quan._obv.jpg',
    'central-mint-1930.jpg': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Completion_of_the_Central_MInt_-_obverse.jpg',
    'panda-silver.jpg': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Chinese_panda_silver_coins_(52282119440).jpg',
}

headers = {'User-Agent': 'CoinAI-News/1.0'}
for filename, url in IMAGES.items():
    target = OUT / filename
    try:
        r = requests.get(url, headers=headers, timeout=45, allow_redirects=True)
        r.raise_for_status()
        if len(r.content) < 1000:
            raise RuntimeError(f'too small: {len(r.content)} bytes')
        target.write_bytes(r.content)
        print(f'OK {filename}: {len(r.content)} bytes')
    except Exception as e:
        print(f'WARN {filename}: {e}')
print('real gallery image mirror finished')
