from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile, ZipInfo

from .artifact_ledger import file_sha256
from .hashing import canonical_json, sha256_digest

_STABLE_DT=(1980,1,1,0,0,0)
_STABLE_TS='1979-03-06T03:06:09Z'
_EXCLUDE={'certificate_bundle.zip','certificate_bundle_zip_manifest.json','certificate_bundle_zip_receipt.json','CERTIFICATE_BUNDLE_ZIP_SUMMARY.md'}


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


def create_certificate_bundle_zip_manifest(bundle_dir: str|Path, zip_path: str|Path|None=None)->dict:
    b=Path(bundle_dir); zp=Path(zip_path) if zip_path else b/'certificate_bundle.zip'
    files=_collect(b) if b.exists() else []
    paths={f['path'] for f in files}
    expected=['certificate_bundle_manifest.json','certificate_bundle_receipt.json','CERTIFICATE_BUNDLE_SUMMARY.md','release_certificate.json','release_certificate_receipt.json','RELEASE_CERTIFICATE.md','release_build_verification.json','release_build_verification_receipt.json','release_build_manifest.json']
    missing=[x for x in expected if x not in paths]
    m={'schema':'waveforge.certificate_bundle_zip_manifest.v2_alpha','project':'WaveForgeStudio','version':'2.7-alpha','bundle_root':'.','zip_output':zp.name,
       'zip_policy':{'deterministic_zip':True,'stable_timestamps':True,'sorted_entries':True,'relative_paths_only':True,'external_calls_allowed':False,'subprocess_allowed':False,'network_allowed':False,'hosting':False,'browser_automation':False,'cryptographic_signature':False,'legal_certificate':False,'video_rendering':False,'muxing':False},
       'files':files,'file_count':len(files),'missing':sorted(missing),
       'outputs':{'zip':zp.name,'zip_manifest':'certificate_bundle_zip_manifest.json','zip_receipt':'certificate_bundle_zip_receipt.json','summary':'CERTIFICATE_BUNDLE_ZIP_SUMMARY.md'}}
    m['receipt']={'schema':'waveforge.certificate_bundle_zip_receipt.v2_alpha','certificate_bundle_zip_hash':sha256_digest(json.loads(canonical_json(m))),'zip_file_sha256':None,'created_at':_STABLE_TS}
    return m


def write_certificate_bundle_zip(bundle_dir: str|Path, zip_path: str|Path|None=None)->dict:
    b=Path(bundle_dir)
    if not b.exists() or not b.is_dir(): raise ValueError('bundle_dir must exist')
    zp=Path(zip_path) if zip_path else b/'certificate_bundle.zip'
    m=create_certificate_bundle_zip_manifest(b,zp)
    comp=ZIP_DEFLATED
    try: _=ZIP_DEFLATED
    except Exception: comp=ZIP_STORED
    with ZipFile(zp,'w',compression=comp,compresslevel=9) as zf:
        for f in m['files']:
            rel=f['path']; src=b/rel
            zi=ZipInfo(rel,date_time=_STABLE_DT); zi.compress_type=comp
            zf.writestr(zi,src.read_bytes())
    m['receipt']['zip_file_sha256']=file_sha256(zp)
    (b/'certificate_bundle_zip_manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True),encoding='utf-8')
    (b/'certificate_bundle_zip_receipt.json').write_text(json.dumps(m['receipt'],indent=2,sort_keys=True),encoding='utf-8')
    (b/'CERTIFICATE_BUNDLE_ZIP_SUMMARY.md').write_text(f"# Certificate Bundle ZIP Summary\n\n- zip: {zp.name}\n- file_count: {m['file_count']}\n- certificate_bundle_zip_hash: {m['receipt']['certificate_bundle_zip_hash']}\n- zip_file_sha256: {m['receipt']['zip_file_sha256']}\n",encoding='utf-8')
    return m


def validate_certificate_bundle_zip_manifest(manifest: dict)->list[str]:
    e=[]
    if manifest.get('schema')!='waveforge.certificate_bundle_zip_manifest.v2_alpha': e.append('schema invalid')
    p=manifest.get('zip_policy',{})
    for k,v in {'deterministic_zip':True,'stable_timestamps':True,'sorted_entries':True,'relative_paths_only':True,'external_calls_allowed':False,'subprocess_allowed':False,'network_allowed':False,'hosting':False,'browser_automation':False,'cryptographic_signature':False,'legal_certificate':False,'video_rendering':False,'muxing':False}.items():
        if p.get(k) is not v: e.append(f'{k} must be {v}')
    if not manifest.get('outputs',{}).get('zip'): e.append('outputs.zip required')
    if not manifest.get('receipt',{}).get('certificate_bundle_zip_hash'): e.append('receipt.certificate_bundle_zip_hash required')
    present={f.get('path') for f in manifest.get('files',[])}
    for req in ['certificate_bundle_manifest.json','release_certificate.json','release_build_verification.json']:
        if req not in present: e.append(f'{req} must be present')
    return e


def assert_valid_certificate_bundle_zip_manifest(manifest: dict)->None:
    e=validate_certificate_bundle_zip_manifest(manifest)
    if e: raise ValueError('Invalid certificate bundle zip manifest: '+'; '.join(e))


def read_certificate_bundle_zip_info(zip_path: str|Path)->dict:
    zp=Path(zip_path)
    if not zp.exists(): return {'exists':False,'size_bytes':0,'file_count':0,'contains_certificate':False,'contains_verification':False,'contains_bundle_manifest':False,'sha256':''}
    with ZipFile(zp,'r') as zf: names=zf.namelist()
    return {'exists':True,'size_bytes':zp.stat().st_size,'file_count':len(names),'contains_certificate':'release_certificate.json' in names,'contains_verification':'release_build_verification.json' in names,'contains_bundle_manifest':'certificate_bundle_manifest.json' in names,'sha256':file_sha256(zp)}
