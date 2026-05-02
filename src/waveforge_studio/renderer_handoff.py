from __future__ import annotations

import json
from pathlib import Path

from .av_timeline import create_av_timeline
from .hashing import canonical_json, sha256_digest

_TS = "1979-03-06T03:06:09Z"


def create_renderer_handoff(packet: dict) -> dict:
    t = create_av_timeline(packet)
    audio = packet.get("audio", {})
    visual = packet.get("visual", {})
    sync = packet.get("sync", {})
    shot_prompts = [f"Scene {s['scene']} | {packet.get('intent',{}).get('prompt')}" for s in visual.get("scenes", [])]
    while len(shot_prompts) < 9:
        shot_prompts.append(f"Sync shot {len(shot_prompts)+1}")
    handoff = {
        "schema": "waveforge.renderer_handoff.v0",
        "project": "WaveForgeStudio",
        "source_packet_hash": sha256_digest(packet),
        "seed": packet.get("seed"),
        "mode": packet.get("mode"),
        "duration_seconds": packet.get("duration_seconds"),
        "timeline": {"schema": t["schema"], "timeline_hash": t["receipt"]["timeline_hash"]},
        "audio_handoff": {
            "target": "PHIAudio", "render_status": "planned", "tempo_bpm": audio.get("tempo_bpm"), "sample_rate": 48000,
            "music_brief": "Deterministic mythic-reel music plan.", "stem_plan": audio.get("stems", []), "voiceover_script": audio.get("voiceover_cues", []), "mix_notes": ["Preserve intent clarity", "Keep sovereign pulse centered"],
        },
        "visual_handoff": {
            "target": "WaveRider", "render_status": "planned", "fps": 24, "style_brief": visual.get("render_style", "planned"),
            "shot_prompts": shot_prompts, "keyframe_prompts": [f"Keyframe {i+1}" for i,_ in enumerate(visual.get("shots", []))],
            "motion_prompts": visual.get("camera_motion", []), "transition_plan": ["crossfade", "hard_cut", "phi_reveal"],
        },
        "sync_handoff": {
            "markers": t.get("markers", []), "beat_to_cut": sync.get("beat_to_cut", []), "voice_to_symbol": sync.get("voice_to_symbol", []), "peak_to_reveal": sync.get("peak_to_reveal", []),
        },
        "renderer_slots": [
            {"id": "slot_001_audio_music", "kind": "audio", "target_adapter": "PHIAudio", "status": "planned", "input": "renderer_handoff.json", "expected_output": "render/audio_mix.wav"},
            {"id": "slot_002_audio_voice", "kind": "audio", "target_adapter": "PHIAudio", "status": "planned", "input": "renderer_handoff.json", "expected_output": "render/voiceover.wav"},
            {"id": "slot_003_visual_keyframes", "kind": "video", "target_adapter": "WaveRider", "status": "planned", "input": "renderer_handoff.json", "expected_output": "render/keyframes/"},
            {"id": "slot_004_visual_motion", "kind": "video", "target_adapter": "WaveRider", "status": "planned", "input": "renderer_handoff.json", "expected_output": "render/motion_pass/"},
            {"id": "slot_005_timeline_preview", "kind": "preview", "target_adapter": "WaveForgeStudio", "status": "planned", "input": "av_timeline.json", "expected_output": "timeline_preview.html"},
            {"id": "slot_006_final_mux", "kind": "future_render", "target_adapter": "WaveForgeStudio", "status": "blocked_plan_only", "input": "render/*", "expected_output": "render/final_video.mp4"},
        ],
        "safety": {"external_calls_allowed": False, "subprocess_allowed": False, "network_allowed": False, "real_rendering_allowed": False, "handoff_only": True},
    }
    hh = sha256_digest(json.loads(canonical_json(handoff)))
    handoff["receipt"] = {"schema": "waveforge.renderer_handoff_receipt.v0", "handoff_hash": hh, "source_packet_hash": handoff["source_packet_hash"], "timeline_hash": t["receipt"]["timeline_hash"], "created_at": _TS}
    return handoff


def validate_renderer_handoff(h: dict) -> list[str]:
    e=[]
    if h.get("schema")!="waveforge.renderer_handoff.v0": e.append("schema invalid")
    if not h.get("source_packet_hash"): e.append("source_packet_hash required")
    if not h.get("timeline",{}).get("timeline_hash"): e.append("timeline.timeline_hash required")
    for k in ["audio_handoff","visual_handoff","sync_handoff"]:
        if k not in h: e.append(f"{k} required")
    if len(h.get("renderer_slots",[]))<6: e.append("renderer_slots >=6 required")
    saf=h.get("safety",{})
    for k in ["external_calls_allowed","subprocess_allowed","network_allowed","real_rendering_allowed"]:
        if saf.get(k) is not False: e.append(f"safety.{k} must be false")
    if len(h.get("visual_handoff",{}).get("shot_prompts",[]))<9: e.append("shot_prompts must be >=9")
    if "handoff_hash" not in h.get("receipt",{}): e.append("receipt.handoff_hash required")
    return e


def assert_valid_renderer_handoff(h: dict) -> None:
    e=validate_renderer_handoff(h)
    if e: raise ValueError("Invalid renderer handoff: "+"; ".join(e))


def write_renderer_handoff(packet: dict, out_dir: str | Path) -> dict:
    out=Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    h=create_renderer_handoff(packet)
    (out/"renderer_handoff.json").write_text(json.dumps(h,indent=2,sort_keys=True),encoding='utf-8')
    (out/"renderer_handoff_receipt.json").write_text(json.dumps(h["receipt"],indent=2,sort_keys=True),encoding='utf-8')
    (out/"audio_render_brief.md").write_text("# Audio Render Brief\n\n"+h["audio_handoff"]["music_brief"],encoding='utf-8')
    (out/"voiceover_script.md").write_text("# Voiceover Script\n\n"+"\n".join([f"- {x}" for x in h["audio_handoff"]["voiceover_script"]]),encoding='utf-8')
    (out/"visual_shot_prompts.md").write_text("# Visual Shot Prompts\n\n"+"\n".join([f"- {x}" for x in h["visual_handoff"]["shot_prompts"]]),encoding='utf-8')
    (out/"motion_prompt_pack.md").write_text("# Motion Prompt Pack\n\n"+"\n".join([f"- {x}" for x in h["visual_handoff"]["motion_prompts"]]),encoding='utf-8')
    (out/"renderer_slots.json").write_text(json.dumps(h["renderer_slots"],indent=2,sort_keys=True),encoding='utf-8')
    (out/"RENDERER_HANDOFF_SUMMARY.md").write_text(f"# Renderer Handoff Summary\n\n- Prompt: {packet.get('intent',{}).get('prompt')}\n- Seed: {h['seed']}\n- Mode: {h['mode']}\n- Duration: {h['duration_seconds']}\n- Source Packet Hash: {h['source_packet_hash']}\n- AV Timeline Hash: {h['timeline']['timeline_hash']}\n- Audio Target: {h['audio_handoff']['target']}\n- Visual Target: {h['visual_handoff']['target']}\n- Shot Prompts: {len(h['visual_handoff']['shot_prompts'])}\n- Renderer Slots: {len(h['renderer_slots'])}\n- Handoff Hash: {h['receipt']['handoff_hash']}\n\nRenderer handoff only — no media rendered in v0.9.\n",encoding='utf-8')
    return h
