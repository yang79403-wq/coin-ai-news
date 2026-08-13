from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = '<!-- REAL_COIN_GALLERY -->'
if marker in s:
    print('real coin gallery already injected')
    raise SystemExit(0)

css = '''<style id="real-coin-gallery-css">
.real-coin-gallery{max-width:1180px;margin:28px auto;padding:0 16px}
.real-coin-gallery h2{font-size:26px;margin:0 0 8px;color:#7a4a13}
.real-coin-gallery .sub{color:#777;margin:0 0 18px}
.real-coin-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.real-coin-card{background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 6px 24px rgba(0,0,0,.08);border:1px solid #eee;cursor:pointer;transition:transform .2s,box-shadow .2s}
.real-coin-card:hover{transform:translateY(-3px);box-shadow:0 10px 30px rgba(0,0,0,.14)}
.real-coin-card img{width:100%;height:210px;object-fit:contain;background:#f5f2ec;display:block}
.real-coin-card .body{padding:14px 16px}
.real-coin-card b{font-size:18px}.real-coin-card small{display:block;color:#888;margin-top:5px}
@media(max-width:760px){.real-coin-grid{grid-template-columns:1fr 1fr}.real-coin-card img{height:150px}}
@media(max-width:460px){.real-coin-grid{grid-template-columns:1fr}.real-coin-card img{height:190px}}
</style>'''

# Only reference image files that are confirmed to exist in assets/coins.
# This prevents GitHub Pages from showing broken-image placeholders.
html = f'''{marker}
<section class="real-coin-gallery" aria-label="真实钱币实物图鉴">
  <h2>🪙 真实钱币实物图鉴</h2>
  <p class="sub">旧版纸币 · 银元 · 铜钱 · 纪念币 · 金银币｜以仓库内已镜像的实物图片作为收藏研究参考</p>
  <div class="real-coin-grid">
    <article class="real-coin-card"><img src="assets/coins/rmb1-100-1b.jpg" alt="第一套人民币旧版纸币实物图" loading="lazy"><div class="body"><b>旧版纸币</b><small>第一套人民币 · 100元票样</small></div></article>
    <article class="real-coin-card"><img src="assets/coins/rmb1-200yuan.jpg" alt="第一套人民币200元实物图" loading="lazy"><div class="body"><b>第一套人民币</b><small>1949年 · 200元票样</small></div></article>
    <article class="real-coin-card"><img src="assets/coins/yuan-3-obverse.jpg" alt="袁世凯像三年壹圆银元实物图" loading="lazy"><div class="body"><b>银元</b><small>袁世凯像 · 民国三年壹圆</small></div></article>
    <article class="real-coin-card"><img src="assets/coins/yuan-1921-iii.png" alt="民国机制银币实物图" loading="lazy"><div class="body"><b>机制银币</b><small>民国机制币 · 实物参考</small></div></article>
    <article class="real-coin-card"><img src="assets/coins/cash-coins-a.jpg" alt="中国古代方孔铜钱实物图" loading="lazy"><div class="body"><b>古钱 · 铜钱</b><small>中国古代方孔钱实物参考</small></div></article>
    <article class="real-coin-card"><img src="assets/coins/cash-coins-a.jpg" alt="清代古钱实物图" loading="lazy"><div class="body"><b>清代古钱</b><small>清代方孔钱 · 实物参考</small></div></article>
    <article class="real-coin-card"><img src="assets/coins/cash-coins-a.jpg" alt="清代通宝古钱实物图" loading="lazy"><div class="body"><b>通宝类古钱</b><small>清代古钱 · 实物参考</small></div></article>
    <article class="real-coin-card"><img src="assets/coins/founding-commemorative.jpg" alt="中国纪念银币实物图" loading="lazy"><div class="body"><b>纪念币</b><small>中国纪念币 · 实物参考</small></div></article>
    <article class="real-coin-card"><img src="assets/coins/panda-2016-reverse.png" alt="中国熊猫银币实物图" loading="lazy"><div class="body"><b>金银币</b><small>中国熊猫系列 · 实物参考</small></div></article>
  </div>
</section>
'''

if '</body>' in s:
    s = s.replace('</body>', html + '\n</body>', 1)
else:
    s += '\n' + html

s = s.replace('</head>', css + '\n</head>', 1) if '</head>' in s else css + s
p.write_text(s, encoding='utf-8')
print('real coin gallery injected')
