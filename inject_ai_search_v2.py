from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

css = r'''<style id="coin-ai-search-css">
.coin-ai-search{margin:8px 0;padding:22px;border-radius:22px;background:linear-gradient(135deg,#fffaf0,#fff);border:1px solid #d9b45d;box-shadow:0 12px 34px rgba(70,20,0,.08)}
.coin-ai-search h2{margin:0;color:#650600;font-size:26px}.coin-ai-search .ai-tag{display:block;margin-top:6px;color:#8a6a24;font-size:12px}
.coin-ai-chat{margin-top:14px;background:#fff;border:1px solid #ead9b9;border-radius:18px;overflow:hidden}
.coin-ai-messages{min-height:120px;max-height:440px;overflow:auto;padding:14px;background:linear-gradient(180deg,#fffdf8,#fffaf2)}
.coin-ai-msg{display:flex;gap:9px;margin:10px 0;align-items:flex-start}.coin-ai-avatar{width:32px;height:32px;border-radius:50%;display:grid;place-items:center;background:#7d0b0b;color:#f7df91;flex:0 0 32px;font-size:16px}.coin-ai-msg.user{justify-content:flex-end}.coin-ai-msg.user .coin-ai-avatar{order:2;background:#ead9b9;color:#650600}.coin-ai-bubble{max-width:88%;padding:10px 13px;border-radius:14px;line-height:1.7;font-size:13px;white-space:pre-wrap}.coin-ai-msg.assistant .coin-ai-bubble{background:#fff;border:1px solid #ead9b9}.coin-ai-msg.user .coin-ai-bubble{background:#7d0b0b;color:#fff}.coin-ai-meta{font-size:10px;color:#928579;margin-top:4px}
.coin-ai-form{display:flex;gap:8px;padding:9px;border-top:1px solid #eee2d1;background:#fff}.coin-ai-input{flex:1;min-width:0;border:0;outline:0;padding:12px;font-size:15px;background:#fff;color:#2b211b}.coin-ai-send{border:0;border-radius:12px;background:#7d0b0b;color:#fff;padding:11px 18px;font-weight:900;cursor:pointer}.coin-ai-upload{border:1px solid #e3d4bb;background:#fffaf0;color:#6a250e;border-radius:12px;padding:10px 12px;cursor:pointer}.coin-ai-file{display:none}
.coin-ai-suggestions{display:flex;gap:7px;flex-wrap:wrap;padding:0 14px 12px}.coin-ai-suggestion{border:1px solid #e5d6bc;background:#fffaf0;border-radius:999px;padding:7px 10px;color:#6a250e;cursor:pointer;font-size:12px}
.coin-ai-status{padding:8px 14px;background:#fff6d8;color:#75603a;font-size:11px;border-top:1px solid #eee2d1}.coin-ai-note{font-size:11px;color:#75603a;background:#fff6d8;border-radius:10px;padding:9px;margin-top:12px;line-height:1.7}
@media(max-width:560px){.coin-ai-search{padding:16px}.coin-ai-form{gap:5px}.coin-ai-send{padding:10px 12px}.coin-ai-upload{padding:10px}.coin-ai-input{font-size:14px}.coin-ai-bubble{max-width:94%}}
</style>'''

html = r'''<!-- COIN_AI_SEARCH_V1 -->
<section id="ai-search" class="section coin-ai-search" aria-label="币智通AI智能搜索">
  <h2>🤖 币智通 AI</h2>
  <span class="ai-tag">像使用 GPT 一样提问：钱币、版别、行情、收藏知识都可以直接问</span>
  <div class="coin-ai-chat">
    <div id="coin-ai-messages" class="coin-ai-messages" aria-live="polite">
      <div class="coin-ai-msg assistant"><div class="coin-ai-avatar">🪙</div><div><div class="coin-ai-bubble">你好，我是币智通 AI。你可以直接问我：这枚钱币是什么？现在大概多少钱？版别怎么判断？最近市场怎么样？也可以上传钱币图片。</div><div class="coin-ai-meta">收藏研究助手 · 价格仅作市场参考</div></div></div>
    </div>
    <div class="coin-ai-suggestions">
      <button class="coin-ai-suggestion" type="button">袁大头三年现在大概什么价格？</button>
      <button class="coin-ai-suggestion" type="button">这枚古钱怎么看版别？</button>
      <button class="coin-ai-suggestion" type="button">老纸币最近市场行情怎么样？</button>
      <button class="coin-ai-suggestion" type="button">金银币收藏价值怎么判断？</button>
    </div>
    <form id="coin-ai-form" class="coin-ai-form">
      <label class="coin-ai-upload" title="上传钱币图片">📷<input id="coin-ai-file" class="coin-ai-file" type="file" accept="image/*"></label>
      <input id="coin-ai-input" class="coin-ai-input" type="search" autocomplete="off" placeholder="直接问我，例如：袁大头三年多少钱？" aria-label="向币智通AI提问">
      <button class="coin-ai-send" type="submit">发送</button>
    </form>
    <div id="coin-ai-status" class="coin-ai-status">🟡 AI接口待连接：当前保留网站资料检索；接入安全 AI API 后自动升级为多轮 GPT 式回答。</div>
  </div>
  <div class="coin-ai-note">⚠️ AI鉴定结果仅作为收藏研究和价格参考，不作为法律意义上的鉴定结论。市场价格受品相、版别、来源及实时成交情况影响。</div>
</section>
<script id="coin-ai-chat-script">
(function(){
  var endpoint = window.COIN_AI_SEARCH_ENDPOINT || '';
  var form=document.getElementById('coin-ai-form'), input=document.getElementById('coin-ai-input'), messages=document.getElementById('coin-ai-messages'), status=document.getElementById('coin-ai-status'), fileInput=document.getElementById('coin-ai-file');
  if(!form||!input||!messages) return;
  var history=[];
  function esc(s){return String(s).replace(/[&<>\"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c];});}
  function add(role,text){var row=document.createElement('div');row.className='coin-ai-msg '+role;row.innerHTML='<div class="coin-ai-avatar">'+(role==='user'?'👤':'🪙')+'</div><div><div class="coin-ai-bubble">'+esc(text).replace(/\n/g,'<br>')+'</div><div class="coin-ai-meta">'+(role==='user'?'你的问题':'币智通 AI')+'</div></div>';messages.appendChild(row);messages.scrollTop=messages.scrollHeight;}
  function localAnswer(q){
    var terms=q.toLowerCase().split(/[^\u4e00-\u9fa5a-z0-9]+/).filter(Boolean), nodes=Array.prototype.slice.call(document.querySelectorAll('main h1,main h2,main h3,main p,main td,main li,.coin b,.coin small,.fact b,.fact p')), scored=nodes.map(function(n){var t=(n.textContent||'').trim(),l=t.toLowerCase(),score=terms.reduce(function(a,w){return a+(l.indexOf(w)>=0?1:0)},0);return {t:t,score:score}}).filter(function(x){return x.score>0}).sort(function(a,b){return b.score-a.score});
    var seen={},hits=[];scored.forEach(function(x){if(hits.length<5&&!seen[x.t]){seen[x.t]=1;hits.push(x.t)}});
    return hits.length?'我先从币智通当前网页资料中找到这些相关内容：\n\n• '+hits.join('\n• ')+'\n\n如果你需要具体价格，我建议再提供：钱币名称、版别、品相和正反面图片。这样接入 AI 行情检索后，我可以进一步综合成交数据分析。':'当前网页资料中暂时没有直接匹配内容。你可以换成具体钱币名称、版别或上传图片继续问。';
  }
  function send(q,imageData){
    q=(q||'').trim(); if(!q&&!imageData)return;
    if(q)add('user',q); else add('user','[已上传钱币图片]');
    history.push({role:'user',content:q||'请分析我上传的钱币图片。'});
    status.textContent='🟠 AI正在理解问题并检索资料…';
    if(!endpoint){setTimeout(function(){var a=localAnswer(q||'钱币图片');add('assistant',a);history.push({role:'assistant',content:a});status.textContent='🟡 当前为网站资料模式。配置安全 AI API 后启用多轮 GPT 式回答与图片理解。';},250);return;}
    fetch(endpoint.replace(/\/$/,'' )+'/chat/completions',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({messages:history, image:imageData||null})}).then(function(r){if(!r.ok)throw new Error('HTTP '+r.status);return r.json()}).then(function(d){var t=d&&d.choices&&d.choices[0]&&d.choices[0].message&&d.choices[0].message.content;if(!t)throw new Error('empty');add('assistant',t);history.push({role:'assistant',content:t});status.textContent='🟢 AI回答完成 · 可继续追问';}).catch(function(){var a=localAnswer(q||'钱币图片');add('assistant',a);history.push({role:'assistant',content:a});status.textContent='🟡 AI接口暂不可用，已自动切换网站资料模式。';});
  }
  form.addEventListener('submit',function(e){e.preventDefault();send(input.value);input.value='';});
  Array.prototype.slice.call(document.querySelectorAll('.coin-ai-suggestion')).forEach(function(b){b.addEventListener('click',function(){input.value=b.textContent;form.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));});});
  if(fileInput)fileInput.addEventListener('change',function(){var f=fileInput.files&&fileInput.files[0];if(!f)return;var r=new FileReader();r.onload=function(){send('',r.result);};r.readAsDataURL(f);});
})();
</script>
'''

pattern = r'<!-- COIN_AI_SEARCH_V1 -->.*?</section>\s*<script id="(?:coin-ai-search-script|coin-ai-chat-script)">.*?</script>'
if re.search(pattern, s, flags=re.S):
    s = re.sub(pattern, lambda _m: html.rstrip(), s, count=1, flags=re.S)
else:
    raise SystemExit('existing AI search marker not found')

css_pattern = r'<style id="coin-ai-search-css">.*?</style>'
if re.search(css_pattern, s, flags=re.S):
    s = re.sub(css_pattern, lambda _m: css.strip(), s, count=1, flags=re.S)
else:
    s = s.replace('</head>', css + '\n</head>', 1)

p.write_text(s, encoding='utf-8')
print('CoinAI GPT-style chat UI upgraded')
