from pathlib import Path
import re

p = Path('fujian.html')
s = p.read_text(encoding='utf-8')

section = r'''<section class="section" id="sources"><div class="wrap"><h2 class="title">中国网站资料与图片来源</h2><p class="desc">本专题优先从中国大陆博物馆、地方史志和国内钱币资料网站建立研究索引。图片严格执行授权优先规则。</p><div class="grid"><article class="card"><span class="badge">权威馆藏</span><h3>中国国家博物馆</h3><p>福建官局造光绪元宝当十铜元馆藏资料，记录面文、背龙、尺寸、重量和铸造年代。该馆页面提供馆藏图片。</p><a href="https://www.chnmuseum.cn/zp/zpml/hb/202106/t20210610_250327.shtml" target="_blank" rel="noopener">查看原始资料与图片 →</a></article><article class="card"><span class="badge">国内资料</span><h3>爱藏网</h3><p>用于福建省造光绪元宝银元版别、图片和研究资料索引。未明确授权的图片只保留原始页面，不直接复制到本站。</p><a href="https://www.airmb.com/html/107636.html" target="_blank" rel="noopener">查看原始资料 →</a></article><article class="card"><span class="badge">国内资料</span><h3>元禾收藏</h3><p>用于福建官局造光绪元宝银元图片、规格和版别资料索引。</p><a href="https://www.ybkinfo.com/yinyuan/p243.html" target="_blank" rel="noopener">查看原始资料 →</a></article><article class="card"><span class="badge">博物馆</span><h3>上海博物馆</h3><p>用于中国历代货币馆的货币史、纸币和机制币研究背景资料。</p><a href="https://www.shanghaimuseum.net/mu/frontend/pg/article/id/RI00004034" target="_blank" rel="noopener">查看货币馆资料 →</a></article><article class="card"><span class="badge">地方史志</span><h3>福建省地方志</h3><p>用于福建金融史、铸币史、地方银行及纸币资料的持续检索。</p><a href="https://data.fjdsfzw.org.cn/" target="_blank" rel="noopener">进入福建地方志资料库 →</a></article><article class="card"><span class="badge">国内图像索引</span><h3>麦稀奇</h3><p>用于福建官局造光绪元宝铜元图片与成交研究索引。图片是否可转载以原站授权为准。</p><a href="https://www.mxiqi.com/auction.item.info/5436614" target="_blank" rel="noopener">查看原始图片与记录 →</a></article></div><div class="note" style="margin-top:14px">图片规则：明确开放授权、自有图片或取得授权的图片才复制进入洪盛集藏图鉴；其他中国网站图片只作为外部原始资料链接。不会把网上图片冒充为洪盛集藏自有图片，也不会把第三方成交价当作本站鉴定或报价。</div></div></section>'''

s, n = re.subn(r'<section class="section" id="sources">.*?</section>', section, s, count=1, flags=re.S)
if n == 0:
    s = s.replace('</main>', section + '\n</main>', 1)

s = s.replace('国家文化记忆库', '中国网站资料索引')
s = s.replace('https://tcmb.culture.tw/', 'https://www.chnmuseum.cn/')
s = s.replace('https://collections.culture.tw/', 'https://www.chnmuseum.cn/')

p.write_text(s, encoding='utf-8')
print('福建专题资料来源已切换为中国大陆网站优先索引')
