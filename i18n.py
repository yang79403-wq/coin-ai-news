from pathlib import Path

path = Path('index.html')
html = path.read_text(encoding='utf-8')

css = '''
<style id="bzt-i18n-style">
.bzt-topbar{max-width:980px;margin:0 auto;padding:10px 16px;display:flex;justify-content:flex-end;gap:8px}
.lang-btn{border:1px solid #ddd;background:#fff;border-radius:999px;padding:7px 13px;cursor:pointer;color:#650000;font-weight:700}.lang-btn.active{background:#650000;color:#fff;border-color:#650000}
.address-card{background:#fff;border-radius:16px;padding:20px;box-shadow:0 4px 18px rgba(80,50,20,.07);margin-bottom:16px}.address-card h3{margin:0 0 9px;color:#7b0000}.address-card p{margin:6px 0;line-height:1.7;color:#555}.map-link{color:#650000;font-weight:700;text-decoration:none}
body.en .zh{display:none!important} body:not(.en) .en{display:none!important}
</style>
'''
if 'bzt-i18n-style' not in html:
    html = html.replace('</head>', css + '</head>', 1)

bar = '''<div class="bzt-topbar"><button class="lang-btn active" id="zhBtn">中文</button><button class="lang-btn" id="enBtn">English</button></div>'''
if 'id="zhBtn"' not in html:
    html = html.replace('<header>', bar + '<header>', 1)

# Address block before service area
address = '''
<div class="address-card" id="contact-address">
  <h3><span class="zh">📍 联系地址</span><span class="en">📍 Contact Address</span></h3>
  <p class="zh"><strong>福建省泉州市后城旅游文化街179号</strong></p>
  <p class="en"><strong>179 Houcheng Tourism &amp; Cultural Street, Quanzhou, Fujian, China</strong></p>
  <p class="zh">📞 服务电话：13799875350｜全国主要城市服务｜隐私全程保密</p>
  <p class="en">📞 Service: 13799875350 | Major cities across China | Privacy protected</p>
  <a class="map-link" href="https://www.google.com/maps/search/?api=1&amp;query=" target="_blank" rel="noopener noreferrer"><span class="zh">查看地图</span><span class="en">View Map</span> →</a>
</div>
'''
if 'id="contact-address"' not in html:
    html = html.replace('<section class="service-wrap" id="services">', address + '<section class="service-wrap" id="services">', 1)

# Add bilingual toggle script before body close
script = '''
<script>
(function(){
 const zh=document.getElementById('zhBtn'), en=document.getElementById('enBtn');
 if(!zh||!en)return;
 function setLang(lang){document.body.classList.toggle('en',lang==='en');zh.classList.toggle('active',lang==='zh');en.classList.toggle('active',lang==='en');localStorage.setItem('bzt-lang',lang);}
 zh.onclick=function(){setLang('zh')}; en.onclick=function(){setLang('en')};
 setLang(localStorage.getItem('bzt-lang')||'zh');
})();
</script>
'''
if 'localStorage.setItem(\'bzt-lang\'' not in html:
    html = html.replace('</body>', script + '</body>', 1)

# Add English subtitle translations for the most important platform labels without changing the Chinese default.
repls = {
    '全球钱币资讯 · AI鉴定评估 · 收藏知识':'<span class="zh">全球钱币资讯 · AI鉴定评估 · 收藏知识</span><span class="en">Global Coin News · AI Appraisal · Collecting Knowledge</span>',
    '📚 钱币收藏资讯中心':'<span class="zh">📚 钱币收藏资讯中心</span><span class="en">📚 Coin Collecting News Center</span>',
    '🔥 今日钱币资讯':'<span class="zh">🔥 今日钱币资讯</span><span class="en">🔥 Today’s Coin News</span>',
    '📈 钱币行情 · 市场分析':'<span class="zh">📈 钱币行情 · 市场分析</span><span class="en">📈 Coin Market · Analysis</span>',
    '📚 钱币知识':'<span class="zh">📚 钱币知识</span><span class="en">📚 Coin Knowledge</span>',
    '🔎 免费鉴定 · 咨询 · 线上估价':'<span class="zh">🔎 免费鉴定 · 咨询 · 线上估价</span><span class="en">🔎 Free Appraisal · Consultation · Online Valuation</span>',
    '🏮 长期专注':'<span class="zh">🏮 长期专注</span><span class="en">🏮 Our Specialties</span>',
    '💰 币智通 AI 服务价格表':'<span class="zh">💰 币智通 AI 服务价格表</span><span class="en">💰 BIZHITONG AI Service Price List</span>',
}
for old,new in repls.items():
    if old in html and new not in html:
        html = html.replace(old,new,1)

# English-only service copy is appended as a compact reference section.
en_service='''
<div class="service-card en" style="margin-top:16px"><h3>🇬🇧 Services</h3><p><strong>Free appraisal · Consultation · Online valuation</strong></p><p>Ancient coins · Silver coins · Gold coins · Commemorative coins · Banknotes · Graded coins</p><p>PCGS · NGC · PMG grading consultation | Photo / video consultation | 24-hour response</p><p>Buyback · Consignment · Appraisal · Valuation · On-site service in major Chinese cities</p><p><strong>Service phone: 13799875350</strong></p></div>
'''
if 'style="margin-top:16px"><h3>🇬🇧 Services' not in html:
    html = html.replace('</section>\n<footer>', en_service + '</section>\n<footer>', 1)

path.write_text(html, encoding='utf-8')
print('中英文模式与福建泉州地址已加入')
