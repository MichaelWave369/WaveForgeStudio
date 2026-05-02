from __future__ import annotations

import json
from pathlib import Path

from ..hashing import canonical_json, sha256_digest

_STABLE_TS = "1979-03-06T03:06:09Z"


def create_waverider_bundle(packet: dict) -> dict:
    source_packet_hash = sha256_digest(packet)
    visual = packet.get("visual", {})
    sync = packet.get("sync", {})
    structure = packet.get("structure", {})
    audio = packet.get("audio", {})

    bundle = {
        "schema": "waveforge.waverider_bundle.v0",
        "project": "WaveForgeStudio",
        "target_adapter": "WaveRider",
        "source_packet_hash": source_packet_hash,
        "seed": packet.get("seed"),
        "duration_seconds": packet.get("duration_seconds"),
        "mode": packet.get("mode"),
        "world": {
            "title": f"WaveWorld_{packet.get('seed')}",
            "prompt": packet.get("intent", {}).get("prompt"),
            "archetype": packet.get("intent", {}).get("archetype"),
            "visual_field": "sovereign_fractal_field",
            "color_field": visual.get("color_field", []),
            "render_style": "planned",
        },
        "scene_graph": {
            "scene_count": len(visual.get("scenes", [])),
            "scenes": visual.get("scenes", []),
        },
        "shot_graph": {
            "shot_count": len(visual.get("shots", [])),
            "shots": visual.get("shots", []),
        },
        "symbol_graph": {
            "symbols": visual.get("symbols", []),
            "voice_to_symbol": sync.get("voice_to_symbol", []),
        },
        "motion_graph": {
            "camera_motion": visual.get("camera_motion", []),
            "transitions": ["crossfade", "hard_cut", "phi_reveal"],
            "phi_cut_points": structure.get("phi_cuts", []),
        },
        "sync_reference": {
            "beat_to_cut": sync.get("beat_to_cut", []),
            "section_to_scene": sync.get("section_to_scene", []),
            "peak_to_reveal": sync.get("peak_to_reveal", []),
        },
        "audio_reference": {
            "tempo_bpm": audio.get("tempo_bpm"),
            "sections": audio.get("sections", []),
            "stems": audio.get("stems", []),
        },
        "render_targets": {
            "storyboard": "planned",
            "keyframes": "planned",
            "image_sequence": "planned",
            "video_timeline": "planned",
            "final_video": "not_rendered",
        },
    }

    stable_copy = json.loads(canonical_json(bundle))
    bundle_hash = sha256_digest(stable_copy)
    bundle["receipt"] = {
        "schema": "waveforge.waverider_bridge_receipt.v0",
        "bundle_hash": bundle_hash,
        "source_packet_hash": source_packet_hash,
        "created_at": _STABLE_TS,
    }
    return bundle


def write_waverider_bundle(packet: dict, out_dir: str | Path) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    bundle = create_waverider_bundle(packet)

    (out / "waverider_bundle.json").write_text(json.dumps(bundle, indent=2, sort_keys=True), encoding="utf-8")
    (out / "waverider_world.json").write_text(json.dumps(bundle["world"], indent=2, sort_keys=True), encoding="utf-8")
    (out / "waverider_scene_graph.json").write_text(json.dumps(bundle["scene_graph"], indent=2, sort_keys=True), encoding="utf-8")
    (out / "waverider_shot_graph.json").write_text(json.dumps(bundle["shot_graph"], indent=2, sort_keys=True), encoding="utf-8")
    (out / "waverider_symbol_graph.json").write_text(json.dumps(bundle["symbol_graph"], indent=2, sort_keys=True), encoding="utf-8")
    (out / "waverider_motion_graph.json").write_text(json.dumps(bundle["motion_graph"], indent=2, sort_keys=True), encoding="utf-8")
    (out / "waverider_receipt.json").write_text(json.dumps(bundle["receipt"], indent=2, sort_keys=True), encoding="utf-8")

    summary = f"""# WaveRider Bridge Summary

- Schema: {bundle['schema']}
- Source Packet Hash: {bundle['source_packet_hash']}
- Bundle Hash: {bundle['receipt']['bundle_hash']}
- Seed: {bundle['seed']}
- Duration: {bundle['duration_seconds']}
- Scenes: {bundle['scene_graph']['scene_count']}
- Shots: {bundle['shot_graph']['shot_count']}
"""
    (out / "WAVERIDER_BRIDGE_SUMMARY.md").write_text(summary, encoding="utf-8")
    return bundle
