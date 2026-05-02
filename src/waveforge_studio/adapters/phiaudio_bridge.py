from __future__ import annotations

import json
from pathlib import Path

from ..hashing import canonical_json, sha256_digest

_STABLE_TS = "1979-03-06T03:06:09Z"


def _stem_events(sections: list[dict], role: str) -> list[dict]:
    return [
        {
            "section": s.get("name", f"section_{i+1}"),
            "start": s.get("start", 0),
            "end": s.get("end", 0),
            "intensity": round((i + 1) / max(len(sections), 1), 3),
            "role": role,
        }
        for i, s in enumerate(sections)
    ]


def create_phiaudio_bundle(packet: dict) -> dict:
    source_packet_hash = sha256_digest(packet)
    audio = packet.get("audio", {})
    visual = packet.get("visual", {})
    sync = packet.get("sync", {})
    sections = audio.get("sections", [])
    stems = audio.get("stems", [])

    bundle = {
        "schema": "waveforge.phiaudio_bundle.v0",
        "project": "WaveForgeStudio",
        "target_adapter": "PHIAudio",
        "source_packet_hash": source_packet_hash,
        "seed": packet.get("seed"),
        "duration_seconds": packet.get("duration_seconds"),
        "tempo_bpm": audio.get("tempo_bpm"),
        "composition": {
            "title": f"WaveForge_{packet.get('seed')}",
            "mode": packet.get("mode"),
            "sections": sections,
            "arrangement": [s.get("name", f"act_{i+1}") for i, s in enumerate(sections)],
            "sonic_palette": audio.get("sonic_palette", []),
        },
        "stems": [
            {
                "id": f"stem_{stem}",
                "role": "rhythm" if i == 0 else "texture",
                "render_mode": "planned",
                "events": _stem_events(sections, stem),
            }
            for i, stem in enumerate(stems)
        ],
        "voiceover": audio.get("voiceover_cues", []),
        "sync": {
            "beat_to_cut": sync.get("beat_to_cut", []),
            "section_to_scene": sync.get("section_to_scene", []),
            "voice_to_symbol": sync.get("voice_to_symbol", []),
            "peak_to_reveal": sync.get("peak_to_reveal", []),
        },
        "visual_reference": {
            "scene_count": len(visual.get("scenes", [])),
            "shot_count": len(visual.get("shots", [])),
            "symbols": visual.get("symbols", []),
        },
        "render_targets": {
            "mix_wav": "planned",
            "stems_wav": "planned",
            "midi": "planned",
            "timeline_json": "planned",
        },
    }

    stable_copy = json.loads(canonical_json(bundle))
    bundle_hash = sha256_digest(stable_copy)
    bundle["receipt"] = {
        "schema": "waveforge.phiaudio_bridge_receipt.v0",
        "bundle_hash": bundle_hash,
        "source_packet_hash": source_packet_hash,
        "created_at": _STABLE_TS,
    }
    return bundle


def write_phiaudio_bundle(packet: dict, out_dir: str | Path) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    bundle = create_phiaudio_bundle(packet)

    (out / "phiaudio_bundle.json").write_text(json.dumps(bundle, indent=2, sort_keys=True), encoding="utf-8")
    (out / "phiaudio_composition.json").write_text(json.dumps(bundle["composition"], indent=2, sort_keys=True), encoding="utf-8")
    (out / "phiaudio_stems.json").write_text(json.dumps(bundle["stems"], indent=2, sort_keys=True), encoding="utf-8")
    (out / "phiaudio_sync.json").write_text(json.dumps(bundle["sync"], indent=2, sort_keys=True), encoding="utf-8")
    (out / "phiaudio_receipt.json").write_text(json.dumps(bundle["receipt"], indent=2, sort_keys=True), encoding="utf-8")

    summary = f"""# PHIAudio Bridge Summary

- Schema: {bundle['schema']}
- Source Packet Hash: {bundle['source_packet_hash']}
- Bundle Hash: {bundle['receipt']['bundle_hash']}
- Seed: {bundle['seed']}
- Duration: {bundle['duration_seconds']}
- Tempo: {bundle['tempo_bpm']}
- Sections: {len(bundle['composition']['sections'])}
- Stems: {len(bundle['stems'])}
- Scenes Ref: {bundle['visual_reference']['scene_count']}
- Shots Ref: {bundle['visual_reference']['shot_count']}
"""
    (out / "PHIAUDIO_BRIDGE_SUMMARY.md").write_text(summary, encoding="utf-8")
    return bundle
