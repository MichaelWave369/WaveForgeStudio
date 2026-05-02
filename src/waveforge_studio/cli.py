from __future__ import annotations
import argparse, json
from pathlib import Path
from .adapters.phiaudio_bridge import write_phiaudio_bundle
from .adapters.registry import list_adapters
from .adapters.waverider_bridge import write_waverider_bundle
from .adapters.wavetalk_bridge import write_wavetalk_bundle
from .artifact_ledger import write_artifact_ledger
from .coherence import score_media_coherence
from .media_packet import create_media_packet
from .production_bundle import write_production_bundle
from .queue_runner import write_queue_execution
from .render_manifest import create_render_manifest
from .render_queue import validate_render_queue, write_render_queue
from .timeline_preview import write_timeline_preview
from .av_timeline import write_av_timeline, validate_av_timeline
from .renderer_handoff import write_renderer_handoff, validate_renderer_handoff
from .validation import validate_media_packet

def _load_valid(path:str):
    p=json.loads(Path(path).read_text(encoding='utf-8')); return p, validate_media_packet(p)
def _dump(p:Path,d:dict): p.write_text(json.dumps(d,indent=2,sort_keys=True),encoding='utf-8')

def compile_command(a):
    out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    p=create_media_packet(a.prompt,duration_seconds=a.duration,seed=a.seed,mode=a.mode)
    _dump(out/'project.waveforge.json',p); _dump(out/'audio_graph.json',p['audio']); _dump(out/'visual_graph.json',p['visual']); _dump(out/'sync_lattice.json',p['sync']); _dump(out/'render_manifest.json',create_render_manifest(p)); _dump(out/'receipt.json',p['receipt'])
    (out/'summary.md').write_text(f"# WaveForgeStudio Run Summary\n\n- Coherence Overall: {score_media_coherence(p)['overall']}\n",encoding='utf-8')
    if a.bundle: write_production_bundle(p,out)
    if a.export_wavetalk: write_wavetalk_bundle(p,out/'wavetalk')
    if a.export_phiaudio: write_phiaudio_bundle(p,out/'phiaudio')
    if a.export_waverider: write_waverider_bundle(p,out/'waverider')
    if a.preview: write_timeline_preview(p,out)
    if a.timeline: write_av_timeline(p,out)
    if a.handoff: write_renderer_handoff(p,out)
    if a.queue: write_render_queue(p,out)
    if a.run_queue:
        r=write_queue_execution(p,out)
        return 0 if r['failed_count']==0 else 1
    return 0

def validate_command(a):
    _,e=_load_valid(a.path); print('VALID media packet' if not e else 'INVALID media packet'); return 0 if not e else 1

def inspect_command(a):
    p,_=_load_valid(a.path); c=score_media_coherence(p)
    print(json.dumps({"project":p.get("project"),"schema":p.get("schema"),"seed":p.get("seed"),"mode":p.get("mode"),"prompt":p.get("intent",{}).get("prompt"),"duration":p.get("duration_seconds"),"audio_sections":len(p.get("audio",{}).get("sections",[])),"visual_scenes":len(p.get("visual",{}).get("scenes",[])),"sync_events":len(p.get("sync",{}).get("events",[])),"coherence_overall":c.get("overall"),"coherence_passed":c.get("passed"),"packet_hash":p.get("receipt",{}).get("packet_hash")},indent=2,sort_keys=True)); return 0

def adapters_command(a): print(json.dumps(list_adapters(),indent=2)); return 0

def export_phiaudio_command(a):
    p,e=_load_valid(a.path)
    if e: print('INVALID media packet'); return 1
    print(write_phiaudio_bundle(p,a.out)['receipt']['bundle_hash']); return 0

def export_waverider_command(a):
    p,e=_load_valid(a.path)
    if e: print('INVALID media packet'); return 1
    print(write_waverider_bundle(p,a.out)['receipt']['bundle_hash']); return 0

def export_wavetalk_command(a):
    p,e=_load_valid(a.path)
    if e: print('INVALID media packet'); return 1
    print(write_wavetalk_bundle(p,a.out)['receipts']['signal_receipt']['bundle_hash']); return 0

def preview_command(a):
    p,e=_load_valid(a.path)
    if e: print('INVALID media packet'); return 1
    print(write_timeline_preview(p,a.out)); return 0

def queue_command(a):
    p,e=_load_valid(a.path)
    if e: print('INVALID media packet'); return 1
    print(write_render_queue(p,a.out)['receipt']['queue_hash']); return 0

def timeline_command(a):
    p,e=_load_valid(a.path)
    if e: print('INVALID media packet'); return 1
    t=write_av_timeline(p,a.out); print(t['receipt']['timeline_hash']); return 0


def timeline_validate_command(a):
    t=json.loads(Path(a.path).read_text(encoding='utf-8')); e=validate_av_timeline(t)
    print('VALID av timeline' if not e else 'INVALID av timeline'); return 0 if not e else 1


def handoff_command(a):
    p,e=_load_valid(a.path)
    if e: print('INVALID media packet'); return 1
    h=write_renderer_handoff(p,a.out); print(h['receipt']['handoff_hash']); return 0


def handoff_validate_command(a):
    h=json.loads(Path(a.path).read_text(encoding='utf-8')); e=validate_renderer_handoff(h)
    print('VALID renderer handoff' if not e else 'INVALID renderer handoff'); return 0 if not e else 1


def queue_validate_command(a):
    q=json.loads(Path(a.path).read_text(encoding='utf-8')); e=validate_render_queue(q)
    print('VALID render queue' if not e else 'INVALID render queue'); return 0 if not e else 1

def run_queue_command(a):
    p,e=_load_valid(a.path)
    if e: print('INVALID media packet'); return 1
    r=write_queue_execution(p,a.out); print(r['receipt']['execution_hash']); print(r['artifact_ledger']['ledger_hash']); return 0 if r['failed_count']==0 else 1

def ledger_command(a): print(write_artifact_ledger(a.path)['receipt']['ledger_hash']); return 0

def bundle_command(a):
    p,e=_load_valid(a.path)
    if e: print('INVALID media packet'); return 1
    print(write_production_bundle(p,a.out)['receipt']['bundle_hash']); return 0

def build_parser():
    parser=argparse.ArgumentParser(prog='waveforge-studio'); sub=parser.add_subparsers(dest='command',required=True)
    c=sub.add_parser('compile'); c.add_argument('prompt'); c.add_argument('--duration',type=int,default=72); c.add_argument('--seed',type=int,default=369369); c.add_argument('--mode',default='mythic-reel'); c.add_argument('--out',required=True); c.add_argument('--export-phiaudio',action='store_true'); c.add_argument('--export-waverider',action='store_true'); c.add_argument('--export-wavetalk',action='store_true'); c.add_argument('--preview',action='store_true'); c.add_argument('--timeline',action='store_true'); c.add_argument('--handoff',action='store_true'); c.add_argument('--bundle',action='store_true'); c.add_argument('--queue',action='store_true'); c.add_argument('--run-queue',action='store_true'); c.set_defaults(func=compile_command)
    for n,f,o in [('validate',validate_command,False),('inspect',inspect_command,False),('adapters',adapters_command,False),('timeline-validate',timeline_validate_command,False),('handoff-validate',handoff_validate_command,False),('queue-validate',queue_validate_command,False),('ledger',ledger_command,False),('export-phiaudio',export_phiaudio_command,True),('export-waverider',export_waverider_command,True),('export-wavetalk',export_wavetalk_command,True),('preview',preview_command,True),('timeline',timeline_command,True),('handoff',handoff_command,True),('queue',queue_command,True),('run-queue',run_queue_command,True),('bundle',bundle_command,True)]:
        p=sub.add_parser(n); p.add_argument('path');
        if o: p.add_argument('--out',required=True)
        p.set_defaults(func=f)
    return parser

def main():
    a=build_parser().parse_args(); return a.func(a)
if __name__=='__main__': raise SystemExit(main())
