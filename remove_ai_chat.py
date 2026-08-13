from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Remove the public AI chat/search UI while preserving the rest of the site.
s, n_style = re.subn(r'<style\s+id=["\']coin-ai-search-css["\'][\s\S]*?</style>\s*', '', s, count=1)
s, n_section = re.subn(r'<section[^>]*class=["\'][^"\']*coin-ai-search[^"\']*["\'][\s\S]*?</section>\s*', '', s, count=1)
# Remove scripts that belong to the old public AI chat/search module.
s, n_script = re.subn(r'<script[^>]*>[\s\S]*?coin-ai-search[\s\S]*?</script>\s*', '', s, flags=re.I)
# Remove standalone AI chat/upload elements left behind by older injectors.
s, n_orphan = re.subn(r'<(?:div|section|aside)[^>]*(?:coin-ai-|ai-chat|ai-search)[^>]*>[\s\S]*?</(?:div|section|aside)>\s*', '', s, flags=re.I)

p.write_text(s, encoding='utf-8')
print(f'已移除前台AI对话/搜索功能：style={n_style}, section={n_section}, script={n_script}, orphan={n_orphan}')
