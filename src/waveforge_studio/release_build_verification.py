from __future__ import annotations

import json
from pathlib import Path

from .artifact_ledger import file_sha256
from .collection_export import validate_collection_export_manifest
from .demo_gallery import validate_gallery_manifest
from .gallery_collection import validate_gallery_collection_manifest
from .hashing import canonical_json, sha256_digest
from .release_build import validate_release_build_manifest
from .release_build_zip import validate_release_build_zip_manifest
from .release_deck import validate_release_deck_manifest
from .release_deck_zip import validate_release_deck_zip_manifest

_STABLE_TS='1979-03-06T03:06:09Z'


def _is_abs(v: str | None) -> bool:
    return bool(v) and Path(v).is_absolute()


def verify_release_build(build_dir: str | Path, strict: bool = False) -> dict:
    b=Path(build_dir)
    checks=[]
    def add(i,c,s,se,m,p=None): checks.append({'id':i,'category':c,'status':s,'severity':se,'message':m,'path':p})
    def load(rel):
        p=b/rel
        return json.loads(p.read_text(encoding='utf-8')) if p.exists() else None

    rb=load('release_build_manifest.json'); gr=load('gallery/gallery_manifest.json'); co=load('collection/collection_manifest.json'); ce=load('collection_export/collection_export_manifest.json'); rd=load('release_deck/release_deck_manifest.json'); rdz=load('release_deck/release_deck_zip_manifest.json'); rbz=load('release_build_zip_manifest.json')
    recs={
      'release_build_receipt':load('release_build_receipt.json'),'gallery_receipt':load('gallery/gallery_receipt.json'),'collection_receipt':load('collection/collection_receipt.json'),'collection_export_receipt':load('collection_export/collection_export_receipt.json'),'release_deck_receipt':load('release_deck/release_deck_receipt.json'),'release_deck_zip_receipt':load('release_deck/release_deck_zip_receipt.json'),'release_build_zip_receipt':load('release_build_zip_receipt.json')
    }
    required=['release_build_manifest.json','release_build_receipt.json','gallery/gallery_manifest.json','collection/collection_manifest.json','collection_export/collection_export_manifest.json','release_deck/release_deck_manifest.json','release_deck/release_deck.zip','release_deck/release_deck_zip_manifest.json']
    for i,rel in enumerate(required,1):
        p=b/rel; ok=p.exists(); check_rel=rel.replace('/','_').replace('.','_'); add(f"check_{i:03d}_present_{check_rel}", 'presence', 'passed' if ok else 'failed', 'error', f'{rel} is '+('present.' if ok else 'missing.'), rel)

    if rb is not None:
        e=validate_release_build_manifest(rb); add('check_100_release_build_manifest_valid','validation','passed' if not e else 'failed','error','release_build_manifest validation '+('passed.' if not e else '; '.join(e)),'release_build_manifest.json')
    if gr is not None:
        e=validate_gallery_manifest(gr); add('check_101_gallery_manifest_valid','validation','passed' if not e else 'failed','error','gallery_manifest validation '+('passed.' if not e else '; '.join(e)),'gallery/gallery_manifest.json')
    if co is not None:
        e=validate_gallery_collection_manifest(co); add('check_102_collection_manifest_valid','validation','passed' if not e else 'failed','error','collection_manifest validation '+('passed.' if not e else '; '.join(e)),'collection/collection_manifest.json')
    if ce is not None:
        e=validate_collection_export_manifest(ce); add('check_103_collection_export_manifest_valid','validation','passed' if not e else 'failed','error','collection_export_manifest validation '+('passed.' if not e else '; '.join(e)),'collection_export/collection_export_manifest.json')
    if rd is not None:
        e=validate_release_deck_manifest(rd); add('check_104_release_deck_manifest_valid','validation','passed' if not e else 'failed','error','release_deck_manifest validation '+('passed.' if not e else '; '.join(e)),'release_deck/release_deck_manifest.json')
    if rdz is not None:
        e=validate_release_deck_zip_manifest(rdz); add('check_105_release_deck_zip_manifest_valid','validation','passed' if not e else 'failed','error','release_deck_zip_manifest validation '+('passed.' if not e else '; '.join(e)),'release_deck/release_deck_zip_manifest.json')
    if rbz is not None:
        e=validate_release_build_zip_manifest(rbz); add('check_106_release_build_zip_manifest_valid','validation','passed' if not e else 'failed','error','release_build_zip_manifest validation '+('passed.' if not e else '; '.join(e)),'release_build_zip_manifest.json')

    deck_zip=b/'release_deck/release_deck.zip'
    if deck_zip.exists() and recs['release_deck_zip_receipt']:
        actual=file_sha256(deck_zip); exp=recs['release_deck_zip_receipt'].get('zip_file_sha256')
        add('check_120_release_deck_zip_sha256','hash','passed' if actual==exp else 'failed','error','release_deck.zip sha256 '+('matched.' if actual==exp else 'mismatched.'),'release_deck/release_deck.zip')

    build_zip=b/'release_build.zip'
    rbzip_present=build_zip.exists(); rbz_manifest_present=rbz is not None
    if not rbzip_present and not rbz_manifest_present and not strict:
        add('check_121_release_build_zip_optional','presence','warning','warning','release_build.zip and release_build_zip_manifest.json are absent in non-strict mode.',None)
    elif not rbzip_present:
        add('check_121_release_build_zip_required','presence','failed','error','release_build.zip is missing.','release_build.zip')
    if strict and not rbz_manifest_present:
        add('check_122_release_build_zip_manifest_required','presence','failed','error','release_build_zip_manifest.json is required in strict mode.','release_build_zip_manifest.json')
    if build_zip.exists() and recs['release_build_zip_receipt']:
        actual=file_sha256(build_zip); exp=recs['release_build_zip_receipt'].get('zip_file_sha256')
        add('check_123_release_build_zip_sha256','hash','passed' if actual==exp else 'failed','error','release_build.zip sha256 '+('matched.' if actual==exp else 'mismatched.'),'release_build.zip')

    stages=['gallery','collection','collection_export','release_deck','release_deck_zip']
    stage_actual={
      'gallery': gr.get('receipt',{}).get('gallery_hash') if gr else None,
      'collection': co.get('receipt',{}).get('collection_hash') if co else None,
      'collection_export': ce.get('receipt',{}).get('collection_export_hash') if ce else None,
      'release_deck': rd.get('receipt',{}).get('release_deck_hash') if rd else None,
      'release_deck_zip': rdz.get('receipt',{}).get('release_deck_zip_hash') if rdz else None,
    }
    stage_hashes={}
    for s in stages:
        exp=(rb or {}).get('stages',{}).get(s,{}).get('hash') if rb else None; act=stage_actual[s]
        matched=(exp==act) if exp is not None and act is not None else None
        stage_hashes[s]={'expected':exp,'actual':act,'matched':matched}
        sev='error' if strict else 'warning'
        if matched is False: add(f'check_14{stages.index(s)}_{s}_stage_hash','consistency','failed',sev,f'{s} stage hash mismatch.',None)
        elif matched is True: add(f'check_14{stages.index(s)}_{s}_stage_hash','consistency','passed','info',f'{s} stage hash matched.',None)
        elif strict: add(f'check_14{stages.index(s)}_{s}_stage_hash','consistency','failed','error',f'{s} stage hash cannot be confirmed in strict mode.',None)
        else: add(f'check_14{stages.index(s)}_{s}_stage_hash','consistency','warning','warning',f'{s} stage hash not fully confirmable.',None)

    known=[rb,gr,co,ce,rd,rdz,rbz]
    abs_bad=False
    for obj in known:
        if not isinstance(obj,dict): continue
        stack=[obj]
        while stack:
            cur=stack.pop()
            if isinstance(cur,dict): stack.extend(cur.values())
            elif isinstance(cur,list): stack.extend(cur)
            elif isinstance(cur,str) and _is_abs(cur): abs_bad=True
    add('check_160_no_absolute_paths','path_safety','passed' if not abs_bad else 'failed','error','No absolute paths detected.' if not abs_bad else 'Absolute path values detected in manifests.',None)

    checks=sorted(checks,key=lambda x:x['id'])
    errors=sum(1 for c in checks if c['severity']=='error' and c['status']=='failed')
    warnings=sum(1 for c in checks if c['status']=='warning' or c['severity']=='warning')

    artifacts={
      'release_build_manifest':{'path':'release_build_manifest.json','present':(b/'release_build_manifest.json').exists(),'hash':file_sha256(b/'release_build_manifest.json') if (b/'release_build_manifest.json').exists() else None},
      'release_build_zip':{'path':'release_build.zip','present':build_zip.exists(),'sha256':file_sha256(build_zip) if build_zip.exists() else None},
    }
    r={'schema':'waveforge.release_build_verification.v2_alpha','project':'WaveForgeStudio','version':'2.4-alpha','build_root':'.','strict':strict,
       'summary':{'passed':errors==0,'error_count':errors,'warning_count':warnings,'check_count':len(checks)},'checks':checks,'artifacts':artifacts,'stage_hashes':stage_hashes,
       'outputs':{'report':'release_build_verification.json','receipt':'release_build_verification_receipt.json','summary':'RELEASE_BUILD_VERIFICATION.md'}}
    r['receipt']={'schema':'waveforge.release_build_verification_receipt.v2_alpha','verification_hash':sha256_digest(json.loads(canonical_json(r))),'created_at':_STABLE_TS}
    return r


def write_release_build_verification(build_dir: str | Path, strict: bool = False) -> dict:
    b=Path(build_dir); b.mkdir(parents=True,exist_ok=True)
    r=verify_release_build(b,strict)
    (b/'release_build_verification.json').write_text(json.dumps(r,indent=2,sort_keys=True),encoding='utf-8')
    (b/'release_build_verification_receipt.json').write_text(json.dumps(r['receipt'],indent=2,sort_keys=True),encoding='utf-8')
    stage='\n'.join([f"| {k} | {v['expected']} | {v['actual']} | {v['matched']} |" for k,v in r['stage_hashes'].items()])
    art='\n'.join([f"| {k} | {v.get('path')} | {v.get('present')} | {v.get('sha256') or v.get('hash')} |" for k,v in r['artifacts'].items()])
    failed='\n'.join([f"- {c['id']}: {c['message']}" for c in r['checks'] if c['status']=='failed']) or '- none'
    warn='\n'.join([f"- {c['id']}: {c['message']}" for c in r['checks'] if c['status']=='warning']) or '- none'
    (b/'RELEASE_BUILD_VERIFICATION.md').write_text(f"# Release Build Verification\n\n- strict: {r['strict']}\n- passed: {r['summary']['passed']}\n- check_count: {r['summary']['check_count']}\n- error_count: {r['summary']['error_count']}\n- warning_count: {r['summary']['warning_count']}\n\n## Stage Hashes\n| stage | expected | actual | matched |\n|---|---|---|---|\n{stage}\n\n## Artifacts\n| artifact | path | present | digest |\n|---|---|---|---|\n{art}\n\n## Failed Checks\n{failed}\n\n## Warnings\n{warn}\n\n- verification_hash: {r['receipt']['verification_hash']}\n\nLocal verification only — no external services or runtime execution.\n",encoding='utf-8')
    return r


def validate_release_build_verification(report: dict) -> list[str]:
    e=[]
    if report.get('schema')!='waveforge.release_build_verification.v2_alpha': e.append('schema invalid')
    if not isinstance(report.get('summary'),dict): e.append('summary required')
    if not isinstance(report.get('checks'),list): e.append('checks required')
    if not report.get('receipt',{}).get('verification_hash'): e.append('receipt.verification_hash required')
    if not report.get('outputs',{}).get('report'): e.append('outputs.report required')
    s=report.get('summary',{}); c=report.get('checks',[])
    if s.get('check_count')!=len(c): e.append('summary.check_count mismatch')
    errs=sum(1 for x in c if x.get('severity')=='error' and x.get('status')=='failed')
    warns=sum(1 for x in c if x.get('status')=='warning' or x.get('severity')=='warning')
    if s.get('error_count')!=errs: e.append('summary.error_count mismatch')
    if s.get('warning_count')!=warns: e.append('summary.warning_count mismatch')
    return e


def assert_valid_release_build_verification(report: dict) -> None:
    e=validate_release_build_verification(report)
    if e: raise ValueError('Invalid release build verification: '+'; '.join(e))


def read_release_build_verification_info(build_dir: str | Path) -> dict:
    b=Path(build_dir)
    rp=b/'release_build_verification.json'; rc=b/'release_build_verification_receipt.json'; sm=b/'RELEASE_BUILD_VERIFICATION.md'
    d=json.loads(rp.read_text(encoding='utf-8')) if rp.exists() else {}
    txt=sm.read_text(encoding='utf-8',errors='ignore').lower() if sm.exists() else ''
    return {'exists':b.exists(),'report_exists':rp.exists(),'receipt_exists':rc.exists(),'summary_exists':sm.exists(),'passed':d.get('summary',{}).get('passed') if d else None,'check_count':d.get('summary',{}).get('check_count') if d else None,'error_count':d.get('summary',{}).get('error_count') if d else None,'warning_count':d.get('summary',{}).get('warning_count') if d else None,'contains_waveforge':'waveforge' in txt}
