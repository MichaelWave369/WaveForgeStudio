from __future__ import annotations

import json
from pathlib import Path

from .hashing import canonical_json, sha256_digest
from .release_build_verification import verify_release_build, write_release_build_verification

_STABLE_TS='1979-03-06T03:06:09Z'


def create_release_certificate(build_dir: str | Path, require_passed: bool = False) -> dict:
    b=Path(build_dir)
    rbp=b/'release_build_manifest.json'; vfp=b/'release_build_verification.json'; zmp=b/'release_build_zip_manifest.json'
    rb=json.loads(rbp.read_text(encoding='utf-8')) if rbp.exists() else {}
    vf=json.loads(vfp.read_text(encoding='utf-8')) if vfp.exists() else verify_release_build(b,strict=False)
    zm=json.loads(zmp.read_text(encoding='utf-8')) if zmp.exists() else {}
    passed=bool(vf.get('summary',{}).get('passed',False))
    warnings=vf.get('summary',{}).get('warning_count',0)
    status='not_certified' if not passed else ('certified_with_warnings' if warnings>0 else 'certified')
    c={
      'schema':'waveforge.release_certificate.v2_alpha','project':'WaveForgeStudio','version':'2.5-alpha',
      'title':rb.get('title','Unknown Release'),'certificate_status':status,'require_passed':require_passed,
      'source':{'build_root':'.','release_build_manifest':'release_build_manifest.json','release_build_verification':'release_build_verification.json','release_build_zip_manifest':'release_build_zip_manifest.json'},
      'release':{'discovered_runs':rb.get('counts',{}).get('discovered_runs',0),'selected_runs':rb.get('counts',{}).get('selected_runs',0),'deck_cards':rb.get('counts',{}).get('deck_cards',0),'zip_count':rb.get('counts',{}).get('zip_count',0),'missing_zip_count':rb.get('counts',{}).get('missing_zip_count',0)},
      'hashes':{'release_build_hash':rb.get('receipt',{}).get('release_build_hash'),'verification_hash':vf.get('receipt',{}).get('verification_hash'),'release_build_zip_hash':zm.get('receipt',{}).get('release_build_zip_hash') if zm else None,'release_build_zip_sha256':zm.get('receipt',{}).get('zip_file_sha256') if zm else None},
      'verification':{'passed':passed,'strict':bool(vf.get('strict',False)),'check_count':vf.get('summary',{}).get('check_count',0),'error_count':vf.get('summary',{}).get('error_count',0),'warning_count':warnings},
      'limitations':['Deterministic certificate only; not cryptographically signed.','Local verification only; no external transparency log.','No legal certification is implied.'],
      'outputs':{'certificate':'release_certificate.json','receipt':'release_certificate_receipt.json','markdown':'RELEASE_CERTIFICATE.md'}
    }
    c['receipt']={'schema':'waveforge.release_certificate_receipt.v2_alpha','release_certificate_hash':sha256_digest(json.loads(canonical_json(c))),'created_at':_STABLE_TS}
    return c


def write_release_certificate(build_dir: str | Path, require_passed: bool = False) -> dict:
    b=Path(build_dir); b.mkdir(parents=True,exist_ok=True)
    if not (b/'release_build_verification.json').exists():
        write_release_build_verification(b,strict=False)
    c=create_release_certificate(b,require_passed=require_passed)
    (b/'release_certificate.json').write_text(json.dumps(c,indent=2,sort_keys=True),encoding='utf-8')
    (b/'release_certificate_receipt.json').write_text(json.dumps(c['receipt'],indent=2,sort_keys=True),encoding='utf-8')
    lim='\n'.join([f"- {x}" for x in c['limitations']])
    (b/'RELEASE_CERTIFICATE.md').write_text(f"# WaveForgeStudio Release Certificate\n\n- release_title: {c['title']}\n- certificate_status: {c['certificate_status']}\n- require_passed: {c['require_passed']}\n- verification_passed: {c['verification']['passed']}\n- strict: {c['verification']['strict']}\n- discovered_runs: {c['release']['discovered_runs']}\n- selected_runs: {c['release']['selected_runs']}\n- deck_cards: {c['release']['deck_cards']}\n- zip_count: {c['release']['zip_count']}\n- missing_zip_count: {c['release']['missing_zip_count']}\n- release_build_hash: {c['hashes']['release_build_hash']}\n- verification_hash: {c['hashes']['verification_hash']}\n- release_build_zip_sha256: {c['hashes']['release_build_zip_sha256']}\n- release_certificate_hash: {c['receipt']['release_certificate_hash']}\n\n## Limitations\n{lim}\n\nDeterministic certificate only — not cryptographically signed.\n",encoding='utf-8')
    return c


def validate_release_certificate(certificate: dict) -> list[str]:
    e=[]
    if certificate.get('schema')!='waveforge.release_certificate.v2_alpha': e.append('schema invalid')
    if certificate.get('certificate_status') not in {'certified','certified_with_warnings','not_certified'}: e.append('certificate_status invalid')
    for k in ['source','release','hashes','verification']:
        if not isinstance(certificate.get(k),dict): e.append(f'{k} required')
    if not isinstance(certificate.get('limitations'),list): e.append('limitations list required')
    if not certificate.get('outputs',{}).get('certificate'): e.append('outputs.certificate required')
    if not certificate.get('receipt',{}).get('release_certificate_hash'): e.append('receipt.release_certificate_hash required')
    if certificate.get('certificate_status')=='certified' and not certificate.get('verification',{}).get('passed'): e.append('certified requires verification passed')
    if certificate.get('certificate_status')=='not_certified' and certificate.get('verification',{}).get('passed'): e.append('not_certified requires verification failed')
    return e


def assert_valid_release_certificate(certificate: dict) -> None:
    e=validate_release_certificate(certificate)
    if e: raise ValueError('Invalid release certificate: '+'; '.join(e))


def read_release_certificate_info(build_dir: str | Path) -> dict:
    b=Path(build_dir)
    cp=b/'release_certificate.json'; rp=b/'release_certificate_receipt.json'; mp=b/'RELEASE_CERTIFICATE.md'
    c=json.loads(cp.read_text(encoding='utf-8')) if cp.exists() else {}
    txt=mp.read_text(encoding='utf-8',errors='ignore').lower() if mp.exists() else ''
    return {'exists':b.exists(),'certificate_exists':cp.exists(),'receipt_exists':rp.exists(),'markdown_exists':mp.exists(),'certificate_status':c.get('certificate_status') if c else None,'verification_passed':c.get('verification',{}).get('passed') if c else None,'contains_waveforge':'waveforge' in txt}
