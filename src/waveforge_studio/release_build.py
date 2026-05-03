from __future__ import annotations

import json
from pathlib import Path

from .demo_gallery import create_gallery_manifest, write_demo_gallery
from .gallery_collection import create_gallery_collection_manifest, write_gallery_collection
from .collection_export import create_collection_export_manifest, write_collection_export
from .release_deck import create_release_deck_manifest, write_release_deck
from .release_deck_zip import create_release_deck_zip_manifest, write_release_deck_zip
from .hashing import canonical_json, sha256_digest

_STABLE = "1979-03-06T03:06:09Z"


def create_release_build_manifest(runs_root: str | Path, build_dir: str | Path | None = None, title: str = "WaveForgeStudio Release Build", description: str = "", include_tags: list[str] | None = None, exclude_tags: list[str] | None = None, include_run_paths: list[str] | None = None) -> dict:
    root=Path(runs_root)
    b=Path(build_dir) if build_dir else root/'release_build'
    g=create_gallery_manifest(root, b/'gallery')
    c=create_gallery_collection_manifest(g, title=title, description=description, include_tags=include_tags, include_run_paths=include_run_paths, exclude_tags=exclude_tags, collection_dir=b/'collection')
    ce=create_collection_export_manifest(c, b/'collection/collection_manifest.json', b/'collection_export')
    rd=create_release_deck_manifest(ce, b/'collection_export/collection_export_manifest.json', b/'release_deck', title=title)
    rz=create_release_deck_zip_manifest(b/'release_deck', b/'release_deck/release_deck.zip')
    m={
      "schema":"waveforge.release_build_manifest.v2_alpha","project":"WaveForgeStudio","version":"2.2-alpha","title":title,"description":description,
      "runs_root":".","build_root":b.name,
      "selection":{"include_tags":include_tags or [],"exclude_tags":exclude_tags or [],"include_run_paths":include_run_paths or [],"missing_run_paths":c.get('selection',{}).get('missing_run_paths',[])},
      "build_policy":{"unified_release_build":True,"generates_new_runs":False,"copies_full_runs":False,"external_calls_allowed":False,"subprocess_allowed":False,"network_allowed":False,"hosting":False,"browser_automation":False,"powerpoint":False,"video_rendering":False,"muxing":False},
      "stages":{
          "gallery":{"path":f"{b.name}/gallery/gallery_manifest.json","status":"planned","hash":None},
          "collection":{"path":f"{b.name}/collection/collection_manifest.json","status":"planned","hash":None},
          "collection_export":{"path":f"{b.name}/collection_export/collection_export_manifest.json","status":"planned","hash":None},
          "release_deck":{"path":f"{b.name}/release_deck/release_deck_manifest.json","status":"planned","hash":None},
          "release_deck_zip":{"path":f"{b.name}/release_deck/release_deck_zip_manifest.json","status":"planned","hash":None,"zip_sha256":None}
      },
      "counts":{"discovered_runs":g.get('run_count',0),"selected_runs":c.get('run_count',0),"zip_count":ce.get('zip_count',0),"missing_zip_count":ce.get('missing_zip_count',0),"deck_cards":rd.get('card_count',0)},
      "outputs":{"gallery_index":f"{b.name}/gallery/index.html","collection_index":f"{b.name}/collection/index.html","collection_export_index":f"{b.name}/collection_export/index.html","release_deck_index":f"{b.name}/release_deck/index.html","release_deck_zip":f"{b.name}/release_deck/release_deck.zip","manifest":f"{b.name}/release_build_manifest.json","receipt":f"{b.name}/release_build_receipt.json","summary":f"{b.name}/RELEASE_BUILD_SUMMARY.md"}
    }
    m['receipt']={"schema":"waveforge.release_build_receipt.v2_alpha","release_build_hash":sha256_digest(json.loads(canonical_json(m))),"created_at":_STABLE}
    return m


def write_release_build(runs_root: str | Path, build_dir: str | Path | None = None, title: str = "WaveForgeStudio Release Build", description: str = "", include_tags: list[str] | None = None, exclude_tags: list[str] | None = None, include_run_paths: list[str] | None = None) -> dict:
    root=Path(runs_root)
    b=Path(build_dir) if build_dir else root/'release_build'
    b.mkdir(parents=True,exist_ok=True)
    g=write_demo_gallery(root,b/'gallery')
    c=write_gallery_collection(b/'gallery/gallery_manifest.json', b/'collection', title=title, description=description, include_tags=include_tags, include_run_paths=include_run_paths, exclude_tags=exclude_tags)
    ce=write_collection_export(b/'collection/collection_manifest.json', b/'collection_export')
    rd=write_release_deck(b/'collection_export/collection_export_manifest.json', b/'release_deck', title=title, subtitle='PHI369 Sovereign Media Showcase')
    rz=write_release_deck_zip(b/'release_deck')
    m=create_release_build_manifest(root,b,title,description,include_tags,exclude_tags,include_run_paths)
    m['stages']['gallery'].update({"status":"completed","hash":g['receipt']['gallery_hash']})
    m['stages']['collection'].update({"status":"completed","hash":c['receipt']['collection_hash']})
    m['stages']['collection_export'].update({"status":"completed","hash":ce['receipt']['collection_export_hash']})
    m['stages']['release_deck'].update({"status":"completed","hash":rd['receipt']['release_deck_hash']})
    m['stages']['release_deck_zip'].update({"status":"completed","hash":rz['receipt']['release_deck_zip_hash'],"zip_sha256":rz['receipt']['zip_file_sha256']})
    m['counts']={"discovered_runs":g['run_count'],"selected_runs":c['run_count'],"zip_count":ce['zip_count'],"missing_zip_count":ce['missing_zip_count'],"deck_cards":rd['card_count']}
    m['receipt']={"schema":"waveforge.release_build_receipt.v2_alpha","release_build_hash":sha256_digest(json.loads(canonical_json({k:v for k,v in m.items() if k!='receipt'}))),"created_at":_STABLE}
    (b/'release_build_manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True),encoding='utf-8')
    (b/'release_build_receipt.json').write_text(json.dumps(m['receipt'],indent=2,sort_keys=True),encoding='utf-8')
    (b/'RELEASE_BUILD_SUMMARY.md').write_text(f"# Release Build Summary\n\n- title: {m['title']}\n- description: {m['description']}\n- runs_root: {root}\n- build_root: {b}\n- include_tags: {m['selection']['include_tags']}\n- exclude_tags: {m['selection']['exclude_tags']}\n- include_run_paths: {m['selection']['include_run_paths']}\n- discovered_runs: {m['counts']['discovered_runs']}\n- selected_runs: {m['counts']['selected_runs']}\n- zip_count: {m['counts']['zip_count']}\n- missing_zip_count: {m['counts']['missing_zip_count']}\n- deck_cards: {m['counts']['deck_cards']}\n- release_deck_zip: {m['outputs']['release_deck_zip']}\n- release_build_hash: {m['receipt']['release_build_hash']}\n\nWaveForgeStudio unified release build only — no new runs or media are rendered.\n",encoding='utf-8')
    return m


def validate_release_build_manifest(manifest: dict) -> list[str]:
    e=[]
    if manifest.get('schema')!='waveforge.release_build_manifest.v2_alpha': e.append('schema invalid')
    p=manifest.get('build_policy',{})
    for k,v in {'unified_release_build':True,'generates_new_runs':False,'copies_full_runs':False,'external_calls_allowed':False,'subprocess_allowed':False,'network_allowed':False,'hosting':False,'browser_automation':False,'powerpoint':False,'video_rendering':False,'muxing':False}.items():
        if p.get(k) is not v: e.append(f'{k} must be {v}')
    if not manifest.get('outputs',{}).get('manifest'): e.append('outputs.manifest required')
    if not manifest.get('receipt',{}).get('release_build_hash'): e.append('receipt.release_build_hash required')
    stages=manifest.get('stages')
    if not isinstance(stages,dict): e.append('stages required')
    for s in ['gallery','collection','collection_export','release_deck','release_deck_zip']:
        if s not in (stages or {}): e.append(f'{s} stage required')
    c=manifest.get('counts',{})
    if c.get('discovered_runs',0) < c.get('selected_runs',0): e.append('selected_runs cannot exceed discovered_runs')
    return e


def assert_valid_release_build_manifest(manifest: dict) -> None:
    e=validate_release_build_manifest(manifest)
    if e: raise ValueError('Invalid release build manifest: '+'; '.join(e))


def read_release_build_info(build_dir: str | Path) -> dict:
    b=Path(build_dir)
    man=b/'release_build_manifest.json'; rec=b/'release_build_receipt.json'; summ=b/'RELEASE_BUILD_SUMMARY.md'
    sel=0
    if man.exists(): sel=json.loads(man.read_text(encoding='utf-8')).get('counts',{}).get('selected_runs',0)
    txt=summ.read_text(encoding='utf-8',errors='ignore').lower() if summ.exists() else ''
    return {'exists':b.exists(),'manifest_exists':man.exists(),'receipt_exists':rec.exists(),'summary_exists':summ.exists(),'gallery_exists':(b/'gallery').exists(),'collection_exists':(b/'collection').exists(),'collection_export_exists':(b/'collection_export').exists(),'release_deck_exists':(b/'release_deck').exists(),'release_deck_zip_exists':(b/'release_deck/release_deck.zip').exists(),'selected_runs':sel,'contains_waveforge':'waveforge' in txt}
