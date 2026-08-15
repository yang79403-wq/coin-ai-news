[Uploading app.js…]()
const grid=document.getElementById('marketGrid');
const updated=document.getElementById('updated');
function money(v){return v==null?'待接入':('¥'+Number(v).toLocaleString('zh-CN',{maximumFractionDigits:2}))}
async function load(cat=''){
  grid.innerHTML='<div class="muted">正在加载行情…</div>';
  const url='/api/prices'+(cat?'?category='+encodeURIComponent(cat):'');
  try{
    const res=await fetch(url); const data=await res.json();
    if(!data.length){grid.innerHTML='<div class="muted">暂无该分类数据，等待自动采集。</div>';return}
    grid.innerHTML=data.map(x=>`<article class="market"><div class="name">${x.name}</div><div class="price">${money(x.price)}</div><div class="${x.change_pct>0?'up':''}">${x.price==null?'市场参考价待更新':(x.change_pct>0?'↑ ':'')+x.change_pct+'%'}</div><div class="source">${x.source||'数据源'} · ${x.captured_at||''}</div></article>`).join('');
    updated.textContent='数据状态：自动化行情接口已连接';
  }catch(e){grid.innerHTML='<div class="muted">行情接口暂不可用，请稍后刷新。</div>';updated.textContent='数据接口离线';}
}
document.querySelectorAll('.filters button').forEach(btn=>btn.addEventListener('click',()=>{document.querySelectorAll('.filters button').forEach(b=>b.classList.remove('active'));btn.classList.add('active');load(btn.dataset.cat);}));
load();

<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>洪盛集藏资讯网｜钱币收藏交流服务</title>
<meta name="description" content="洪盛集藏资讯网：收藏交流、免费鉴赏参考、品相分析、市场行情、评级咨询、福建钱币资料研究。">
<link rel="stylesheet" href="/static/style.css">
</head>
<body>

<header class="top">
  <div class="wrap nav">
    <a class="brand" href="#"><span>洪盛</span>集藏资讯网</a>
    <nav>
      <a href="#services">资讯服务</a>
      <a href="#advisor">收藏顾问</a>
      <a href="#grading">评级服务</a>
      <a href="#research">收藏研究</a>
      <a href="#fujian">福建资料库</a>
    </nav>
    <a class="phone" href="tel:13799875350">☎ 13799875350</a>
  </div>
</header>

<section class="hero">
  <div class="wrap hero-grid">
    <div>
      <div class="eyebrow">HONGSHENG JICANG · COIN COLLECTING</div>
      <h1>洪盛集藏资讯网</h1>
      <h2>钱币收藏交流服务</h2>
      <p class="hero-text">
        收藏交流 · 鉴赏参考 · 品相分析 · 市场行情 · 钱币文化研究
      </p>

      <div class="public-welfare">
        <div class="pw-title">📚 公益收藏资料平台</div>
        <p><strong>洪盛集藏资讯网为公益性钱币收藏交流与资料研究网站。</strong></p>
        <p>本网站主要用于钱币收藏知识分享、资料整理、行情信息交流、历史文化研究及收藏爱好者之间的学习交流。</p>
        <p><strong>所有价格、成交信息、行情数据、图片、资料及分析内容，仅供收藏爱好者学习、研究和收藏参考，不构成任何买卖、投资、鉴定、估价或交易依据。</strong></p>
        <p class="pw-note">钱币实际价值受品种、年份、版别、品相、真伪、评级、市场供需及实际成交情况等因素影响。</p>
      </div>

      <div class="service-banner">
        <strong>📍 福建省内周边 · 厦门 · 泉州 · 漳州 · 福州 · 成都</strong>
        <span>当天可预约上门面对面分析交流</span>
      </div>

      <div class="hero-actions">
        <a class="btn primary" href="#consult">免费鉴定</a>
        <a class="btn gold" href="#consult">免费估价</a>
        <a class="btn outline" href="tel:13799875350">立即咨询</a>
      </div>

      <div class="trust">
        <span>✓ 免费鉴定交流</span>
        <span>✓ 免费估价参考</span>
        <span>✓ 隐私保密</span>
        <span>✓ 无交易不收费</span>
      </div>
    </div>

    <div class="hero-panel">
      <div class="seal">洪盛<br><small>集藏</small></div>
      <div class="panel-title">专业收藏交流</div>
      <div class="panel-big">免费鉴定 · 免费估价</div>
      <div class="panel-line"></div>
      <div class="panel-contact">13799875350</div>
      <div class="panel-small">照片 / 视频线上咨询 · 面对面交流预约</div>
    </div>
  </div>
</section>

<section id="services" class="section">
  <div class="wrap">
    <div class="head">
      <span class="eyebrow">COLLECTION SERVICE</span>
      <h2>钱币收藏交流服务</h2>
      <p>以收藏知识、鉴赏交流和市场信息为核心，为藏友提供长期、专业的交流参考。</p>
    </div>
    <div class="service-grid eight">
      <article><b>✅ 收藏交流</b><p>藏品展示、玩家交流与收藏经验分享。</p></article>
      <article><b>✅ 免费鉴赏参考</b><p>照片、视频在线交流，提供基础判断思路。</p></article>
      <article><b>✅ 品相分析</b><p>磨损、包浆、原味状态等维度交流。</p></article>
      <article><b>✅ 收藏建议</b><p>结合个人方向提供收藏参考。</p></article>
      <article><b>✅ 市场行情分享</b><p>关注收藏热点、成交趋势与行情变化。</p></article>
      <article><b>✅ 真伪交流</b><p>分享基础辨识思路与收藏经验。</p></article>
      <article><b>✅ 收藏知识普及</b><p>版别、历史、材质、铸造知识学习。</p></article>
      <article><b>✅ 藏品展示</b><p>建立藏品图片与资料展示空间。</p></article>
    </div>
  </div>
</section>

<section id="advisor" class="section cream">
  <div class="wrap">
    <div class="head">
      <span class="eyebrow">COLLECTOR ADVISOR</span>
      <h2>收藏顾问服务</h2>
      <p>从新手入门到长期收藏，帮助藏友建立更清晰的收藏体系。</p>
    </div>
    <div class="advisor-grid">
      <div class="advisor-main">
        <h3>让收藏更有方向</h3>
        <p>根据收藏兴趣、预算和研究方向，提供收藏规划与知识学习参考。</p>
        <div class="taglist">
          <span>收藏方向规划</span><span>钱币价值分析参考</span><span>市场行情交流</span>
          <span>收藏投资思路分享</span><span>藏品配置建议</span><span>收藏风险提示</span>
          <span>新手入门指导</span><span>玩家交流互动</span><span>版本知识学习</span>
          <span>长期收藏指导</span>
        </div>
      </div>
      <div class="advisor-side">
        <div class="number">10</div>
        <strong>项收藏顾问服务</strong>
        <p>覆盖收藏方向、行情、版别、风险及长期收藏规划。</p>
      </div>
    </div>
  </div>
</section>

<section id="grading" class="section dark">
  <div class="wrap">
    <div class="head">
      <span class="eyebrow">GRADING CONSULTATION</span>
      <h2>评级服务交流</h2>
      <p>提供评级知识、送评流程和收藏建议交流，不代替评级机构作出评级结论。</p>
    </div>
    <div class="grading-grid">
      <article><span>⭐</span><h3>PCGS</h3><p>美国评级咨询</p></article>
      <article><span>⭐</span><h3>NGC</h3><p>国际评级咨询</p></article>
      <article><span>⭐</span><h3>PMG</h3><p>纸币评级咨询</p></article>
      <article><span>⭐</span><h3>华夏评级</h3><p>送评指导</p></article>
    </div>
    <div class="grading-list">
      <span>⭐ 评级知识交流</span>
      <span>⭐ 评级流程、标准及注意事项交流</span>
      <span>⭐ 裸币与评级币收藏建议</span>
    </div>
  </div>
</section>

<section id="research" class="section">
  <div class="wrap">
    <div class="head">
      <span class="eyebrow">RESEARCH & KNOWLEDGE</span>
      <h2>收藏研究与知识服务</h2>
      <p>围绕不同钱币门类持续整理资料，建立洪盛集藏钱币知识库。</p>
    </div>
    <div class="research-grid">
      <article><b>🏮 老银元收藏交流</b><p>袁大头、船洋、龙洋等，研究年份、版式、铸造特征与品相。</p></article>
      <article><b>🏮 铜钱古币版别研究</b><p>清钱、古泉、花钱等，整理文字、版别与历史资料。</p></article>
      <article><b>🏮 老纸币价值分析</b><p>第一至第四套人民币、地方纸币等，研究版别与品相。</p></article>
      <article><b>🏮 纪念币收藏咨询</b><p>流通纪念币、金银币、现代纪念币资料交流。</p></article>
      <article><b>🏮 机制币版别交流</b><p>年份、版式、铸造特征及图片对比研究。</p></article>
      <article><b>🏮 品相评估交流</b><p>磨损、包浆、原味状态等收藏品相参考。</p></article>
      <article><b>🏮 真伪知识分享</b><p>基础辨识思路与收藏经验交流。</p></article>
      <article><b>🏮 市场行情动态</b><p>收藏热点、成交趋势与行情参考。</p></article>
      <article><b>🏮 收藏体系搭建</b><p>收藏方向规划、预算配置建议。</p></article>
      <article><b>🏮 钱币文化与历史研究</b><p>历史背景、铸造工艺、文化故事。</p></article>
      <article><b>🏮 藏品保管建议</b><p>保存、防氧化、防潮等经验分享。</p></article>
    </div>
  </div>
</section>

<section id="fujian" class="section fujian">
  <div class="wrap">
    <div class="head">
      <span class="eyebrow">FUJIAN COIN DATABASE</span>
      <h2>福建钱币资料库</h2>
      <p>专门建立福建钱币、福建地方钱币资料的自动整理与研究数据库。</p>
    </div>
    <div class="database-box">
      <div>
        <h3>🇨🇳 福建钱币研究资料库</h3>
        <p>自动发现公开资料 → 分类整理 → 图片资料归档 → OCR识别 → 去重 → AI研究分析 → 建立钱币知识档案。</p>
      </div>
      <div class="db-tags">
        <span>福建钱币</span><span>福建地方钱币</span><span>福建机制币</span>
        <span>福建银元</span><span>福建铜钱</span><span>福建纸币</span>
        <span>泉州</span><span>厦门</span><span>漳州</span><span>福州</span>
      </div>
    </div>
  </div>
</section>

<section id="consult" class="section consult">
  <div class="wrap consult-grid">
    <div>
      <span class="eyebrow">FREE CONSULTATION</span>
      <h2>免费鉴定 · 免费估价</h2>
      <p>可提供藏品照片或视频，配合年份、重量、尺寸、来源等信息进行线上交流。</p>
      <p>福建省内周边、厦门、泉州、漳州、福州、成都，可提前预约当天上门面对面分析交流。</p>
      <div class="notice">🔒 隐私全程保密　｜　免费鉴定　｜　免费估价　｜　无交易不收费</div>
    </div>
    <div class="contact-card">
      <div>咨询 / 微信</div>
      <a href="tel:13799875350">13799875350</a>
      <p>在线咨询 · 上门交流预约</p>
      <a class="btn primary wide" href="tel:13799875350">立即电话咨询</a>
    </div>
  </div>
</section>

<footer>
  <div class="wrap footer-inner">
    <div><b>洪盛集藏资讯网</b><small>钱币收藏交流服务 · 收藏 · 鉴赏 · 文化分享</small></div>
    <div>☎ 13799875350</div>
  </div>
  <div class="wrap legal">
    <strong>📚 公益性网站声明</strong>：本网站为公益性钱币收藏交流与资料研究平台。所有数据、价格、成交信息、图片、资料及分析内容仅供收藏爱好者学习、研究、交流及收藏参考，不构成任何投资建议、交易承诺、鉴定结论、估价结论或价格保证。
  </div>
</footer>

</body>
</html>
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;color:#241b18;background:#fbf8f3}a{text-decoration:none;color:inherit}.wrap{width:min(1180px,92%);margin:auto}.top{position:sticky;top:0;z-index:20;background:rgba(27,15,12,.97);color:#fff;border-bottom:1px solid rgba(255,255,255,.08)}.nav{height:72px;display:flex;align-items:center;gap:28px}.brand{font-size:21px;font-weight:900;letter-spacing:1px;white-space:nowrap}.brand span{color:#d9aa52}.nav nav{display:flex;gap:22px;margin-left:auto}.nav nav a{font-size:13px;color:#ddd}.phone{background:#b98b3d;padding:11px 17px;border-radius:999px;font-weight:800;font-size:13px;white-space:nowrap}.hero{background:radial-gradient(circle at 78% 28%,#712319 0,#421610 38%,#1b0f0d 76%);color:#fff;padding:88px 0 82px}.hero-grid{display:grid;grid-template-columns:1.25fr .75fr;gap:70px;align-items:center}.eyebrow{font-size:12px;letter-spacing:2.2px;color:#c49a50;font-weight:900}.hero h1{font-size:58px;line-height:1.08;margin:18px 0 6px}.hero h2{font-size:29px;margin:0 0 20px;color:#e2bd75}.hero-text{font-size:18px;color:#d8cbc5}.service-banner{display:flex;flex-direction:column;gap:7px;border-left:3px solid #c89b4c;background:rgba(255,255,255,.055);padding:15px 18px;margin:25px 0;color:#f1dfc1}.service-banner span{font-size:13px;color:#cbbdb5}.hero-actions{display:flex;gap:11px;flex-wrap:wrap;margin:26px 0}.btn{display:inline-block;padding:14px 22px;border-radius:10px;font-weight:900}.primary{background:#d1a24f;color:#24170f}.gold{background:#8f3024;color:#fff}.outline{border:1px solid #8d6e62;color:#fff}.trust{display:flex;flex-wrap:wrap;gap:15px;color:#cfc0b9;font-size:12px}.hero-panel{background:linear-gradient(145deg,#5c1b15,#291310);border:1px solid rgba(215,168,78,.4);border-radius:25px;padding:34px;min-height:350px;display:flex;flex-direction:column;justify-content:center;box-shadow:0 25px 70px rgba(0,0,0,.28)}.seal{width:78px;height:78px;border:2px solid #d7ad5c;border-radius:50%;display:flex;align-items:center;justify-content:center;text-align:center;color:#e3bd73;font-weight:900;line-height:1.05;margin-bottom:28px}.seal small{font-size:11px}.panel-title{font-size:14px;color:#c9b8ae}.panel-big{font-size:29px;font-weight:900;margin:10px 0}.panel-line{height:1px;background:#63453d;margin:20px 0}.panel-contact{font-size:28px;color:#ddb362;font-weight:900}.panel-small{font-size:12px;color:#aa9890;margin-top:8px}.section{padding:78px 0}.cream{background:#f2ede5}.dark{background:#20120f;color:#fff}.head{margin-bottom:30px}.head h2{font-size:36px;margin:9px 0}.head p{color:#71645d;line-height:1.8;margin:0;max-width:800px}.dark .head p{color:#c8b8b1}.service-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:15px}.service-grid article,.research-grid article{background:#fff;border:1px solid #e7ddd2;border-radius:17px;padding:22px;transition:.2s}.service-grid article:hover,.research-grid article:hover{transform:translateY(-3px);box-shadow:0 12px 30px rgba(54,30,20,.08)}article b{font-size:16px}.service-grid p,.research-grid p{font-size:13px;color:#71645d;line-height:1.75;margin-bottom:0}.advisor-grid{display:grid;grid-template-columns:1fr 300px;gap:18px}.advisor-main,.advisor-side{background:#fff;border:1px solid #e4d8cc;border-radius:20px;padding:30px}.advisor-main h3{font-size:25px;margin-top:0}.advisor-main p{color:#70635b;line-height:1.8}.taglist{display:flex;flex-wrap:wrap;gap:9px}.taglist span{background:#f4eee5;border:1px solid #e2d4c4;padding:9px 12px;border-radius:999px;font-size:13px}.advisor-side{background:#2a1712;color:#fff}.number{font-size:64px;color:#d7aa58;font-weight:900}.advisor-side p{color:#c7b8b0;line-height:1.7}.grading-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:15px}.grading-grid article{background:#2b1813;border:1px solid #5b3c33;border-radius:18px;padding:25px}.grading-grid span{color:#dfb45f;font-size:22px}.grading-grid h3{font-size:24px;margin:10px 0 4px}.grading-grid p{color:#c9b9b1;margin:0}.grading-list{display:flex;gap:12px;flex-wrap:wrap;margin-top:18px}.grading-list span{border:1px solid #60443a;border-radius:999px;padding:10px 14px;color:#d8c8c0;font-size:13px}.research-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:15px}.fujian{background:#f0e9df}.database-box{background:#2a1712;color:#fff;border-radius:22px;padding:30px;display:flex;justify-content:space-between;gap:35px;align-items:center}.database-box h3{font-size:24px;margin:0 0 10px}.database-box p{color:#cbbab1;line-height:1.8;max-width:680px}.db-tags{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}.db-tags span{border:1px solid #75584b;border-radius:999px;padding:9px 12px;color:#dfbd7c;font-size:12px}.consult{background:linear-gradient(120deg,#f6efe5,#e9ddcd)}.consult-grid{display:grid;grid-template-columns:1fr 390px;gap:60px;align-items:center}.consult h2{font-size:42px;margin:10px 0}.consult p{line-height:1.85;color:#655850}.notice{margin-top:20px;padding:15px 17px;background:#fff;border-left:4px solid #b8893e;color:#5d4b3d;font-size:13px}.contact-card{background:#281511;color:#fff;border-radius:21px;padding:30px}.contact-card>div{font-size:13px;color:#c5b4ac}.contact-card>a:not(.btn){display:block;font-size:30px;color:#dfb15a;font-weight:900;margin:10px 0}.contact-card p{color:#c8b8b0}.wide{text-align:center;width:100%}footer{background:#140b09;color:#c7b7ae;padding:25px 0}.footer-inner{display:flex;justify-content:space-between;gap:20px;font-size:13px}.footer-inner b{color:#dfb45e;display:block}.footer-inner small{display:block;color:#897971;margin-top:6px}@media(max-width:900px){.nav nav{display:none}.hero-grid,.consult-grid,.advisor-grid{grid-template-columns:1fr}.service-grid{grid-template-columns:repeat(2,1fr)}.grading-grid{grid-template-columns:repeat(2,1fr)}.research-grid{grid-template-columns:repeat(2,1fr)}.database-box{display:block}.db-tags{justify-content:flex-start}.hero h1{font-size:46px}}@media(max-width:560px){.nav{height:64px}.phone{display:none}.hero{padding:58px 0}.hero h1{font-size:38px}.hero h2{font-size:23px}.service-grid,.grading-grid,.research-grid{grid-template-columns:1fr}.section{padding:56px 0}.consult h2{font-size:34px}.footer-inner{display:block}.footer-inner>div+div{margin-top:10px}}.public-welfare{margin:25px 0 0;padding:18px 20px;background:rgba(255,246,220,.075);border:1px solid rgba(218,175,91,.38);border-left:4px solid #d3a554;border-radius:14px;color:#e6d7cb;font-size:12px;line-height:1.75}.public-welfare .pw-title{font-size:16px;color:#e4bd72;font-weight:900;margin-bottom:7px}.public-welfare p{margin:4px 0}.public-welfare .pw-note{color:#bca9a0}.legal{padding:16px 0 5px;color:#78655d;font-size:11px;line-height:1.7}.legal strong{color:#b9904d}
