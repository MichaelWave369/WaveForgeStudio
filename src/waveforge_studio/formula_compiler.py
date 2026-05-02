from __future__ import annotations

from .constants import FIB_SEQUENCE


def _round3(x: float) -> float:
    return round(x, 3)


def compile_formula(duration_seconds: int) -> dict:
    act_len = duration_seconds / 3
    scene_len = duration_seconds / 6
    beat_len = duration_seconds / 9

    acts = [
        {"act": i + 1, "start": _round3(i * act_len), "end": _round3((i + 1) * act_len)}
        for i in range(3)
    ]
    scenes = [
        {"scene": i + 1, "start": _round3(i * scene_len), "end": _round3((i + 1) * scene_len)}
        for i in range(6)
    ]
    sync_beats = [
        {"beat": i + 1, "timestamp": _round3((i + 1) * beat_len)}
        for i in range(9)
    ]
    phi_cuts = [
        {"ratio": 0.382, "timestamp": _round3(duration_seconds * 0.382)},
        {"ratio": 0.618, "timestamp": _round3(duration_seconds * 0.618)},
        {"ratio": 0.809, "timestamp": _round3(duration_seconds * 0.809)},
    ]
    fib_timing = [_round3(duration_seconds * (n / 88)) for n in FIB_SEQUENCE]

    return {
        "acts": acts,
        "scenes": scenes,
        "sync_beats": sync_beats,
        "phi_cuts": phi_cuts,
        "fib_timing": fib_timing,
    }
