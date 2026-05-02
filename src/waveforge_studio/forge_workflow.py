from __future__ import annotations
import json
from pathlib import Path
from .adapters.phiaudio_bridge import write_phiaudio_bundle
from .adapters.waverider_bridge import write_waverider_bundle
from .adapters.wavetalk_bridge import write_wavetalk_bundle
from .artifact_ledger import write_artifact_ledger
from .av_timeline import write_av_timeline
from .hashing import canonical_json, sha256_digest
from .media_packet import create_media_packet
from .production_bundle import write_production_bundle
from .queue_runner import write_queue_execution
from .release_manifest import write_release_manifest
from .render_manifest import create_render_manifest
from .render_queue import write_render_queue
from .renderer_handoff import write_renderer_handoff
from .schema_registry import write_schema_registry
from .studio_seal import write_studio_seal
from .timeline_preview import write_timeline_preview
from .version import __version__, RELEASE_NAME, DEFAULT_RELEASE_TIMESTAMP

def run_forge_workflow(prompt:str,out_dir:str|Path,duration_seconds:int=72,seed:int=369369,mode:str="mythic-reel")->dict:
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    p=create_media_packet(prompt,duration_seconds=duration_seconds,seed=seed,mode=mode)
    for n,d in [("project.waveforge.json",p),("audio_graph.json",p['audio']),("visual_graph.json",p['visual']),("sync_lattice.json",p['sync']),("render_manifest.json",create_render_manifest(p)),("receipt.json",p['receipt'])]:
        (out/n).write_text(json.dumps(d,indent=2,sort_keys=True),encoding='utf-8')
    (out/'summary.md').write_text('# Summary\n',encoding='utf-8')
    av=write_av_timeline(p,out); rh=write_renderer_handoff(p,out); write_timeline_preview(p,out)
    write_phiaudio_bundle(p,out/'phiaudio'); write_waverider_bundle(p,out/'waverider'); write_wavetalk_bundle(p,out/'wavetalk')
    prod=write_production_bundle(p,out); write_render_queue(p,out); exec_rep=write_queue_execution(p,out)
    write_schema_registry(out); ledger=write_artifact_ledger(out); rel=write_release_manifest(out,p); write_studio_seal(out,rel)
    rep={"schema":"waveforge.forge_report.v1_alpha","project":"WaveForgeStudio","version":__version__,"release_name":RELEASE_NAME,"prompt":prompt,"seed":seed,"duration_seconds":duration_seconds,"mode":mode,"source_packet_hash":p['receipt']['packet_hash'],"production_bundle_hash":prod['receipt']['bundle_hash'],"artifact_ledger_hash":ledger['receipt']['ledger_hash'],"release_hash":rel['receipt']['release_hash'],"alpha_ready":rel['alpha_ready'],"outputs":{"project":"project.waveforge.json","production_bundle":"production_bundle.json","timeline_preview":"timeline_preview.html","release_manifest":"release_manifest.json","studio_seal":"STUDIO_SEAL.md"}}
    rep['receipt']={"schema":"waveforge.forge_report_receipt.v1_alpha","forge_hash":sha256_digest(json.loads(canonical_json(rep))),"created_at":DEFAULT_RELEASE_TIMESTAMP}
    (out/'forge_report.json').write_text(json.dumps(rep,indent=2,sort_keys=True),encoding='utf-8')
    (out/'forge_report_receipt.json').write_text(json.dumps(rep['receipt'],indent=2,sort_keys=True),encoding='utf-8')
    (out/'FORGE_SUMMARY.md').write_text(f"# Forge Summary\n\n- alpha_ready: {rep['alpha_ready']}\n",encoding='utf-8')
    return rep
