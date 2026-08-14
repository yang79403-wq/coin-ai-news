from pathlib import Path
import re

p = Path('market_update.py')
s = p.read_text(encoding='utf-8')

replacement = '''SOURCES = [
    {"provider_id":"yichen","source_name":"一尘网","url":"https://www.pm001.net/index.asp",
     "seeds":[
         "https://www.pm001.net/index.asp",
         "https://www1.pm001.net/index.asp",
         "https://www2.pm001.net/index.asp",
         "https://www3.pm001.net/index.asp",
         "http://www.pm001.net/index.asp",
         "http://www1.pm001.net/index.asp",
         "http://www2.pm001.net/index.asp",
         "http://www3.pm001.net/index.asp",
     ]},
    {"provider_id":"yy11","source_name":"钱币天堂","url":"https://www.yy11.com/c2c/forum/4.html",
     "seeds":[
         "https://www.yy11.com/c2c/forum/4.html",
         "https://www.yy11.com/c2c/forum/4.html#1",
         "https://www.yy11.com/c2c",
     ]},
    {"provider_id":"huaxia","source_name":"华夏古泉","url":"https://www.hxguquan.com/",
     "seeds":["https://www.hxguquan.com/","https://wwwn.hxguquan.com/","https://www.hxguquan.com/goods-list.html?gid=76167"]},
]
'''

pattern = r'SOURCES = \[.*?\n\]'
new_s, n = re.subn(pattern, replacement.rstrip(), s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('SOURCES block not found; refusing to modify market_update.py')

# The old generic link filter missed actual YY11 /c2c/topic/<id>.html links
# and legacy Yichen board/discussion links. Add only URL markers; same-host
# restriction remains in market_update.py.
new_s, n2 = re.subn(
    r'"topic\.cgi","dispbbs\.asp"\)',
    '"topic.cgi","dispbbs.asp","/c2c/topic/","boardid=","boardID=","/c2c/forum/")',
    new_s,
    count=1,
)
if n2 != 1:
    raise SystemExit('link-key marker not found; refusing to modify market_update.py')

p.write_text(new_s, encoding='utf-8')
print('market sources updated: 一尘网多入口 + 钱币天堂 /c2c/forum/4.html + topic/ detail links')
