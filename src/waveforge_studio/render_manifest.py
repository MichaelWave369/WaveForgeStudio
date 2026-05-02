from __future__ import annotations


def create_render_manifest(packet: dict) -> dict:
    return {
        "schema": "waveforge.render_manifest.v0",
        "project": packet.get("project", "WaveForgeStudio"),
        "seed": packet.get("seed"),
        "audio_render": "stub",
        "video_render": "stub",
        "final_artifact": "not_rendered",
        "required_outputs": [
            "audio_graph.json",
            "visual_graph.json",
            "sync_lattice.json",
            "render_manifest.json",
            "receipt.json",
        ],
    }
