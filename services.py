from pathlib import Path

path = Path("index.html")
html = path.read_text(encoding="utf-8")

css = '''
<style id="bzt-services-style">
.service-wrap{max-width:980px;margin:0 auto;padding:0 16px 10px}
.service-hero{background:linear-gradient(135deg,#4d0000,#8a0505 55%,#b8860b);color:#fff;border-radius:18px;padding:24px 22px;margin-bottom:18px;box-shadow:0 6px 22px rgba(80,0,0,.15)}
.service-hero h2{margin:0 0 10px;font-size:25px}.service-hero p{margin:7px 0;line-height:1.8}
.phone{display:inline-block;margin-top:10px;background:#fff;color:#7b0000;text-decoration:none;font-weight:800;padding:10px 18px;border-radius:999px;font-size:19px}
.service-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-bottom:16px}
.service-card{background:#fff;border-radius:16px;padding:18px 20px;box-shadow:0 3px 14px rgba(80,50,20,.06)}
.service-card h3{margin:0 0 10px;color:#7b0000;font-size:19px}.service-card p{line-height:1.75;color:#555;margin:7px 0}
.service-list{margin:0;padding-left:20px;line-height:2;color:#444}.service-list li::marker{color:#9b0000}
.price-card{background:#fff;border-radius:16px;padding:20px;box-shadow:0 3px 14px rgba(80,50,20,.06);overflow:auto}
.price-card h3{margin:0 0 14px;color:#7b0000;font-size:20px}.price-table{width:100%;min-width:650px;border-collapse:collapse}
.price-table th,.price-table td{border-bottom:1px solid #eee;padding:12px 10px;text-align:left;line-height:1.55}.price-table th{background:#faf5e8;color:#6f0000}
.free{color:#16803c;font-weight:800}.notice{font-size:12px;color:#888;line-height:1.7;margin:12px 0 0}
@media(max-width:700px){.service-grid{grid-template-columns:1fr}.service-hero h2{font-size:22px}.phone{font-size:17px}}
</style>
'''

services = '''
<div class="service-wrap" id="services">
  <section class="service-hero">
    <h2>🪙 免费鉴定 · 咨询 · 线上估价</h2>
    <p>📞 服务电话：<strong>13799875350</strong></p>
    <p>覆盖全国主要城市｜免费评估｜无交易不收费｜照片 / 视频在线咨询｜24小时响应</p>
  </section>

  <div class="service-grid">
    <div class="service-card">
      <h3>🔎 免费鉴定评估</h3>
      <ul class="service-list">
        <li>免费鉴定、咨询、线上估价</li>
        <li>提供照片 / 视频即可在线咨询</li>
        <li>免费评估，无交易不收费</li>
        <li>24小时响应</li>
      </ul>
    </div>
    <div class="service-card">
      <h3>🚗 上门服务</h3>
      <ul class="service-list">
        <li>覆盖全国主要城市</li>
        <li>同城当面交流</li>
        <li>安全保障，隐私全程保密</li>
        <li>提前联系预约服务</li>
      </ul>
    </div>
    <div class="service-card">
      <h3>💰 回收｜寄卖｜鉴定｜评估</h3>
      <ul class="service-list">
        <li>钱币回收、寄卖</li>
        <li>藏品鉴定、价值评估</li>
        <li>全方位收藏品应急变现服务</li>
        <li>贵金属、黄铂金实体店铺相关服务咨询</li>
      </ul>
    </div>
    <div class="service-card">
      <h3>🏆 评级与收藏服务</h3>
      <ul class="service-list">
        <li>PCGS｜NGC｜PMG评级咨询</li>
        <li>评级送评服务</li>
        <li>收藏交流</li>
        <li>实时行情资讯</li>
      </ul>
    </div>
  </div>

  <section class="service-card" style="margin-bottom:16px">
    <h3>🏮 我们长期专注</h3>
    <p><strong>老银元｜机制币｜铜钱古币</strong></p>
    <p><strong>老纸币｜纪念币｜评级币</strong></p>
    <p><strong>PCGS｜NGC｜PMG评级咨询</strong></p>
  </section>

  <section class="price-card">
    <h3>💰 币智通AI 服务价格表</h3>
    <table class="price-table">
      <thead><tr><th>服务项目</th><th>价格</th><th>服务说明</th></tr></thead>
      <tbody>
        <tr><td>免费鉴定</td><td class="free">免费</td><td>照片 / 视频在线提交，24小时响应</td></tr>
        <tr><td>收藏咨询</td><td class="free">免费</td><td>古钱、银币、金币、纪念币等收藏咨询</td></tr>
        <tr><td>线上估价 / 评估</td><td class="free">免费</td><td>根据品种、版别、品相等信息综合评估</td></tr>
        <tr><td>同城当面交流</td><td class="free">免费</td><td>提前电话预约，具体安排以实际沟通为准</td></tr>
        <tr><td>上门服务</td><td class="free">免费咨询</td><td>覆盖全国主要城市，需提前预约</td></tr>
        <tr><td>钱币回收</td><td>实时询价</td><td>根据真伪、版别、品相及市场行情核价</td></tr>
        <tr><td>钱币寄卖</td><td>具体议价</td><td>根据藏品情况确认寄卖方式及服务条件</td></tr>
        <tr><td>PCGS / NGC / PMG评级咨询</td><td class="free">免费咨询</td><td>评级机构实际费用、快递等费用另计</td></tr>
        <tr><td>评级送评服务</td><td>咨询后报价</td><td>根据评级机构、数量及实际服务内容确定</td></tr>
        <tr><td>贵金属 / 黄铂金回收</td><td>实时询价</td><td>按当日行情、成色、重量等实际情况核价</td></tr>
      </tbody>
    </table>
    <p class="notice">※ “免费”仅指对应咨询、鉴定或评估服务本身不收取费用。实际回收、寄卖、评级、快递等产生的费用或成交价格，以双方最终确认内容为准。藏品价值会因真伪、版别、品相、评级及市场行情变化而变化。</p>
  </section>
</div>
'''

# 每次自动生成资讯后重新注入，避免每日更新时服务内容消失
if 'id="bzt-services-style"' not in html:
    html = html.replace('</head>', css + '\n</head>', 1)

if 'id="services"' in html:
    a = html.find('<div class="service-wrap" id="services">')
    b = html.find('</div>\n', a)
    # 不依赖嵌套 div 的结束位置，使用固定服务标记替换更安全
    start_marker = '<div class="service-wrap" id="services">'
    end_marker = '</div>\n\n<main class="container">'
    if start_marker in html and end_marker in html:
        start = html.index(start_marker)
        end = html.index(end_marker, start)
        html = html[:start] + services.rstrip() + '\n\n' + html[end + len('</div>\n\n'):]
else:
    html = html.replace('<main class="container">', services + '\n<main class="container">', 1)

path.write_text(html, encoding='utf-8')
print('服务内容与价格表已更新')
