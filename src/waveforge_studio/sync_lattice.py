from __future__ import annotations


def build_sync_lattice(audio_graph: dict, visual_graph: dict, duration_seconds: int) -> dict:
    sections = audio_graph.get("sections", [])
    scenes = visual_graph.get("scenes", [])
    symbols = visual_graph.get("symbols", [])
    cues = audio_graph.get("voiceover_cues", [])

    events = []
    for i in range(9):
        ts = round((i + 1) * (duration_seconds / 9), 3)
        events.append({"event": i + 1, "timestamp": ts, "binding": "beat_to_cut"})

    return {
        "events": events,
        "beat_to_cut": [{"beat": e["event"], "cut": e["event"]} for e in events],
        "section_to_scene": [
            {"section": s["name"], "scene": scenes[min(i * 2, len(scenes)-1)]["scene"]}
            for i, s in enumerate(sections)
        ],
        "voice_to_symbol": [
            {"cue": cues[i]["cue"], "symbol": symbols[i % len(symbols)]}
            for i in range(min(len(cues), len(symbols)))
        ],
        "peak_to_reveal": [
            {"peak": "phi_0.809", "reveal": "artifact_emergence", "timestamp": round(duration_seconds * 0.809, 3)}
        ],
    }
