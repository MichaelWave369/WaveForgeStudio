from __future__ import annotations


def build_audio_graph(packet_or_prompt, duration_seconds: int, seed: int) -> dict:
    tempo_bpm = 72 + (seed % 73)
    keys = ["A minor", "C minor", "D dorian", "E phrygian", "G mixolydian"]
    key = keys[seed % len(keys)]
    section_len = duration_seconds / 3
    sections = [
        {"name": f"act_{i+1}", "start": round(i * section_len, 3), "end": round((i + 1) * section_len, 3)}
        for i in range(3)
    ]
    return {
        "tempo_bpm": tempo_bpm,
        "key": key,
        "sections": sections,
        "stems": ["pulse", "bass", "atmos", "lead", "percussion"],
        "voiceover_cues": [
            {"timestamp": round(duration_seconds * 0.382, 3), "cue": "invoke_signal"},
            {"timestamp": round(duration_seconds * 0.618, 3), "cue": "declare_intent"},
            {"timestamp": round(duration_seconds * 0.809, 3), "cue": "seal_artifact"},
        ],
        "sonic_palette": ["fractal_pad", "granular_bell", "sovereign_pulse"],
    }
