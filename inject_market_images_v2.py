from pathlib import Path

INDEX = Path('index.html')
MARKER = '<!-- COIN-AI-MARKET-IMAGE-V2 -->'

JS = r'''<script id="coin-ai-market-image-v2">
/* COIN-AI-MARKET-IMAGE-V2 */
(function(){
  const map={
    '银元':'assets/coins/yuan-3-obverse.jpg','袁':'assets/coins/yuan-3-obverse.jpg',
    '古钱':'assets/coins/cash-coins-a.jpg','宝':'assets/coins/cash-coins-a.jpg',
    '纸币':'assets/coins/rmb1-100-1b.jpg','人民币':'assets/coins/rmb1-100-1b.jpg',
    '纪念币':'assets/coins/founding-commemorative.jpg','纪念钞':'assets/coins/rmb1-100-1b.jpg',
    '金银币':'assets/coins/panda-2016-reverse.png','金币':'assets/coins/panda-2016-reverse.png','银币':'assets/coins/panda-2016-reverse.png'
  };
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const imgFor=name=>{name=String(name||'');for(const k in map)if(name.includes(k))return map[k];return 'assets/coins/cash-coins-a.jpg'};
  function openCoin(r,img){
    const old=document.getElementById('coin-image-modal');if(old)old.remove();
    const el=document.createElement('div');el.id='coin-image-modal';
    el.innerHTML='<div class="cim-mask"></div><div class="cim-card"><button class="cim-close" aria-label="关闭">×</button><img src="'+img+'" alt="'+esc(r.name)+'"><h3>'+esc(r.name)+'</h3><div class="cim-price">¥'+Number(r.price||0).toLocaleString('zh-CN')+'</div><div class="cim-meta">'+esc(r.date||'')+' · '+esc(r.type||'公开成交/报价线索')+'</div><p>图片为本站钱币图鉴参考图，不代表本条成交记录中的具体实物。真伪、版别、品相和评级请以原始实物资料为准。</p></div>';
    document.body.appendChild(el);el.querySelector('.cim-mask').onclick=()=>el.remove();el.querySelector('.cim-close').onclick=()=>el.remove();
  }
  function render(){
    fetch('market-data.json?v='+Date.now(),{cache:'no-store'}).then(r=>r.json()).then(d=>{
      const rows=d.rows||[];
      document.querySelectorAll('.market-live .price-table').forEach(table=>{
        const cat=table.getAttribute('data-category')||'';
        const rr=rows.filter(r=>r.category===cat).slice(0,15);const tbody=table.querySelector('tbody');if(!tbody)return;
        tbody.innerHTML=rr.length?rr.map(r=>{const payload=encodeURIComponent(JSON.stringify(r));return '<tr class="market-row" data-coin="'+payload+'" tabindex="0"><td class="coin-name"><img class="market-thumb" src="'+imgFor(r.name)+'" alt="钱币图">'+esc(r.name)+'</td><td><strong>¥'+Number(r.price||0).toLocaleString('zh-CN')+'</strong></td><td>'+esc(r.date||'')+'</td></tr>'}).join(''):'<tr><td colspan="3" class="empty">暂无可确认的公开价格数据<br><small>下一次自动采集后更新</small></td></tr>';
        tbody.querySelectorAll('.market-row').forEach(row=>{const r=JSON.parse(decodeURIComponent(row.dataset.coin));row.onclick=()=>openCoin(r,imgFor(r.name));row.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();openCoin(r,imgFor(r.name))}}});
      });
    }).catch(()=>{});
  }
  const style=document.createElement('style');style.textContent=`.market-live .market-row{cursor:pointer}.market-live .market-row:hover,.market-live .market-row:focus{background:#fff7df;outline:none}.market-live .coin-name{display:flex;align-items:center;gap:9px;font-weight:800}.market-live .market-thumb{width:46px;height:46px;border-radius:50%;object-fit:cover;border:2px solid #d9b45d}#coin-image-modal{position:fixed;inset:0;z-index:9999;display:grid;place-items:center}#coin-image-modal .cim-mask{position:absolute;inset:0;background:#160000d9;backdrop-filter:blur(5px)}#coin-image-modal .cim-card{position:relative;z-index:2;width:min(92vw,520px);background:#fffaf0;border:1px solid #d9b45d;border-radius:24px;padding:22px;text-align:center;box-shadow:0 25px 80px #0008}#coin-image-modal img{width:min(70vw,300px);height:min(70vw,300px);max-width:300px;max-height:300px;border-radius:50%;object-fit:cover;border:6px solid #d9b45d}.cim-close{position:absolute;right:12px;top:8px;border:0;background:transparent;font-size:32px;color:#680904}.cim-price{font-size:28px;font-weight:900;color:#74470a}.cim-meta{font-size:12px;color:#75695f}#coin-image-modal p{font-size:11px;line-height:1.7;color:#75603a;background:#fff2cf;padding:10px;border-radius:12px}`;document.head.appendChild(style);
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',render);else render();
})();
</script>'''

html=INDEX.read_text(encoding='utf-8')
if MARKER not in html:
    html=html.replace('</body>',MARKER+'\n'+JS+'\n</body>',1)
else:
    import re
    html=re.sub(r'<!-- COIN-AI-MARKET-IMAGE-V2 -->.*?<script id="coin-ai-market-image-v2">.*?</script>',MARKER+'\n'+JS,html,flags=re.S)
INDEX.write_text(html,encoding='utf-8')
print('market image v2 injected')
