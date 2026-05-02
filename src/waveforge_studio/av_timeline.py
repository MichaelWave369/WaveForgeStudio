from __future__ import annotations

import json
from pathlib import Path

from .hashing import canonical_json, sha256_digest

_STABLE_TS = "1979-03-06T03:06:09Z"


def _r(x: float) -> float:
    return round(float(x), 3)


def create_av_timeline(packet: dict) -> dict:
    d = packet.get("duration_seconds", 0)
    audio = packet.get("audio", {})
    visual = packet.get("visual", {})
    sync = packet.get("sync", {})
    structure = packet.get("structure", {})
    events = sync.get("events", [])
    markers = [
        {"id": f"marker_{i+1:03d}", "time": _r(min(max(0.0, e.get("timestamp", 0.0)), max(0.0, d-0.001))), "kind": "sync", "label": f"sync_{i+1}"}
        for i, e in enumerate(events)
    ]
    tracks = [
        {"id": "track_audio_music", "kind": "audio", "role": "music", "clips": [{"id": f"music_{i+1}", "start": _r(s.get("start",0)), "end": _r(s.get("end",0))} for i,s in enumerate(audio.get("sections", []))]},
        {"id": "track_audio_voice", "kind": "audio", "role": "voiceover", "clips": [{"id": f"voice_{i+1}", "start": _r(c.get("timestamp",0)), "end": _r(min(d, c.get("timestamp",0)+2.0))} for i,c in enumerate(audio.get("voiceover_cues", []))]},
        {"id": "track_video_scene", "kind": "video", "role": "scene_keyframes", "clips": [{"id": f"scene_{i+1}", "start": _r(s.get("start",0)), "end": _r(s.get("end",0))} for i,s in enumerate(visual.get("scenes", []))]},
        {"id": "track_video_motion", "kind": "video", "role": "camera_motion", "clips": [{"id": f"motion_{i+1}", "start": _r((i*d)/max(len(visual.get('camera_motion',[])),1)), "end": _r(min(d, ((i+1)*d)/max(len(visual.get('camera_motion',[])),1)))} for i,_ in enumerate(visual.get("camera_motion", []))]},
        {"id": "track_symbols", "kind": "symbolic", "role": "symbols", "clips": [{"id": f"symbol_{i+1}", "start": _r((i*d)/max(len(visual.get('symbols',[])),1)), "end": _r(min(d,((i+1)*d)/max(len(visual.get('symbols',[])),1)))} for i,_ in enumerate(visual.get("symbols", []))]},
        {"id": "track_markers", "kind": "marker", "role": "sync_markers", "clips": [{"id": f"mclip_{i+1}", "start": _r(m["time"]), "end": _r(min(d,m["time"]+0.001))} for i,m in enumerate(markers)]},
    ]
    timeline = {
        "schema": "waveforge.av_timeline.v0",
        "project": "WaveForgeStudio",
        "source_packet_hash": sha256_digest(packet),
        "seed": packet.get("seed"),
        "mode": packet.get("mode"),
        "duration_seconds": d,
        "timebase": {"unit": "seconds", "fps": 24, "sample_rate": 48000, "tempo_bpm": audio.get("tempo_bpm")},
        "structure": {"pattern": structure.get("pattern", "3-6-9"), "acts": structure.get("acts", []), "scenes": structure.get("scenes", []), "sync_events": events, "phi_cut_points": structure.get("phi_cuts", [])},
        "tracks": tracks,
        "markers": markers,
        "exports": {"json": "av_timeline.json", "markdown": "AV_TIMELINE_SUMMARY.md", "csv_markers": "av_timeline_markers.csv", "render_status": "not_rendered"},
    }
    thash = sha256_digest(json.loads(canonical_json(timeline)))
    timeline["receipt"] = {"schema": "waveforge.av_timeline_receipt.v0", "timeline_hash": thash, "source_packet_hash": timeline["source_packet_hash"], "created_at": _STABLE_TS}
    return timeline


def validate_av_timeline(t: dict) -> list[str]:
    e=[]
    if t.get("schema")!="waveforge.av_timeline.v0": e.append("schema invalid")
    if t.get("duration_seconds",0)<=0: e.append("duration_seconds invalid")
    tracks=t.get("tracks",[])
    if len(tracks)!=6: e.append("tracks must be 6")
    if len(t.get("markers",[]))<9: e.append("markers must be >=9")
    ids=[x.get("id") for x in tracks]
    if len(ids)!=len(set(ids)): e.append("duplicate track ids")
    dur=t.get("duration_seconds",0)
    for tr in tracks:
        cids=[]
        for c in tr.get("clips",[]):
            cid=c.get("id");
            if cid in cids: e.append("duplicate clip ids")
            cids.append(cid)
            s=c.get("start",0); en=c.get("end",0)
            if not (0<=s<en<=dur): e.append("invalid clip timing")
    if not t.get("source_packet_hash"): e.append("source_packet_hash required")
    if "timeline_hash" not in t.get("receipt",{}): e.append("receipt.timeline_hash required")
    return e


def assert_valid_av_timeline(t: dict) -> None:
    e=validate_av_timeline(t)
    if e: raise ValueError("Invalid av timeline: "+"; ".join(e))


def write_av_timeline(packet: dict, out_dir: str | Path) -> dict:
    out=Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    t=create_av_timeline(packet)
    (out/"av_timeline.json").write_text(json.dumps(t,indent=2,sort_keys=True),encoding="utf-8")
    (out/"av_timeline_receipt.json").write_text(json.dumps(t["receipt"],indent=2,sort_keys=True),encoding="utf-8")
    csv="id,time,kind,label\n"+"\n".join([f"{m['id']},{m['time']},{m['kind']},{m['label']}" for m in t["markers"]])
    (out/"av_timeline_markers.csv").write_text(csv,encoding="utf-8")
    (out/"AV_TIMELINE_SUMMARY.md").write_text(f"# AV Timeline Summary\n\n- Prompt: {packet.get('intent',{}).get('prompt')}\n- Seed: {t['seed']}\n- Mode: {t['mode']}\n- Duration: {t['duration_seconds']}\n- Timebase: {t['timebase']}\n- 3/6/9 counts: acts={len(t['structure']['acts'])}, scenes={len(t['structure']['scenes'])}, sync={len(t['structure']['sync_events'])}\n- Tracks: {', '.join([x['id'] for x in t['tracks']])}\n- Markers: {len(t['markers'])}\n- Timeline Hash: {t['receipt']['timeline_hash']}\n\nDeterministic AV timeline only — no media rendered in v0.8.\n",encoding='utf-8')
    return t
