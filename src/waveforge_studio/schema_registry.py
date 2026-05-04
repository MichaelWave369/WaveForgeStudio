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
("waveforge.preview_pack_zip_manifest.v1_alpha","v1_alpha","preview pack zip manifest","preview_pack_zip_manifest.json"),
("waveforge.preview_pack_zip_receipt.v1_alpha","v1_alpha","preview pack zip receipt","preview_pack_zip_receipt.json"),
("waveforge.demo_gallery_manifest.v1_alpha","v1_alpha","Local searchable demo gallery manifest","gallery_manifest.json"),
("waveforge.demo_gallery_receipt.v1_alpha","v1_alpha","demo gallery receipt","gallery_receipt.json"),
("waveforge.gallery_collection_manifest.v1_alpha","v1_alpha","gallery collection manifest","collection_manifest.json"),
("waveforge.gallery_collection_receipt.v1_alpha","v1_alpha","gallery collection receipt","collection_receipt.json"),
("waveforge.collection_export_manifest.v1_alpha","v1_alpha","collection export manifest","collection_export_manifest.json"),
("waveforge.collection_export_receipt.v1_alpha","v1_alpha","collection export receipt","collection_export_receipt.json"),
("waveforge.release_deck_manifest.v2_alpha","v2_alpha","release deck manifest","release_deck_manifest.json"),
("waveforge.release_deck_receipt.v2_alpha","v2_alpha","release deck receipt","release_deck_receipt.json"),
("waveforge.release_deck_zip_manifest.v2_alpha","v2_alpha","release deck zip manifest","release_deck_zip_manifest.json"),
("waveforge.release_deck_zip_receipt.v2_alpha","v2_alpha","release deck zip receipt","release_deck_zip_receipt.json"),
("waveforge.release_build_manifest.v2_alpha","v2_alpha","release build manifest","release_build_manifest.json"),
("waveforge.release_build_receipt.v2_alpha","v2_alpha","release build receipt","release_build_receipt.json"),
("waveforge.release_build_zip_manifest.v2_alpha","v2_alpha","Deterministic release build ZIP manifest","release_build_zip_manifest.json"),
("waveforge.release_build_zip_receipt.v2_alpha","v2_alpha","Deterministic release build ZIP receipt","release_build_zip_receipt.json"),
("waveforge.release_build_verification.v2_alpha","v2_alpha","release build verification report","release_build_verification.json"),
("waveforge.release_build_verification_receipt.v2_alpha","v2_alpha","release build verification receipt","release_build_verification_receipt.json"),
("waveforge.release_certificate.v2_alpha","v2_alpha","release certificate","release_certificate.json"),
("waveforge.release_certificate_receipt.v2_alpha","v2_alpha","release certificate receipt","release_certificate_receipt.json"),
("waveforge.certificate_bundle_manifest.v2_alpha","v2_alpha","certificate bundle manifest","certificate_bundle_manifest.json"),
("waveforge.certificate_bundle_receipt.v2_alpha","v2_alpha","certificate bundle receipt","certificate_bundle_receipt.json"),
("waveforge.certificate_bundle_zip_manifest.v2_alpha","v2_alpha","certificate bundle zip manifest","certificate_bundle_zip_manifest.json"),
("waveforge.certificate_bundle_zip_receipt.v2_alpha","v2_alpha","certificate bundle zip receipt","certificate_bundle_zip_receipt.json"),
("waveforge.release_build_index_manifest.v2_alpha","v2_alpha","release build index manifest","release_build_index_manifest.json"),
("waveforge.release_build_index_receipt.v2_alpha","v2_alpha","release build index receipt","release_build_index_receipt.json"),
("waveforge.final_release_manifest.v2_alpha","v2_alpha","final release manifest","final_release_manifest.json"),
("waveforge.final_release_receipt.v2_alpha","v2_alpha","final release receipt","final_release_receipt.json"),
("waveforge.command_inventory.v3_alpha","v3_alpha","command inventory","command_inventory.json"),
("waveforge.command_inventory_receipt.v3_alpha","v3_alpha","command inventory receipt","command_inventory_receipt.json"),
("waveforge.signature_envelope.v3_alpha","v3_alpha","signature envelope","signature_envelope.json"),
("waveforge.signature_envelope_receipt.v3_alpha","v3_alpha","signature envelope receipt","signature_envelope_receipt.json"),
("waveforge.detached_signature_manifest.v3_alpha","v3_alpha","detached signature manifest","detached_signature_manifest.json"),
("waveforge.detached_signature_receipt.v3_alpha","v3_alpha","detached signature receipt","detached_signature_receipt.json"),
("waveforge.renderer_adapter_manifest.v3_alpha","v3_alpha","renderer adapter manifest","renderer_adapter_manifest.json"),
("waveforge.renderer_adapter_receipt.v3_alpha","v3_alpha","renderer adapter receipt","renderer_adapter_receipt.json"),
("waveforge.ffmpeg_adapter_contract.v3_alpha","v3_alpha","ffmpeg adapter contract","ffmpeg_adapter_contract.json"),
("waveforge.ffmpeg_adapter_contract_receipt.v3_alpha","v3_alpha","ffmpeg adapter contract receipt","ffmpeg_adapter_contract_receipt.json"),
("waveforge.phiaudio_adapter_contract.v3_alpha","v3_alpha","phiaudio adapter contract","phiaudio_adapter_contract.json"),
("waveforge.phiaudio_adapter_contract_receipt.v3_alpha","v3_alpha","phiaudio adapter contract receipt","phiaudio_adapter_contract_receipt.json"),
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
