from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Remove the former front-end AI chat/search block.
s = re.sub(r'\s*<style id="coin-ai-search-css">.*?</style>\s*', '\n', s, flags=re.S)
s = re.sub(r'\s*<!-- COIN_AI_SEARCH_V1 -->.*?<script id="coin-ai-chat-script">.*?</script>\s*', '\n', s, flags=re.S)

# Remove stale user-facing AI chatbot wording while keeping backend automation.
for old, new in {
    '新时代人工智能，让收藏信息畅通无阻': '新时代信息集成，让收藏畅通无阻',
    '新时代人工智能 AI，让收藏畅通无阻': '新时代信息集成，让收藏畅通无阻',
    'AI自动收集 · 整理 · 分析 · 每日更新': '每日自动收集 · 整理 · 分析 · 信息更新',
    '让 AI 每天自动收集、筛选、整理钱币行业信息': '平台每天自动收集、筛选、整理钱币行业公开信息',
    'AI全自动信息助手': '每日信息自动整理',
    'AI正在整理今日钱币行业信息，自动生成摘要与重点观察。': '平台正在整理今日钱币行业信息，自动生成摘要与重点观察。',
    '每日 AI 整理行业新闻、市场大事、拍卖动态与收藏热点': '每日整理行业新闻、市场大事、拍卖动态与收藏热点',
}.items():
    s = s.replace(old, new)

# Remove accidental duplicate legacy market-image script blocks.
blocks = re.findall(r'<script>\s*/\* COIN-AI-MARKET-IMAGE-SCRIPT-START \*/.*?/\* COIN-AI-MARKET-IMAGE-SCRIPT-END \*/\s*</script>', s, flags=re.S)
for extra in blocks[1:]:
    s = s.replace(extra, '', 1)

# Modern Chinese-heritage visual layer: classical typography for titles, modern typography for body/data.
css = '''<style id="hongsheng-heritage-theme">
:root{--hs-red:#6f0a08;--hs-deep:#260302;--hs-gold:#b98a35;--hs-gold2:#e8ca79;--hs-paper:#f6efe2;--hs-line:#ddc9a7;--hs-ink:#2b211b}
html{scroll-behavior:smooth}
body{background:radial-gradient(circle at 12% 8%,rgba(185,138,53,.08),transparent 24%),radial-gradient(circle at 90% 35%,rgba(111,10,8,.055),transparent 26%),var(--hs-paper);color:var(--hs-ink);font-family:-apple-system,BlinkMacSystemFont,"Noto Sans SC","PingFang SC","Microsoft YaHei",Arial,sans-serif}
body:before{content:"";position:fixed;inset:0;pointer-events:none;opacity:.035;background-image:radial-gradient(#6b4b2a .7px,transparent .7px);background-size:7px 7px;z-index:-1}
.top{background:linear-gradient(90deg,#160000,#4b0503,#160000);border-bottom:1px solid rgba(232,202,121,.45);letter-spacing:1.5px}
.hero{position:relative;overflow:hidden;background:radial-gradient(circle at 78% 35%,rgba(232,202,121,.16),transparent 18%),radial-gradient(circle at 22% 80%,rgba(255,255,255,.06),transparent 28%),linear-gradient(135deg,#160000 0%,#650705 58%,#310202 100%);padding:42px 0 40px}
.hero:after{content:"";position:absolute;left:5%;right:5%;bottom:10px;height:1px;background:linear-gradient(90deg,transparent,var(--hs-gold2),transparent);opacity:.7}
.kicker,.brand,.sub,.title,.coin b,.table th{font-family:"STKaiti","KaiTi","FZKai-Z03","Songti SC","Noto Serif SC",serif}
.kicker{letter-spacing:5px;color:#ead18a}.brand{font-size:64px!important;letter-spacing:5px!important;text-shadow:0 2px 0 #3a0000,0 5px 18px rgba(0,0,0,.28)!important}.sub{letter-spacing:2.5px}
.hero p{font-size:15px;max-width:720px}.hero-coin img{border-color:var(--hs-gold2);box-shadow:0 22px 55px rgba(0,0,0,.48),0 0 0 10px rgba(232,202,121,.08)!important}
.nav{background:rgba(255,250,240,.94);border-bottom:1px solid var(--hs-line);box-shadow:0 4px 18px rgba(70,30,0,.06)}.nav a{font-family:"STKaiti","KaiTi","Songti SC",serif;font-size:15px;color:var(--hs-red)!important;border:1px solid transparent;transition:.2s}.nav a:hover{border-color:var(--hs-line);background:#fff6df;transform:translateY(-1px)}
.title{font-size:30px!important;letter-spacing:1px;position:relative;padding-left:18px}.title:before{content:"";position:absolute;left:0;top:5px;bottom:5px;width:4px;border-radius:3px;background:linear-gradient(#6f0a08,#b98a35)}.title:after{content:"◆";font-family:serif;color:var(--hs-gold);font-size:11px;margin-left:10px;vertical-align:middle}
.section{padding:32px 0}.service-banner,.panel,.market,.metal,.svc,.address,.fact{box-shadow:0 8px 28px rgba(80,45,15,.055)}.service-banner{border-color:var(--hs-gold);position:relative}.service-banner:before{content:"藏";position:absolute;right:18px;top:12px;font-family:"STKaiti","KaiTi","Songti SC",serif;font-size:62px;color:rgba(111,10,8,.055);font-weight:900}
.news-main{border:1px solid rgba(232,202,121,.35);box-shadow:0 12px 36px rgba(45,0,0,.16)}.news-copy h2{font-family:"STKaiti","KaiTi","Songti SC",serif;font-size:31px}
.coin{box-shadow:0 7px 20px rgba(50,10,0,.12);transition:transform .2s,box-shadow .2s}.coin:hover{transform:translateY(-4px);box-shadow:0 13px 28px rgba(50,10,0,.18)}.coin b{font-size:16px}
.table th{font-size:15px}.market{border-color:var(--hs-line)}.market .table tbody tr:hover{background:#fff7df}.price{font-family:Georgia,"Times New Roman",serif;letter-spacing:.5px}.contact{box-shadow:0 10px 28px rgba(50,0,0,.18)}.btn,.contact a{box-shadow:0 5px 14px rgba(70,10,0,.12)}.notice{border-left:4px solid var(--hs-gold)}footer{background:rgba(255,250,240,.5)}
@media(max-width:520px){.hero{padding:30px 0 32px}.brand{font-size:45px!important;letter-spacing:3px!important}.title{font-size:25px!important}.hero p{font-size:13px}.nav a{font-size:14px}}
</style>'''
if 'id="hongsheng-heritage-theme"' not in s:
    s = s.replace('</head>', css + '\n</head>', 1)

p.write_text(s, encoding='utf-8')
print('洪盛集藏网：古韵现代化视觉升级完成；前台AI对话已清理。')
