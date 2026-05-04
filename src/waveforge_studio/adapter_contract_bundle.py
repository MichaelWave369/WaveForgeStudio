from __future__ import annotations
import json, shutil
from pathlib import Path
from .artifact_ledger import file_sha256
from .hashing import canonical_json, sha256_digest
from .renderer_adapters import create_renderer_adapter_manifest, write_renderer_adapter_manifest
from .ffmpeg_adapter_contract import create_ffmpeg_adapter_contract, write_ffmpeg_adapter_contract
from .phiaudio_adapter_contract import create_phiaudio_adapter_contract, write_phiaudio_adapter_contract
from .waverider_adapter_contract import create_waverider_adapter_contract, write_waverider_adapter_contract

_STABLE_TS='1979-03-06T03:06:09Z'
_REQ=[('renderer_adapter_manifest.json','renderer_adapters'),('renderer_adapter_receipt.json','renderer_adapters'),('RENDERER_ADAPTERS.md','renderer_adapters'),('ffmpeg_adapter_contract.json','ffmpeg'),('ffmpeg_adapter_contract_receipt.json','ffmpeg'),('FFMPEG_ADAPTER_CONTRACT.md','ffmpeg'),('phiaudio_adapter_contract.json','phiaudio'),('phiaudio_adapter_contract_receipt.json','phiaudio'),('PHIAUDIO_ADAPTER_CONTRACT.md','phiaudio'),('waverider_adapter_contract.json','waverider'),('waverider_adapter_contract_receipt.json','waverider'),('WAVERIDER_ADAPTER_CONTRACT.md','waverider')]

def _default_bundle_root(source_dir,bundle_dir):
    if bundle_dir: return Path(bundle_dir)
    if source_dir: return Path(source_dir)/'adapter_contract_bundle'
    return Path('adapter_contract_bundle')

def create_adapter_contract_bundle_manifest(source_dir: str|Path|None=None,bundle_dir: str|Path|None=None)->dict:
    src=Path(source_dir) if source_dir else None
    br=_default_bundle_root(source_dir,bundle_dir)
    ram,ff,ph,wr=create_renderer_adapter_manifest(),create_ffmpeg_adapter_contract(),create_phiaudio_adapter_contract(),create_waverider_adapter_contract()
    hash_map={'renderer_adapter_manifest.json':ram['receipt']['renderer_adapter_manifest_hash'],'ffmpeg_adapter_contract.json':ff['receipt']['ffmpeg_adapter_contract_hash'],'phiaudio_adapter_contract.json':ph['receipt']['phiaudio_adapter_contract_hash'],'waverider_adapter_contract.json':wr['receipt']['waverider_adapter_contract_hash']}
    evidence=[]; missing=[]
    for name,_ in sorted(_REQ,key=lambda x:x[0]):
        p=src/name if src else None; present=p.exists() if p else False
        if not present and src: missing.append(name)
        evidence.append({'source':name,'target':name,'present':present,'required':True,'sha256':file_sha256(p) if present else None,'artifact_hash':hash_map.get(name)})
    m={'schema':'waveforge.adapter_contract_bundle_manifest.v3_alpha','project':'WaveForgeStudio','version':'3.7-alpha','bundle_root':'adapter_contract_bundle','bundle_policy':{'contract_bundle_only':True,'real_rendering':False,'runtime_execution':False,'model_execution':False,'subprocess_allowed':False,'network_allowed':False,'external_calls_allowed':False,'ffmpeg_execution':False,'phiaudio_execution':False,'waverider_execution':False,'browser_automation':False,'default_enabled':False},'contracts':{'renderer_adapters':{'schema':'waveforge.renderer_adapter_manifest.v3_alpha','status':'interface_contract','path':'renderer_adapter_manifest.json','present':True,'hash':ram['receipt']['renderer_adapter_manifest_hash']},'ffmpeg':{'schema':'waveforge.ffmpeg_adapter_contract.v3_alpha','status':'disabled_contract','path':'ffmpeg_adapter_contract.json','present':True,'hash':ff['receipt']['ffmpeg_adapter_contract_hash']},'phiaudio':{'schema':'waveforge.phiaudio_adapter_contract.v3_alpha','status':'disabled_contract','path':'phiaudio_adapter_contract.json','present':True,'hash':ph['receipt']['phiaudio_adapter_contract_hash']},'waverider':{'schema':'waveforge.waverider_adapter_contract.v3_alpha','status':'disabled_contract','path':'waverider_adapter_contract.json','present':True,'hash':wr['receipt']['waverider_adapter_contract_hash']}},'evidence':evidence,'required_missing':sorted(missing),'contract_count':4,'evidence_count':len(evidence),'execution_enabled_count':0,'future_runtime_count':3,'outputs':{'manifest':'adapter_contract_bundle_manifest.json','receipt':'adapter_contract_bundle_receipt.json','markdown':'ADAPTER_CONTRACT_BUNDLE.md'}}
    m['receipt']={'schema':'waveforge.adapter_contract_bundle_receipt.v3_alpha','adapter_contract_bundle_hash':sha256_digest(json.loads(canonical_json(m))),'created_at':_STABLE_TS}
    return m

def write_adapter_contract_bundle(out_dir:str|Path,source_dir:str|Path|None=None)->dict:
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    src=Path(source_dir) if source_dir else None
    if src:
        for f,_ in _REQ:
            sp=src/f; dp=out/f
            if sp.exists():
                dp.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(sp,dp)
    write_renderer_adapter_manifest(out); write_ffmpeg_adapter_contract(out); write_phiaudio_adapter_contract(out); write_waverider_adapter_contract(out)
    m=create_adapter_contract_bundle_manifest(source_dir=src or out,bundle_dir=out)
    (out/'adapter_contract_bundle_manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True),encoding='utf-8')
    (out/'adapter_contract_bundle_receipt.json').write_text(json.dumps(m['receipt'],indent=2,sort_keys=True),encoding='utf-8')
    (out/'ADAPTER_CONTRACT_BUNDLE.md').write_text('# WaveForgeStudio Adapter Contract Bundle\n\nContract bundle only — no renderer runtime is executed.\n',encoding='utf-8')
    return m

def validate_adapter_contract_bundle_manifest(manifest:dict)->list[str]:
    e=[]
    if manifest.get('schema')!='waveforge.adapter_contract_bundle_manifest.v3_alpha': e.append('schema invalid')
    if manifest.get('version')!='3.7-alpha': e.append('version invalid')
    p=manifest.get('bundle_policy',{})
    for k,v in {'contract_bundle_only':True,'real_rendering':False,'runtime_execution':False,'model_execution':False,'subprocess_allowed':False,'network_allowed':False,'external_calls_allowed':False,'ffmpeg_execution':False,'phiaudio_execution':False,'waverider_execution':False,'browser_automation':False,'default_enabled':False}.items():
        if p.get(k) is not v: e.append(f'{k} must be {v}')
    c=manifest.get('contracts',{})
    for k in ['renderer_adapters','ffmpeg','phiaudio','waverider']:
        if k not in c: e.append(f'contracts.{k} required')
    if manifest.get('contract_count')!=4: e.append('contract_count must be 4')
    if manifest.get('future_runtime_count')!=3: e.append('future_runtime_count must be 3')
    ev=manifest.get('evidence',[])
    if not isinstance(ev,list): e.append('evidence must be list')
    if manifest.get('evidence_count')!=len(ev): e.append('evidence_count mismatch')
    if manifest.get('required_missing'): e.append('required_missing must be empty')
    if not manifest.get('receipt',{}).get('adapter_contract_bundle_hash'): e.append('receipt.adapter_contract_bundle_hash required')
    for x in ev:
        if Path(x.get('source','')).is_absolute() or Path(x.get('target','')).is_absolute(): e.append('evidence paths must be relative')
    return e

def assert_valid_adapter_contract_bundle_manifest(manifest:dict)->None:
    err=validate_adapter_contract_bundle_manifest(manifest)
    if err: raise ValueError('Invalid adapter contract bundle manifest: '+'; '.join(err))

def read_adapter_contract_bundle_info(bundle_dir:str|Path)->dict:
    b=Path(bundle_dir); mp=b/'adapter_contract_bundle_manifest.json'; rp=b/'adapter_contract_bundle_receipt.json'; md=b/'ADAPTER_CONTRACT_BUNDLE.md'
    m=json.loads(mp.read_text(encoding='utf-8')) if mp.exists() else {}
    t=md.read_text(encoding='utf-8',errors='ignore').lower() if md.exists() else ''
    return {'exists':b.exists(),'manifest_exists':mp.exists(),'receipt_exists':rp.exists(),'markdown_exists':md.exists(),'renderer_manifest_exists':(b/'renderer_adapter_manifest.json').exists(),'ffmpeg_contract_exists':(b/'ffmpeg_adapter_contract.json').exists(),'phiaudio_contract_exists':(b/'phiaudio_adapter_contract.json').exists(),'waverider_contract_exists':(b/'waverider_adapter_contract.json').exists(),'contract_count':m.get('contract_count') if m else None,'future_runtime_count':m.get('future_runtime_count') if m else None,'contains_waveforge':'waveforge' in t}
