from __future__ import annotations

import json, shutil
from pathlib import Path

from .artifact_ledger import file_sha256
from .hashing import canonical_json, sha256_digest
from .release_certificate import write_release_certificate

_STABLE_TS='1979-03-06T03:06:09Z'


def create_certificate_bundle_manifest(build_dir: str | Path, bundle_dir: str | Path | None = None, include_zip_file: bool = False) -> dict:
    b=Path(build_dir); bd=Path(bundle_dir) if bundle_dir else b/'certificate_bundle'
    req=['release_certificate.json','release_certificate_receipt.json','RELEASE_CERTIFICATE.md','release_build_verification.json','release_build_verification_receipt.json','release_build_manifest.json','release_build_receipt.json']
    opt=['RELEASE_BUILD_VERIFICATION.md','RELEASE_BUILD_SUMMARY.md','release_build_zip_manifest.json','release_build_zip_receipt.json','RELEASE_BUILD_ZIP_SUMMARY.md','release_deck/release_deck_zip_manifest.json','release_deck/release_deck_zip_receipt.json','release_deck/RELEASE_DECK_ZIP_SUMMARY.md']
    if include_zip_file: opt.append('release_build.zip')
    ev=[]
    for p in req+opt:
        src=b/p; t=Path(p).name if p.startswith('release_deck/') else p
        ev.append({'source':p,'target':t,'present':src.exists(),'required':p in req,'sha256':file_sha256(src) if src.exists() else None})
    ev=sorted(ev,key=lambda x:x['target'])
    req_m=sorted([x['source'] for x in ev if x['required'] and not x['present']])
    opt_m=sorted([x['source'] for x in ev if (not x['required']) and not x['present']])
    cert=json.loads((b/'release_certificate.json').read_text(encoding='utf-8')) if (b/'release_certificate.json').exists() else {}
    ver=json.loads((b/'release_build_verification.json').read_text(encoding='utf-8')) if (b/'release_build_verification.json').exists() else {}
    rb=json.loads((b/'release_build_manifest.json').read_text(encoding='utf-8')) if (b/'release_build_manifest.json').exists() else {}
    m={'schema':'waveforge.certificate_bundle_manifest.v2_alpha','project':'WaveForgeStudio','version':'2.6-alpha','build_root':'.','bundle_root':bd.name,'include_zip_file':include_zip_file,
       'bundle_policy':{'proof_metadata_only':True,'copies_release_zip_by_default':False,'copies_full_runs':False,'copies_preview_zips':False,'external_calls_allowed':False,'subprocess_allowed':False,'network_allowed':False,'hosting':False,'browser_automation':False,'cryptographic_signature':False,'legal_certificate':False},
       'evidence':ev,'required_missing':req_m,'optional_missing':opt_m,'evidence_count':len(ev),'required_count':len(req),'optional_count':len(ev)-len(req),
       'certificate_status':cert.get('certificate_status'),'verification_passed':ver.get('summary',{}).get('passed') if ver else cert.get('verification',{}).get('passed'),
       'release_build_hash':rb.get('receipt',{}).get('release_build_hash'),'verification_hash':ver.get('receipt',{}).get('verification_hash') if ver else cert.get('hashes',{}).get('verification_hash'),
       'certificate_hash':cert.get('receipt',{}).get('release_certificate_hash'),'release_build_zip_sha256':cert.get('hashes',{}).get('release_build_zip_sha256'),
       'outputs':{'bundle_manifest':f'{bd.name}/certificate_bundle_manifest.json','bundle_receipt':f'{bd.name}/certificate_bundle_receipt.json','summary':f'{bd.name}/CERTIFICATE_BUNDLE_SUMMARY.md'}}
    m['receipt']={'schema':'waveforge.certificate_bundle_receipt.v2_alpha','certificate_bundle_hash':sha256_digest(json.loads(canonical_json(m))),'created_at':_STABLE_TS}
    return m


def write_certificate_bundle(build_dir: str | Path, bundle_dir: str | Path | None = None, include_zip_file: bool = False) -> dict:
    b=Path(build_dir); bd=Path(bundle_dir) if bundle_dir else b/'certificate_bundle'
    if not (b/'release_certificate.json').exists(): write_release_certificate(b)
    m=create_certificate_bundle_manifest(b,bd,include_zip_file=include_zip_file)
    bd.mkdir(parents=True,exist_ok=True)
    for e in m['evidence']:
        if not e['present']: continue
        src=b/e['source']; dst=bd/e['target']; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
    (bd/'certificate_bundle_manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True),encoding='utf-8')
    (bd/'certificate_bundle_receipt.json').write_text(json.dumps(m['receipt'],indent=2,sort_keys=True),encoding='utf-8')
    rows='\n'.join([f"| {e['target']} | {e['present']} | {e['required']} |" for e in m['evidence']])
    (bd/'CERTIFICATE_BUNDLE_SUMMARY.md').write_text(f"# WaveForgeStudio Certificate Bundle\n\n- certificate_status: {m['certificate_status']}\n- verification_passed: {m['verification_passed']}\n- release_build_hash: {m['release_build_hash']}\n- verification_hash: {m['verification_hash']}\n- certificate_hash: {m['certificate_hash']}\n- release_build_zip_sha256: {m['release_build_zip_sha256']}\n- include_zip_file: {include_zip_file}\n\n## Evidence\n| target | present | required |\n|---|---|---|\n{rows}\n\n## Required Missing\n{m['required_missing']}\n\n## Optional Missing\n{m['optional_missing']}\n\n- metadata proof bundle only\n- not cryptographically signed\n- not legal certification\n- no external transparency log\n",encoding='utf-8')
    return m


def validate_certificate_bundle_manifest(manifest: dict) -> list[str]:
    e=[]
    if manifest.get('schema')!='waveforge.certificate_bundle_manifest.v2_alpha': e.append('schema invalid')
    p=manifest.get('bundle_policy',{})
    for k,v in {'proof_metadata_only':True,'copies_full_runs':False,'copies_preview_zips':False,'external_calls_allowed':False,'subprocess_allowed':False,'network_allowed':False,'hosting':False,'browser_automation':False,'cryptographic_signature':False,'legal_certificate':False}.items():
        if p.get(k) is not v: e.append(f'{k} must be {v}')
    if not isinstance(manifest.get('evidence'),list): e.append('evidence required')
    if not manifest.get('receipt',{}).get('certificate_bundle_hash'): e.append('receipt.certificate_bundle_hash required')
    if not manifest.get('outputs',{}).get('bundle_manifest'): e.append('outputs.bundle_manifest required')
    if manifest.get('required_missing'): e.append('required_missing must be empty')
    if manifest.get('evidence_count')!=len(manifest.get('evidence',[])): e.append('evidence_count mismatch')
    return e


def assert_valid_certificate_bundle_manifest(manifest: dict) -> None:
    e=validate_certificate_bundle_manifest(manifest)
    if e: raise ValueError('Invalid certificate bundle manifest: '+'; '.join(e))


def read_certificate_bundle_info(bundle_dir: str | Path) -> dict:
    b=Path(bundle_dir)
    mp=b/'certificate_bundle_manifest.json'; rp=b/'certificate_bundle_receipt.json'; sp=b/'CERTIFICATE_BUNDLE_SUMMARY.md'
    m=json.loads(mp.read_text(encoding='utf-8')) if mp.exists() else {}
    txt=sp.read_text(encoding='utf-8',errors='ignore').lower() if sp.exists() else ''
    return {'exists':b.exists(),'manifest_exists':mp.exists(),'receipt_exists':rp.exists(),'summary_exists':sp.exists(),'certificate_exists':(b/'release_certificate.json').exists(),'verification_exists':(b/'release_build_verification.json').exists(),'evidence_count':m.get('evidence_count'),'certificate_status':m.get('certificate_status'),'verification_passed':m.get('verification_passed'),'contains_waveforge':'waveforge' in txt}
