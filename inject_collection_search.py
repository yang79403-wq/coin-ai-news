from pathlib import Path

INDEX = Path('index.html')
MARKER = '<!-- HONGSHENG_COLLECTION_SEARCH -->'

CSS = r'''<style id="hongsheng-collection-search-css">
.hs-search{max-width:1180px;margin:0 auto;padding:0 16px}
.hs-search-box{background:linear-gradient(135deg,#fff8e8,#fffdf8);border:1px solid #c9a75c;border-radius:22px;padding:22px;box-shadow:0 12px 32px rgba(70,30,0,.08)}
.hs-search-head{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin-bottom:14px}
.hs-search-title{font-family:"STKaiti","KaiTi","Songti SC","Noto Serif SC",serif;font-size:28px;font-weight:900;color:#650600;margin:0}
.hs-search-sub{margin:5px 0 0;color:#75695f;font-size:13px;line-height:1.6}
.hs-search-icon{font-size:34px;filter:drop-shadow(0 3px 5px rgba(70,20,0,.12))}
.hs-search-form{display:flex;gap:9px;margin-top:12px}
.hs-search-input{flex:1;min-width:0;border:1px solid #d8c39b;background:#fff;border-radius:13px;padding:13px 15px;font-size:15px;outline:none;color:#34261d}
.hs-search-input:focus{border-color:#9d701d;box-shadow:0 0 0 3px rgba(185,138,53,.12)}
.hs-search-submit{border:0;border-radius:13px;padding:0 20px;background:linear-gradient(135deg,#7d0b0b,#4a0302);color:#ffe5a0;font-weight:900;cursor:pointer}
.hs-search-links{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:14px}
.hs-search-link{display:flex;align-items:center;justify-content:space-between;gap:10px;text-decoration:none;background:#fff;border:1px solid #e2d3b8;border-radius:15px;padding:14px 15px;color:#5c0905;transition:.2s}
.hs-search-link:hover{transform:translateY(-2px);border-color:#b98a35;box-shadow:0 8px 20px rgba(70,30,0,.08)}
.hs-search-link b{font-family:"STKaiti","KaiTi","Songti SC",serif;font-size:18px}.hs-search-link small{display:block;color:#81756b;margin-top:3px;font-size:11px}.hs-arrow{font-size:20px;color:#b98a35}
.hs-search-results{display:none;margin-top:12px;padding:11px 13px;border-radius:12px;background:#fff7df;border:1px solid #ead5a4;color:#665441;font-size:12px;line-height:1.7}
.hs-search-results.show{display:block}.hs-search-results strong{color:#650600}
@media(max-width:560px){.hs-search-box{padding:17px}.hs-search-head{align-items:center}.hs-search-title{font-size:24px}.hs-search-form{display:grid;grid-template-columns:1fr}.hs-search-submit{padding:12px}.hs-search-links{grid-template-columns:1fr}.hs-search-icon{font-size:29px}}
</style>'''

HTML = r'''<!-- HONGSHENG_COLLECTION_SEARCH -->
<section class="section hs-search" id="collection-search">
  <div class="hs-search-box">
    <div class="hs-search-head">
      <div>
        <h2 class="hs-search-title">🔎 钱币信息查询</h2>
        <p class="hs-search-sub">搜索钱币名称、年份、版别、银元、古钱、纸币等关键词，快速进入相关收藏信息来源。</p>
      </div>
      <div class="hs-search-icon">🪙</div>
    </div>
    <form class="hs-search-form" id="hs-search-form">
      <input class="hs-search-input" id="hs-search-input" type="search" autocomplete="off" placeholder="例如：袁大头、康熙通宝、第一套人民币">
      <button class="hs-search-submit" type="submit">查询</button>
    </form>
    <div class="hs-search-results" id="hs-search-results"></div>
    <div class="hs-search-links">
      <a class="hs-search-link" href="https://www.pm001.net/index.asp" target="_blank" rel="noopener noreferrer" data-source="一尘网">
        <span><b>一尘网 · 交易信息</b><small>进入一尘网查询钱币交易、行情及收藏信息</small></span><span class="hs-arrow">→</span>
      </a>
      <a class="hs-search-link" href="https://www.yy11.com/htm/shop.cgi" target="_blank" rel="noopener noreferrer" data-source="钱币天堂">
        <span><b>钱币天堂 · 钱币商城</b><small>进入钱币天堂查询商城、钱币及交易信息</small></span><span class="hs-arrow">→</span>
      </a>
    </div>
  </div>
</section>
<script id="hongsheng-collection-search-js">
(function(){
  const form=document.getElementById('hs-search-form');
  const input=document.getElementById('hs-search-input');
  const result=document.getElementById('hs-search-results');
  if(!form||!input||!result)return;
  form.addEventListener('submit',function(e){
    e.preventDefault();
    const q=input.value.trim();
    if(!q){result.innerHTML='请输入钱币名称、年份或版别关键词后再查询。';result.classList.add('show');input.focus();return;}
    try{navigator.clipboard&&navigator.clipboard.writeText(q)}catch(_){ }
    result.innerHTML='<strong>关键词：</strong>'+q+'<br>已准备查询。请选择下方 <strong>一尘网</strong> 或 <strong>钱币天堂</strong>，进入对应网站继续查询。关键词已尝试复制到剪贴板，可直接粘贴。';
    result.classList.add('show');
  });
})();
</script>
'''

s = INDEX.read_text(encoding='utf-8')
if MARKER in s:
    import re
    s = re.sub(r'<!-- HONGSHENG_COLLECTION_SEARCH -->[\s\S]*?</section>\s*<script id="hongsheng-collection-search-js">[\s\S]*?</script>\s*', HTML, s, count=1)
else:
    anchor = '</main>'
    if anchor in s:
        s = s.replace(anchor, HTML + '\n' + anchor, 1)
    elif '</body>' in s:
        s = s.replace('</body>', HTML + '\n</body>', 1)
    else:
        s += '\n' + HTML

if '</head>' in s:
    if 'hongsheng-collection-search-css' not in s:
        s = s.replace('</head>', CSS + '\n</head>', 1)
else:
    s = CSS + s

INDEX.write_text(s, encoding='utf-8')
print('洪盛集藏网钱币信息查询入口已注入')
