from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / 'index.html'
MARKET = ROOT / 'market-data.json'

# Local real-coin images already mirrored into the site.
DEFAULT_IMAGES = {
    '银元': 'assets/coins/yuan-shikai.jpg',
    '袁': 'assets/coins/yuan-shikai.jpg',
    '古钱': 'assets/coins/ancient-coin.jpg',
    '宝': 'assets/coins/ancient-coin.jpg',
    '纸币': 'assets/coins/banknote.jpg',
    '人民币': 'assets/coins/banknote.jpg',
    '纪念币': 'assets/coins/commemorative-coin.jpg',
    '纪念钞': 'assets/coins/commemorative-note.jpg',
    '金银币': 'assets/coins/gold-silver.jpg',
    '金币': 'assets/coins/gold-silver.jpg',
    '银币': 'assets/coins/gold-silver.jpg',
}

MARKER_START = '<!-- COIN-AI-MARKET-IMAGE-SCRIPT-START -->'
MARKER_END = '<!-- COIN-AI-MARKET-IMAGE-SCRIPT-END -->'

JS = r'''<script>
/* COIN-AI-MARKET-IMAGE-SCRIPT-START */
(function(){
  const map={
    '银元':'assets/coins/yuan-shikai.jpg','袁':'assets/coins/yuan-shikai.jpg',
    '古钱':'assets/coins/ancient-coin.jpg','宝':'assets/coins/ancient-coin.jpg',
    '纸币':'assets/coins/banknote.jpg','人民币':'assets/coins/banknote.jpg',
    '纪念币':'assets/coins/commemorative-coin.jpg','纪念钞':'assets/coins/commemorative-note.jpg',
    '金银币':'assets/coins/gold-silver.jpg','金币':'assets/coins/gold-silver.jpg','银币':'assets/coins/gold-silver.jpg'
  };
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function imgFor(name){
    name=String(name||'');
    for(const k in map) if(name.includes(k)) return map[k];
    return 'assets/coins/rare-xianfeng.jpg';
  }
  function openCoin(r,img){
    const old=document.getElementById('coin-image-modal'); if(old) old.remove();
    const el=document.createElement('div'); el.id='coin-image-modal';
    el.innerHTML='<div class="cim-mask"></div><div class="cim-card"><button class="cim-close" aria-label="关闭">×</button><img src="'+img+'" alt="'+esc(r.name)+'"><div class="cim-title">'+esc(r.name)+'</div><div class="cim-price">¥'+Number(r.price||0).toLocaleString('zh-CN')+'</div><div class="cim-meta">'+esc(r.date||'')+' · '+esc(r.type||'公开成交/报价线索')+'</div><div class="cim-note">图片为网站本地钱币图鉴参考图。具体成交藏品的版别、品相、评级与真伪，请以原始实物资料为准。</div></div>';
    document.body.appendChild(el);
    el.querySelector('.cim-mask').onclick=()=>el.remove(); el.querySelector('.cim-close').onclick=()=>el.remove();
  }
  function render(){
    fetch('market-data.json?marketimg='+Date.now(),{cache:'no-store'}).then(r=>r.json()).then(d=>{
      const rows=d.rows||[];
      const table=document.querySelector('.market-live .price-table');
      if(!table) return;
      const tbody=table.querySelector('tbody'); if(!tbody) return;
      tbody.innerHTML=rows.length?rows.slice(0,40).map(r=>{
        const im=imgFor(r.name); const payload=encodeURIComponent(JSON.stringify(r));
        return '<tr class="market-row" data-coin="'+payload+'" tabindex="0" title="点击查看钱币图片与成交信息"><td class="coin-name"><img class="market-thumb" src="'+im+'" alt="钱币图"> <span>'+esc(r.name)+'</span></td><td><strong>¥'+Number(r.price||0).toLocaleString('zh-CN')+'</strong></td><td>'+esc(r.date||'')+'</td><td>'+esc(r.type||'公开成交/报价线索')+'</td></tr>';
      }).join(''):'<tr><td colspan="4" style="text-align:center;color:#999">暂无可确认价格线索</td></tr>';
      tbody.querySelectorAll('.market-row').forEach(row=>{
        const r=JSON.parse(decodeURIComponent(row.dataset.coin)); const im=imgFor(r.name);
        row.onclick=()=>openCoin(r,im); row.onkeydown=e=>{if(e.key==='Enter'||e.key===' ') {e.preventDefault();openCoin(r,im)}};
      });
    }).catch(()=>{});
  }
  const style=document.createElement('style'); style.textContent=`
    .market-live .price-table{width:100%;border-collapse:collapse}
    .market-live .market-row{cursor:pointer;transition:.18s;background:#fff}
    .market-live .market-row:hover,.market-live .market-row:focus{background:#fff7df;box-shadow:inset 4px 0 #d9b45d;outline:none}
    .market-live .coin-name{display:flex;align-items:center;gap:9px;font-weight:800}
    .market-live .market-thumb{width:46px;height:46px;border-radius:50%;object-fit:cover;border:2px solid #d9b45d;box-shadow:0 2px 8px #5b250020}
    #coin-image-modal{position:fixed;inset:0;z-index:9999;display:grid;place-items:center}
    #coin-image-modal .cim-mask{position:absolute;inset:0;background:#160000d9;backdrop-filter:blur(5px)}
    #coin-image-modal .cim-card{position:relative;z-index:2;width:min(92vw,520px);background:#fffaf0;border:1px solid #d9b45d;border-radius:24px;padding:22px;text-align:center;box-shadow:0 25px 80px #0008}
    #coin-image-modal img{width:min(70vw,300px);height:min(70vw,300px);max-width:300px;max-height:300px;border-radius:50%;object-fit:cover;border:6px solid #d9b45d;box-shadow:0 10px 35px #0003}
    #coin-image-modal .cim-close{position:absolute;right:12px;top:8px;border:0;background:transparent;font-size:32px;color:#680904;cursor:pointer}
    #coin-image-modal .cim-title{margin-top:14px;font-size:18px;font-weight:900;color:#680904;line-height:1.5}
    #coin-image-modal .cim-price{font-size:28px;font-weight:900;color:#74470a;margin:7px 0}
    #coin-image-modal .cim-meta{font-size:12px;color:#75695f}
    #coin-image-modal .cim-note{margin-top:12px;padding:10px;border-radius:12px;background:#fff2cf;color:#75603a;font-size:11px;line-height:1.7;text-align:left}
  `; document.head.appendChild(style);
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',render); else render();
})();
/* COIN-AI-MARKET-IMAGE-SCRIPT-END */
</script>'''

html = INDEX.read_text(encoding='utf-8')
# Remove an older injected block if present.
start = html.find(MARKER_START)
if start >= 0:
    script_start = html.rfind('<script>', 0, start)
    end_marker = html.find(MARKER_END, start)
    script_end = html.find('</script>', end_marker)
    if script_start >= 0 and script_end >= 0:
        html = html[:script_start] + html[script_end + len('</script>'):]

pos = html.lower().rfind('</body>')
if pos < 0:
    raise SystemExit('index.html 中未找到 </body>')
html = html[:pos] + JS + '\n' + html[pos:]
INDEX.write_text(html, encoding='utf-8')
print('已注入成交价格图片点击查看功能')
