from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile, ZipInfo

from .artifact_ledger import file_sha256
from .hashing import canonical_json, sha256_digest

_STABLE_DT = (1980, 1, 1, 0, 0, 0)
_STABLE_TS = "1979-03-06T03:06:09Z"
_EXCLUDE = {"release_deck.zip", "release_deck_zip_manifest.json", "release_deck_zip_receipt.json", "RELEASE_DECK_ZIP_SUMMARY.md"}


def _include(rel: Path) -> bool:
    if any(p.startswith('.') for p in rel.parts): return False
    if any(p in {'__pycache__','.pytest_cache'} for p in rel.parts): return False
    if rel.name in _EXCLUDE: return False
    return True


def _collect(deck: Path) -> list[dict]:
    items=[]
    for p in sorted(deck.rglob('*')):
        if not p.is_file(): continue
        rel=p.relative_to(deck)
        if not _include(rel): continue
        items.append({"path": rel.as_posix(), "size_bytes": p.stat().st_size, "sha256": file_sha256(p)})
    return items


def create_release_deck_zip_manifest(deck_dir: str | Path, zip_path: str | Path | None = None) -> dict:
    deck=Path(deck_dir)
    zp=Path(zip_path) if zip_path else deck/'release_deck.zip'
    files=_collect(deck) if deck.exists() else []
    paths={f['path'] for f in files}
    missing=[x for x in ['index.html','RELEASE_DECK.md','release_deck_manifest.json','release_deck_receipt.json'] if x not in paths]
    card_count=len([p for p in paths if p.startswith('cards/card_') and p.endswith('.html')])
    try:
        man=json.loads((deck/'release_deck_manifest.json').read_text(encoding='utf-8'))
        if man.get('card_count',0)>0 and card_count==0: missing.append('cards/card_*.html')
    except Exception:
        pass
    m={
      "schema":"waveforge.release_deck_zip_manifest.v2_alpha","project":"WaveForgeStudio","version":"2.1-alpha","deck_root":".","zip_output":zp.name,
      "zip_policy":{"deterministic_zip":True,"stable_timestamps":True,"sorted_entries":True,"relative_paths_only":True,"external_calls_allowed":False,"subprocess_allowed":False,"network_allowed":False,"powerpoint":False,"slide_rendering":False,"video_rendering":False,"muxing":False,"browser_automation":False},
      "files":files,"file_count":len(files),"card_count":card_count,"missing":sorted(missing),
      "outputs":{"zip":zp.name,"zip_manifest":"release_deck_zip_manifest.json","zip_receipt":"release_deck_zip_receipt.json","summary":"RELEASE_DECK_ZIP_SUMMARY.md"}
    }
    m['receipt']={"schema":"waveforge.release_deck_zip_receipt.v2_alpha","release_deck_zip_hash":sha256_digest(json.loads(canonical_json(m))),"zip_file_sha256":None,"created_at":_STABLE_TS}
    return m


def write_release_deck_zip(deck_dir: str | Path, zip_path: str | Path | None = None) -> dict:
    deck=Path(deck_dir)
    if not deck.exists() or not deck.is_dir(): raise ValueError('deck_dir must exist')
    zp=Path(zip_path) if zip_path else deck/'release_deck.zip'
    m=create_release_deck_zip_manifest(deck,zp)
    comp=ZIP_DEFLATED
    try: _=ZIP_DEFLATED
    except Exception: comp=ZIP_STORED
    with ZipFile(zp,'w',compression=comp,compresslevel=9) as zf:
        for f in m['files']:
            rel=f['path']; src=deck/rel
            zi=ZipInfo(rel,date_time=_STABLE_DT); zi.compress_type=comp
            zf.writestr(zi,src.read_bytes())
    m['receipt']['zip_file_sha256']=file_sha256(zp)
    (deck/'release_deck_zip_manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True),encoding='utf-8')
    (deck/'release_deck_zip_receipt.json').write_text(json.dumps(m['receipt'],indent=2,sort_keys=True),encoding='utf-8')
    (deck/'RELEASE_DECK_ZIP_SUMMARY.md').write_text(f"# Release Deck ZIP Summary\n\n- zip: {zp.name}\n- file_count: {m['file_count']}\n- card_count: {m['card_count']}\n- release_deck_zip_hash: {m['receipt']['release_deck_zip_hash']}\n- zip_file_sha256: {m['receipt']['zip_file_sha256']}\n",encoding='utf-8')
    return m


def validate_release_deck_zip_manifest(manifest: dict) -> list[str]:
    e=[]
    if manifest.get('schema')!='waveforge.release_deck_zip_manifest.v2_alpha': e.append('schema invalid')
    p=manifest.get('zip_policy',{})
    for k,v in {'deterministic_zip':True,'stable_timestamps':True,'sorted_entries':True,'relative_paths_only':True,'external_calls_allowed':False,'subprocess_allowed':False,'network_allowed':False,'powerpoint':False,'slide_rendering':False,'video_rendering':False,'muxing':False,'browser_automation':False}.items():
        if p.get(k) is not v: e.append(f'{k} must be {v}')
    if not manifest.get('outputs',{}).get('zip'): e.append('outputs.zip required')
    if not manifest.get('receipt',{}).get('release_deck_zip_hash'): e.append('receipt.release_deck_zip_hash required')
    present={f.get('path') for f in manifest.get('files',[])}
    for req in ['index.html','RELEASE_DECK.md','release_deck_manifest.json']:
        if req not in present: e.append(f'{req} must be present')
    return e


def assert_valid_release_deck_zip_manifest(manifest: dict) -> None:
    e=validate_release_deck_zip_manifest(manifest)
    if e: raise ValueError('Invalid release deck zip manifest: '+'; '.join(e))


def read_release_deck_zip_info(zip_path: str | Path) -> dict:
    zp=Path(zip_path)
    if not zp.exists(): return {'exists':False,'size_bytes':0,'file_count':0,'contains_index':False,'contains_markdown':False,'card_count':0,'sha256':''}
    with ZipFile(zp,'r') as zf: names=zf.namelist()
    return {'exists':True,'size_bytes':zp.stat().st_size,'file_count':len(names),'contains_index':'index.html' in names,'contains_markdown':'RELEASE_DECK.md' in names,'card_count':len([n for n in names if n.startswith('cards/card_') and n.endswith('.html')]),'sha256':file_sha256(zp)}
