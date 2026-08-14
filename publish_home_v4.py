import json
from pathlib import Path

INDEX = Path("index.html")
MARKET = Path("market-data.json")
PUBLIC = Path("data/market.json")
MARKER = "<!-- HONGSHENG-MARKET-V4 -->"

css = r'''<style id="hongsheng-market-v4-css">
.hs-v4{max-width:1180px;margin:24px auto;padding:0 16px}.hs-v4-card{background:#fffdf8;border:1px solid #ddc9a7;border-radius:20px;padding:20px;box-shadow:0 8px 28px rgba(80,45,15,.07)}.hs-v4-title{margin:0 0 8px;color:#6f0a08;font:900 29px "STKaiti","KaiTi","Songti SC",serif}.hs-v4-desc{margin:0 0 14px;color:#75695f;font-size:13px}.hs-v4-search{display:flex;gap:8px;margin:12px 0 18px}.hs-v4-search input{flex:1;min-width:0;border:1px solid #ddc9a7;border-radius:12px;padding:13px 14px;font-size:14px;background:#fff}.hs-v4-search button{border:0;border-radius:12px;padding:0 18px;background:#6f0a08;color:#fff;font-weight:900}.hs-v4-tags{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:14px}.hs-v4-tags button{border:1px solid #d9b45d;background:#fff6df;color:#6f0a08;border-radius:99px;padding:7px 11px}.hs-v4-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.hs-v4-item{background:#fff;border:1px solid #eee2d1;border-radius:15px;overflow:hidden}.hs-v4-item img{width:100%;height:180px;object-fit:contain;background:#f5f2ec}.hs-v4-body{padding:12px}.hs-v4-body b{display:block;color:#5f0804;font-size:16px}.hs-v4-price{font-size:22px;font-weight:900;color:#74470a;margin:5px 0}.hs-v4-meta{font-size:11px;color:#81776e;line-height:1.6}.hs-v4-link{display:inline-block;margin-top:8px;color:#6f0a08;font-weight:900;text-decoration:none}.hs-v4-empty{padding:18px;text-align:center;color:#887c70;background:#fff7e5;border-radius:12px}.hs-v4-status{font-size:11px;color:#887c70;margin-top:10px}@media(max-width:760px){.hs-v4-grid{grid-template-columns:1fr 1fr}}@media(max-width:480px){.hs-v4-grid{grid-template-columns:1fr}.hs-v4-search{flex-direction:column}.hs-v4-search button{padding:12px}}
</style>'''

html = rf'''{MARKER}
<section class="hs-v4" id="hongsheng-market-v4">
  <div class="hs-v4-card">
    <h2 class="hs-v4-title">🔍 洪盛集藏搜索中心</h2>
    <p class="hs-v4-desc">搜索最新成交记录、价格、来源与原始商品链接。成交图片与成交价格必须来自同一原始记录。</p>
    <div class="hs-v4-search"><input id="hs-v4-input" type="search" placeholder="输入袁大头、咸丰重宝、船洋、纸币等"><button id="hs-v4-btn">立即搜索</button></div>
    <div class="hs-v4-tags"><button data-q="袁大头">袁大头</button><button data-q="孙小头">孙小头</button><button data-q="咸丰重宝">咸丰重宝</button><button data-q="船洋">船洋</button><button data-q="纸币">纸币</button><button data-q="纪念币">纪念币</button></div>
    <div id="hs-v4-list"><div class="hs-v4-empty">正在加载今日成交行情…</div></div>
    <div class="hs-v4-status" id="hs-v4-status"></div>
  </div>
</section>
<script id="hongsheng-market-v4-js">
(function(){
  const input=document.getElementById('hs-v4-input'), btn=document.getElementById('hs-v4-btn'), list=document.getElementById('hs-v4-list'), status=document.getElementById('hs-v4-status');
  let rows=[];
  const esc=s=>String(s??'').replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c]));
  const money=v=>{const n=Number(v); return Number.isFinite(n)?'¥'+n.toLocaleString('zh-CN',{maximumFractionDigits:2}):'价格待核';};
  function render(q=''){
    const key=q.trim().toLowerCase();
    const filtered=key?rows.filter(r=>(`${r.name||''} ${r.category||''} ${r.source_name||''}`).toLowerCase().includes(key)):rows;
    if(!filtered.length){list.innerHTML='<div class="hs-v4-empty">暂未找到匹配的成交记录。请换一个钱币名称搜索。</div>';return;}
    list.innerHTML='<div class="hs-v4-grid">'+filtered.slice(0,30).map(r=>`<article class="hs-v4-item"><img loading="lazy" src="${esc(r.image_url||'')}" alt="${esc(r.name||'钱币成交实物')}"><div class="hs-v4-body"><b>${esc(r.name||'未命名钱币')}</b><div class="hs-v4-price">${money(r.price)}</div><div class="hs-v4-meta">${esc(r.date||'')} · ${esc(r.category||'其他')}<br>来源：${esc(r.source_name||'未知')}</div>${r.item_url?`<a class="hs-v4-link" href="${esc(r.item_url)}" target="_blank" rel="noopener noreferrer">查看原始成交记录 →</a>`:''}</div></article>`).join('')+'</div>';
  }
  function doSearch(){render(input.value);document.getElementById('hongsheng-market-v4').scrollIntoView({behavior:'smooth',block:'start'});}
  btn.addEventListener('click',doSearch); input.addEventListener('keydown',e=>{if(e.key==='Enter')doSearch();});
  document.querySelectorAll('[data-q]').forEach(b=>b.addEventListener('click',()=>{input.value=b.dataset.q;doSearch();}));
  fetch('market-data.json?ts='+Date.now(),{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('HTTP '+r.status);return r.json();}).then(d=>{rows=Array.isArray(d.rows)?d.rows.filter(r=>r.transaction_confirmed&&r.item_url&&r.image_url&&r.price!=null):[];render();status.textContent=`数据更新时间：${d.updated_at||'未知'} · 已验证成交记录：${rows.length} 条`;}).catch(e=>{list.innerHTML='<div class="hs-v4-empty">今日成交数据暂时无法加载，网站其他内容仍可正常浏览。</div>';status.textContent='成交数据加载异常：'+e.message;});
})();
</script>'''

if not INDEX.exists() or not MARKET.exists():
    raise SystemExit("index.html or market-data.json missing")

data=json.loads(MARKET.read_text(encoding="utf-8"))
PUBLIC.parent.mkdir(parents=True,exist_ok=True)
PUBLIC.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
s=INDEX.read_text(encoding="utf-8")
if MARKER in s:
    start=s.index(MARKER)
    end=s.find('</script>',start)
    end=s.find('</script>',end+9)
    if end!=-1:
        end += len('</script>')
        # include the section and script, preserving the rest of the page
        s=s[:start]+html+s[end:]
else:
    s=s.replace('</head>',css+'\n</head>',1)
    s=s.replace('</body>',html+'\n</body>',1)
INDEX.write_text(s,encoding="utf-8")
print('Homepage V4 injected. Verified rows:',len(data.get('rows',[])))
