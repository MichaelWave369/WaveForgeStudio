from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from .adapters.phiaudio_bridge import write_phiaudio_bundle
from .adapters.registry import list_adapters
from .adapters.waverider_bridge import write_waverider_bundle
from .adapters.wavetalk_bridge import write_wavetalk_bundle
from .artifact_ledger import write_artifact_ledger
from .coherence import score_media_coherence
from .forge_workflow import run_forge_workflow
from .media_packet import create_media_packet
from .production_bundle import write_production_bundle
from .queue_runner import write_queue_execution
from .release_manifest import write_release_manifest
from .render_manifest import create_render_manifest
from .render_queue import validate_render_queue, write_render_queue
from .schema_registry import list_schemas
from .local_audio_renderer import render_audio_stub, validate_audio_render_manifest
from .local_visual_renderer import render_visual_stub, validate_visual_render_manifest
from .local_av_preview import render_av_preview, validate_av_preview_manifest
from .preview_pack import write_preview_pack, validate_preview_pack_manifest
from .preview_pack_zip import write_preview_pack_zip, validate_preview_pack_zip_manifest
from .demo_gallery import write_demo_gallery, validate_gallery_manifest
from .gallery_collection import write_gallery_collection, validate_gallery_collection_manifest
from .collection_export import write_collection_export, validate_collection_export_manifest
from .release_deck import write_release_deck, validate_release_deck_manifest
from .release_deck_zip import write_release_deck_zip, validate_release_deck_zip_manifest
from .release_build import write_release_build, validate_release_build_manifest
from .release_build_zip import write_release_build_zip, validate_release_build_zip_manifest
from .release_build_verification import write_release_build_verification, validate_release_build_verification
from .release_certificate import write_release_certificate, validate_release_certificate
from .certificate_bundle import write_certificate_bundle, validate_certificate_bundle_manifest
from .certificate_bundle_zip import write_certificate_bundle_zip, validate_certificate_bundle_zip_manifest
from .smoke import write_golden_demo_smoke
from .timeline_preview import write_timeline_preview
from .av_timeline import write_av_timeline, validate_av_timeline
from .renderer_handoff import write_renderer_handoff, validate_renderer_handoff
from .validation import validate_media_packet
from .version import PROJECT_NAME, RELEASE_NAME, __version__

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

def forge_command(a):
    run_forge_workflow(prompt=a.prompt, out_dir=a.out, duration_seconds=a.duration, seed=a.seed, mode=a.mode)
    packet = json.loads((Path(a.out) / "project.waveforge.json").read_text(encoding="utf-8"))
    rendered = False
    if getattr(a, "render_audio_stub", False):
        render_audio_stub(packet, a.out); rendered = True
    if getattr(a, "render_visual_stub", False):
        render_visual_stub(packet, a.out); rendered = True
    if getattr(a, "av_preview", False) or getattr(a, "preview_pack", False):
        render_av_preview(packet, a.out); rendered = True
    if getattr(a, "preview_pack", False):
        write_preview_pack(a.out); rendered = True
    if getattr(a, "preview_pack_zip", False):
        write_preview_pack(a.out); write_preview_pack_zip(Path(a.out)/"preview_pack"); rendered = True
    if rendered:
        write_release_manifest(a.out, packet)
    return 0

def release_command(a):
    root = Path(a.path)
    packet = json.loads((root / 'project.waveforge.json').read_text(encoding='utf-8')) if (root / 'project.waveforge.json').exists() else None
    manifest = write_release_manifest(root, packet)
    print(manifest['receipt']['release_hash'])
    return 0

def version_command(a):
    print(json.dumps({"project": PROJECT_NAME, "version": __version__, "release_name": RELEASE_NAME}, indent=2, sort_keys=True)); return 0

def schemas_command(a):
    print(json.dumps({"schema": "waveforge.schema_registry.v1_alpha", "schemas": list_schemas()}, indent=2, sort_keys=True)); return 0

def smoke_command(a):
    rep = write_golden_demo_smoke(a.out, prompt=a.prompt, duration_seconds=a.duration, seed=a.seed, mode=a.mode, render_audio=getattr(a, "render_audio_stub", False), render_visual=getattr(a, "render_visual_stub", False), av_preview=getattr(a, "av_preview", False), preview_pack=getattr(a, "preview_pack", False), preview_pack_zip=getattr(a, "preview_pack_zip", False))
    print(json.dumps({"out": str(a.out), "smoke_passed": rep['smoke_passed'], "alpha_ready": rep['alpha_ready'], "release_hash": rep['release_hash'], "smoke_hash": rep['receipt']['smoke_hash']}, indent=2, sort_keys=True))
    return 0 if rep['smoke_passed'] else 1


def render_audio_stub_command(a):
    p,e=_load_valid(a.path)
    if e: print('INVALID media packet'); return 1
    m = render_audio_stub(p, a.out, max_duration_seconds=a.max_duration, sample_rate=a.sample_rate)
    print(json.dumps({"out": str(a.out), "rendered_duration_seconds": m["rendered_duration_seconds"], "mix": m["outputs"]["mix"], "audio_render_hash": m["receipt"]["audio_render_hash"]}, indent=2, sort_keys=True))
    return 0


def audio_render_validate_command(a):
    m=json.loads(Path(a.path).read_text(encoding='utf-8')); e=validate_audio_render_manifest(m)
    print('VALID audio render manifest' if not e else 'INVALID audio render manifest')
    return 0 if not e else 1

def render_visual_stub_command(a):
    p,e=_load_valid(a.path)
    if e: print('INVALID media packet'); return 1
    m = render_visual_stub(p, a.out, frame_count=a.frame_count, width=a.width, height=a.height)
    print(json.dumps({"out": str(a.out), "frame_count": m["frame_count"], "storyboard_index": m["outputs"]["storyboard_index"], "visual_render_hash": m["receipt"]["visual_render_hash"]}, indent=2, sort_keys=True))
    return 0


def visual_render_validate_command(a):
    m=json.loads(Path(a.path).read_text(encoding='utf-8')); e=validate_visual_render_manifest(m)
    print('VALID visual render manifest' if not e else 'INVALID visual render manifest')
    return 0 if not e else 1


def preview_av_command(a):
    p,e=_load_valid(a.path)
    if e: print('INVALID media packet'); return 1
    m = render_av_preview(p, a.out)
    print(json.dumps({"out": str(a.out), "preview_html": m["outputs"]["preview_html"], "audio_present": m["assets"]["audio_mix"]["present"], "frame_count": len(m["assets"]["storyboard_frames"]), "av_preview_hash": m["receipt"]["av_preview_hash"]}, indent=2, sort_keys=True))
    return 0


def av_preview_validate_command(a):
    m=json.loads(Path(a.path).read_text(encoding='utf-8')); e=validate_av_preview_manifest(m)
    print('VALID av preview manifest' if not e else 'INVALID av preview manifest')
    return 0 if not e else 1


def pack_preview_command(a):
    out = a.out or str(Path(a.path)/'preview_pack')
    m = write_preview_pack(a.path, out)
    e = validate_preview_pack_manifest(m)
    print(json.dumps({"pack_path": out, "index_path": m["outputs"]["pack_index"], "storyboard_frame_count": len(m["storyboard_frames"]), "missing_count": len(m["missing"]), "preview_pack_hash": m["receipt"]["preview_pack_hash"]}, indent=2, sort_keys=True))
    return 0 if not e else 1


def preview_pack_validate_command(a):
    m=json.loads(Path(a.path).read_text(encoding='utf-8')); e=validate_preview_pack_manifest(m)
    print('VALID preview pack manifest' if not e else 'INVALID preview pack manifest')
    return 0 if not e else 1



def zip_preview_pack_command(a):
    m = write_preview_pack_zip(a.path, a.out)
    e = validate_preview_pack_zip_manifest(m)
    print(json.dumps({"zip_path": str((Path(a.out) if a.out else Path(a.path)/"preview_pack.zip")), "file_count": m["file_count"], "zip_sha256": m["receipt"]["zip_file_sha256"], "preview_pack_zip_hash": m["receipt"]["preview_pack_zip_hash"]}, indent=2, sort_keys=True))
    return 0 if not e else 1


def preview_pack_zip_validate_command(a):
    m=json.loads(Path(a.path).read_text(encoding='utf-8')); e=validate_preview_pack_zip_manifest(m)
    print('VALID preview pack zip manifest' if not e else 'INVALID preview pack zip manifest')
    return 0 if not e else 1


def gallery_command(a):
    out = a.out or str(Path(a.root_dir)/"gallery")
    m = write_demo_gallery(a.root_dir, out)
    e = validate_gallery_manifest(m)
    print(json.dumps({"gallery_path": out, "run_count": m["run_count"], "ready_count": m["ready_count"], "smoke_passed_count": m["smoke_passed_count"], "zip_count": m["zip_count"], "tag_count": m.get("search",{}).get("tag_count",0), "available_tags_preview": m.get("search",{}).get("available_tags",[])[:10], "gallery_hash": m["receipt"]["gallery_hash"]}, indent=2, sort_keys=True))
    return 0 if not e else 1

def gallery_validate_command(a):
    m=json.loads(Path(a.path).read_text(encoding='utf-8')); e=validate_gallery_manifest(m)
    print('VALID gallery manifest' if not e else 'INVALID gallery manifest')
    return 0 if not e else 1


def collection_command(a):
    m = write_gallery_collection(a.path, a.out, title=a.title, description=a.description, include_tags=a.include_tag, include_run_paths=a.include_run, exclude_tags=a.exclude_tag)
    e = validate_gallery_collection_manifest(m)
    print(json.dumps({"collection_path": str(Path(a.out) if a.out else Path(a.path).parent/"collection"), "title": m["title"], "run_count": m["run_count"], "ready_count": m["ready_count"], "smoke_passed_count": m["smoke_passed_count"], "zip_count": m["zip_count"], "collection_hash": m["receipt"]["collection_hash"], "missing_run_paths_count": len(m["selection"]["missing_run_paths"])}, indent=2, sort_keys=True))
    return 0 if not e else 1

def collection_validate_command(a):
    m=json.loads(Path(a.path).read_text(encoding='utf-8')); e=validate_gallery_collection_manifest(m)
    print('VALID gallery collection manifest' if not e else 'INVALID gallery collection manifest')
    return 0 if not e else 1


def collection_export_command(a):
    m=write_collection_export(a.path,a.out)
    e=validate_collection_export_manifest(m)
    print(json.dumps({"export_path": str(Path(a.out) if a.out else Path(a.path).parent/"collection_export"), "title": m["title"], "run_count": m["run_count"], "zip_count": m["zip_count"], "missing_zip_count": m["missing_zip_count"], "collection_export_hash": m["receipt"]["collection_export_hash"]}, indent=2, sort_keys=True))
    return 0 if not e else 1

def collection_export_validate_command(a):
    m=json.loads(Path(a.path).read_text(encoding='utf-8')); e=validate_collection_export_manifest(m)
    print('VALID collection export manifest' if not e else 'INVALID collection export manifest')
    return 0 if not e else 1


def release_deck_command(a):
    m=write_release_deck(a.path,a.out,title=a.title,subtitle=a.subtitle)
    e=validate_release_deck_manifest(m)
    print(json.dumps({"deck_path": str(Path(a.out) if a.out else Path(a.path).parent/"release_deck"), "title": m["title"], "card_count": m["card_count"], "release_deck_hash": m["receipt"]["release_deck_hash"]}, indent=2, sort_keys=True))
    return 0 if not e else 1

def release_deck_validate_command(a):
    m=json.loads(Path(a.path).read_text(encoding='utf-8')); e=validate_release_deck_manifest(m)
    print('VALID release deck manifest' if not e else 'INVALID release deck manifest')
    return 0 if not e else 1


def zip_release_deck_command(a):
    m=write_release_deck_zip(a.path,a.out)
    e=validate_release_deck_zip_manifest(m)
    print(json.dumps({"zip_path": str(Path(a.out) if a.out else Path(a.path)/"release_deck.zip"), "file_count": m["file_count"], "card_count": m["card_count"], "zip_sha256": m["receipt"]["zip_file_sha256"], "release_deck_zip_hash": m["receipt"]["release_deck_zip_hash"]}, indent=2, sort_keys=True))
    return 0 if not e else 1

def release_deck_zip_validate_command(a):
    m=json.loads(Path(a.path).read_text(encoding='utf-8')); e=validate_release_deck_zip_manifest(m)
    print('VALID release deck zip manifest' if not e else 'INVALID release deck zip manifest')
    return 0 if not e else 1


def release_build_command(a):
    m=write_release_build(a.runs_root,a.out,title=a.title,description=a.description,include_tags=a.include_tag,exclude_tags=a.exclude_tag,include_run_paths=a.include_run)
    if getattr(a, "zip", False):
        write_release_build_zip(Path(a.out) if a.out else Path(a.runs_root)/"release_build")
    if getattr(a, "verify", False):
        write_release_build_verification(Path(a.out) if a.out else Path(a.runs_root)/"release_build", strict=False)
    if getattr(a, "certify", False):
        write_release_certificate(Path(a.out) if a.out else Path(a.runs_root)/"release_build", require_passed=False)
    if getattr(a, "certificate_bundle", False):
        write_certificate_bundle(Path(a.out) if a.out else Path(a.runs_root)/"release_build", include_zip_file=getattr(a, "certificate_bundle_include_zip", False))
    if getattr(a, "certificate_bundle_zip", False):
        rb=Path(a.out) if a.out else Path(a.runs_root)/"release_build"
        write_certificate_bundle(rb, include_zip_file=getattr(a, "certificate_bundle_include_zip", False))
        write_certificate_bundle_zip(rb/'certificate_bundle')
    e=validate_release_build_manifest(m)
    print(json.dumps({"build_path": str(Path(a.out) if a.out else Path(a.runs_root)/"release_build"), "title": m["title"], "discovered_runs": m["counts"]["discovered_runs"], "selected_runs": m["counts"]["selected_runs"], "zip_count": m["counts"]["zip_count"], "missing_zip_count": m["counts"]["missing_zip_count"], "deck_card_count": m["counts"]["deck_cards"], "release_deck_zip": m["outputs"]["release_deck_zip"], "release_build_hash": m["receipt"]["release_build_hash"]}, indent=2, sort_keys=True))
    return 0 if not e else 1

def release_build_validate_command(a):
    m=json.loads(Path(a.path).read_text(encoding='utf-8')); e=validate_release_build_manifest(m)
    print('VALID release build manifest' if not e else 'INVALID release build manifest')
    return 0 if not e else 1

def zip_release_build_command(a):
    m=write_release_build_zip(a.path,a.out)
    e=validate_release_build_zip_manifest(m)
    print(json.dumps({"zip_path": str((Path(a.out) if a.out else Path(a.path)/"release_build.zip")), "file_count": m["file_count"], "zip_sha256": m["receipt"]["zip_file_sha256"], "release_build_zip_hash": m["receipt"]["release_build_zip_hash"]}, indent=2, sort_keys=True))
    return 0 if not e else 1

def release_build_zip_validate_command(a):
    m=json.loads(Path(a.path).read_text(encoding='utf-8')); e=validate_release_build_zip_manifest(m)
    print('VALID release build zip manifest' if not e else 'INVALID release build zip manifest')
    return 0 if not e else 1

def verify_release_build_command(a):
    m=write_release_build_verification(a.path, strict=getattr(a, "strict", False))
    print(json.dumps({"build_path": str(a.path), "strict": m["strict"], "passed": m["summary"]["passed"], "check_count": m["summary"]["check_count"], "error_count": m["summary"]["error_count"], "warning_count": m["summary"]["warning_count"], "verification_hash": m["receipt"]["verification_hash"]}, indent=2, sort_keys=True))
    return 0 if m["summary"]["passed"] else 1

def release_build_verification_validate_command(a):
    m=json.loads(Path(a.path).read_text(encoding='utf-8')); e=validate_release_build_verification(m)
    print('VALID release build verification report' if not e else 'INVALID release build verification report')
    return 0 if not e else 1

def certify_release_build_command(a):
    c=write_release_certificate(a.path, require_passed=getattr(a, "require_passed", False))
    e=validate_release_certificate(c)
    print(json.dumps({"build_path": str(a.path), "certificate_status": c["certificate_status"], "verification_passed": c["verification"]["passed"], "warning_count": c["verification"]["warning_count"], "error_count": c["verification"]["error_count"], "release_build_zip_sha256": c["hashes"]["release_build_zip_sha256"], "release_certificate_hash": c["receipt"]["release_certificate_hash"]}, indent=2, sort_keys=True))
    if e: return 1
    return 1 if getattr(a, "require_passed", False) and not c["verification"]["passed"] else 0

def release_certificate_validate_command(a):
    c=json.loads(Path(a.path).read_text(encoding='utf-8')); e=validate_release_certificate(c)
    print('VALID release certificate' if not e else 'INVALID release certificate')
    return 0 if not e else 1

def certificate_bundle_command(a):
    m=write_certificate_bundle(a.path, a.out, include_zip_file=getattr(a, "include_zip_file", False))
    e=validate_certificate_bundle_manifest(m)
    print(json.dumps({"bundle_path": str(Path(a.out) if a.out else Path(a.path)/"certificate_bundle"), "evidence_count": m["evidence_count"], "required_missing_count": len(m["required_missing"]), "optional_missing_count": len(m["optional_missing"]), "certificate_status": m["certificate_status"], "verification_passed": m["verification_passed"], "certificate_bundle_hash": m["receipt"]["certificate_bundle_hash"]}, indent=2, sort_keys=True))
    return 0 if not e else 1

def certificate_bundle_validate_command(a):
    m=json.loads(Path(a.path).read_text(encoding='utf-8')); e=validate_certificate_bundle_manifest(m)
    print('VALID certificate bundle manifest' if not e else 'INVALID certificate bundle manifest')
    return 0 if not e else 1

def zip_certificate_bundle_command(a):
    m=write_certificate_bundle_zip(a.path,a.out)
    e=validate_certificate_bundle_zip_manifest(m)
    print(json.dumps({"zip_path": str((Path(a.out) if a.out else Path(a.path)/"certificate_bundle.zip")), "file_count": m["file_count"], "zip_sha256": m["receipt"]["zip_file_sha256"], "certificate_bundle_zip_hash": m["receipt"]["certificate_bundle_zip_hash"]}, indent=2, sort_keys=True))
    return 0 if not e else 1

def certificate_bundle_zip_validate_command(a):
    m=json.loads(Path(a.path).read_text(encoding='utf-8')); e=validate_certificate_bundle_zip_manifest(m)
    print('VALID certificate bundle zip manifest' if not e else 'INVALID certificate bundle zip manifest')
    return 0 if not e else 1

def doctor_command(a):
    cmd_summary = ["version","schemas","forge","release","smoke","doctor","compile","validate","inspect","adapters","timeline","timeline-validate","handoff","handoff-validate","queue","queue-validate","run-queue","ledger","bundle","preview","export-phiaudio","export-waverider","export-wavetalk"]
    report = {
        "project": PROJECT_NAME,
        "version": __version__,
        "release_name": RELEASE_NAME,
        "python_version": sys.version.split()[0],
        "package_import_status": "ok",
        "available_commands": cmd_summary,
        "renderer_status": "plan-only / no real rendering",
        "external_calls": "disabled",
        "subprocess_rendering": "disabled",
    }
    print(json.dumps(report, indent=2, sort_keys=True)); return 0

def validate_command(a):
    _,e=_load_valid(a.path); print('VALID media packet' if not e else 'INVALID media packet'); return 0 if not e else 1
# ... keeping existing commands

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
    v=sub.add_parser('version'); v.set_defaults(func=version_command)
    s=sub.add_parser('schemas'); s.set_defaults(func=schemas_command)
    f=sub.add_parser('forge'); f.add_argument('prompt'); f.add_argument('--duration',type=int,default=72); f.add_argument('--seed',type=int,default=369369); f.add_argument('--mode',default='mythic-reel'); f.add_argument('--out',required=True); f.add_argument('--render-audio-stub',action='store_true'); f.add_argument('--render-visual-stub',action='store_true'); f.add_argument('--av-preview',action='store_true'); f.add_argument('--preview-pack',action='store_true'); f.add_argument('--preview-pack-zip',action='store_true'); f.set_defaults(func=forge_command)
    r=sub.add_parser('release'); r.add_argument('path'); r.set_defaults(func=release_command)
    sm=sub.add_parser('smoke'); sm.add_argument('--out',required=True); sm.add_argument('--prompt',default='The Sovereign Signal awakens across the infinite fractal wave.'); sm.add_argument('--duration',type=int,default=72); sm.add_argument('--seed',type=int,default=369369); sm.add_argument('--mode',default='mythic-reel'); sm.add_argument('--render-audio-stub',action='store_true'); sm.add_argument('--render-visual-stub',action='store_true'); sm.add_argument('--av-preview',action='store_true'); sm.add_argument('--preview-pack',action='store_true'); sm.add_argument('--preview-pack-zip',action='store_true'); sm.set_defaults(func=smoke_command)
    d=sub.add_parser('doctor'); d.set_defaults(func=doctor_command)
    ra=sub.add_parser('render-audio-stub'); ra.add_argument('path'); ra.add_argument('--out',required=True); ra.add_argument('--max-duration',type=int,default=12); ra.add_argument('--sample-rate',type=int,default=48000); ra.set_defaults(func=render_audio_stub_command)
    arv=sub.add_parser('audio-render-validate'); arv.add_argument('path'); arv.set_defaults(func=audio_render_validate_command)
    rv=sub.add_parser('render-visual-stub'); rv.add_argument('path'); rv.add_argument('--out',required=True); rv.add_argument('--frame-count',type=int,default=9); rv.add_argument('--width',type=int,default=1280); rv.add_argument('--height',type=int,default=720); rv.set_defaults(func=render_visual_stub_command)
    vrv=sub.add_parser('visual-render-validate'); vrv.add_argument('path'); vrv.set_defaults(func=visual_render_validate_command)
    pav=sub.add_parser('preview-av'); pav.add_argument('path'); pav.add_argument('--out',required=True); pav.set_defaults(func=preview_av_command)
    pavv=sub.add_parser('av-preview-validate'); pavv.add_argument('path'); pavv.set_defaults(func=av_preview_validate_command)
    pp=sub.add_parser('pack-preview'); pp.add_argument('path'); pp.add_argument('--out'); pp.set_defaults(func=pack_preview_command)
    ppv=sub.add_parser('preview-pack-validate'); ppv.add_argument('path'); ppv.set_defaults(func=preview_pack_validate_command)
    zpp=sub.add_parser('zip-preview-pack'); zpp.add_argument('path'); zpp.add_argument('--out'); zpp.set_defaults(func=zip_preview_pack_command)
    zppv=sub.add_parser('preview-pack-zip-validate'); zppv.add_argument('path'); zppv.set_defaults(func=preview_pack_zip_validate_command)
    gal=sub.add_parser('gallery'); gal.add_argument('root_dir'); gal.add_argument('--out'); gal.set_defaults(func=gallery_command)
    galv=sub.add_parser('gallery-validate'); galv.add_argument('path'); galv.set_defaults(func=gallery_validate_command)
    col=sub.add_parser('collection'); col.add_argument('path'); col.add_argument('--out'); col.add_argument('--title', default='WaveForgeStudio Collection'); col.add_argument('--description', default=''); col.add_argument('--include-tag', action='append'); col.add_argument('--exclude-tag', action='append'); col.add_argument('--include-run', action='append'); col.set_defaults(func=collection_command)
    colv=sub.add_parser('collection-validate'); colv.add_argument('path'); colv.set_defaults(func=collection_validate_command)
    cexp=sub.add_parser('collection-export'); cexp.add_argument('path'); cexp.add_argument('--out'); cexp.set_defaults(func=collection_export_command)
    cexpv=sub.add_parser('collection-export-validate'); cexpv.add_argument('path'); cexpv.set_defaults(func=collection_export_validate_command)
    rd=sub.add_parser('release-deck'); rd.add_argument('path'); rd.add_argument('--out'); rd.add_argument('--title'); rd.add_argument('--subtitle', default='PHI369 Sovereign Media Showcase'); rd.set_defaults(func=release_deck_command)
    rdv=sub.add_parser('release-deck-validate'); rdv.add_argument('path'); rdv.set_defaults(func=release_deck_validate_command)
    zrd=sub.add_parser('zip-release-deck'); zrd.add_argument('path'); zrd.add_argument('--out'); zrd.set_defaults(func=zip_release_deck_command)
    zrdv=sub.add_parser('release-deck-zip-validate'); zrdv.add_argument('path'); zrdv.set_defaults(func=release_deck_zip_validate_command)
    rb=sub.add_parser('release-build'); rb.add_argument('runs_root'); rb.add_argument('--out'); rb.add_argument('--title', default='WaveForgeStudio Release Build'); rb.add_argument('--description', default=''); rb.add_argument('--include-tag', action='append'); rb.add_argument('--exclude-tag', action='append'); rb.add_argument('--include-run', action='append'); rb.add_argument('--zip', action='store_true'); rb.add_argument('--verify', action='store_true'); rb.add_argument('--certify', action='store_true'); rb.add_argument('--certificate-bundle', action='store_true'); rb.add_argument('--certificate-bundle-include-zip', action='store_true'); rb.add_argument('--certificate-bundle-zip', action='store_true'); rb.set_defaults(func=release_build_command)
    rbv=sub.add_parser('release-build-validate'); rbv.add_argument('path'); rbv.set_defaults(func=release_build_validate_command)
    zrb=sub.add_parser('zip-release-build'); zrb.add_argument('path'); zrb.add_argument('--out'); zrb.set_defaults(func=zip_release_build_command)
    zrbv=sub.add_parser('release-build-zip-validate'); zrbv.add_argument('path'); zrbv.set_defaults(func=release_build_zip_validate_command)
    vrb=sub.add_parser('verify-release-build'); vrb.add_argument('path'); vrb.add_argument('--strict', action='store_true'); vrb.set_defaults(func=verify_release_build_command)
    vrbv=sub.add_parser('release-build-verification-validate'); vrbv.add_argument('path'); vrbv.set_defaults(func=release_build_verification_validate_command)
    crb=sub.add_parser('certify-release-build'); crb.add_argument('path'); crb.add_argument('--require-passed', action='store_true'); crb.set_defaults(func=certify_release_build_command)
    crbv=sub.add_parser('release-certificate-validate'); crbv.add_argument('path'); crbv.set_defaults(func=release_certificate_validate_command)
    cb=sub.add_parser('certificate-bundle'); cb.add_argument('path'); cb.add_argument('--out'); cb.add_argument('--include-zip-file', action='store_true'); cb.set_defaults(func=certificate_bundle_command)
    cbv=sub.add_parser('certificate-bundle-validate'); cbv.add_argument('path'); cbv.set_defaults(func=certificate_bundle_validate_command)
    zcb=sub.add_parser('zip-certificate-bundle'); zcb.add_argument('path'); zcb.add_argument('--out'); zcb.set_defaults(func=zip_certificate_bundle_command)
    zcbv=sub.add_parser('certificate-bundle-zip-validate'); zcbv.add_argument('path'); zcbv.set_defaults(func=certificate_bundle_zip_validate_command)
    c=sub.add_parser('compile'); c.add_argument('prompt'); c.add_argument('--duration',type=int,default=72); c.add_argument('--seed',type=int,default=369369); c.add_argument('--mode',default='mythic-reel'); c.add_argument('--out',required=True); c.add_argument('--export-phiaudio',action='store_true'); c.add_argument('--export-waverider',action='store_true'); c.add_argument('--export-wavetalk',action='store_true'); c.add_argument('--preview',action='store_true'); c.add_argument('--timeline',action='store_true'); c.add_argument('--handoff',action='store_true'); c.add_argument('--bundle',action='store_true'); c.add_argument('--queue',action='store_true'); c.add_argument('--run-queue',action='store_true'); c.set_defaults(func=compile_command)
    for n,f,o in [('validate',validate_command,False),('inspect',inspect_command,False),('adapters',adapters_command,False),('timeline-validate',timeline_validate_command,False),('handoff-validate',handoff_validate_command,False),('queue-validate',queue_validate_command,False),('ledger',ledger_command,False),('export-phiaudio',export_phiaudio_command,True),('export-waverider',export_waverider_command,True),('export-wavetalk',export_wavetalk_command,True),('preview',preview_command,True),('timeline',timeline_command,True),('handoff',handoff_command,True),('queue',queue_command,True),('run-queue',run_queue_command,True),('bundle',bundle_command,True)]:
        p=sub.add_parser(n); p.add_argument('path');
        if o: p.add_argument('--out',required=True)
        p.set_defaults(func=f)
    return parser

def main():
    a=build_parser().parse_args(); return a.func(a)
if __name__=='__main__': raise SystemExit(main())
