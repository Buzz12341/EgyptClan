import hashlib, json, time
from pathlib import Path
import requests

API='https://api.modrinth.com/v2'
s=requests.Session(); s.headers.update({'User-Agent':'Buzz12341-NeoForge-Modpack-Link-Exporter/1.0'})
mods=Path('out/mods')
rows=[]
for i,p in enumerate(sorted(mods.glob('*.jar')),1):
    h=hashlib.sha512()
    with open(p,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    digest=h.hexdigest()
    try:
        r=s.get(f'{API}/version_file/{digest}',params={'algorithm':'sha512'},timeout=45)
        r.raise_for_status(); v=r.json()
        pid=v['project_id']
        r=s.get(f'{API}/project/{pid}',timeout=45); r.raise_for_status(); proj=r.json()
        title=proj.get('title',p.stem)
        slug=proj.get('slug',pid)
        rows.append((title,f'https://modrinth.com/mod/{slug}',p.name))
        print(f'{i:03d} OK {title} -> {slug}',flush=True)
    except Exception as e:
        rows.append((p.stem,'NOT_FOUND',p.name))
        print(f'{i:03d} FAIL {p.name}: {e}',flush=True)
    time.sleep(0.05)

rows.sort(key=lambda x:x[0].lower())
Path('out/MODRINTH_LINKS.txt').write_text('\n'.join(f'{i+1:03d}. {title} — {url}' for i,(title,url,fn) in enumerate(rows))+'\n',encoding='utf-8')
Path('out/MODRINTH_LINKS_WITH_FILES.txt').write_text('\n'.join(f'{i+1:03d}. {title} | {fn} | {url}' for i,(title,url,fn) in enumerate(rows))+'\n',encoding='utf-8')
print(f'WROTE {len(rows)} links',flush=True)
