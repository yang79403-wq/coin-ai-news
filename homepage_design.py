from pathlib import Path

path = Path("index.html")
html = path.read_text(encoding="utf-8")

start = '<!-- BZT-HOME-FREE-START -->'
end = '<!-- BZT-HOME-FREE-END -->'
if start in html and end in html:
    a = html.index(start)
    b = html.index(end) + len(end)
    html = html[:a] + html[b:]

css = '''
<style id="bzt-home-design">
.bzt-topbar{max-width:980px;margin:0 auto;padding:14px 16px 0}
.bzt-free{display:grid;grid-template-columns:1.25fr .75fr;gap:14px;margin-bottom:18px}
.bzt-free-main,.bzt-free-side{border-radius:18px;box-shadow:0 6px 22px rgba(80,20,10,.12);overflow:hidden}
.bzt-free-main{background:linear-gradient(135deg,#650000,#920909 62%,#b8860b);color:#fff;padding:24px}
.bzt-free-main h2{margin:0 0 8px;font-size:25px;color:#fff}.bzt-free-main p{margin:7px 0;line-height:1.75}
.bzt-badge{display:inline-block;background:#fff;color:#720000;border-radius:999px;padding:5px 10px;font-weight:800;font-size:12px;margin-bottom:8px}
.bzt-actions{display:flex;gap:9px;flex-wrap:wrap;margin-top:14px}.bzt-btn{display:inline-block;text-decoration:none;border-radius:999px;padding:10px 16px;font-weight:800;font-size:14px}
.bzt-btn-white{background:#fff;color:#650000}.bzt-btn-gold{border:1px solid rgba(255,255,255,.65);color:#fff;background:rgba(255,255,255,.08)}
.bzt-free-side{background:#fff;padding:22px}.bzt-free-side h3{margin:0 0 10px;color:#650000;font-size:20px}.bzt-free-side p{margin:7px 0;color:#666;line-height:1.7}.bzt-list{margin:10px 0 0;padding:0;list-style:none;display:grid;grid-template-columns:1fr 1fr;gap:7px}.bzt-list li{background:#faf5e8;border-radius:9px;padding:8px;font-size:13px;color:#5b4a42}.bzt-info-nav{display:flex;gap:8px;overflow:auto;margin:0 0 18px}.bzt-info-nav a{white-space:nowrap;text-decoration:none;color:#650000;background:#fff;border:1px solid #eadfce;border-radius:999px;padding:8px 13px;font-size:13px;font-weight:700}
.bzt-mini{max-width:980px;margin:0 auto;padding:0 16px}.bzt-mini-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:18px}.bzt-mini-card{background:#fff;border-radius:13px;padding:13px;text-align:center;box-shadow:0 3px 13px rgba(80,50,20,.06)}.bzt-mini-card b{display:block;color:#650000;font-size:16px;margin-bottom:4px}.bzt-mini-card span{font-size:12px;color:#777}
@media(max-width:700px){.bzt-free{grid-template-columns:1fr}.bzt-free-main{padding:20px}.bzt-free-main h2{font-size:22px}.bzt-mini-grid{grid-template-columns:1fr 1fr}.bzt-list{grid-template-columns:1fr 1fr}}
</style>
'''

block = '''
<!-- BZT-HOME-FREE-START -->
<div class="bzt-topbar">
  <section class="bzt-free">
    <div class="bzt-free-main">
      <span class="bzt-badge">⭐ 平台核心服务</span>
      <h2>🔎 免费鉴定 · 免费评估 · 免费咨询</h2>
      <p><strong>钱币照片 / 视频在线提交</strong>，获取初步鉴定与行情分析。</p>
      <p>古钱｜银元｜金币｜纸币｜纪念币｜机制币｜评级币</p>
      <p>⏰ 24小时响应　🔐 隐私保密　💰 无交易不收费</p>
      <div class="bzt-actions">
        <a class="bzt-btn bzt-btn-white" href="ai_appraisal.html">📷 免费在线鉴定</a>
        <a class="bzt-btn bzt-btn-gold" href="tel:13799875350">📞 13799875350</a>
      </div>
    </div>
    <div class="bzt-free-side">
      <h3>📰 今日钱币资讯</h3>
      <p><strong>资讯是平台核心内容</strong></p>
      <p>每日自动更新收藏热点、行情、拍卖、古钱币、银元、纸币和纪念币资讯。</p>
      <ul class="bzt-list">
        <li>🔥 收藏热点</li><li>📈 市场行情</li><li>🔨 拍卖成交</li><li>📚 钱币知识</li>
      </ul>
    </div>
  </section>
  <nav class="bzt-info-nav">
    <a href="#news-list">📰 最新资讯</a><a href="#services">🔎 免费鉴定</a><a href="ai_appraisal.html">🤖 AI初步分析</a><a href="#market">📈 行情分析</a><a href="#knowledge">📚 收藏知识</a>
  </nav>
</div>
<div class="bzt-mini">
  <div class="bzt-mini-grid">
    <div class="bzt-mini-card"><b>免费鉴定</b><span>照片 / 视频咨询</span></div>
    <div class="bzt-mini-card"><b>免费评估</b><span>收藏价值初步判断</span></div>
    <div class="bzt-mini-card"><b>免费咨询</b><span>24小时响应</span></div>
    <div class="bzt-mini-card"><b>全国服务</b><span>主要城市可预约</span></div>
  </div>
</div>
<!-- BZT-HOME-FREE-END -->
'''

if '</head>' in html and 'id="bzt-home-design"' not in html:
    html = html.replace('</head>', css + '</head>', 1)

if '<div class="bzt-topbar">' not in html:
    html = html.replace('<section class="container">', block + '\n<section class="container">', 1)

html = html.replace('<h2 class="section-title">📈 钱币行情 · 市场分析</h2>', '<h2 id="market" class="section-title">📈 钱币行情 · 市场分析</h2>')
html = html.replace('<h2 class="section-title">📚 钱币知识</h2>', '<h2 id="knowledge" class="section-title">📚 钱币知识</h2>')

path.write_text(html, encoding='utf-8')
print('首页免费服务与资讯视觉入口已完成')
