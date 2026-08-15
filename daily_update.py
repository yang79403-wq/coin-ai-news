#!/usr/bin/env python3
import json,datetime
from pathlib import Path
p=Path('data/status.json')
d=json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
d['updated']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M Asia/Shanghai')
d.setdefault('news',0); d.setdefault('market',0); d.setdefault('fujian',0)
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print(d)