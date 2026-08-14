from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

marker = '<!-- HONGSHENG_FUJIAN_SECTION_V1 -->'
if marker not in s:
    section = r'''<!-- HONGSHENG_FUJIAN_SECTION_V1 -->
<section class="section hs-fujian-feature" id="fujian-coins">
  <div class="wrap">
    <div class="hs-fujian-head">
      <div>
        <div class="hs-fujian-kicker">HONGSHENG JICANG · FUJIAN NUMISMATICS</div>
        <h2 class="title">🇨🇳 福建钱币 · 洪盛集藏特色资料库</h2>
        <p class="desc">福建铜元 · 福建银元 · 福建纸币 · 福建铸币历史 · 中国网站资料图鉴 · 后续成交行情</p>
      </div>
      <a class="hs-fujian-more" href="./fujian.html">进入福建钱币专题 →</a>
    </div>
    <div class="hs-fujian-grid">
      <a href="./fujian.html#copper" class="hs-fujian-card"><b>🪙 福建铜元</b><span>福建官局造、闽海关铜元及清末地方机制铜币</span></a>
      <a href="./fujian.html#silver" class="hs-fujian-card"><b>🥈 福建银元</b><span>福建官局造光绪元宝及福建地方银币资料</span></a>
      <a href="./fujian.html#paper" class="hs-fujian-card"><b>💴 福建纸币</b><span>福建官银钱局、福建银行、福建省银行等</span></a>
      <a href="./fujian.html#sources" class="hs-fujian-card"><b>🖼 中国网站资料图鉴</b><span>优先使用中国大陆博物馆、地方史志及国内钱币资料网站的公开图片与资料</span></a>
    </div>
    <div class="hs-fujian-note">资料图片采用“授权优先”原则：明确开放授权、自有或取得授权的图片才进入网站图鉴；其他中国网站图片仅建立原始页面索引，不直接复制发布。</div>
  </div>
</section>
<style id="hongsheng-fujian-feature-css">
.hs-fujian-feature{padding-top:18px}.hs-fujian-feature .wrap{background:linear-gradient(135deg,#fff9e9,#fffdf8);border:1px solid #c59a43;border-radius:22px;padding:22px;box-shadow:0 12px 34px rgba(75,30,0,.08)}.hs-fujian-head{display:flex;align-items:center;justify-content:space-between;gap:18px}.hs-fujian-kicker{font-size:10px;letter-spacing:3px;color:#9a742d}.hs-fujian-more{white-space:nowrap;background:#700806;color:#ffe8a2;text-decoration:none;padding:11px 15px;border-radius:999px;font-weight:900;font-size:12px}.hs-fujian-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:16px}.hs-fujian-card{display:block;text-decoration:none;background:#fff;border:1px solid #ead9b9;border-radius:15px;padding:15px;transition:.2s}.hs-fujian-card:hover{transform:translateY(-3px);box-shadow:0 8px 22px rgba(70,30,0,.1)}.hs-fujian-card b{display:block;color:#700806;font-size:17px;margin-bottom:6px}.hs-fujian-card span{display:block;color:#75695f;font-size:11px;line-height:1.7}.hs-fujian-note{margin-top:12px;background:#fff5d5;border-left:4px solid #c59a43;padding:10px 12px;border-radius:9px;color:#6d5b3d;font-size:11px;line-height:1.7}@media(max-width:760px){.hs-fujian-grid{grid-template-columns:1fr 1fr}.hs-fujian-head{align-items:flex-start;flex-direction:column}.hs-fujian-more{align-self:stretch;text-align:center}}@media(max-width:460px){.hs-fujian-grid{grid-template-columns:1fr}}
</style>
'''
    s = s.replace('</body>', section + '</body>', 1)
else:
    s = s.replace('福建铜元 · 福建银元 · 福建纸币 · 福建铸币历史 · 授权馆藏图鉴 · 后续成交行情', '福建铜元 · 福建银元 · 福建纸币 · 福建铸币历史 · 中国网站资料图鉴 · 后续成交行情')
    s = s.replace('<b>🖼 授权图鉴</b><span>优先收录 CC BY、自有或明确授权的正背面实物图片</span>', '<b>🖼 中国网站资料图鉴</b><span>优先使用中国大陆博物馆、地方史志及国内钱币资料网站的公开图片与资料</span>')
    s = s.replace('图片采用“授权优先”原则：公共机构开放授权、自有图片或获得授权的图片进入图鉴；其他来源仅保留原始页面与研究索引。', '资料图片采用“授权优先”原则：明确开放授权、自有或取得授权的图片才进入网站图鉴；其他中国网站图片仅建立原始页面索引，不直接复制发布。')

source_marker = '<!-- HONGSHENG_FUJIAN_CHINA_SOURCES_V1 -->'
if source_marker not in s:
    source_section = r'''<!-- HONGSHENG_FUJIAN_CHINA_SOURCES_V1 -->
<section class="section hs-fujian-cn-sources" id="fujian-china-sources">
  <div class="wrap">
    <h2 class="title">🖼 福建钱币 · 中国网站资料与图片索引</h2>
    <p class="desc">自动整理中国大陆公开网站中的福建钱币资料。图片按授权规则处理：明确授权才复制进站，未明确授权的图片只保留原始链接。</p>
    <div class="hs-cn-source-grid">
      <a class="hs-cn-source" href="https://www.chnmuseum.cn/zp/zpml/hb/202106/t20210610_250327.shtml" target="_blank" rel="noopener"><b>中国国家博物馆</b><span>福建官局造光绪元宝当十铜元 · 馆藏图文资料</span></a>
      <a class="hs-cn-source" href="https://www.airmb.com/html/107636.html" target="_blank" rel="noopener"><b>爱藏网</b><span>福建省造光绪元宝银元版别与图片资料索引</span></a>
      <a class="hs-cn-source" href="https://www.ybkinfo.com/yinyuan/p243.html" target="_blank" rel="noopener"><b>元禾收藏</b><span>福建官局造光绪元宝银元资料与图片索引</span></a>
      <a class="hs-cn-source" href="https://www.shanghaimuseum.net/mu/frontend/pg/article/id/RI00004034" target="_blank" rel="noopener"><b>上海博物馆</b><span>中国历代货币馆 · 货币史与纸币、金属货币研究背景</span></a>
      <a class="hs-cn-source" href="https://data.fjdsfzw.org.cn/" target="_blank" rel="noopener"><b>福建省地方志</b><span>福建金融、铸币、地方史志资料持续检索入口</span></a>
      <a class="hs-cn-source" href="https://www.mxiqi.com/auction.item.info/5436614" target="_blank" rel="noopener"><b>麦稀奇</b><span>福建官局造光绪元宝十文钱币图片与成交研究索引</span></a>
    </div>
  </div>
</section>
<style id="hongsheng-fujian-cn-sources-css">
.hs-fujian-cn-sources{padding-top:8px}.hs-cn-source-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.hs-cn-source{display:block;text-decoration:none;background:#fffdf8;border:1px solid #dfcaa6;border-radius:16px;padding:16px;transition:.2s;box-shadow:0 7px 22px rgba(76,27,0,.05)}.hs-cn-source:hover{transform:translateY(-3px);box-shadow:0 10px 26px rgba(76,27,0,.11)}.hs-cn-source b{display:block;color:#700806;font-size:17px;margin-bottom:7px}.hs-cn-source span{display:block;color:#74685d;font-size:12px;line-height:1.7}@media(max-width:760px){.hs-cn-source-grid{grid-template-columns:1fr 1fr}}@media(max-width:460px){.hs-cn-source-grid{grid-template-columns:1fr}}
</style>
'''
    s = s.replace('</body>', source_section + '</body>', 1)

Path('data/fujian-china-sources.json').write_text('''[
  {"name":"中国国家博物馆","url":"https://www.chnmuseum.cn/zp/zpml/hb/202106/t20210610_250327.shtml","type":"馆藏资料与图片","rights":"按原站授权规则使用"},
  {"name":"爱藏网","url":"https://www.airmb.com/html/107636.html","type":"福建银元版别图片资料索引","rights":"仅保留原始链接，图片需确认授权后使用"},
  {"name":"元禾收藏","url":"https://www.ybkinfo.com/yinyuan/p243.html","type":"福建银元图片资料索引","rights":"仅保留原始链接，图片需确认授权后使用"},
  {"name":"上海博物馆","url":"https://www.shanghaimuseum.net/mu/frontend/pg/article/id/RI00004034","type":"中国货币史资料","rights":"按原站规则使用"},
  {"name":"福建省地方志","url":"https://data.fjdsfzw.org.cn/","type":"福建金融与铸币史志","rights":"按原站规则使用"},
  {"name":"麦稀奇","url":"https://www.mxiqi.com/auction.item.info/5436614","type":"福建铜元图片与成交研究索引","rights":"仅保留原始链接，图片需确认授权后使用"}
]''', encoding='utf-8')

p.write_text(s, encoding='utf-8')
print('已将福建钱币首页版块升级为中国网站资料与图片索引版')
