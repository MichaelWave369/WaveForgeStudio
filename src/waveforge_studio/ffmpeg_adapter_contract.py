from __future__ import annotations
import json
from pathlib import Path
from .hashing import canonical_json, sha256_digest

_STABLE_TS='1979-03-06T03:06:09Z'

def create_ffmpeg_adapter_contract() -> dict:
    c={"schema":"waveforge.ffmpeg_adapter_contract.v3_alpha","project":"WaveForgeStudio","version":"3.4-alpha","adapter_id":"ffmpeg_optional_future","name":"Optional FFmpeg Export Adapter Contract","status":"disabled_contract","execution_policy":{"contract_only":True,"execution_enabled":False,"requires_operator_enablement":True,"requires_external_runtime":True,"requires_subprocess":True,"requires_ffmpeg":True,"network_allowed":False,"external_calls_allowed":False,"browser_automation":False,"video_rendering":False,"muxing_enabled":False,"default_enabled":False},"planned_capabilities":["derive_inputs_from_av_timeline","emit_ffmpeg_render_manifest","emit_ffmpeg_render_receipt","export_local_preview_mp4","mux_audio_visual_stub_outputs"],"required_inputs":[{"path":"audio_render_manifest.json","required":True,"description":"Local audio stub render manifest."},{"path":"av_timeline.json","required":True,"description":"Unified AV timeline contract."},{"path":"project.waveforge.json","required":True,"description":"Source WaveForge packet."},{"path":"visual_render_manifest.json","required":True,"description":"Local visual storyboard render manifest."}],"planned_outputs":[{"path":"FFMPEG_RENDER_SUMMARY.md","description":"Future human-readable FFmpeg render summary."},{"path":"ffmpeg_render_manifest.json","description":"Future FFmpeg render manifest."},{"path":"ffmpeg_render_receipt.json","description":"Future FFmpeg render receipt."},{"path":"render/final_preview.mp4","description":"Future local MP4 preview output."}],"safety_gates":[{"gate":"deterministic_manifest","required":True,"description":"Future implementation must emit deterministic render manifests and receipts."},{"gate":"ffmpeg_binary_check","required":True,"description":"Future implementation must check FFmpeg availability without failing unrelated workflows."},{"gate":"operator_enablement","required":True,"description":"Adapter must require explicit operator opt-in."},{"gate":"path_safety","required":True,"description":"Future implementation must reject path traversal and absolute output paths."},{"gate":"subprocess_policy","required":True,"description":"Future implementation must centralize subprocess invocation and arguments."}],"future_cli":{"render_command":"ffmpeg-render","validate_command":"ffmpeg-render-validate","enablement_flag":"--enable-ffmpeg","default_behavior":"disabled"},"relationship_to_renderer_adapters":{"renderer_adapter_id":"ffmpeg_optional_future","manifest":"renderer_adapter_manifest.json","status":"future_disabled_adapter"},"limitations":["Contract only; FFmpeg is not executed.","No subprocesses are started.","No video rendering or muxing is performed.","No FFmpeg availability check is performed.","Future implementation must remain opt-in."],"outputs":{"contract":"ffmpeg_adapter_contract.json","receipt":"ffmpeg_adapter_contract_receipt.json","markdown":"FFMPEG_ADAPTER_CONTRACT.md"}}
    c['receipt']={"schema":"waveforge.ffmpeg_adapter_contract_receipt.v3_alpha","ffmpeg_adapter_contract_hash":sha256_digest(json.loads(canonical_json(c))),"created_at":_STABLE_TS}
    return c

def write_ffmpeg_adapter_contract(out_dir:str|Path)->dict:
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    c=create_ffmpeg_adapter_contract()
    (out/'ffmpeg_adapter_contract.json').write_text(json.dumps(c,indent=2,sort_keys=True),encoding='utf-8')
    (out/'ffmpeg_adapter_contract_receipt.json').write_text(json.dumps(c['receipt'],indent=2,sort_keys=True),encoding='utf-8')
    (out/'FFMPEG_ADAPTER_CONTRACT.md').write_text('# WaveForgeStudio Optional FFmpeg Export Adapter Contract\n\nContract only — FFmpeg is not executed.\n',encoding='utf-8')
    return c

def validate_ffmpeg_adapter_contract(contract:dict)->list[str]:
    e=[]
    if contract.get('schema')!='waveforge.ffmpeg_adapter_contract.v3_alpha': e.append('schema invalid')
    if contract.get('version')!='3.4-alpha': e.append('version invalid')
    if contract.get('adapter_id')!='ffmpeg_optional_future': e.append('adapter_id invalid')
    if contract.get('status')!='disabled_contract': e.append('status invalid')
    p=contract.get('execution_policy',{})
    for k,v in {'contract_only':True,'execution_enabled':False,'requires_operator_enablement':True,'requires_external_runtime':True,'requires_subprocess':True,'requires_ffmpeg':True,'network_allowed':False,'external_calls_allowed':False,'browser_automation':False,'video_rendering':False,'muxing_enabled':False,'default_enabled':False}.items():
        if p.get(k) is not v: e.append(f'{k} must be {v}')
    if not contract.get('required_inputs'): e.append('required_inputs required')
    if not contract.get('planned_outputs'): e.append('planned_outputs required')
    if not contract.get('safety_gates'): e.append('safety_gates required')
    if contract.get('future_cli',{}).get('default_behavior')!='disabled': e.append('future_cli.default_behavior invalid')
    if not contract.get('receipt',{}).get('ffmpeg_adapter_contract_hash'): e.append('receipt.ffmpeg_adapter_contract_hash required')
    for x in contract.get('required_inputs',[]):
        if Path(x.get('path','')).is_absolute(): e.append('required input path must be relative')
    for x in contract.get('planned_outputs',[]):
        if Path(x.get('path','')).is_absolute(): e.append('planned output path must be relative')
    for _,v in (contract.get('outputs') or {}).items():
        if Path(v).is_absolute(): e.append('output path must be relative')
    return e

def assert_valid_ffmpeg_adapter_contract(contract:dict)->None:
    err=validate_ffmpeg_adapter_contract(contract)
    if err: raise ValueError('Invalid ffmpeg adapter contract: '+'; '.join(err))

def read_ffmpeg_adapter_contract_info(out_dir:str|Path)->dict:
    out=Path(out_dir); cp=out/'ffmpeg_adapter_contract.json'; rp=out/'ffmpeg_adapter_contract_receipt.json'; mp=out/'FFMPEG_ADAPTER_CONTRACT.md'
    c=json.loads(cp.read_text(encoding='utf-8')) if cp.exists() else {}
    t=mp.read_text(encoding='utf-8',errors='ignore').lower() if mp.exists() else ''
    return {'exists':out.exists(),'contract_exists':cp.exists(),'receipt_exists':rp.exists(),'markdown_exists':mp.exists(),'status':c.get('status') if c else None,'execution_enabled':c.get('execution_policy',{}).get('execution_enabled') if c else None,'requires_ffmpeg':c.get('execution_policy',{}).get('requires_ffmpeg') if c else None,'contains_waveforge':'waveforge' in t}
