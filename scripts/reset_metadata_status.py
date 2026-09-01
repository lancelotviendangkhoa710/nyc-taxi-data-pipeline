import json
from pathlib import Path

path = Path('data/metadata/etl_metadata.json')
d = json.loads(path.read_text())
for v in d.values():
    v['status'] = 'fetched'
path.write_text(json.dumps(d, indent=2, ensure_ascii=False))
print('Reset done:')
for k, v in sorted(d.items()):
    print(f"  {k} -> {v['status']}")
