from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = '<!-- COIN_AI_SEARCH_V1 -->'
if marker in s:
    print('AI search already injected')
    raise SystemExit(0)

css = r'''<style id="coin-ai-search-css">
.coin-ai-search{margin:8px 0;padding:22px;border-radius:22px;background:linear-gradient(135deg,#fffaf0,#fff);border:1px solid #d9b45d;box-shadow:0 12px 34px rgba(70,20,0,.08)}
.coin-ai-search h2{margin:0;color:#650600;font-size:26px}.coin-ai-search .ai-tag{display:block;margin-top:6px;color:#8a6a24;font-size:12px}
.coin-ai-search .ai-search-form{display:flex;gap:8px;background:#fff;border:1px solid #e3d4bb;border-radius:15px;padding:7px;margin-top:14px}
.coin-ai-search input{flex:1;min-width:0;border:0;outline:0;padding:12px;font-size:15px;background:transparent;color:#2b211b}.coin-ai-search button{border:0;border-radius:11px;background:#7d0b0b;color:#fff;padding:11px 18px;font-weight:900;cursor:pointer}
.coin-ai-search .ai-suggestions{display:flex;gap:7px;flex-wrap:wrap;margin:11px 0}.coin-ai-search .ai-suggestion{border:1px solid #e5d6bc;background:#fffaf0;border-radius:999px;padding:7px 10px;color:#6a250e;cursor:pointer;font-size:12px}
.coin-ai-search .ai-answer{display:none;margin-top:14px;background:#fffdf8;border:1px solid #ead9b9;border-radius:16px;padding:16px;line-height:1.75}.coin-ai-search .ai-answer.show{display:block}
.coin-ai-search .ai-result{padding:10px 0;border-bottom:1px solid #eee2d1}.coin-ai-search .ai-meta{font-size:11px;color:#897b6d;margin-top:5px}.coin-ai-search .ai-note{font-size:11px;color:#75603a;background:#fff6d8;border-radius:10px;padding:9px;margin-top:12px}
@media(max-width:560px){.coin-ai-search .ai-search-form{padding:5px}.coin-ai-search button{padding:10px 12px}.coin-ai-search input{font-size:14px}}
</style>'''

html = r'''<!-- COIN_AI_SEARCH_V1 -->
<section id="ai-search" class="section coin-ai-search" aria-label="币智通AI智能搜索">
  <h2>🔎 币智通 AI 智能搜索</h2>
  <span class="ai-tag">问钱币 · 问价格 · 问版别 · 问收藏知识</span>
  <form class="ai-search-form" id="coin-ai-search-form">
    <input id="coin-ai-search-input" type="search" autocomplete="off" placeholder="例如：袁大头三年现在大概什么价格？" aria-label="搜索钱币问题">
    <button type="submit">AI搜索</button>
  </form>
  <div class="ai-suggestions">
    <button class="ai-suggestion" type="button">袁大头三年价格</button>
    <button class="ai-suggestion" type="button">古钱币怎么辨版</button>
    <button class="ai-suggestion" type="button">老纸币市场行情</button>
    <button class="ai-suggestion" type="button">金银币收藏知识</button>
  </div>
  <div id="coin-ai-search-answer" class="ai-answer" aria-live="polite"></div>
  <div class="ai-note">优先检索币智通网站资料；接入 AI Search 后，可进一步使用持续更新的知识库生成综合回答。价格仅作收藏研究参考。</div>
</section>
<script id="coin-ai-search-script">
(function(){
  var endpoint = window.COIN_AI_SEARCH_ENDPOINT || '';
  var form = document.getElementById('coin-ai-search-form');
  var input = document.getElementById('coin-ai-search-input');
  var answer = document.getElementById('coin-ai-search-answer');
  if(!form || !input || !answer) return;
  function esc(s){return String(s).replace(/[&<>\"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c];});}
  function clean(s){return String(s || '').replace(/\s+/g,' ').trim();}
  function localSearch(q){
    var words=clean(q).toLowerCase().split(/[^\u4e00-\u9fa5a-z0-9]+/).filter(Boolean);
    var nodes=Array.prototype.slice.call(document.querySelectorAll('main h1,main h2,main h3,main p,main td,main li,.coin b,.coin small,.fact b,.fact p'));
    var scored=nodes.map(function(n){var t=clean(n.textContent),low=t.toLowerCase(),score=words.reduce(function(a,w){return a+(low.indexOf(w)>=0?1:0);},0);return {t:t,score:score};}).filter(function(x){return x.score>0;}).sort(function(a,b){return b.score-a.score;});
    var out=[],seen={};
    scored.forEach(function(x){if(out.length<6 && !seen[x.t]){seen[x.t]=1;out.push(x.t);}});
    return out;
  }
  function showLocal(q){
    var hits=localSearch(q);
    var body=hits.length?hits.map(function(x){return '<div class="ai-result">'+esc(x)+'</div>';}).join(''):'<div class="ai-result">暂未找到直接匹配资料。请换一个钱币名称、版别或价格问题。</div>';
    answer.innerHTML='<h3>📚 币智通资料检索</h3>'+body+'<div class="ai-meta">当前为网站内资料检索。配置 AI Search 后将升级为 AI 综合回答。</div>';
    answer.classList.add('show');
  }
  function search(q){
    answer.innerHTML='<h3>🤖 AI正在检索</h3><div class="ai-result">正在分析“'+esc(q)+'”…</div>';
    answer.classList.add('show');
    if(!endpoint){showLocal(q);return;}
    fetch(endpoint.replace(/\/$/,'')+'/chat/completions',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({messages:[{role:'user',content:q}]})})
      .then(function(r){if(!r.ok) throw new Error('HTTP '+r.status);return r.json();})
      .then(function(data){var text=data&&data.choices&&data.choices[0]&&data.choices[0].message&&data.choices[0].message.content;if(text){answer.innerHTML='<h3>🤖 币智通 AI 分析</h3><div class="ai-result">'+esc(text).replace(/\n/g,'<br>')+'</div><div class="ai-meta">AI Search · 实时检索结果</div>'; }else{showLocal(q);}})
      .catch(function(){showLocal(q);});
  }
  form.addEventListener('submit',function(e){e.preventDefault();var q=clean(input.value);if(q)search(q);});
  Array.prototype.slice.call(document.querySelectorAll('.ai-suggestion')).forEach(function(b){b.addEventListener('click',function(){input.value=b.textContent;form.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));});});
})();
</script>
'''

if '<main' not in s:
    s += css + html
else:
    s = s.replace('<main', css + '\n<main', 1)
    anchor = '>\n<section class="section">'
    if anchor in s:
        s = s.replace(anchor, '>\n' + html + '\n<section class="section">', 1)
    else:
        s = s.replace('<main', '<main>\n' + html, 1)

p.write_text(s, encoding='utf-8')
print('AI search injected')
