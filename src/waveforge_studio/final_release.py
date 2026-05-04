from __future__ import annotations

import json
from pathlib import Path

from .hashing import canonical_json, sha256_digest
from .release_build import create_release_build_manifest, write_release_build
from .release_build_zip import write_release_build_zip
from .release_build_verification import write_release_build_verification
from .release_certificate import write_release_certificate
from .certificate_bundle import write_certificate_bundle
from .certificate_bundle_zip import write_certificate_bundle_zip
from .release_build_index import write_release_build_index

_STABLE_TS='1979-03-06T03:06:09Z'


def create_final_release_manifest(runs_root: str | Path, final_dir: str | Path | None = None, title: str = 'WaveForgeStudio Final Release', description: str = '', include_tags: list[str] | None = None, exclude_tags: list[str] | None = None, include_run_paths: list[str] | None = None) -> dict:
    root=Path(runs_root); fd=Path(final_dir) if final_dir else root/'final_release'
    rb=create_release_build_manifest(root,fd,title=title,description=description,include_tags=include_tags,exclude_tags=exclude_tags,include_run_paths=include_run_paths)
    m={'schema':'waveforge.final_release_manifest.v2_alpha','project':'WaveForgeStudio','version':'2.9-alpha','title':title,'description':description,'runs_root':'.','final_root':fd.name,
       'selection':rb.get('selection',{}),
       'final_policy':{'final_release_build':True,'generates_new_runs':False,'renders_media':False,'copies_full_runs':False,'external_calls_allowed':False,'subprocess_allowed':False,'network_allowed':False,'hosting':False,'browser_automation':False,'powerpoint':False,'video_rendering':False,'muxing':False,'cryptographic_signature':False,'legal_certificate':False},
       'stages':{'release_build':{'path':f'{fd.name}/release_build_manifest.json','status':'planned','hash':None},'release_build_zip':{'path':f'{fd.name}/release_build_zip_manifest.json','status':'planned','hash':None,'zip_sha256':None},'verification':{'path':f'{fd.name}/release_build_verification.json','status':'planned','hash':None,'passed':None},'certificate':{'path':f'{fd.name}/release_certificate.json','status':'planned','hash':None,'certificate_status':None},'certificate_bundle':{'path':f'{fd.name}/certificate_bundle/certificate_bundle_manifest.json','status':'planned','hash':None},'certificate_bundle_zip':{'path':f'{fd.name}/certificate_bundle/certificate_bundle_zip_manifest.json','status':'planned','hash':None,'zip_sha256':None},'index':{'path':f'{fd.name}/release_build_index_manifest.json','status':'planned','hash':None}},
       'counts':{'discovered_runs':rb.get('counts',{}).get('discovered_runs',0),'selected_runs':rb.get('counts',{}).get('selected_runs',0),'zip_count':rb.get('counts',{}).get('zip_count',0),'missing_zip_count':rb.get('counts',{}).get('missing_zip_count',0),'deck_cards':rb.get('counts',{}).get('deck_cards',0),'verification_checks':0,'verification_errors':0,'verification_warnings':0},
       'outputs':{'index':f'{fd.name}/index.html','release_build_zip':f'{fd.name}/release_build.zip','certificate_bundle_zip':f'{fd.name}/certificate_bundle/certificate_bundle.zip','manifest':f'{fd.name}/final_release_manifest.json','receipt':f'{fd.name}/final_release_receipt.json','summary':f'{fd.name}/FINAL_RELEASE_SUMMARY.md'}}
    m['receipt']={'schema':'waveforge.final_release_receipt.v2_alpha','final_release_hash':sha256_digest(json.loads(canonical_json(m))),'created_at':_STABLE_TS}
    return m


def write_final_release(runs_root: str | Path, final_dir: str | Path | None = None, title: str = 'WaveForgeStudio Final Release', description: str = '', include_tags: list[str] | None = None, exclude_tags: list[str] | None = None, include_run_paths: list[str] | None = None) -> dict:
    root=Path(runs_root); fd=Path(final_dir) if final_dir else root/'final_release'; fd.mkdir(parents=True,exist_ok=True)
    rb=write_release_build(root,fd,title=title,description=description,include_tags=include_tags,exclude_tags=exclude_tags,include_run_paths=include_run_paths)
    rbz=write_release_build_zip(fd)
    v=write_release_build_verification(fd,strict=True)
    c=write_release_certificate(fd,require_passed=True)
    cb=write_certificate_bundle(fd)
    cbz=write_certificate_bundle_zip(fd/'certificate_bundle')
    idx=write_release_build_index(fd)
    m=create_final_release_manifest(root,fd,title,description,include_tags,exclude_tags,include_run_paths)
    m['stages']['release_build'].update({'status':'completed','hash':rb['receipt']['release_build_hash']})
    m['stages']['release_build_zip'].update({'status':'completed','hash':rbz['receipt']['release_build_zip_hash'],'zip_sha256':rbz['receipt']['zip_file_sha256']})
    m['stages']['verification'].update({'status':'completed','hash':v['receipt']['verification_hash'],'passed':v['summary']['passed']})
    m['stages']['certificate'].update({'status':'completed','hash':c['receipt']['release_certificate_hash'],'certificate_status':c['certificate_status']})
    m['stages']['certificate_bundle'].update({'status':'completed','hash':cb['receipt']['certificate_bundle_hash']})
    m['stages']['certificate_bundle_zip'].update({'status':'completed','hash':cbz['receipt']['certificate_bundle_zip_hash'],'zip_sha256':cbz['receipt']['zip_file_sha256']})
    m['stages']['index'].update({'status':'completed','hash':idx['receipt']['release_build_index_hash']})
    m['counts'].update({'discovered_runs':rb['counts']['discovered_runs'],'selected_runs':rb['counts']['selected_runs'],'zip_count':rb['counts']['zip_count'],'missing_zip_count':rb['counts']['missing_zip_count'],'deck_cards':rb['counts']['deck_cards'],'verification_checks':v['summary']['check_count'],'verification_errors':v['summary']['error_count'],'verification_warnings':v['summary']['warning_count']})
    m['receipt']={'schema':'waveforge.final_release_receipt.v2_alpha','final_release_hash':sha256_digest(json.loads(canonical_json({k:v for k,v in m.items() if k!='receipt'}))),'created_at':_STABLE_TS}
    (fd/'final_release_manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True),encoding='utf-8')
    (fd/'final_release_receipt.json').write_text(json.dumps(m['receipt'],indent=2,sort_keys=True),encoding='utf-8')
    (fd/'FINAL_RELEASE_SUMMARY.md').write_text(f"# WaveForgeStudio Final Release Summary\n\n- title: {title}\n- description: {description}\n- runs_root: {root}\n- final_root: {fd}\n- include_tags: {include_tags or []}\n- exclude_tags: {exclude_tags or []}\n- include_run_paths: {include_run_paths or []}\n- stages: {m['stages']}\n- counts: {m['counts']}\n- release_build.zip: {m['outputs']['release_build_zip']}\n- certificate_bundle.zip: {m['outputs']['certificate_bundle_zip']}\n- verification_passed: {m['stages']['verification']['passed']}\n- certificate_status: {m['stages']['certificate']['certificate_status']}\n- final_release_hash: {m['receipt']['final_release_hash']}\n\nFinal release build only — no new runs or media are rendered.\n",encoding='utf-8')
    return m


def validate_final_release_manifest(manifest: dict) -> list[str]:
    e=[]
    if manifest.get('schema')!='waveforge.final_release_manifest.v2_alpha': e.append('schema invalid')
    p=manifest.get('final_policy',{})
    for k,v in {'final_release_build':True,'generates_new_runs':False,'renders_media':False,'copies_full_runs':False,'external_calls_allowed':False,'subprocess_allowed':False,'network_allowed':False,'hosting':False,'browser_automation':False,'powerpoint':False,'video_rendering':False,'muxing':False,'cryptographic_signature':False,'legal_certificate':False}.items():
        if p.get(k) is not v: e.append(f'{k} must be {v}')
    if not manifest.get('outputs',{}).get('manifest'): e.append('outputs.manifest required')
    if not manifest.get('outputs',{}).get('index'): e.append('outputs.index required')
    if not manifest.get('receipt',{}).get('final_release_hash'): e.append('receipt.final_release_hash required')
    s=manifest.get('stages',{})
    for k in ['release_build','release_build_zip','verification','certificate','certificate_bundle','certificate_bundle_zip','index']:
        if k not in s: e.append(f'{k} stage required')
    c=manifest.get('counts',{})
    if c.get('discovered_runs',0)<c.get('selected_runs',0): e.append('selected_runs cannot exceed discovered_runs')
    return e


def assert_valid_final_release_manifest(manifest: dict) -> None:
    e=validate_final_release_manifest(manifest)
    if e: raise ValueError('Invalid final release manifest: '+'; '.join(e))


def read_final_release_info(final_dir: str | Path) -> dict:
    f=Path(final_dir)
    mp=f/'final_release_manifest.json'; rp=f/'final_release_receipt.json'; sp=f/'FINAL_RELEASE_SUMMARY.md'; ip=f/'index.html'
    m=json.loads(mp.read_text(encoding='utf-8')) if mp.exists() else {}
    txt=sp.read_text(encoding='utf-8',errors='ignore').lower() if sp.exists() else ''
    return {'exists':f.exists(),'manifest_exists':mp.exists(),'receipt_exists':rp.exists(),'summary_exists':sp.exists(),'index_exists':ip.exists(),'release_build_zip_exists':(f/'release_build.zip').exists(),'certificate_bundle_zip_exists':(f/'certificate_bundle/certificate_bundle.zip').exists(),'verification_passed':m.get('stages',{}).get('verification',{}).get('passed') if m else None,'certificate_status':m.get('stages',{}).get('certificate',{}).get('certificate_status') if m else None,'selected_runs':m.get('counts',{}).get('selected_runs') if m else None,'contains_waveforge':'waveforge' in txt}
