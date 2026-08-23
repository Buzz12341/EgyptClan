import os, sys, json, time, hashlib, shutil, zipfile, re
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher
import requests

API='https://api.modrinth.com/v2'
GAME='1.21.1'
LOADER='neoforge'
TARGET=118
MAX_COUNT=120
UA='Buzz12341-NeoForge-Modpack-Builder/2.0 (personal-use modpack builder)'
s=requests.Session(); s.headers.update({'User-Agent':UA})

# Do not include these even if a search happens to return them.
BLACKLIST_SLUGS={
    'natures-compass','explorers-compass','embeddium','oculus','optifine','iris'
}

# Mandatory/high-priority content. The builder will refuse a root if a required
# dependency cannot be resolved for NeoForge 1.21.1.
MUST=[
 ('Create','create','6.0.10'),
 ('Create Aeronautics','create-aeronautics','1.3'),
 ('Create Aeronautics: Gadgets & Gizmos','create-aeronautics-gadgets-and-gizmos',None),
 ('Create Aeronautics: Automated Logistics','create-aeronautics-automated-logistics',None),
 ('Create Aeronautics Discovery','create-aeronautics-discovery',None),
 ('Create Aeronautics Structures','aeronautics-structures',None),
 ('Create Aeronautics: Transmission & Linkage','create-aeronautics-transmission-linkage',None),
 ('Create Aeronautics Gyro Stabilizers','create-aeronautics-gyroscope-stabilizers',None),
 ('Create Aeronautics Rubies','simrubies',None),
 ('Create Diesel Generators','create-diesel-generators',None),
 ('Create Radars','create-radars',None),
 ('Create Big Cannons','create-big-cannons',None),
 ('Create Crafts & Additions','createaddition',None),
 ('Create Enchantment Industry',None,None),
 ('Create Slice & Dice',None,None),
 ('Create Copycats+','copycats',None),
 ('Create Connected',None,None),
 ('Create New Age',None,None),
 ('Create Power Loader',None,None),
 ("Create Steam 'n' Rails",'create-steam-n-rails-1.21.1',None),
 ('Create Aeroworks',None,None),
 ('Create Dragons Plus',None,None),
 ('Create Structures',None,None),

 ('IceAndFire Community Edition','iceandfire-ce',None),
 ('Ice and Fire Spellbooks',None,None),
 ('Ice and Fire Dragon Care',None,None),
 ('Ice and Fire Better Combat',None,None),
 ('Spartan Weaponry Ice and Fire Unofficial',None,None),
 ('Spartan Weaponry Unofficial',None,None),

 ("L_Ender's Cataclysm",'l_enders-cataclysm',None),
 ('Cataclysm Spellbooks','cataclysm-spellbooks',None),
 ('Cataclysm Tools',None,None),
 ('Reliquified L_Enders Cataclysm',None,None),
 ('Simply Swords Cataclysm',None,None),

 ('Better Combat','better-combat',None),
 ('Simply Swords','simply-swords',None),
 ('Punchy','punchy-fpa',None),
 ('Not Enough Animations','not-enough-animations',None),
 ('Better Animations Collection','better-animations-collection',None),
 ('3D Skin Layers','3dskinlayers',None),

 ('BetterEnd New Dawn','betterend-neoforge',None),
 ('BetterNether New Dawn','betternether-neoforge',None),
 ('Terralith','terralith',None),
 ('Tectonic','tectonic',None),
 ("YUNG's API",None,None),
 ("YUNG's Better Mineshafts",None,None),
 ("YUNG's Better Dungeons",None,None),
 ("YUNG's Better Strongholds",None,None),
 ("YUNG's Better Desert Temples",None,None),
 ("YUNG's Better Jungle Temples",None,None),
 ("YUNG's Better Ocean Monuments",None,None),
 ("YUNG's Better Witch Huts",None,None),
 ("YUNG's Better Nether Fortresses",None,None),
 ('When Dungeons Arise','when-dungeons-arise',None),
 ('Dungeons and Taverns','dungeons-and-taverns',None),
 ('Towns and Towers','towns-and-towers',None),
 ('Repurposed Structures','repurposed-structures',None),

 ('Enhanced AI',None,None),
 ('Improved Mobs',None,None),

 ('Just Enough Items',None,None),
 ('Jade','jade',None),
 ('Sodium','sodium',None),
 ('Sodium Extra','sodium-extra',None),
 ('FerriteCore','ferrite-core',None),
 ('ModernFix','modernfix',None),
 ('Entity Culling','entityculling',None),
 ('Clumps','clumps',None),
 ('AppleSkin','appleskin',None),
 ('Mouse Tweaks','mouse-tweaks',None),
 ('Controlling','controlling',None),
 ('Searchables','searchables',None),
 ("Xaero's Minimap",None,None),
 ("Xaero's World Map",None,None),
 ('Waystones','waystones',None),
 ('Lootr','lootr',None),
 ('Sophisticated Backpacks',None,None),
 ('Sophisticated Storage',None,None),
 ('Farmer\'s Delight',None,None),
 ("Iron's Spells 'n Spellbooks",None,None),
 ('Relics',None,None),
]

# Filler is deliberately ordered: Create/Aeronautics first, then adventure,
# structures, QoL/performance. We stop at TARGET and never go over MAX_COUNT.
CANDIDATES=[
 ('Create Deco',None,None),('Create Interiors',None,None),('Create Stuff & Additions',None,None),
 ('Create Central Kitchen',None,None),('Create Dreams & Desires',None,None),('Create Escalated',None,None),
 ('Create Hypertube',None,None),('Create Jetpack',None,None),('Create Jetpack Curios',None,None),
 ('Create Cyber Goggles','create-cyber-goggles',None),('Create Collision Crashfix','create-collision-crashfix',None),
 ('Create Bits n Bobs',None,None),('Create Blocks & Bogies',None,None),('Design n Decor',None,None),
 ('Create Prismatic Shine',None,None),('Gears n Kinetics Create',None,None),('Create Power Grid',None,None),
 ('Create Compact Transmission',None,None),('Create Let The Adventure Begin',None,None),
 ('Create Structures Arise',None,None),('Create Transmission',None,None),('Create Storage',None,None),
 ('Create More Automation',None,None),('Create Ultimate Factory',None,None),('Create Train Parts',None,None),
 ('Create Factory Logistics',None,None),('Create Tradeworks',None,None),('Create Stock Market',None,None),
 ('Create Tweaked Controllers',None,None),('Create Garnished',None,None),('Create Mechanical Extruder',None,None),
 ('Create Mechanical Spawner',None,None),('Create Ore Excavation',None,None),('Create Sifter',None,None),
 ('Create Recycling',None,None),('Create Utilities',None,None),('Create Railways Navigator',None,None),
 ('Create Bells & Whistles',None,None),('Create Liquid Fuel',None,None),('Create Dynamic Village',None,None),

 ('Create Aeronautics Weight','create-aeronautics-weight',None),
 ('Create Aeronautics Lift Patch','create-aeronautics-lift-patch',None),
 ('Dimensional Sable','dimensional-sable',None),('Sable Far and Wide','sable-far-and-wide',None),
 ('Create Aeronautics Ship Saver','aeroship-saver',None),('Aeronautics Winds and Weather','aeronautics-winds-and-weather',None),
 ('Create Missiles','create-missiles',None),('Create Propulsion Simulated',None,None),
 ('Create Linear Motion Simulated',None,None),('Create Aeronautics Toolgun',None,None),
 ('Create Aero Cables',None,None),('Climbable Ropes Create Aeronautics',None,None),
 ('Copycats Aeronautics Weight',None,None),('Big Tires Create Aeronautics',None,None),
 ('Sticky Wheels Create Aeronautics',None,None),('Create Tracks Plus',None,None),

 ('Integrated Cataclysm','integrated-catalcysm',None),('Cataclysm Better Combat',None,None),
 ('Ice and Fire XaeroMap Support',None,None),('Ice and Fire Smithing',None,None),

 ('Explorify','explorify',None),('Structory','structory',None),('Formations',None,None),
 ('Formations Overworld',None,None),('Formations Nether',None,None),('ChoiceTheorems Overhauled Village',None,None),
 ("YUNG's Bridges",None,None),("YUNG's Extras",None,None),

 ('Supplementaries','supplementaries',None),('Amendments','amendments',None),('Quark','quark',None),
 ('Artifacts','artifacts',None),('Ars Nouveau','ars-nouveau',None),('Apotheosis','apotheosis',None),
 ('Naturalist','naturalist',None),('Guard Villagers','guard-villagers',None),('Creeper Overhaul','creeper-overhaul',None),
 ('Enderman Overhaul','enderman-overhaul',None),('Friends and Foes','friends-and-foes',None),
 ('Mowzies Mobs',None,None),('Alexs Mobs',None,None),('Alexs Caves',None,None),

 ('Carry On','carry-on',None),('Corpse','corpse',None),('BetterF3','betterf3',None),
 ('Polymorph','polymorph',None),('Shulker Box Tooltip','shulkerboxtooltip',None),
 ('Enchantment Descriptions','enchantment-descriptions',None),('Inventory Sorter',None,None),
 ('Sound Physics Remastered','sound-physics-remastered',None),('Presence Footsteps','presence-footsteps',None),
 ('Dynamic FPS','dynamic-fps',None),('ImmediatelyFast','immediatelyfast',None),
 ('Spark','spark',None),('Better Third Person','better-third-person',None),
 ('FallingTree','fallingtree',None),('Serene Seasons','serene-seasons',None),
 ('Storage Drawers','storage-drawers',None),('Functional Storage','functional-storage',None),
 ('Cooking for Blockheads','cooking-for-blockheads',None),('Farmers Respite','farmers-respite',None),
]

out=Path('out'); mods=out/'mods'; out.mkdir(exist_ok=True); mods.mkdir(exist_ok=True)
log=[]; failed=[]; warnings=[]
project_cache={}; versions_cache={}; version_cache={}
planned={} # project_id -> version object
planned_names={}


def note(x):
    print(x, flush=True); log.append(x)

def api_get(path, params=None, retries=5):
    url=path if path.startswith('http') else API+path
    last=None
    for i in range(retries):
        try:
            r=s.get(url,params=params,timeout=45)
            if r.status_code==429:
                time.sleep(2+i*2); continue
            r.raise_for_status(); return r.json()
        except Exception as e:
            last=e; time.sleep(1.5*(i+1))
    raise last

def norm(t):
    return re.sub(r'[^a-z0-9]+','',t.lower())

def compatible(v):
    return GAME in (v.get('game_versions') or []) and LOADER in (v.get('loaders') or [])

def versions_for(project_id, prefix=None):
    key=(project_id,prefix or '')
    if key in versions_cache: return versions_cache[key]
    vs=api_get(f'/project/{project_id}/version', {'loaders':json.dumps([LOADER]),'game_versions':json.dumps([GAME])})
    if not isinstance(vs,list): vs=[vs] if vs else []
    if prefix: vs=[v for v in vs if str(v.get('version_number','')).startswith(prefix)]
    # Modrinth usually returns newest first. Keep release > beta > alpha, then newest ISO timestamp.
    pri={'release':0,'beta':1,'alpha':2}
    vs.sort(key=lambda v:(pri.get(v.get('version_type'),3), v.get('date_published','')), reverse=False)
    # The previous sort puts oldest timestamp first within type, correct that explicitly.
    grouped=[]
    for typ in ('release','beta','alpha'):
        g=[v for v in vs if v.get('version_type')==typ]
        g.sort(key=lambda v:v.get('date_published',''), reverse=True)
        grouped.extend(g)
    grouped.extend([v for v in vs if v.get('version_type') not in ('release','beta','alpha')])
    versions_cache[key]=grouped
    return grouped

def get_version(vid):
    if vid in version_cache: return version_cache[vid]
    v=api_get(f'/version/{vid}'); version_cache[vid]=v; return v

def project_by_ref(name, slug=None):
    ck=(name,slug)
    if ck in project_cache: return project_cache[ck]
    if slug:
        if slug in BLACKLIST_SLUGS: return None
        try:
            p=api_get('/project/'+slug)
            if p.get('slug') in BLACKLIST_SLUGS: return None
            project_cache[ck]=p; return p
        except Exception:
            pass
    facets=json.dumps([[f'versions:{GAME}'],[f'categories:{LOADER}'],['project_type:mod']])
    res=api_get('/search', {'query':name,'limit':20,'index':'downloads','facets':facets})
    hits=res.get('hits',[]) if isinstance(res,dict) else []
    if not hits: return None
    n=norm(name)
    ranked=[]
    for h in hits:
        if h.get('slug') in BLACKLIST_SLUGS: continue
        title=h.get('title','')
        score=SequenceMatcher(None,n,norm(title)).ratio()
        if norm(title)==n: score+=1.0
        elif n in norm(title) or norm(title) in n: score+=0.3
        ranked.append((score,h))
    ranked.sort(key=lambda x:x[0],reverse=True)
    for score,h in ranked:
        if score < 0.58: continue
        try:
            if versions_for(h['project_id']):
                p=api_get('/project/'+h['project_id'])
                project_cache[ck]=p; return p
        except Exception:
            continue
    return None

def choose_version(project_id,prefix=None):
    vs=versions_for(project_id,prefix)
    return vs[0] if vs else None

def closure_for(rootv):
    closure={}; stack=[rootv]
    while stack:
        v=stack.pop(); project_id=str(v.get('project_id'))
        if project_id in closure: continue
        closure[project_id]=v
        for d in v.get('dependencies') or []:
            if d.get('dependency_type')!='required': continue
            dv=None
            try:
                if d.get('version_id'):
                    cand=get_version(d['version_id'])
                    if compatible(cand): dv=cand
                if dv is None and d.get('project_id'):
                    dv=choose_version(str(d['project_id']))
                if dv is None:
                    raise RuntimeError(f"required dependency unresolved: {d}")
                stack.append(dv)
            except Exception as e:
                return None, f'{project_id}: {e}'
    return closure,None

def try_add(entry,mandatory=False):
    name,slug,prefix=entry
    try:
        p=project_by_ref(name,slug)
        if not p: raise RuntimeError('project not found on Modrinth for NeoForge 1.21.1')
        if p.get('slug') in BLACKLIST_SLUGS: raise RuntimeError('blacklisted')
        v=choose_version(str(p['id']),prefix)
        if not v: raise RuntimeError('compatible version not found'+(f' with prefix {prefix}' if prefix else ''))
        closure,err=closure_for(v)
        if closure is None: raise RuntimeError(err)

        new=[k for k in closure if k not in planned]
        future=len(planned)+len(new)
        if not mandatory and future>TARGET:
            note(f'SKIP limit: {name} (+{len(new)} -> {future})'); return False
        if future>MAX_COUNT:
            if mandatory:
                warnings.append(f'Mandatory root {name} would exceed {MAX_COUNT}; skipped to preserve requested size.')
            return False

        # Avoid replacing an already planned project with a different version.
        for project_id,v2 in closure.items():
            if project_id in planned and planned[project_id].get('id')!=v2.get('id'):
                # Create 6.0.10 and other already-selected roots take precedence.
                continue
            if project_id not in planned:
                planned[project_id]=v2
                try:
                    pp=api_get('/project/'+project_id)
                    planned_names[project_id]=pp.get('title') or pp.get('slug') or project_id
                except Exception:
                    planned_names[project_id]=project_id
        note(f'ADD {name}: {v.get("version_number")} | total {len(planned)}')
        return True
    except Exception as e:
        failed.append(f'{name}: {e}')
        note(f'SKIP {name}: {e}')
        return False

note('=== Mandatory/high-priority mods ===')
for e in MUST:
    try_add(e,mandatory=True)

note(f'After mandatory roots/dependencies: {len(planned)}')
note('=== Filling to target ===')
for e in CANDIDATES:
    if len(planned)>=TARGET: break
    try_add(e,mandatory=False)

note(f'Final planned count: {len(planned)}')
if len(planned)<100:
    warnings.append(f'Only {len(planned)} projects resolved; expected at least 100.')

# Download all jars selected by the plan.
installed=[]
for i,(project_id,v) in enumerate(planned.items(),1):
    files=v.get('files') or []
    f=next((x for x in files if x.get('primary')), files[0] if files else None)
    if not f:
        failed.append(f'{planned_names.get(project_id,project_id)}: no file in version {v.get("version_number")}')
        continue
    filename=f['filename']
    if not filename.lower().endswith('.jar'):
        # A required mod dependency should be a jar; skip non-jar payloads rather than contaminating mods/.
        failed.append(f'{planned_names.get(project_id,project_id)}: selected file is not jar: {filename}')
        continue
    dest=mods/filename
    print(f'DOWNLOAD [{i}/{len(planned)}] {filename}',flush=True)
    ok=False
    for attempt in range(5):
        try:
            with s.get(f['url'],stream=True,timeout=180) as r:
                r.raise_for_status()
                with open(dest,'wb') as fh:
                    for chunk in r.iter_content(1024*1024):
                        if chunk: fh.write(chunk)
            sha1=(f.get('hashes') or {}).get('sha1')
            if sha1:
                h=hashlib.sha1()
                with open(dest,'rb') as fh:
                    for chunk in iter(lambda:fh.read(1024*1024),b''): h.update(chunk)
                if h.hexdigest().lower()!=sha1.lower():
                    raise RuntimeError('SHA1 mismatch')
            ok=True; break
        except Exception as e:
            if dest.exists(): dest.unlink()
            if attempt==4: failed.append(f'{filename}: download failed: {e}')
            time.sleep(2*(attempt+1))
    if ok:
        installed.append((planned_names.get(project_id,project_id),v.get('version_number',''),filename))

# Sanity blacklist on resulting filenames.
for p in list(mods.glob('*.jar')):
    low=p.name.lower()
    if 'naturescompass' in low or 'nature_compass' in low or 'explorerscompass' in low or 'explorer_compass' in low:
        p.unlink(); warnings.append('Removed blacklisted compass: '+p.name)

installed.sort(key=lambda x:x[2].lower())
(out/'MODLIST.txt').write_text('\n'.join(f'{i+1:03d}. {n} | {ver} | {fn}' for i,(n,ver,fn) in enumerate(installed))+'\n',encoding='utf-8')
(out/'FAILED_OR_SKIPPED.txt').write_text('\n'.join(failed)+'\n',encoding='utf-8')
(out/'BUILD_NOTES.txt').write_text(
    f'Minecraft {GAME} / NeoForge\nJava 21\nJAR files downloaded: {len(installed)}\n'
    'Nature\'s Compass: NOT INCLUDED\nExplorer\'s Compass: NOT INCLUDED\n'
    'Create pinned to 6.0.10 when available.\n\nWarnings:\n'+'\n'.join(warnings)+'\n',encoding='utf-8')

# The workflow artifact itself will be a ZIP containing this folder. Also create a direct ZIP inside it.
zipname=out/'Survival_1.21.1_NeoForge_MODS.zip'
with zipfile.ZipFile(zipname,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(mods.glob('*.jar')):
        z.write(p,arcname='mods/'+p.name)
    for fname in ('MODLIST.txt','FAILED_OR_SKIPPED.txt','BUILD_NOTES.txt'):
        z.write(out/fname,arcname=fname)

print(f'ZIP_READY={zipname} size={zipname.stat().st_size} jars={len(installed)}',flush=True)
if len(installed)<90:
    print('ERROR: too few jars downloaded',file=sys.stderr); sys.exit(2)
