from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = '<!-- COIN_AI_SEARCH_V1 -->'
if marker in s:
    print('AI search already injected')
    raise SystemExit(0)

css = '''<style id="coin-ai-search-css">
.coin-ai-search{margin:8px 0 8px;padding:22px;border-radius:22px;background:linear-gradient(135deg,#fffaf0,#fff);border:1px solid #d9b45d;box-shadow:0 12px 34px rgba(70,20,0,.08)}
.coin-ai-search .ai-search-head{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin-bottom:14px}
.coin-ai-search h2{margin:0;color:#650600;font-size:26px}
.coin-ai-search .ai-tag{display:inline-block;margin-top:6px;color:#8a6a24;font-size:12px}
.coin-ai-search .ai-search-form{display:flex;gap:8px;background:#fff;border:1px solid #e3d4bb;border-radius:15px;padding:7px}
.coin-ai-search input{flex:1;min-width:0;border:0;outline:0;padding:12px;font-size:15px;background:transparent;color:#2b211b}
.coin-ai-search button{border:0;border-radius:11px;background:#7d0b0b;color:#fff;padding:11px 18px;font-weight:900;cursor:pointer}
.coin-ai-search .ai-suggestions{display:flex;gap:7px;flex-wrap:wrap;margin:11px 0}
.coin-ai-search .ai-suggestion{border:1px solid #e5d6bc;background:#fffaf0;border-radius:999px;padding:7px 10px;color:#6a250e;cursor:pointer;font-size:12px}
.coin-ai-search .ai-answer{display:none;margin-top:14px;background:#fffdf8;border:1px solid #ead9b9;border-radius:16px;padding:16px;line-height:1.75}
.coin-ai-search .ai-answer.show{display:block}
.coin-ai-search .ai-answer h3{margin:0 0 8px;color:#680904;font-size:17px}
.coin-ai-search .ai-result{padding:10px 0;border-bottom:1px solid #eee2d1}
.coin-ai-search .ai-result:last-child{border-bottom:0}
.coin-ai-search .ai-meta{font-size:11px;color:#897b6d;margin-top:4px}
.coin-ai-search .ai-note{font-size:11px;color:#75603a;background:#fff6d8;border-radius:10px;padding:9px;margin-top:12px}
@media(max-width:560px){.coin-ai-search .ai-search-head{display:block}.coin-ai-search .ai-search-form{padding:5px}.coin-ai-search button{padding:10px 12px}.coin-ai-search input{font-size:14px}}
</style>'''

html = f'''{marker}
<section id="ai-search" class="section coin-ai-search" aria-label="币智通AI智能搜索">
  <div class="ai-search-head">
    <div><h2>🔎 币智通 AI 智能搜索</h2><span class="ai-tag">问钱币 · 问价格 · 问版别 · 问收藏知识</span></div>
  </div>
  <form class="ai-search-form" id="coin-ai-search-form">
    <input id="coin-ai-search-input" type="search" autocomplete="off" placeholder="例如：袁大头三年现在大概什么价格？" aria-label="搜索钱币问题">
    <button type="submit">AI搜索</button>
  </form>
  <div class="ai-suggestions" aria-label="热门搜索">
    <button class="ai-suggestion" type="button">袁大头三年价格</button>
    <button class="ai-suggestion" type="button">古钱币怎么辨版</button>
    <button class="ai-suggestion" type="button">老纸币市场行情</button>
    <button class="ai-suggestion" type="button">金银币收藏知识</button>
  </div>
  <div id="coin-ai-search-answer" class="ai-answer" aria-live="polite"></div>
  <div class="ai-note">AI搜索会优先结合币智通网站资料；接入 AI Search 后，可进一步检索持续更新的知识库并生成综合回答。价格内容仅作收藏研究参考，不构成交易承诺。</div>
</section>
<script id="coin-ai-search-script">
(function(){
  const endpoint = window.COIN_AI_SEARCH_ENDPOINT || '';
  const form = document.getElementById('coin-ai-search-form');
  const input = document.getElementById('coin-ai-search-input');
  const answer = document.getElementById('coin-ai-search-answer');
  if(!form || !input || !answer) return;
  const clean = s => (s || '').replace(/\\s+/g,' ').trim();
  const localSearch = q => {
    const words = clean(q).toLowerCase().split(/[^\\u4e00-\\u9fa5a-z0-9]+/).filter(Boolean);
    const nodes = [...document.querySelectorAll('main h1,main h2,main h3,main p,main td,main li,.coin b,.coin small,.fact b,.fact p')];
    const scored = nodes.map(n => { const t=clean(n.textContent); const low=t.toLowerCase(); const score=words.reduce((a,w)=>a+(low.includes(w)?1:0),0); return {t,score}; }).filter(x=>x.score>0).sort((a,b)=>b.score-a.score);
    const unique=[]; const seen=new Set(); for(const x of scored){ if(!seen.has(x.t)){seen.add(x.t);unique.push(x.t);} if(unique.length>=6) break; }
    return unique;
  };
  async function aiSearch(q){
    answer.classList.add('show');
    answer.innerHTML='<h3>🤖 AI正在检索</h3><div class="ai-result">正在分析“'+escapeHtml(q)+'”…</div>';
    if(endpoint){
      try{
        const r=await fetch(endpoint.replace(/\\/$/,'')+'/chat/completions',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({messages:[{role:'user',content:q}]})});
        if(!r.ok) throw new Error('HTTP '+r.status);
        const data=await r.json();
        const text=data?.choices?.[0]?.message?.content || data?.response || data?.answer || '';
        if(text){ answer.innerHTML='<h3>🤖 币智通 AI 分析</h3><div class="ai-result">'+escapeHtml(text).replace(/\\n/g,'<br>')+'</div><div class="ai-meta">AI Search · 实时检索结果</div>'; return; }
      }catch(e){ console.warn('AI search endpoint failed',e); }
    }
    const hits=localSearch(q);
    answer.innerHTML='<h3>📚 币智通资料检索</h3>'+(hits.length?hits.map(x=>'<div class="ai-result">'+escapeHtml(x)+'</div>').join(''):'<div class="ai-result">暂未在当前页面找到直接匹配内容。你可以换一个钱币名称、版别或价格问题继续搜索。</div>')+'<div class="ai-meta">当前为网站内资料检索；配置 AI Search 后将升级为 AI 综合回答。</div>';
  }
  function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
  form.addEventListener('submit',e=>{e.preventDefault();const q=clean(input.value);if(q) aiSearch(q);});
  document.querySelectorAll('.ai-suggestion').forEach(b=>b.addEventListener('click',()=>{input.value=b.textContent;form.requestSubmit();}));
})();
</script>
'''

# Insert the search immediately before the main content starts, keeping the existing page intact.
if '<main' in s:
    s = s.replace('<main', css + '\n<main', 1)
    s = s.replace('>\n<section class="section">', '>\n' + html + '\n<section class="section">', 1)
else:
    s += css + html

p.write_text(s, encoding='utf-8')
print('AI search injected')
