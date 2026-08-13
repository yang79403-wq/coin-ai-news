from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# 统一网站前台品牌，避免自动资讯/搜索注入器再次恢复旧品牌名称。
replacements = {
    '币智通 AI · CoinAI｜福建泉州、厦门、福州钱币行业信息服务平台｜AI资讯、收藏趣闻、行情分析、免费鉴定评估': '洪盛集藏网｜全球钱币收藏信息集成与咨询服务平台｜资讯、趣闻、行情、成交、图鉴、咨询',
    '币智通 AI · CoinAI｜钱币行业信息平台': '洪盛集藏网｜钱币收藏信息集成与咨询服务平台',
    '币智通 <em>AI</em>': '洪盛集藏网',
    '币智通AI': '洪盛集藏网',
    '币智通 AI': '洪盛集藏网',
    'COIN AI': 'HONGSHENG COLLECTION',
    'CoinAI': 'Hongsheng Collection',
    '币智通当前网页资料': '洪盛集藏网当前网页资料',
}
for old, new in replacements.items():
    s = s.replace(old, new)

# 品牌主标题不再显示“AI”，但保留AI自动整理作为后台能力描述。
s = s.replace('新时代人工智能 AI，让收藏畅通无阻', '新时代人工智能，让收藏信息畅通无阻')
s = s.replace('人工智能 AI', '人工智能')

p.write_text(s, encoding='utf-8')
print('网站品牌已统一为：洪盛集藏网')
