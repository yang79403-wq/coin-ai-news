from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

marker = '<!-- HONGSHENG_FUJIAN_SECTION_V1 -->'
if marker in s:
    print('福建钱币专题已存在，无需重复注入')
    raise SystemExit(0)

section = r'''<!-- HONGSHENG_FUJIAN_SECTION_V1 -->
<section class="section hs-fujian-feature" id="fujian-coins">
  <div class="wrap">
    <div class="hs-fujian-head">
      <div>
        <div class="hs-fujian-kicker">HONGSHENG JICANG · FUJIAN NUMISMATICS</div>
        <h2 class="title">🇨🇳 福建钱币 · 洪盛集藏特色资料库</h2>
        <p class="desc">福建铜元 · 福建银元 · 福建纸币 · 福建铸币历史 · 授权馆藏图鉴 · 后续成交行情</p>
      </div>
      <a class="hs-fujian-more" href="./fujian.html">进入福建钱币专题 →</a>
    </div>
    <div class="hs-fujian-grid">
      <a href="./fujian.html#copper" class="hs-fujian-card"><b>🪙 福建铜元</b><span>福建官局造、闽海关铜元及清末地方机制铜币</span></a>
      <a href="./fujian.html#silver" class="hs-fujian-card"><b>🥈 福建银元</b><span>福建官局造光绪元宝及福建地方银币资料</span></a>
      <a href="./fujian.html#paper" class="hs-fujian-card"><b>💴 福建纸币</b><span>福建官银钱局、福建银行、福建省银行等</span></a>
      <a href="./fujian.html#sources" class="hs-fujian-card"><b>🖼 授权图鉴</b><span>优先收录 CC BY、自有或明确授权的正背面实物图片</span></a>
    </div>
    <div class="hs-fujian-note">图片采用“授权优先”原则：公共机构开放授权、自有图片或获得授权的图片进入图鉴；其他来源仅保留原始页面与研究索引。</div>
  </div>
</section>
<style id="hongsheng-fujian-feature-css">
.hs-fujian-feature{padding-top:18px}.hs-fujian-feature .wrap{background:linear-gradient(135deg,#fff9e9,#fffdf8);border:1px solid #c59a43;border-radius:22px;padding:22px;box-shadow:0 12px 34px rgba(75,30,0,.08)}.hs-fujian-head{display:flex;align-items:center;justify-content:space-between;gap:18px}.hs-fujian-kicker{font-size:10px;letter-spacing:3px;color:#9a742d}.hs-fujian-more{white-space:nowrap;background:#700806;color:#ffe8a2;text-decoration:none;padding:11px 15px;border-radius:999px;font-weight:900;font-size:12px}.hs-fujian-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:16px}.hs-fujian-card{display:block;text-decoration:none;background:#fff;border:1px solid #ead9b9;border-radius:15px;padding:15px;transition:.2s}.hs-fujian-card:hover{transform:translateY(-3px);box-shadow:0 8px 22px rgba(70,30,0,.1)}.hs-fujian-card b{display:block;color:#700806;font-size:17px;margin-bottom:6px}.hs-fujian-card span{display:block;color:#75695f;font-size:11px;line-height:1.7}.hs-fujian-note{margin-top:12px;background:#fff5d5;border-left:4px solid #c59a43;padding:10px 12px;border-radius:9px;color:#6d5b3d;font-size:11px;line-height:1.7}@media(max-width:760px){.hs-fujian-grid{grid-template-columns:1fr 1fr}.hs-fujian-head{align-items:flex-start;flex-direction:column}.hs-fujian-more{align-self:stretch;text-align:center}}@media(max-width:460px){.hs-fujian-grid{grid-template-columns:1fr}}
</style>
'''

s = s.replace('</body>', section + '</body>', 1)
p.write_text(s, encoding='utf-8')
print('已将福建钱币特色版块注入首页')
