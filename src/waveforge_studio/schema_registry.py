from __future__ import annotations
import json
from pathlib import Path

_SCHEMAS = [
("waveforge.media_packet.v0","v0","intent packet","project.waveforge.json"),
("waveforge.receipt.v0","v0","packet receipt","receipt.json"),
("waveforge.phiaudio_bundle.v0","v0","audio bridge","phiaudio/phiaudio_bundle.json"),
("waveforge.waverider_bundle.v0","v0","visual bridge","waverider/waverider_bundle.json"),
("waveforge.wavetalk_bundle.v0","v0","signal bridge","wavetalk/wavetalk_bundle.json"),
("waveforge.production_bundle.v0","v0","unified bundle","production_bundle.json"),
("waveforge.render_queue.v0","v0","queue manifest","render_queue.json"),
("waveforge.safe_queue_execution.v0","v0","safe execution report","execution_report.json"),
("waveforge.artifact_ledger.v0","v0","artifact ledger","artifact_ledger.json"),
("waveforge.av_timeline.v0","v0","av timeline","av_timeline.json"),
("waveforge.renderer_handoff.v0","v0","renderer handoff","renderer_handoff.json"),
("waveforge.local_audio_render_manifest.v1_alpha","v1_alpha","local audio render manifest","audio_render_manifest.json"),
("waveforge.local_audio_render_receipt.v1_alpha","v1_alpha","local audio render receipt","audio_render_receipt.json"),
("waveforge.local_visual_render_manifest.v1_alpha","v1_alpha","local visual render manifest","visual_render_manifest.json"),
("waveforge.local_visual_render_receipt.v1_alpha","v1_alpha","local visual render receipt","visual_render_receipt.json"),
("waveforge.local_av_preview_manifest.v1_alpha","v1_alpha","local av preview manifest","av_preview_manifest.json"),
("waveforge.local_av_preview_receipt.v1_alpha","v1_alpha","local av preview receipt","av_preview_receipt.json"),
("waveforge.preview_pack_manifest.v1_alpha","v1_alpha","preview pack manifest","preview_pack_manifest.json"),
("waveforge.preview_pack_receipt.v1_alpha","v1_alpha","preview pack receipt","preview_pack_receipt.json"),
]

def list_schemas() -> list[dict]:
    return [{"name":n,"version":v,"role":r,"primary_file":f,"status":"alpha_contract"} for n,v,r,f in _SCHEMAS]

def get_schema(name:str)->dict|None:
    for s in list_schemas():
        if s['name']==name: return s
    return None

def write_schema_registry(out_dir:str|Path)->dict:
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    payload={"schema":"waveforge.schema_registry.v1_alpha","schemas":list_schemas()}
    (out/'schema_registry.json').write_text(json.dumps(payload,indent=2,sort_keys=True),encoding='utf-8')
    (out/'SCHEMA_REGISTRY.md').write_text('# Schema Registry\n\n'+'\n'.join([f"- {s['name']}" for s in payload['schemas']]),encoding='utf-8')
    return payload
