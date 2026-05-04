from __future__ import annotations

import json
from html import escape
from pathlib import Path

from .hashing import canonical_json, sha256_digest

_STABLE_TS='1979-03-06T03:06:09Z'


def _load(p: Path):
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else None


def create_release_build_index_manifest(build_dir: str | Path) -> dict:
    b=Path(build_dir)
    rb=_load(b/'release_build_manifest.json') or {}
    rbz=_load(b/'release_build_zip_manifest.json') or {}
    v=_load(b/'release_build_verification.json') or {}
    c=_load(b/'release_certificate.json') or {}
    cb=_load(b/'certificate_bundle/certificate_bundle_manifest.json') or {}
    cbz=_load(b/'certificate_bundle/certificate_bundle_zip_manifest.json') or {}
    g=_load(b/'gallery/gallery_manifest.json') or {}
    col=_load(b/'collection/collection_manifest.json') or {}
    ce=_load(b/'collection_export/collection_export_manifest.json') or {}
    rd=_load(b/'release_deck/release_deck_manifest.json') or {}
    rdz=_load(b/'release_deck/release_deck_zip_manifest.json') or {}

    links={
      'release_deck':{'label':'Open Release Deck','path':'release_deck/index.html','present':(b/'release_deck/index.html').exists()},
      'gallery':{'label':'Open Gallery','path':'gallery/index.html','present':(b/'gallery/index.html').exists()},
      'collection':{'label':'Open Collection','path':'collection/index.html','present':(b/'collection/index.html').exists()},
      'collection_export':{'label':'Open Collection Export','path':'collection_export/index.html','present':(b/'collection_export/index.html').exists()},
      'release_build_zip':{'label':'Download Release Build ZIP','path':'release_build.zip','present':(b/'release_build.zip').exists()},
      'certificate_bundle_zip':{'label':'Download Certificate Bundle ZIP','path':'certificate_bundle/certificate_bundle.zip','present':(b/'certificate_bundle/certificate_bundle.zip').exists()},
      'release_certificate':{'label':'View Release Certificate','path':'RELEASE_CERTIFICATE.md','present':(b/'RELEASE_CERTIFICATE.md').exists() or (b/'release_certificate.json').exists()},
      'verification_report':{'label':'View Verification Report','path':'RELEASE_BUILD_VERIFICATION.md','present':(b/'RELEASE_BUILD_VERIFICATION.md').exists() or (b/'release_build_verification.json').exists()},
    }
    m={'schema':'waveforge.release_build_index_manifest.v2_alpha','project':'WaveForgeStudio','version':'2.8-alpha','build_root':'.','title':rb.get('title','WaveForgeStudio Release Build'),
       'index_policy':{'local_launch_page':True,'copies_assets':False,'generates_new_runs':False,'renders_media':False,'external_calls_allowed':False,'subprocess_allowed':False,'network_allowed':False,'hosting':False,'browser_automation':False,'powerpoint':False,'video_rendering':False,'muxing':False},
       'status':{'release_build_present':(b/'release_build_manifest.json').exists(),'release_build_zip_present':links['release_build_zip']['present'],'verification_present':(b/'release_build_verification.json').exists(),'verification_passed':v.get('summary',{}).get('passed'),'certificate_present':(b/'release_certificate.json').exists(),'certificate_status':c.get('certificate_status'),'certificate_bundle_present':(b/'certificate_bundle/certificate_bundle_manifest.json').exists(),'certificate_bundle_zip_present':links['certificate_bundle_zip']['present']},
       'counts':{'discovered_runs':rb.get('counts',{}).get('discovered_runs',0),'selected_runs':rb.get('counts',{}).get('selected_runs',0),'deck_cards':rb.get('counts',{}).get('deck_cards',0),'zip_count':rb.get('counts',{}).get('zip_count',0),'missing_zip_count':rb.get('counts',{}).get('missing_zip_count',0),'verification_checks':v.get('summary',{}).get('check_count',0),'verification_errors':v.get('summary',{}).get('error_count',0),'verification_warnings':v.get('summary',{}).get('warning_count',0)},
       'hashes':{'release_build_hash':rb.get('receipt',{}).get('release_build_hash'),'release_build_zip_hash':rbz.get('receipt',{}).get('release_build_zip_hash'),'release_build_zip_sha256':rbz.get('receipt',{}).get('zip_file_sha256'),'verification_hash':v.get('receipt',{}).get('verification_hash'),'certificate_hash':c.get('receipt',{}).get('release_certificate_hash'),'certificate_bundle_hash':cb.get('receipt',{}).get('certificate_bundle_hash'),'certificate_bundle_zip_hash':cbz.get('receipt',{}).get('certificate_bundle_zip_hash'),'certificate_bundle_zip_sha256':cbz.get('receipt',{}).get('zip_file_sha256')},
       'links':links,
       'stage_hashes':{
         'gallery':{'hash':g.get('receipt',{}).get('gallery_hash'),'path':'gallery/gallery_manifest.json','present':(b/'gallery/gallery_manifest.json').exists()},
         'collection':{'hash':col.get('receipt',{}).get('collection_hash'),'path':'collection/collection_manifest.json','present':(b/'collection/collection_manifest.json').exists()},
         'collection_export':{'hash':ce.get('receipt',{}).get('collection_export_hash'),'path':'collection_export/collection_export_manifest.json','present':(b/'collection_export/collection_export_manifest.json').exists()},
         'release_deck':{'hash':rd.get('receipt',{}).get('release_deck_hash'),'path':'release_deck/release_deck_manifest.json','present':(b/'release_deck/release_deck_manifest.json').exists()},
         'release_deck_zip':{'hash':rdz.get('receipt',{}).get('release_deck_zip_hash'),'path':'release_deck/release_deck_zip_manifest.json','present':(b/'release_deck/release_deck_zip_manifest.json').exists()},
         'release_build_zip':{'hash':rbz.get('receipt',{}).get('release_build_zip_hash'),'path':'release_build_zip_manifest.json','present':(b/'release_build_zip_manifest.json').exists()},
         'verification':{'hash':v.get('receipt',{}).get('verification_hash'),'path':'release_build_verification.json','present':(b/'release_build_verification.json').exists()},
         'certificate':{'hash':c.get('receipt',{}).get('release_certificate_hash'),'path':'release_certificate.json','present':(b/'release_certificate.json').exists()},
         'certificate_bundle':{'hash':cb.get('receipt',{}).get('certificate_bundle_hash'),'path':'certificate_bundle/certificate_bundle_manifest.json','present':(b/'certificate_bundle/certificate_bundle_manifest.json').exists()},
         'certificate_bundle_zip':{'hash':cbz.get('receipt',{}).get('certificate_bundle_zip_hash'),'path':'certificate_bundle/certificate_bundle_zip_manifest.json','present':(b/'certificate_bundle/certificate_bundle_zip_manifest.json').exists()},
       },
       'outputs':{'index':'index.html','manifest':'release_build_index_manifest.json','receipt':'release_build_index_receipt.json','summary':'RELEASE_BUILD_INDEX_SUMMARY.md'}}
    m['receipt']={'schema':'waveforge.release_build_index_receipt.v2_alpha','release_build_index_hash':sha256_digest(json.loads(canonical_json(m))),'created_at':_STABLE_TS}
    return m


def write_release_build_index(build_dir: str | Path) -> dict:
    b=Path(build_dir); m=create_release_build_index_manifest(b)
    def badge(name,val): return f"<span class='b'>{escape(name)}: {escape(str(val))}</span>"
    cards=[]
    for v in m['links'].values():
        if v['present']:
            body=f"<a href='{escape(v['path'])}'>{escape(v['label'])}</a>"
        else:
            body=f"{escape(v['label'])} (unavailable)"
        cards.append(f"<div class='card'>{body}</div>")
    actions=''.join(cards)
    stage=''.join([f"<tr><td>{escape(k)}</td><td>{escape(str(v['present']))}</td><td>{escape(str(v['hash']))}</td></tr>" for k,v in m['stage_hashes'].items()])
    hashes=''.join([f"<tr><td>{escape(k)}</td><td>{escape(str(v))}</td></tr>" for k,v in m['hashes'].items()])
    html=f"<!doctype html><html><head><meta charset='utf-8'><title>WaveForgeStudio Release Build</title><style>body{{font-family:Arial;margin:24px}}.b{{display:inline-block;margin:4px;padding:6px 10px;background:#eef;border-radius:6px}}.grid{{display:grid;grid-template-columns:repeat(2,minmax(220px,1fr));gap:10px}}.card{{border:1px solid #ddd;padding:10px;border-radius:8px}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:6px}}</style></head><body><h1>WaveForgeStudio Release Build</h1><h2>{escape(m['title'])}</h2>{badge('release build',m['status']['release_build_present'])}{badge('release build ZIP',m['status']['release_build_zip_present'])}{badge('verification passed',m['status']['verification_passed'])}{badge('certificate status',m['status']['certificate_status'])}{badge('certificate bundle',m['status']['certificate_bundle_present'])}{badge('certificate bundle ZIP',m['status']['certificate_bundle_zip_present'])}<h3>Primary Actions</h3><div class='grid'>{actions}</div><h3>Counts</h3><ul>{''.join([f'<li>{escape(k)}: {escape(str(v))}</li>' for k,v in m['counts'].items()])}</ul><h3>Hashes</h3><table><tr><th>name</th><th>value</th></tr>{hashes}</table><h3>Stage Table</h3><table><tr><th>stage</th><th>present</th><th>hash</th></tr>{stage}</table><p>Local release launch page only — no assets are copied, hosted, or rendered.</p></body></html>"
    (b/'index.html').write_text(html,encoding='utf-8')
    (b/'release_build_index_manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True),encoding='utf-8')
    (b/'release_build_index_receipt.json').write_text(json.dumps(m['receipt'],indent=2,sort_keys=True),encoding='utf-8')
    (b/'RELEASE_BUILD_INDEX_SUMMARY.md').write_text(f"# WaveForgeStudio Release Build Index Summary\n\n- title: {m['title']}\n- status: {m['status']}\n- counts: {m['counts']}\n- hashes: {m['hashes']}\n- links: {m['links']}\n- release_build_index_hash: {m['receipt']['release_build_index_hash']}\n\nLocal release launch page only — no assets are copied, hosted, or rendered.\n",encoding='utf-8')
    return m


def validate_release_build_index_manifest(manifest: dict) -> list[str]:
    e=[]
    if manifest.get('schema')!='waveforge.release_build_index_manifest.v2_alpha': e.append('schema invalid')
    p=manifest.get('index_policy',{})
    for k,v in {'local_launch_page':True,'copies_assets':False,'generates_new_runs':False,'renders_media':False,'external_calls_allowed':False,'subprocess_allowed':False,'network_allowed':False,'hosting':False,'browser_automation':False,'powerpoint':False,'video_rendering':False,'muxing':False}.items():
        if p.get(k) is not v: e.append(f'{k} must be {v}')
    if not manifest.get('outputs',{}).get('index'): e.append('outputs.index required')
    if not manifest.get('receipt',{}).get('release_build_index_hash'): e.append('receipt.release_build_index_hash required')
    for k in ['links','status','counts','hashes']:
        if not isinstance(manifest.get(k),dict): e.append(f'{k} required')
    for link in (manifest.get('links') or {}).values():
        if Path(link.get('path','')).is_absolute(): e.append('link path must be relative')
    return e


def assert_valid_release_build_index_manifest(manifest: dict) -> None:
    e=validate_release_build_index_manifest(manifest)
    if e: raise ValueError('Invalid release build index manifest: '+'; '.join(e))


def read_release_build_index_info(build_dir: str | Path) -> dict:
    b=Path(build_dir)
    mp=b/'release_build_index_manifest.json'; rp=b/'release_build_index_receipt.json'; sp=b/'RELEASE_BUILD_INDEX_SUMMARY.md'; ip=b/'index.html'
    m=json.loads(mp.read_text(encoding='utf-8')) if mp.exists() else {}
    txt=sp.read_text(encoding='utf-8',errors='ignore').lower() if sp.exists() else ''
    return {'exists':b.exists(),'index_exists':ip.exists(),'manifest_exists':mp.exists(),'receipt_exists':rp.exists(),'summary_exists':sp.exists(),'verification_passed':m.get('status',{}).get('verification_passed') if m else None,'certificate_status':m.get('status',{}).get('certificate_status') if m else None,'release_build_zip_present':m.get('status',{}).get('release_build_zip_present') if m else False,'certificate_bundle_zip_present':m.get('status',{}).get('certificate_bundle_zip_present') if m else False,'contains_waveforge':'waveforge' in txt}
