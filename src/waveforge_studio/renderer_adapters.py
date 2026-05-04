from __future__ import annotations
import json
from pathlib import Path
from .hashing import canonical_json, sha256_digest

_STABLE_TS='1979-03-06T03:06:09Z'


def create_renderer_adapter_manifest() -> dict:
    adapters = [
        {"adapter_id":"local_audio_stub","name":"Local Audio WAV Stub","kind":"audio","status":"available","execution_mode":"local_stub","execution_enabled":True,"safe_by_default":True,"requires_external_runtime":False,"requires_subprocess":False,"requires_network":False,"requires_ffmpeg":False,"inputs":["project.waveforge.json","av_timeline.json"],"outputs":["render/audio_mix.wav","audio_render_manifest.json","audio_render_receipt.json"],"cli_commands":["render-audio-stub","audio-render-validate"],"notes":["Deterministic placeholder WAV only.","No generative audio model is executed."]},
        {"adapter_id":"local_av_preview","name":"Local AV Preview","kind":"preview","status":"available","execution_mode":"local_stub","execution_enabled":True,"safe_by_default":True,"requires_external_runtime":False,"requires_subprocess":False,"requires_network":False,"requires_ffmpeg":False,"inputs":["audio_render_manifest.json","visual_render_manifest.json"],"outputs":["av_preview.html","av_preview_manifest.json","av_preview_receipt.json"],"cli_commands":["preview-av","av-preview-validate"],"notes":["Offline HTML preview only."]},
        {"adapter_id":"local_visual_stub","name":"Local Visual SVG Stub","kind":"visual","status":"available","execution_mode":"local_stub","execution_enabled":True,"safe_by_default":True,"requires_external_runtime":False,"requires_subprocess":False,"requires_network":False,"requires_ffmpeg":False,"inputs":["project.waveforge.json","av_timeline.json"],"outputs":["render/storyboard/*.svg","visual_render_manifest.json","visual_render_receipt.json"],"cli_commands":["render-visual-stub","visual-render-validate"],"notes":["Deterministic storyboard SVG placeholders only."]},
        {"adapter_id":"phiaudio_bridge_contract","name":"PHIAudio Bridge Contract","kind":"audio_contract","status":"planned","execution_mode":"plan_only","execution_enabled":False,"safe_by_default":True,"requires_external_runtime":False,"requires_subprocess":False,"requires_network":False,"requires_ffmpeg":False,"inputs":["project.waveforge.json"],"outputs":["phiaudio/phiaudio_bundle.json"],"cli_commands":["export-phiaudio"],"notes":["Contract export only; no runtime execution."]},
        {"adapter_id":"waverider_bridge_contract","name":"WaveRider Bridge Contract","kind":"visual_contract","status":"planned","execution_mode":"plan_only","execution_enabled":False,"safe_by_default":True,"requires_external_runtime":False,"requires_subprocess":False,"requires_network":False,"requires_ffmpeg":False,"inputs":["project.waveforge.json"],"outputs":["waverider/waverider_bundle.json"],"cli_commands":["export-waverider"],"notes":["Contract export only; no runtime execution."]},
        {"adapter_id":"wavetalk_bridge_contract","name":"WaveTalk Bridge Contract","kind":"signal_contract","status":"planned","execution_mode":"plan_only","execution_enabled":False,"safe_by_default":True,"requires_external_runtime":False,"requires_subprocess":False,"requires_network":False,"requires_ffmpeg":False,"inputs":["project.waveforge.json"],"outputs":["wavetalk/wavetalk_bundle.json"],"cli_commands":["export-wavetalk"],"notes":["Contract export only; no runtime execution."]},
    ]
    future = [
        {"adapter_id":"comfyui_optional_future","name":"Optional ComfyUI Adapter","kind":"image_video_generation","status":"future","execution_mode":"disabled_future","execution_enabled":False,"safe_by_default":False,"requires_external_runtime":True,"requires_subprocess":True,"requires_network":False,"requires_ffmpeg":False,"planned_inputs":["renderer_handoff.json"],"planned_outputs":["render/comfyui_output_manifest.json"],"notes":["Future optional adapter only."]},
        {"adapter_id":"ffmpeg_optional_future","name":"Optional FFmpeg Export Adapter","kind":"mux_video","status":"future","execution_mode":"disabled_future","execution_enabled":False,"safe_by_default":False,"requires_external_runtime":True,"requires_subprocess":True,"requires_network":False,"requires_ffmpeg":True,"planned_inputs":["audio_render_manifest.json","visual_render_manifest.json","av_timeline.json"],"planned_outputs":["render/final_preview.mp4","ffmpeg_render_manifest.json"],"notes":["Future optional adapter only.","Must remain disabled until explicit operator enablement exists."]},
        {"adapter_id":"phiaudio_runtime_future","name":"PHIAudio Runtime Adapter","kind":"audio_generation","status":"future","execution_mode":"disabled_future","execution_enabled":False,"safe_by_default":False,"requires_external_runtime":True,"requires_subprocess":True,"requires_network":False,"requires_ffmpeg":False,"planned_inputs":["phiaudio/phiaudio_bundle.json"],"planned_outputs":["render/phiaudio_runtime_manifest.json"],"notes":["Future runtime adapter only."]},
        {"adapter_id":"waverider_runtime_future","name":"WaveRider Runtime Adapter","kind":"video_generation","status":"future","execution_mode":"disabled_future","execution_enabled":False,"safe_by_default":False,"requires_external_runtime":True,"requires_subprocess":True,"requires_network":False,"requires_ffmpeg":False,"planned_inputs":["waverider/waverider_bundle.json"],"planned_outputs":["render/waverider_runtime_manifest.json"],"notes":["Future runtime adapter only."]},
    ]
    adapters=sorted(adapters,key=lambda x:x['adapter_id']); future=sorted(future,key=lambda x:x['adapter_id'])
    enabled=sum(1 for a in adapters if a.get('execution_enabled'))
    m={"schema":"waveforge.renderer_adapter_manifest.v3_alpha","project":"WaveForgeStudio","version":"3.3-alpha","adapter_policy":{"interface_contract_only":True,"execution_enabled":False,"external_calls_allowed":False,"subprocess_allowed":False,"network_allowed":False,"ffmpeg_required":False,"browser_automation":False,"real_media_rendering":False,"stub_rendering_allowed":True},"adapter_count":len(adapters),"enabled_adapter_count":enabled,"execution_enabled_adapter_count":enabled,"adapters":adapters,"future_adapters":future,"adapter_contract":{"required_fields":["adapter_id","name","kind","status","execution_mode","execution_enabled","safe_by_default","requires_external_runtime","requires_subprocess","requires_network","inputs","outputs"],"allowed_statuses":["available","planned","future","disabled"],"allowed_execution_modes":["local_stub","plan_only","disabled_future"]},"outputs":{"manifest":"renderer_adapter_manifest.json","receipt":"renderer_adapter_receipt.json","markdown":"RENDERER_ADAPTERS.md"}}
    m['receipt']={"schema":"waveforge.renderer_adapter_receipt.v3_alpha","renderer_adapter_manifest_hash":sha256_digest(json.loads(canonical_json(m))),"created_at":_STABLE_TS}
    return m

def write_renderer_adapter_manifest(out_dir: str|Path) -> dict:
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    m=create_renderer_adapter_manifest()
    (out/'renderer_adapter_manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True),encoding='utf-8')
    (out/'renderer_adapter_receipt.json').write_text(json.dumps(m['receipt'],indent=2,sort_keys=True),encoding='utf-8')
    (out/'RENDERER_ADAPTERS.md').write_text('# WaveForgeStudio Renderer Adapter Interface\n\nInterface contract only — no real rendering or external runtime execution is enabled.\n',encoding='utf-8')
    return m

def validate_renderer_adapter_manifest(manifest: dict) -> list[str]:
    e=[]
    if manifest.get('schema')!='waveforge.renderer_adapter_manifest.v3_alpha': e.append('schema invalid')
    if manifest.get('version')!='3.3-alpha': e.append('version invalid')
    p=manifest.get('adapter_policy',{})
    for k,v in {'interface_contract_only':True,'execution_enabled':False,'external_calls_allowed':False,'subprocess_allowed':False,'network_allowed':False,'ffmpeg_required':False,'browser_automation':False,'real_media_rendering':False,'stub_rendering_allowed':True}.items():
        if p.get(k) is not v: e.append(f'{k} must be {v}')
    adapters=manifest.get('adapters',[]); future=manifest.get('future_adapters',[])
    if not isinstance(adapters,list): e.append('adapters must be list')
    if not isinstance(future,list): e.append('future_adapters must be list')
    if manifest.get('adapter_count')!=len(adapters): e.append('adapter_count mismatch')
    enabled=sum(1 for a in adapters if a.get('execution_enabled'))
    if manifest.get('enabled_adapter_count')!=enabled: e.append('enabled_adapter_count mismatch')
    if manifest.get('execution_enabled_adapter_count')!=enabled: e.append('execution_enabled_adapter_count mismatch')
    ids=[a.get('adapter_id') for a in adapters+future]
    if len(ids)!=len(set(ids)): e.append('duplicate adapter_id')
    req=set(manifest.get('adapter_contract',{}).get('required_fields',[]))
    for a in adapters:
        if not req.issubset(set(a.keys())): e.append(f"adapter missing required fields: {a.get('adapter_id')}")
    for a in future:
        if a.get('execution_enabled') is not False: e.append('future adapter execution_enabled must be false')
        if a.get('safe_by_default') is not False: e.append('future adapter safe_by_default must be false')
    if not manifest.get('receipt',{}).get('renderer_adapter_manifest_hash'): e.append('receipt.renderer_adapter_manifest_hash required')
    return e

def assert_valid_renderer_adapter_manifest(manifest: dict) -> None:
    err=validate_renderer_adapter_manifest(manifest)
    if err: raise ValueError('Invalid renderer adapter manifest: '+'; '.join(err))

def read_renderer_adapter_info(out_dir: str|Path)->dict:
    out=Path(out_dir)
    mp=out/'renderer_adapter_manifest.json'; rp=out/'renderer_adapter_receipt.json'; md=out/'RENDERER_ADAPTERS.md'
    m=json.loads(mp.read_text(encoding='utf-8')) if mp.exists() else {}
    t=md.read_text(encoding='utf-8',errors='ignore').lower() if md.exists() else ''
    return {'exists':out.exists(),'manifest_exists':mp.exists(),'receipt_exists':rp.exists(),'markdown_exists':md.exists(),'adapter_count':m.get('adapter_count') if m else None,'future_adapter_count':len(m.get('future_adapters',[])) if m else None,'execution_enabled_adapter_count':m.get('execution_enabled_adapter_count') if m else None,'contains_waveforge':'waveforge' in t}
