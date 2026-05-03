from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile, ZipInfo

from .artifact_ledger import file_sha256
from .hashing import canonical_json, sha256_digest

_STABLE_DT=(1980,1,1,0,0,0)
_STABLE_TS='1979-03-06T03:06:09Z'
_EXCLUDE={'release_build.zip','release_build_zip_manifest.json','release_build_zip_receipt.json','RELEASE_BUILD_ZIP_SUMMARY.md'}


def _include(rel: Path)->bool:
    if any(p.startswith('.') for p in rel.parts): return False
    if any(p in {'__pycache__','.pytest_cache'} for p in rel.parts): return False
    if rel.name in _EXCLUDE: return False
    return True


def _collect(root: Path)->list[dict]:
    out=[]
    for p in sorted(root.rglob('*')):
        if not p.is_file(): continue
        rel=p.relative_to(root)
        if not _include(rel): continue
        out.append({'path':rel.as_posix(),'size_bytes':p.stat().st_size,'sha256':file_sha256(p)})
    return out


def create_release_build_zip_manifest(build_dir: str|Path, zip_path: str|Path|None=None)->dict:
    b=Path(build_dir); zp=Path(zip_path) if zip_path else b/'release_build.zip'
    files=_collect(b) if b.exists() else []
    paths={f['path'] for f in files}
    expected=['release_build_manifest.json','release_build_receipt.json','RELEASE_BUILD_SUMMARY.md','gallery/gallery_manifest.json','collection/collection_manifest.json','collection_export/collection_export_manifest.json','release_deck/release_deck_manifest.json','release_deck/release_deck.zip','release_deck/release_deck_zip_manifest.json','release_deck/release_deck_zip_receipt.json']
    missing=[x for x in expected if x not in paths]
    m={'schema':'waveforge.release_build_zip_manifest.v2_alpha','project':'WaveForgeStudio','version':'2.3-alpha','build_root':'.','zip_output':zp.name,
       'zip_policy':{'deterministic_zip':True,'stable_timestamps':True,'sorted_entries':True,'relative_paths_only':True,'external_calls_allowed':False,'subprocess_allowed':False,'network_allowed':False,'hosting':False,'browser_automation':False,'powerpoint':False,'video_rendering':False,'muxing':False},
       'files':files,'file_count':len(files),'missing':sorted(missing),
       'outputs':{'zip':zp.name,'zip_manifest':'release_build_zip_manifest.json','zip_receipt':'release_build_zip_receipt.json','summary':'RELEASE_BUILD_ZIP_SUMMARY.md'}}
    m['receipt']={'schema':'waveforge.release_build_zip_receipt.v2_alpha','release_build_zip_hash':sha256_digest(json.loads(canonical_json(m))),'zip_file_sha256':None,'created_at':_STABLE_TS}
    return m


def write_release_build_zip(build_dir: str|Path, zip_path: str|Path|None=None)->dict:
    b=Path(build_dir)
    if not b.exists() or not b.is_dir(): raise ValueError('build_dir must exist')
    zp=Path(zip_path) if zip_path else b/'release_build.zip'
    m=create_release_build_zip_manifest(b,zp)
    comp=ZIP_DEFLATED
    try: _=ZIP_DEFLATED
    except Exception: comp=ZIP_STORED
    with ZipFile(zp,'w',compression=comp,compresslevel=9) as zf:
        for f in m['files']:
            rel=f['path']; src=b/rel
            zi=ZipInfo(rel,date_time=_STABLE_DT); zi.compress_type=comp
            zf.writestr(zi,src.read_bytes())
    m['receipt']['zip_file_sha256']=file_sha256(zp)
    (b/'release_build_zip_manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True),encoding='utf-8')
    (b/'release_build_zip_receipt.json').write_text(json.dumps(m['receipt'],indent=2,sort_keys=True),encoding='utf-8')
    (b/'RELEASE_BUILD_ZIP_SUMMARY.md').write_text(f"# Release Build ZIP Summary\n\n- zip: {zp.name}\n- file_count: {m['file_count']}\n- release_build_zip_hash: {m['receipt']['release_build_zip_hash']}\n- zip_file_sha256: {m['receipt']['zip_file_sha256']}\n",encoding='utf-8')
    return m


def validate_release_build_zip_manifest(manifest: dict)->list[str]:
    e=[]
    if manifest.get('schema')!='waveforge.release_build_zip_manifest.v2_alpha': e.append('schema invalid')
    p=manifest.get('zip_policy',{})
    for k,v in {'deterministic_zip':True,'stable_timestamps':True,'sorted_entries':True,'relative_paths_only':True,'external_calls_allowed':False,'subprocess_allowed':False,'network_allowed':False,'hosting':False,'browser_automation':False,'powerpoint':False,'video_rendering':False,'muxing':False}.items():
        if p.get(k) is not v: e.append(f'{k} must be {v}')
    if not manifest.get('outputs',{}).get('zip'): e.append('outputs.zip required')
    if not manifest.get('receipt',{}).get('release_build_zip_hash'): e.append('receipt.release_build_zip_hash required')
    present={f.get('path') for f in manifest.get('files',[])}
    for req in ['release_build_manifest.json','release_deck/release_deck.zip']:
        if req not in present: e.append(f'{req} must be present')
    return e


def assert_valid_release_build_zip_manifest(manifest: dict)->None:
    e=validate_release_build_zip_manifest(manifest)
    if e: raise ValueError('Invalid release build zip manifest: '+'; '.join(e))


def read_release_build_zip_info(zip_path: str|Path)->dict:
    zp=Path(zip_path)
    if not zp.exists():
        return {'exists':False,'size_bytes':0,'file_count':0,'contains_release_build_manifest':False,'contains_gallery_manifest':False,'contains_collection_manifest':False,'contains_release_deck_zip':False,'sha256':''}
    with ZipFile(zp,'r') as zf: names=zf.namelist()
    return {'exists':True,'size_bytes':zp.stat().st_size,'file_count':len(names),'contains_release_build_manifest':'release_build_manifest.json' in names,'contains_gallery_manifest':'gallery/gallery_manifest.json' in names,'contains_collection_manifest':'collection/collection_manifest.json' in names,'contains_release_deck_zip':'release_deck/release_deck.zip' in names,'sha256':file_sha256(zp)}
