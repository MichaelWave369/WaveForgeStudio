from __future__ import annotations


def build_visual_graph(packet_or_prompt, duration_seconds: int, seed: int) -> dict:
    scene_len = duration_seconds / 6
    scenes = [
        {"scene": i + 1, "start": round(i * scene_len, 3), "end": round((i + 1) * scene_len, 3)}
        for i in range(6)
    ]
    shots = [
        {"shot": i + 1, "timestamp": round((i + 1) * (duration_seconds / 9), 3), "framing": "medium"}
        for i in range(9)
    ]
    return {
        "scenes": scenes,
        "shots": shots,
        "symbols": ["spiral", "sigil", "horizon_gate"],
        "color_field": ["obsidian", "gold", "violet"],
        "camera_motion": ["orbital", "dolly_in", "parallax_pan"],
        "render_style": "mythic-fractal-cinematic",
    }
