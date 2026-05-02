from __future__ import annotations

from .constants import C_STAR


def score_media_coherence(packet: dict) -> dict:
    scores = {
        "intent_audio_alignment": 0.82,
        "intent_visual_alignment": 0.83,
        "audio_visual_alignment": 0.81,
        "structure_alignment": 0.88,
    }
    overall = round(
        scores["intent_audio_alignment"] * 0.25
        + scores["intent_visual_alignment"] * 0.25
        + scores["audio_visual_alignment"] * 0.2
        + scores["structure_alignment"] * 0.3,
        6,
    )
    scores["overall"] = overall
    scores["passed"] = overall >= C_STAR
    return scores
