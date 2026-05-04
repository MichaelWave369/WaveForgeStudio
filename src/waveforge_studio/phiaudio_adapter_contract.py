from __future__ import annotations
import json
from pathlib import Path
from .hashing import canonical_json, sha256_digest

_STABLE_TS='1979-03-06T03:06:09Z'

def create_phiaudio_adapter_contract() -> dict:
    c={"schema":"waveforge.phiaudio_adapter_contract.v3_alpha","project":"WaveForgeStudio","version":"3.5-alpha","adapter_id":"phiaudio_runtime_future","name":"PHIAudio Runtime Adapter Pilot Contract","status":"disabled_contract","execution_policy":{"contract_only":True,"execution_enabled":False,"requires_operator_enablement":True,"requires_external_runtime":True,"requires_subprocess":False,"requires_network":False,"external_calls_allowed":False,"network_allowed":False,"audio_model_execution":False,"real_audio_generation":False,"default_enabled":False},"planned_capabilities":["align_stems_to_av_timeline_future","consume_phiaudio_bridge_bundle","emit_audio_render_receipts_future","emit_stem_manifests_future","generate_audio_stems_future","support_local_runtime_mode_future"],"required_inputs":[{"path":"av_timeline.json","required":True,"description":"Unified AV timeline contract."},{"path":"phiaudio/phiaudio_bundle.json","required":True,"description":"Deterministic PHIAudio bridge bundle contract."},{"path":"project.waveforge.json","required":True,"description":"Source WaveForge packet."},{"path":"renderer_handoff.json","required":True,"description":"Renderer handoff package."}],"planned_outputs":[{"path":"PHIAUDIO_RENDER_SUMMARY.md","description":"Future human-readable PHIAudio render summary."},{"path":"phiaudio_render_manifest.json","description":"Future PHIAudio render manifest."},{"path":"phiaudio_render_receipt.json","description":"Future PHIAudio render receipt."},{"path":"render/phiaudio/master.wav","description":"Future PHIAudio generated master audio."},{"path":"render/phiaudio/stems/bass.wav","description":"Future PHIAudio generated bass stem."},{"path":"render/phiaudio/stems/drums.wav","description":"Future PHIAudio generated drums stem."},{"path":"render/phiaudio/stems/harmony.wav","description":"Future PHIAudio generated harmony stem."},{"path":"render/phiaudio/stems/lead.wav","description":"Future PHIAudio generated lead stem."}],"governance_gates":[{"gate":"content_receipt","required":True,"description":"Future implementation must record input bundle hashes and output stem hashes."},{"gate":"deterministic_manifest","required":True,"description":"Future implementation must emit deterministic manifests and receipts."},{"gate":"local_first_policy","required":True,"description":"Future implementation should prefer local runtime execution before any remote mode is considered."},{"gate":"no_network_default","required":True,"description":"Network access must remain disabled by default."},{"gate":"operator_enablement","required":True,"description":"Adapter must require explicit operator opt-in."},{"gate":"path_safety","required":True,"description":"Future implementation must reject path traversal and absolute output paths."},{"gate":"runtime_availability_check","required":True,"description":"Future implementation must check PHIAudio runtime availability without failing unrelated workflows."}],"future_cli":{"render_command":"phiaudio-render","validate_command":"phiaudio-render-validate","enablement_flag":"--enable-phiaudio","default_behavior":"disabled"},"relationship_to_phiaudio_bridge":{"bridge_schema":"waveforge.phiaudio_bundle.v0","bridge_command":"export-phiaudio","bridge_artifact":"phiaudio/phiaudio_bundle.json","status":"bridge_contract_only"},"relationship_to_renderer_adapters":{"renderer_adapter_id":"phiaudio_runtime_future","manifest":"renderer_adapter_manifest.json","status":"future_disabled_adapter"},"limitations":["Contract only; PHIAudio runtime is not executed.","No audio model is executed.","No real generative audio is produced.","No subprocesses are started.","No network calls are made.","No PHIAudio availability check is performed.","Future implementation must remain opt-in."],"outputs":{"contract":"phiaudio_adapter_contract.json","receipt":"phiaudio_adapter_contract_receipt.json","markdown":"PHIAUDIO_ADAPTER_CONTRACT.md"}}
    c['receipt']={"schema":"waveforge.phiaudio_adapter_contract_receipt.v3_alpha","phiaudio_adapter_contract_hash":sha256_digest(json.loads(canonical_json(c))),"created_at":_STABLE_TS}
    return c

def write_phiaudio_adapter_contract(out_dir:str|Path)->dict:
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    c=create_phiaudio_adapter_contract()
    (out/'phiaudio_adapter_contract.json').write_text(json.dumps(c,indent=2,sort_keys=True),encoding='utf-8')
    (out/'phiaudio_adapter_contract_receipt.json').write_text(json.dumps(c['receipt'],indent=2,sort_keys=True),encoding='utf-8')
    (out/'PHIAUDIO_ADAPTER_CONTRACT.md').write_text('# WaveForgeStudio PHIAudio Runtime Adapter Pilot Contract\n\nContract only — PHIAudio runtime is not executed.\n',encoding='utf-8')
    return c

def validate_phiaudio_adapter_contract(contract:dict)->list[str]:
    e=[]
    if contract.get('schema')!='waveforge.phiaudio_adapter_contract.v3_alpha': e.append('schema invalid')
    if contract.get('version')!='3.5-alpha': e.append('version invalid')
    if contract.get('adapter_id')!='phiaudio_runtime_future': e.append('adapter_id invalid')
    if contract.get('status')!='disabled_contract': e.append('status invalid')
    p=contract.get('execution_policy',{})
    for k,v in {'contract_only':True,'execution_enabled':False,'requires_operator_enablement':True,'requires_external_runtime':True,'external_calls_allowed':False,'network_allowed':False,'audio_model_execution':False,'real_audio_generation':False,'default_enabled':False}.items():
        if p.get(k) is not v: e.append(f'{k} must be {v}')
    if not contract.get('required_inputs'): e.append('required_inputs required')
    if not contract.get('planned_outputs'): e.append('planned_outputs required')
    if not contract.get('governance_gates'): e.append('governance_gates required')
    if contract.get('future_cli',{}).get('default_behavior')!='disabled': e.append('future_cli.default_behavior invalid')
    if not contract.get('relationship_to_phiaudio_bridge',{}).get('bridge_artifact'): e.append('relationship_to_phiaudio_bridge.bridge_artifact required')
    if not contract.get('receipt',{}).get('phiaudio_adapter_contract_hash'): e.append('receipt.phiaudio_adapter_contract_hash required')
    for x in contract.get('required_inputs',[]):
        if Path(x.get('path','')).is_absolute(): e.append('required input path must be relative')
    for x in contract.get('planned_outputs',[]):
        if Path(x.get('path','')).is_absolute(): e.append('planned output path must be relative')
    for _,v in (contract.get('outputs') or {}).items():
        if Path(v).is_absolute(): e.append('output path must be relative')
    return e

def assert_valid_phiaudio_adapter_contract(contract:dict)->None:
    err=validate_phiaudio_adapter_contract(contract)
    if err: raise ValueError('Invalid phiaudio adapter contract: '+'; '.join(err))

def read_phiaudio_adapter_contract_info(out_dir:str|Path)->dict:
    out=Path(out_dir); cp=out/'phiaudio_adapter_contract.json'; rp=out/'phiaudio_adapter_contract_receipt.json'; mp=out/'PHIAUDIO_ADAPTER_CONTRACT.md'
    c=json.loads(cp.read_text(encoding='utf-8')) if cp.exists() else {}
    t=mp.read_text(encoding='utf-8',errors='ignore').lower() if mp.exists() else ''
    return {'exists':out.exists(),'contract_exists':cp.exists(),'receipt_exists':rp.exists(),'markdown_exists':mp.exists(),'status':c.get('status') if c else None,'execution_enabled':c.get('execution_policy',{}).get('execution_enabled') if c else None,'requires_external_runtime':c.get('execution_policy',{}).get('requires_external_runtime') if c else None,'contains_waveforge':'waveforge' in t}
